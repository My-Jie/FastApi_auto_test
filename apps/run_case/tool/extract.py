#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: extract.py
@Time: 2022/10/27-18:34
"""

import re


async def extract(pattern: str, string: str, index: int):
    """
    参数提取
    :param pattern:
    :param string:
    :param index:
    :return:
    """
    res_list = re.findall(pattern=pattern, string=string)
    if res_list:
        try:
            return res_list[index]
        except IndexError:
            return ''
    else:
        return ''
