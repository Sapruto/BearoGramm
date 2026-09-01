import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.modules.chats.api.chat_service_api import ChatServiceAPI, get_chat_service_api
from src.modules.chats.models.message_action_type import MessageActionType
from src.modules.chats.chat_types.personal.models.personal_access_type import (
    PersonalAccessType,
)


@pytest.mark.unit
class TestChatServiceAPI:
    @pytest.mark.asyncio
    async def test_chat_exists_true(
        self, chat_service_api, chat_repository, sample_chat_entity
    ):
        chat_repository.get = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service_api.chat_exists(sample_chat_entity.uuid)

        assert result is True
        chat_repository.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_exists_false(self, chat_service_api, chat_repository):
        chat_repository.get = AsyncMock(return_value=None)

        result = await chat_service_api.chat_exists(str(uuid4()))

        assert result is False

    @pytest.mark.asyncio
    async def test_user_in_chat_true(
        self, chat_service_api, chat_repository, sample_chat_entity
    ):
        chat_repository.get = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service_api.user_in_chat(
            sample_chat_entity.uuid,
            sample_chat_entity.accesses[0].user_uuid,
            MessageActionType.GET,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_user_in_chat_false(
        self, chat_service_api, chat_repository, sample_chat_entity
    ):
        chat_repository.get = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service_api.user_in_chat(
            sample_chat_entity.uuid, str(uuid4()), MessageActionType.GET
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_user_in_chat_chat_not_found(self, chat_service_api, chat_repository):
        chat_repository.get = AsyncMock(return_value=None)

        result = await chat_service_api.user_in_chat(
            str(uuid4()), str(uuid4()), MessageActionType.GET
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_get_chat(
        self, chat_service_api, chat_repository, sample_chat_entity
    ):
        chat_repository.get = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service_api.get_chat(sample_chat_entity.uuid)

        assert result == sample_chat_entity

    @pytest.mark.asyncio
    async def test_get_chat_by_uuid(
        self, chat_service_api, chat_repository, sample_chat_entity
    ):
        chat_repository.get = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service_api.get_chat_by_uuid(sample_chat_entity.uuid)

        assert result == sample_chat_entity

    @pytest.mark.asyncio
    async def test_delete_chat_success(self, chat_service_api, chat_repository):
        chat_repository.delete = AsyncMock(return_value=1)

        result = await chat_service_api.delete_chat(str(uuid4()))

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_chat_failed(self, chat_service_api, chat_repository):
        chat_repository.delete = AsyncMock(return_value=0)

        result = await chat_service_api.delete_chat(str(uuid4()))

        assert result is False

    @pytest.mark.asyncio
    async def test_get_chat_participants(
        self, chat_service_api, chat_repository, sample_chat_entity
    ):
        chat_repository.get = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service_api.get_chat_participants(sample_chat_entity.uuid)

        assert len(result) == 2
        assert sample_chat_entity.accesses[0].user_uuid in result

    @pytest.mark.asyncio
    async def test_get_chat_participants_chat_not_found(
        self, chat_service_api, chat_repository
    ):
        chat_repository.get = AsyncMock(return_value=None)

        result = await chat_service_api.get_chat_participants(str(uuid4()))

        assert result == []

    @pytest.mark.asyncio
    async def test_get_chat_participants_with_get_user_uuid(
        self, chat_service_api, chat_repository
    ):
        mock_access = MagicMock()
        mock_access.get_user_uuid = MagicMock(return_value="test_uuid")
        mock_access.user_uuid = "test_uuid"
        mock_chat = MagicMock()
        mock_chat.accesses = [mock_access]
        chat_repository.get = AsyncMock(return_value=mock_chat)

        result = await chat_service_api.get_chat_participants(str(uuid4()))

        assert len(result) == 1
        assert result[0] == "test_uuid"

    def test_get_chat_service_api(self):
        service = get_chat_service_api()
        assert isinstance(service, ChatServiceAPI)
