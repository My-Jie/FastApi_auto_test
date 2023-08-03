#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: case_data.py
@Time: 2023/6/16-10:23
"""

import re


async def get_row_data(playwright_text: str):
    """
    处理text文本数据
    :param playwright_text:
    :return:
    """
    data_list = playwright_text.split('\n')

    result = []
    for i, data in enumerate(data_list):
        if '{{' in data and "}}" in data:
            for x in re.findall(r"{{(.*?)}}", data):
                result.append({'row': i + 1, 'data': x})

    return result
