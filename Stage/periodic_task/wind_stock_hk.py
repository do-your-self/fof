# -*- coding: utf-8 -*-
"""
Created on 2018/1/17
@author: MG
"""

import logging
import math
import pandas as pd
from datetime import datetime, date, timedelta
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
from config_fh import get_db_engine, get_db_session, STR_FORMAT_DATE, UN_AVAILABLE_DATE, WIND_REST_URL
from fh_tools.windy_utils_rest import WindRest, APIError
from fh_tools.fh_utils import get_last, get_first, date_2_str
import logging
from sqlalchemy.types import String, Date, Float, Integer
from sqlalchemy.dialects.mysql import DOUBLE
logger = logging.getLogger()
DATE_BASE = datetime.strptime('1980-01-01', STR_FORMAT_DATE).date()
ONE_DAY = timedelta(days=1)
# 标示每天几点以后下载当日行情数据
BASE_LINE_HOUR = 20

w = WindRest(WIND_REST_URL)


def get_stock_code_set(date_fetch):
    date_fetch_str = date_fetch.strftime(STR_FORMAT_DATE)
    stock_df = w.wset("sectorconstituent", "date=%s;sectorid=a002010100000000" % date_fetch_str)  # 全部港股
    if stock_df is None:
        logging.warning('%s 获取股票代码失败', date_fetch_str)
        return None
    stock_count = stock_df.shape[0]
    logging.info('get %d stocks on %s', stock_count, date_fetch_str)
    return set(stock_df['wind_code'])


def import_wind_stock_info_hk(refresh=False):

    # 获取全市场股票代码及名称
    logging.info("更新 wind_stock_info_hk 开始")
    if refresh:
        date_fetch = DATE_BASE
    else:
        date_fetch = date.today()
    date_end = date.today()
    stock_code_set = set()
    while date_fetch < date_end:
        stock_code_set_sub = get_stock_code_set(date_fetch)
        if stock_code_set_sub is not None:
            stock_code_set |= stock_code_set_sub
        date_fetch += timedelta(days=365)
    stock_code_set_sub = get_stock_code_set(date_end)
    if stock_code_set_sub is not None:
        stock_code_set |= stock_code_set_sub

    # 获取股票对应上市日期，及摘牌日期
    # w.wss("300005.SZ,300372.SZ,000003.SZ", "ipo_date,trade_code,mkt,exch_city,exch_eng")
    stock_code_list = list(stock_code_set)
    stock_code_count = len(stock_code_list)
    seg_count = 1000
    loop_count = math.ceil(float(stock_code_count) / seg_count)
    stock_info_df_list = []
    for n in range(loop_count):
        num_start = n * seg_count
        num_end = (n + 1) * seg_count
        num_end = num_end if num_end <= stock_code_count else stock_code_count
        stock_code_list_sub = stock_code_list[num_start:num_end]
        # 尝试将 stock_code_list_sub 直接传递给wss，是否可行
        stock_info_df = w.wss(stock_code_list_sub, "sec_name,trade_code,ipo_date,delist_date,mkt,exch_city,exch_eng,prename")
        stock_info_df_list.append(stock_info_df)

    stock_info_all_df = pd.concat(stock_info_df_list)
    stock_info_all_df.index.rename('WIND_CODE', inplace=True)
    logging.info('%s stock data will be import', stock_info_all_df.shape[0])
    engine = get_db_engine()
    stock_info_all_df.reset_index(inplace=True)
    data_list = list(stock_info_all_df.T.to_dict().values())
    sql_str = "REPLACE INTO wind_stock_info_hk (wind_code, trade_code, sec_name, ipo_date, delist_date, mkt, exch_city, exch_eng, prename) values (:WIND_CODE, :TRADE_CODE, :SEC_NAME, :IPO_DATE, :DELIST_DATE, :MKT, :EXCH_CITY, :EXCH_ENG, :PRENAME)"
    # sql_str = "insert INTO wind_stock_info_hk (wind_code, trade_code, sec_name, ipo_date, delist_date, mkt, exch_city, exch_eng, prename) values (:WIND_CODE, :TRADE_CODE, :SEC_NAME, :IPO_DATE, :DELIST_DATE, :MKT, :EXCH_CITY, :EXCH_ENG, :PRENAME)"
    with get_db_session(engine) as session:
        session.execute(sql_str, data_list)
        stock_count = session.execute('select count(*) from wind_stock_info_hk').first()[0]
    logging.info("更新 wind_stock_info_hk 完成 存量数据 %d 条", stock_count)


