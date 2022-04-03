# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/17 17:21
@Auth ： ZhaoFan
@File ：my_work.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import os
import sys
import time
import shutil
import subprocess
import logging.config
from distutils.core import setup
from Cython.Build import cythonize

starttime = time.time()
setupfile = os.path.join(os.path.abspath('.'), __file__)
build_dir = "build"
build_tmp_dir = build_dir + "/temp"

log_config = {
    'version': 1,
    'formatters': {
        'tmp': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'tmp',
            'stream': 'ext://sys.stdout',
        },
        'fucking_package_worker': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'tmp',
            'filename': os.getenv('PACKAGEMODELLOG', './package_worker.log'),
            'encoding': 'utf-8',
            'when': 'W0',  # 每周一切割日志
        },
    },
    'loggers': {
        'console': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': 0
        },
        'worker': {
            'level': 'INFO',
            'handlers': ['fucking_package_worker', 'console'],
            'propagate': 0
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}

logging.config.dictConfig(log_config)

logger = logging.getLogger("worker")


def clean_worker(model):
    """清理package"""
    os.system(f'rm -rf ./{model}_model/')
    if os.path.exists(f'./{model}_model/'):
        clean_worker(model)


def runcmd(command, options_msg, model):
    """执行shell 命令"""
    ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, encoding="utf-8", timeout=1)
    if ret.returncode == 0:
        logger.info(f'{options_msg} done')
    else:
        logger.error(f'{options_msg} fail with {str(ret.returncode)}')
        clean_worker(model)
        exit()


def getpy(basepath=os.path.abspath('.'), parentpath='', name='', excepts=(), copyOther=False, delC=False):
    """获取py文件的路径

    :param basepath: 根路径
    :param parentpath: 父路径
    :param name: 文件/夹
    :param excepts: 排除文件
    :param copyOther: 是否copy其他文件
    :param delC: 是否删除.c文件
    :return: py文件的迭代器
    """
    fullpath = os.path.join(basepath, parentpath, name)
    for fname in os.listdir(fullpath):
        ffile = os.path.join(fullpath, fname)
        # print basepath, parentpath, name,file
        if os.path.isdir(ffile) and fname != build_dir and not fname.startswith('.'):
            for f in getpy(basepath, os.path.join(parentpath, name), fname, excepts, copyOther, delC):
                yield f
        elif os.path.isfile(ffile):
            ext = os.path.splitext(fname)[1]
            if ext == ".c":
                if delC and os.stat(ffile).st_mtime > starttime:
                    os.remove(ffile)
            elif ffile not in excepts and os.path.splitext(fname)[1] not in ('.pyc', '.pyx'):
                if os.path.splitext(fname)[1] in ('.py', '.pyx') and not fname.startswith('__'):
                    yield os.path.join(parentpath, name, fname)
                elif copyOther:
                    dstdir = os.path.join(basepath, build_dir, parentpath, name)
                    if not os.path.isdir(dstdir): os.makedirs(dstdir)
                    shutil.copyfile(ffile, os.path.join(dstdir, fname))
        else:
            pass


########################################################################
def make_setup(model, path):
    # 执行打包
    os.chdir(path)
    module_list = list(getpy(basepath=os.path.abspath('.'), excepts=(setupfile)))
    for i in module_list:
        print(i)
    setup(
        ext_modules=cythonize(module_list),
        script_args=["build_ext", "-b", build_dir, "-t", build_tmp_dir]
    )

    if os.path.exists(build_tmp_dir):
        shutil.rmtree(build_tmp_dir)

    print("complate! time:", time.time() - starttime, 's')


def move_file(model):
    # 移出run_package.py
    move_run_package = f'mv ./{model}_model/models/{model}/run_package.py ./{model}_model/'
    runcmd(move_run_package, '移出run_package.py', model)

    # 移出requirements.txt
    move_requirements = f'mv ./{model}_model/models/{model}/requirements.txt ./{model}_model/'
    runcmd(move_requirements, '移出requirements.txt', model)


def copy_project_code(model):
    """拷贝models"""
    # 复制models
    copy_model = f'cp -r ./supermodel/models/{model} ./{model}_model/models/'
    runcmd(copy_model, '复制model', model)

    # 复制models/__init__.py
    copy_model_init = f'cp ./supermodel/models/__init__.py ./{model}_model/models/'
    runcmd(copy_model_init, '复制model/__init__.py', model)

    # 复制common
    copy_common = f'cp -r ./supermodel/common ./{model}_model'
    runcmd(copy_common, '复制common', model)

    # 复制settings
    copy_common = f'cp -r ./supermodel/settings.py ./{model}_model'
    runcmd(copy_common, '复制settings', model)


def make_project_dir(model):
    """创建打包目录"""
    path = f'./{model}_model/models/{model}'
    if os.path.exists(path):
        # 若打包目录已存在, 告警并退出
        logger.error(f'{path} 已存在, 请删除')
        exit()
    else:
        # 创建打包目录
        os.makedirs(path)
        logger.info(f'创建目录: {path}')


def choose_and_ensure_model(models):
    """选择一个模型并确认"""
    while True:
        logger.info(f'>> 检索到{len(models)}个模型如下:')
        for index, model in enumerate(models, 1):
            print(f'{index} -- {model}')

        logger.info('请选择打包的项目序号:')
        choose = input()
        project_name = models[int(choose) - 1]
        logger.info(f'确认打包--{project_name}: y/n')
        ensure = input()
        if ensure.upper() == 'Y':
            return project_name


def show_all_project():
    """检索supermodels中所有已经支持的项目"""
    for root, dirs, files in os.walk('./supermodel/models'):
        if dirs:
            return dirs
    # 若没有文件, 则告警并退出
    logger.error('supermodel, 请确认')
    exit()


def main():
    """
    # 检索所有模型
    models = show_all_project()

    # 选择模型and确认
    model = choose_and_ensure_model(models)

    # 创建打包目录
    make_project_dir(model)

    # 拷贝代码
    logger.info(f'开始拷贝模型:{model}')
    copy_project_code(model)

    # 转移需要保留的文件(run_package.py + requirements.txt)
    move_file(model)
    """

    model = 'navest'
    # 生成setup.py并打包
    make_setup(model, f'./{model}_model/')
    logger.info('打包完成')


if __name__ == '__main__':
    main()
