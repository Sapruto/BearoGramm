import pytest
import json
from datetime import datetime, timezone
from uuid import uuid4

from src.modules.calls.core.repositories.mappers.calls_state_mapper import CallsStateMapper
from src.modules.calls.models.entities.call_state_entity import CallStateEntity, CallStatus, CallType, CallStateFields


@pytest.mark.unit
class TestCallsStateMapper:
    def test_to_redis(self, calls_state_mapper, sample_call_state_entity):
        redis_data = calls_state_mapper.to_redis(sample_call_state_entity)

        assert redis_data["user_uuid"] == sample_call_state_entity.user_uuid
        assert redis_data["room_id"] == ""
        assert redis_data["status"] == "waiting"
        assert redis_data["participants"] == "[]"
        assert redis_data["sdp_offer"] == "test_offer"
        assert redis_data["sdp_answer"] == ""
        assert redis_data["caller_uuid"] == sample_call_state_entity.caller_uuid
        assert redis_data["callee_uuid"] == sample_call_state_entity.callee_uuid
        assert redis_data["call_type"] == "p2p"
        assert "created_at" in redis_data
        assert "updated_at" in redis_data

    def test_to_redis_with_room(self, calls_state_mapper, sample_room_call_entity):
        redis_data = calls_state_mapper.to_redis(sample_room_call_entity)

        assert redis_data["room_id"] == sample_room_call_entity.room_id
        assert redis_data["participants"] == json.dumps(sample_room_call_entity.participants)
        assert redis_data["call_type"] == "room"

    def test_to_entity(self, calls_state_mapper):
        user_uuid = str(uuid4())
        now = datetime.now(timezone.utc)

        redis_data = {
            "user_uuid": user_uuid,
            "room_id": "",
            "status": "waiting",
            "participants": "[]",
            "sdp_offer": "test_offer",
            "sdp_answer": "",
            "caller_uuid": user_uuid,
            "callee_uuid": str(uuid4()),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "call_type": "p2p"
        }

        entity = calls_state_mapper.to_entity(redis_data)

        assert entity.user_uuid == user_uuid
        assert entity.status == "waiting"
        assert entity.participants == []
        assert entity.call_type == CallType.P2P

    def test_to_entity_with_room(self, calls_state_mapper, sample_room_id):
        user_uuid = str(uuid4())
        now = datetime.now(timezone.utc)

        redis_data = {
            "user_uuid": user_uuid,
            "room_id": sample_room_id,
            "status": "active",
            "participants": json.dumps([user_uuid]),
            "sdp_offer": "",
            "sdp_answer": "",
            "caller_uuid": user_uuid,
            "callee_uuid": "",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "call_type": "room"
        }

        entity = calls_state_mapper.to_entity(redis_data)

        assert entity.room_id == sample_room_id
        assert entity.status == "active"
        assert entity.call_type == CallType.ROOM
        assert entity.participants == [user_uuid]

    def test_to_entity_invalid_date(self, calls_state_mapper):
        redis_data = {
            "user_uuid": str(uuid4()),
            "status": "waiting",
            "participants": "[]",
            "created_at": "invalid_date",
            "updated_at": "invalid_date",
            "call_type": "p2p"
        }

        entity = calls_state_mapper.to_entity(redis_data)

        assert entity.created_at is not None
        assert entity.updated_at is not None

    def test_to_entity_invalid_participants(self, calls_state_mapper):
        redis_data = {
            "user_uuid": str(uuid4()),
            "status": "waiting",
            "participants": "invalid_json",
            "call_type": "p2p"
        }

        entity = calls_state_mapper.to_entity(redis_data)

        assert entity.participants == []

    def test_to_entity_invalid_call_type(self, calls_state_mapper):
        redis_data = {
            "user_uuid": str(uuid4()),
            "status": "waiting",
            "participants": "[]",
            "call_type": "invalid"
        }

        entity = calls_state_mapper.to_entity(redis_data)

        assert entity.call_type == CallType.P2P

    def test_to_redis_value_participants(self, calls_state_mapper):
        field, value = calls_state_mapper.to_redis_value(
            CallStateFields.PARTICIPANTS,
            ["user1", "user2"]
        )
        assert field == "participants"
        assert value == '["user1", "user2"]'

    def test_to_redis_value_datetime(self, calls_state_mapper):
        now = datetime.now(timezone.utc)
        field, value = calls_state_mapper.to_redis_value(
            CallStateFields.CREATED_AT,
            now
        )
        assert field == "created_at"
        assert value == now.isoformat()

    def test_to_redis_value_none(self, calls_state_mapper):
        field, value = calls_state_mapper.to_redis_value(
            CallStateFields.ROOM_ID,
            None
        )
        assert field == "room_id"
        assert value == ""

    def test_to_entity_value_participants(self, calls_state_mapper):
        field, value = calls_state_mapper.to_entity_value(
            "participants",
            '["user1", "user2"]'
        )
        assert field == CallStateFields.PARTICIPANTS
        assert value == ["user1", "user2"]

    def test_to_entity_value_participants_invalid(self, calls_state_mapper):
        field, value = calls_state_mapper.to_entity_value(
            "participants",
            "invalid"
        )
        assert field == CallStateFields.PARTICIPANTS
        assert value == []

    def test_to_entity_value_datetime(self, calls_state_mapper):
        now = datetime.now(timezone.utc)
        field, value = calls_state_mapper.to_entity_value(
            "created_at",
            now.isoformat()
        )
        assert field == CallStateFields.CREATED_AT
        assert value == now

    def test_to_entity_value_empty(self, calls_state_mapper):
        field, value = calls_state_mapper.to_entity_value(
            "room_id",
            ""
        )
        assert field == CallStateFields.ROOM_ID
        assert value is None

    def test_to_redis_field(self, calls_state_mapper):
        assert calls_state_mapper.to_redis_field(CallStateFields.USER_UUID) == "user_uuid"
        assert calls_state_mapper.to_redis_field(CallStateFields.STATUS) == "status"

    def test_to_entity_field(self, calls_state_mapper):
        assert calls_state_mapper.to_entity_field("user_uuid") == CallStateFields.USER_UUID
        assert calls_state_mapper.to_entity_field("status") == CallStateFields.STATUS

    def test_get_id_field(self, calls_state_mapper):
        assert calls_state_mapper.get_id_field() == CallStateFields.USER_UUID

    def test_get_id_from_entity(self, calls_state_mapper, sample_call_state_entity):
        assert calls_state_mapper.get_id_from_entity(sample_call_state_entity) == sample_call_state_entity.user_uuid
