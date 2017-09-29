drop table if exists fund_event;

/*==============================================================*/
/* Table: fund_event                                            */
/*==============================================================*/
CREATE TABLE `fund_event` (
   `id` int(11) NOT NULL AUTO_INCREMENT,
   `wind_code` varchar(20) NOT NULL COMMENT '�������',
   `event_date` date NOT NULL COMMENT '�¼�����',
   `event_type` varchar(20) NOT NULL COMMENT '�¼�����',
   `remind_date` date DEFAULT NULL COMMENT '������ʼ����',
   `handle_status` tinyint(4) DEFAULT NULL COMMENT '����״̬ 0��������1���Ѵ���',
   `description` text COMMENT '��ʾ��Ϣ',
   `create_date` date DEFAULT NULL COMMENT '�¼���������',
   `color` varchar(20) DEFAULT NULL,
   `create_user` varchar(45) DEFAULT NULL,
   `private` tinyint(4) DEFAULT NULL,
   PRIMARY KEY (`id`)
 ) ENGINE=MyISAM AUTO_INCREMENT=34 DEFAULT CHARSET=utf8;
