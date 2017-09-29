drop index uk_fund_sec_pct on fund_sec_pct;

drop table if exists fund_sec_pct;

/*==============================================================*/
/* Table: fund_sec_pct                                          */
/*==============================================================*/
create table fund_sec_pct
(
   id                   int not null AUTO_INCREMENT,
   wind_code            varchar(20) not null comment 'wind_code ����Ǹ����Լ����ӻ���򸴻�Ͷ�ʵ�δ������Ʒ�����Ǹ�������',
   sec_code             varchar(20) not null,
   nav_date             date not null comment '��ֵ����',
   direction            int not null comment '����1 ���ࣻ0 ����
            ��ƱĬ��Ϊ��
            ��ָĬ�ϱ��澻�յ�',
   position             int comment '�ֲ�����',
   cost_unit            double comment ' ��λ�ɱ�',
   cost_tot             double comment '�ܳɱ�',
   cost_pct             double comment '�ɱ�ռ��',
   value_tot            double comment '�ֲ���ֵ',
   value_pct            double comment '��ֵռ��',
   trade_status         varchar(200),
   sec_type             int comment '֤ȯ���� 0����Ʊ��1���ڻ���2��ծȯ��3����ع�',
   primary key (id),
   UNIQUE KEY `uk_fund_sec_pct` (`wind_code`,`sec_code`,`nav_date`,`direction`)
) ENGINE=MyISAM;
