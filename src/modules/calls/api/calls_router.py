from fastapi import APIRouter, WebSocket
import json

from src.modules.user import authenticate_by_token
from src.core.logger import get_logger

from .calls_router_names import CallsRoutes
from ..core.services.calls_state_service import get_calls_state_service

logger = get_logger(__name__)

calls_router = APIRouter(prefix=CallsRoutes.base)

@calls_router.websocket(CallsRoutes.call)
async def call(websocket: WebSocket):
    closed = False
    try:
        await websocket.accept()

        raw_data = await websocket.receive_text()
        data = json.loads(raw_data)
        token = data.get('auth')

        if not token:
            await websocket.send_text(json.dumps({"error": "Missing auth token"}))
            await websocket.close(code=1008, reason="Missing auth token")
            closed = True
            return
        user = await authenticate_by_token(token)
        if not user:
            await websocket.send_text(json.dumps({"error": "Invalid token"}))
            await websocket.close(code=1008, reason="Invalid token")
            closed = True
            return
        async def send_message(data: str) -> None:
            await websocket.send_text(data)

        async def receive_message() -> str:
            return await websocket.receive_text()

        ws_service = get_calls_state_service()

        await ws_service.call(
            user_uuid=user.uuid,
            ws_send=send_message,
            ws_receive=receive_message
        )

    finally:
        if not closed:
            try:
                await websocket.close(code=4000)
            except Exception as e:
                logger.error(f"Error closing websocket: {e}")

@calls_router.websocket(CallsRoutes.listen_calls)
async def listen_calls(websocket: WebSocket, phone_number: str):
    closed = False
    try:
        await websocket.accept()

        raw_data = await websocket.receive_text()
        data = json.loads(raw_data)
        token = data.get('auth')

        if not token:
            await websocket.send_text(json.dumps({"error": "Missing auth token"}))
            await websocket.close(code=1008, reason="Missing auth token")
            closed = True
            return
        user = await authenticate_by_token(token)
        if not user:
            await websocket.send_text(json.dumps({"error": "Invalid token"}))
            await websocket.close(code=1008, reason="Invalid token")
            closed = True
            return
        async def send_message(data: str) -> None:
            await websocket.send_text(data)

        async def receive_message() -> str:
            return await websocket.receive_text()

        ws_service = get_calls_state_service()

        await ws_service.listen_calls(
            user_uuid=user.uuid,
            ws_send=send_message,
            ws_receive=receive_message
        )

    finally:
        if not closed:
            try:
                await websocket.close(code=4000)
            except Exception as e:
                logger.error(f"Error closing websocket: {e}")
