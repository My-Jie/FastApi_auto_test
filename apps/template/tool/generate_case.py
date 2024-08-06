#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: generate_case.py
@Time: 2022/8/18-16:39
"""

import jsonpath
from typing import List, Any
from apps.template import schemas
from apps.case_service.tool import my_auto_check
from tools.tips import TIPS
from sqlalchemy.ext.asyncio import AsyncSession


class GenerateCase:

    async def read_template_to_api(
            self,
            db: AsyncSession,
            temp_name: str,
            mode: str,
            fail_stop: bool,
            template_data: List[schemas.TemplateDataOut]
    ):
        """
        读取模板生成准测试数据
        :param db:
        :param temp_name:
        :param mode:
        :param fail_stop:
        :param template_data:
        :return:
        """
        response = [x.response for x in template_data]

        case_data_list = []
        temp_id = None
        for num, template in enumerate(template_data):
            if num == 0:
                params = template.params
                data = template.data
            else:
                params = await self._extract_params_keys(param=template.params, response=response[:num])
                data = await self._extract_params_keys(param=template.data, response=response[:num])
            auto_check = await my_auto_check(db=db)
            case_data = {
                'number': template.number,
                'path': template.path,
                'headers': {},
                'params': params,
                'data': data,
                'file': True if template.file else False,
                'check': {
                    **{'status_code': template.code},
                    **{k: v for k, v in auto_check.items() if
                       isinstance(template.response, dict) and template.response.get(k) == v}
                },
                'description': template.description,
                'config': {
                    'is_login': True if num == 0 else None,
                    'sleep': 0.3,
                    'stop': False,
                    'code': False,
                    'extract': [],
                    'fail_stop': fail_stop,
                    'skip': False
                }
            }
            temp_id = template.temp_id
            case_data_list.append(case_data)

        return {
            'tips': TIPS,
            'temp_name': temp_name,
            'temp_id': temp_id,
            'mode': mode,
            'data': case_data_list
        }

    @staticmethod
    async def _extract_params_keys(param: [dict, list], response: list) -> dict:
        """
        提取字典中的key
        :param param:
        :param response:
        :return:
        """

        def header_key(data: Any) -> [dict, list, str]:

            if isinstance(data, list):
                return [header_key(x) for x in data]

            if isinstance(data, (str, int, float, bool)):
                return data

            target = {}
            for key in data.keys():
                print(len(response))
                for i, res in enumerate(response):
                    value = jsonpath.jsonpath(res, f"$..{key}")
                    if isinstance(value, list):
                        ipath = jsonpath.jsonpath(res, f"$..{key}", result_type='IPATH')[0]
                        if key.lower() == ipath[-1].lower() and data[key] == value[0] and value[0]:
                            target[key] = "{{" + f"{i}.$.{'.'.join(ipath)}" + "}}"
                            break
                        else:
                            target[key] = data[key]
                    else:
                        target[key] = data[key]
                # else:
                #     if isinstance(data[key], dict):
                #         header_key(data[key])
                #         continue
                #
                #     if isinstance(data[key], list):
                #         for k in data[key]:
                #             if isinstance(k, (list, dict)):
                #                 header_key(k)
                #             else:
                #                 target[key] = data[key]
                #         continue

            return target

        return header_key(param)

    async def read_template_to_ddt(self):
        pass

    async def read_template_to_perf(self):
        pass


async def _auto_extract(
        x: int,
        ipath: str,
        auto_extract: str,
        left_key: str,
        right_key: str,
        lift_value: Any,
        right_value: Any
):
    """
    按不同模式进行匹配
    :param x:
    :param ipath:
    :param auto_extract:
    :param left_key:
    :param right_key:
    :param lift_value:
    :param right_value:
    :return:
    """
    if auto_extract == 'all':
        if left_key.lower() == right_key.lower() and lift_value == right_value and right_value:
            return "{{" + f"{x}.$.{'.'.join(ipath)}" + "}}"
        return ''

    if auto_extract == 'all-diff':
        if left_key == right_key and lift_value == right_value and right_value:
            return "{{" + f"{x}.$.{'.'.join(ipath)}" + "}}"
        return ''

    if auto_extract == 'key':
        if left_key == right_key and right_value:
            return "{{" + f"{x}.$.{'.'.join(ipath)}" + "}}"
        return ''

    if auto_extract == 'value':
        if lift_value == right_value and right_value:
            return "{{" + f"{x}.$.{'.'.join(ipath)}" + "}}"
        return ''
