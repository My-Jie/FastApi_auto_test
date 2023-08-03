#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: operation_json.py
@Time: 2022/8/19-23:55
"""

import json


class OperationJson:

    @staticmethod
    async def write(path: str, data: dict):
        """
        写入json
        :param path:
        :param data:
        :return:
        """
        with open(path, 'w', encoding='utf-8') as w:
            w.write(json.dumps(data, indent=2, ensure_ascii=False))

    @staticmethod
    async def read(path: str) -> dict:
        """
        读取json
        :param path:
        :return:
        """
        with open(path, 'r', encoding='utf-8') as r:
            return json.loads(r.read())
