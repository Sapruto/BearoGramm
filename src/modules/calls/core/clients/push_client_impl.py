from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from src.core.logger import get_logger

logger = get_logger(__name__)


class PushClientImpl(ABC):
    @abstractmethod
    async def send(
        self,
        phone_number: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        pass


class DummyPushClientImpl(PushClientImpl):
    async def send(
        self,
        phone_number: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        logger.info(
            f"DUMMY PUSH EPTA To: {phone_number}, Title: {title}, Body: {body}, Data: {data}"
        )
        return True


_push_impl: Optional[PushClientImpl] = None


def get_push_impl() -> PushClientImpl:
    global _push_impl

    _push_impl = DummyPushClientImpl()

    return _push_impl
