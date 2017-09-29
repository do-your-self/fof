drop table if exists fund_file;

/*==============================================================*/
/* Table: fund_file                                    */
/*==============================================================*/
CREATE TABLE `fund_file` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `wind_code` varchar(20) DEFAULT NULL COMMENT '�������',
  `type_name` varchar(100) DEFAULT NULL COMMENT '�ļ����ͣ������ͬ��Ͷ��ָ�ϵȣ����ַ��洢',
  `upload_datetime` datetime DEFAULT NULL,
  `show_name` varchar(500) DEFAULT NULL,
  `file_content` longblob,
  PRIMARY KEY (`id`),
  KEY `file_type` (`type_name`),
  KEY `wind_code` (`wind_code`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