def import_stock_daily_hk():
    """
    插入股票日线数据到最近一个工作日-1。
    如果超过 BASE_LINE_HOUR 时间，则获取当日的数据
    :return: 
    """
    logging.info("更新 wind_stock_daily_hk 开始")
    engine = get_db_engine()

    col_name_dic = {
        "OPEN": "open",
        "HIGH": "high",
        "LOW": "low",
        "CLOSE": "close",
        "ADJFACTOR": "adjfactor",
        "VOLUME": "volume",
        "AMT": "amt",
        "PCT_CHG": "pct_chg",
        "MAXUPORDOWN": "maxupordown",
        "SWING": "swing",
        "TURN": "turn",
        "FREE_TURN": "free_turn",
        "TRADE_STATUS": "trade_status",
        "SUSP_DAYS": "susp_days",
        "TOTAL_SHARES": "total_shares",
        "FREE_FLOAT_SHARES": "free_float_shares",
        "EV2_TO_EBITDA": "ev",
        'PS_TTM': 'PS',
        'PE_TTM': 'PE',
        'PB_MRQ': 'PB',
        }
    col_name_list = [col_name.lower() for col_name in col_name_dic.keys()]
    # wind_indictor_str = "open,high,low,close,adjfactor,volume,amt,pct_chg,maxupordown," + \
    #                     "swing,turn,free_turn,trade_status,susp_days," + \
    #                     "total_shares,free_float_shares,ev2_to_ebitda"
    wind_indictor_str = ",".join(col_name_list)
    w = WindRest(WIND_REST_URL)

    with get_db_session(engine) as session:
        # 获取每只股票最新交易日数据
        sql_str = 'select wind_code, max(Trade_date) from wind_stock_daily_hk group by wind_code'
        table = session.execute(sql_str)
        stock_trade_date_latest_dic = dict(table.fetchall())
        # 获取市场有效交易日数据
        sql_str = "select trade_date from wind_trade_date_hk where trade_date > '1980-1-1'"
        table = session.execute(sql_str)
        trade_date_sorted_list = [t[0] for t in table.fetchall()]
        trade_date_sorted_list.sort()
        logger.info("加载交易日数据完成，最小交易日 %s", trade_date_sorted_list[0])
        # 获取每只股票上市日期、退市日期
        table = session.execute('SELECT wind_code, ipo_date, delist_date FROM wind_stock_info_hk')
        stock_date_dic = {wind_code: (ipo_date, delist_date if delist_date is None or delist_date > UN_AVAILABLE_DATE else None) for
                          wind_code, ipo_date, delist_date in table.fetchall()}
    date_ending = date.today() - ONE_DAY if datetime.now().hour < BASE_LINE_HOUR else date.today()
    data_df_list = []
    data_len = len(stock_date_dic)
    logger.info('%d stocks will been import into wind_stock_daily_hk', data_len)
    try:
        for data_num, (wind_code, date_pair) in enumerate(stock_date_dic.items()):
            date_ipo, date_delist = date_pair
            if date_ipo is None:
                date_ipo = DATE_BASE
                logger.warning("%d/%d) %s 没有缺少 date_ipo 字段，默认使用 %s", data_num, data_len, wind_code, date_2_str(DATE_BASE))
            # 获取 date_from
            if wind_code in stock_trade_date_latest_dic:
                date_latest_t1 = stock_trade_date_latest_dic[wind_code] + ONE_DAY
                date_from = max([date_latest_t1, DATE_BASE, date_ipo])
            else:
                date_from = max([DATE_BASE, date_ipo])
            date_from = get_first(trade_date_sorted_list, lambda x: x >= date_from)
            # 获取 date_to
            if date_delist is None:
                date_to = date_ending
            else:
                date_to = min([date_delist, date_ending])
            date_to = get_last(trade_date_sorted_list, lambda x: x <= date_to)
            if date_from is None or date_to is None or date_from > date_to:
                continue
            # 获取股票量价等行情数据
            try:
                data_df = w.wsd(wind_code, wind_indictor_str, date_from, date_to)
            except APIError as exp:
                logger.exception("%d/%d) %s 执行异常", data_num, data_len, wind_code)
                if exp.ret_dic.setdefault('error_code', 0) in (
                        -40520007,  # 没有可用数据
                        -40521009,  # 数据解码失败。检查输入参数是否正确，如：日期参数注意大小月月末及短二月
                ):
                    continue
                else:
                    break
            if data_df is None:
                logger.warning('%d/%d) %s has no data during %s %s', data_num, data_len, wind_code, date_from, date_to)
                continue
            logger.info('%d/%d) %d data of %s between %s and %s', data_num, data_len, data_df.shape[0], wind_code, date_from, date_to)
            data_df['wind_code'] = wind_code
            data_df_list.append(data_df)
            # 仅供调试使用
            # if len(data_df_list) > 10:
            #     break
    finally:
        # 导入数据库
        if len(data_df_list) > 0:
            data_df_all = pd.concat(data_df_list)
            data_df_all.index.rename('trade_date', inplace=True)
            data_df_all.reset_index(inplace=True)
            data_df_all.rename(columns=col_name_dic)
            data_df_all.set_index(['wind_code', 'trade_date'], inplace=True)
            data_df_all.to_sql('wind_stock_daily_hk', engine, if_exists='append',
                               dtype={
                                   'wind_code': String(20),
                                   'trade_date': Date,
                                   'open': DOUBLE,
                                   'high': DOUBLE,
                                   'low': DOUBLE,
                                   'close': DOUBLE,
                                   'adjfactor': DOUBLE,
                                   'volume': DOUBLE,
                                   'amt': DOUBLE,
                                   'pct_chg': DOUBLE,
                                   'maxupordown': Integer,
                                   'swing': DOUBLE,
                                   'turn': DOUBLE,
                                   'free_turn': DOUBLE,
                                   'trade_status': String(20),
                                   'susp_days': Integer,
                                   'total_shares': DOUBLE,
                                   'free_DOUBLE_shares': DOUBLE,
                                   'ev2_to_ebitda': DOUBLE,
                               }
                               )
            logging.info("更新 wind_stock_daily_hk 结束 %d 条信息被更新", data_df_all.shape[0])


