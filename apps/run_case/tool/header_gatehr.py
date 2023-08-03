#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: header_gatehr.py
@Time: 2023/3/11-22:36
"""

import copy


async def header(case_data: list, gather_data: list):
    """
    把数据集替换到测试数据中
    :param case_data:
    :param gather_data:
    :return:
    """

    # 把用例按数据集分成多份
    suite = list(set([gather.suite for gather in gather_data]))
    case_list = [copy.deepcopy(case_data) for _ in suite]

    # 替换字段的值
    for suite, case_info in enumerate(case_list):
        for case in case_info:
            for gather in gather_data:
                if suite + 1 == gather.suite and case.number == gather.number:
                    case.params = await _rep_dict(case_data=case.params, gather_data=gather.params)
                    case.data = await _rep_dict(case_data=case.data, gather_data=gather.data)
                    case.check = await _rep_dict(case_data=case.check, gather_data=gather.check)
                    case.headers = await _rep_dict(case_data=case.headers, gather_data=gather.headers)

    return case_list


async def _rep_dict(case_data: dict, gather_data: dict):
    """
    递归替换
    :param case_data:
    :param gather_data:
    :return:
    """

    def inter(data: dict):
        if isinstance(data, str):
            return data

        target = {}
        for k, v in data.items():
            if isinstance(v, dict):
                inter(v)
            elif isinstance(v, list):
                v_list = []
                for x in v:
                    v_list.append(inter(x))
                target[k] = v_list
            else:
                if gather_data.get(k, '_') != '_':
                    target[k] = gather_data[k]
                else:
                    target[k] = v

        return target

    return inter(case_data)
