import os
import logging
import logging.config

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

work_logger = logging.getLogger("worker")
