#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: header_playwright.py
@Time: 2023/6/25-20:18
"""

from tools.read_setting import setting
from tools import get_session_id
from urllib3 import exceptions
from tools import logger

BROWSER_TEMP: str = f"""
    browser = playwright.chromium.connect_over_cdp(
        args=["--start-maximized"]),
        endpoint_url='ws://{setting['selenoid']['selenoid_ui_host']}/ws/devtools/driver.session_id'
    )
"""


async def replace_playwright(
        playwright_text: str,
        temp_name: str,
        remote: bool,
        remote_id: int,
        headless: bool,
        file_name: str
):
    """
    替换文本内容
    :param playwright_text:
    :param temp_name:
    :param remote: 是否使用远程浏览器
    :param remote_id: 浏览器配置列表id
    :param headless: 无头模式运行
    :param file_name: 用例名称
    :return:
    """

    new_text = playwright_text.replace(
        'case_name', temp_name
    ).replace(
        '{{', ''
    ).replace(
        '}}', ''
    )

    # 无头模式
    if headless:
        new_text = new_text.replace(
            'browser = playwright.chromium.launch(headless=False)',
            'browser = playwright.chromium.launch(headless=True, args=["--start-maximized"])'
        )
    else:
        new_text = new_text.replace(
            'browser = playwright.chromium.launch(headless=False)',
            'browser = playwright.chromium.launch(headless=False, args=["--start-maximized"])'
        )

    # 放大浏览器
    new_text = new_text.replace(
        'browser.new_context()',
        'browser.new_context(no_viewport=True)'
    )

    # 远程运行
    if remote and remote_id:
        se = setting['selenoid']['browsers'][remote_id - 1]
        try:
            session_id = await get_session_id(
                browser_name=se['browser_name'],
                browser_version=se['browser_name'],
                file_name=file_name
            )
            logger.info(f'session_id: {session_id}')
        except exceptions.MaxRetryError:
            return ''
        browser_temp = BROWSER_TEMP.replace('driver.session_id', str(session_id))
        logger.info(f'browser_temp: {browser_temp}')
        new_text = new_text.replace(
            'browser = playwright.chromium.launch(headless=False), args=["--start-maximized"])',
            browser_temp
        )

    return new_text
