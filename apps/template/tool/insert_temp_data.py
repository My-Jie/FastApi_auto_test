#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: insert_temp_data.py
@Time: 2023/1/9-16:14
"""

from typing import List
from sqlalchemy.orm import Session
from apps.template import schemas, crud


class InsertTempData:

    @classmethod
    async def one_data(
            cls,
            db: Session,
            temp_id: int,
            num_list: list,
            har_data: list,
            template_data: List[schemas.TemplateDataOut]
    ):
        """
        按一个序号插入多条数据
        :param db:
        :param temp_id:
        :param num_list:
        :param har_data:
        :param template_data:
        :return:
        """

        # 先插入数据
        index = num_list[0]
        for x in range(len(har_data)):
            har_data[x]['number'] = index + x
            await crud.create_template_data(
                db=db,
                data=schemas.TemplateDataIn(**har_data[x]),
                temp_id=temp_id,
            )

        # 再根据id修改旧数据的number
        for x in template_data:
            if index == x.number:
                for i in template_data[index:]:
                    await crud.update_template_data(
                        db=db,
                        id_=i.id,
                        temp_id=temp_id,
                        old_number=i.number,
                        new_number=i.number + len(har_data)
                    )

        # 更新api_count
        await crud.update_template(db=db, temp_id=temp_id, api_count=len(template_data) + len(har_data))
        return [x for x in range(index, index + len(har_data))]

    @classmethod
    async def many_data(
            cls,
            db: Session,
            temp_id: int,
            num_list: list,
            har_data: list,
            template_data: List[schemas.TemplateDataOut]
    ):
        """
        按序号1对1插入数据
        :param db:
        :param temp_id:
        :param num_list:
        :param har_data:
        :param template_data:
        :return:
        """
        # 先插入数据
        new_id = []
        for x in range(len(har_data)):
            har_data[x]['number'] = num_list[x]
            data_info = await crud.create_template_data(
                db=db,
                data=schemas.TemplateDataIn(**har_data[x]),
                temp_id=temp_id,
            )
            new_id.append(data_info.id)

        # 再根据id修改旧数据的number
        num = 1
        for index in range(len(num_list)):
            for x in template_data[num_list[index]:]:
                await crud.update_template_data(
                    db=db,
                    id_=x.id,
                    temp_id=temp_id,
                    old_number=x.number + index,
                    new_number=x.number + index + num
                )
            num += 1

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
        await crud.update_template(db=db, temp_id=temp_id, api_count=len(old_template_data))
        return [x + num_list[x] for x in range(len(num_list))]
