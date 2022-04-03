import pandas as pd
from firp_db.mysql import engine


class User:
    """用户信息表"""

    @staticmethod
    def get_user(sub):
        """获取指定用户信息"""
        sql = f"""select sub, colum_key, colum_val
              from firp_user where sub = '{sub}'
              """
        return pd.read_sql(sql, engine)

    @staticmethod
    def get_all_username():
        """获取所有用户名称"""
        sql = """select sub, colum_val as username
        from firp_user where colum_key = 'username'
        """
        return pd.read_sql(sql, engine)

    @staticmethod
    def user_exist(sub):
        """判断用户是否存在"""
        sql = f"""select 1 from firp_user
         where sub = '{sub}'"""
        return pd.read_sql(sql, engine)

    @staticmethod
    def add_user(df):
        """添加用户到firp_user"""
        df.to_sql('firp_user', engine, if_exists='append', index=False)


class Similarity:
    """追踪相似性组合表"""

    @staticmethod
    def check_data_live(target_code, compute_date, pool_size, white_list, port_num):
        sql = f"""
            SELECT port_name FROM fund_similarity_port
            WHERE white_list='{white_list}'
            AND port_num={port_num}
            AND port_size={pool_size}
            AND compute_date='{compute_date}'
            AND target_code='{target_code}'
            """
        return pd.read_sql(sql, engine)

    @staticmethod
    def get_similar_port_by_id(sub, _id):
        """根据id查询用户追踪的相似性组合"""
        sql = f"""
        SELECT id, sub, tracker, port_name, target_code, target_name,
            compute_date, similarity_port_detail, port_industry_detail,
            back_test_interval, verification_interval
        FROM fund_similarity_port
        WHERE sub='{sub}' AND id={_id}
        """
        return pd.read_sql(sql, engine)

    @staticmethod
    def get_similar_port_by_sub(sub):
        """查询用户所有追踪的相似性组合"""
        """"""
        sql = f"""
        SELECT target_code, target_name
        FROM fund_similarity_port
        WHERE sub='{sub}'
        ORDER BY create_time DESC
        """
        return pd.read_sql(sql, engine)

    @staticmethod
    def get_similar_port_by_port_name(sub, port_name):
        """根据保存的名称查询用户追踪的相似性组合"""
        sql = f"""
        SELECT id, sub, tracker, port_name, target_code, target_name,
            compute_date, similarity_port_detail, port_industry_detail,
            back_test_interval, verification_interval
        FROM fund_similarity_port
        WHERE sub='{sub}' AND port_name='{port_name}'
        """
        return pd.read_sql(sql, engine)

    @staticmethod
    def get_similar_port_by_target_code(sub, target_code, limit=None):
        """根据目标基金代码或者目标基金组合id查询用户追踪的相似性组合"""
        if limit:
            sql = f"""
            SELECT id, sub, tracker, port_name, target_code, target_name,
                compute_date, similarity_port_detail, port_industry_detail,
                back_test_interval, verification_interval
            FROM fund_similarity_port
            WHERE sub='{sub}' AND target_code='{target_code}'
            ORDER BY create_time DESC
            LIMIT {limit}
            """
        else:
            sql = f"""
            SELECT id, sub, tracker, port_name, target_code, target_name,
                compute_date, similarity_port_detail, port_industry_detail,
                back_test_interval, verification_interval
            FROM fund_similarity_port
            WHERE sub='{sub}' AND target_code='{target_code}'
            ORDER BY create_time DESC
            """
        return pd.read_sql(sql, engine)

    @staticmethod
    def get_similar_port_by_target_name(sub, target_name, limit=None):
        """根据目标基金名称或者目标基金组合名称查询用户追踪的相似性组合"""
        if limit:
            sql = f"""
            SELECT id, sub, tracker, port_name, target_code, target_name,
                compute_date, similarity_port_detail, port_industry_detail,
                back_test_interval, verification_interval
            FROM fund_similarity_port
            WHERE sub='{sub}' AND target_name='{target_name}'
            ORDER BY create_time DESC
            LIMIT {limit}
            """
        else:
            sql = f"""
            SELECT id, sub, tracker, port_name, target_code, target_name,
                compute_date, similarity_port_detail, port_industry_detail,
                back_test_interval, verification_interval
            FROM fund_similarity_port
            WHERE sub='{sub}' AND target_name='{target_name}'
            ORDER BY create_time DESC
            """
        return pd.read_sql(sql, engine)

    @staticmethod
    def get_similar_list_by_targe_code(sub, targe_code, page, page_size=10):
        """根据目标基金代码或者目标基金组合id查询用户追踪的相似性组合列表"""
        sql = f"""
        SELECT id, port_name, target_code, target_name, create_time as tracking_time, tracker
        FROM fund_similarity_port
        WHERE sub='{sub}' AND target_code='{targe_code}'
        ORDER BY create_time DESC
        LIMIT {page - 1}, {page_size}
        """
        df = pd.read_sql(sql, engine)
        df.tracking_time = df.tracking_time.apply(lambda x: x.strftime('%F'))
        return df

    @staticmethod
    def save(df):
        """追踪(保存)相似性计算结果"""
        df.to_sql('fund_similarity_port', engine, if_exists='append', index=False)

    @staticmethod
    def remove(ids):
        """停止追踪(删除)相似性计算结果"""
        if isinstance(ids, list):
            ids = tuple(ids)
        if len(ids) == 1:
            sql = f"delete from fund_similarity_port where id = {ids[0]}"
        else:
            sql = f"delete from fund_similarity_port where id in {ids}"
        engine.execute(sql)


if __name__ == "__main__":
    ''' python -m firp_db.mysql.base '''
    fund_code = '001384.OF'
    compute_date = '2022-03-02'
    pool_size = 5
    white_list = 'all_fund'
    port_num = 0
    res = Similarity.check_data_live(fund_code, compute_date, pool_size, white_list, port_num)
    if not res.empty:
        print(123)
    else:
        print(456)
