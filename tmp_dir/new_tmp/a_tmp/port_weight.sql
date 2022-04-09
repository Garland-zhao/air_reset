-- 组合列表
CREATE TABLE
IF
	NOT EXISTS portfolio_info (
        id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	    portfolio_id VARCHAR (255) NOT NULL UNIQUE COMMENT '组合ID唯一' ,
	    portfolio_name VARCHAR (255) NOT NULL UNIQUE COMMENT '组合名称唯一',
	    manager VARCHAR (255) NOT NULL COMMENT '管理人',
	    create_date Date NOT NULL COMMENT '创建日期',
	    abstract VARCHAR (255) NOT NULL COMMENT '摘要',
        updated_time TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE
    CURRENT_TIMESTAMP COMMENT '更新时间',
        INDEX port_id_index ( `portfolio_id` ),
        INDEX manager_index ( `manager` ),
        INDEX create_date_index ( `create_date` )
        USING BTREE
	) ENGINE = INNODB DEFAULT CHARSET = UTF8;


-- 组合明细表
CREATE TABLE
IF
	NOT EXISTS portfolio_detail (
        id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	    portfolio_id VARCHAR (255) NOT NULL COMMENT '组合ID',
	    portfolio_name VARCHAR (255) NOT NULL COMMENT '组合name',
        create_date Date NOT NULL COMMENT '创建日期',
	    fund_code VARCHAR (255) NOT NULL COMMENT '基金代码',
	    fund_name VARCHAR (255) NOT NULL COMMENT '基金名称',
        amount DOUBLE NOT NULL COMMENT '初始持仓金额， 单位元',
        INDEX port_id_index ( `portfolio_id` ),
        INDEX create_date_index ( `create_date` )
        USING BTREE
	) ENGINE = INNODB DEFAULT CHARSET = UTF8;


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
        INDEX port_id_index ( `portfolio_id` ),
        INDEX create_date_index ( `create_date` )
        USING BTREE
	) ENGINE = INNODB DEFAULT CHARSET = UTF8;

-- 组合收益
CREATE TABLE
IF
	NOT EXISTS portfolio_ret (
        id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	    portfolio_id VARCHAR (255) NOT NULL COMMENT '组合ID',
        create_date Date NOT NULL COMMENT '创建日期',
	    daily_total_amount DOUBLE NOT NULL COMMENT '总金额(组合每日持仓)，单位元',
	    daily_earnings_amount DOUBLE NOT NULL COMMENT '收益金额(组合每日持仓)，单位元',
        daily_ret DOUBLE NOT NULL COMMENT '收益率(组合每日持仓)， 0~1',
        time_weight_ret DOUBLE NOT NULL COMMENT '组合时间加权收益率， 0~1',
        cash DOUBLE NOT NULL COMMENT '现金持仓，单位元',
        updated_time TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE
    CURRENT_TIMESTAMP COMMENT '更新时间',
        INDEX port_id_index ( `portfolio_id` ),
        INDEX create_date_index ( `create_date` )
        USING BTREE
	) ENGINE = INNODB DEFAULT CHARSET = UTF8;


-- 历史曲线
CREATE TABLE
IF
	NOT EXISTS history_line (
        id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	    portfolio_id VARCHAR (255) NOT NULL COMMENT '组合ID唯一',
        create_date Date NOT NULL COMMENT '创建日期',
	    daily_earnings_amount DOUBLE NOT NULL COMMENT '昨日收益',
	    time_weight_ret DOUBLE NOT NULL COMMENT '时间加权收益率(相对于初始)， 0~1',
        daily_total_amount DOUBLE NOT NULL COMMENT '现持仓金额',
        INDEX port_id_index ( `portfolio_id` ),
        INDEX create_date_index ( `create_date` )
        USING BTREE
	) ENGINE = INNODB DEFAULT CHARSET = UTF8;

