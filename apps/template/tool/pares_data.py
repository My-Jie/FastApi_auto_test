#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: pares_data.py
@Time: 2022/8/8-15:03
"""

import base64
import json
from tools.global_log import logger

FILTER_MIME_TYPE = [
    'application/javascript',
    'text/css',
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/gif',
    'image/bmp',
    'image/webp',
    'image/x-icon',
    'image/vnd',
    'microsoft.icon',
]


class ParseData:
    """
    解析Har数据
    """

    @classmethod
    async def pares_data(cls, har_data: bytes) -> list:
        data_json = json.loads(har_data.decode('utf-8'))

        temp_info = []
        api_count = 0
        for data in data_json['log']['entries']:
            # 过滤文件接口
            if data['response']['content'].get('mimeType') in FILTER_MIME_TYPE:
                continue

            logger.debug(f"{'=' * 30}开始解析{api_count}{'=' * 30}")
            # logger.debug(f"原始数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            try:
                host = [x['value'] for x in data['request']['headers'] if x['name'] == 'Host'][0]
            except IndexError:
                continue
            http, path = data['request']['url'].split(host, 1)

            # 处理请求中的params数据
            if data['request'].get('queryString'):
                query = {query['name']: query['value'] for query in data['request']['queryString']}
            else:
                query = {}

            # 处理请求中 body和json数据
            if data['request'].get('postData'):
                body_json = await cls._post_data(data['request']['postData'])
            else:
                body_json = ['body', {}]

            if 'application/json' in str(data['response']['content'].get('mimeType')):
                if data['response']['content'].get('text'):
                    res_data = json.loads(base64.b64decode(data['response']['content']['text'].encode('utf-8')))
                else:
                    res_data = {}
            elif 'text/json' in str(data['response']['content'].get('mimeType')):
                res_data = json.loads(data['response']['content']['text'])
            else:
                res_data = {}

            new_data = {
                'number': api_count,
                'host': http + host,
                'path': path.split('?', 1)[0],
                'code': data['response']['status'],
                'method': data['request']['method'],
                'params': query,
                'json_body': 'json' if body_json[0] == 'json' else 'body',
                'data': body_json[1] if body_json[0] != 'file' else {},
                'file': True if body_json[0] == 'file' else False,
                'file_data': body_json[1] if body_json[0] == 'file' else [],
                'headers': {header['name']: header['value'] for header in data['request']['headers']},
                'response': res_data,
            }
            temp_info.append(new_data)
            logger.debug(f"解析数据: {json.dumps(new_data, indent=2, ensure_ascii=False)}")
            logger.debug(f"{'=' * 30}解析完成{api_count}{'=' * 30}")
            api_count += 1

        return temp_info

    @classmethod
    async def _post_data(cls, post_data: dict):
        """
        处理请求数据类型
        :param post_data:
        :return:
        """
        if post_data['mimeType'] is None:
            return ['other', {}]

        if 'application/x-www-form-urlencoded' in post_data['mimeType']:
            return ['body', {params['name']: params['value'] for params in post_data['params']}]

        if 'application/json' in post_data['mimeType']:
            return ['json', json.loads(post_data['text'])]

        if 'multipart/form-data' in post_data['mimeType']:
            return ['file', post_data['params']]

        return ['other', {}]
