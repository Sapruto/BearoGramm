import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from uuid import uuid4

from src.modules.chats.models.entities.chat_entity import ChatEntity
from src.modules.chats.models.orm.chat_orm import ChatORM
from src.modules.chats.core.repositories.mappers.chat_mapper import ChatMapper
from src.modules.chats.core.repositories.chat_repository import ChatRepository
from src.modules.chats.core.services.chat_service import ChatService
from src.modules.chats.api.chat_service_api import ChatServiceAPI
from src.modules.chats.chat_types.base.base_chat_service import BaseChatService
from src.modules.participants import PermissionService
from src.modules.user import UserEntity


@pytest.fixture
def sample_user_uuid():
    return str(uuid4())


@pytest.fixture
def sample_companion_uuid():
    return str(uuid4())


@pytest.fixture
def sample_chat_uuid():
    return str(uuid4())


@pytest.fixture
def sample_chat_entity(sample_chat_uuid):
    return ChatEntity(
        uuid=sample_chat_uuid,
        chat_type="personal",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_chat_manager():
    manager = MagicMock()
    manager.save = AsyncMock()
    manager.delete = AsyncMock()
    manager.get = AsyncMock()
    manager.get_all = AsyncMock()
    manager.get_by_field = AsyncMock()
    manager.count = AsyncMock()
    manager.update = AsyncMock()
    manager.get_by_id = AsyncMock()
    manager.get_all_by_stmt = AsyncMock()
    manager.identifier_field = "uuid"
    manager.model = ChatORM
    return manager


@pytest.fixture
def chat_mapper():
    return ChatMapper()


@pytest.fixture
def chat_repository(mock_chat_manager, chat_mapper):
    repo = ChatRepository(manager=mock_chat_manager)
    repo._mapper = chat_mapper
    repo.get_by_uuid = AsyncMock()
    repo.delete_by_uuid = AsyncMock()
    return repo


@pytest.fixture
def permission_service():
    service = MagicMock(spec=PermissionService)
    service.get_by_resource = AsyncMock()
    service.validate = AsyncMock()
    service.get_by_user_resource = AsyncMock()
    return service


@pytest.fixture
def chat_service(chat_repository, permission_service):
    service = ChatService(
        chat_repository=chat_repository,
        permission_service=permission_service
    )
    return service


@pytest.fixture
def chat_service_api(chat_service):
    return ChatServiceAPI(chat_service=chat_service)


@pytest.fixture
def mock_user():
    return UserEntity(uuid=str(uuid4()))
