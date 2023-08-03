#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: check_data.py
@Time: 2023/7/29-12:50
"""


async def check_customize(customize_list: list):
    """
    校验自定参数，组装成list
    :param customize_list:
    :return:
    """
    customize_dict = {}
    for x in customize_list:
        # 判断是否使用自定参数
        if x['change'] is not True:
            continue

        try:
            if x['type'] == 'string':
                customize_dict[x['key']] = str(x['value'])
            if x['type'] == 'number':
                customize_dict[x['key']] = int(x['value'])
            if x['type'] == 'int':
                customize_dict[x['key']] = int(x['value'])
            if x['type'] == 'float':
                customize_dict[x['key']] = float(x['value'])
            if x['type'] == 'boolean':
                customize_dict[x['key']] = x['value']
            if x['type'] == 'null':
                customize_dict[x['key']] = None
        except ValueError:
            customize_dict[x['key']] = x['value']

    return customize_dict
