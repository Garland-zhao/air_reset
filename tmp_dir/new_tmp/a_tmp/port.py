class PortfolioInfo(ModelBase):
    """组合列表"""

    __tablename__ = 'portfolio_info'
    portfolio_id = Column(String(32), index=True,
                          unique=True, comment='组合ID唯一', nullable=False)
    portfolio_name = Column(String(64), unique=True,
                            nullable=False, comment="组合名称唯一")
    manager = Column(String(64), nullable=False, comment='管理人')
    create_date = Column(Date, nullable=False, index=True, comment='创建日期')
    total_amount = Column(DECIMAL(40, 2), nullable=False, comment='账户总金额，单位元')
    history_ret = Column(Float, comment='至今业绩， 0~1')
    abstract = Column(String(128), comment='摘要')
    updated_time = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='更新日期')
    __table_args__ = (UniqueConstraint(
        'portfolio_id', 'portfolio_name', name='portfolio_id_name'),)



class PortfolioInfoNew(ModelBase):
    """组合列表"""
    __tablename__ = 'portfolio_info_new'
    portfolio_id = Column(String(32), index=True,
                          unique=True, comment='组合ID唯一', nullable=False)
    portfolio_name = Column(String(64), unique=True,
                            nullable=False, comment="组合名称唯一")
    manager = Column(String(64), nullable=False, comment='管理人')
    create_date = Column(Date, nullable=False, index=True, comment='创建日期')
    abstract = Column(String(128), comment='摘要')
    updated_time = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='更新日期')
    __table_args__ = (UniqueConstraint(
        'portfolio_id', 'portfolio_name', name='portfolio_id_name'),)



class PortfolioDetailNew(ModelBase):
    """组合明细新表"""

    __tablename__ = 'portfolio_detail_new'
    portfolio_id = Column(String(32), index=True,
                          comment='组合ID', nullable=False)
    create_date = Column(Date, nullable=False, index=True, comment='创建日期')
    stock_code = Column(String(32), nullable=False, comment="股票代码")
    stock_name = Column(String(64), nullable=False, comment='股票名称')
    amount = Column(DECIMAL(40, 2), nullable=False, comment='初始持仓金额， 单位元')

    __table_args__ = (UniqueConstraint(
        'portfolio_id', 'stock_code', 'create_date', name='portfolio_id_code_date'),)


class PortfolioDetail(ModelBase):
    """组合明细"""

    __tablename__ = 'portfolio_detail'
    portfolio_id = Column(String(32), index=True,
                          comment='组合ID', nullable=False)
    create_date = Column(Date, nullable=False, index=True, comment='创建日期')
    stock_code = Column(String(32), nullable=False, comment="股票代码")
    stock_name = Column(String(64), nullable=False, comment='股票名称')
    amount = Column(DECIMAL(40, 2), nullable=False, comment='持仓金额， 单位元')
    rebalance_flag = Column(Integer, nullable=False,
                            comment='标志, 首次调仓:1,　非调仓:0， 再次调仓:2')
    updated_time = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='更新日期')
    weight = Column(DECIMAL(17, 16), comment='权重，0~1')

    __table_args__ = (UniqueConstraint(
        'portfolio_id', 'stock_code', 'create_date', name='portfolio_id_code_date'),)




class PortfolioBenchmark(ModelBase):
    """组合基准"""

    __tablename__ = 'portfolio_benchmark'
    portfolio_id = Column(String(32), index=True,
                          comment='组合ID', nullable=False)
    create_date = Column(Date, nullable=False, index=True, comment='创建日期')
    benchmark_code = Column(String(32), nullable=False, comment="基准代码")
    benchmark_name = Column(String(64), nullable=False, comment='基准名称')
    weight = Column(Float, nullable=False, comment='权重，0~100')
    updated_time = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='更新日期')


class PortfolioBenchmarkNew(ModelBase):
    """组合基准"""

    __tablename__ = 'portfolio_benchmark_new'
    portfolio_id = Column(String(32), index=True,
                          comment='组合ID', nullable=False)
    create_date = Column(Date, nullable=False, index=True, comment='创建日期')
    benchmark_code = Column(String(32), nullable=False, comment="基准代码")
    benchmark_name = Column(String(64), nullable=False, comment='基准名称')
    weight = Column(Float, nullable=False, comment='权重，0~100')
    updated_time = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='更新日期')

    __table_args__ = (UniqueConstraint(
        'portfolio_id', 'benchmark_code', 'create_date', name='portfolio_id_mark_date'),)


class PortfolioRet(ModelBase):
    """组合收益"""

    __tablename__ = 'portfolio_ret'

    portfolio_id = Column(String(32), index=True,
                          comment='组合ID唯一', nullable=False)
    create_date = Column(Date, nullable=False, index=True, comment='创建日期')
    daily_total_amount = Column(
        DECIMAL(40, 2), nullable=False, comment='总金额(组合每日持仓)，单位元')
    daily_earnings_amount = Column(
        DECIMAL(40, 2), nullable=False, comment='收益金额(组合每日持仓)，单位元')
    daily_ret = Column(Float, comment='收益率(组合每日持仓)， 0~1')
    time_weight_ret = Column(Float, comment='组合时间加权收益率， 0~1')
    cash = Column(DECIMAL(40, 2), nullable=False, comment='现金持仓，单位元')
    updated_time = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='更新日期')
    __table_args__ = (UniqueConstraint(
        'portfolio_id', 'create_date', name='portfolio_id_date'),)


class HistoryLine(ModelBase):
    """历史曲线"""
    __tablename__ = 'history_line'

    portfolio_id = Column(String(32), index=True,
                          comment='组合ID唯一', nullable=False)
    create_date = Column(Date, nullable=False, index=True, comment='创建日期')
    daily_earnings_amount = Column(
        Float, nullable=False, comment='昨日收益')

    time_weight_ret = Column(Float, comment='时间加权收益率(相对于初始)， 0~1')
    daily_total_amount = Column(
        DECIMAL(40, 2), nullable=False, comment='现持仓金额')

    __table_args__ = (UniqueConstraint(
        'portfolio_id', 'create_date', name='portfolio_id_date'),)