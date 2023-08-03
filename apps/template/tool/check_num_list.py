#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: check_num_list.py
@Time: 2023/1/9-15:34
"""

from typing import List
from apps.template import schemas


async def check_num(nums: str, template_data: List[schemas.TemplateDataIn], har_data: list = None) -> list:
    """
    校验数据列表
    :param nums:
    :param har_data:
    :param template_data:
    :return:
    """
    num_list = nums.split(',')
    try:
        num_list = [int(x) for x in num_list if x]
    except ValueError:
        raise ValueError('numbers 不是全数字或分隔符使用错误')

    if [num for num in num_list if num not in [data.number for data in template_data]]:
        raise ValueError('numbers 序号超出了现有模板的序列序号范围')

    if [x for x in num_list if int(x) < 0]:
        raise ValueError('numbers 序号不能小于0')

    if har_data:
        if len(num_list) != len(har_data) and len(num_list) != 1:
            raise ValueError('当需要插入2条及以上数量的数据时，numbers的数量需要同插入数据的数量一致')

    return num_list
