#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: jsonpath_count.py
@Time: 2023/8/31-21:54
"""

import re


def json_count(dict_data: dict):
    """
    统计jsonpath出现的位置
    :param dict_data:
    :return:
    """

    def handle_value(data_json):
        target = {}
        if not isinstance(data_json, (dict, list, str)):
            return target

        if isinstance(data_json, str):
            if "{{" in data_json and "$" in data_json and "}}" in data_json:
                for josnpath in re.compile(r'{{(.*?)}}', re.S).findall(data_json):
                    path = "{{" + josnpath + "}}"
                    if target.get(path):
                        target[path] += 1
                    else:
                        target[path] = 1
        else:
            for k, v in data_json.items():
                if isinstance(v, str):
                    if "{{" in v and "$" in v and "}}" in v:
                        for josnpath in re.compile(r'{{(.*?)}}', re.S).findall(v):
                            path = "{{" + josnpath + "}}"
                            if target.get(path):
                                target[path] += 1
                            else:
                                target[path] = 1
                    continue
                if isinstance(v, dict):
                    handle_value(v)
                    continue
                if isinstance(v, list):
                    for x in v:
                        handle_value(x)
                    continue
        return target

    return handle_value(dict_data)


def str_count(str_data: str):
    """
    统计jsonpath出现的位置
    :param str_data:
    :return:
    """
    target = {}
    if "{{" in str_data and "$" in str_data and "}}" in str_data:
        for josnpath in re.compile(r'{{(.*?)}}', re.S).findall(str_data):
            path = "{{" + josnpath + "}}"
            if target.get(path):
                target[path] += 1
            else:
                target[path] = 1
    return target


def count(case_list: list):
    data_count = {}
    for i, case in enumerate(case_list):
        for k, v in str_count(case.path).items():
            if data_count.get(k):
                if data_count[k].get('path'):
                    data_count[k]['path']['numbers'].append(i)
                    data_count[k]['path']['count'] += v
                else:
                    data_count[k] = {
                        'path': {
                            'numbers': [i],
                            'count': v
                        },
                        'params': data_count[k].get('params', {}),
                        'data': data_count[k].get('data', {}),
                        'headers': data_count[k].get('headers', {}),
                        'check': data_count[k].get('check', {})
                    }
            else:
                data_count[k] = {
                    'path': {
                        'numbers': [i],
                        'count': v
                    },
                    'params': data_count.get(k, {}).get('params', {}),
                    'data': data_count.get(k, {}).get('data', {}),
                    'headers': data_count.get(k, {}),
                    'check': data_count.get(k, {}).get('check', {})
                }

    for i, case in enumerate(case_list):
        for k, v in json_count(case.params).items():
            if data_count.get(k):
                if data_count[k].get('params'):
                    data_count[k]['params']['numbers'].append(i)
                    data_count[k]['params']['count'] += v
                else:
                    data_count[k] = {
                        'path': data_count[k].get('path', {}),
                        'params': {
                            'numbers': [i],
                            'count': v
                        },
                        'data': data_count[k].get('data', {}),
                        'headers': data_count[k].get('headers', {}),
                        'check': data_count[k].get('check', {})
                    }
            else:
                data_count[k] = {
                    'path': data_count.get(k, {}).get('path', {}),
                    'params': {
                        'numbers': [i],
                        'count': v
                    },
                    'data': data_count.get(k, {}).get('data', {}),
                    'headers': data_count.get(k, {}).get('headers', {}),
                    'check': data_count.get(k, {}).get('check', {})
                }

    for i, case in enumerate(case_list):
        for k, v in json_count(case.data).items():
            if data_count.get(k):
                if data_count[k].get('data'):
                    data_count[k]['data']['numbers'].append(i)
                    data_count[k]['data']['count'] += v
                else:
                    data_count[k] = {
                        'path': data_count[k].get('path', {}),
                        'params': data_count[k].get('params', {}),
                        'data': {
                            'numbers': [i],
                            'count': v
                        },
                        'headers': data_count[k].get('headers', {}),
                        'check': data_count[k].get('check', {})
                    }
            else:
                data_count[k] = {
                    'path': data_count.get(k, {}).get('path', {}),
                    'params': data_count.get(k, {}).get('params', {}),
                    'data': {
                        'numbers': [i],
                        'count': v
                    },
                    'headers': data_count.get(k, {}).get('headers', {}),
                    'check': data_count.get(k, {}).get('check', {})
                }

    for i, case in enumerate(case_list):
        for k, v in json_count(case.headers).items():
            if data_count.get(k):
                if data_count[k].get('headers'):
                    data_count[k]['headers']['numbers'].append(i)
                    data_count[k]['headers']['count'] += v
                else:
                    data_count[k] = {
                        'path': data_count[k].get('path', {}),
                        'params': data_count[k].get('params', {}),
                        'data': data_count[k].get('data', {}),
                        'headers': {
                            'numbers': [i],
                            'count': v
                        },
                        'check': data_count[k].get('check', {})
                    }
            else:
                data_count[k] = {
                    'path': data_count.get(k, {}).get('path', {}),
                    'params': data_count.get(k, {}).get('params', {}),
                    'data': data_count.get(k, {}).get('data', {}),
                    'headers': {
                        'numbers': [i],
                        'count': v
                    },
                    'check': data_count.get(k, {}).get('check', {})
                }

    for i, case in enumerate(case_list):
        for k, v in json_count(case.check).items():
            if data_count.get(k):
                if data_count[k].get('check'):
                    data_count[k]['check']['numbers'].append(i)
                    data_count[k]['check']['count'] += v
                else:
                    data_count[k] = {
                        'path': data_count[k].get('path', {}),
                        'params': data_count[k].get('params', {}),
                        'data': data_count[k].get('data', {}),
                        'headers': data_count[k].get('headers', {}),
                        'check': {
                            'numbers': [i],
                            'count': v
                        },
                    }
            else:
                data_count[k] = {
                    'path': data_count.get(k, {}).get('path', {}),
                    'params': data_count.get(k, {}).get('params', {}),
                    'data': data_count.get(k, {}).get('data', {}),
                    'headers': data_count.get(k, {}).get('headers', {}),
                    'check': {
                        'numbers': [i],
                        'count': v
                    },
                }

    # 转行为前端能处理的格式
    data_list = []
    for k, v in data_count.items():
        data_list.append(
            {
                'jsonpath': k,
                'path': v['path'].get('numbers', []),
                'params': v['params'].get('numbers', []),
                'data': v['data'].get('numbers', []),
                'headers': v['headers'].get('numbers', []),
                'check': v['check'].get('numbers', []),
                'count': v['path'].get('count', 0) +
                         v['params'].get('count', 0) +
                         v['data'].get('count', 0) +
                         v['headers'].get('count', 0) +
                         v['check'].get('count', 0)
            }
        )

    return data_list
