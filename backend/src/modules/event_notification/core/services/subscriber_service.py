import asyncio
import json
from typing import Awaitable, Callable, Optional

from src.core.logger import get_logger

from ..registry.registry import get_registry
from ..repositories.subscriber_repository import (
    SubscriberRepository,
    get_subscriber_repository,
)

logger = get_logger(__name__)


class SubscriberService:
    def __init__(
        self,
        subscriber_repository: Optional[SubscriberRepository] = None,
    ):
        self.repo = subscriber_repository or get_subscriber_repository()
        self.registry = get_registry()

    async def subscribe(self, user_uuid: str) -> bool:
        return await self.repo.add_subscriber(user_uuid)

    async def unsubscribe(self, user_uuid: str) -> bool:
        return await self.repo.remove_subscriber(user_uuid)

    async def _handle_event(
        self,
        raw: str,
        send_message: Callable[[str], Awaitable[None]],
    ) -> None:
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Invalid event payload: ", raw)
            return

        event_type = parsed.get("type")
        handler = self.registry.get(event_type)
        if handler is None:
            logger.warning("No handler for event type: ", event_type)
            return

        result = await handler(parsed.get("data", {}))
        if result is not None:
            await send_message(result)

    async def listen_events(
        self,
        user_uuid: str,
        send_message: Callable[[str], Awaitable[None]],
    ) -> None:
        await self.subscribe(user_uuid)

        pubsub = self.repo.redis.pubsub()
        channel = f"user:notifications:{user_uuid}"
        await pubsub.subscribe(channel)

        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode()
                await self._handle_event(data, send_message)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Subscriber listen error: {e}", exc_info=True)
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            await self.unsubscribe(user_uuid)


_subscriber_service: Optional[SubscriberService] = None


def get_subscriber_service() -> SubscriberService:
    global _subscriber_service
    if _subscriber_service is None:
        _subscriber_service = SubscriberService()
    return _subscriber_service
