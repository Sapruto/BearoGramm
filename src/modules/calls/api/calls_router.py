from fastapi import APIRouter, WebSocket

calls_router = APIRouter()

@calls_router.websocket("api/ws/call")
async def call(websocket: WebSocket, phone_number: str):
    pass