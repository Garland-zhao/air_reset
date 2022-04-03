-- port_weight_table
CREATE TABLE
IF
	NOT EXISTS port_weight_table (
	    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	    port_id VARCHAR (255) NOT NULL COMMENT '组合id',
	    fund_code VARCHAR (255) NOT NULL COMMENT '基金代码',
	    fund_name VARCHAR (255) NOT NULL COMMENT '基金名称',
	    holding_weight DOUBLE NOT NULL COMMENT '持仓占比',
        holding_amount DOUBLE NOT NULL COMMENT '持仓金额',
        rebalance_flag Int NOT NULL COMMENT '调仓标记',
        trading_day Date NOT NULL COMMENT '插入时间',
        INDEX port_id_index ( `port_id` ),
        INDEX fund_code_index ( `fund_code` ),
        UNIQUE KEY `id_fund_date` (`port_id`, `fund_code`, `trading_day`)
        USING BTREE
	) ENGINE = INNODB DEFAULT CHARSET = UTF8;


--  port_weight_table
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