#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: debug_api.py
@Time: 2023/7/31-22:00
"""

import copy
import json
import aiohttp
from aiohttp import client_exceptions
from sqlalchemy.orm import Session
from apps.template import schemas
from apps import response_code
from tools import get_cookie as cookie_info
from tools import ExtractParamsPath, replace_data, FakerData

RESPONSE_INFO = {}
COOKIE_INFO = {}


async def send_api(db: Session, api_info: schemas.TemplateDataInTwo, get_cookie: bool):
    """
    调试接口专用方法
    :return:
    """
    api_info.headers = {k.title(): v for k, v in api_info.headers.items() if k.lower() != 'content-length'}

    if COOKIE_INFO.get(f"{api_info.temp_id}_{api_info.host}"):
        if api_info.headers.get('Cookie'):
            api_info.headers['Cookie'] = COOKIE_INFO[f"{api_info.temp_id}_{api_info.host}"]

    # 处理下response数据格式
    temp_info = RESPONSE_INFO.get(api_info.temp_id, {})
    temp_list = []
    for i in range(api_info.number):
        if temp_info.get(i):
            temp_list.append(temp_info.get(i, {}).get('response', {}))
        else:
            temp_list.append({})

    fk = FakerData()
    # 识别url表达式
    url = await replace_data.replace_url(
        db=db,
        old_str=f"{api_info.host}{api_info.path}",
        response=temp_list,
        faker=fk,
        code='',
        extract='',
        customize={}
    )
    # 识别params表达式
    params = await replace_data.replace_params_data(
        db=db,
        data=api_info.params,
        response=temp_list,
        faker=fk,
        code='',
        extract='',
        customize={}
    )
    # 识别data表达式
    data = await replace_data.replace_params_data(
        db=db,
        data=api_info.data,
        response=temp_list,
        faker=fk,
        code='',
        extract='',
        customize={}
    )
    # 识别headers中的表达式
    case_header = await replace_data.replace_params_data(
        db=db,
        data=api_info.headers,
        response=temp_list,
        faker=fk,
        customize={}
    )

    req_data = {
        'url': url,
        'method': api_info.method,
        'headers': case_header,
        'params': params,
        f"{'json' if api_info.json_body == 'json' else 'data'}": data,
    }

    async with aiohttp.ClientSession() as sess:
        try:
            async with sess.request(**req_data, allow_redirects=False) as res:
                res_data = await res.json(content_type='application/json' if not api_info.file else None)
        except (json.decoder.JSONDecodeError,):
            res_data = {}
        except (client_exceptions.ContentTypeError, client_exceptions.ClientConnectorError,):
            res_data = {}
        except Exception as e:
            res_data = f"{str(e)}"

        cookie = await cookie_info(rep_type='aiohttp', response=res) if get_cookie else case_header['Cookie']

        res_info = {
            'status': res.status,
            'path': url,
            'params': params,
            'data': data,
            'request-headers': case_header,
            'response-headers': dict(res.headers),
            'response': res_data,
            'cookie': cookie,
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
            RESPONSE_INFO[temp_id][number] = res_info
    else:
        RESPONSE_INFO[temp_id] = {number: res_info}

    COOKIE_INFO[f"{temp_id}_{host}"] = cookie


async def get_jsonpath(
        temp_id,
        number,
        extract_contents,
        type_,
        key_value,
        ext_type,

):
    if RESPONSE_INFO.get(temp_id):

        class Data:
            """
            模拟的一个数据模型，在调用下面处理函数时方便直接使用
            """
            number: int
            path: str
            params: dict
            data: dict
            headers: dict
            response: dict

        temp_data = []
        for k, v in RESPONSE_INFO.get(temp_id).items():
            if k >= number:
                continue

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
        return value_list
    return {'extract_contents': []}


async def del_debug(temp_id: int):
    """
    按模板id删除调试的信息
    :param temp_id:
    :return:
    """
    if RESPONSE_INFO.get(temp_id):
        del RESPONSE_INFO[temp_id]

    cookie_info_ = copy.deepcopy(COOKIE_INFO)
    for k, v in cookie_info_.items():
        id_, _ = k.split('_')
        if temp_id == int(id_):
            del COOKIE_INFO[k]
