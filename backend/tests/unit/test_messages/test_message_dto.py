import pytest
from uuid import uuid4

from src.modules.messages.models.dto.requests import (
    SendMessageRequest,
    UpdateMessageRequest,
    DeleteMessageRequest,
    GetMessagesRequest,
)
from src.modules.messages.models.dto.responses import (
    SendMessageResponse,
    UpdateMessageResponse,
    DeleteMessageResponse,
    GetMessagesResponse,
)
from src.modules.messages.models.entities.message_entity import MessageEntity


@pytest.mark.unit
class TestMessageRequests:
    def test_send_message_request(self):
        request = SendMessageRequest(
            chat_uuid=str(uuid4()),
            user_uuid=str(uuid4()),
            typing_to_data=[("text_message_type", "Hello")],
        )
        assert request.chat_uuid is not None
        assert request.user_uuid is not None
        assert len(request.typing_to_data) == 1

    def test_update_message_request(self):
        request = UpdateMessageRequest(
            message_uuid=str(uuid4()),
            user_uuid=str(uuid4()),
            typing_to_data=[("text_message_type", "Updated")],
        )
        assert request.message_uuid is not None
        assert request.user_uuid is not None

    def test_delete_message_request(self):
        request = DeleteMessageRequest(
            message_uuid=str(uuid4()), user_uuid=str(uuid4())
        )
        assert request.message_uuid is not None
        assert request.user_uuid is not None

    def test_get_messages_request(self):
        request = GetMessagesRequest(
            chat_uuid=str(uuid4()),
            user_uuid=str(uuid4()),
            limit=20,
            offset=0,
            show_new=True,
        )
        assert request.chat_uuid is not None
        assert request.user_uuid is not None
        assert request.limit == 20
        assert request.offset == 0
        assert request.show_new is True

    def test_get_messages_request_defaults(self):
        request = GetMessagesRequest(chat_uuid=str(uuid4()), user_uuid=str(uuid4()))
        assert request.limit == 10
        assert request.offset == 0
        assert request.show_new is True


@pytest.mark.unit
class TestMessageResponses:
    def test_send_message_response_success(self, sample_message_entity):
        response = SendMessageResponse(
            success=True, message_entity=sample_message_entity
        )
        assert response.success is True
        assert response.message_entity is not None
        assert response.error_message is None

    def test_send_message_response_failure(self):
        response = SendMessageResponse(success=False, error_message="Failed to send")
        assert response.success is False
        assert response.message_entity is None
        assert response.error_message == "Failed to send"

    def test_update_message_response_success(self, sample_message_entity):
        response = UpdateMessageResponse(
            success=True, message_entity=sample_message_entity
        )
        assert response.success is True

    def test_delete_message_response_success(self):
        response = DeleteMessageResponse(success=True)
        assert response.success is True

    def test_get_messages_response_success(self, sample_message_entity):
        response = GetMessagesResponse(
            success=True, message_entity=[sample_message_entity]
        )
        assert response.success is True
        assert len(response.message_entity) == 1
