import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from uuid import uuid4

from src.modules.chats.models.entities.chat_entity import ChatEntity
from src.modules.chats.models.orm.chat_orm import ChatORM
from src.modules.chats.core.repositories.mappers.chat_mapper import ChatMapper
from src.modules.chats.chat_types.personal.personal_models.personal_access_type import (
    PersonalAccessType,
)
from src.modules.chats.chat_types.personal.personal_models.personal_access_threshold import (
    PersonalAccessThreshold,
)
from src.modules.chats.chat_types.personal.personal_models.personal_contact import (
    PersonalContact,
)
from src.modules.chats.chat_types.personal.core.personal_repository import (
    PersonalChatRepository,
)
from src.modules.chats.chat_types.personal.core.personal_access_service import (
    PersonalAccessService,
)
from src.general.db.base_manager import BaseManager


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
def sample_personal_access(sample_user_uuid):
    return PersonalAccessType(user_uuid=sample_user_uuid)


@pytest.fixture
def sample_personal_access_blocked(sample_user_uuid, sample_companion_uuid):
    return PersonalAccessType(
        user_uuid=sample_user_uuid,
        is_blocked=True,
        blocked_at=datetime.now(timezone.utc),
        blocked_by=sample_companion_uuid,
    )


@pytest.fixture
def sample_personal_threshold():
    return PersonalAccessThreshold(is_blocked=False, unread_count=0)


@pytest.fixture
def sample_personal_contact(sample_chat_uuid, sample_companion_uuid):
    return PersonalContact(
        chat_uuid=sample_chat_uuid,
        user_uuid=sample_companion_uuid,
        is_blocked=False,
        unread_count=0,
    )


@pytest.fixture
def sample_chat_entity(sample_chat_uuid, sample_user_uuid, sample_companion_uuid):
    return ChatEntity(
        uuid=sample_chat_uuid,
        accesses=[
            PersonalAccessType(user_uuid=sample_user_uuid),
            PersonalAccessType(user_uuid=sample_companion_uuid),
        ],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_chat_manager():
    manager = MagicMock(spec=BaseManager)
    manager.save = AsyncMock()
    manager.delete = AsyncMock()
    manager.get = AsyncMock()
    manager.get_all = AsyncMock()
    manager.get_by_field = AsyncMock()
    manager.count = AsyncMock()
    manager.update = AsyncMock()
    manager.get_by_id = AsyncMock()
    manager.identifier_field = "uuid"
    manager.model = ChatORM
    return manager


@pytest.fixture
def chat_mapper():
    return ChatMapper()


@pytest.fixture
def personal_repository(mock_chat_manager, chat_mapper):
    repo = PersonalChatRepository(manager=mock_chat_manager)
    repo._mapper = chat_mapper
    return repo


@pytest.fixture
def personal_access_service(personal_repository):
    return PersonalAccessService(repo=personal_repository)


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.uuid = str(uuid4())
    return user
