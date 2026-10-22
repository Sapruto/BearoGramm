from typing import List, Optional, Tuple, Callable

from src.general.repository.sql.sql_query import SqlQuery
from src.core.logger import get_logger
from src.modules.profiles_custom.core.services.profile_custom_service import get_profile_custom_service, \
    ProfileCustomService

from src.modules.user import (
    UserServiceAPI,
    get_user_service_api,
    UserNotFound,
)

from ..exceptions import (
    InvalidTargetIdentifier,
    CannotBeFriendWithSelf,
    FriendshipAlreadyExists,
    FriendRequestNotFound,
    FriendRequestAlreadyHandled,
    CannotAcceptOwnRequest,
    CannotRejectOwnRequest,
    CannotBlockYourself,
    UserAlreadyBlocked,
    NotFriends,
)
from ..repositories.friend_repository import FriendRepository, get_friend_repository
from ...models.enums import FriendStatus
from ...models.entities.friend_entity import FriendEntity, FriendFields
from ...models.dto.requests import (
    SendFriendRequest,
    FriendStatusRequest,
    TargetIdentifier,
)
from ...models.dto.responses import (
    FriendItemResponse,
    FriendRequestResponse,
    GetFriendsResponse,
    GetFriendRequestsResponse,
    FriendActionResponse,
)

logger = get_logger(__name__)


