#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
@File    ：jsonpath_tips.py
@IDE     ：PyCharm 
@Author  ：Kobayasi
@Date    ：2023/12/21 15:24 
"""

JSONPATH_TIPS = {
    'faker': [
        {
            'label': '身份证',
            'value': '{ssn}',
        },
        {
            'label': '名称',
            'value': '{name}',
        },
        {
            'label': '电话',
            'value': '{phone_number}',
        },
        {
            'label': '银行卡',
            'value': '{credit_card_number}',
        },
        {
            'label': '城市',
            'value': '{city}',
        },
        {
            'label': '地址',
            'value': '{address}',
        },
        {
            'label': '随机数字',
            'value': '{random_int.1} number为长度',
        },
        {
            'label': '随机小写字母',
            'value': '{random_lower.1} number为长度',
        },
        {
            'label': '随机大写字母',
            'value': '{random_upper.1} number为长度',
        },
        {
            'label': '随机大小写字母',
            'value': '{random_letter.1} number为长度',
        },
        {
            'label': '随机汉字',
            'value': '{random_cn.1} number为长度',
        },
        {
            'label': '数字计算',
            'value': '{compute}',
        },
        {
            'label': '时间字符串',
            'value': '{time_str.1} 同时间戳',
        },
        {
            'label': '时间戳',
            'value': '{time_int.0} 0:当前时间, -1:当前时间前一天, 1:当前时间后一天,-2:前一天00:00:00, 2:后一天23:59:59',
        },
    ],
    'jsonpath': [
        {
            'label': '提取response',
            'value': '{{number.$.jsonpath}}',
        },
        {
            'label': '提取response-headers',
            'value': '{{number.h$.jsonpath}}',
        },
        {
            'label': '索引切片(组合时后置)',
            'value': '{{number.$.jsonpath|index:index}}',
        },
        {
            'label': '列表取值(组合时后置)',
            'value': '{{number.$.jsonpath?number}}',
        },
        {
            'label': '同级邻居确认',
            'value': '{{number.$.jsonpath,string in key,string == key}}',
        },
    ],
    'global': [
        {
            'label': '直接提取',
            'value': '%{{key}}',
        },
    ]
}
