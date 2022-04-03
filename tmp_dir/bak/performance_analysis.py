"""基金研究/业绩分析"""

import time
import json
import datetime
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
from flask_restplus import Namespace
from flask_restplus import Resource

import common.utils as lt
from common.http_conf import HttpCode
from common.model_config import months_to_days_map
from common.model_config import SimilarType
from common.log import webapi_logger as logger
from common.common_compute import ComputeSimilarInterval
from firp_db.data_service import get_userinfo
from firp_db.data_service import current_user
from firp_db.data_service import get_similar_port
from firp_db.data_service import get_all_username
from firp_db.data_service import save_similar_port
from firp_db.data_service import remove_similar_port
from firp_db.data_service import similarity_page_data
from firp_db.data_service import create_similarity_task
from firp_db.data_service import check_user_similarity_port_exists
from firp_db.data_service import exist_similar_user_task
from firp_db.data_service import exist_similar_task
from firp_db.data_service import exist_similar_result
from firp_db.data_service import get_similarity_task_data
from firp_db.data_service import user_similar_history
from firp_db.data_service import get_fund_port_name_by_id
from iodb.data_service import get_last_nav
from iodb.data_service import get_fundinfo
from iodb.data_service import get_fund_name_by_fund_code
from iodb.data_service import get_rt_evaluation_data
from iodb.data_service import get_rt_ev_data_histline
from iodb.data_service import get_port_industry_weight
from iodb.data_service import get_key_stock_by_fund_code

ns = Namespace('fund_research/performance_analysis',
               description='基金研究/业绩分析相关接口', )

# 实时估值参数
rt_e_parser = ns.parser()
rt_e_parser.add_argument('fund_code', type=str,
                         required=True, help='基金代码', location='args')

# 基金重仓股、债接口参数
hhf_parser = ns.parser()
hhf_parser.add_argument('fund_code', type=str,
                        required=True, help='基金代码', location='args')

# 估值曲线参数
vh_parser = ns.parser()
vh_parser.add_argument('fund_code', type=str,
                       required=True, help='基金代码', location='args')

# 生成相似组合参数get
gsp_parser = ns.parser()
gsp_parser.add_argument('fund_code', type=str,
                        required=True, help='基金代码', location='args')
gsp_parser.add_argument('compute_date', type=str,
                        required=True, help='计算日期', location='args')
gsp_parser.add_argument('pool_size', type=int, default=3,
                        help='每个组合包含的基金数量', location='args')
gsp_parser.add_argument('white_list', type=str, default="all_fund",
                        help='白名单', location='args')
gsp_parser.add_argument('port_num', type=int, default=0,
                        help='相似组合序号', location='args')

# 生成相似组合参数post
gsp_post_parser = ns.parser()
gsp_post_parser.add_argument('fund_code', type=str,
                             required=True, help='基金代码', location='form')
gsp_post_parser.add_argument('compute_date', type=str,
                             required=True, help='计算日期', location='form')
gsp_post_parser.add_argument('pool_size', type=int, default=3,
                             help='每个组合包含的基金数量', location='form')
gsp_post_parser.add_argument('white_list', type=str, default="all_fund",
                             help='白名单', location='form')

# 追踪相似组合参数
tsp_get_parser = ns.parser()
tsp_get_parser.add_argument('id', type=int, default=None, help='相似组合id', location='args')
tsp_get_parser.add_argument('port_name', type=str, default=None, help='保存的名称', location='args')
tsp_get_parser.add_argument('target_code', type=str, default=None, help='目标基金代码或目标基金组合id', location='args')
tsp_get_parser.add_argument('target_name', type=str, default=None, help='目标基金名称或目标基金组合名称', location='args')

tsp_del_parser = ns.parser()
tsp_del_parser.add_argument("port_id_list", type=str,
                            required=True, help="相似组合id列表", location="args")
tsp_parser = ns.parser()
tsp_parser.add_argument('fund_code', type=str,
                        required=True, help='基金代码', location='form')
tsp_parser.add_argument('compute_date', type=str,
                        required=True, help='计算日期', location='form')
tsp_parser.add_argument('pool_size', type=int, default=3,
                        help='每个组合包含的基金数量', location='form')
tsp_parser.add_argument('white_list', type=str, default="all_fund",
                        help='白名单', location='form')
tsp_parser.add_argument('port_num', type=int, default=0,
                        help='相似组合序号', location='form')
tsp_parser.add_argument('port_name', type=str,
                        required=True, help='相似组合名称', location='form')

