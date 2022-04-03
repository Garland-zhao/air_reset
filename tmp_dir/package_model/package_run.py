# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/17 17:21
@Auth ： ZhaoFan
@File ：a.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import argparse

from models.navest.navest_api import package_run as run_api
from models.navest.navest_run import package_run as run_navest
from models.navest.navest_pr edata import package_run as run_predata
from models.navest.navest_backfill import package_run as run_backfill
from models.navest.navest_backtest import package_run as run_backtest
from models.navest.monitor.navest_fetch import package_run as run_fetch
from models.navest.monitor.navest_webui import package_run as run_webui


def parser_predata(subparsers):
    """数据准备"""
    predata = subparsers.add_parser('navest_predata', help='prepare predata')
    predata.set_defaults(func=run_predata)


def parser_navest(subparsers):
    """运行估值程序"""
    navest_run = subparsers.add_parser('navest_run', help='run navest')
    navest_run.set_defaults(func=run_navest)


def parser_api(subparsers):
    """运行接口"""
    navest_api = subparsers.add_parser('navest_api', help='run navest api')
    navest_api.set_defaults(func=run_api)
    navest_api.add_argument('-h', '--host', dest='host', type=str, help='host of run navest api', default='0.0.0.0')
    navest_api.add_argument('-p', '--port', dest='port', type=int, help='port of run navest api', default=5000)


def parser_backfill(subparsers):
    """回填某日的分时估值数据（如果某日的股票分时数据有）"""
    navest_backfill = subparsers.add_parser('navest_backfill', help='back fill data of some date')
    navest_backfill.set_defaults(func=run_backfill)
    navest_backfill.add_argument('-c', '--compute-date', dest='compute_date', type=str,
                                 help='The compute date, e.g. 2021-12-06, default is today', default='')
    navest_backfill.add_argument('-s', '--start-time', dest='start_time', type=str,
                                 help='The start time on the compute date, e.g. 09:29', default='09:29')
    navest_backfill.add_argument('-e', '--end-time', dest='end_time', type=str,
                                 help='The end time on the compute date, e.g. 15:00', default='16:10')


def parser_backtest(subparsers):
    """回测工具"""
    navest_backtest = subparsers.add_parser('navest_backtest', help='back fill data of some date')
    navest_backtest.set_defaults(func=run_backtest)
    navest_backtest.add_argument('-s', '--start-date', dest='start_date',
                                 help='The start compute date, e.g. 2021-01-01', type=str, required=True, default='')
    navest_backtest.add_argument('-e', '--end-date', dest='end_date',
                                 help='The end compute date, e.g. 2021-12-01', type=str, required=True, default='')
    navest_backtest.add_argument('-t', '--compute-time', dest='compute_time',
                                 help='The compute time on each compute date, e.g. 15:00', type=str, default='15:00')
    navest_backtest.add_argument('-a', '--analysis-err-dat', dest='analysis_err_dat', action='store_true',
                                 help='Specify to analyze the ret err data.')


def parser_fetch(subparsers):
    """监控程序--抓取实时数据（分钟级）"""
    navest_fetch = subparsers.add_parser('navest_fetch', help='back fill data of some date')
    navest_fetch.set_defaults(func=run_fetch)
    navest_fetch.add_argument('-s', '--start-time-str', dest='start_time_str',
                              help='The start date time of the data, e.g. 202112100929', type=str, default='')
    navest_fetch.add_argument('-e', '--end-time-str', dest='end_time_str',
                              help='The end time of the data, e.g. 1500', type=str, default='')
    navest_fetch.add_argument('-t', '--tickers', dest='tickers',
                              help='The tickers to fectch, e.g. 001385,000001', type=str, default='')
    navest_fetch.add_argument('-d', '--daemon', dest='daemon', action="store_true",
                              help='Run as daemon mode and fetch the result every 1min using scheduler.')
    navest_fetch.add_argument('-f', '--force-override', dest='force_override', action="store_true",
                              help="Force to override the local cached data.")


def parser_webui(subparsers):
    """显示到web ui"""
    navest_webui = subparsers.add_parser('navest_webui', help='back fill data of some date')
    navest_webui.set_defaults(func=run_webui)
    navest_webui.add_argument('-h', '--host', dest='host', type=str, help='host of run navest api', default='0.0.0.0')
    navest_webui.add_argument('-p', '--port', dest='port', type=int, help='port of run navest api', default=5001)


def main():
    """打包运行的入口

    通过解析子命令来选择运行的内容和参数
    """
    # 构造参数
    parser = argparse.ArgumentParser(prog='', description='')
    subparsers = parser.add_subparsers(help='')

    # 添加已支持的子命令
    parser_predata(subparsers)
    parser_navest(subparsers)
    parser_api(subparsers)
    parser_backfill(subparsers)
    parser_backtest(subparsers)
    parser_fetch(subparsers)
    parser_webui(subparsers)

    # 解析命令行参数
    args = parser.parse_args()

    # 根据所选方法是否有参数, 决定是否需要传参
    if args.func.__code__.co_varnames:
        args.func(args)
    else:
        args.func()


if __name__ == '__main__':
    """python -m navest_package --help"""
    main()
