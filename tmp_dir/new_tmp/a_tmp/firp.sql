-- firp_user
CREATE TABLE
IF
	NOT EXISTS firp_user (
	    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
		sub VARCHAR ( 255 ) NOT NULL COMMENT '用户id',
		colum_key VARCHAR ( 255 ) NOT NULL COMMENT '用户信息字段名',
		colum_val VARCHAR ( 255 ) NOT NULL COMMENT '用户信息字段值',
		INDEX sub_index ( `sub` )
	) ENGINE = INNODB DEFAULT CHARSET = UTF8;

-- fund_similarity_port
CREATE TABLE
IF
	NOT EXISTS fund_similarity_port (
	    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	    sub VARCHAR (255) NOT NULL COMMENT '用户id',
	    tracker VARCHAR (255) NOT NULL COMMENT '追踪人id',
	    target_code VARCHAR (255) NOT NULL COMMENT '需要计算相似性的基金代码或基金组合id',
	    target_name VARCHAR (255) NOT NULL COMMENT '需要计算相似性的基金名称或基金组合名称',
	    port_name VARCHAR (255) NOT NULL COMMENT '保存的自定义组合名称',
	    white_list VARCHAR (255) NOT NULL COMMENT '白名单id or all_fund',
	    port_num int NOT NULL COMMENT '保存的自定义组合序号',
	    port_size int NOT NULL COMMENT '每个组合中基金的数量',
	    compute_date VARCHAR (255) NOT NULL COMMENT '计算日期, eg:2020-02-18',
        similarity_port_detail MEDIUMTEXT NOT NULL COMMENT '相似基金名称和权重',
        port_industry_detail MEDIUMTEXT NOT NULL COMMENT '行业组合详情',
        back_test_interval MEDIUMTEXT COMMENT '回测区间详情',
        verification_interval MEDIUMTEXT COMMENT '验证区间详情',
        create_time datetime NOT NULL COMMENT '保存时间',
        update_time datetime NOT NULL COMMENT '更新时间',
        INDEX sub_index ( `sub` ),
        INDEX port_name_index ( `port_name` ),
        UNIQUE KEY `sub_port_name` (`sub`, `tracker`, `port_name`) USING BTREE
	) ENGINE = INNODB DEFAULT CHARSET = UTF8;

-- portfolio_detail
CREATE TABLE
IF
	NOT EXISTS portfolio_detail (
        id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	    portfolio_id VARCHAR (255) NOT NULL COMMENT '组合ID',
	    portfolio_name VARCHAR (255) NOT NULL COMMENT '组合名称',
        create_date Date NOT NULL COMMENT '创建日期',
        updated_time timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日期',
	    fund_code VARCHAR (255) NOT NULL COMMENT '基金代码',
	    fund_name VARCHAR (255) NOT NULL COMMENT '基金名称',
        amount DOUBLE NOT NULL COMMENT '初始持仓金额， 单位元',
        sub VARCHAR (255) NOT NULL COMMENT '用户sub',
        manager VARCHAR (255) NOT NULL COMMENT '管理者',
        INDEX port_id_index ( `portfolio_id` ),
        INDEX create_date_index ( `create_date` )
        USING BTREE
	) ENGINE = INNODB DEFAULT CHARSET = UTF8;

-- portfolio_holding
CREATE TABLE `portfolio_holding` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `portfolio_id` varchar(255) NOT NULL COMMENT '组合ID',
  `fund_code` varchar(255) NOT NULL COMMENT '基金代码',
  `holding_weight` decimal(10,8) NOT NULL COMMENT '持仓占比',
  `holding_amount` decimal(22,4) NOT NULL COMMENT '持仓金额',
  `fund_chg` decimal(10,6) DEFAULT '0.000000' COMMENT '基金日收益率',
  `fund_accu_chg` decimal(10,6) DEFAULT '0.000000' COMMENT '基金累计收益率',
  `year_earnings_chg` decimal(10,6) DEFAULT '0.000000' COMMENT '近一年收益',
  `trading_day` date NOT NULL COMMENT '交易日期',
  PRIMARY KEY (`id`),
  UNIQUE KEY `port_fund_trad` (`portfolio_id`,`fund_code`,`trading_day`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 COMMENT='组合持仓明细表';

-- 组合基准
CREATE TABLE
IF
	NOT EXISTS portfolio_benchmark (
        id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	    portfolio_id VARCHAR (255) NOT NULL COMMENT '组合ID',
        create_date Date NOT NULL COMMENT '创建日期',
	    benchmark_code VARCHAR (255) NOT NULL COMMENT '基准代码',
	    benchmark_name VARCHAR (255) NOT NULL COMMENT '基准名称',
	    benchmark_type VARCHAR (255) NOT NULL COMMENT '基准类型:0-基金, 1-股票, 2-指数',
        weight DOUBLE NOT NULL COMMENT '权重，0~100',
        updated_time TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE
    CURRENT_TIMESTAMP COMMENT '更新时间',
        UNIQUE KEY `port_sub_trad` (`portfolio_id`,`trading_day`) USING BTREE
	) ENGINE = INNODB DEFAULT CHARSET = UTF8;