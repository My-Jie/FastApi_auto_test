#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: my_selenoid.py
@Time: 2023/6/25-20:02
"""

from tools.read_setting import setting
from selenium import webdriver


async def get_session_id(browser_name: str, browser_version: str, file_name: str):
    """
    获取远程浏览器的session_id
    :param browser_name: 浏览器名称
    :param browser_version: 浏览器版本
    :param file_name: 用例名称，用来生成视频文件
    :return:
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.set_capability("browserName", browser_name)
    chrome_options.set_capability("browserVersion", browser_version)
    chrome_options.set_capability("selenoid:options", {
        "enableVNC": True,
        "enableVideo": True,
        "videoName": f"{file_name}.mp4",
        "enableLog": True,
        "logName": f'{file_name}.log'
    })

    driver = webdriver.Remote(
        command_executor=f"http://{setting['selenoid']['selenoid_hub_host']}/wd/hub",
        options=chrome_options
    )

    return driver.session_id