# 追踪相似组合列表参数
tsp_list_parser = ns.parser()
tsp_list_parser.add_argument('page_num', type=int, default=1,
                             help='页码', location='args')
tsp_list_parser.add_argument('page_size', type=int, default=20,
                             help='每页条数', location='args')
tsp_list_parser.add_argument('target_code', type=str, help='目标基金代码或目标基金组合id', location='args')

# 验证相似性组合白名单
check_white_list_parser = ns.parser()
check_white_list_parser.add_argument('white_code', type=str, required=True, help='白名单id', location='args')


@ns.route('/realtime_evaluation')
class RealTimeEvaluation(Resource):
    @ns.doc(parser=rt_e_parser, description='实时估值')
    def get(self):
        res = lt.get_api_response_template_copy()
        # 获取参数
        args = rt_e_parser.parse_args()
        fund_code = args.fund_code
        data = {}
        # 获取净值相关数据
        nav = get_last_nav(fund_code)
        if nav.empty:
            return res
        data['trading_day'] = nav.trading_day.strftime('%F')
        data['unit_nav'] = nav.nv
        data['acc_nav'] = nav.accumulative_nv
        data['nav_chg'] = nav.nv_growth_rate
        res['data'] = data

        # 实时估值数据
        rt_df, lastest_navest, lastest_chg, lastest_time = get_rt_evaluation_data(fund_code)
        if rt_df.empty:
            res['data']['lastest_navest'] = lastest_navest
            res['data']['lastest_chg'] = lastest_chg
            res['data']['lastest_time'] = None if not lastest_time else pd.to_datetime(lastest_time).strftime('%F '
                                                                                                              '%H:%M')
            return res
        if not rt_df.empty:
            rt_df = rt_df.round(6)
        rt_df = rt_df.where(rt_df.notnull(), None)
        # 更改日期格式
        dt = pd.to_datetime(rt_df.time)
        rt_df.time = dt.apply(lambda x: x.strftime('%F %H:%M'))

        res['data']['lastest_navest'] = lastest_navest
        res['data']['lastest_chg'] = lastest_chg
        res['data']['lastest_time'] = pd.to_datetime(lastest_time).strftime('%F %H:%M')
        res['data']['rt_v'] = rt_df.to_dict(orient='records')
        return res


@ns.route('/heavily_held_fund')
class HeavilyHeldFund(Resource):
    @ns.doc(parser=hhf_parser, description='基金重仓实时数据')
    def get(self):
        res = lt.get_api_response_template_copy()
        # 获取参数
        args = hhf_parser.parse_args()
        fund_code = args.fund_code
        fund_key_stock, fund_key_bond = get_key_stock_by_fund_code(fund_code)
        # 截取前十大
        fund_key_stock = fund_key_stock.head(10)
        fund_key_bond = fund_key_bond.head(10)
        res["data"] = {}
        if not fund_key_stock.empty:
            report_date = fund_key_stock.loc[0, "report_date"]
            fund_key_stock.drop(columns=["report_date"], inplace=True)

            fund_key_stock = fund_key_stock.where(fund_key_stock.notnull(), None)
            res["data"]["stock_top10"] = fund_key_stock.to_dict(orient="records")
            res["data"]["bond_top10"] = fund_key_bond.to_dict(orient="records")
            res["data"]["stock_top10_pos"] = round(fund_key_stock["pos"].sum(), 6)
            res["data"]["report_date"] = report_date
        if not fund_key_bond.empty:
            fund_key_bond.drop(columns=["report_date"], inplace=True)
            res["data"]["bond_top10_pos"] = round(fund_key_bond["pos"].sum(), 6)
        return res


@ns.route('/evaluation_histline')
class EvaluationHistline(Resource):
    @ns.doc(parser=vh_parser, description='历史估值曲线')
    def get(self):
        res = lt.get_api_response_template_copy()
        # 获取参数
        args = vh_parser.parse_args()
        fund_code = args.fund_code
        end_date = time.strftime('%F')

        # 检索一年内的历史估值
        df = get_rt_ev_data_histline(fund_code, end_date)
        if df.empty:
            res['code'] = HttpCode.data_empty_error.value[0]
            res['msg'] = HttpCode.data_empty_error.value[1]
            return res

        df['error'] = abs(df['est_ret'] - df['gt_ret'])
        data = {}

        # 分别计算1个月, 3个月, 6个月, 12个月的平均误差和最大误差
        for item in (1, 3, 6, 12):
            _df = df.head(months_to_days_map[item])
            err_nav = abs(_df['est_nav'] - _df['gt_nav'])
            _df = _df.round(6)
            avg_error = err_nav.mean().round(6)
            max_error = err_nav.max().round(6)
            data[f'avg_error_{item}'] = None if avg_error is np.nan else avg_error
            data[f'max_error_{item}'] = None if max_error is np.nan else max_error

        df = df.where(df.notnull(), None).round(6)
        data['nav'] = df.to_dict(orient='records')
        res['data'] = data
        return res


