#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: charts_free.py
@Time: 2023/7/12-10:45
"""

from typing import List
from collections import Counter
from apps.template import schemas
from apps.case_service import schemas as case_schemas
from apps.case_ddt import schemas as ddt_schemas
from apps.case_ui import schemas as ui_schemas


async def api_free(
        temp_info: List[schemas.TemplateOut],
        case_info: List[case_schemas.TestCaseOut],
        ddt_info: List[ddt_schemas.TestGraterOut]
):
    """
    将模板数据和用例数据关联，处理成树形结构
    :param temp_info:
    :param case_info:
    :param ddt_info:
    :return:
    """
    base_dict = {
        'name': 'api',
        'value': '',
        'children': []
    }

    system = list(set([x.project_name for x in temp_info]))

    base_dict['value'] = len(system)
    for x in system:
        pro = [y for y in temp_info if x == y.project_name]
        project = {
            'name': x,
            'value': len(pro),
            'children': []
        }
        for t in pro:
            case = [z for z in case_info if t.id == z.temp_id]
            temp = {
                'name': t.temp_name,
                'value': len(case),
                'children': []
            }
            for i in case:
                ddt = Counter([d.name for d in ddt_info if d.case_id == i.id])
                dd = {
                    'name': i.case_name,
                    'value': len(ddt),
                    'children': []
                }
                temp['children'].append(dd)
                for k, v in ddt.items():
                    dd['children'].append(
                        {
                            'name': k,
                            'value': v
                        }
                    )

            project['children'].append(temp)

        base_dict['children'].append(project)

    return base_dict


async def ui_free(
        temp_info: List[ui_schemas.PlaywrightOut],
        case_info: List[ui_schemas.PlaywrightDataOut],
):
    """
    将模板数据和用例数据关联，处理成树形结构
    :param temp_info:
    :param case_info:
    :return:
    """
    base_dict = {
        'name': 'ui',
        'value': '',
        'children': []
    }

    system = list(set([x.project_name for x in temp_info]))

    base_dict['value'] = len(system)
    for x in system:
        pro = [y for y in temp_info if x == y.project_name]
        project = {
            'name': x,
            'value': len(pro),
            'children': []
        }
        for t in pro:
            case = [z for z in case_info if t.id == z.temp_id]
            temp = {
                'name': t.temp_name,
                'value': len(case),
                'children': []
            }
            for i in case:
                dd = {
                    'name': i.case_name,
                    'value': f"rows: {len(i.rows_data)}",
                }
                temp['children'].append(dd)

            project['children'].append(temp)

        base_dict['children'].append(project)

    return base_dict
