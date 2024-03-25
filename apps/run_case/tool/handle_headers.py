#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
@File    ：handle_headers.py
@IDE     ：PyCharm 
@Author  ：Kobayasi
@Date    ：2023/11/27 19:37 
"""


def replace_headers(cookie: str, tmp_header: dict, case_header: dict, tmp_file: bool) -> dict:
    """
    替换headers中的内容
    :param cookie:
    :param tmp_header:
    :param case_header:
    :param tmp_file:
    :return:
    """
    for k, v in case_header.items():
        tmp_header[k] = v

    # 替换cookie
    if tmp_header.get('Cookie'):
        tmp_header['Cookie'] = cookie
    if tmp_header.get('cookie'):
        tmp_header['cookie'] = cookie

    # 有附件时，要删除Content-Type
    if tmp_file and tmp_header.get('Content-Type'):
        del tmp_header['Content-Type']

    # aiohttp 需要删除Content-Length
    if tmp_header.get('Content-Length'):
        del tmp_header['Content-Length']

    return tmp_header
