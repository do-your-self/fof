drop table if exists fund_nav_calc;

CREATE TABLE fund_nav_calc (
   `wind_code` varchar(20) NOT NULL,
   `nav_date` date NOT NULL,
   `share` float DEFAULT '0' COMMENT '����ݶ�',
   `market_value` float DEFAULT '0' COMMENT '������ֵ',
   `cash_amount` float DEFAULT '0' COMMENT '�����ֽ����',
   `manage_fee` float DEFAULT '0' COMMENT '�����',
   `custodian_fee` float DEFAULT '0' COMMENT '�йܷ�',
   `admin_fee` float DEFAULT '0' COMMENT '���������',
   `storage_fee` float DEFAULT '0' COMMENT '�ͻ�ר���ʽ𱣹�',
   `other_fee` float DEFAULT '0' COMMENT '�������ã����ڱ�������δ�����ķ��ã���Ҫ���ֹ���дʹ�ã�',
   `nav` float DEFAULT '1' COMMENT '����ֵ',
   PRIMARY KEY (`wind_code`,`nav_date`)
 ) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='����ֵ��������ӻ���ĸ����ֵ����ʹ��';
 