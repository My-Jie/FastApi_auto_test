#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: __init__.py.py
@Time: 2022/8/11-16:40
"""

import pathlib
from .excel import CreateExcel, ReadExcel, ReadUiExcel
from .operation_json import OperationJson
from .global_log import logger
from .aiohttp_get_cookie import get_cookie
from .my_sql import AsyncMySql
from .get_value_path import ExtractParamsPath, RepData, filter_number
from .rep_case_data_value import rep_value, rep_url
from .my_selenoid import get_session_id
from .read_setting import setting
from .faker_data import FakerData
from .diff_dict import compare_data, apply_changes


def mkdir():
    """
    按项目创建多级目录
    :return:
    """
    # pathlib.Path(f"{ALLURE_PATH}/allure_plus/1/1").mkdir(parents=True, exist_ok=True)
    pathlib.Path(setting['allure_path']).mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'./files/excel').mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'./files/json').mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'./files/code').mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'./files/tmp').mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'./sqlite').mkdir(parents=True, exist_ok=True)


mkdir()
