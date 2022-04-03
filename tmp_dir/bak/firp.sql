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
	    white_list_name VARCHAR (100) NOT NULL COMMENT '白名单名称',
	    port_num int NOT NULL COMMENT '保存的自定义组合序号',
	    fund_code VARCHAR (100) NOT NULL COMMENT '基金代码',
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