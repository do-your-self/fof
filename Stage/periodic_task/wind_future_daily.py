# -*- coding: utf-8 -*-
"""
Created on 2017/5/2
@author: MG
"""
from config_fh import STR_FORMAT_DATE, get_db_engine, get_db_session
from fh_tools.windy_utils_rest import WindRest
from config_fh import get_db_engine, WIND_REST_URL
# from fh_tools.windy_utils import wsd_cache
# from fh_tools import windy_utils
# from WindPy import w
import pandas as pd
from sqlalchemy.types import String, Date, Float
import logging
logger = logging.getLogger()


def import_wind_future_daily():
    # w.wsd("AG1612.SHF", "open,high,low,close,volume,amt,dealnum,settle,oi,st_stock", "2016-11-01", "2016-12-21", "")
    sql_str = """select fi.wind_code, ifnull(trade_date_max_1, ipo_date) date_frm, 
    if(subdate(curdate(), 1)<lasttrade_date,subdate(curdate(), 1),lasttrade_date) date_to
    from wind_future_info fi left outer join
    (select wind_code, adddate(max(trade_date),1) trade_date_max_1 from wind_future_daily group by wind_code) wfd
    on fi.wind_code = wfd.wind_code"""
    engine = get_db_engine()
    future_date_dic = {}
    with get_db_session(engine) as session:
        table = session.execute(sql_str)
        for wind_code, date_frm, date_to in table.fetchall():
            future_date_dic[wind_code] = (date_frm, date_to)
    data_df_list = []
    # w.start()
    rest = WindRest(WIND_REST_URL)  # 初始化服务器接口，用于下载万得数据
    future_count = len(future_date_dic)
    try:
        logger.info("%d future instrument will be handled", future_count)
        for n_future, (wind_code, date_pair) in enumerate(future_date_dic.items()):
            # 暂时只处理 RU 期货合约信息
            # if wind_code.find('RU') == -1:
            #     continue
            date_frm, date_to = date_pair
            if date_frm > date_to:
                continue
            logger.info('%d/%d) get %s between %s and %s', n_future, future_count, wind_code, date_frm, date_to)
            # data_df_tmp = wsd_cache(w, wind_code, "open,high,low,close,volume,amt,dealnum,settle,oi,st_stock",
            #                         date_frm, date_to, "")
            data_df_tmp = rest.wsd(wind_code, "open,high,low,close,volume,amt,dealnum,settle,oi,st_stock",
                                    date_frm, date_to, "")
            data_df_tmp['wind_code'] = wind_code
            data_df_list.append(data_df_tmp)
            # if len(data_df_list) >= 50:
            #     break
    finally:
        data_df_count = len(data_df_list)
        if data_df_count > 0:
            logger.info('merge data with %d df', data_df_count)
            data_df = pd.concat(data_df_list)
            data_df.index.rename('trade_date', inplace=True)
            data_df = data_df.reset_index().set_index(['wind_code', 'trade_date'])
            data_df.rename(columns={c: str.lower(c) for c in data_df.columns}, inplace=True)
            data_df.rename(columns={'oi': 'position'}, inplace=True)
            data_count = data_df.shape[0]
            data_df.to_sql('wind_future_daily', engine, if_exists='append',
                           index_label=['wind_code', 'trade_date'],
                           dtype={
                               'wind_code': String(20),
                               'trade_date': Date,
                               'open': Float,
                               'high': Float,
                               'low': Float,
                               'close': Float,
                               'volume': Float,
                               'amt': Float,
                               'dealnum': Float,
                               'settle': Float,
                               'position': Float,
                               'st_stock': Float,
                           })
            logger.info('%d data import', data_count)
        else:
            logger.info('no data for merge')
        # w.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(levelname)s [%(name)s] %(message)s')
    # windy_utils.CACHE_ENABLE = False
    import_wind_future_daily()
