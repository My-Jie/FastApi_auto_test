#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2022/8/22-9:51
"""

import os
import time
from sqlalchemy.orm import Session
from typing import List
from fastapi import APIRouter, UploadFile, Depends
from starlette.responses import FileResponse
from starlette.background import BackgroundTask

from depends import get_db
from apps import response_code
from tools import ReadExcel
from .tool import CaseDataGather
from apps.case_ddt import crud, schemas
from apps.case_service import crud as case_crud

case_ddt = APIRouter()


@case_ddt.get(
    '/down/data/gather',
    name='测试数据集下载-Excel'
)
async def down_data_gather(case_id: int, db: Session = Depends(get_db)):
    """
    测试数据集下载，数据集模板下载
    """
    case_data = await case_crud.get_case_data(db=db, case_id=case_id)
    if not case_data:
        return await response_code.resp_404(message='没有获取到这个用例id')

    case_info = await case_crud.get_case_info(db=db, case_id=case_id)
    case_name = case_info[0].case_name

    path = f'./files/excel/{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.xlsx'
    # 查数据集
    case_grater = await crud.get_gather(db=db, case_id=case_id)
    cdg = CaseDataGather()
    if case_grater:
        gather_list = await cdg.header_gather(gather_data=case_grater)
        await cdg.data_gather(case_data=gather_list, path=path, gather=True)
    else:
        await cdg.data_gather(case_data=case_data, path=path, case_name=case_name)

    case_info = await case_crud.get_case_info(db=db, case_id=case_id)
    return FileResponse(
        path=path,
        filename=f'{case_info[0].case_name}.xlsx',
        background=BackgroundTask(lambda: os.remove(path))
    )


@case_ddt.post(
    '/upload/data/gather',
    name='测试数据集上传-Excel'
)
async def upload_data_gather(
        case_id: int,
        file: UploadFile,
        db: Session = Depends(get_db)
):
    """
    测试数据集上传
    """
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return await response_code.resp_400(message='文件类型错误，只支持xlsx格式文件')

    case_data = await case_crud.get_case_info(db=db, case_id=case_id)
    if not case_data:
        return await response_code.resp_404(message='没有获取到这个用例id')

    path = f'./files/excel/{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.xlsx'
    # 写入本地
    with open(path, 'wb') as w:
        w.write(file.file.read())

    # 读取并处理数据
    gather_data = await ReadExcel(path=path, case_id=case_id).read()
    # 入库
    await crud.del_test_gather(db=db, case_id=case_id)
    for gather in gather_data:
        await crud.create_test_gather(db=db, data=schemas.TestGrater(**gather))
    return await response_code.resp_200(
        background=BackgroundTask(lambda: os.remove(path))
    )


@case_ddt.get(
    '/data/gather',
    name='获取数据集数据',
    response_model=List[schemas.TestGraterOut],
    response_class=response_code.MyJSONResponse,
)
async def get_data_gather(case_id: int, db: Session = Depends(get_db)):
    """
    获取数据集数据
    """
    gather_info = await crud.get_gather(db=db, case_id=case_id)
    if not gather_info:
        return await response_code.resp_404(message='这个用例没有上传数据集')

    return gather_info
