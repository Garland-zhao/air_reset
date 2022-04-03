import pandas as pd

from common.utils import TokenHandler
from firp_db.mysql.base import User
from firp_db.mysql.base import Similarity
from firp_db.redis.similarity import SimilarityTask
from firp_db.redis.similarity import SimilarityPortCache


# ---------------------------------- Request --------------------------------------------
def current_user():
    """从token获取当前用户sub

    :return: 用户sub
    """
    return TokenHandler.current_user()


def base_user_info():
    """从token获取基本用户信息

    :return:
    """
    return TokenHandler.base_user_info()


# ----------------------------------- Redis ---------------------------------------------
def exist_current_user_task(sub):
    """检索当前用户是否存在任务

    :param sub: 用户sub
    :return: user_task_key or None
    """
    return SimilarityTask.current_user_task_exist(sub)


def exist_similar_user_task(ticker, compute_date, size, white_id):
    """判断该相似性任务是否在用户队列中"""
    task = f"*:{SimilarityTask.task_key(ticker, compute_date, size, white_id)}"
    return SimilarityTask.exist_in_user_queue(task)


def exist_similar_task(ticker, compute_date, size, white_id):
    """判断该相似性任务是否在队列中"""
    task = SimilarityTask.task_key(ticker, compute_date, size, white_id)
    return SimilarityTask.exist_in_task_queue(task)


def exist_similar_result(ticker, compute_date, size, white_id):
    """判断该相似性任务的结果是否已缓存"""
    r = SimilarityPortCache()
    return r.exist_similarity_task(ticker, compute_date, size, white_id)


def create_similarity_task(sub, ticker, compute_date, size, white_id, status="new"):
    """生成相似性组合计算

    :param sub: 用户sub
    :param ticker: 需要计算相似性的基金, 不带.OF
    :param compute_date: 追踪时间
    :param size: 生成每支组合中基金的数量
    :param white_id: 白名单id
    :param status: 任务状态
    """
    SimilarityTask.generate_task(ticker, compute_date, size, white_id, sub, status)


def get_similar_task():
    ''' 从任务队列里面 取出一个任务, 如果没有任务则会阻塞 '''
    return SimilarityTask.next_task()


def get_similarity_task_data(ticker, compute_date, size, white_id, port_id):
    """从redis中获取似性任务计算结果

    :param ticker: 需要计算相似性的基金，不带.OF
    :param compute_date: 追踪时间
    :param size: 生成每支组合中基金的数量
    :param white_id: 白名单id
    :param port_id: 生成的组合的id
    :return data_mapping: {fund_code: weight, ...}
    """
    r = SimilarityPortCache()
    data_mapping = r.get_task_data(ticker, compute_date, size, white_id, port_id)
    return data_mapping


def similarity_page_data(ticker, compute_date, size, white_id, port_id, data=None):
    """在redis中缓存或检索相似性页面结果

    :param ticker: 需要计算相似性的基金，不带.OF
    :param compute_date: 追踪时间
    :param size: 生成每支组合中基金的数量
    :param white_id: 白名单id
    :param port_id: 生成的组合的id
    :param data: 相似性页面的全部计算结果(port, ind, ret)
    :type data: dict
    :return data_mapping: {"similarity_port_detail":[...],
                           "port_industry_detail": [...],
                           "back_test_interval": [...],
                           "verification_interval": [...]}

    :rtype data_mapping: dict
    """
    r = SimilarityPortCache()
    if data:
        # 缓存相似性页面计算结果
        r.set_similarity_data(ticker, compute_date, size, white_id, port_id, data)
        return
    # 检索相似性页面计算结果
    data_mapping = r.get_similarity_data(ticker, compute_date, size, white_id, port_id)
    return data_mapping


def cache_similarity_task_data(ticker, compute_date, size, white_id, data):
    """缓存相似性任务计算结果

    :param ticker: 需要计算相似性的基金，不带.OF
    :param compute_date: 追踪时间
    :param size: 生成每支组合中基金的数量
    :param white_id: 白名单id
    :param data: [Series, ...]
    :type data: list
    """
    r = SimilarityPortCache()
    r.cache_task_data(ticker, compute_date, size, white_id, data)


def update_user_similar_task_status(ticker, compute_date, size, white_id, status=0, sub=None):
    """修改用户队列中的相似性任务状态为"""
    task_key = SimilarityTask.task_key(ticker, compute_date, size, white_id)
    SimilarityTask.update_user_task(task_key, status=status, sub=sub)


def user_similar_history(sub, limit=10):
    """用户生成的相似性任务历史记录

    :param sub: 用户sub
    :param limit: 返回的记录最大条数
    :return:
    """
    return SimilarityTask.current_user_task(sub, limit)


def all_user_similar_history():
    """获取所有基金相似性组合的用户任务记录"""
    return SimilarityTask.all_user_task()


# ----------------------------------- MySQL ---------------------------------------------
def user_exist(sub):
    """判断用户是否存在

    :param sub: 用户sub
    :return:
    """
    df = User.user_exist(sub)
    return not df.empty


def add_firp_user():
    """添加用户到firp_user

    :return:
    """
    df = TokenHandler.base_user_info()
    User.add_user(df)


def get_userinfo(sub):
    """获取用户信息

    :param sub: 用户sub
    :return: 用户信息 DataFrame
    """
    df = User.get_user(sub)
    df = pd.pivot(df, index="sub", columns="colum_key", values="colum_val")
    df = df.rename_axis(columns=None)
    df = df.reset_index()
    return df


def get_all_username():
    """获取所有用户名称

    :return: 所有用户名称和sub
    :rtype: DataFrame
    """
    return User.get_all_username()


def get_similar_port(sub, _id=None, port_name=None,
                     target_code=None, target_name=None,
                     page=None, page_size=10):
    """获取已保存的相似性组合数据

    :param sub: 用户sub
    :param _id: 相似性组合的id
    :param port_name: 相似性组合的名称
    :param target_code: 目标基金代码或者目标基金组合id
    :param target_name: 标基金名称或者目标基金组合名称
    :param page: 页码
    :param page_size: 每页返回数量
    :return: 保存的相似性组合数据
    :rtype: DataFrame
    """
    if _id:
        df = Similarity.get_similar_port_by_id(sub, _id)
    elif port_name:
        df = Similarity.get_similar_port_by_port_name(sub, port_name)
    elif page:
        df = Similarity.get_similar_list_by_targe_code(sub, target_code, page, page_size)
    elif target_code:
        df = Similarity.get_similar_port_by_target_code(sub, target_code, limit=1)
    elif target_name:
        df = Similarity.get_similar_port_by_target_name(sub, target_name, limit=1)
    else:
        df = Similarity.get_similar_port_by_sub(sub)
    return df


def save_similar_port(df):
    """保存相似性组合到MySQL

    :param df: 需要保存的相似性组合数据
    :type df: DataFrame
    """
    Similarity.save(df)


def remove_similar_port(ids):
    """(批量)删除相似性组合

    :param ids: 待删除的相似性组合的ids
    :type ids: tuple or list
    :return:
    """
    Similarity.remove(ids)


def get_fund_port_name_by_id(_id):
    """根据基金组合id查询基金组合名称"""
    pass


def check_user_similarity_port_exists(target_code, compute_date, pool_size, white_list, port_num):
    return Similarity.check_data_live(target_code, compute_date, pool_size, white_list, port_num)


if __name__ == '__main__':
    ticker = '001384'
    compute_date = '2022-03-25'
    size = 3
    white_id = 'all_fund'
    if exist_similar_result(ticker, compute_date, size, white_id):
        print('cached')
    else:
        print('no cache')

