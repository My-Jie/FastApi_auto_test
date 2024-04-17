#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2023/6/9-16:31
"""

import os
import time
import shutil
from fastapi import APIRouter, Depends, UploadFile
from depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse
from starlette.background import BackgroundTask

from apps import response_code
from tools.excel import CreateExcelToUi
from apps.case_ui import schemas, crud
from apps.case_ui.tool import case_data
from apps.whole_conf import crud as conf_crud
from tools import ReadUiExcel
from tools.read_setting import setting

case_ui = APIRouter()


@case_ui.put(
    '/add/playwright',
    name='新增UI用例'
)
async def put_playwright(pd: schemas.PlaywrightIn, db: AsyncSession = Depends(get_db)):
    """
    导入新的playwright脚本文件
    """
    if pd.id:
        temp_id = await crud.get_playwright(db=db, temp_id=pd.id)
        if not temp_id:
            return await response_code.resp_404()

        project_code = await conf_crud.get_project_code(db=db, id_=pd.project_name)
        await crud.update_playwright(
            db=db,
            temp_id=pd.id,
            project_name=project_code,
            temp_name=pd.temp_name,
            rows=pd.text.count('\n'),
            text=pd.text,
        )
        return await response_code.resp_200()

    temp_name = await crud.get_playwright(db=db, temp_name=pd.temp_name)
    if temp_name:
        return await response_code.resp_400(message='存在同名模板')

    await crud.create_playwright(db=db, data=pd, rows=pd.text.count('\n'))
    return await response_code.resp_200()


@case_ui.get(
    '/get/playwright/data',
    name='获取UI数据详情',
    response_model=schemas.PlaywrightOut,
    response_class=response_code.MyJSONResponse,
)
async def get_playwright_data(temp_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取playwright详情
    """
    temp_info = await crud.get_playwright(db=db, temp_id=temp_id)
    return temp_info[0]


@case_ui.get(
    '/get/playwright/list',
    name='获取UI数据列表',
    response_model=schemas.PaginationPlaywright,
    response_class=response_code.MyJSONResponse,
    response_model_exclude=['text']
)
async def get_playwright_list(
        temp_name: str = None,
        page: int = 1,
        size: int = 10,
        db: AsyncSession = Depends(get_db)
):
    """
    获取playwright列表
    """
    temp_info = await crud.get_playwright(db=db, temp_name=temp_name, like=True, page=page, size=size)
    temp_list = []
    for temp in temp_info:
        temp_list.append(
            {
                'id': temp.id,
                'project_name': await conf_crud.get_project_code(db=db, id_=temp.project_name),
                'temp_name': temp.temp_name,
                'rows': temp.rows,
                'run_order': temp.run_order,
                'success': temp.success,
                'fail': temp.fail,
                'text': temp.text,
                'created_at': temp.created_at,
                'updated_at': temp.updated_at,
            }
        )

    return {
        'items': temp_list,
        'total': await crud.get_count(db=db, temp_name=temp_name),
        'page': page,
        'size': size
    }


