from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from ..core.personal_repository import PersonalChatRepository, get_personal_chat_repository
from ..models.personal_access_type import PersonalAccessType
from ..models.dto.responses import CreateChatResponse, GetChatResponse, ListChatsResponse, ContactsResponse, FindChatResponse, BlockUserResponse, UnblockUserResponse, DeleteChatResponse
from ....models.entities.chat_entity import ChatEntity

class PersonalAccessService:
    def __init__(self, repo: Optional[PersonalChatRepository] = None):
        self.repo = repo or get_personal_chat_repository()

    def _is_user_in_chat(self, chat: ChatEntity, user_uuid: str) -> bool:
        return any(a.user_uuid == user_uuid for a in chat.accesses)

    def _get_user_access(self, chat: ChatEntity, user_uuid: str) -> Optional[PersonalAccessType]:
        for access in chat.accesses:
            if access.user_uuid == user_uuid:
                return access
        return None

    def _validate_personal_chat(self, chat: ChatEntity) -> bool:
        participants = [a.user_uuid for a in chat.accesses]
        return len(participants) == 2 and len(set(participants)) == 2

    async def create_personal_chat(self, user_uuid: str, companion_uuid: str) -> CreateChatResponse:
        try:
            if user_uuid == companion_uuid:
                return CreateChatResponse(
                    success=False,
                    error_message="Нельзя создать чат с самим собой"
                )

            existing = await self.repo.find_between_users(user_uuid, companion_uuid)
            if existing:
                return CreateChatResponse(
                    success=False,
                    error_message="Чат между пользователями уже существует"
                )

            chat = ChatEntity(
                uuid=str(uuid4()),
                accesses=[
                    PersonalAccessType(user_uuid=user_uuid),
                    PersonalAccessType(user_uuid=companion_uuid)
                ],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            result = await self.repo.save(chat)
            return CreateChatResponse(success=True, chat=result)

        except Exception as e:
            return CreateChatResponse(
                success=False,
                error_message=f"Ошибка создания чата: {str(e)}"
            )

    async def get_personal_chat(self, chat_uuid: str, user_uuid: str) -> GetChatResponse:
        try:
            chat = await self.repo.get_by_uuid(chat_uuid)
            if not chat:
                return GetChatResponse(
                    success=False,
                    error_message=f"Чат {chat_uuid} не найден"
                )

            if not self._is_user_in_chat(chat, user_uuid):
                return GetChatResponse(
                    success=False,
                    error_message="Вы не в этом чате"
                )

            if not self._validate_personal_chat(chat):
                return GetChatResponse(
                    success=False,
                    error_message="Чат не является личным"
                )

            return GetChatResponse(success=True, chat=chat)

        except Exception as e:
            return GetChatResponse(
                success=False,
                error_message=f"Ошибка получения чата: {str(e)}"
            )

    async def get_chats_for_user(self, user_uuid: str, limit: int = 50, offset: int = 0) -> ListChatsResponse:
        try:
            chats, total = await self.repo.get_user_chats(user_uuid, limit, offset)
            return ListChatsResponse(
                success=True,
                chats=chats,
                total=total
            )

        except Exception as e:
            return ListChatsResponse(
                success=False,
                error_message=f"Ошибка получения чатов: {str(e)}"
            )

    async def get_contact_list(self, user_uuid: str, limit: int = 50, offset: int = 0) -> ContactsResponse:
        try:
            contacts, total = await self.repo.get_contacts_with_status(user_uuid, limit, offset)
            return ContactsResponse(
                success=True,
                contacts=contacts,
                total=total
            )

        except Exception as e:
            return ContactsResponse(
                success=False,
                error_message=f"Ошибка получения контактов: {str(e)}"
            )

    async def find_chat_between_users(self, user_uuid: str, companion_uuid: str) -> FindChatResponse:
        try:
            chat = await self.repo.find_between_users(user_uuid, companion_uuid)
            return FindChatResponse(
                chat=chat,
                found=chat is not None
            )

        except Exception as e:
            return FindChatResponse(
                chat=None,
                found=False
            )

    async def block_user_in_chat(self, chat_uuid: str, blocker_uuid: str, blocked_uuid: str) -> BlockUserResponse:
        try:
            chat = await self.repo.get_by_uuid(chat_uuid)
            if not chat:
                return BlockUserResponse(
                    success=False,
                    error_message=f"Чат {chat_uuid} не найден"
                )

            if not self._is_user_in_chat(chat, blocker_uuid):
                return BlockUserResponse(
                    success=False,
                    error_message="Вы не в этом чате"
                )

            blocked_access = self._get_user_access(chat, blocked_uuid)
            if not blocked_access:
                return BlockUserResponse(
                    success=False,
                    error_message=f"Пользователь {blocked_uuid} не в чате"
                )

            if blocker_uuid == blocked_uuid:
                return BlockUserResponse(
                    success=False,
                    error_message="Нельзя заблокировать самого себя"
                )

            if blocked_access.is_blocked:
                return BlockUserResponse(
                    success=False,
                    error_message="Пользователь уже заблокирован"
                )

            blocked_access.is_blocked = True
            blocked_access.blocked_at = datetime.now()
            blocked_access.blocked_by = blocker_uuid

            result = await self.repo.save(chat)
            return BlockUserResponse(success=True, chat=result)

        except Exception as e:
            return BlockUserResponse(
                success=False,
                error_message=f"Ошибка блокировки: {str(e)}"
            )

    async def unblock_user_in_chat(self, chat_uuid: str, user_uuid: str, unblocker_uuid: str) -> UnblockUserResponse:
        try:
            chat = await self.repo.get_by_uuid(chat_uuid)
            if not chat:
                return UnblockUserResponse(
                    success=False,
                    error_message=f"Чат {chat_uuid} не найден"
                )

            if not self._is_user_in_chat(chat, unblocker_uuid):
                return UnblockUserResponse(
                    success=False,
                    error_message="Вы не в этом чате"
                )

            user_access = self._get_user_access(chat, user_uuid)
            if not user_access:
                return UnblockUserResponse(
                    success=False,
                    error_message=f"Пользователь {user_uuid} не в чате"
                )

            if not user_access.is_blocked:
                return UnblockUserResponse(
                    success=False,
                    error_message="Пользователь не заблокирован"
                )

            user_access.is_blocked = False
            user_access.blocked_at = None
            user_access.blocked_by = None

            result = await self.repo.save(chat)
            return UnblockUserResponse(success=True, chat=result)

        except Exception as e:
            return UnblockUserResponse(
                success=False,
                error_message=f"Ошибка разблокировки: {str(e)}"
            )

    async def delete_chat(self, chat_uuid: str, user_uuid: str) -> DeleteChatResponse:
        try:
            chat = await self.repo.get_by_uuid(chat_uuid)
            if not chat:
                return DeleteChatResponse(
                    success=False,
                    error_message=f"Чат {chat_uuid} не найден"
                )

            if not self._is_user_in_chat(chat, user_uuid):
                return DeleteChatResponse(
                    success=False,
                    error_message="Вы не в этом чате"
                )

            await self.repo.delete(chat_uuid)
            return DeleteChatResponse(success=True)

        except Exception as e:
            return DeleteChatResponse(
                success=False,
                error_message=f"Ошибка удаления чата: {str(e)}"
            )

def get_personal_access_service() -> PersonalAccessService:
    return PersonalAccessService()
