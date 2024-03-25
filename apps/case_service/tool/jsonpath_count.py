#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: jsonpath_count.py
@Time: 2023/8/31-21:54
"""

import re
import jsonpath


def json_count(dict_data: [dict, list, str], data_type: str, number: int):
    """
    统计jsonpath出现的位置
    :param dict_data:
    :param data_type:
    :param number:
    :return:
    """

    def held_str(data_json, target):
        if "{{" in data_json and "$" in data_json and "}}" in data_json:
            for json_path in re.compile(r'{{(.*?)}}', re.S).findall(data_json):
                path = "{{" + json_path + "}}"
                target.append((path, data_type, number))

    def handle_value(data_json):
        target = []
        if not isinstance(data_json, (dict, list, str)):
            return target

        if isinstance(data_json, str):
            held_str(data_json, target)
        else:
            for k, v in data_json.items():
                if isinstance(v, str):
                    held_str(v, target)
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


def jsonpath_count(case_list: list, temp_list: list, run_case: list, get_temp_value=False):
    """

    :param case_list:
    :param temp_list:
    :param run_case:
    :param get_temp_value: 是否获取temp_value的数据
    :return:
    """

    # 查出jsonpath的位置
    json_path_list = []
    for case in case_list:
        json_path_list += json_count(case.path, 'path', case.number)
        json_path_list += json_count(case.params, 'params', case.number)
        json_path_list += json_count(case.data, 'data', case.number)
        json_path_list += json_count(case.headers, 'headers', case.number)
        json_path_list += json_count(case.check, 'check', case.number)

    # 整理jsonpath
    data_count = {}
    for data in json_path_list:
        if data_count.get(data[0]):
            data_count[data[0]][data[1]].append(data[2])
            data_count[data[0]]['count'] += 1
        else:
            new_key = re.sub('{{', '', re.sub('}}', '', data[0]))
            if 'h$' in data[0]:
                new_key = new_key.replace('h$', '$')
            number, json_path = new_key.split('.', 1)

            # 模板中的值
            if get_temp_value:
                temp_value = jsonpath.jsonpath(
                    temp_list[int(number)].headers if 'h$' in data[0] else temp_list[int(number)].response,
                    json_path
                )
                temp_value = temp_value[0] if temp_value else '-'
            else:
                temp_value = '-'

            # 用例中的值
            try:
                case_value = jsonpath.jsonpath(
                    run_case[int(number)]['response_info'][-1]['headers'] if 'h$' in data[0] else
                    run_case[int(number)]['response_info'][-1]['response'],
                    json_path
                )
                case_value = case_value[0] if case_value else '-'
            except (KeyError, IndexError):
                case_value = '-'

            data_count[data[0]] = {
                'jsonpath': data[0],
                'temp_value': temp_value,
                'case_value': case_value,
                'path': {'path': [data[2]]}.get(data[1], []),
                'params': {'params': [data[2]]}.get(data[1], []),
                'data': {'data': [data[2]]}.get(data[1], []),
                'headers': {'headers': [data[2]]}.get(data[1], []),
                'check': {'check': [data[2]]}.get(data[1], []),
                'count': 1,
            }

    return list(data_count.values())
