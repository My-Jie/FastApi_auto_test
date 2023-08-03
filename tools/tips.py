#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: tips.py
@Time: 2022/8/23-12:54
"""

# TIPS
TIPS: dict = {
    '1': '编写用例时，只需关注path/params/data/check',
    '2': 'headers接受键值对输入，有内容则在执行时添加/替换请求头内容',
    '3': 'is_login标记登录接口，标记后自动获取cookie进行替换',
    '4': {
        '请求参数提取': [
            '1.默认会按key-value完全匹配提取上级接口响应数据',
            "2.参数提取表达式-1'{{number.$.jsonPath表达式}}'",
            "3.参数提取表达式-2'{{number.$.jsonPath表达式}}|index:index'",
            "4.参数提取表达式-3'{{number.$.jsonPath表达式}},string in key,string == key'"
        ],
        '响应数据校验': [
            '1.key为要校验的字段，value为校验的值',
            '2.若value数据类型为: string/integer/float/bool/dict, 按 == 直接进行校验',
            '3.若value数据类型为: list, 索引0应填写比较符: <,<=,==,!=,>=,>,in,not in; 索引1填写比较的值'
        ],
        '数据库校验': [
            '1.key 以 "sql_" 标记开头的字段则需要执行数据库校验',
            '2.value 以 ["期望值", "select查询语句"] 表达式',
        ]
    },
    '5': 'description: 单接口用例描述信息',
    '6': 'mode: 运行模式, 支持: service/ddt/perf',
    '7': {
        'config': {
            'is_login': '是否是登录接口, 默认第一个接口为true',
            'sleep': '接口的等待时间, 默认0.3',
            'stop': '主动停止执行, 默认false',
            'code': '是否识别验证码, 默认false, 需要和假数据表达式{get_code}配合使用',
            'extract': '正则提取表达式[pattern,string], 默认[], 需要和假数据表达式{extract}配合使用',
            'fail_stop': 'True表示用例执行失败，则停止继续执行'
        }
    },
    '8': {"假数据使用表达式'{function.int}'": {
        'name': '名称',
        'ssn': '身份证',
        'phone_number': '电话',
        'credit_card_number': '银行卡',
        'city': '城市',
        'address': '地址',
        'random_int': {
            ':param 1': '长度为1的随机数字',
            ':param 5': '长度为5的随机数字'
        },
        'random_lower': '随机小写字母',
        'random_upper': '随机大写字母',
        'random_letter': '随机大小写字母',
        'random_cn': '随机汉字',
        'compute': '数字计算',
        'time_int': {
            ':param 0': '当前时间',
            ':param -1': '当前时间前一天',
            ':param 1': '当前时间后一天',
            ':param -2': '前一天00:00:00',
            ':param 2': '后一天23:59:59',
        },
        'time_str': '时间字符串, 同上',
        'get_code': '取得验证码, 需要和配置项: code, 配合使用',
        'get_extract': '取得提取内容, 需要和配置项: extract, 配合使用',
    }}
}
