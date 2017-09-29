drop table if exists fund_incentive_fee_structure;

/*==============================================================*/
/* Table: fund_incentive_fee_structure                          */
/*==============================================================*/
create table fund_incentive_fee_structure
(
   id                   int not null AUTO_INCREMENT comment 'Ψһid',
   wind_code_p          varchar(20) comment 'ĸ�������',
   wind_code            varchar(20) comment '�ӻ������',
   nav_mark             double comment '��ֵ�Ƚϻ�׼',
   much                 double comment '��ȡ����',
   primary key (id)
) ENGINE=MyISAM;

alter table fund_incentive_fee_structure comment 'ҵ����ȡ incentive fee structure';
