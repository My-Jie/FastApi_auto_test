#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: operate_dict.py
@Time: 2023/2/26-9:43
"""

from typing import Any


def dict_add(seek_key: str, insert_key: str, dict_data: dict, value: Any = None):
    """
    对字典进行添加操作
    :param seek_key:
    :param insert_key:
    :param value:
    :param dict_data:
    :return:
    """
    if seek_key is None:
        if insert_key not in dict_data.keys():
            dict_data[insert_key] = value
        return dict_data

    def handle_value(data_json):
        target = {}
        for k, v in data_json.items():
            target[k] = v
            if k == seek_key:
                if isinstance(v, list) and isinstance(v[0], dict):
                    x_list = []
                    for x in v:
                        if insert_key not in x.keys():
                            x[insert_key] = value
                        x_list.append(x)
                    target[k] = x_list

                elif isinstance(v, dict):
                    if insert_key not in v.keys():
                        v[insert_key] = value

        return target

    return handle_value(dict_data)


def dict_edit(old_key: str, new_key: str, dict_data: dict, value: Any = None):
    """
    对字典进行修改操作
    :param old_key:
    :param new_key:
    :param dict_data:
    :param value:
    :return:
    """

    def handle_value(data_json):
        target = {}
        for k, v in data_json.items():
            if not isinstance(v, (list, dict)):
                if k == old_key:
                    target[new_key] = value if value else v
                else:
                    target[k] = v
                continue
            if isinstance(v, dict):
                target[k] = handle_value(v)
                continue
            if isinstance(v, list):
                new_list = []
                for x in v:
                    new_list.append(handle_value(x))
                target[k] = new_list
                continue
        return target

    return handle_value(dict_data)


def dict_del(old_key: str, dict_data: dict):
    """
    对字典进行删除操作
    :param old_key:
    :param dict_data:
    :return:
    """

    def handle_value(data_json):
        target = {}
        for k, v in data_json.items():
            if not isinstance(v, (list, dict)):
                if k == old_key:
                    pass
                else:
                    target[k] = v
                continue
            if isinstance(v, dict):
                target[k] = handle_value(v)
                continue
            if isinstance(v, list):
                new_list = []
                for x in v:
                    new_list.append(handle_value(x))
                target[k] = new_list
                continue
        return target

    return handle_value(dict_data)
