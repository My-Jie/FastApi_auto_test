#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2022/8/22-9:51
"""

from fastapi import APIRouter

case_perf = APIRouter()


@case_perf.get('/demo', name='开发中')
async def mode():
    pass
