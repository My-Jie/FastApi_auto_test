#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: __init__.py.py
@Time: 2022/8/23-14:33
"""

from .run_pytest import run, allure_generate
from .handle_gatehr import handle
from .run_ui import run_ui
from .run_case import run_service_case, run_ddt_case, run_ui_case
from .handle_playwright import replace_playwright
from .check_data import check_customize
from .assert_case import AssertCase
