from typing import Protocol

from ..models.dto.responses import FriendActionResponse, GetFriendsResponse, GetFriendRequestsResponse
from ..models.dto.requests import FriendStatusRequest, SendFriendRequest


class FriendProtocol(Protocol):
    async def send_friend_request(self, from_user_uuid: str, request: SendFriendRequest) -> FriendActionResponse:
        pass

    async def change_status(self, current_user_uuid: str, request: FriendStatusRequest) -> FriendActionResponse:
        pass

    async def get_friends(self, user_uuid: str, limit: int, offset: int) -> GetFriendsResponse:
        pass

    async def get_request_to_friends(self, user_uuid: str) -> GetFriendRequestsResponse:
        pass


class PersonalProtocol(Protocol):
    async def create_by_uuid_with_bool(self, user_uuid: str, other_user_uuid: str) -> bool:
        pass


class FriendUseCases:
    def __init__(self, friend_protocol: FriendProtocol, personal_protocol: PersonalProtocol):
        self._friend_protocol = friend_protocol
        self._personal_protocol = personal_protocol

    async def send_friend_request(self, from_user_uuid: str, request: SendFriendRequest) -> FriendActionResponse:
        return await self._friend_protocol.send_friend_request(from_user_uuid, request)

    async def change_friend_status(self, current_user_uuid: str, request: FriendStatusRequest) -> FriendActionResponse:
        response = await self._friend_protocol.change_status(
            current_user_uuid=current_user_uuid,
            request=request,
        )
        if response.just_created_chat:
            await self._personal_protocol.create_by_uuid_with_bool(response.uuid, response.other_uuid)
        return response

    async def get_friends(self, user_uuid: str, limit: int, offset: int) -> GetFriendsResponse:
        return await self._friend_protocol.get_friends(user_uuid, limit, offset)

    async def get_request_to_friends(self, user_uuid: str) -> GetFriendRequestsResponse:
        return await self._friend_protocol.get_request_to_friends(user_uuid)
