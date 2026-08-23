from fastapi import APIRouter, Depends, HTTPException, status, Query, Path

from src.modules.user import get_current_user_depends
from src.modules.user.models.entities.user_entity import UserEntity

from .personal_chats_router_names import PersonalChatsRoutes
from ..core.personal_access_service import PersonalAccessService, get_personal_access_service
from ..models.dto.responses import CreateChatResponse, GetChatResponse, ListChatsResponse, ContactsResponse, FindChatResponse, BlockUserResponse, UnblockUserResponse, DeleteChatResponse

personal_chats_router = APIRouter(prefix=PersonalChatsRoutes.base)

@personal_chats_router.post(
    PersonalChatsRoutes.create,
    response_model=CreateChatResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_personal_chat(current_user: UserEntity = Depends(get_current_user_depends()), companion_uuid: str = Query(...), service: PersonalAccessService = Depends(get_personal_access_service)):
    try:
        chat = await service.create_personal_chat(current_user.uuid, companion_uuid)
        return CreateChatResponse(chat=chat)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@personal_chats_router.get(
    PersonalChatsRoutes.get,
    response_model=GetChatResponse
)
async def get_personal_chat(current_user: UserEntity = Depends(get_current_user_depends()), chat_uuid: str = Path(...), service: PersonalAccessService = Depends(get_personal_access_service)):
    chat = await service.get_by_uuid(chat_uuid)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Chat {chat_uuid} not found")
    if not service.validate_personal_chat(chat):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chat is not a valid personal chat")

    if not service.is_user_in_chat(chat, current_user.uuid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not in this chat")

    return GetChatResponse(chat=chat)

@personal_chats_router.get(
    PersonalChatsRoutes.list,
    response_model=ListChatsResponse
)
async def list_personal_chats(current_user: UserEntity = Depends(get_current_user_depends()), service: PersonalAccessService = Depends(get_personal_access_service)):
    chats = await service.get_chats_for_user(current_user.uuid)
    return ListChatsResponse(chats=chats, total=len(chats))

@personal_chats_router.get(
    PersonalChatsRoutes.contacts,
    response_model=ContactsResponse
)
async def get_contacts(current_user: UserEntity = Depends(get_current_user_depends()), service: PersonalAccessService = Depends(get_personal_access_service)):
    contacts = await service.get_contact_list(current_user.uuid)
    return ContactsResponse(contacts=contacts, total=len(contacts))

@personal_chats_router.get(
    PersonalChatsRoutes.find,
    response_model=FindChatResponse
)
async def find_chat_between_users(current_user: UserEntity = Depends(get_current_user_depends()), companion_uuid: str = Query(...), service: PersonalAccessService = Depends(get_personal_access_service)):
    chat = await service.find_chat_between_users(current_user.uuid, companion_uuid)
    return FindChatResponse(chat=chat, found=chat is not None)
@personal_chats_router.post(
    PersonalChatsRoutes.block,
    response_model=BlockUserResponse
)
async def block_user_in_chat(current_user: UserEntity = Depends(get_current_user_depends()), chat_uuid: str = Path(...), blocked_uuid: str = Query(...), service: PersonalAccessService = Depends(get_personal_access_service)):
    chat = await service.get_by_uuid(chat_uuid)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Chat {chat_uuid} not found")

    if not service.is_user_in_chat(chat, current_user.uuid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not in this chat")

    try:
        updated_chat = await service.block_user_in_chat(chat, current_user.uuid, blocked_uuid)
        return BlockUserResponse(chat=updated_chat)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@personal_chats_router.post(
    PersonalChatsRoutes.unblock,
    response_model=UnblockUserResponse
)
async def unblock_user_in_chat(current_user: UserEntity = Depends(get_current_user_depends()), chat_uuid: str = Path(...), user_uuid: str = Query(...), service: PersonalAccessService = Depends(get_personal_access_service)):
    chat = await service.get_by_uuid(chat_uuid)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Chat {chat_uuid} not found")

    if not service.is_user_in_chat(chat, current_user.uuid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not in this chat")

    try:
        updated_chat = await service.unblock_user_in_chat(chat, user_uuid)
        return UnblockUserResponse(chat=updated_chat)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@personal_chats_router.delete(
    PersonalChatsRoutes.delete,
    response_model=DeleteChatResponse
)
async def delete_personal_chat(current_user: UserEntity = Depends(get_current_user_depends()), chat_uuid: str = Path(...), service: PersonalAccessService = Depends(get_personal_access_service)):
    chat = await service.get_by_uuid(chat_uuid)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Chat {chat_uuid} not found")

    if not service.is_user_in_chat(chat, current_user.uuid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not in this chat")

    await service.delete_chat(chat_uuid)
    return DeleteChatResponse(chat_uuid=chat_uuid)
