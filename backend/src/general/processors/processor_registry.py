from typing import Dict, Optional
from .base.base_data_processor import BaseDataProcessor


class ProcessorRegistry:
    def __init__(self):
        self._registry: Dict[str, BaseDataProcessor] = {}

    def register(self, data_type: str, service: BaseDataProcessor) -> None:
        self._registry[data_type] = service

    def get_data_service(self, data_type: str) -> Optional[BaseDataProcessor]:
        return self._registry.get(data_type)


_registry = ProcessorRegistry()
_is_init: bool = False


def init_processor_registry():
    from .text import TextTypeName, TextProcessor
    from .media import MediaTypeName, MediaProcessor

    _registry.register(TextTypeName, TextProcessor)
    _registry.register(MediaTypeName, MediaProcessor)


def get_processor_registry() -> ProcessorRegistry:
    global _registry, _is_init
    if not _is_init:
        init_processor_registry()
    return _registry
