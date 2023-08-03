#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: check_case_json.py
@Time: 2022/8/21-21:46
"""

from apps.case_service import schemas
from apps.template import crud
from sqlalchemy.orm import Session
from typing import List


class CheckJson:
    """
    校验上传的测试json数据
    """

    @classmethod
    async def check_to_service(cls, db: Session, temp_id: int, case_data: List[schemas.TestCaseData]):
        """
        校验数据
        :param db:
        :param temp_id:
        :param case_data:
        :return:
        """
        temp_info = await crud.get_temp_name(db=db, temp_id=temp_id)
        if temp_info[0].api_count != len(case_data):
            return [f'模板api数量: {temp_info[0].api_count}, 与用例api数量: {len(case_data)}, 不一致']

        keys = ['number', 'path', 'headers', 'params', 'data', 'file', 'check', 'description', 'config']
        msg_list = []
        for x in range(len(case_data)):
            # 校验字段
            msg = [key for key in keys if key not in dict(case_data[x]).keys()]
            if msg:
                msg_list.append(f"用例${x}缺少字段: {','.join(msg)}")
                continue

            # 校验check
            check = dict(case_data[x]).get('check')
            if not check:
                continue

            for k, v in check.items():
                if v is None:
                    continue

                if isinstance(v, (int, float, str, bool, dict)):
                    continue

                if isinstance(v, list) and len(v) < 2:
                    msg_list.append(f"用例${x}比较符内容不足: {k}: {v}")
                    continue

                if v[0] not in ['<', '<=', '==', '!=', '>=', '>', 'in', 'not in', 'notin']:
                    msg_list.append(f"用例${x}比较符填写错误: {k}: {v}")
                else:
                    if v[0] in ['<', '<=', '>=', '>'] and not isinstance(v[1], (int, float)):
                        msg_list.append(f"用例${x}比较类型不匹配: {k}: {v}")
                        continue

                    if v[0] in ['in', 'not in'] and not isinstance(v[1], (list, str)):
                        msg_list.append(f"用例${x}比较类型不匹配: {k}: {v}")
                        continue

                    if v[0] in ['==', '!='] and not isinstance(
                            v[1], (bool, str, dict, int, float, list)
                    ) and v[1] is not None:
                        msg_list.append(f"用例${x}比较类型不匹配: {k}: {v}")
                        continue

                if isinstance(v, list) and k[:4] == 'sql_':
                    if len(v) < 2:
                        msg_list.append(f"用例${x}查询内容不足: {k}: {v}")

                    if 'select' not in v[1]:
                        msg_list.append(f"用例${x}查询条件不足: {k}: {v}")

        return msg_list

    @classmethod
    async def check_to_ddt(cls):
        pass

    @classmethod
    async def check_to_perf(cls):
        pass
