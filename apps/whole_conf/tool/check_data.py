#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: check_data.py
@Time: 2023/7/22-13:28
"""

from apps.whole_conf import schemas


def check(enum: (schemas.ConfUnifyResIn, schemas.ConfCustomizeIn)):
    if enum.type == schemas.ModeEnum.int or enum.type == schemas.ModeEnum.number:
        enum.value = int(enum.value)
    elif enum.type == schemas.ModeEnum.float:
        enum.value = float(enum.value)
    elif enum.type == schemas.ModeEnum.string:
        enum.value = str(enum.value)
    elif enum.type == schemas.ModeEnum.boolean:
        enum.value = True if enum.value == 1 else False
    elif enum.type == schemas.ModeEnum.null:
        enum.value = None
