from enum import Enum
from typing import Any, Awaitable, Callable, Dict, Optional


EventHandler = Callable[[Dict[str, Any]], Awaitable[Optional[str]]]


class HandlerRegistry:
    def __init__(self) -> None:
        self._handlers: Dict[Enum, EventHandler] = {}

    def register(self, event_type: Enum, handler: EventHandler) -> None:
        if event_type in self._handlers:
            raise ValueError(f"Handler for {event_type} already registered")
        self._handlers[event_type] = handler

    def register_from_dict(self, mapping: Dict[Enum, EventHandler]) -> None:
        for event_type, handler in mapping.items():
            self.register(event_type, handler)

    def unregister(self, event_type: Enum) -> None:
        self._handlers.pop(event_type, None)

    def get(self, event_type: Enum) -> Optional[EventHandler]:
        return self._handlers.get(event_type)

    def has(self, event_type: Enum) -> bool:
        return event_type in self._handlers

    def clear(self) -> None:
        self._handlers.clear()

    def __contains__(self, event_type: Enum) -> bool:
        return event_type in self._handlers

    def __len__(self) -> int:
        return len(self._handlers)


class HandlerInitializer:
    _registry: Optional[HandlerRegistry] = None

    @classmethod
    def get_registry(cls) -> HandlerRegistry:
        if cls._registry is None:
            cls._registry = cls._build_registry()
        return cls._registry

    @classmethod
    def reset(cls) -> None:
        cls._registry = None

    @classmethod
    def _build_registry(cls) -> HandlerRegistry:
        registry = HandlerRegistry()

        from ..handlers.messages import message_handlers

        registry.register_from_dict(message_handlers)

        return registry


def get_registry() -> HandlerRegistry:
    return HandlerInitializer.get_registry()
