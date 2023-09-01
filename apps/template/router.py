#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2022/8/4-15:30
"""

import os
import time
import json
from typing import List, Any
from pydantic import HttpUrl
from fastapi import APIRouter, UploadFile, Depends, Form, File, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette.responses import FileResponse
from starlette.background import BackgroundTask
from apps import response_code
from depends import get_db

from apps.case_service import (
    schemas as service_schemas
)
from apps.template import crud, schemas
from apps.case_service import schemas as case_schemas
from apps.case_service import crud as case_crud
from apps.template.tool import ParseData, check_num, GenerateCase, InsertTempData, DelTempData, ReadSwagger
from apps.case_service.tool import refresh, temp_to_case
from apps.whole_conf import crud as conf_crud
from tools import CreateExcel, OperationJson
from .tool import send_api, get_jsonpath, del_debug, curl_to_request_kwargs

template = APIRouter()


@template.post(
    '/upload/har',
    response_model=schemas.TemplateOut,
    response_class=response_code.MyJSONResponse,
    response_model_exclude_unset=True,
    name='上传Charles的har文件-先解析-再写入'
)
async def upload_file_har(
        temp_name: str,
        project_name: str,
        har_type: schemas.HarType,
        file: UploadFile,
        db: Session = Depends(get_db)
):
    """
    1、上传文件后，解析数据，形成模板数据\n
    2、自动过滤掉'js','css','image'\n
    3、记录原始数据，拆解params、body、json数据
    """
    if file.content_type != 'application/har+json':
        return await response_code.resp_400(message=f'文件类型错误，只支持har格式文件')

    if await crud.get_temp_name(db=db, temp_name=temp_name):
        return await response_code.resp_400(message=f'模板名称已存在')

    conf = await conf_crud.get_project(db=db)
    if project_name not in [x.code for x in conf]:
        return await response_code.resp_400(message='项目编码不匹配或未创建项目')

    # 解析数据，拿到解析结果
    temp_info = await ParseData.pares_data(
        har_data=file.file.read(),
        har_type=har_type
    )

    # 创建主表数据
    db_template = await crud.create_template(db=db, temp_name=temp_name, project_name=project_name)
    # 批量写入数据
    for temp in temp_info:
        await crud.create_template_data(db=db, data=schemas.TemplateDataIn(**temp), temp_id=db_template.id)
    return await crud.update_template(db=db, temp_id=db_template.id, api_count=len(temp_info))


@template.post(
    '/analysis/har',
    response_model=List[schemas.TemplateDataIn],
    response_class=response_code.MyJSONResponse,
    response_model_exclude_unset=True,
    name='上传Charles的har文件-仅解析-不写入',
    response_model_exclude=['headers', 'file_data']
)
async def analysis_file_har(file: UploadFile):
    """
    仅解析Charles数据，不返回['headers', 'file_data', 'response']\n
    用于同一接口多次使用时，查看请求数据的不同处
    """
    if file.content_type != 'application/har+json':
        return await response_code.resp_400(message=f'文件类型错误，只支持har格式文件')

    return await ParseData.pares_data(har_data=file.file.read(), har_type=schemas.HarType.charles)


@template.post(
    '/upload/swagger/json',
    name='上传SwaggerJson文件',
    response_model=schemas.TemplateOut,
)
async def upload_swagger_json(
        project_name: str,
        host: HttpUrl,
        file: UploadFile,
        db: Session = Depends(get_db)
):
    """
    上传Swagger的json文件，解析后存入模板，文件名称作为模板名称
    """
    if file.content_type != 'application/json':
        return await response_code.resp_400(message='文件类型错误，只支持json格式文件')

    # 校验数据
    try:
        temp_data = json.loads(file.file.read().decode('utf-8'))
    except json.decoder.JSONDecodeError as e:
        return await response_code.resp_400(message=f'json文件格式有错误: {str(e)}')

    conf = await conf_crud.get_project(db=db)
    if project_name not in [x.code for x in conf]:
        return await response_code.resp_400(message='项目编码不匹配或未创建项目')

    # 解析数据，拿到解析结果
    try:
        rs = ReadSwagger(host)
        temp_info = rs.header(temp_data)
    except KeyError as e:
        return await response_code.resp_400(message=f'Swagger文件内容有错误: {str(e)}')
    else:
        # 创建主表数据
        try:
            db_template = await crud.create_template(
                db=db,
                temp_name=file.filename.split('.')[0],
                project_name=project_name
            )
        except IntegrityError:
            return await response_code.resp_400(message=f'创建数据失败: temp_name 重复')
        else:
            # 批量写入数据
            for temp in temp_info:
                await crud.create_template_data(db=db, data=schemas.TemplateDataIn(**temp), temp_id=db_template.id)
            return await crud.update_template(db=db, temp_id=db_template.id, api_count=len(temp_info))


@template.post(
    '/upload/curl',
    name='解析cURL(bash)数据',
    response_class=response_code.MyJSONResponse,
)
async def upload_curl(
        curl_command: schemas.curlCommand
):
    try:
        data = curl_to_request_kwargs(curl_command=curl_command.curl_command)
        return data
    except IndexError:
        return response_code.resp_400(message='数据格式错误')


@template.put(
    '/insert/har',
    response_model=case_schemas.TestCaseDataOut,
    # response_class=response_code.MyJSONResponse,
    response_model_exclude_unset=True,
    name='插入charles原始数据到模板中，并提供插入数据的预处理数据下载',
    # response_model_exclude=['headers', 'file_data']
)
async def insert_har(
        temp_id: int = Query(description='模板id'),
        numbers: str = Form(description='索引-整数列表,使用英文逗号隔开', min_length=1),
        file: UploadFile = File(description='上传Har文件'),
        db: Session = Depends(get_db)
):
    """
    按num序号，按顺序插入原始数据到模板中
    """
    if file.content_type != 'application/har+json':
        return await response_code.resp_400(message=f'文件类型错误，只支持har格式文件')

    har_data = await ParseData.pares_data(har_data=file.file.read(), har_type=schemas.HarType.charles)
    template_data = await crud.get_template_data(db=db, temp_id=temp_id)
    if not template_data:
        return await response_code.resp_400(message='没有获取到这个模板id')

    try:
        num_list = await check_num(nums=numbers, har_data=har_data, template_data=template_data)
    except ValueError as e:
        return await response_code.resp_400(
            message=f'序号校验错误, 错误:{e}',
            data={
                'numbers': numbers,
                'har_length': len(har_data),
            }
        )
    else:
        if len(num_list) == 1:
            new_numbers = await InsertTempData.one_data(
                db=db,
                temp_id=temp_id,
                num_list=num_list,
                har_data=har_data,
                template_data=template_data
            )
        else:
            new_numbers = await InsertTempData.many_data(
                db=db,
                temp_id=temp_id,
                num_list=num_list,
                har_data=har_data,
                template_data=template_data
            )

    test_data = await GenerateCase().read_template_to_api(
        db=db,
        temp_name=str(temp_id),
        mode=case_schemas.ModeEnum.service,
        fail_stop=True,
        template_data=await crud.get_template_data(db=db, temp_id=temp_id, numbers=new_numbers)
    )

    path = f'./files/json/{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.json'
    await OperationJson.write(path=path, data=test_data)
    return FileResponse(
        path=path,
        filename=f'模板{temp_id}_新增数据.json',
        background=BackgroundTask(lambda: os.remove(path))
    )


@template.put(
    '/swap/one',
    name='编排模板数据的顺序-单次'
)
async def swap_data_one(sdo: schemas.SwapDataOne, db: Session = Depends(get_db)):
    """
    单次替换模板中API的顺序-索引号
    """
    template_data = await crud.get_template_data(db=db, temp_id=sdo.temp_id)
    if not template_data:
        return await response_code.resp_400(message='没有获取到这个模板id')

    # 判断序号
    numbers = {x.number: x.id for x in template_data}
    null_num = [num for num in [sdo.old_number, sdo.new_number] if num not in [x for x in numbers]]
    if null_num:
        return await response_code.resp_400(message=f'序号{null_num} 不在该模板的序号中')

    # 替换number序号
    id_ = numbers[sdo.old_number]
    await crud.update_template_data(db=db, temp_id=sdo.temp_id, id_=id_, new_number=sdo.new_number)
    id_ = numbers[sdo.new_number]
    await crud.update_template_data(db=db, temp_id=sdo.temp_id, id_=id_, new_number=sdo.old_number)

    return await response_code.resp_200(
        data={
            'old_number': sdo.old_number,
            'new_number': sdo.new_number
        }
    )


@template.put(
    '/swap/many',
    name='编排模板数据的顺序-全部'
)
async def swap_data_many(sdm: schemas.SwapDataMany, db: Session = Depends(get_db)):
    """
    依次替换模板中API的顺序-索引号
    """
    template_data = await crud.get_template_data(db=db, temp_id=sdm.temp_id)
    if not template_data:
        return await response_code.resp_400(message='没有获取到这个模板id')

    if len(set(sdm.new_numbers)) != len(template_data):
        return await response_code.resp_400(
            message=f'new_numbers长度：{len(set(sdm.new_numbers))}，'
                    f'与数据库中的numbers长度：{len(template_data)}，不一致'
        )

    # 判断序号
    numbers = {x.number: x.id for x in template_data}
    null_num = [num for num in sdm.new_numbers if num not in [x for x in numbers]]
    if null_num:
        return await response_code.resp_400(message=f'序号{null_num} 不在该模板的序号中')

    # 替换number序号
    num_info = False
    for x in range(len(sdm.new_numbers)):
        if x != sdm.new_numbers[x]:
            await crud.update_template_data(
                db=db,
                temp_id=sdm.temp_id,
                id_=numbers[x],
                new_number=sdm.new_numbers[x]
            )
            num_info = True

    return await response_code.resp_200(
        data={
            'old_number': [x for x in numbers],
            'new_number': sdm.new_numbers
        }
    ) if num_info else await response_code.resp_200(
        message='数据无变化'
    )


@template.delete(
    '/del/part',
    response_model=List[schemas.TemplateDataIn],
    response_class=response_code.MyJSONResponse,
    response_model_exclude_unset=True,
    name='删除部分模板数据',
    response_model_exclude=['headers', 'file_data']
)
async def del_har(
        temp_id: int = Query(description='模板id'),
        numbers: str = Form(description='索引-整数列表,使用英文逗号隔开', min_length=1),
        db: Session = Depends(get_db)
):
    template_data = await crud.get_template_data(db=db, temp_id=temp_id)
    if not template_data:
        return await response_code.resp_400(message='没有获取到这个模板id')

    try:
        num_list = await check_num(nums=numbers, template_data=template_data)
    except ValueError as e:
        return await response_code.resp_400(
            message=f'序号校验错误, 错误:{e}',
            data={
                'numbers': numbers,
            }
        )
    else:
        await DelTempData.del_data(
            db=db,
            temp_id=temp_id,
            num_list=num_list,
            template_data=template_data
        )
        return await response_code.resp_200(
            data={
                'numbers': numbers,
            }
        )


@template.delete(
    '/del/all/{temp_id}',
    name='删除全部模板数据'
)
async def delete_name(temp_id: int, db: Session = Depends(get_db)):
    """
    删除模板数据
    """

    temp_info = await crud.get_temp_name(db=db, temp_id=temp_id)

    if temp_info:
        case_info = await case_crud.get_case(db=db, temp_id=temp_info[0].id)
        if case_info:
            return await response_code.resp_400(message='模板下还存在用例')
        else:
            template_data = await crud.del_template_data_all(db=db, temp_id=temp_info[0].id)
            if template_data:
                return await response_code.resp_200(message='删除成功')
            else:
                return await response_code.resp_400()
    else:
        return await response_code.resp_400()


@template.get(
    '/name/list',
    response_model=schemas.PaginationTempTestCase,
    response_class=response_code.MyJSONResponse,
    response_model_exclude_unset=True,
    name='查询模板数据'
)
async def get_templates(
        temp_name: str = None,
        temp_id: int = None,
        outline: bool = True,
        page: int = 1,
        size: int = 10,
        db: Session = Depends(get_db)
):
    """
    1、查询已存在的测试模板/场景\n
    2、场景包含的测试用例\n
    3、默认返回所有模板
    """
    if temp_id:
        templates = await crud.get_temp_name(db=db, temp_id=temp_id)
    elif temp_name:
        templates = await crud.get_temp_name(db=db, temp_name=temp_name, like=True, page=page, size=size)
    else:
        templates = await crud.get_temp_name(db=db, page=page, size=size)

    out_info = []
    for temp in templates:
        case_info = await crud.get_temp_case_info(db=db, temp_id=temp.id, outline=outline)
        temp_info = {
            'temp_name': temp.temp_name,
            'project_name': temp.project_name,
            'id': temp.id,
            'api_count': temp.api_count,
            'created_at': temp.created_at,
            'updated_at': temp.updated_at,
        } if outline is False else {
            'temp_name': temp.temp_name,
            'id': temp.id,
        }
        temp_info.update(case_info)
        out_info.append(temp_info)

    return {
        'items': out_info,
        'total': await crud.get_count(db=db, temp_name=temp_name),
        'page': page,
        'size': size
    }


@template.put(
    '/name/edit',
    response_model=schemas.TemplateOut,
    response_class=response_code.MyJSONResponse,
    name='修改模板名称'
)
async def update_name(un: schemas.UpdateName, db: Session = Depends(get_db)):
    """
    修改模板名称
    """
    return await crud.put_temp_name(
        db=db,
        temp_id=un.temp_id,
        new_name=un.new_name
    ) or await response_code.resp_400()


@template.get(
    '/data/list',
    response_model=List[schemas.TemplateDataOut],
    response_class=response_code.MyJSONResponse,
    response_model_exclude_unset=True,
    response_model_exclude=['file_data'],
    name='查询模板接口原始数据'
)
async def get_template_data(temp_name: str = None, temp_id: int = None, db: Session = Depends(get_db)):
    """
    按模板名称查询接口原始数据，不返回['headers', 'file_data']
    """
    if temp_name:
        return await crud.get_template_data(db=db, temp_name=temp_name)

    if temp_id:
        return await crud.get_template_data(db=db, temp_id=temp_id)


@template.get(
    '/data/host/list',
    name='查询模板host数据'
)
async def get_temp_host_list(temp_id: int, db: Session = Depends(get_db)):
    """
    查询模板的host列表
    """
    hosts = await crud.get_temp_host(db=db, temp_id=temp_id)
    return hosts


@template.post(
    '/create/new/temp',
    name='创建新的模板'
)
async def create_new_temp(
        temp_name: str,
        project_name: str,
        number_list: List[str],
        db: Session = Depends(get_db)
):
    """
    创建新的模板数据
    """
    temp_name_ = await crud.get_temp_name(db=db, temp_name=temp_name)
    if temp_name_:
        return await response_code.resp_400(message='模板名称重复')

    conf = await conf_crud.get_project(db=db)
    if project_name not in [x.code for x in conf]:
        return await response_code.resp_400(message='项目编码不匹配或未创建项目')

    # 查找数据
    new_temp_info = []
    for i, x in enumerate(number_list):
        try:
            temp_id, number, method = x.split('-')
            temp_info = await crud.get_new_temp_info(
                db=db,
                temp_id=int(temp_id),
                number=int(number),
                method=str(method)
            )
        except ValueError:
            return await response_code.resp_400(message=f'数据拆解失败：{x}')

        if temp_info:
            new_temp_info.append({
                'number': i,
                'host': temp_info.host,
                'path': temp_info.path,
                'code': temp_info.code,
                'method': temp_info.method,
                'params': temp_info.params,
                'json_body': temp_info.json_body,
                'data': temp_info.data,
                'file': temp_info.file,
                'file_data': temp_info.file_data,
                'headers': temp_info.headers,
                'response': temp_info.response,
            })
        else:
            return await response_code.resp_400(message=f'未查到的模板信息：{x}')

    # 创建主表数据
    db_template = await crud.create_template(db=db, temp_name=temp_name, project_name=project_name)
    # 批量写入数据
    for temp in new_temp_info:
        await crud.create_template_data(db=db, data=schemas.TemplateDataIn(**temp), temp_id=db_template.id)
    await crud.update_template(db=db, temp_id=db_template.id, api_count=len(new_temp_info))
    return await response_code.resp_200()


@template.get(
    '/temp/all',
    name='模板全部数据'
)
async def temp_all(db: Session = Depends(get_db)):
    """
    查询模板全部数据
    """
    distinct_list = []
    temp_data = []
    for x in await crud.get_temp_all(db=db):
        if x[3] not in distinct_list:
            distinct_list.append(x[3])
            temp_data.append({
                'temp_id': x[0],
                'number': x[1],
                'method': x[2],
                'path': x[3],
            })
    return temp_data


@template.put(
    '/add/api',
    name='添加模板api',
)
async def add_api(api_info: schemas.TemplateDataInTwo, db: Session = Depends(get_db)):
    """
    新增模板接口，若关联得有用例，则同步新增用例接口
    """
    temp_info = await crud.get_template_data(db=db, temp_id=api_info.temp_id)
    # 校验下数据
    max_number = max([x.number for x in temp_info]) if temp_info else -1
    if api_info.number > max_number + 1:
        return await response_code.resp_400(message=f'number值超过当前最大序号: {max_number} + 1')

    if api_info.number == max_number + 1:
        # 插入数据
        await crud.create_template_data_add(db=db, data=api_info)
        await crud.update_template(db=db, temp_id=api_info.temp_id, api_count=len(temp_info) + 1)
    else:
        # 重新对number进行编号
        number_info = await crud.get_temp_numbers(db=db, temp_id=api_info.temp_id, number=api_info.number)
        for i, x in enumerate(number_info):
            await crud.update_template_data(db=db, temp_id=api_info.temp_id, id_=x.id, new_number=x.number + 1)

        # 插入数据
        await crud.create_template_data_add(db=db, data=api_info)
        await crud.update_template(db=db, temp_id=api_info.temp_id, api_count=len(temp_info) + 1)

    # 对用例进行操作
    for case in await case_crud.get_case(db=db, temp_id=api_info.temp_id):
        if api_info.number == max_number + 1:
            # 插入数据
            case_info = await temp_to_case(db=db, api_info=api_info, case_id=case.id)
            await case_crud.create_test_case_data_add(db=db, data=case_schemas.TestCaseDataInTwo(**case_info))
            await case_crud.update_test_case(db=db, case_id=case.id, case_count=len(temp_info) + 1)
        else:
            # 刷新用例的number
            await refresh(db=db, case_id=case.id, start_number=api_info.number, type_='add')

            case_info = await temp_to_case(db=db, api_info=api_info, case_id=case.id)
            await case_crud.create_test_case_data_add(db=db, data=case_schemas.TestCaseDataInTwo(**case_info))
            await case_crud.update_test_case(db=db, case_id=case.id, case_count=len(temp_info) + 1)

    return await response_code.resp_200()


@template.put(
    '/edit/api',
    name='修改模板api',
)
async def edit_api(api_info: schemas.TemplateDataInTwo, db: Session = Depends(get_db)):
    """
    修改模板接口，若关联得有用例，则同步修改用例接口
    """
    if await crud.update_api_info(db=db, api_info=api_info):
        return await response_code.resp_200()
    else:
        return await response_code.resp_400(message='修改失败，未获取到内容')


@template.delete(
    '/del/api',
    name='删除模板api'
)
async def del_api(temp_id: int, number: int, db: Session = Depends(get_db)):
    """
    删除模板接口，若关联得有用例，则同步删除用例接口
    """
    temp_info = await crud.get_template_data(db=db, temp_id=temp_id, numbers=[number])
    if not temp_info:
        return await response_code.resp_400(message='没有获取到这个模板api数据')

    # 删除数据
    await crud.del_template_data(db=db, temp_id=temp_id, number=number)
    api_count = await crud.get_temp_name(db=db, temp_id=temp_id)
    await crud.update_template(
        db=db,
        temp_id=temp_id,
        api_count=api_count[0].api_count - 1 if api_count[0].api_count - 1 >= 0 else 0
    )

    # 重新对number进行编号
    number_info = await crud.get_temp_numbers(db=db, temp_id=temp_id, number=number + 1)
    for i, x in enumerate(number_info):
        await crud.update_template_data(db=db, temp_id=temp_id, id_=x.id, new_number=x.number - 1)

    # 对用例进行操作
    for case in await case_crud.get_case(db=db, temp_id=temp_id):
        # 删除数据
        await case_crud.del_test_case_data(db=db, case_id=case.id, number=number)
        await case_crud.update_test_case(
            db=db,
            case_id=case.id,
            case_count=case.case_count - 1 if case.case_count - 1 >= 0 else 0
        )

        await refresh(db=db, case_id=case.id, start_number=number, type_='del')

    return await response_code.resp_200()


@template.post(
    '/send/api',
    name='发送测试数据调试',
)
async def send_api_info(api_info: schemas.TemplateDataInTwo, get_cookie: bool, db: Session = Depends(get_db)):
    return await send_api(db=db, api_info=api_info, get_cookie=get_cookie)


@template.get(
    '/response/jsonpath/list',
    name='调试接口获取jsonpath'
)
async def get_jsonpath_list(
        temp_id: int,
        number: int,
        extract_contents: Any,
        type_: service_schemas.RepType,
        key_value: service_schemas.KeyValueType,
        ext_type: service_schemas.ExtType,
):
    return await get_jsonpath(
        temp_id=temp_id,
        number=number,
        extract_contents=extract_contents,
        type_=type_,
        key_value=key_value,
        ext_type=ext_type
    )


@template.delete(
    '/del/debug/info',
    name='按temp_id删除掉缓存的调试信息'
)
async def del_debug_info(temp_id: int):
    await del_debug(temp_id=temp_id)
    return await response_code.resp_200()


@template.get(
    '/download/excel',
    name='下载模板数据-excel',
    # deprecated=True,
    # include_in_schema=False
)
async def download_temp_excel(temp_id: int, db: Session = Depends(get_db)):
    """
    将Charles录制的测试场景原始数据下载到excel
    """
    template_data = await crud.get_template_data(db=db, temp_id=temp_id)
    temp_name = await crud.get_temp_name(db=db, temp_id=temp_id)
    temp_name = temp_name[0].temp_name
    if template_data:
        sheet_name = [temp_name]
        sheet_title = ['host', 'path', 'code', 'params', 'data']
        sheet_data = [
            [
                [x.host, x.path, x.code, x.params, x.data] for x in template_data
            ]
        ]
        path = f'./files/excel/{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.xlsx'
        excel = CreateExcel(path=path)
        excel.insert(sheet_name=sheet_name, sheet_title=sheet_title, sheet_data=sheet_data)

        return FileResponse(
            path=path,
            filename=f'{temp_name}.xlsx',
            background=BackgroundTask(lambda: os.remove(path))
        )
    return await response_code.resp_400()
