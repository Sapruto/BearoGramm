import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.modules.messages.models.entities.message_entity import MessageEntity, MessageFields
from src.modules.messages.models.orm.message_orm import MessageORM
from src.modules.messages.core.repositories.mappers.message_mapper import MessageMapper
from src.modules.messages.core.repositories.message_repository import MessageRepository
from src.modules.messages.core.services.message_service import MessageService
from src.modules.messages.core.services.data_processor import DataProcessor
from src.modules.messages.core.services.websocket_message_service import WebSocketMessageService
from src.modules.messages.types.text.text_message_data import TextMessageData
from src.modules.messages.types.message_registry import MessageRegistry
from src.modules.chats import ChatServiceAPI
from src.general.repository.sql.sql_query import SqlQuery


@pytest.fixture
def sample_text_data():
    return TextMessageData(text="Hello world", data_type="text_message_type")


@pytest.fixture
def sample_message_entity(sample_text_data):
    return MessageEntity(
        uuid=str(uuid4()),
        message_data=[sample_text_data],
        chat_uuid=str(uuid4()),
        user_uuid=str(uuid4()),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_message_orm(sample_text_data):
    return MessageORM(
        uuid=str(uuid4()),
        message_data=[sample_text_data],
        chat_uuid=str(uuid4()),
        user_uuid=str(uuid4()),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def mock_message_registry():
    registry = MagicMock(spec=MessageRegistry)
    mock_service = MagicMock()
    mock_service.save_data = AsyncMock(return_value=TextMessageData(text="test", data_type="text_message_type"))
    mock_service.delete_data = AsyncMock(return_value=True)
    mock_service.prepare_to_save = AsyncMock(return_value=TextMessageData(text="test", data_type="text_message_type"))
    mock_service.prepare_to_use = AsyncMock(return_value=TextMessageData(text="test", data_type="text_message_type"))
    registry.get_data_service = MagicMock(return_value=mock_service)
    return registry


@pytest.fixture
def mock_chat_service():
    service = MagicMock(spec=ChatServiceAPI)
    service.chat_exists = MagicMock(return_value=True)
    service.user_in_chat = MagicMock(return_value=True)
    service.get_chat_participants = AsyncMock(return_value=[str(uuid4()) for _ in range(3)])
    return service


@pytest.fixture
def message_mapper(mock_message_registry):
    return MessageMapper(message_registry=mock_message_registry)


@pytest.fixture
def mock_message_manager():
    manager = MagicMock()
    manager.save = AsyncMock()
    manager.update = AsyncMock()
    manager.delete = AsyncMock()
    manager.get = AsyncMock()
    manager.get_all = AsyncMock()
    manager.get_by_field = AsyncMock()
    return manager


@pytest.fixture
def message_repository(mock_message_manager, message_mapper):
    repo = MessageRepository(manager=mock_message_manager)
    repo._mapper = message_mapper
    return repo


@pytest.fixture
def mock_websocket_service():
    service = MagicMock(spec=WebSocketMessageService)
    service.notify_chat_participants = AsyncMock()
    service.notify_user = AsyncMock()
    service.connect = AsyncMock(return_value=True)
    service.disconnect = AsyncMock(return_value=True)
    return service


@pytest.fixture
def data_processor(mock_message_registry):
    return DataProcessor(message_registry=mock_message_registry)


@pytest.fixture
def message_service(message_repository, data_processor, mock_websocket_service, mock_chat_service):
    return MessageService(
        message_repository=message_repository,
        data_processor=data_processor,
        websocket_service=mock_websocket_service,
        chat_service=mock_chat_service
    )


@pytest.fixture
def mock_request():
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test_token"}
    request.state = MagicMock()
    return request
