#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2023/9/19-15:14
"""

from apps.status.tool import ConnectionManager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from apps.run_case import CASE_STATUS_LIST, CASE_STATUS
from tools import logger

ws_app = APIRouter()

manager = ConnectionManager()


@ws_app.websocket("/status/{user}")
async def status(websocket: WebSocket, user: str):
    await manager.connect(websocket)
    # await manager.broadcast(f"{user}-开始访问")
    logger.info(f"用例时序表-{user}-开始访问")

    try:
        while True:
            key_id = await websocket.receive_text()
            msg = CASE_STATUS_LIST.get(key_id, [])
            await manager.send_personal_message(msg, websocket)
            CASE_STATUS_LIST[key_id] = []

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"用例时序表-{user}-离开")


@ws_app.websocket("/percentage/{user}")
async def percentage(websocket: WebSocket, user: str):
    await manager.connect(websocket)
    logger.info(f"进度条-{user}-开始访问")

    try:
        while True:
            await websocket.receive_text()
            new_status = sorted(CASE_STATUS.items(), key=lambda x: x[0], reverse=True)
            await manager.send_personal_message(dict(new_status), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"进度条-{user}-离开")
