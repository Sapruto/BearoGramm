import pytest
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import ValidationError

from src.modules.calls.models.entities.call_state_entity import (
    CallStateEntity,
    CallStatus,
    CallType,
    CallStateFields,
)


@pytest.mark.unit
class TestCallStateEntity:
    def test_call_state_entity_creation(self, sample_user_uuid, sample_callee_uuid):
        now = datetime.now(timezone.utc)
        entity = CallStateEntity(
            user_uuid=sample_user_uuid,
            caller_uuid=sample_user_uuid,
            callee_uuid=sample_callee_uuid,
            status=CallStatus.WAITING,
            call_type=CallType.P2P,
            sdp_offer="test_offer",
            created_at=now,
            updated_at=now,
        )

        assert entity.user_uuid == sample_user_uuid
        assert entity.caller_uuid == sample_user_uuid
        assert entity.callee_uuid == sample_callee_uuid
        assert entity.status == CallStatus.WAITING
        assert entity.call_type == CallType.P2P
        assert entity.sdp_offer == "test_offer"
        assert entity.sdp_answer is None
        assert entity.participants == []
        assert entity.created_at == now
        assert entity.updated_at == now

    def test_call_state_entity_defaults(self, sample_user_uuid):
        entity = CallStateEntity(user_uuid=sample_user_uuid)

        assert entity.status == CallStatus.WAITING
        assert entity.call_type == CallType.P2P
        assert entity.created_at is not None
        assert entity.updated_at is not None
        assert entity.participants == []

    def test_call_state_entity_ttl_waiting(self, sample_user_uuid):
        entity = CallStateEntity(user_uuid=sample_user_uuid, status=CallStatus.WAITING)
        assert entity.ttl == 30

    def test_call_state_entity_ttl_active(self, sample_user_uuid):
        entity = CallStateEntity(user_uuid=sample_user_uuid, status=CallStatus.ACTIVE)
        assert entity.ttl == 3600

    def test_call_state_entity_ttl_rejected(self, sample_user_uuid):
        entity = CallStateEntity(user_uuid=sample_user_uuid, status=CallStatus.REJECTED)
        assert entity.ttl == 300

    def test_call_state_entity_ttl_ended(self, sample_user_uuid):
        entity = CallStateEntity(user_uuid=sample_user_uuid, status=CallStatus.ENDED)
        assert entity.ttl == 86400

    def test_call_state_entity_ttl_timeout(self, sample_user_uuid):
        entity = CallStateEntity(user_uuid=sample_user_uuid, status=CallStatus.TIMEOUT)
        assert entity.ttl == 60

    def test_call_state_entity_ttl_room_active(self, sample_user_uuid, sample_room_id):
        entity = CallStateEntity(
            user_uuid=sample_user_uuid,
            room_id=sample_room_id,
            call_type=CallType.ROOM,
            status=CallStatus.ACTIVE,
        )
        assert entity.ttl == 7200

    def test_call_state_entity_ttl_room_active_without_room_id(self, sample_user_uuid):
        entity = CallStateEntity(
            user_uuid=sample_user_uuid,
            call_type=CallType.ROOM,
            status=CallStatus.ACTIVE,
        )
        assert entity.ttl == 7200

    def test_call_state_entity_update_ttl(self, sample_user_uuid):
        entity = CallStateEntity(user_uuid=sample_user_uuid)
        result = entity.update_ttl(100)
        assert result == entity

    def test_call_status_values(self):
        assert CallStatus.WAITING == "waiting"
        assert CallStatus.ACTIVE == "active"
        assert CallStatus.REJECTED == "rejected"
        assert CallStatus.ENDED == "ended"
        assert CallStatus.TIMEOUT == "timeout"

    def test_call_type_values(self):
        assert CallType.P2P == "p2p"
        assert CallType.ROOM == "room"

    def test_call_state_fields_enum(self):
        assert CallStateFields.USER_UUID == "user_uuid"
        assert CallStateFields.ROOM_ID == "room_id"
        assert CallStateFields.STATUS == "status"
        assert CallStateFields.PARTICIPANTS == "participants"
        assert CallStateFields.CALLER_UUID == "caller_uuid"
        assert CallStateFields.CALLEE_UUID == "callee_uuid"
        assert CallStateFields.CREATED_AT == "created_at"
        assert CallStateFields.UPDATED_AT == "updated_at"
        assert CallStateFields.CALL_TYPE == "call_type"

    def test_call_state_fields_str(self):
        field = CallStateFields.STATUS
        assert str(field) == "status"