@ns.route('/similar_fund/gen_ports')
class GenerateSimilarPort(Resource):
    @ns.doc(parser=gsp_parser, description='查询相似组合计算结果')
    def get(self):
        res = lt.get_api_response_template_copy()
        args = gsp_parser.parse_args()
        fund_code = args.fund_code
        compute_date = args.compute_date
        pool_size = args.pool_size
        white_list = args.white_list
        port_num = args.port_num
        info = {}
        ticker = fund_code.split(".")[0]
        # 1.查询相似性页面数据 是否存在 若存在返回数据
        ret_similarity_page_data = similarity_page_data(ticker, compute_date, pool_size, white_list, port_num)
        if ret_similarity_page_data:
            info = ret_similarity_page_data
            res["data"]["status"] = "done"
            res["data"]["info"] = info
        # 2. 如果不存在 查询相似任务计算结果
        else:
            similar_data = get_similarity_task_data(ticker, compute_date, pool_size, white_list, port_num)
            # 3.如果计算任务存在 计算相似性组合页面数据,保存到redis，返回数据
            if not similar_data.empty:
                # 匹配基金名称
                similar_data["code"] = similar_data["fund_code"] + ".OF"
                fund_info = get_fundinfo(fund_code_list=similar_data.code.to_list())
                df = similar_data.merge(fund_info, how="left")
                df.rename(columns={"name": "fund_name"}, inplace=True)
                df.drop(columns=["code", "main_code"], inplace=True)
                info["similarity_port_detail"] = df.round(6).to_dict(orient="records")
                # 匹配行业分析
                similarity_port_main_code = similar_data["main_code"].to_list()  # 相似组合资产
                similarity_port_weight = similar_data["weight"].to_list()  # 相似组合资产权重
                similarity_port_industry_dict = get_port_industry_weight(similarity_port_main_code,
                                                                         similarity_port_weight,
                                                                         compute_date)  # 相似组合行业
                target_port_industry_dict = get_port_industry_weight([ticker], [1], compute_date)  # 自选组合行业
                port_industry_detail = []  # 组合行业详情
                for industry in target_port_industry_dict.keys():
                    port_industry_detail.append({
                        "industry_name": industry,
                        "target_weight": target_port_industry_dict.get(industry),
                        "similarity_weight": similarity_port_industry_dict.get(industry)
                    })
                info["port_industry_detail"] = port_industry_detail

                # 计算回测区间
                start_date_t = datetime.datetime.strptime(compute_date, "%Y-%m-%d") + relativedelta(months=-3)
                back_test_start_time = str(start_date_t.date())
                info["back_test_interval"] = ComputeSimilarInterval.compute_similar_interval(
                    fund_code, info["similarity_port_detail"], back_test_start_time, compute_date)

                # 计算验证区间(当计算日期小于今天)
                if datetime.datetime.strptime(compute_date, "%Y-%m-%d").date() < datetime.date.today():
                    update_date = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
                    info["verification_interval"] = ComputeSimilarInterval.compute_similar_interval(
                        fund_code, info["similarity_port_detail"], compute_date, update_date, is_back_test=False)
                else:
                    info["verification_interval"] = {}

                res["data"]["status"] = "done"
                res["data"]["info"] = info
                #  将生成的相似组合存入到redis中
                similarity_page_data(ticker, compute_date, pool_size, white_list, port_num, data=info)
            # 4.如果计算任务结果不存在,判断任务是否存在
            else:
                task_in_user = exist_similar_user_task(ticker, compute_date, pool_size, white_list)
                if not task_in_user:
                    # 该任务不存在
                    res["data"]["status"] = "similarity task not exist"
                else:
                    task = exist_similar_task(ticker, compute_date, pool_size, white_list)
                    # 如果存在任务返回waiting 反之 working
                    res["data"]["status"] = "waiting" if task else "working"
                res["data"]["info"] = ""
        return res

    @ns.doc(parser=gsp_post_parser, description='生成相似组合')
    def post(self):
        res = lt.get_api_response_template_copy()
        # 获取参数
        args = gsp_post_parser.parse_args()
        fund_code = args.fund_code
        compute_date = args.compute_date
        pool_size = args.pool_size
        white_list = args.white_list
        ticker = fund_code.split(".")[0]
        sub = current_user()  # 获取当前用户

        # 已有缓存的计算结果 ==> 添加到用户队列并设置为完成
        if exist_similar_result(ticker, compute_date, pool_size, white_list):
            logger.info(f"{ticker}-{compute_date}-{pool_size}--{white_list} 已有缓存")
            status = 'done'
            res["msg"] = "result done"

        # 该任务不存在 ==> 添加到任务队列 + 用户队列
        else:
            logger.info(f"{ticker}-{compute_date}-{pool_size}--{white_list} 准备添加到任务队列")
            status = 'new'
            res["msg"] = "成功加入到计算任务中"

        create_similarity_task(sub, ticker, compute_date, pool_size, white_list, status)  # 生成计算相似组合任务
        logger.info(f"{ticker}-{compute_date}-{pool_size}--{white_list} 成功加入到计算任务中")

        return res


