#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: del_temp_data.py
@Time: 2023/2/1-11:09
"""

from typing import List
from sqlalchemy.orm import Session
from apps.template import schemas, crud


class DelTempData:

    @classmethod
    async def del_data(
            cls,
            db: Session,
            temp_id: int,
            num_list: list,
            template_data: List[schemas.TemplateDataOut]
    ):
        # 删除历史数据
        [await crud.del_template_data(db=db, temp_id=temp_id, number=num) for num in num_list]

        # 再从新查询数据更新number
        old_template_data: List[schemas.TemplateDataOut] = await crud.get_template_data(db=db, temp_id=temp_id)
        num = 0
        for x in old_template_data:
            await crud.update_template_data(
                db=db,
                id_=x.id,
                temp_id=temp_id,
                new_number=num
            )
            num += 1

        # 更新api_count
        await crud.update_template(db=db, temp_id=temp_id, api_count=len(template_data) - len(num_list))