@case_ui.get(
    '/get/playwright/case/{temp_id}',
    name='获取文本中对应的数据',
)
async def get_playwright_case(temp_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取测试数据
    """
    temp_info = await crud.get_playwright(db=db, temp_id=temp_id)
    if temp_info:
        data = await case_data.get_row_data(playwright_text=temp_info[0].text)
        if data:
            return await response_code.resp_200(data=data)
        else:
            return data
    else:
        return temp_info


@case_ui.get(
    '/down/playwright/data/{temp_id}',
    name='下载文本中的数据'
)
async def down_playwright_data(temp_id: int, db: AsyncSession = Depends(get_db)):
    """
    下载ui测试数据
    """
    temp_info = await crud.get_playwright(db=db, temp_id=temp_id)
    if temp_info:
        case_info = await crud.get_play_case_data(db=db, temp_id=temp_id)
        path = f'./files/excel/{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.xlsx'
        if case_info:
            create = CreateExcelToUi(path=path)
            create.insert(
                names=['rows'] + [x.case_name for x in case_info],
                data=[x.rows_data for x in case_info]
            )
            return FileResponse(
                path=path,
                filename=f'{temp_info[0].temp_name}.xlsx',
                background=BackgroundTask(lambda: os.remove(path))
            )
        else:
            data = await case_data.get_row_data(playwright_text=temp_info[0].text)
            if data:
                create = CreateExcelToUi(path=path)
                create.insert(
                    names=['rows', '原始数据', '数据集1', '数据集2'],
                    data=[data]
                )
                return FileResponse(
                    path=path,
                    filename=f'{temp_info[0].temp_name}.xlsx',
                    background=BackgroundTask(lambda: os.remove(path))
                )
            else:
                return await response_code.resp_400(message='没有提取到内容')
    else:
        return temp_info


@case_ui.post(
    '/upload/playwright/data/',
    name='UI测试数据集上传-Excel'
)
async def upload_data_gather(
        temp_id: int,
        file: UploadFile,
        db: AsyncSession = Depends(get_db)
):
    """
    测试数据集上传
    """
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return await response_code.resp_400(message='文件类型错误，只支持xlsx格式文件')

    temp_data = await crud.get_playwright(db=db, temp_id=temp_id)
    if not temp_data:
        return await response_code.resp_400(message='没有获取到这个模板id')

    path = f'./files/excel/{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.xlsx'
    # 写入本地
    with open(path, 'wb') as w:
        w.write(file.file.read())

    # 读取并处理数据
    gather_data = await ReadUiExcel(path=path, temp_id=temp_id).read()
    # 入库
    await crud.del_play_case_data(db=db, temp_id=temp_id)
    for gather in gather_data:
        await crud.create_play_case_data(db=db, data=schemas.PlaywrightDataIn(**gather))
    return await response_code.resp_200(
        background=BackgroundTask(lambda: os.remove(path))
    )


@case_ui.delete(
    '/del/playwright/data/{temp_id}',
    name='删除UI数据列表,'
)
async def del_playwright_data(temp_id: int, db: AsyncSession = Depends(get_db)):
    """
    删除UI数据列表
    """
    await crud.del_template_data(db=db, temp_id=temp_id)
    shutil.rmtree(f"{setting['allure_path_ui']}/{temp_id}", ignore_errors=True)
    return await response_code.resp_200()


@case_ui.get(
    '/get/playwright/gather/{temp_id}',
    name='获取UI数据集详情',
    response_class=response_code.MyJSONResponse,
)
async def get_playwright_gather(temp_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取UI数据集详情:
    """
    temp_info = await crud.get_playwright(db=db, temp_id=temp_id)
    if temp_info:
        case_info = await crud.get_play_case_data(db=db, temp_id=temp_id)
        if case_info:
            for x in case_info:
                x.rows_data = [{y['row']: y['data']} for y in x.rows_data]
            return case_info
        else:
            return case_info
    else:
        return temp_info


@case_ui.get(
    '/get/remote/browsers',
    name='获取配置好的远程浏览器'
)
async def get_remote_browsers():
    """
    获取配置好的远程浏览器
    """
    data = [
        {
            "key": i + 1,
            "value": f"{data['browser_name']}:{data['browser_version']}"
        } for i, data in enumerate(setting['selenoid']['browsers'])
    ]

    return await response_code.resp_200(data=data)


@case_ui.get(
    '/copy/case',
    name='复制测试用例数据，形成新的测试用例',
)
async def copy_case(temp_id: int, db: AsyncSession = Depends(get_db)):
    temp_info = await crud.get_playwright(db=db, temp_id=temp_id)
    if not temp_info:
        return await response_code.resp_400(message='没有获取到这个用例id')

    project_code = await conf_crud.get_project_code(db=db, id_=temp_info[0].project_name)
    await crud.create_playwright(
        db=db,
        data=schemas.PlaywrightIn(**{
            'project_name': project_code,
            'temp_name': temp_info[0].temp_name + ' - 副本',
            'text': temp_info[0].text,
        }),
        rows=temp_info[0].rows
    )

    return await response_code.resp_200()


@case_ui.delete(
    '/del/gather',
    name='删除数据集'
)
async def del_gather(dg: schemas.DelGrater, db: AsyncSession = Depends(get_db)):
    await crud.del_play_case_data(db=db, temp_id=dg.temp_id, case_ids=dg.gather_ids)
    return await response_code.resp_200()
