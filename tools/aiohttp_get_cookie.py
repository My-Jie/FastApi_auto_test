#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: aiohttp_get_cookie.py
@Time: 2022/8/29-12:55
"""

import re


async def get_cookie(rep_type, response) -> str:
    """
    获取cookie数据
    :param rep_type: requests 或者 aiohttp
    :param response:
    :return:
    """
    cookie = ''
    if rep_type == 'aiohttp':
        for k, v in response.cookies.items():
            cookie += f"{k}={re.compile(r'=(.*?); ', re.S).findall(str(v))[0]}; "
        return cookie

    if rep_type == 'requests':
        for k, v in response.cookies.get_dict().items():
            cookie += f"{k}={v}; "
        return cookie
