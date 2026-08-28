import pytest
from unittest.mock import MagicMock, patch

from src.modules.messages.types.message_registry import (
    MessageRegistry,
    get_message_registry,
    init_message_registry,
    _registry,
    _is_init
)
from src.modules.messages.types.base.base_data_service import BaseDataService


@pytest.mark.unit
class TestMessageRegistry:
    def test_registry_creation(self):
        registry = MessageRegistry()
        assert registry._registry == {}

    def test_register_service(self):
        registry = MessageRegistry()
        mock_service = MagicMock(spec=BaseDataService)

        registry.register("test_type", mock_service)

        assert "test_type" in registry._registry
        assert registry._registry["test_type"] == mock_service

    def test_get_data_service_exists(self):
        registry = MessageRegistry()
        mock_service = MagicMock(spec=BaseDataService)
        registry.register("test_type", mock_service)

        result = registry.get_data_service("test_type")

        assert result == mock_service

    def test_get_data_service_not_exists(self):
        registry = MessageRegistry()

        result = registry.get_data_service("unknown_type")

        assert result is None

    def test_get_data_service_case_sensitive(self):
        registry = MessageRegistry()
        mock_service = MagicMock(spec=BaseDataService)
        registry.register("Test_Type", mock_service)

        result = registry.get_data_service("test_type")

        assert result is None

    def test_register_multiple_services(self):
        registry = MessageRegistry()
        mock_service1 = MagicMock(spec=BaseDataService)
        mock_service2 = MagicMock(spec=BaseDataService)

        registry.register("type1", mock_service1)
        registry.register("type2", mock_service2)

        assert registry.get_data_service("type1") == mock_service1
        assert registry.get_data_service("type2") == mock_service2
        assert len(registry._registry) == 2

    def test_override_existing_service(self):
        registry = MessageRegistry()
        mock_service1 = MagicMock(spec=BaseDataService)
        mock_service2 = MagicMock(spec=BaseDataService)

        registry.register("test_type", mock_service1)
        registry.register("test_type", mock_service2)

        assert registry.get_data_service("test_type") == mock_service2
        assert len(registry._registry) == 1

    def test_get_message_registry_init(self):
        with patch('src.modules.messages.types.message_registry._is_init', False):
            with patch('src.modules.messages.types.message_registry.init_message_registry') as mock_init:
                result = get_message_registry()

                mock_init.assert_called_once()
                assert result is not None

    def test_get_message_registry_already_init(self):
        with patch('src.modules.messages.types.message_registry._is_init', True):
            with patch('src.modules.messages.types.message_registry.init_message_registry') as mock_init:
                result = get_message_registry()

                mock_init.assert_not_called()
                assert result is not None
