drop table if exists wind_stock_info;

/*==============================================================*/
/* Table: wind_stock_info                                       */
/*==============================================================*/
create table wind_stock_info
(
   wind_code            varchar(20) not null,
   trade_code           varchar(20) comment '��Ʊ����',
   sec_name             varchar(20) comment '��Ʊ����',
   ipo_date             date comment '��������',
   delist_date          date comment 'ժ������',
   exch_city            varchar(20) comment '��������ַ',
   exch_eng             varchar(20) comment '������Ӣ��',
   mkt                  varchar(20) comment '�г����ƣ����塢��С�塢��ҵ���',
   prename              varchar(2000) comment '������',
   primary key (wind_code)
) ENGINE=MyISAM;
