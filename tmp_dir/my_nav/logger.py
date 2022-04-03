# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/15 10:37
@Auth ： ZhaoFan
@File ：logger.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import os
import logging
import logging.config

log_config = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'common': {
            'format': '%(asctime)s - %(name)s - %(filename)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'common',
            'stream': 'ext://sys.stdout',
        },
        'nav_handler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'common',
            'filename': os.getenv('SUPERMODELLOG', '/tmp/supermodel.log'),
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
        'nav': {
            'level': 'INFO',
            'handlers': ['nav_handler', 'console'],
            'propagate': 0
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}

logging.config.dictConfig(log_config)


def get_logger(log_name):
    return logging.getLogger(log_name)


nav_logger = get_logger("nav")
