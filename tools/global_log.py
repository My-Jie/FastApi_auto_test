#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: global_log.py
@Time: 2020/11/19-17:22
"""

import logging
import logging.config
import logging.handlers
import os
import copy

from .read_setting import setting
from enum import Enum, unique

__all__ = [
    'logger'
]


@unique
class _DirMode(Enum):
    CONFIG = 0
    PACKAGE = 1


# """
# 日志等级：使用范围
#
# FATAL：致命错误
# CRITICAL：特别糟糕的事情，如内存耗尽、磁盘空间为空，一般很少使用
# ERROR：发生错误时，如IO操作失败或者连接问题
# WARNING：发生很重要的事件，但是并不是错误时，如用户登录密码错误
# INFO：处理请求或者状态变化等日常事务
# DEBUG：调试过程中使用DEBUG等级，如算法中每个循环的中间状态
# """
# """
# fomatter中可用变量
# %(levelno)s: 打印日志级别的数值
# %(levelname)s: 打印日志级别名称
# %(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]
# %(module)s: 打印当前模块名称
# %(filename)s: 打印当前执行程序名
# %(funcName)s: 打印日志的当前函数
# %(lineno)d: 打印日志的当前行号
# %(asctime)s: 打印日志的时间
# %(thread)d: 打印线程ID
# %(threadName)s: 打印线程名称
# %(code_process)d: 打印进程ID
# %(message)s: 打印日志信息
# """

_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "log_dir": setting['log_path'],
    "formatters": {
        "simple": {
            # 'format': '%(asctime)s [%(levelname)s] [%(thread)d#%(threadName)s] [%(module)s#%(funcName)s] - %(message)s',
            'format': '%(asctime)s [%(levelname)s] - %(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] - %(message)s'
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",  # 日志输出等级
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "debug": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "debug.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 6,
            "encoding": 'utf-8'
        },
        "info": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "info.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 6,
            "encoding": 'utf-8'
        },
        "warn": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "WARN",
            "formatter": "simple",
            "filename": "warn.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 6,
            "encoding": 'utf-8'
        },
        "error": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "ERROR",
            "formatter": "simple",
            "filename": "error.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 6,
            "encoding": 'utf-8'
        }
    },

    "loggers": {
        "data": {
            "level": "DEBUG",
            "handlers": ['debug', "info", "warn", "error", "console"],
            "propagate": False
        }
    },

    "root": {
        'handlers': ['debug', "info", "warn", "error", "console"],
        'level': "DEBUG",
        'propagate': False
    }
}


def _get_filter(level):
    if level == logging.DEBUG:
        return lambda record: record.levelno < logging.INFO
    elif level == logging.INFO:
        return lambda record: record.levelno < logging.WARN
    elif level == logging.WARN:
        return lambda record: record.levelno < logging.ERROR
    else:
        return lambda record: record.levelno <= logging.FATAL


def _adjust_config(logging_config, level, dir_mode=_DirMode.CONFIG):
    # 使用配置目录
    if dir_mode == _DirMode.CONFIG:
        dir_name = logging_config['log_dir']
    # 使用项目同级目录
    else:
        current_dir = os.path.abspath(os.path.dirname(os.getcwd()) + os.path.sep + ".")
        dir_name = current_dir + '/logs/'

    handlers = logging_config.get('handlers')
    handlers['console']['level'] = level
    for handler_name, handler_config in handlers.items():
        filename = handler_config.get('filename', None)
        if filename is None:
            continue
        if dir_name is not None:
            if not os.path.exists(dir_name):
                try:
                    os.makedirs(dir_name)
                except Exception as e:
                    print(e)
            handler_config['filename'] = dir_name + filename
    return logging_config


def _get_logger(level='DEBUG'):
    #  拷贝配置字典
    logging_config = copy.deepcopy(_LOGGING_CONFIG)

    # 调整配置内容
    _adjust_config(logging_config, level, _DirMode.CONFIG)

    # 使用调整后配置生成logger
    logging.config.dictConfig(logging_config)
    res_logger = logging.getLogger()

    for handler in res_logger.handlers:
        if handler.name == 'console':
            continue
        log_filter = logging.Filter()
        log_filter.filter = _get_filter(handler.level)
        handler.addFilter(log_filter)
    return res_logger


logger = _get_logger(level=setting['logger_level'])
