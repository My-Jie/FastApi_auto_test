#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: response_code.py
@Time: 2022/8/26-11:27
"""

import json
import typing
from fastapi import status
from fastapi.responses import JSONResponse, Response  # , ORJSONResponse,UJSONResponse,JSONResponse
from typing import Union
from starlette.background import BackgroundTask


class MyJSONResponse(JSONResponse):
    """
    重写JSONResponse
    """

    def __init__(
            self,
            content: typing.Any,
            status_code: int = 200,
            headers: typing.Optional[dict] = None,
            media_type: typing.Optional[str] = None,
            background: typing.Optional[BackgroundTask] = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(",", ":"),
        ).encode("utf-8")


async def resp_200(*, data: Union[list, dict, str, int, float] = '', message: str = 'Success',
                   background=None) -> Response:
    return MyJSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'code': 0,
            'message': message,
            'data': data,
        },
        background=background
    )


async def resp_400(*, data: Union[list, dict, str, int, float] = '', message: str = "操作失败") -> Response:
    return MyJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'code': 1,
            'message': message,
            'data': data,
        }
    )


async def resp_404(*, data: Union[list, dict, str, int, float] = '', message: str = "未获取到内容") -> Response:
    return MyJSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            'code': 1,
            'message': message,
            'data': data,
        }
    )
