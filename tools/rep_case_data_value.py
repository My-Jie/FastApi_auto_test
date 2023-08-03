#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: rep_case_data_value.py
@Time: 2023/2/16-10:28
"""


def rep_value(json_data: dict, old_str: str, new_str: str) -> dict:
    """

    :param json_data:
    :param old_str:
    :param new_str:
    :return:
    """

    def handle_value(data):
        target = {}
        if isinstance(data, str):
            if old_str == data:
                return old_str.replace(old_str, new_str)
            else:
                return data

        if isinstance(data, list):
            return [handle_value(x) for x in data]

        for k, v in data.items():

            if not isinstance(v, (list, dict)):
                if v == old_str:
                    target[k] = new_str
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

    return handle_value(json_data)


def rep_url(url: str, old_str: str, new_str: str, ) -> str:
    """
    替换url
    :param old_str:
    :param new_str:
    :param url:
    :return:
    """
    if '{' + old_str + '}' in url:
        old_str = '{' + old_str + '}'
    return url.replace(old_str, new_str)