class FriendService:
    def __init__(
        self,
        friend_repository: Optional[FriendRepository] = None,
        user_service: Optional[UserServiceAPI] = None,
        profile_service: Optional[ProfileCustomService] = None,
        max_limit: Optional[int] = None,
    ):
        self._friend_repo = friend_repository or get_friend_repository()
        self._user_service = user_service or get_user_service_api()
        self._profile_service = profile_service or get_profile_custom_service()
        self._max_limit = max_limit or 100

    async def _get_pair(self, uuid_a: str, uuid_b: str) -> Optional[FriendEntity]:
        for first, second in ((uuid_a, uuid_b), (uuid_b, uuid_a)):
            query = (
                SqlQuery[FriendFields]()
                .add_filter(field=FriendFields.USER_UUID1, value=first)
                .add_filter(field=FriendFields.USER_UUID2, value=second)
            )
            found = await self._friend_repo.get(query)
            if found:
                return found
        return None

    async def _list_pairs_for_user(self, user_uuid: str) -> List[FriendEntity]:
        query_by_first = SqlQuery[FriendFields]().add_filter(
            field=FriendFields.USER_UUID1, value=user_uuid
        )
        query_by_second = SqlQuery[FriendFields]().add_filter(
            field=FriendFields.USER_UUID2, value=user_uuid
        )
        left = await self._friend_repo.get_all(query_by_first)
        right = await self._friend_repo.get_all(query_by_second)
        return left + right

    async def _resolve_target_uuid(self, request: SendFriendRequest) -> str:
        resolvers: dict[TargetIdentifier, Callable] = {
            TargetIdentifier.UUID: self._user_service.get_user_by_uuid,
            TargetIdentifier.PHONE: self._user_service.get_user_by_phone,
            TargetIdentifier.USERNAME: self._user_service.get_user_by_username,
            TargetIdentifier.EMAIL: self._user_service.get_user_by_email,
        }
        handler = resolvers.get(request.target_type)
        if handler is None:
            raise InvalidTargetIdentifier(request.target_value)

        user = await handler(request.target_value)
        if not user:
            raise UserNotFound(request.target_value)
        return user.uuid

    @staticmethod
    def _my_side(
            entity: FriendEntity, user_uuid: str
    ) -> Tuple[FriendStatus, str, FriendStatus]:
        if entity.user_uuid1 == user_uuid:
            return entity.user_status1, entity.user_uuid2, entity.user_status2
        return entity.user_status2, entity.user_uuid1, entity.user_status1

    @staticmethod
    def _set_my_status(
            entity: FriendEntity, user_uuid: str, status: FriendStatus
    ) -> None:
        if entity.user_uuid1 == user_uuid:
            entity.user_status1 = status
        else:
            entity.user_status2 = status

    def _validate_transition(
        self,
        entity: FriendEntity,
        current_user_uuid: str,
        new_status: FriendStatus,
    ) -> None:
        my_status, _, other_status = self._my_side(entity, current_user_uuid)

        match new_status:
            case FriendStatus.ACCEPT:
                if entity.initiator_uuid == current_user_uuid:
                    raise CannotAcceptOwnRequest()
                if my_status == FriendStatus.ACCEPT and other_status == FriendStatus.ACCEPT:
                    raise FriendRequestAlreadyHandled(FriendStatus.ACCEPT.value)

            case FriendStatus.REJECT:
                if entity.initiator_uuid == current_user_uuid:
                    raise CannotRejectOwnRequest()
                if my_status == FriendStatus.REJECT:
                    raise FriendRequestAlreadyHandled(FriendStatus.REJECT.value)

            case FriendStatus.BLOCKED:
                if my_status == FriendStatus.BLOCKED:
                    raise UserAlreadyBlocked(current_user_uuid, entity.user_uuid2)

            case FriendStatus.PROCESS:
                if not (my_status == FriendStatus.ACCEPT and other_status == FriendStatus.ACCEPT):
                    raise NotFriends(current_user_uuid, entity.user_uuid2)

    async def send_friend_request(
        self, from_user_uuid: str, request: SendFriendRequest
    ) -> FriendActionResponse:
        to_user_uuid = await self._resolve_target_uuid(request)

        if from_user_uuid == to_user_uuid:
            raise CannotBeFriendWithSelf()

        existing = await self._get_pair(from_user_uuid, to_user_uuid)
        if existing:
            my_status, _, other_status = self._my_side(existing, from_user_uuid)
            if my_status == FriendStatus.BLOCKED:
                raise UserAlreadyBlocked(from_user_uuid, to_user_uuid)
            if other_status == FriendStatus.BLOCKED:
                raise UserAlreadyBlocked(to_user_uuid, from_user_uuid)
            raise FriendshipAlreadyExists(from_user_uuid, to_user_uuid)

        entity = FriendEntity(
            user_uuid1=from_user_uuid,
            user_status1=FriendStatus.PROCESS,
            user_uuid2=to_user_uuid,
            user_status2=FriendStatus.PROCESS,
            initiator_uuid=from_user_uuid,
        )
        saved = await self._friend_repo.save(entity)
        if not saved:
            raise FriendshipAlreadyExists(from_user_uuid, to_user_uuid)

        return FriendActionResponse(success=True, message="Friend request sent")

    async def change_status(
        self, current_user_uuid: str, request: FriendStatusRequest
    ) -> FriendActionResponse:
        if (
            request.status == FriendStatus.BLOCKED
            and current_user_uuid == request.target_uuid
        ):
            raise CannotBlockYourself()

        entity = await self._get_pair(current_user_uuid, request.target_uuid)

        if not entity:
            if request.status == FriendStatus.BLOCKED:
                entity = FriendEntity(
                    user_uuid1=current_user_uuid,
                    user_status1=FriendStatus.BLOCKED,
                    user_uuid2=request.target_uuid,
                    user_status2=FriendStatus.REJECT,
                    initiator_uuid=current_user_uuid,
                )
                await self._friend_repo.save(entity)
                return FriendActionResponse(success=True, message="Status changed")
            raise FriendRequestNotFound(current_user_uuid, request.target_uuid)

        self._validate_transition(entity, current_user_uuid, request.status)
        self._set_my_status(entity, current_user_uuid, request.status)

        if request.status == FriendStatus.ACCEPT and entity.initiator_uuid:
            if entity.user_uuid1 == entity.initiator_uuid and entity.user_status1 == FriendStatus.PROCESS:
                entity.user_status1 = FriendStatus.ACCEPT
            elif entity.user_uuid2 == entity.initiator_uuid and entity.user_status2 == FriendStatus.PROCESS:
                entity.user_status2 = FriendStatus.ACCEPT

        await self._friend_repo.save(entity, to_update=True)

        if entity.user_status1 == FriendStatus.ACCEPT and entity.user_status2 == FriendStatus.ACCEPT:
            return FriendActionResponse(success=True, just_created_chat=True, uuid=entity.user_uuid1,
                                        other_uuid=entity.user_uuid2, message="Status changed")
        return FriendActionResponse(success=True, message="Status changed")

    async def get_friends(
        self, user_uuid: str, limit: int, offset: int
    ) -> GetFriendsResponse:
        limit = max(1, min(limit, self._max_limit))
        offset = max(0, offset)

        pairs = await self._list_pairs_for_user(user_uuid)

        items: List[FriendItemResponse] = []
        uuids = []
        for entity in pairs:
            my_status, other_uuid, other_status = self._my_side(entity, user_uuid)

            if other_status == FriendStatus.BLOCKED:
                continue
            if my_status == FriendStatus.ACCEPT and other_status == FriendStatus.ACCEPT:
                items.append(
                    FriendItemResponse(
                        user_uuid=other_uuid,
                        status=FriendStatus.ACCEPT,
                        is_initiator=entity.initiator_uuid == user_uuid,
                        created_at=entity.created_at,
                    )
                )
                uuids.append(other_uuid)

        profiles_by_uuid = await self._profile_service.get_by_user_uuids(
            list(uuids),
        )

        total = len(items)
        items.sort(key=lambda i: i.created_at, reverse=True)
        paginated = items[offset: offset + limit]

        return GetFriendsResponse(
            items=paginated,
            total=total,
            profiles=profiles_by_uuid,
        )

    async def get_request_to_friends(
        self, user_uuid: str
    ) -> GetFriendRequestsResponse:
        pairs = await self._list_pairs_for_user(user_uuid)

        incoming: List[FriendRequestResponse] = []
        outgoing: List[FriendRequestResponse] = []

        for entity in pairs:
            my_status, other_uuid, other_status = self._my_side(entity, user_uuid)

            if other_status == FriendStatus.BLOCKED:
                continue
            if my_status != FriendStatus.PROCESS:
                continue

            if entity.initiator_uuid == user_uuid:
                outgoing.append(
                    FriendRequestResponse(
                        from_user_uuid=user_uuid,
                        to_user_uuid=other_uuid,
                        status=FriendStatus.PROCESS,
                        created_at=entity.created_at,
                    )
                )
            else:
                incoming.append(
                    FriendRequestResponse(
                        from_user_uuid=other_uuid,
                        to_user_uuid=user_uuid,
                        status=FriendStatus.PROCESS,
                        created_at=entity.created_at,
                    )
                )

        return GetFriendRequestsResponse(
            incoming=incoming,
            outgoing=outgoing,
            total_incoming=len(incoming),
            total_outgoing=len(outgoing),
        )

    async def check_friends(self, user_uuid1: str, user_uuid2: str) -> bool:
        entity = await self._get_pair(user_uuid1, user_uuid2)
        if not entity:
            return False
        return (
            entity.user_status1 == FriendStatus.ACCEPT
            and entity.user_status2 == FriendStatus.ACCEPT
        )


def get_friend_service() -> FriendService:
    return FriendService()
