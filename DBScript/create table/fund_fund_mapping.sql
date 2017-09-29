drop table if exists fund_fund_mapping;

/*==============================================================*/
/* Table: fund_fund_mapping                                     */
/*==============================================================*/
create table fund_fund_mapping
(
   wind_code_s          varchar(20) not null comment '��Ͷ�������',
   wind_code            varchar(20) not null comment 'ʵ�ʻ������',
   sec_name_s           varchar(100) comment '��Ͷ�ʻ������',
   date_start           date comment 'Ͷ���ӻ�����ʼ�ۼƾ�ֵ',
   date_end             date comment '��������',
   warning_line         double comment 'Ԥ����',
   winding_line         double comment '������',
   primary key (wind_code_s)
);

alter table fund_fund_mapping comment '��¼��Ͷ�ʻ�����ʵ�ʻ����Ʒ֮���ϵ';
