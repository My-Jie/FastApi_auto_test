#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: run_ui.py
@Time: 2023/9/3-21:42
"""

import time
from tools.faker_data import FakerData
from apps.run_case.tool import run


async def run_ui(playwright_text: str, temp_id: int, allure_dir: str):
    """
    生成临时py脚本
    :param playwright_text:
    :param temp_id:
    :param allure_dir:
    :return:
    """

    # 写入临时的py文件
    f = FakerData()
    path = f'./files/tmp/{int(time.time() * 1000)}_{f.faker_data("random_lower", 6)}.py'
    with open(path, 'w', encoding='utf-8') as w:
        w.write(playwright_text)

    # 执行用例
    allure_plus_dir, allure_path = await run(
        test_path=path,
        allure_dir=allure_dir,
        case_id=temp_id,
    )

    return allure_plus_dir, allure_path, path
