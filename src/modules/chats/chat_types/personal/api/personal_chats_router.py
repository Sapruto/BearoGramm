from fastapi import APIRouter, Depends, Query, Path

from src.modules.user import get_current_user_depends
from src.modules.user.models.entities.user_entity import UserEntity

from .personal_chats_router_names import PersonalChatsRoutes
from ..core.personal_access_service import PersonalAccessService, get_personal_access_service
from ..models.dto.responses import CreateChatResponse, GetChatResponse, ListChatsResponse, ContactsResponse, FindChatResponse, BlockUserResponse, UnblockUserResponse, DeleteChatResponse

personal_chats_router = APIRouter(prefix=PersonalChatsRoutes.base)

@personal_chats_router.post(
    PersonalChatsRoutes.create,
    response_model=CreateChatResponse
)
async def create_personal_chat(current_user: UserEntity = Depends(get_current_user_depends()), companion_uuid: str = Query(...), service: PersonalAccessService = Depends(get_personal_access_service)):
    return await service.create_personal_chat(current_user.uuid, companion_uuid)

@personal_chats_router.get(
    PersonalChatsRoutes.get,
    response_model=GetChatResponse
)
async def get_personal_chat(current_user: UserEntity = Depends(get_current_user_depends()), chat_uuid: str = Path(...), service: PersonalAccessService = Depends(get_personal_access_service)):
    return await service.get_personal_chat(chat_uuid, current_user.uuid)

@personal_chats_router.get(
    PersonalChatsRoutes.list,
    response_model=ListChatsResponse
)
async def list_personal_chats(current_user: UserEntity = Depends(get_current_user_depends()), limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), service: PersonalAccessService = Depends(get_personal_access_service)):
    return await service.get_chats_for_user(current_user.uuid, limit, offset)

@personal_chats_router.get(
    PersonalChatsRoutes.contacts,
    response_model=ContactsResponse
)
async def get_contacts(current_user: UserEntity = Depends(get_current_user_depends()), limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), service: PersonalAccessService = Depends(get_personal_access_service)):
    return await service.get_contact_list(current_user.uuid, limit, offset)

@personal_chats_router.get(
    PersonalChatsRoutes.find,
    response_model=FindChatResponse
)
async def find_chat_between_users(current_user: UserEntity = Depends(get_current_user_depends()), companion_uuid: str = Query(...), service: PersonalAccessService = Depends(get_personal_access_service)):
    return await service.find_chat_between_users(current_user.uuid, companion_uuid)

@personal_chats_router.post(
    PersonalChatsRoutes.block,
    response_model=BlockUserResponse
)
async def block_user_in_chat(current_user: UserEntity = Depends(get_current_user_depends()), chat_uuid: str = Path(...), blocked_uuid: str = Query(...), service: PersonalAccessService = Depends(get_personal_access_service)):
    return await service.block_user_in_chat(chat_uuid, current_user.uuid, blocked_uuid)

@personal_chats_router.post(
    PersonalChatsRoutes.unblock,
    response_model=UnblockUserResponse
)
async def unblock_user_in_chat(current_user: UserEntity = Depends(get_current_user_depends()), chat_uuid: str = Path(...), user_uuid: str = Query(...), service: PersonalAccessService = Depends(get_personal_access_service)):
    return await service.unblock_user_in_chat(chat_uuid, user_uuid, current_user.uuid)


@personal_chats_router.delete(
    PersonalChatsRoutes.delete,
    response_model=DeleteChatResponse
)
async def delete_personal_chat(current_user: UserEntity = Depends(get_current_user_depends()), chat_uuid: str = Path(...), service: PersonalAccessService = Depends(get_personal_access_service)):
    return await service.delete_chat(chat_uuid, current_user.uuid)
