#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: replace_data.py
@Time: 2023/8/9-15:56
"""

import re
import jsonpath
from aiohttp import FormData
from typing import List
from tools.faker_data import FakerData
from sqlalchemy.ext.asyncio import AsyncSession

from apps.whole_conf import crud as conf_crud

COUNT = ['+', '-', '*', '/', '//', '%']


async def replace_params_data(
        db: AsyncSession,
        data: [dict, list],
        api_list: list,
        faker: FakerData,
        code: str = None,
        extract: str = '',
        customize: dict = None
) -> dict:
    """
    替换params和data的值
    """

    async def handle_value(data_json):

        if isinstance(data_json, list):
            return [await handle_value(x) for x in data_json]

        if isinstance(data_json, str):
            return await header_srt(
                db=db,
                x=data_json,
                api_list=api_list,
                faker=faker,
                code=code,
                extract=extract,
                customize=customize
            )

        target = {}
        if not data_json:
            return target

        if isinstance(data_json, FormData):
            return target

        for key in data_json.keys():
            if isinstance(data_json[key], str):
                target[key] = await header_srt(
                    db=db,
                    x=data_json[key],
                    api_list=api_list,
                    faker=faker,
                    code=code,
                    extract=extract,
                    customize=customize
                )
                continue

            if isinstance(data_json[key], dict):
                target[key] = await handle_value(data_json[key])
                continue

            if isinstance(data_json[key], list):
                new_list = []
                for x in data_json[key]:
                    if isinstance(x, (list, dict)):
                        new_list.append(await handle_value(x))
                    elif isinstance(x, str):
                        new_list.append(await header_srt(
                            db=db,
                            x=x,
                            api_list=api_list,
                            faker=faker,
                            code=code,
                            extract=extract,
                            customize=customize
                        ))
                    else:
                        new_list.append(x)

                target[key] = new_list
                continue

            target[key] = data_json[key]

        return target

    return await handle_value(data)


async def replace_url(
        db: AsyncSession,
        old_str: str,
        api_list: list,
        faker: FakerData,
        code: str,
        extract: str,
        customize: dict
) -> str:
    """
    替换url的值
    """
    return await header_srt(
        db=db,
        x=old_str,
        api_list=api_list,
        faker=faker,
        value_type='url',
        code=code,
        extract=extract,
        customize=customize
    )


async def header_srt(
        db: AsyncSession,
        x: str,
        api_list: list,
        faker: FakerData,
        value_type: str = None,
        code: str = None,
        extract: str = '',
        customize: dict = None

):
    """
    处理数据
    :param db:
    :param x:
    :param api_list:
    :param faker:
    :param value_type:
    :param code:
    :param extract:
    :param customize:
    :return:
    """
    # 接口上下级数据关联的参数提取
    if "{{" in x and "$" in x and "}}" in x:
        replace_values: List[str] = re.compile(r'{{(.*?)}}', re.S).findall(x)
        for replace in replace_values:
            try:
                # if 'h$' in x:
                #     new_value = await _header_str_param(x=replace, response=response_headers)
                # else:
                #     new_value = await _header_str_param(x=replace, response=response)
                is_header: bool = True if 'h$' in x else False
                new_value = await _header_str_param(x=replace, api_list=api_list, is_header=is_header)
            except IndexError:
                new_value = ''

            if value_type == 'url':
                x = re.sub("{{(.*?)}}", str(new_value), x, count=1)
                continue

            if isinstance(new_value, (str, float, int)):
                if isinstance(new_value, (float, int)) and [_ for _ in COUNT if _ in x]:
                    x = re.sub("{{(.*?)}}", str(new_value), x, count=1)
                else:
                    x = re.sub("{{(.*?)}}", str(new_value), x, count=1)
            else:
                x = new_value

    # 自定参数提取
    if "%{{" in x and "}}" in x:
        replace_key: List[str] = re.compile(r'%{{(.*?)}}', re.S).findall(x)
        for key in replace_key:
            value = customize.get(key, '_')
            if value == '_':
                customize_info = await conf_crud.get_customize(
                    db=db,
                    key=key
                )
                value = customize_info[0].value if customize_info else None

            if value_type == 'url':
                x = re.sub("%{{(.*?)}}", str(value), x, count=1)
            else:
                x = re.sub("%{{(.*?)}}", str(value), x, count=1)

    # 假数据提取
    if isinstance(x, str) and "{" in x and "}" in x:
        replace_values: List[str] = re.compile(r'{(.*?)}', re.S).findall(x)
        for replace in replace_values:
            if replace == 'get_code':
                x = code
            elif 'get_extract' in replace:
                x = extract
            else:
                new_value = await _header_str_func(x=replace, faker=faker)
                if new_value is None:
                    return x

                if value_type == 'url':
                    x = re.sub("{(.*?)}", str(new_value), x, count=1)
                    continue

                if len(replace) + 2 == len(x):
                    x = new_value
                else:
                    x = re.sub("{(.*?)}", str(new_value), x, count=1)

    return x


async def _header_str_param(x: str, api_list: list, is_header: bool):
    """
    提取参数：字符串内容
    :param x:
    :param api_list:
    :return:
    """
    num, json_path = x.split('.', 1)
    # list列表索引
    list_index = 0
    if "?" in json_path:
        try:
            list_index = int(json_path.split('?', 1)[1])
        except ValueError:
            list_index = 0

    # 字符串索引切片取值
    start_index, end_index = None, None
    if "|" in json_path:
        json_path, str_index = json_path.split('|', 1)
        start_index, end_index = str_index.split(':', 1)

    # 同级邻居确认
    if ',' in json_path:
        json_path, seek_list = json_path.split(',', 1)
        extract_key = json_path.split('.')[-1]
        seek_list = seek_list.split(',')

        value = set()
        for seek in seek_list:
            seek_value, compare, seek_name = seek.strip().split(' ')
            # 同级相邻
            value_set = await _header_adjoin(
                seek_name,
                seek_value,
                compare,
                extract_key,
                api_list[
                    int(num)
                ]['response_info'][-1]['headers'] if is_header else api_list[int(num)]['response_info'][-1]['response'],
            )
            if value_set:
                if not value:
                    value = value_set
                value = value & value_set

        if value:
            return list(value)[list_index]
        else:
            return ''

    value = jsonpath.jsonpath(
        api_list[
            int(num)
        ]['response_info'][-1]['headers'] if is_header else api_list[int(num)]['response_info'][-1]['response'],
        json_path
    )
    if value:
        if start_index is None and end_index is None:
            return value[list_index]
        else:
            if isinstance(value[list_index], str):
                try:
                    return value[list_index][
                           int(start_index):int(
                               end_index) if end_index != '' else None
                           ]
                except ValueError:
                    return value[list_index]
            else:
                return value[list_index]
    else:
        return ''


async def _header_adjoin(seek_name: str, seek_value: str, compare: str, extract_key: str, response_data):
    """

    :param seek_name: 相邻的key
    :param seek_value: 相邻的key的内容
    :param compare: 比较符
    :param extract_key: 需要提取的字段
    :param response_data: 响应内容
    :return:
    """
    path_list = jsonpath.jsonpath(response_data, f'$..{seek_name}', result_type='IPATH')

    if not path_list:
        return []

    value_list = []
    for path in path_list:
        json_data = jsonpath.jsonpath(response_data, f"$.{'.'.join(path)}")
        if compare == 'in' and json_data and seek_value in json_data[0]:
            path[-1] = extract_key
            data = jsonpath.jsonpath(response_data, f"$.{'.'.join(path)}")
            value_list.append(data[0] if data else None)
            continue

        if compare == '==' and json_data and seek_value == json_data[0]:
            path[-1] = extract_key
            data = jsonpath.jsonpath(response_data, f"$.{'.'.join(path)}")
            value_list.append(data[0] if data else None)
            continue

    return set(value_list)


async def _header_str_func(x: str, faker: FakerData):
    """
    处理随机方法生成的数据
    :param x:
    :param faker:
    :return:
    """
    try:
        if '.' in x:
            func, param = x.split('.', 1)
        else:
            func, param = x, 1

        value = faker.faker_data(func=func, param=param)
        if value is None:
            return None

        return value if value else x

    except ValueError:
        return x
