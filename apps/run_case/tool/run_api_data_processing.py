#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
@File    ：run_api_data_processing.py
@IDE     ：PyCharm 
@Author  ：Kobayasi
@Date    ：2023/11/27 13:49 
"""

import base64
from aiohttp import FormData
# from apps.template import schemas as temp
# from apps.case_service import schemas as service
from tools import replace_data
from sqlalchemy.orm import Session
from tools.faker_data import FakerData
from .handle_headers import replace_headers


class DataProcessing:
    """
    执行用例前，处理数据：表达式替换
    """

    def __init__(
            self,
            db: Session,
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


def req_info(
        url: str,
        params: dict,
        data: dict,
        case_header: dict,
        temp_data,
        cookies: dict,
):
    """
    接口请求前，处理request信息
    :param url:
    :param params:
    :param data:
    :param case_header:
    :param temp_data:
    :param cookies:
    :return:
    """
    request_info = {
        'url': url,
        'method': temp_data.method,
        'headers': replace_headers(  # 替换headers中的内容
            cookies=cookies,
            tmp_header=temp_data.headers,
            case_header=case_header,
            tmp_host=temp_data.host,
            tmp_file=temp_data.file
        ),
        'params': params,
        f"{'json' if temp_data.json_body == 'json' else 'data'}": data,
    }

    if temp_data.file_data:
        files_data = FormData()
        for file in temp_data.file_data:
            files_data.add_field(
                name=file['name'],
                value=base64.b64decode(file['value'].encode('utf-8')),
                content_type=file['contentType'],
                filename=file['fileName'].encode().decode('unicode_escape')
            )
        request_info['data'] = files_data

    return request_info
