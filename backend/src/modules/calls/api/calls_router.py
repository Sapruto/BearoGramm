from fastapi import APIRouter, WebSocket
import json

from starlette.websockets import WebSocketDisconnect

from src.modules.user import authenticate_by_token
from src.core.logger import get_logger
from src.general.websockets import safe_close

from .calls_router_names import CallsRoutes
from ..core.services.calls_state_service import get_calls_state_service

logger = get_logger(__name__)

calls_router = APIRouter(prefix=CallsRoutes.base)


@calls_router.websocket("/ws/call/{room_uuid}")
async def call(websocket: WebSocket, room_uuid: str):
    await websocket.accept()

    try:
        ws_service = get_calls_state_service()

        raw_data = await websocket.receive_text()
        try:
            token = json.loads(raw_data).get("auth")
        except Exception:
            await safe_close(websocket, 1008, "Invalid request to auth")
            return

        if not token:
            await websocket.send_text(json.dumps({"error": "Missing auth token"}))
            await safe_close(websocket, 1008, "Missing auth token")
            return

        user = await authenticate_by_token(token)
        if not user:
            await websocket.send_text(json.dumps({"error": "Invalid token"}))
            await safe_close(websocket, 1008, "Invalid token")
            return

        await websocket.send_text(
            json.dumps({"status": "authenticated", "user_uuid": user.uuid})
        )

        async def send_message(message: bytes | str) -> None:
            if isinstance(message, (bytes, bytearray)):
                message = message.decode("utf-8")
            elif not isinstance(message, str):
                message = json.dumps(message, default=str)
            await websocket.send_text(message)

        async def receive_message() -> str:
            return await websocket.receive_text()

        await ws_service.handle_call_session(
            user_uuid=user.uuid,
            room_uuid=room_uuid,
            ws_send=send_message,
            ws_receive=receive_message,
        )

    except WebSocketDisconnect:
        logger.info("Client disconnected from events websocket")
    except Exception:
        logger.exception("Unexpected error in events websocket")
        await safe_close(websocket, 1011, "Internal error")
    finally:
        await safe_close(websocket, 1000)
