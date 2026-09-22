from fastapi import APIRouter, WebSocket
import json

from ..core.services.subscriber_service import get_subscriber_service

from src.core.logger import get_logger
from src.modules.user import authenticate_by_token


logger = get_logger(__name__)

event_notification_router = APIRouter(tags=["event_notification"])


@event_notification_router.websocket("ws/listen_events")
async def listen_messages_websocket(websocket: WebSocket):
    closed = False
    try:
        await websocket.accept()

        ws_service = get_subscriber_service()

        raw_data = await websocket.receive_text()
        try:
            data = json.loads(raw_data)
            token = data.get("auth")
        except Exception:
            await websocket.close(code=1008, reason="Invalid request to auth")
            closed = True
            return

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
        await websocket.send_text(
            json.dumps({"status": "authenticated", "user_uuid": user.uuid})
        )

        async def send_message(message: str) -> None:
            await websocket.send_text(message)

        async def receive_message() -> str:
            return await websocket.receive_text()

        await ws_service.listen_events(
            user_uuid=user.uuid,
            send_message=send_message,
            receive_message=receive_message,
        )
    finally:
        if not closed:
            try:
                await websocket.close(code=4000)
            except Exception as e:
                logger.error(f"Error closing websocket: {e}")
