from typing import Optional
from enum import Enum

from src.modules.event_notification import (
    EventNotificationService,
    get_notification_event_service,
)

from ...models.entities.call_state_entity import CallStateEntity


class CallEventType(str, Enum):
    INCOMING = "incoming_call"
    ANSWER = "call_answer"
    ACCEPTED = "call_accepted"
    REJECTED = "call_rejected"
    ENDED = "call_ended"
    ICE_CANDIDATE = "ice_candidate"
    PARTICIPANT_JOINED = "participant_joined"

    def __str__(self):
        return self.value


class CallNotificator:
    def __init__(
        self,
        notification_service: Optional[EventNotificationService] = None,
    ):
        self._notification_service = (
            notification_service or get_notification_event_service()
        )

    async def notify_incoming_call(
        self,
        callee_uuid: str,
        caller_uuid: str,
        sdp_offer: str,
        room_uuid: Optional[str],
    ) -> None:
        await self._notification_service.notify_user(
            user_uuid=callee_uuid,
            notification={
                "type": CallEventType.INCOMING.value,
                "caller_uuid": caller_uuid,
                "sdp_offer": sdp_offer,
                "room_uuid": room_uuid,
            },
        )

    async def notify_call_answer(
        self,
        caller_uuid: str,
        callee_uuid: str,
        sdp_answer: str,
    ) -> None:
        await self._notification_service.notify_user(
            user_uuid=caller_uuid,
            notification={
                "type": CallEventType.ANSWER.value,
                "sdp_answer": sdp_answer,
                "callee_uuid": callee_uuid,
            },
        )

    async def notify_call_rejected(
        self,
        caller_uuid: str,
        callee_uuid: str,
    ) -> None:
        await self._notification_service.notify_user(
            user_uuid=caller_uuid,
            notification={
                "type": CallEventType.REJECTED.value,
                "callee_uuid": callee_uuid,
            },
        )

    async def notify_call_ended(
        self,
        target_uuid: str,
        user_uuid: str,
    ) -> None:
        await self._notification_service.notify_user(
            user_uuid=target_uuid,
            notification={
                "type": CallEventType.ENDED.value,
                "user_uuid": user_uuid,
            },
        )

    async def notify_ice_candidate(
        self,
        target_uuid: str,
        candidate: dict,
    ) -> None:
        await self._notification_service.notify_user(
            user_uuid=target_uuid,
            notification={
                "type": CallEventType.ICE_CANDIDATE.value,
                "candidate": candidate,
            },
        )

    async def notify_participant_joined(
        self,
        participant_uuid: str,
        joined_uuid: str,
        room_id: str,
    ) -> None:
        await self._notification_service.notify_user(
            user_uuid=participant_uuid,
            notification={
                "type": CallEventType.PARTICIPANT_JOINED.value,
                "user_uuid": joined_uuid,
                "room_id": room_id,
            },
        )

    async def notify_about_call_event(
        self,
        entity: CallStateEntity,
        event_type: CallEventType,
    ) -> None:
        recipients = [entity.caller_uuid]
        if entity.callee_uuid:
            recipients.append(entity.callee_uuid)
        recipients.extend(p for p in entity.participants if p not in recipients)

        await self._notification_service.notify_users(
            user_uuids=recipients,
            notification={
                "type": event_type.value,
                "data": entity.model_dump(mode="json"),
            },
        )


def get_call_notificator() -> CallNotificator:
    return CallNotificator()
