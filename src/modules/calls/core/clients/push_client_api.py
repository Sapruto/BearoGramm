from typing import Optional, Dict, Any
from .push_client_impl import get_push_impl

from src.core.logger import get_logger

logger = get_logger(__name__)


class PushClientAPI:
    def __init__(self):
        self.push_impl = get_push_impl()

    async def send_push_notification(
        self,
        phone_number: str,
        title: str = "",
        body: str = "",
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        try:
            if data is None:
                data = {}

            data["type"] = "incoming_call_push"

            result = await self.push_impl.send(
                phone_number=phone_number, title=title, body=body, data=data
            )

            return result

        except Exception as e:
            logger.error(f"Failed to send push to {phone_number}: {e}")
            return False

    async def send_call_push(
        self,
        phone_number: str,
        caller_uuid: str,
        caller_name: str = "caller_name",
        room_id: Optional[str] = None,
    ) -> bool:
        data = {"caller_uuid": caller_uuid, "room_id": room_id}

        return await self.send_push_notification(
            phone_number=phone_number,
            title=f"{caller_name} звонит",
            body="Нажмите, чтобы ответить",
            data=data,
        )


def get_push_client_api() -> PushClientAPI:
    return PushClientAPI()
