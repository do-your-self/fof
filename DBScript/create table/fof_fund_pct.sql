drop index uk_fof_fund_pct on fof_fund_pct;

drop table if exists fof_fund_pct;

/*==============================================================*/
/* Table: fof_fund_pct                                          */
/*==============================================================*/
 CREATE TABLE `fof_fund_pct` (
   `id` int(11) NOT NULL AUTO_INCREMENT,
   `wind_code_p` varchar(20) NOT NULL COMMENT 'ĸ�������',
   `wind_code_s` varchar(20) NOT NULL COMMENT ' ��Ͷ�������',
   `date_adj` date NOT NULL COMMENT '��������',
   `invest_scale` double DEFAULT NULL COMMENT 'Ͷ�ʹ�ģ',
   PRIMARY KEY (`id`),
   UNIQUE KEY `uk_fof_fund_pct` (`wind_code_p`,`wind_code_s`,`date_adj`)
 ) ENGINE=MyISAM AUTO_INCREMENT=290 DEFAULT CHARSET=utf8