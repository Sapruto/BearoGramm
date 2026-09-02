from uuid import uuid4

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.modules.chats.core.services.chat_service import ChatService, get_chat_service
from src.modules.user import UserEntity
from src.modules.chats.chat_types.base.exceptions import ChatNotFoundError, UserNotParticipantError


@pytest.mark.unit
class TestChatService:
    @pytest.mark.asyncio
    async def test_chat_exists_true(
        self, chat_service, chat_repository, sample_chat_entity
    ):
        chat_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service.chat_exists(sample_chat_entity.uuid)

        assert result is True
        chat_repository.get_by_uuid.assert_called_once_with(sample_chat_entity.uuid)

    @pytest.mark.asyncio
    async def test_chat_exists_false(self, chat_service, chat_repository):
        chat_repository.get_by_uuid = AsyncMock(return_value=None)

        result = await chat_service.chat_exists(str(uuid4()))

        assert result is False

    @pytest.mark.asyncio
    async def test_get_chat_success(
        self, chat_service, chat_repository, sample_chat_entity
    ):
        chat_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service.get_chat(sample_chat_entity.uuid)

        assert result == sample_chat_entity
        chat_repository.get_by_uuid.assert_called_once_with(sample_chat_entity.uuid)

    @pytest.mark.asyncio
    async def test_get_chat_not_found(self, chat_service, chat_repository):
        chat_repository.get_by_uuid = AsyncMock(return_value=None)

        result = await chat_service.get_chat(str(uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_get_chat_exception(self, chat_service, chat_repository):
        chat_repository.get_by_uuid = AsyncMock(side_effect=Exception("DB error"))

        result = await chat_service.get_chat(str(uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_get_chat_by_uuid(
        self, chat_service, chat_repository, sample_chat_entity
    ):
        chat_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service.get_chat_by_uuid(sample_chat_entity.uuid)

        assert result == sample_chat_entity

    @pytest.mark.asyncio
    async def test_get_chats_by_user(
        self, chat_service, chat_repository, sample_chat_entity
    ):
        mock_orm = MagicMock()
        chat_repository.manager.get_all_by_stmt = AsyncMock(return_value=[mock_orm, mock_orm])
        chat_repository._to_entity = MagicMock(return_value=sample_chat_entity)

        result = await chat_service.get_chats_by_user(str(uuid4()))

        assert len(result) == 2
        assert result[0] == sample_chat_entity

    @pytest.mark.asyncio
    async def test_get_chats_by_user_exception(self, chat_service, chat_repository):
        chat_repository.manager.get_all_by_stmt = AsyncMock(
            side_effect=Exception("DB error")
        )

        result = await chat_service.get_chats_by_user(str(uuid4()))

        assert result == []

    @pytest.mark.asyncio
    async def test_delete_chat_success(self, chat_service, chat_repository):
        chat_repository.delete_by_uuid = AsyncMock(return_value=1)

        result = await chat_service.delete_chat(str(uuid4()))

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_chat_failed(self, chat_service, chat_repository):
        chat_repository.delete_by_uuid = AsyncMock(return_value=0)

        result = await chat_service.delete_chat(str(uuid4()))

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_chat_exception(self, chat_service, chat_repository):
        chat_repository.delete_by_uuid = AsyncMock(side_effect=Exception("DB error"))

        result = await chat_service.delete_chat(str(uuid4()))

        assert result is False

    @pytest.mark.asyncio
    async def test_get_chat_participants(
        self, chat_service, permission_service, sample_chat_entity
    ):
        permission_service.get_by_resource = AsyncMock(
            return_value=[
                MagicMock(user_uuid="user1"),
                MagicMock(user_uuid="user2"),
            ]
        )
        chat_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service.get_chat_participants(sample_chat_entity.uuid)

        assert len(result) == 2
        assert "user1" in result

    @pytest.mark.asyncio
    async def test_get_chat_participants_chat_not_found(
        self, chat_service, chat_repository
    ):
        chat_repository.get_by_uuid = AsyncMock(return_value=None)

        result = await chat_service.get_chat_participants(str(uuid4()))

        assert result == []

    def test_get_chat_service(self):
        service = get_chat_service()
        assert isinstance(service, ChatService)
