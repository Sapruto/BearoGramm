from typing import Protocol

from src.modules.profiles_custom.models.entities.profile_custom_entity import ProfileCustomEntity
from ..models.dto.requests import SendCodeRequest, VerifyCodeRequest
from ..models.dto.responses import SendCodeResponse, VerifyCodeResponse


class AuthProtocol(Protocol):
    async def send_code_and_register_if_not(self, request: SendCodeRequest) -> SendCodeResponse:
        pass

    async def verify_phone(self, request: VerifyCodeRequest) -> VerifyCodeResponse:
        pass


class ProfileProtocol(Protocol):
    async def create(self, user_uuid: str) -> ProfileCustomEntity:
        pass

    async def get_by_user_uuid(self, user_uuid: str) -> ProfileCustomEntity:
        pass


class AuthUseCases:
    def __init__(self, auth_protocol: AuthProtocol, profile_protocol: ProfileProtocol):
        self._auth_protocol = auth_protocol
        self._profile_protocol = profile_protocol

    async def send_code(self, data: SendCodeRequest) -> SendCodeResponse:
        return await self._auth_protocol.send_code_and_register_if_not(data)

    async def verify_phone(self, data: VerifyCodeRequest) -> VerifyCodeResponse:
        response = await self._auth_protocol.verify_phone(data)

        profile = await self._profile_protocol.get_by_user_uuid(response.user.uuid)
        if not profile:
            response.just_created_profile = True
            profile = await self._profile_protocol.create(response.user.uuid)
        response.profile = profile

        return response
