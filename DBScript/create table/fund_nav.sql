drop table if exists fund_nav;

/*==============================================================*/
/* Table: fund_nav                                              */
/*==============================================================*/
create table fund_nav
(
   wind_code            varchar(20) not null comment '�������',
   nav_date             date not null comment '��ֵ����',
   nav                  double comment '��ֵ',
   nav_acc              double comment '�ۼƾ�ֵ',
   nav_tot              double comment '�ʲ���ֵ',
   source_mark          int comment '����Դ��0��wind��1���ֶ���2������',
   primary key (wind_code, nav_date)
) ENGINE=MyISAM;
