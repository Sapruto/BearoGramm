import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.modules.chats.api.chat_service_api import ChatServiceAPI, get_chat_service_api


@pytest.mark.unit
class TestChatServiceAPI:
    @pytest.mark.asyncio
    async def test_chat_exists_true(
        self, chat_service_api, chat_service, sample_chat_entity
    ):
        chat_service.chat_exists = AsyncMock(return_value=True)

        result = await chat_service_api.chat_exists(sample_chat_entity.uuid)

        assert result is True
        chat_service.chat_exists.assert_called_once_with(sample_chat_entity.uuid)

    @pytest.mark.asyncio
    async def test_chat_exists_false(self, chat_service_api, chat_service):
        chat_service.chat_exists = AsyncMock(return_value=False)

        result = await chat_service_api.chat_exists(str(uuid4()))

        assert result is False

    @pytest.mark.asyncio
    async def test_get_chat(self, chat_service_api, chat_service, sample_chat_entity):
        chat_service.get_chat = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service_api.get_chat(sample_chat_entity.uuid)

        assert result == sample_chat_entity

    @pytest.mark.asyncio
    async def test_get_chat_by_uuid(
        self, chat_service_api, chat_service, sample_chat_entity
    ):
        chat_service.get_chat_by_uuid = AsyncMock(return_value=sample_chat_entity)

        result = await chat_service_api.get_chat_by_uuid(sample_chat_entity.uuid)

        assert result == sample_chat_entity

    @pytest.mark.asyncio
    async def test_get_chats_by_user(
        self, chat_service_api, chat_service, sample_chat_entity
    ):
        chat_service.get_chats_by_user = AsyncMock(
            return_value=[sample_chat_entity, sample_chat_entity]
        )

        result = await chat_service_api.get_chats_by_user(str(uuid4()))

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_delete_chat_success(self, chat_service_api, chat_service):
        chat_service.delete_chat = AsyncMock(return_value=True)

        result = await chat_service_api.delete_chat(str(uuid4()))

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_chat_failed(self, chat_service_api, chat_service):
        chat_service.delete_chat = AsyncMock(return_value=False)

        result = await chat_service_api.delete_chat(str(uuid4()))

        assert result is False

    @pytest.mark.asyncio
    async def test_get_chat_participants(self, chat_service_api, chat_service):
        chat_service.get_chat_participants = AsyncMock(
            return_value=["user1", "user2"]
        )

        result = await chat_service_api.get_chat_participants(str(uuid4()))

        assert len(result) == 2

    def test_get_chat_service_api(self):
        service = get_chat_service_api()
        assert isinstance(service, ChatServiceAPI)