def import_stock_quertarly_hk():
    """
    插入股票日线数据到最近一个工作日-1
    :return: 
    """
    logging.info("更新 wind_stock_quertarly_hk 开始")

    w = WindRest(WIND_REST_URL)
    engine = get_db_engine()
    with get_db_session(engine) as session:
        # 获取每只股票最新交易日数据
        sql_str = 'select wind_code, max(Trade_date) from wind_stock_quertarly_hk group by wind_code'
        table = session.execute(sql_str)
        stock_trade_date_latest_dic = dict(table.fetchall())
        # 获取市场有效交易日数据
        sql_str = "select trade_date from wind_trade_date_hk where trade_date > '2005-1-1'"
        table = session.execute(sql_str)
        trade_date_sorted_list = [t[0] for t in table.fetchall()]
        trade_date_sorted_list.sort()
        # 获取每只股票上市日期、退市日期
        table = session.execute('SELECT wind_code, ipo_date, delist_date FROM wind_stock_info_hk')
        stock_date_dic = {wind_code: (ipo_date, delist_date if delist_date is None or delist_date > UN_AVAILABLE_DATE else None) for
                          wind_code, ipo_date, delist_date in table.fetchall()}
    date_ending = date.today() - ONE_DAY if datetime.now().hour < BASE_LINE_HOUR else date.today()
    data_df_list = []
    logger.info('%d stocks will been import into wind_stock_quertarly_hk', len(stock_date_dic))
    # 获取股票量价等行情数据
    field_col_name_dic = {
        'roic_ttm': 'roic_ttm',
        'yoyprofit': 'yoyprofit',
        'ebit': 'ebit',
        'ebit2': 'ebit2',
        'ebit2_ttm': 'ebit2_ttm',
        'surpluscapitalps': 'surpluscapitalps',
        'undistributedps': 'undistributedps',
        'stm_issuingdate': 'stm_issuingdate',
    }
    wind_indictor_str = ",".join(field_col_name_dic.keys())
    upper_col_2_name_dic = {name.upper(): val for name, val in field_col_name_dic.items()}
    try:
        for stock_num, (wind_code, date_pair) in enumerate(stock_date_dic.items()):
            date_ipo, date_delist = date_pair
            # 获取 date_from
            if wind_code in stock_trade_date_latest_dic:
                date_latest_t1 = stock_trade_date_latest_dic[wind_code] + ONE_DAY
                date_from = max([date_latest_t1, DATE_BASE, date_ipo])
            else:
                date_from = max([DATE_BASE, date_ipo])
            date_from = get_first(trade_date_sorted_list, lambda x: x >= date_from)
            # 获取 date_to
            if date_delist is None:
                date_to = date_ending
            else:
                date_to = min([date_delist, date_ending])
            date_to = get_last(trade_date_sorted_list, lambda x: x <= date_to)
            if date_from is None or date_to is None or date_from > date_to:
                continue
            # 获取股票量价等行情数据
            # w.wsd("002122.SZ", "roic_ttm,yoyprofit,ebit,ebit2,ebit2_ttm,surpluscapitalps,undistributedps,stm_issuingdate", "2012-12-31", "2017-12-06", "unit=1;rptType=1;Period=Q")
            data_df = w.wsd(wind_code, wind_indictor_str, date_from, date_to, "unit=1;rptType=1;Period=Q")
            if data_df is None:
                logger.warning('%d) %s has no data during %s %s', stock_num, wind_code, date_from, date_to)
                continue
            data_df.rename(columns=upper_col_2_name_dic, inplace=True)
            # 清理掉期间全空的行
            for trade_date in list(data_df.index):
                is_all_none = data_df.loc[trade_date].apply(lambda x: x is None).all()
                if is_all_none:
                    logger.warning("%s %s 数据全部为空", wind_code, trade_date)
                    data_df.drop(trade_date, inplace=True)
            logger.info('%d) %d data of %s between %s and %s', stock_num, data_df.shape[0], wind_code, date_from, date_to)
            data_df['wind_code'] = wind_code
            data_df_list.append(data_df)
            # 仅供调试使用
            if len(data_df_list) > 10:
                break
    finally:
        # 导入数据库
        if len(data_df_list) > 0:
            data_df_all = pd.concat(data_df_list)
            data_df_all.index.rename('trade_date', inplace=True)
            data_df_all.reset_index(inplace=True)
            data_df_all.set_index(['wind_code', 'trade_date'], inplace=True)
            data_df_all.to_sql('wind_stock_quertarly_hk', engine, if_exists='append')
            logging.info("更新 wind_stock_quertarly_hk 结束 %d 条信息被更新", data_df_all.shape[0])


