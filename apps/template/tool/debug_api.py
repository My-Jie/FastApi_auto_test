#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: debug_api.py
@Time: 2023/7/31-22:00
"""

import json
import aiohttp
from aiohttp import client_exceptions
from apps.template import schemas
from apps import response_code
from tools import get_cookie as cookie_info
from tools import ExtractParamsPath

RESPONSE_INFO = {}
COOKIE_INFO = {}


async def send_api(api_info: schemas.TemplateDataInTwo, get_cookie: bool):
    """
    调试接口专用方法
    :param api_info:
    :param get_cookie:
    :return:
    """
    api_info.headers = {k.title(): v for k, v in api_info.headers.items() if k.lower() != 'content-length'}

    if COOKIE_INFO.get(f"{api_info.temp_id}_{api_info.host}"):
        if api_info.headers.get('Cookie'):
            api_info.headers['Cookie'] = COOKIE_INFO[f"{api_info.temp_id}_{api_info.host}"]

    req_data = {
        'url': f"{api_info.host}{api_info.path}",
        'method': api_info.method,
        'headers': api_info.headers,
        'params': api_info.params,
        f"{'json' if api_info.json_body == 'json' else 'data'}": api_info.data,
    }
    async with aiohttp.ClientSession() as sess:
        try:
            async with sess.request(**req_data, allow_redirects=False) as res:
                try:
                    res_data = await res.json(content_type='application/json' if not api_info.file else None)
                except (json.decoder.JSONDecodeError,):
                    res_data = {}
        except (client_exceptions.ContentTypeError, client_exceptions.ClientConnectorError,):
            res_data = {}
        except Exception as e:
            res_data = f"{str(e)}"

        cookie = await cookie_info(rep_type='aiohttp', response=res) if get_cookie else ''

        res_info = {
            'status': res.status,
            'path': api_info.path,
            'params': api_info.params,
            'data': api_info.data,
            'request-headers': api_info.headers,
            'response-headers': dict(res.headers),
            'response': res_data,
            'cookie': cookie if cookie else api_info.headers['Cookie'],
        }

        await save_response(
            temp_id=api_info.temp_id,
            number=api_info.number,
            res_info=res_info,
            host=api_info.host,
            cookie=cookie
        )

        return await response_code.resp_200(data=res_info)


async def save_response(temp_id: int, number: int, res_info: dict, host: str, cookie: str):
    """
    保存响应到缓存中
    :param temp_id:
    :param number:
    :param res_info:
    :param host:
    :param cookie:
    :return:
    """
    if RESPONSE_INFO.get(temp_id):
        if RESPONSE_INFO[temp_id].get(number, '_') != '_':
            RESPONSE_INFO[temp_id][number] = res_info
        else:
            RESPONSE_INFO[temp_id] = {number: res_info}
    else:
        RESPONSE_INFO[temp_id] = {number: res_info}

    if cookie:
        COOKIE_INFO[f"{temp_id}_{host}"] = cookie


async def get_jsonpath(
        temp_id,
        extract_contents,
        type_,
        key_value,
        ext_type,

):
    if RESPONSE_INFO.get(temp_id):

        class Data:
            number: int
            path: str
            params: dict
            data: dict
            headers: dict
            response: dict

        temp_data = []
        for k, v in RESPONSE_INFO.get(temp_id).items():
            d = Data()
            d.number = k
            d.path = v['path']
            d.params = v['params']
            d.data = v['data']
            d.headers = v['request-headers']
            d.response = v['response']
            temp_data.append(d)

        value_list = ExtractParamsPath.get_value_path(
            extract_contents=extract_contents,
            my_data=temp_data,
            type_=type_,
            key_value=key_value,
            ext_type=ext_type
        )
        return value_list if value_list.get('extract_contents') else {}
    else:
        return {}
