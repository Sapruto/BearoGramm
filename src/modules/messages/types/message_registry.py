from typing import Dict, Optional
from .base.base_data_service import BaseDataService

class MessageRegistry:
    def __init__(self):
        self._registry: Dict[str, BaseDataService] = {}

    def register(self, data_type: str, service: BaseDataService) -> None:
        self._registry[data_type] = service

    def get_data_service(self, data_type: str) -> Optional[BaseDataService]:
        return self._registry.get(data_type)

_registry = MessageRegistry()
_is_init: bool = False

def init_message_registry():
    from .text import TextMessageTypeName, TextMessageService

    _registry.register(TextMessageTypeName, TextMessageService)

def get_message_registry() -> MessageRegistry:
    global _registry, _is_init
    if not _is_init:
        init_message_registry()
    return _registry
