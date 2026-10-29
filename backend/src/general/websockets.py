from starlette.websockets import WebSocket, WebSocketState


async def safe_close(websocket: WebSocket, code: int, reason: str = "") -> None:
    try:
        if (
                websocket.client_state != WebSocketState.DISCONNECTED
                and websocket.application_state != WebSocketState.DISCONNECTED
        ):
            await websocket.close(code=code, reason=reason)
    except Exception:
        pass
