#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: get_value_path.py
@Time: 2023/2/14-12:58
"""

import re
import jsonpath
from typing import Any
from apps.case_service import schemas


class ExtractParamsPath:
    """
    通过value提取json路径
    """

    @classmethod
    def get_url_path(
            cls,
            extract_contents: str,
            my_data: list,
    ):
        """
        从url字段中获取数据
        :param extract_contents:
        :param my_data:
        :return:
        """
        return {
            'extract_contents': [{
                'jsonpath': f"{x.number}.{x.path}",
                'path': x.path
            } for x in my_data if extract_contents in x.path]
        }

    @classmethod
    def get_value_path(
            cls,
            extract_contents: Any,
            my_data: list,
            type_: schemas.RepType,
            key_value: schemas.KeyValueType,
            ext_type: schemas.ExtType
    ) -> dict:
        """
        获取value的json路径
        :param extract_contents:
        :param my_data:
        :param type_:
        :param key_value:
        :param ext_type:
        :return:
        """

        path_list = []
        for data in my_data:
            if type_ == schemas.RepType.params:
                if key_value == schemas.KeyValueType.value:
                    value_path_list = cls._get_json_path(
                        extract_contents,
                        key_list=cls._out_function(extract_contents, data.params, ext_type),
                        response=data.params,
                        number=data.number,
                        ext_type=ext_type,
                        path=data.path
                    )
                else:
                    value_path_list = cls._get_key_path(
                        extract_contents,
                        response=data.params,
                        number=data.number,
                        path=data.path
                    )
            elif type_ == schemas.RepType.data:
                if key_value == schemas.KeyValueType.value:
                    value_path_list = cls._get_json_path(
                        extract_contents,
                        key_list=cls._out_function(extract_contents, data.data, ext_type),
                        response=data.data,
                        number=data.number,
                        ext_type=ext_type,
                        path=data.path
                    )
                else:
                    value_path_list = cls._get_key_path(
                        extract_contents,
                        response=data.data,
                        number=data.number,
                        path=data.path
                    )
            elif type_ == schemas.RepType.headers:
                if key_value == schemas.KeyValueType.value:
                    value_path_list = cls._get_json_path(
                        extract_contents,
                        key_list=cls._out_function(extract_contents, data.headers, ext_type),
                        response=data.headers,
                        number=data.number,
                        ext_type=ext_type,
                        path=data.path
                    )
                else:
                    value_path_list = cls._get_key_path(
                        extract_contents,
                        response=data.headers,
                        number=data.number,
                        path=data.path
                    )
            elif type_ == schemas.RepType.response_headers:
                if key_value == schemas.KeyValueType.value:
                    value_path_list = cls._get_json_path(
                        extract_contents,
                        key_list=cls._out_function(extract_contents, data.response_headers, ext_type),
                        response=data.response_headers,
                        number=data.number,
                        ext_type=ext_type,
                        path=data.path,
                        rep_type=schemas.RepType.response_headers
                    )
                else:
                    value_path_list = cls._get_key_path(
                        extract_contents,
                        response=data.response_headers,
                        number=data.number,
                        path=data.path,
                        rep_type=schemas.RepType.response_headers
                    )
            else:
                if key_value == schemas.KeyValueType.value:
                    value_path_list = cls._get_json_path(
                        extract_contents,
                        key_list=cls._out_function(extract_contents, data.response, ext_type),
                        response=data.response,
                        number=data.number,
                        ext_type=ext_type,
                        path=data.path
                    )
                else:
                    value_path_list = cls._get_key_path(
                        extract_contents,
                        response=data.response,
                        number=data.number,
                        path=data.path
                    )

            path_list += value_path_list
        if type_ == schemas.RepType.response or type_ == schemas.RepType.response_headers:
            return {'extract_contents': path_list[:100]}
        return {'extract_contents': path_list[:100]}

    @classmethod
    def _out_function(cls, extract_contents: Any, data: dict, ext_type: schemas.ExtType) -> list:
        """
        提取出和value值相等的key
        :param extract_contents:
        :param data:
        :return:
        """
        target = []

        def in_function(response):
            if isinstance(response, dict):
                for k, v in response.items():
                    if isinstance(v, (list, dict)):
                        if extract_contents == v:
                            target.append(k)
                        else:
                            in_function(v)
                    else:
                        if ext_type == schemas.ExtType.equal and extract_contents == str(v):
                            target.append(k)
                        elif ext_type == schemas.ExtType.contain and extract_contents in str(v):
                            target.append(k)
                        else:
                            in_function(v)

            elif isinstance(response, list):
                for x in range(len(response)):
                    if isinstance(response[x], (list, dict)):
                        if extract_contents == response[x]:
                            target.append(x)
                        else:
                            in_function(response[x])
                    else:
                        if ext_type == schemas.ExtType.equal and extract_contents == str(response[x]):
                            target.append(x)
                        elif ext_type == schemas.ExtType.contain and extract_contents in str(response[x]):
                            target.append(x)
                        else:
                            in_function(response[x])

            return target

        return in_function(data)

    @classmethod
    def _get_json_path(
            cls,
            extract_contents: Any,
            key_list: list,
            response: dict,
            number: int,
            ext_type: schemas.ExtType,
            path: str,
            rep_type: schemas.RepType = 'response'
    ) -> list:
        """
        通过提取出来的key，获取多个ipath，再通过value判断那个ipath是正确的
        :param extract_contents:
        :param key_list:
        :param response:
        :param number:
        :param ext_type:
        :param path:
        :param rep_type:
        :return:
        """
        new_path_list = []
        for key_ in key_list:

            value_list = jsonpath.jsonpath(response, f"$..{key_}")
            path_list = jsonpath.jsonpath(response, f"$..{key_}", result_type='IPATH')

            for k, v in zip(value_list, path_list):
                if ext_type == schemas.ExtType.equal:
                    if str(k) == extract_contents:
                        new_path_list.append({
                            'jsonpath': "{{" + f"{number}.{'$' if rep_type == 'response' else 'h$'}.{'.'.join(v)}" + "}}",
                            'path': path
                        })
                else:
                    if extract_contents in str(k):
                        new_path_list.append({
                            'jsonpath': "{{" + f"{number}.{'$' if rep_type == 'response' else 'h$'}.{'.'.join(v)}" + "}}",
                            'path': path
                        })

        return new_path_list

    @classmethod
    def _get_key_path(
            cls,
            extract_contents: str,
            response: dict,
            number: int,
            path: str,
            rep_type: schemas.RepType = 'response'
    ):
        """
        通过key获取jsonpath
        :param extract_contents:
        :param response:
        :param number:
        :param path:
        :return:
        """
        json_path = jsonpath.jsonpath(response, f"$..{extract_contents}", result_type='IPATH')
        if json_path:
            return [{
                'jsonpath': "{{" + f"{number}.{'$' if rep_type == 'response' else 'h$'}.{'.'.join(x)}" + "}}",
                'path': path
            } for x in json_path]
        else:
            return []


class RepData:
    """
    替换数据
    """

    @classmethod
    def rep_url(cls, url_list: dict, new_str: str, extract_contents: str):
        """
        替换数据预览
        :param url_list:
        :param new_str:
        :param extract_contents:
        :return:
        """
        # new_url_list = []
        for url in url_list['extract_contents']:
            number, json_path = url['jsonpath'].split('.', 1)
            url['old_data'] = extract_contents
            url['new_data'] = new_str
            url['jsonpath'] = 'replace(old, new)'
            url['number'] = int(number)
        return url_list

    @classmethod
    def rep_json(cls, json_data: dict, case_data: list, new_str: str, type_: str):
        """
        替换数据预览
        :param json_data:
        :param case_data:
        :param new_str:
        :param type_:
        :return:
        """
        for data in json_data['extract_contents']:
            bb = re.sub('}}', '', re.sub('{{', '', data['jsonpath']))
            number, json_path = bb.split('.', 1)

            if type_ == 'params':
                old_data = jsonpath.jsonpath(case_data[int(number)].params, f"{json_path}")
                data['old_data'] = old_data[0] if len(old_data) > 0 else False
            elif type_ == 'headers':
                old_data = jsonpath.jsonpath(case_data[int(number)].headers, f"{json_path}")
                data['old_data'] = old_data[0] if len(old_data) > 0 else False
            else:
                old_data = jsonpath.jsonpath(case_data[int(number)].data, f"{json_path}")
                data['old_data'] = old_data[0] if len(old_data) > 0 else False
            data['new_data'] = new_str
            data['number'] = int(number)

        return json_data


async def filter_number(json_data: dict) -> dict:
    """
    过滤
    :param json_data:
    :return:
    """

    new_extract_contents = []
    for i, data in enumerate(json_data['extract_contents']):
        new_data = data['new_data']
        if '{{' in new_data and '$' in new_data and '}}' in new_data:
            aa = re.sub('}}', '', re.sub('{{', '', new_data))
            number, json_path = aa.split('.', 1)
            if data['number'] > int(number):
                new_extract_contents.append(data)
        else:
            new_extract_contents.append(data)
    else:
        json_data['extract_contents'] = new_extract_contents

    return json_data
