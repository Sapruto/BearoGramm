import asyncio
import json
from typing import Any, Awaitable, Callable, Dict, Optional

from src.core.logger import get_logger

from ..registry.registry import get_registry
from ..repositories.subscriber_repository import (
    SubscriberRepository,
    get_subscriber_repository,
)

logger = get_logger(__name__)

SendMessage = Callable[[str], Awaitable[None]]


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

    async def handle_incoming(self, user_uuid: str, raw: str) -> Optional[str]:
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Invalid incoming payload: %r", raw)
            return None

        event_type = parsed.get("type")
        if not event_type:
            return None

        data: Dict[str, Any] = parsed.get("data") or {}
        data.setdefault("user_uuid", user_uuid)

        handler = self.registry.get(event_type)
        if handler is None:
            logger.warning("No handler for event type: %s", event_type)
            return None

        try:
            return await handler(data)
        except Exception as e:
            logger.error("Handler error for %s: %s", event_type, e, exc_info=True)
            return None

    async def _redis_to_send(
        self,
        user_uuid: str,
        send_message: SendMessage,
    ) -> None:
        pubsub = self.repo.redis.pubsub()
        channel = f"user:notifications:{user_uuid}"
        await pubsub.subscribe(channel)

        try:
            async for event in pubsub.listen():
                if event.get("type") != "message":
                    continue
                data = event["data"]
                if isinstance(data, bytes):
                    data = data.decode()
                try:
                    await send_message(data)
                except Exception as e:
                    logger.error("send_message failed: %s", e, exc_info=True)
                    break
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error("Redis listen error: %s", e, exc_info=True)
        finally:
            try:
                await pubsub.unsubscribe(channel)
            except Exception:
                pass
            await pubsub.close()

    async def listen_events(
        self,
        user_uuid: str,
        receive_message: Callable[[], Awaitable[str]],
        send_message: SendMessage,
    ) -> None:
        await self.subscribe(user_uuid)

        redis_task = asyncio.create_task(
            self._redis_to_send(user_uuid, send_message),
            name=f"redis->send:{user_uuid}",
        )

        try:
            while True:
                raw = await receive_message()
                reply = await self.handle_incoming(user_uuid, raw)
                if reply is not None:
                    await send_message(reply)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error("listen_events loop error for %s: %s", user_uuid, e, exc_info=True)
        finally:
            redis_task.cancel()
            try:
                await redis_task
            except (asyncio.CancelledError, Exception):
                pass
            await self.unsubscribe(user_uuid)


_subscriber_service: Optional[SubscriberService] = None


def get_subscriber_service() -> SubscriberService:
    global _subscriber_service
    if _subscriber_service is None:
        _subscriber_service = SubscriberService()
    return _subscriber_service
