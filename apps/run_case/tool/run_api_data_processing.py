#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
@File    ：run_api_data_processing.py
@IDE     ：PyCharm 
@Author  ：Kobayasi
@Date    ：2023/11/27 13:49 
"""

from tools import replace_data
from sqlalchemy.ext.asyncio import AsyncSession
from tools.faker_data import FakerData


class DataProcessing:
    """
    执行用例前，处理数据：表达式替换
    """

    def __init__(
            self,
            db: AsyncSession,
            code: str = None,
            extract: str = None,
    ):
        self.db = db
        self.fk = FakerData()
        self.code = code
        self.extract = extract

    async def processing(
            self,
            url: str,
            params: dict,
            data: dict,
            headers: dict,
            check: dict,
            api_list: list,
            customize: dict,
    ):
        """
        一次性处理接口所有的数据
        :return:
        """
        url = await self._url(
            old_str=url,
            api_list=api_list,
            customize=customize
        )

        params = await self._json(
            data=params,
            api_list=api_list,
            customize=customize
        )

        data = await self._json(
            data=data,
            api_list=api_list,
            customize=customize
        )

        headers = await self._json(
            data=headers,
            api_list=api_list,
            customize=customize
        )

        check = await self._json(
            data=check,
            api_list=api_list,
            customize=customize
        )

        return url, params, data, headers, check

    async def _url(
            self,
            old_str: str,
            api_list: list,
            customize: dict,
    ):
        return await replace_data.replace_url(
            db=self.db,
            old_str=old_str,
            api_list=api_list,
            faker=self.fk,
            code=self.code,
            extract=self.extract,
            customize=customize
        )

    async def _json(
            self,
            data: dict,
            api_list: list,
            customize: dict,
    ):
        return await replace_data.replace_params_data(
            db=self.db,
            data=data,
            api_list=api_list,
            faker=self.fk,
            code=self.code,
            extract=self.extract,
            customize=customize
        )
