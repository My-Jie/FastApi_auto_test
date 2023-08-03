#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: update_case.py
@Time: 2023/3/26-13:54
"""

import re
from typing import List
from sqlalchemy.orm import Session
from apps.case_service import crud, schemas
from apps.template import schemas as temp_schemas
from .auto_check import my_auto_check


async def refresh(db: Session, case_id: int, start_number: int, type_: str):
    """
    刷新用例的number序号和jsonPath中的number
    :param db:
    :param case_id:
    :param start_number:
    :param type_:
    :return:
    """
    # 重新对number进行编号
    number_info = await crud.get_case_numbers(db=db, case_id=case_id, number=start_number)

    if type_ == 'add':
        for i, x in enumerate(number_info):
            await crud.update_api_number(db=db, case_id=case_id, id_=x.id, new_number=x.number + 1)

        for i, x in enumerate(number_info):
            path = await _rep_url(x.path, start_number, 'add')
            params = await _rep_dict(x.params, start_number, 'add')
            data = await _rep_dict(x.data, start_number, 'add')
            check = await _rep_dict(x.check, start_number, 'add')
            headers = await _rep_dict(x.headers, start_number, 'add')
            await crud.update_api_info(db=db, api_info=schemas.TestCaseDataOut1(**{
                'number': x.number,
                'case_id': x.case_id,
                'path': path,
                'headers': headers,
                'params': params,
                'data': data,
                'file': x.file,
                'check': check,
                'description': x.description,
                'config': x.config
            }))
        return

    if type_ == 'del':
        for i, x in enumerate(number_info):
            await crud.update_api_number(db=db, case_id=case_id, id_=x.id, new_number=x.number - 1)

        for i, x in enumerate(number_info):
            path = await _rep_url(x.path, start_number, 'del')
            params = await _rep_dict(x.params, start_number, 'del')
            data = await _rep_dict(x.data, start_number, 'del')
            check = await _rep_dict(x.check, start_number, 'del')
            headers = await _rep_dict(x.headers, start_number, 'del')
            await crud.update_api_info(db=db, api_info=schemas.TestCaseDataOut1(**{
                'number': x.number,
                'case_id': x.case_id,
                'path': path,
                'headers': headers,
                'params': params,
                'data': data,
                'file': x.file,
                'check': check,
                'description': x.description,
                'config': x.config
            }))


async def temp_to_case(db: Session, case_id: int, api_info: temp_schemas.TemplateDataInTwo):
    """
    将模板数据转为用例数据
    :param case_id:
    :param api_info:
    :return:
    """
    auto_check = await my_auto_check(db=db)

    return {
        'case_id': case_id,
        'number': api_info.number,
        'path': api_info.path,
        'headers': api_info.headers,
        'params': api_info.params,
        'data': api_info.data,
        'file': api_info.file,
        'check': {
            **{'status_code': api_info.code},
            **{k: v for k, v in auto_check.items() if
               isinstance(api_info.response, dict) and api_info.response.get(k) == v}
        },
        'description': api_info.description,
        'config': {
            'is_login': None,
            'sleep': 0.3,
            'stop': False,
            'code': False,
            'extract': [],
            'fail_stop': False
        }
    }


async def _rep_dict(case_data: dict, start_number: int, type_: str):
    """
    递归替换
    :param case_data:
    :param start_number:
    :param type_:
    :return:
    """

    def inter(data: dict):
        target = {}

        if isinstance(data, str):
            if "{{" in data and "$" in data and "}}" in data:
                replace_values: List[str] = re.compile(r'{{(.*?)}}', re.S).findall(data)
                v = ''
                for replace in replace_values:
                    number, json_path = replace.split('.', 1)
                    if int(number) >= start_number:
                        if type_ == 'add':
                            v = re.sub("{{(.*?)}}", "{{" + f"{int(number) + 1}.{json_path}" + "}}", data, count=1)
                        if type_ == 'del':
                            v = re.sub("{{(.*?)}}", "{{" + f"{int(number) - 1}.{json_path}" + "}}", data, count=1)
                    else:
                        v = re.sub("{{(.*?)}}", "{{" + f"{int(number)}.{json_path}" + "}}", data, count=1)
                return v
            else:
                return data

        for k, v in data.items():
            if isinstance(v, dict):
                inter(v)
            elif isinstance(v, list):
                v_list = []
                for x in v:
                    v_list.append(inter(x))
                target[k] = v_list
            else:
                if isinstance(v, str):
                    if "{{" in v and "$" in v and "}}" in v:
                        replace_values: List[str] = re.compile(r'{{(.*?)}}', re.S).findall(v)
                        for replace in replace_values:
                            number, json_path = replace.split('.', 1)
                            if int(number) >= start_number:
                                if type_ == 'add':
                                    v = re.sub("{{(.*?)}}", "{{" + f"{int(number) + 1}.{json_path}" + "}}", v, count=1)
                                if type_ == 'del':
                                    v = re.sub("{{(.*?)}}", "{{" + f"{int(number) - 1}.{json_path}" + "}}", v, count=1)
                            else:
                                v = re.sub("{{(.*?)}}", "{{" + f"{int(number)}.{json_path}" + "}}", v, count=1)
                        target[k] = v
                    else:
                        target[k] = v
                else:
                    target[k] = v

        return target

    return inter(case_data)


async def _rep_url(url: str, start_number: int, type_: str):
    """
    替换url数据
    :param url:
    :param start_number:
    :param type_:
    :return:
    """
    if "{{" in url and "$" in url and "}}" in url:
        replace_values: List[str] = re.compile(r'{{(.*?)}}', re.S).findall(url)
        for replace in replace_values:
            number, json_path = replace.split('.', 1)
            if int(number) >= start_number:
                if type_ == 'add':
                    url = re.sub("{{(.*?)}}", "{{" + f"{int(number) + 1}.{json_path}" + "}}", url, count=1)
                if type_ == 'del':
                    url = re.sub("{{(.*?)}}", "{{" + f"{int(number) - 1}.{json_path}" + "}}", url, count=1)
            else:
                url = re.sub("{{(.*?)}}", "{{" + f"{int(number)}.{json_path}" + "}}", url, count=1)

    return url