@ns.route('/similar_fund/tracking_port')
class TrackingSimilarPort(Resource):
    @ns.doc(parser=tsp_get_parser, description='查询追踪的相似性组合')
    def get(self):
        res = lt.get_api_response_template_copy()
        # 获取参数
        sub = current_user()  # 获取当前用户
        args = tsp_get_parser.parse_args()
        _id = args.id
        port_name = args.port_name
        target_code = args.target_code
        target_name = args.target_name

        #  获取数据
        similar_port_data = get_similar_port(sub, _id=_id, port_name=port_name,
                                             target_code=target_code, target_name=target_name)
        if similar_port_data.empty:
            res["data"] = None
        else:
            info = {
                "similarity_port_detail": json.loads(similar_port_data.loc[0, "similarity_port_detail"]),
                "port_industry_detail": json.loads(similar_port_data.loc[0, "port_industry_detail"]),
                "back_test_interval": json.loads(similar_port_data.loc[0, "back_test_interval"]),
                "verification_interval": json.loads(similar_port_data.loc[0, "verification_interval"]),
            }
            user_name = get_userinfo(sub)
            res["data"]["info"] = info
            res["data"]["id"] = int(similar_port_data.loc[0, "id"])
            res["data"]["target_code"] = similar_port_data.loc[0, 'target_code']
            res["data"]["target_name"] = similar_port_data.loc[0, 'target_name']
            res["data"]["port_name"] = similar_port_data.loc[0, "port_name"]
            res["data"]["tracker"] = user_name.loc[0, "username"]
            res["data"]["compute_date"] = similar_port_data.loc[0, "compute_date"]
        return res

    @ns.doc(parser=tsp_parser, description='追踪相似组合')
    def post(self):
        res = lt.get_api_response_template_copy()
        # 获取参数
        args = tsp_parser.parse_args()
        fund_code = args.fund_code
        compute_date = args.compute_date
        pool_size = args.pool_size
        port_num = args.port_num
        white_list = args.white_list
        port_name = args.port_name
        target_code, target_type = lt.get_target_code(fund_code)

        #  从redis中获取数据
        r_similarity_page_data = similarity_page_data(target_code, compute_date, pool_size, white_list, port_num)
        if not r_similarity_page_data:
            logger.error('无缓存页面数据')
            res["msg"] = "无缓存页面数据"
            res["data"] = "error"
            res["code"] = 400
            return res

        sub = current_user()  # 获取当前用户
        df_data = check_user_similarity_port_exists(target_code, compute_date, pool_size, white_list, port_num)
        if not df_data.empty:
            res['code'] = HttpCode.duplicate_data.value[0]
            res['msg'] = HttpCode.duplicate_data.value[1]
            res["data"] = "该用户已保存过该组合"
            return res
        #  解析数据持久化到mysql中
        similarity_port_detail = r_similarity_page_data.get("similarity_port_detail")
        port_industry_detail = r_similarity_page_data.get("port_industry_detail")
        back_test_interval = r_similarity_page_data.get("back_test_interval")
        verification_interval = r_similarity_page_data.get("verification_interval")

        # 获取target_code && target_name
        if target_type == SimilarType.FUND:
            target_name_df = get_fund_name_by_fund_code(target_code)
            target_name = target_name_df.loc[0, "fund_abbr"]
        else:
            target_name = get_fund_port_name_by_id(target_code)
        df = pd.DataFrame({
            "sub": [sub],
            "tracker": [sub],
            "target_code": [target_code],
            "target_name": [target_name],
            "white_list": [white_list],
            "port_num": [port_num],
            "port_name": [port_name],
            "port_size": [pool_size],
            "compute_date": [compute_date],
            "similarity_port_detail": [json.dumps(similarity_port_detail, ensure_ascii=False)],
            "port_industry_detail": [json.dumps(port_industry_detail, ensure_ascii=False)],
            "back_test_interval": [json.dumps(back_test_interval, ensure_ascii=False)],
            "verification_interval": [json.dumps(verification_interval, ensure_ascii=False)],
            "create_time": [str(datetime.datetime.now())],
            "update_time": [str(datetime.datetime.now())]
        })

        # 入库MySQL
        try:
            save_similar_port(df)
            res["data"] = "success"
        except Exception as e:
            if "Duplicate entry" in str(e):
                res["data"] = f"该用户已存在[{port_name}]组合"
                res['code'] = HttpCode.duplicate_data.value[0]
                res['msg'] = HttpCode.duplicate_data.value[1]
            else:
                res["data"] = "error"
                res['code'] = HttpCode.internal_error.value[0]
                res['msg'] = HttpCode.internal_error.value[1]
        return res

    @ns.doc(parser=tsp_del_parser, description='停止追踪')
    def delete(self):
        res = lt.get_api_response_template_copy()
        # 获取参数
        args = tsp_del_parser.parse_args()
        port_id_list = json.loads(args.port_id_list)
        remove_similar_port(port_id_list)
        res["data"] = "success"
        return res


