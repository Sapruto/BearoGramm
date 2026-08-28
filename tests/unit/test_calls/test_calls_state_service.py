import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from uuid import uuid4
import asyncio

from src.modules.calls.core.services.calls_state_service import CallsStateService
from src.modules.calls.models.entities.call_state_entity import CallStateEntity, CallStatus, CallType
from src.general.repository.redis.redis_query import RedisQuery


@pytest.mark.unit
class TestCallsStateService:
    @pytest.mark.asyncio
    async def test_parse_redis_message_bytes(self, calls_state_service):
        data = b'{"type": "test", "data": "value"}'
        result = calls_state_service._parse_redis_message(data)
        assert result == {"type": "test", "data": "value"}

    @pytest.mark.asyncio
    async def test_parse_redis_message_str(self, calls_state_service):
        data = '{"type": "test", "data": "value"}'
        result = calls_state_service._parse_redis_message(data)
        assert result == {"type": "test", "data": "value"}

    @pytest.mark.asyncio
    async def test_entity_to_dict(self, calls_state_service, sample_call_state_entity):
        result = calls_state_service._entity_to_dict(sample_call_state_entity)

        assert result["user_uuid"] == sample_call_state_entity.user_uuid
        assert result["room_id"] == sample_call_state_entity.room_id
        assert result["status"] == "waiting"
        assert result["caller_uuid"] == sample_call_state_entity.caller_uuid
        assert result["participants"] == sample_call_state_entity.participants

    @pytest.mark.asyncio
    async def test_create_call_entity_p2p(self, calls_state_service):
        caller = str(uuid4())
        callee = str(uuid4())
        sdp = "test_sdp"

        entity = calls_state_service._create_call_entity(caller, callee, sdp, None)

        assert entity.user_uuid == caller
        assert entity.caller_uuid == caller
        assert entity.callee_uuid == callee
        assert entity.sdp_offer == sdp
        assert entity.status == CallStatus.WAITING
        assert entity.call_type == CallType.P2P
        assert entity.room_id is None

    @pytest.mark.asyncio
    async def test_create_call_entity_room(self, calls_state_service):
        caller = str(uuid4())
        callee = str(uuid4())
        sdp = "test_sdp"
        room_id = str(uuid4())

        entity = calls_state_service._create_call_entity(caller, callee, sdp, room_id)

        assert entity.call_type == CallType.ROOM
        assert entity.room_id == room_id
        assert entity.participants == [caller]

    @pytest.mark.asyncio
    async def test_update_call_status(self, calls_state_service, sample_call_state_entity):
        calls_state_service.calls_state_repository.save = AsyncMock()

        await calls_state_service._update_call_status(sample_call_state_entity, "answered")

        assert sample_call_state_entity.status == CallStatus.ACTIVE
        calls_state_service.calls_state_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_call_status_rejected(self, calls_state_service, sample_call_state_entity):
        calls_state_service.calls_state_repository.save = AsyncMock()

        await calls_state_service._update_call_status(sample_call_state_entity, "rejected")

        assert sample_call_state_entity.status == CallStatus.REJECTED

    @pytest.mark.asyncio
    async def test_update_call_status_timeout(self, calls_state_service, sample_call_state_entity):
        calls_state_service.calls_state_repository.save = AsyncMock()

        await calls_state_service._update_call_status(sample_call_state_entity, "timeout")

        assert sample_call_state_entity.status == CallStatus.TIMEOUT

    @pytest.mark.asyncio
    async def test_update_call_status_unknown(self, calls_state_service, sample_call_state_entity):
        calls_state_service.calls_state_repository.save = AsyncMock()

        await calls_state_service._update_call_status(sample_call_state_entity, "unknown")

        assert sample_call_state_entity.status == CallStatus.TIMEOUT

    @pytest.mark.asyncio
    async def test_send_pending_calls(self, calls_state_service):
        mock_ws_send = AsyncMock()
        calls_state_service.calls_state_repository.get_all = AsyncMock(return_value=[])

        await calls_state_service._send_pending_calls(str(uuid4()), mock_ws_send)

        mock_ws_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_pending_calls_with_entities(self, calls_state_service, sample_call_state_entity):
        mock_ws_send = AsyncMock()
        calls_state_service.calls_state_repository.get_all = AsyncMock(return_value=[sample_call_state_entity])

        await calls_state_service._send_pending_calls(str(uuid4()), mock_ws_send)

        mock_ws_send.assert_called_once()
        call_args = mock_ws_send.call_args[0][0]
        data = json.loads(call_args)
        assert data["type"] == "pending_calls"
        assert len(data["calls"]) == 1

    @pytest.mark.asyncio
    async def test_handle_accept(self, calls_state_service):
        user_uuid = str(uuid4())
        caller_uuid = str(uuid4())
        data = {
            "caller_uuid": caller_uuid,
            "sdp_answer": "test_answer"
        }
        mock_ws_send = AsyncMock()

        calls_state_service.calls_state_repository.notify_user = AsyncMock()
        calls_state_service.calls_state_repository.get_by_id = AsyncMock(return_value=None)
        calls_state_service.calls_state_repository.save = AsyncMock()

        await calls_state_service._handle_accept(user_uuid, data, mock_ws_send)

        calls_state_service.calls_state_repository.notify_user.assert_called_once()
        mock_ws_send.assert_called_with(json.dumps({"type": "call_accepted"}))

    @pytest.mark.asyncio
    async def test_handle_accept_with_room(self, calls_state_service, sample_room_call_entity):
        user_uuid = str(uuid4())
        caller_uuid = str(uuid4())
        room_id = str(uuid4())
        data = {
            "caller_uuid": caller_uuid,
            "sdp_answer": "test_answer"
        }
        mock_ws_send = AsyncMock()

        calls_state_service.calls_state_repository.notify_user = AsyncMock()
        calls_state_service.calls_state_repository.get_by_id = AsyncMock(return_value=sample_room_call_entity)
        calls_state_service.calls_state_repository.save = AsyncMock()
        calls_state_service._add_participant = AsyncMock()

        await calls_state_service._handle_accept(user_uuid, data, mock_ws_send)

        calls_state_service._add_participant.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_reject(self, calls_state_service):
        user_uuid = str(uuid4())
        caller_uuid = str(uuid4())
        data = {"caller_uuid": caller_uuid}
        mock_ws_send = AsyncMock()

        calls_state_service.calls_state_repository.notify_user = AsyncMock()
        calls_state_service.calls_state_repository.delete_by_id = AsyncMock(return_value=True)

        await calls_state_service._handle_reject(user_uuid, data, mock_ws_send)

        calls_state_service.calls_state_repository.notify_user.assert_called_once()
        calls_state_service.calls_state_repository.delete_by_id.assert_called_once_with(caller_uuid)
        mock_ws_send.assert_called_with(json.dumps({"type": "call_rejected"}))

    @pytest.mark.asyncio
    async def test_handle_reject_no_caller(self, calls_state_service):
        user_uuid = str(uuid4())
        data = {}
        mock_ws_send = AsyncMock()

        await calls_state_service._handle_reject(user_uuid, data, mock_ws_send)

        calls_state_service.calls_state_repository.notify_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_ice(self, calls_state_service):
        user_uuid = str(uuid4())
        target_uuid = str(uuid4())
        data = {
            "target_uuid": target_uuid,
            "candidate": "test_candidate"
        }
        mock_ws_send = AsyncMock()

        calls_state_service.calls_state_repository.notify_user = AsyncMock()

        await calls_state_service._handle_ice(user_uuid, data, mock_ws_send)

        calls_state_service.calls_state_repository.notify_user.assert_called_once_with(
            target_uuid,
            {"type": "ice_candidate", "candidate": "test_candidate"}
        )

    @pytest.mark.asyncio
    async def test_handle_ice_no_target(self, calls_state_service):
        user_uuid = str(uuid4())
        data = {"candidate": "test_candidate"}
        mock_ws_send = AsyncMock()

        calls_state_service.calls_state_repository.notify_user = AsyncMock()

        await calls_state_service._handle_ice(user_uuid, data, mock_ws_send)

        calls_state_service.calls_state_repository.notify_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_hangup(self, calls_state_service):
        user_uuid = str(uuid4())
        target_uuid = str(uuid4())
        data = {"target_uuid": target_uuid}
        mock_ws_send = AsyncMock()

        calls_state_service.calls_state_repository.notify_user = AsyncMock()
        calls_state_service.calls_state_repository.delete_by_id = AsyncMock(return_value=True)

        await calls_state_service._handle_hangup(user_uuid, data, mock_ws_send)

        calls_state_service.calls_state_repository.notify_user.assert_called_once()
        calls_state_service.calls_state_repository.delete_by_id.assert_called_once_with(user_uuid)

    @pytest.mark.asyncio
    async def test_add_participant(self, calls_state_service, sample_room_call_entity):
        room_id = str(uuid4())
        participant_uuid = str(uuid4())

        calls_state_service.calls_state_repository.get_all = AsyncMock(return_value=[sample_room_call_entity])
        calls_state_service.calls_state_repository.save = AsyncMock()
        calls_state_service.calls_state_repository.notify_user = AsyncMock()

        await calls_state_service._add_participant(room_id, participant_uuid)

        assert participant_uuid in sample_room_call_entity.participants
        calls_state_service.calls_state_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_participant_no_room(self, calls_state_service):
        room_id = str(uuid4())
        participant_uuid = str(uuid4())

        calls_state_service.calls_state_repository.get_all = AsyncMock(return_value=[])

        await calls_state_service._add_participant(room_id, participant_uuid)

        calls_state_service.calls_state_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_command(self, calls_state_service):
        user_uuid = str(uuid4())
        mock_ws_send = AsyncMock()

        calls_state_service._handle_accept = AsyncMock()
        calls_state_service._handle_reject = AsyncMock()
        calls_state_service._handle_ice = AsyncMock()
        calls_state_service._handle_hangup = AsyncMock()

        await calls_state_service._handle_command(user_uuid, {"type": "accept_call"}, mock_ws_send)
        calls_state_service._handle_accept.assert_called_once()

        await calls_state_service._handle_command(user_uuid, {"type": "reject_call"}, mock_ws_send)
        calls_state_service._handle_reject.assert_called_once()

        await calls_state_service._handle_command(user_uuid, {"type": "ice_candidate"}, mock_ws_send)
        calls_state_service._handle_ice.assert_called_once()

        await calls_state_service._handle_command(user_uuid, {"type": "hangup"}, mock_ws_send)
        calls_state_service._handle_hangup.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_command_ping(self, calls_state_service):
        user_uuid = str(uuid4())
        mock_ws_send = AsyncMock()

        await calls_state_service._handle_command(user_uuid, {"type": "ping"}, mock_ws_send)

        mock_ws_send.assert_called_with(json.dumps({"type": "pong"}))

    @pytest.mark.asyncio
    async def test_handle_command_unknown(self, calls_state_service):
        user_uuid = str(uuid4())
        mock_ws_send = AsyncMock()

        await calls_state_service._handle_command(user_uuid, {"type": "unknown"}, mock_ws_send)

        mock_ws_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_receive_json(self, calls_state_service):
        mock_ws_receive = AsyncMock(return_value='{"type": "test"}')

        result = await calls_state_service._receive_json(mock_ws_receive)

        assert result == {"type": "test"}

    @pytest.mark.asyncio
    async def test_call_success(self, calls_state_service):
        user_uuid = str(uuid4())
        callee_uuid = str(uuid4())
        mock_ws_send = AsyncMock()
        mock_ws_receive = AsyncMock()
        mock_ws_receive.return_value = json.dumps({
            "type": "call_offer",
            "callee_uuid": callee_uuid,
            "sdp_offer": "test_offer"
        })

        calls_state_service.calls_state_repository.save = AsyncMock()
        calls_state_service.calls_state_repository.notify_user = AsyncMock()
        calls_state_service.push_client_api.send_call_push = AsyncMock(return_value=True)
        calls_state_service._wait_for_answer = AsyncMock(return_value="answered")
        calls_state_service._update_call_status = AsyncMock()

        await calls_state_service.call(user_uuid, mock_ws_send, mock_ws_receive)

        calls_state_service.calls_state_repository.save.assert_called_once()
        calls_state_service.calls_state_repository.notify_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_missing_callee(self, calls_state_service):
        user_uuid = str(uuid4())
        mock_ws_send = AsyncMock()
        mock_ws_receive = AsyncMock()
        mock_ws_receive.return_value = json.dumps({
            "type": "call_offer",
            "sdp_offer": "test_offer"
        })

        await calls_state_service.call(user_uuid, mock_ws_send, mock_ws_receive)

        mock_ws_send.assert_called_with(json.dumps({"error": "Missing callee_uuid or sdp_offer"}))

    @pytest.mark.asyncio
    async def test_call_wrong_type(self, calls_state_service):
        user_uuid = str(uuid4())
        mock_ws_send = AsyncMock()
        mock_ws_receive = AsyncMock()
        mock_ws_receive.return_value = json.dumps({"type": "wrong_type"})

        await calls_state_service.call(user_uuid, mock_ws_send, mock_ws_receive)

        mock_ws_send.assert_called_with(json.dumps({"error": "Expected call_offer"}))

    @pytest.mark.asyncio
    async def test_call_timeout(self, calls_state_service):
        user_uuid = str(uuid4())
        callee_uuid = str(uuid4())
        mock_ws_send = AsyncMock()
        mock_ws_receive = AsyncMock()
        mock_ws_receive.return_value = json.dumps({
            "type": "call_offer",
            "callee_uuid": callee_uuid,
            "sdp_offer": "test_offer"
        })

        calls_state_service.calls_state_repository.save = AsyncMock()
        calls_state_service.calls_state_repository.notify_user = AsyncMock()
        calls_state_service.push_client_api.send_call_push = AsyncMock(return_value=True)
        calls_state_service._wait_for_answer = AsyncMock(side_effect=asyncio.TimeoutError())
        calls_state_service._update_call_status = AsyncMock()

        await calls_state_service.call(user_uuid, mock_ws_send, mock_ws_receive)

        calls_state_service._update_call_status.assert_called_once()
        args = calls_state_service._update_call_status.call_args[0]
        assert args[1] == "timeout"

    @pytest.mark.asyncio
    async def test_call_exception(self, calls_state_service):
        user_uuid = str(uuid4())
        mock_ws_send = AsyncMock()
        mock_ws_receive = AsyncMock()
        mock_ws_receive.side_effect = Exception("Test error")

        await calls_state_service.call(user_uuid, mock_ws_send, mock_ws_receive)

        mock_ws_send.assert_called_with(json.dumps({"error": "Test error"}))

    def test_get_calls_state_service(self):
        from src.modules.calls.core.services.calls_state_service import get_calls_state_service
        service = get_calls_state_service()
        assert isinstance(service, CallsStateService)
