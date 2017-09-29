CREATE TABLE `fof_ams_dev`.`wind_future_daily` (
  `wind_code` VARCHAR(20) NOT NULL,
  `trade_date` DATE NOT NULL,
  `open` FLOAT NULL,
  `high` FLOAT NULL,
  `low` FLOAT NULL,
  `close` FLOAT NULL,
  `volume` FLOAT NULL,
  `amt` FLOAT NULL,
  `dealnum` FLOAT NULL COMMENT '�ɽ�������ͳ����ʳɽ�������',
  `settle` FLOAT NULL COMMENT '�����',
  `maxupordown` INT NULL COMMENT '���������ͣ���ͣ״̬,1��ʾ��ͣ��-1���ʾ��ͣ��0��ʾδ�ǵ�ͣ��',
  `oi` FLOAT NULL COMMENT '�ֲ���',
  `st_stock` FLOAT NULL COMMENT 'ע��ֵ�����',
  PRIMARY KEY (`wind_code`, `trade_date`))
ENGINE = MyISAM;