def fill_col():
    """补充历史col数据"""

    engine = get_db_engine()

    # 股票列表
    sql_str = """select *
    from (
    select wind_code, sum(amt) amt_tot
    from wind_stock_daily_hk
    where trade_date BETWEEN '2015-1-1' and '2017-12-31'
    GROUP BY wind_code
    ) tt
    order by amt_tot desc"""
    data_df = pd.read_sql(sql_str, engine, index_col='wind_code')
    # 由于数量比较大，目前只执行前 N 支股票
    stock_count = data_df.shape[0]
    first_n_count = 2200
    logger.info("共 %d 支股票需要更新，目前只更新前 %d 支", stock_count, first_n_count)
    wind_code_list = list(data_df[:first_n_count].index)

    col_name_dic = {'PS_TTM': 'PS',
                  'PE_TTM': 'PE',
                  'PB_MRQ': 'PB',
                  }
    col_name_list = [col_name.lower() for col_name in col_name_dic.keys()]
    # 获取每只股票ipo 日期 及 最小的交易日前一天
    #     sql_str = """select si.wind_code, td_from, td_to
    # from wind_stock_info si,
    # (select wind_code, min(trade_date) td_from, max(trade_date) td_to from wind_stock_daily where ev2_to_ebitda is null group by wind_code) sd
    # where si.wind_code = sd.wind_code"""
    sql_str = """select wsd.wind_code, min_trade_date, max_trade_date
from
(
select wind_code, min(trade_date) min_trade_date, max(trade_date) max_trade_date, max(amt) amt_max
from wind_stock_daily_hk
group by wind_code
) wsd
LEFT JOIN
(
select wind_code
from wind_stock_daily_hk
where PB is not null
group by wind_code
) wsd_null
on wsd.wind_code = wsd_null.wind_code
where wsd_null.wind_code is null
order by amt_max desc"""
    w = WindRest(WIND_REST_URL)
    with get_db_session(engine) as session:
        table = session.execute(sql_str)
        stock_trade_date_range_dic = {content[0]: (content[1], content[2]) for content in table.fetchall()}
    data_df_list = []
    try:
        # for n, (wind_code, (date_from, date_to)) in enumerate(stock_trade_date_range_dic.items()):
        for data_num, wind_code in enumerate(wind_code_list, start=1):
            if wind_code not in stock_trade_date_range_dic:
                continue
            if wind_code == '8008.HK':  # 这支票数据有问题 实际应该是 '1686.HK' '新意网集团'
                continue
            date_from, date_to = stock_trade_date_range_dic[wind_code]
            # 获取股票量价等行情数据
            wind_indictor_str = col_name_list
            data_df = w.wsd(wind_code, wind_indictor_str, date_from, date_to)
            if data_df is None:
                logger.warning('%d) %s has no data during %s %s', data_num, wind_code, date_from, date_to)
                continue
            logger.info('%d) %d data of %s between %s and %s', data_num, data_df.shape[0], wind_code, date_from, date_to)
            data_df['wind_code'] = wind_code
            data_df_list.append(data_df)
            # 仅供调试使用
            # if data_num > 10:
            #     break
    finally:
        # 导入数据库
        if len(data_df_list) > 0:
            data_df_all = pd.concat(data_df_list)
            data_df_all.index.rename('trade_date', inplace=True)
            data_df_all.reset_index(inplace=True)
            # 只有全部列为空的项才需要剔除
            is_na_s = None
            for col_name in col_name_dic.keys():
                if is_na_s is None:
                    is_na_s = data_df_all[col_name].isna()
                else:
                    is_na_s = is_na_s & data_df_all[col_name].isna()
            data_df_not_null = data_df_all[~is_na_s]
            data_df_not_null.fillna('null', inplace=True)
            if data_df_not_null.shape[0] > 0:
                data_dic_list = data_df_not_null.to_dict(orient='records')
                sql_str = "update wind_stock_daily_hk set " + \
                          ",".join(["%s=:%s" % (db_col_name, col_name) for col_name, db_col_name in col_name_dic.items()]) +\
                          " where wind_code=:wind_code and trade_date=:trade_date"
                with get_db_session(engine) as session:
                    table = session.execute(sql_str, params=data_dic_list)
            logger.info('%d data imported', data_df_not_null.shape[0])
        else:
            logger.warning('no data for update')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(levelname)s [%(name)s:%(funcName)s] %(message)s')
    # import_wind_stock_info_hk(refresh=False)
    import_stock_daily_hk()
    # import_stock_quertarly_hk()
    # fill_col()
