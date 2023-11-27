#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: handle_host.py
@Time: 2023/4/21-12:27
"""

import re
from typing import List
from apps.template import schemas as temp_schemas


async def whole_host(temp_data: List[temp_schemas.TemplateDataOut], temp_hosts: list = None):
    """
    处理模板中的host，替换掉全局配置中选择的host
    :param temp_data:
    :param temp_hosts:
    :return:
    """
    if not temp_hosts:
        return

    for temp in temp_data:
        for host in temp_hosts:
            # 判断是否使用自定参数，是否有有效的host值
            if host.get('change') and host.get('settingHost') and temp.host == host.get('host'):
                temp.host = host['settingHost']

                for k, v in temp.headers.items():
                    if k.lower() == 'host':
                        if 'http://' in host['settingHost']:
                            host_ = re.findall(r"http://(.*?)/", host['settingHost'] + '/')
                        else:
                            host_ = re.findall(r"https://(.*?)/", host['settingHost'] + '/')
                        temp.headers[k] = host_[0]

                    if host['host'] in v:
                        temp.headers[k] = temp.headers[k].replace(host['host'], host['settingHost'])

                break

    return temp_data
