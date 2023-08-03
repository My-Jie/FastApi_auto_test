#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: check_Info.py
@Time: 2023/3/2-15:36
"""

from apps.case_service import schemas


def check(check: schemas.CheckInfo):
    """
    校验字段之间的逻辑性
    :param check:
    :return:
    """

    if check.type == 'string':
        if check.s in ['==', '!=', 'in', '!in', 'not in', 'notin', '!not in', '!notin']:
            if isinstance(check.value, (str, int, float)):
                return True

    elif check.type == 'number':
        if check.s in ['==', '!=', '<', '<=', '>', '>=']:
            if isinstance(check.value, (int, float)):
                return True

    elif check.type == 'boolean':
        if check.s in ['==', '!=']:
            if check.value in [1, 0]:
                return True

    elif check.type == 'null':
        if check.s in ['==', '!=']:
            if check.value in [None, 'null']:
                return True
