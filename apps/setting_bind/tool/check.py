#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: check.py
@Time: 2023/7/27-23:32
"""


async def check_setting(bind: bool, id_: int, ids: list):
    """
    校验绑定数据
    :param bind:
    :param id_:
    :param ids:
    :return:
    """
    if id_ is None:
        return

    if bind:
        if id_ in ids:
            raise ValueError('存在重复的绑定id')
    else:
        if id_ not in ids:
            raise ValueError('id不存在')
