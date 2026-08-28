from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone
import json

from src.general.repository.redis.redis_base_mapper import BaseRedisMapper

from ....models.entities.call_state_entity import CallStateEntity, CallStateFields, CallType

class CallsStateMapper(BaseRedisMapper[CallStateEntity, CallStateFields]):
    key_prefix = "call:state"
    storage_type = "hash"

    field_mapping = {
        CallStateFields.USER_UUID: "user_uuid",
        CallStateFields.ROOM_ID: "room_id",
        CallStateFields.STATUS: "status",
        CallStateFields.PARTICIPANTS: "participants",
        CallStateFields.SDP_OFFER: "sdp_offer",
        CallStateFields.SDP_ANSWER: "sdp_answer",
        CallStateFields.CALLER_UUID: "caller_uuid",
        CallStateFields.CALLEE_UUID: "callee_uuid",
        CallStateFields.CREATED_AT: "created_at",
        CallStateFields.UPDATED_AT: "updated_at",
        CallStateFields.CALL_TYPE: "call_type"
    }

    def to_redis(self, entity: CallStateEntity) -> Dict[str, Any]:
        return {
            "user_uuid": entity.user_uuid,
            "room_id": entity.room_id or "",
            "status": entity.status.value if hasattr(entity.status, 'value') else entity.status,
            "participants": json.dumps(entity.participants),
            "sdp_offer": entity.sdp_offer or "",
            "sdp_answer": entity.sdp_answer or "",
            "caller_uuid": entity.caller_uuid or "",
            "callee_uuid": entity.callee_uuid or "",
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat(),
            "call_type": entity.call_type.value if hasattr(entity.call_type, 'value') else entity.call_type
        }

    def to_entity(self, data: Dict[str, Any]) -> CallStateEntity:
        participants = []
        if data.get("participants"):
            try:
                participants = json.loads(data["participants"])
            except (json.JSONDecodeError, TypeError):
                participants = []

        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)

        try:
            if data.get("created_at"):
                created_at = datetime.fromisoformat(data["created_at"])
            if data.get("updated_at"):
                updated_at = datetime.fromisoformat(data["updated_at"])
        except (ValueError, TypeError):
            pass

        call_type_raw = data.get("call_type", CallType.P2P.value)
        if isinstance(call_type_raw, str):
            try:
                call_type = CallType(call_type_raw)
            except ValueError:
                call_type = CallType.P2P
        else:
            call_type = call_type_raw or CallType.P2P

        return CallStateEntity(
            user_uuid=data.get("user_uuid", ""),
            room_id=data.get("room_id") or None,
            status=data.get("status", "waiting"),
            participants=participants,
            sdp_offer=data.get("sdp_offer") or None,
            sdp_answer=data.get("sdp_answer") or None,
            caller_uuid=data.get("caller_uuid") or None,
            callee_uuid=data.get("callee_uuid") or None,
            created_at=created_at,
            updated_at=updated_at,
            call_type=call_type,  # 👈
        )

    def to_redis_value(self, field: CallStateFields, value: Any) -> Tuple[str, Any]:
        redis_field = self.to_redis_field(field)

        if field == CallStateFields.PARTICIPANTS:
            return redis_field, json.dumps(value) if value else "[]"
        elif field in (CallStateFields.CREATED_AT, CallStateFields.UPDATED_AT):
            if isinstance(value, datetime):
                return redis_field, value.isoformat()
            return redis_field, str(value)
        elif value is None:
            return redis_field, ""

        return redis_field, self.serialize_value(value)

    def to_entity_value(self, redis_field: str, value: Any) -> Tuple[CallStateFields, Any]:
        field = self.to_entity_field(redis_field)

        if field == CallStateFields.PARTICIPANTS:
            try:
                return field, json.loads(value) if value else []
            except (json.JSONDecodeError, TypeError):
                return field, []
        elif field in (CallStateFields.CREATED_AT, CallStateFields.UPDATED_AT):
            try:
                return field, datetime.fromisoformat(value)
            except (ValueError, TypeError):
                return field, datetime.now(timezone.utc)
        elif value is None or value == "":
            return field, None

        return field, self.deserialize_value(value, str)

    def to_redis_field(self, field: CallStateFields) -> str:
        return self.field_mapping.get(field, field.value)

    def to_entity_field(self, redis_field: str) -> CallStateFields:
        return self.reverse_field_mapping.get(redis_field, CallStateFields(redis_field))

    def get_id_field(self) -> Optional[CallStateFields]:
        return CallStateFields.USER_UUID

    def get_id_from_entity(self, entity: CallStateEntity) -> Optional[Any]:
        return entity.user_uuid