@ns.route('/similar_fund/tracking_port_list')
class TrackingSimilarPortList(Resource):
    @ns.doc(parser=tsp_list_parser, description='追踪相似组合列表')
    def get(self):
        res = lt.get_api_response_template_copy()
        # 获取参数
        args = tsp_list_parser.parse_args()
        target_code = args.target_code
        page_num = args.page_num
        page_size = args.page_size
        sub = current_user()

        # 获取该用户的相似性组合
        port_df = get_similar_port(sub, target_code=target_code, page=page_num, page_size=page_size)

        # 获取所有的用户名
        user_df = get_all_username()

        # 合并出tracker的名字并删除用户id列
        df = pd.merge(port_df, user_df,
                      left_on='tracker',
                      right_on='sub') \
            .drop(columns=['tracker', 'sub']) \
            .rename(columns={'username': 'tracker'})

        res['data'] = df.to_dict(orient='records')
        return res


@ns.route('/similar_fund/history')
class SimilarPortHistory(Resource):
    @ns.doc(parser=tsp_list_parser, description='相似性组合历史记录')
    def get(self):
        res = lt.get_api_response_template_copy()
        sub = current_user()
        history_df = user_similar_history(sub)
        if history_df.empty:
            logger.info(f'user {sub} has no similar task history')
            res["data"] = None
            return res
        # 处理基金相似性任务记录
        tikcer_task_df = history_df[history_df.target_code.str.len() == 6]
        tikcer_task_df.target_code = tikcer_task_df.target_code + '.OF'
        fund_code_list = tikcer_task_df.target_code.to_list()
        fund_name_df = get_fundinfo(fund_code_list)
        df = pd.merge(tikcer_task_df, fund_name_df, left_on='target_code', right_on='code')
        df = df.drop(columns=['code']).rename(columns={'name': 'target_name'})

        res['data'] = df.to_dict(orient='records')
        return res


@ns.route('/similar_fund/white_list')
class SimilarPortWhiteList(Resource):
    @ns.doc(description='获取相似性组合白名单')
    def get(self):
        res = lt.get_api_response_template_copy()
        # sub = current_user()

        # TODO 将来需要完善通过用户id查询出白名单列表
        res['data'] = [{'name': '全部基金', 'white_list_id': '00001'}]
        return res


@ns.route('/similar_fund/check_white_list')
class SimilarPortCheckWhiteList(Resource):
    @ns.doc(parser=check_white_list_parser, description='验证相似性组合白名单是否可计算')
    def get(self):
        res = lt.get_api_response_template_copy()
        # sub = current_user()
        # 获取参数
        # args = check_white_list_parser.parse_args()
        # white_code = args.white_code

        # TODO 将来需要完善白名单列表是否可以计算
        # 三种状态 可计算 1 不可计算 0  可能会计算失败 -1
        res['data'] = {'status': 1}
        return res

