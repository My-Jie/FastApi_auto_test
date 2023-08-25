#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: curl_input.py
@Time: 2023/8/25-15:34
"""

import argparse
import json
from shlex import split
from urllib.parse import urlparse, unquote
from w3lib.http import basic_auth_header


class CurlParser(argparse.ArgumentParser):
    def error(self, message):
        error_msg = 'There was an error parsing the curl command: {}'.format(message)
        raise ValueError(error_msg)


curl_parser = CurlParser()
curl_parser.add_argument('url')
curl_parser.add_argument('-H', '--header', dest='headers', action='append')
curl_parser.add_argument('-X', '--request', dest='method', default='get')
curl_parser.add_argument('-d', '--data-raw', dest='data')
curl_parser.add_argument('-u', '--user', dest='auth')

safe_to_ignore_arguments = [
    ['--compressed'],
    ['-s', '--silent'],
    ['-v', '--verbose'],
    ['-#', '--progress-bar']
]
for argument in safe_to_ignore_arguments:
    curl_parser.add_argument(*argument, action='store_true')


def curl_to_request_kwargs(curl_command: str):
    """
    解析cURl(bash)数据
    :param curl_command:
    :return:
    """
    curl_args = split(curl_command)
    if curl_args[0] != 'curl':
        raise ValueError('A curl command must start with "curl"')
    parsed_args, argv = curl_parser.parse_known_args(curl_args[1:])

    parsed_url = urlparse(parsed_args.url)

    method = 'get' if parsed_args.data is None else 'post'

    result = {
        'host': f"{parsed_args.url.split(parsed_url.netloc)[0]}{parsed_url.netloc}",
        'path': parsed_url.path,
        'method': method.upper() if parsed_args.method == 'get' else parsed_args.method.upper(),
        'json_body': 'body',
        'params': {
            x.split('=')[0]: unquote(x.split('=')[1]) for x in parsed_url.query.split('&')
        } if parsed_url.query else {}
    }
    if parsed_args.data:
        try:
            result['data'] = json.loads(parsed_args.data)
        except json.decoder.JSONDecodeError:
            result['data'] = {x.split('=')[0]: unquote(x.split('=')[1]) for x in parsed_args.data.split('&')}
    else:
        result['data'] = {}

    headers = []
    for header in parsed_args.headers:
        name, val = header.split(':', 1)
        headers.append((name.strip(), val.strip()))
        if name.strip() == 'Content-Type':
            result['json_body'] = 'json' if 'application/json' in val else 'body'

    if parsed_args.auth:
        headers.append(('Authorization', basic_auth_header(*tuple(parsed_args.auth.split(':', 1)))))

    result['headers'] = dict(headers) if headers else {}
    result['response'] = {}
    result['response_headers'] = {}

    return result
