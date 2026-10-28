from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
import json

from ..core.services.subscriber_service import get_subscriber_service

from src.core.logger import get_logger
from src.modules.user import authenticate_by_token


logger = get_logger(__name__)

event_notification_router = APIRouter(tags=["event_notification"])


async def safe_close(websocket: WebSocket, code: int, reason: str = "") -> None:
    try:
        if (
                websocket.client_state != WebSocketState.DISCONNECTED
                and websocket.application_state != WebSocketState.DISCONNECTED
        ):
            await websocket.close(code=code, reason=reason)
    except Exception:
        pass


@event_notification_router.websocket("/ws/listen_events/")
async def listen_events_websocket(websocket: WebSocket):
    await websocket.accept()

    try:
        ws_service = get_subscriber_service()

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

        await ws_service.listen_events(
            user_uuid=user.uuid,
            send_message=send_message,
            receive_message=receive_message,
        )

    except WebSocketDisconnect:
        logger.info("Client disconnected from events websocket")
    except Exception:
        logger.exception("Unexpected error in events websocket")
        await safe_close(websocket, 1011, "Internal error")
    finally:
        await safe_close(websocket, 1000)
