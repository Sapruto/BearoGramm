import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.modules.messages.core.services.message_service import MessageService
from src.modules.messages.models.dto.requests import (
    SendMessageRequest,
    UpdateMessageRequest,
    DeleteMessageRequest,
    GetMessagesRequest,
)
from src.modules.messages.models.entities.message_entity import MessageEntity
from src.modules.messages.types.text.text_message_data import TextMessageData
from src.general.repository.sql.sql_query import SqlQuery
from src.modules.chats import MessageActionType


@pytest.mark.unit
class TestMessageService:
    @pytest.mark.asyncio
    async def test_send_message_success(
        self,
        message_service,
        message_repository,
        data_processor,
        mock_websocket_service,
    ):
        chat_uuid = str(uuid4())
        user_uuid = str(uuid4())
        request = SendMessageRequest(
            chat_uuid=chat_uuid,
            user_uuid=user_uuid,
            typing_to_data=[("text_message_type", "Hello")],
        )

        processed_data = [TextMessageData(text="Hello", data_type="text_message_type")]
        data_processor.save_data = AsyncMock(
            return_value=MagicMock(success=True, processed_data=processed_data)
        )

        saved_entity = MessageEntity(
            chat_uuid=chat_uuid, user_uuid=user_uuid, message_data=processed_data
        )
        message_repository.save = AsyncMock(return_value=saved_entity)

        response = await message_service.send_message(request)

        assert response.success is True
        assert response.message_entity is not None
        assert response.error_message is None
        mock_websocket_service.notify_chat_participants.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_chat_check_failed(self, message_service):
        with patch.object(message_service, "_checks_in_chat_service") as mock_check:
            mock_check.return_value = False

            request = SendMessageRequest(
                chat_uuid=str(uuid4()),
                user_uuid=str(uuid4()),
                typing_to_data=[("text_message_type", "Hello")],
            )

            response = await message_service.send_message(request)

            assert response.success is False

    @pytest.mark.asyncio
    async def test_send_message_processing_failed(
        self, message_service, data_processor
    ):
        request = SendMessageRequest(
            chat_uuid=str(uuid4()),
            user_uuid=str(uuid4()),
            typing_to_data=[("text_message_type", "Hello")],
        )

        data_processor.save_data = AsyncMock(
            return_value=MagicMock(success=False, error_message="Processing failed")
        )

        response = await message_service.send_message(request)

        assert response.success is False
        assert "Processing failed" in response.error_message

    @pytest.mark.asyncio
    async def test_send_message_exception(self, message_service, data_processor):
        request = SendMessageRequest(
            chat_uuid=str(uuid4()),
            user_uuid=str(uuid4()),
            typing_to_data=[("text_message_type", "Hello")],
        )

        data_processor.save_data = AsyncMock(side_effect=Exception("DB error"))

        response = await message_service.send_message(request)

        assert response.success is False
        assert "DB error" in response.error_message

    @pytest.mark.asyncio
    async def test_update_message_success(
        self,
        message_service,
        message_repository,
        data_processor,
        mock_websocket_service,
    ):
        message_uuid = str(uuid4())
        user_uuid = str(uuid4())
        chat_uuid = str(uuid4())

        old_data = [TextMessageData(text="Old", data_type="text_message_type")]
        new_data = [TextMessageData(text="New", data_type="text_message_type")]

        existing_entity = MessageEntity(
            uuid=message_uuid,
            chat_uuid=chat_uuid,
            user_uuid=user_uuid,
            message_data=old_data,
        )

        message_repository.get = AsyncMock(return_value=existing_entity)
        data_processor.update_data = AsyncMock(
            return_value=MagicMock(success=True, processed_data=new_data)
        )
        message_repository.update = AsyncMock(return_value=existing_entity)

        request = UpdateMessageRequest(
            message_uuid=message_uuid,
            user_uuid=user_uuid,
            typing_to_data=[("text_message_type", "New")],
        )

        response = await message_service.update_message(request)

        assert response.success is True
        assert response.message_entity is not None
        mock_websocket_service.notify_chat_participants.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_message_not_found(self, message_service, message_repository):
        message_repository.get = AsyncMock(return_value=None)

        request = UpdateMessageRequest(
            message_uuid=str(uuid4()),
            user_uuid=str(uuid4()),
            typing_to_data=[("text_message_type", "New")],
        )

        response = await message_service.update_message(request)

        assert response.success is False
        assert response.error_message == "Message not found"

    @pytest.mark.asyncio
    async def test_update_message_not_owner(self, message_service, message_repository):
        existing_entity = MessageEntity(
            uuid=str(uuid4()),
            chat_uuid=str(uuid4()),
            user_uuid="other_user",
            message_data=[],
        )
        message_repository.get = AsyncMock(return_value=existing_entity)

        request = UpdateMessageRequest(
            message_uuid=str(uuid4()),
            user_uuid="current_user",
            typing_to_data=[("text_message_type", "New")],
        )

        response = await message_service.update_message(request)

        assert response.success is False
        assert response.error_message == "Message not belong to user"

    @pytest.mark.asyncio
    async def test_delete_message_success(
        self, message_service, message_repository, mock_websocket_service
    ):
        message_uuid = str(uuid4())
        user_uuid = str(uuid4())
        chat_uuid = str(uuid4())

        existing_entity = MessageEntity(
            uuid=message_uuid, chat_uuid=chat_uuid, user_uuid=user_uuid, message_data=[]
        )

        message_repository.get = AsyncMock(return_value=existing_entity)
        message_repository.delete = AsyncMock(return_value=1)

        request = DeleteMessageRequest(message_uuid=message_uuid, user_uuid=user_uuid)

        response = await message_service.delete_message(request)

        assert response.success is True
        assert response.error_message is None
        mock_websocket_service.notify_chat_participants.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_message_not_found(self, message_service, message_repository):
        message_repository.get = AsyncMock(return_value=None)

        request = DeleteMessageRequest(
            message_uuid=str(uuid4()), user_uuid=str(uuid4())
        )

        response = await message_service.delete_message(request)

        assert response.success is False
        assert response.error_message == "Message not found"

    @pytest.mark.asyncio
    async def test_delete_message_not_owner(self, message_service, message_repository):
        existing_entity = MessageEntity(
            uuid=str(uuid4()),
            chat_uuid=str(uuid4()),
            user_uuid="other_user",
            message_data=[],
        )
        message_repository.get = AsyncMock(return_value=existing_entity)

        request = DeleteMessageRequest(
            message_uuid=str(uuid4()), user_uuid="current_user"
        )

        response = await message_service.delete_message(request)

        assert response.success is False
        assert response.error_message == "Message not belong to user"

    @pytest.mark.asyncio
    async def test_get_messages_success(self, message_service, message_repository):
        chat_uuid = str(uuid4())
        user_uuid = str(uuid4())

        messages = [
            MessageEntity(chat_uuid=chat_uuid, user_uuid=user_uuid, message_data=[]),
            MessageEntity(chat_uuid=chat_uuid, user_uuid=user_uuid, message_data=[]),
        ]

        message_repository.get_all = AsyncMock(return_value=messages)

        request = GetMessagesRequest(
            chat_uuid=chat_uuid, user_uuid=user_uuid, limit=10, offset=0, show_new=True
        )

        response = await message_service.get_messages(request)

        assert response.success is True
        assert len(response.message_entity) == 2
        assert response.error_message is None

    @pytest.mark.asyncio
    async def test_get_messages_with_limit_exceeded(
        self, message_service, message_repository
    ):
        chat_uuid = str(uuid4())
        user_uuid = str(uuid4())

        message_repository.get_all = AsyncMock(return_value=[])

        request = GetMessagesRequest(
            chat_uuid=chat_uuid, user_uuid=user_uuid, limit=200, offset=0, show_new=True
        )

        response = await message_service.get_messages(request)

        assert response.success is True
        assert message_repository.get_all.called
        args = message_repository.get_all.call_args[0][0]
        assert args.limit == 100

    @pytest.mark.asyncio
    async def test_get_messages_exception(self, message_service, message_repository):
        message_repository.get_all = AsyncMock(side_effect=Exception("DB error"))

        request = GetMessagesRequest(
            chat_uuid=str(uuid4()), user_uuid=str(uuid4()), limit=10, offset=0
        )

        response = await message_service.get_messages(request)

        assert response.success is False
        assert "DB error" in response.error_message
