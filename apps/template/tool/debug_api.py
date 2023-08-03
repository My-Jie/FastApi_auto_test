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

RESPONSE_INFO = {}


async def send_api(api_info: schemas.TemplateDataInTwo, get_cookie: bool):
    """
    调试接口专用方法
    :param api_info:
    :param get_cookie:
    :return:
    """
    if api_info.headers.get('Content-Length'):
        del api_info.headers['Content-Length']

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

                res_data = await res.json(content_type='application/json' if not api_info.file else None)


        except (
                client_exceptions.ContentTypeError,
                client_exceptions.ClientConnectorError,
        ):
            res_data = {}
        except (
                json.decoder.JSONDecodeError
        ):
            res_data = {}

        except Exception as e:
            res_data = f"{e}"

        cookie = await cookie_info(rep_type='aiohttp', response=res) if get_cookie else ''
        await save_response(
            temp_id=api_info.temp_id,
            number=api_info.number,
            res_info={
                'status': res.status,
                'response-headers': res.headers,
                'response': res_data,
                'cookie': cookie
            }
        )

        return await response_code.resp_200(
            data={
                'status': res.status,
                'response-headers': res.headers,
                'response': res_data,
                'cookie': cookie
            }
        )


async def save_response(temp_id: int, number: int, res_info: dict):
    """
    保存响应到缓存中
    :param temp_id:
    :param number:
    :param res_info:
    :return:
    """
    if RESPONSE_INFO.get(temp_id):
        if RESPONSE_INFO[temp_id].get(number):
            RESPONSE_INFO[temp_id][number] = res_info
        else:
            RESPONSE_INFO[temp_id] = {number: res_info}
    else:
        RESPONSE_INFO[temp_id] = {number: res_info}
