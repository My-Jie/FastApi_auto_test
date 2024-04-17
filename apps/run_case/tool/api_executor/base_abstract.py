#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
@File    ：base_abstract.py
@IDE     ：PyCharm 
@Author  ：Kobayasi
@Date    ：2024/3/22 10:48 
"""

import abc


class ApiBase(abc.ABC):

    def __init__(self):
        self.api_group: list = []  # 自定义对象，用于收集一些过程数据
        self.report_list: list = []

    @abc.abstractmethod
    async def collect_sql(self, **kwargs):
        """
        收集数据库数据
        :return:
        """

    @abc.abstractmethod
    async def collect_config(self, **kwargs):
        """
        收集配置数据
        :return:
        """

    @abc.abstractmethod
    async def collect_req_data(self, **kwargs):
        """
        处理查询出来的数据，处理成api请求数据
        :return:
        """

    @abc.abstractmethod
    async def executor_api(self, **kwargs):
        """
        执行api请求
        :return:
        """

    @abc.abstractmethod
    async def collect_report(self, **kwargs):
        """
        收集测试报告
        :return:
        """
