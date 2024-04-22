#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
@File    ：del_status.py
@IDE     ：PyCharm 
@Author  ：Kobayasi
@Date    ：2024/4/22 11:27 
"""

import asyncio
from tools import logger
from apps.run_case import CASE_STATUS, CASE_STATUS_LIST


async def del_status(key_id: str, sleep_time: int = 60):
    await asyncio.sleep(sleep_time)
    if CASE_STATUS_LIST.get(key_id):
        del CASE_STATUS_LIST[key_id]

    if CASE_STATUS.get(key_id):
        del CASE_STATUS[key_id]

    logger.info(f'已延迟 {sleep_time}s 删除ksy_id {key_id}')
