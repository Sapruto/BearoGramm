from uuid import uuid4

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.modules.chats.core.services.chat_service import ChatService, get_chat_service
from src.modules.chats.chat_types.personal.personal_models.personal_access_type import (
    PersonalAccessType,
)


@pytest.mark.unit
class TestChatService:
    @pytest.mark.asyncio
    async def test_chat_exists_true(
        self, chat_service, chat_repository, sample_chat_entity
    ):
        chat_repository.get_by_id = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service.chat_exists(sample_chat_entity.uuid)

        assert result is True
        chat_repository.get_by_id.assert_called_once_with(sample_chat_entity.uuid)

    @pytest.mark.asyncio
    async def test_chat_exists_false(self, chat_service, chat_repository):
        chat_repository.get_by_id = AsyncMock(return_value=None)

        result = await chat_service.chat_exists(str(uuid4()))

        assert result is False

    @pytest.mark.asyncio
    async def test_user_in_chat_true(
        self, chat_service, chat_repository, sample_chat_entity
    ):
        chat_repository.get_by_id = AsyncMock(return_value=sample_chat_entity)
        user = MagicMock()
        user.uuid = sample_chat_entity.accesses[0].user_uuid

        result = await chat_service.user_in_chat(sample_chat_entity.uuid, user)

        assert result is True

    @pytest.mark.asyncio
    async def test_user_in_chat_false(
        self, chat_service, chat_repository, sample_chat_entity
    ):
        chat_repository.get_by_id = AsyncMock(return_value=sample_chat_entity)
        user = MagicMock()
        user.uuid = str(uuid4())

        result = await chat_service.user_in_chat(sample_chat_entity.uuid, user)

        assert result is False

    @pytest.mark.asyncio
    async def test_user_in_chat_chat_not_found(self, chat_service, chat_repository):
        chat_repository.get_by_id = AsyncMock(return_value=None)
        user = MagicMock()
        user.uuid = str(uuid4())

        result = await chat_service.user_in_chat(str(uuid4()), user)

        assert result is False

    @pytest.mark.asyncio
    async def test_user_in_chat_with_access_get_user_uuid(
        self, chat_service, chat_repository
    ):
        mock_access = MagicMock()
        mock_access.get_user_uuid = MagicMock(return_value="test_uuid")
        mock_chat = MagicMock()
        mock_chat.accesses = [mock_access]
        chat_repository.get_by_id = AsyncMock(return_value=mock_chat)

        user = MagicMock()
        user.uuid = "test_uuid"

        result = await chat_service.user_in_chat(str(uuid4()), user)

        assert result is True

    @pytest.mark.asyncio
    async def test_user_in_chat_exception(self, chat_service, chat_repository):
        chat_repository.get_by_id = AsyncMock(side_effect=Exception("DB error"))
        user = MagicMock()
        user.uuid = str(uuid4())

        result = await chat_service.user_in_chat(str(uuid4()), user)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_chat_success(
        self, chat_service, chat_repository, sample_chat_entity
    ):
        chat_repository.get_by_id = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service.get_chat(sample_chat_entity.uuid)

        assert result == sample_chat_entity
        chat_repository.get_by_id.assert_called_once_with(sample_chat_entity.uuid)

    @pytest.mark.asyncio
    async def test_get_chat_not_found(self, chat_service, chat_repository):
        chat_repository.get_by_id = AsyncMock(return_value=None)

        result = await chat_service.get_chat(str(uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_get_chat_exception(self, chat_service, chat_repository):
        chat_repository.get_by_id = AsyncMock(side_effect=Exception("DB error"))

        result = await chat_service.get_chat(str(uuid4()))

        assert result is None

    def test_get_chat_service(self):
        service = get_chat_service()
        assert isinstance(service, ChatService)
