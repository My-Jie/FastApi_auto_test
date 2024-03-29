#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: read_setting.py
@Time: 2023/7/18-10:03
"""

import yaml


def read_yaml() -> dict:
    """
    读取setting配置文件
    :return:
    """
    with open('setting.yaml', 'r', encoding='utf-8', errors='ignore') as r:
        data = r.read()

    conf = yaml.load(data, Loader=yaml.FullLoader)

    try:
        if conf['logger_level'] not in ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CONSOLE']:
            conf['logger_level'] = 'INFO'

        if not conf['log_path']:
            conf['log_path'] = './logs/'

        if not conf['allure_path']:
            conf['allure_path'] = './auto_report/api/'

        if not conf['allure_path_ui']:
            conf['allure_path_ui'] = './auto_report/ui/'

        if not conf['selenoid']:
            pass

        if not conf['host']:
            pass

        if not conf['sqlite']:
            conf['sqlite'] = 'sqlite+aiosqlite3:///./sqlite/auto_test.sqlite3'

    except KeyError:
        raise KeyError('配置文件读取错误，请检查 setting.yaml')

    return conf


setting = read_yaml()
