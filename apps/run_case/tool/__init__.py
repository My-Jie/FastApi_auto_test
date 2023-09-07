#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: __init__.py.py
@Time: 2022/8/23-14:33
"""

from .run_api import RunApi
from .run_pytest import run, allure_generate
from .header_gatehr import header
from .run_ui import run_ui
from .run_case import run_service_case, run_ddt_case, run_ui_case
from .header_playwright import replace_playwright
from .check_data import check_customize
