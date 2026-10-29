import json
import asyncio
from typing import Callable, Awaitable, Optional
from datetime import datetime, timezone

from src.core.logger import get_logger
from src.general.repository.redis.redis_query import RedisQuery

from ..repositories.calls_state_repository import (
    get_calls_state_repository,
    CallsStateRepository,
)
from ..clients.push_client_api import get_push_client_api, PushClientAPI
from ...models.entities.call_state_entity import (
    CallStateEntity,
    CallStatus,
    CallType,
    CallStateFields,
)
from .call_notificator import CallNotificator, get_call_notificator

logger = get_logger(__name__)

WsSend = Callable[[str], Awaitable[None]]
WsReceive = Callable[[], Awaitable[str]]


class CallsStateService:
    def __init__(
        self,
        calls_state_repository: Optional[CallsStateRepository] = None,
        push_client_api: Optional[PushClientAPI] = None,
        call_notificator: Optional[CallNotificator] = None,
    ):
        self.calls_state_repository = (
            calls_state_repository or get_calls_state_repository()
        )
        self.push_client_api = push_client_api or get_push_client_api()
        self.call_notificator = call_notificator or get_call_notificator()
        self.CALL_TIMEOUT = 30

    def _entity_to_dict(self, entity: CallStateEntity) -> dict:
        return {
            "user_uuid": entity.user_uuid,
            "room_id": entity.room_id,
            "status": entity.status.value,
            "caller_uuid": entity.caller_uuid,
            "participants": entity.participants,
        }

    def _create_call_entity(
        self, caller: str, callee: str, sdp: str, room_uuid: str
    ) -> CallStateEntity:
        return CallStateEntity(
            user_uuid=caller,
            caller_uuid=caller,
            callee_uuid=callee,
            sdp_offer=sdp,
            status=CallStatus.WAITING,
            call_type=CallType.ROOM if room_uuid else CallType.P2P,
            room_uuid=room_uuid,
            participants=[caller] if room_uuid else [],
        )

    async def _update_call_status(self, entity: CallStateEntity, result: str) -> None:
        status_map = {
            "answered": CallStatus.ACTIVE,
            "rejected": CallStatus.REJECTED,
            "timeout": CallStatus.TIMEOUT,
        }
        entity.status = status_map.get(result, CallStatus.TIMEOUT)
        entity.updated_at = datetime.now(timezone.utc)
        await self.calls_state_repository.save(entity)

    async def _send_pending_calls(self, user_uuid: str, ws_send: WsSend) -> None:
        query = RedisQuery[CallStateFields]()
        query.add_filter(CallStateFields.CALLEE_UUID, user_uuid)
        query.add_filter(CallStateFields.STATUS, CallStatus.WAITING.value)
        query.set_pagination(limit=10)

        entities = await self.calls_state_repository.get_all(query)
        if entities:
            await ws_send(
                json.dumps(
                    {
                        "type": "pending_calls",
                        "calls": [self._entity_to_dict(e) for e in entities],
                    }
                )
            )

    async def _receive_json(self, ws_receive: WsReceive) -> dict:
        raw = await ws_receive()
        return json.loads(raw)

    async def _handle_command(
        self, user_uuid: str, data: dict, ws_send: WsSend
    ) -> None:
        msg_type = data.get("type")

        handlers = {
            "accept_call": self._handle_accept,
            "reject_call": self._handle_reject,
            "ice_candidate": self._handle_ice,
            "hangup": self._handle_hangup,
            "ping": lambda *_: ws_send(json.dumps({"type": "pong"})),
        }

        handler = handlers.get(msg_type)
        if handler:
            await handler(user_uuid, data, ws_send)

    async def _handle_accept(
        self, user_uuid: str, data: dict, ws_send: WsSend
    ) -> None:
        caller_uuid = data.get("caller_uuid")
        sdp_answer = data.get("sdp_answer")

        if caller_uuid and sdp_answer:
            await self.call_notificator.notify_call_answer(
                caller_uuid=caller_uuid,
                callee_uuid=user_uuid,
                sdp_answer=sdp_answer,
            )

            entity = await self.calls_state_repository.get_by_id(caller_uuid)
            if entity:
                entity.status = CallStatus.ACTIVE
                entity.sdp_answer = sdp_answer
                entity.updated_at = datetime.now(timezone.utc)
                await self.calls_state_repository.save(entity)

                if entity.room_id:
                    await self._add_participant(entity.room_id, user_uuid)

            await ws_send(json.dumps({"type": "call_accepted"}))

    async def _handle_reject(
        self, user_uuid: str, data: dict, ws_send: WsSend
    ) -> None:
        caller_uuid = data.get("caller_uuid")
        if caller_uuid:
            await self.call_notificator.notify_call_rejected(
                caller_uuid=caller_uuid,
                callee_uuid=user_uuid,
            )
            await self.calls_state_repository.delete_by_id(caller_uuid)
            await ws_send(json.dumps({"type": "call_rejected"}))

    async def _handle_ice(self, user_uuid: str, data: dict, ws_send: WsSend) -> None:
        target_uuid = data.get("target_uuid")
        candidate = data.get("candidate")
        if target_uuid and candidate:
            await self.call_notificator.notify_ice_candidate(
                target_uuid=target_uuid,
                candidate=candidate,
            )

    async def _handle_hangup(
        self, user_uuid: str, data: dict, ws_send: WsSend
    ) -> None:
        target_uuid = data.get("target_uuid")
        if target_uuid:
            await self.call_notificator.notify_call_ended(
                target_uuid=target_uuid,
                user_uuid=user_uuid,
            )
            await self.calls_state_repository.delete_by_id(user_uuid)
            await ws_send(json.dumps({"type": "call_ended"}))

    async def _add_participant(self, room_id: str, participant_uuid: str) -> None:
        query = RedisQuery[CallStateFields]()
        query.add_filter(CallStateFields.ROOM_ID, room_id)
        query.add_filter(CallStateFields.CALL_TYPE, CallType.ROOM.value)

        entities = await self.calls_state_repository.get_all(query)
        for entity in entities:
            if (
                entity.call_type == CallType.ROOM
                and participant_uuid not in entity.participants
            ):
                entity.participants.append(participant_uuid)
                entity.updated_at = datetime.now(timezone.utc)
                await self.calls_state_repository.save(entity)

                for p in entity.participants:
                    if p != participant_uuid:
                        await self.call_notificator.notify_participant_joined(
                            participant_uuid=p,
                            joined_uuid=participant_uuid,
                            room_id=room_id,
                        )
                break

    async def handle_call_session(
        self,
        user_uuid: str,
        room_uuid: str | None,
        ws_send: WsSend,
        ws_receive: WsReceive,
    ) -> None:
        stop_event = asyncio.Event()
        listen_task = asyncio.create_task(
            self.call_notificator.listen_events(
                user_uuid=user_uuid,
                ws_send=ws_send,
                stop_event=stop_event,
            )
        )
        outgoing_call_task: Optional[asyncio.Task] = None

        try:
            await self._send_pending_calls(user_uuid, ws_send)

            if room_uuid:
                async def _run_call():
                    try:
                        data = await self._receive_json(ws_receive)
                        if data.get("type") != "call_offer":
                            return await ws_send(
                                json.dumps({"error": "Expected call_offer"})
                            )

                        callee_uuid = data.get("callee_uuid")
                        sdp_offer = data.get("sdp_offer")
                        caller_name = data.get("caller_name")
                        if not callee_uuid or not sdp_offer:
                            return await ws_send(
                                json.dumps({"error": "Missing callee_uuid or sdp_offer"})
                            )

                        entity = self._create_call_entity(
                            user_uuid, callee_uuid, sdp_offer, room_uuid
                        )
                        await self.calls_state_repository.save(entity)

                        await self.call_notificator.notify_incoming_call(
                            callee_uuid=callee_uuid,
                            caller_uuid=user_uuid,
                            sdp_offer=sdp_offer,
                            room_uuid=room_uuid,
                        )
                        await self.push_client_api.send_call_push(
                            phone_number=callee_uuid,
                            caller_uuid=user_uuid,
                            caller_name=caller_name,
                            room_uuid=room_uuid,
                        )

                        result = await self.call_notificator.wait_for_answer(
                            user_uuid=user_uuid,
                            ws_send=ws_send,
                            timeout=self.CALL_TIMEOUT,
                        )
                        await self._update_call_status(entity, result)
                    except Exception as ce:
                        logger.error(f"Outgoing call error: {ce}")
                        await ws_send(json.dumps({"error": str(ce)}))

                outgoing_call_task = asyncio.create_task(_run_call())
                await asyncio.sleep(0.01)

            while True:
                data = await self._receive_json(ws_receive)
                await self._handle_command(user_uuid, data, ws_send)

        except Exception as e:
            logger.error(f"Session error: {e}")
            try:
                await ws_send(json.dumps({"error": str(e)}))
            except Exception:
                pass
        finally:
            stop_event.set()
            if outgoing_call_task and not outgoing_call_task.done():
                outgoing_call_task.cancel()
            listen_task.cancel()
            try:
                await listen_task
            except (asyncio.CancelledError, Exception):
                pass


_calls_state_service: Optional[CallsStateService] = None


def get_calls_state_service() -> CallsStateService:
    global _calls_state_service
    if _calls_state_service is None:
        _calls_state_service = CallsStateService()
    return _calls_state_service
