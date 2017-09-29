drop table if exists fund_info;

/*==============================================================*/
/* Table: fund_info                                             */
/*==============================================================*/
CREATE TABLE `fund_info` (
   `wind_code` varchar(20) NOT NULL COMMENT '�������',
   `sec_name` varchar(100) DEFAULT NULL COMMENT '��������',
   `strategy_type` varchar(50) DEFAULT NULL COMMENT '�������͡�\n            ���fund_strategy���ӦΪ�գ���ʹ�ø���ֵ',
   `fund_setupdate` date DEFAULT NULL COMMENT '���������',
   `fund_maturitydate` date DEFAULT NULL COMMENT '������ֹ��',
   `fund_mgrcomp` varchar(200) DEFAULT NULL COMMENT '������',
   `fund_existingyear` double DEFAULT NULL COMMENT '��������',
   `fund_ptmyear` double DEFAULT NULL COMMENT '��������',
   `fund_type` varchar(50) DEFAULT NULL COMMENT '��������',
   `fund_fundmanager` varchar(200) DEFAULT NULL COMMENT '�����������Ϣ',
   `fund_status` int(11) DEFAULT NULL COMMENT '����״̬ 0 δ���У�1 ����',
   `alias` varchar(50) DEFAULT NULL COMMENT '����',
   `scale_tot` double DEFAULT NULL COMMENT '�ܹ�ģ',
   `scale_a` double DEFAULT NULL COMMENT 'A��ݶ��ģ��ļ���˵ķݶ�����ǽṹ���ݶ�',
   `scale_b` double DEFAULT NULL COMMENT 'B��ݶ��ģ��ļ���˵ķݶ�����ǽṹ���ݶ�',
   `priority_asset` double DEFAULT NULL COMMENT '���ȼ��ʲ���ģ',
   `inferior_asset` double DEFAULT NULL COMMENT '�Ӻ��ʲ���ģ',
   `priority_interest_rate` double DEFAULT NULL COMMENT '���ȼ��껪������',
   `source_mark` int(11) DEFAULT NULL COMMENT '����Դ 0��wind��1���ֶ�',
   `rank` int(11) DEFAULT NULL COMMENT '����������Ϣ Ĭ��0 δ������1 ����ע��2 �۲죻3 ��ѡ��4 ���ĳ�',
   `annual_return` double DEFAULT NULL COMMENT '�껯������',
   `nav_acc_mdd` double DEFAULT NULL COMMENT '���س���',
   `sharpe` double DEFAULT NULL COMMENT '���ձ���',
   `nav_acc_latest` double DEFAULT NULL COMMENT '���¾�ֵ',
   `nav_date_latest` date DEFAULT NULL COMMENT '���¾�ֵ����',
   `trade_date_latest` date DEFAULT NULL COMMENT '���½����գ�����ÿ��wind_fund_nav�����ݸ�����ʼ���ڲο�',
   `fh_inv_manager` varchar(20) DEFAULT NULL COMMENT 'Ͷ�ʸ�����',
   `fh_prod_manager` varchar(20) DEFAULT NULL COMMENT '��Ʒ������',
   `fh_channel_manager` varchar(20) DEFAULT NULL COMMENT '����������',
   `belongtofh` int(11) DEFAULT '0' COMMENT '0 ������˾����; 1 �������µĻ���',
   PRIMARY KEY (`wind_code`)
 ) ENGINE=MyISAM;