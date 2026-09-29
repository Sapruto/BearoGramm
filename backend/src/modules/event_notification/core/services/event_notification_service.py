import json
from typing import Any, Dict, Optional

from src.core.logger import get_logger

from ..repositories.subscriber_repository import (
    SubscriberRepository,
    get_subscriber_repository,
)

logger = get_logger(__name__)


class EventNotificationService:
    def __init__(
        self,
        subscriber_repository: Optional[SubscriberRepository] = None,
    ):
        self.repo = subscriber_repository or get_subscriber_repository()

    async def notify_user(
        self, user_uuid: str, notification: Dict[str, Any]
    ) -> None:
        channel = f"user:notifications:{user_uuid}"
        await self.repo.redis.publish(
            channel, json.dumps(notification, ensure_ascii=False)
        )

    async def notify_users(
        self, user_uuids: list[str], notification: Dict[str, Any]
    ) -> None:
        for uuid in user_uuids:
            await self.notify_user(uuid, notification)


def get_notification_event_service() -> EventNotificationService:
    return EventNotificationService()
