import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from uuid import uuid4

from src.modules.chats.chat_types.personal.core.personal_access_service import (
    PersonalAccessService,
    get_personal_access_service,
)
from src.modules.chats.models.entities.chat_entity import ChatEntity
from src.modules.chats.chat_types.personal.personal_models.personal_access_type import (
    PersonalAccessType,
)


@pytest.mark.unit
class TestPersonalAccessService:
    @pytest.mark.asyncio
    async def test_create_personal_chat_success(
        self,
        personal_access_service,
        personal_repository,
        sample_user_uuid,
        sample_companion_uuid,
    ):
        personal_repository.find_between_users = AsyncMock(return_value=None)

        from src.modules.chats.models.entities.chat_entity import ChatEntity
        from src.modules.chats.chat_types.personal.personal_models.personal_access_type import (
            PersonalAccessType,
        )

        mock_chat = ChatEntity(
            uuid=str(uuid4()),
            accesses=[
                PersonalAccessType(user_uuid=sample_user_uuid),
                PersonalAccessType(user_uuid=sample_companion_uuid),
            ],
        )
        personal_repository.save = AsyncMock(return_value=mock_chat)

        response = await personal_access_service.create_personal_chat(
            sample_user_uuid, sample_companion_uuid
        )

        assert response.success is True
        assert response.chat is not None

    @pytest.mark.asyncio
    async def test_create_personal_chat_same_user(
        self, personal_access_service, sample_user_uuid
    ):
        response = await personal_access_service.create_personal_chat(
            sample_user_uuid, sample_user_uuid
        )

        assert response.success is False

    @pytest.mark.asyncio
    async def test_create_personal_chat_already_exists(
        self,
        personal_access_service,
        personal_repository,
        sample_user_uuid,
        sample_companion_uuid,
    ):
        personal_repository.find_between_users = AsyncMock(return_value=MagicMock())

        response = await personal_access_service.create_personal_chat(
            sample_user_uuid, sample_companion_uuid
        )

        assert response.success is False

    @pytest.mark.asyncio
    async def test_create_personal_chat_exception(
        self,
        personal_access_service,
        personal_repository,
        sample_user_uuid,
        sample_companion_uuid,
    ):
        personal_repository.find_between_users = AsyncMock(
            side_effect=Exception("DB error")
        )

        response = await personal_access_service.create_personal_chat(
            sample_user_uuid, sample_companion_uuid
        )

        assert response.success is False

    @pytest.mark.asyncio
    async def test_get_personal_chat_success(
        self,
        personal_access_service,
        personal_repository,
        sample_chat_entity,
        sample_user_uuid,
    ):
        personal_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)

        response = await personal_access_service.get_personal_chat(
            sample_chat_entity.uuid, sample_user_uuid
        )

        assert response.success is True
        assert response.chat == sample_chat_entity

    @pytest.mark.asyncio
    async def test_get_personal_chat_not_found(
        self, personal_access_service, personal_repository
    ):
        personal_repository.get_by_uuid = AsyncMock(return_value=None)

        response = await personal_access_service.get_personal_chat(
            str(uuid4()), str(uuid4())
        )

        assert response.success is False

    @pytest.mark.asyncio
    async def test_get_personal_chat_user_not_in_chat(
        self, personal_access_service, personal_repository, sample_chat_entity
    ):
        personal_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)

        response = await personal_access_service.get_personal_chat(
            sample_chat_entity.uuid, str(uuid4())
        )

        assert response.success is False

    @pytest.mark.asyncio
    async def test_get_personal_chat_not_personal(
        self,
        personal_access_service,
        personal_repository,
        sample_chat_entity,
        sample_user_uuid,
    ):
        sample_chat_entity.accesses = [
            PersonalAccessType(user_uuid=sample_user_uuid),
            PersonalAccessType(user_uuid=str(uuid4())),
            PersonalAccessType(user_uuid=str(uuid4())),
        ]
        personal_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)

        response = await personal_access_service.get_personal_chat(
            sample_chat_entity.uuid, sample_user_uuid
        )

        assert response.success is False

    @pytest.mark.asyncio
    async def test_get_chats_for_user_success(
        self,
        personal_access_service,
        personal_repository,
        sample_chat_entity,
        sample_user_uuid,
    ):
        personal_repository.get_user_chats = AsyncMock(
            return_value=([sample_chat_entity], 1)
        )

        response = await personal_access_service.get_chats_for_user(
            sample_user_uuid, limit=10, offset=0
        )

        assert response.success is True
        assert len(response.chats) == 1
        assert response.total == 1

    @pytest.mark.asyncio
    async def test_get_chats_for_user_empty(
        self, personal_access_service, personal_repository, sample_user_uuid
    ):
        personal_repository.get_user_chats = AsyncMock(return_value=([], 0))

        response = await personal_access_service.get_chats_for_user(
            sample_user_uuid, limit=10, offset=0
        )

        assert response.success is True
        assert len(response.chats) == 0
        assert response.total == 0

    @pytest.mark.asyncio
    async def test_get_chats_for_user_exception(
        self, personal_access_service, personal_repository, sample_user_uuid
    ):
        personal_repository.get_user_chats = AsyncMock(
            side_effect=Exception("DB error")
        )

        response = await personal_access_service.get_chats_for_user(
            sample_user_uuid, limit=10, offset=0
        )

        assert response.success is False

    @pytest.mark.asyncio
    async def test_get_contact_list_success(
        self,
        personal_access_service,
        personal_repository,
        sample_user_uuid,
        sample_companion_uuid,
    ):
        from src.modules.chats.chat_types.personal.personal_models.personal_contact import (
            PersonalContact,
        )

        contacts = [
            PersonalContact(chat_uuid=str(uuid4()), user_uuid=sample_companion_uuid)
        ]
        personal_repository.get_contacts_with_status = AsyncMock(
            return_value=(contacts, 1)
        )

        response = await personal_access_service.get_contact_list(
            sample_user_uuid, limit=10, offset=0
        )

        assert response.success is True
        assert len(response.contacts) == 1
        assert response.total == 1

    @pytest.mark.asyncio
    async def test_find_chat_between_users_found(
        self,
        personal_access_service,
        personal_repository,
        sample_chat_entity,
        sample_user_uuid,
        sample_companion_uuid,
    ):
        personal_repository.find_between_users = AsyncMock(
            return_value=sample_chat_entity
        )

        response = await personal_access_service.find_chat_between_users(
            sample_user_uuid, sample_companion_uuid
        )

        assert response.found is True
        assert response.chat == sample_chat_entity

    @pytest.mark.asyncio
    async def test_find_chat_between_users_not_found(
        self, personal_access_service, personal_repository
    ):
        personal_repository.find_between_users = AsyncMock(return_value=None)

        response = await personal_access_service.find_chat_between_users(
            str(uuid4()), str(uuid4())
        )

        assert response.found is False
        assert response.chat is None

    @pytest.mark.asyncio
    async def test_block_user_in_chat_success(
        self,
        personal_access_service,
        personal_repository,
        sample_chat_entity,
        sample_user_uuid,
        sample_companion_uuid,
    ):
        personal_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)
        personal_repository.save = AsyncMock(
            return_value=ChatEntity(
                uuid=str(uuid4()),
                accesses=[
                    PersonalAccessType(user_uuid=sample_user_uuid),
                    PersonalAccessType(user_uuid=sample_companion_uuid),
                ],
            )
        )

        response = await personal_access_service.block_user_in_chat(
            sample_chat_entity.uuid, sample_user_uuid, sample_companion_uuid
        )

        assert response.success is True
        assert response.chat is not None
        personal_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_block_user_in_chat_already_blocked(
        self,
        personal_access_service,
        personal_repository,
        sample_chat_entity,
        sample_user_uuid,
        sample_companion_uuid,
    ):
        for access in sample_chat_entity.accesses:
            if access.user_uuid == sample_companion_uuid:
                access.is_blocked = True

        personal_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)

        response = await personal_access_service.block_user_in_chat(
            sample_chat_entity.uuid, sample_user_uuid, sample_companion_uuid
        )

        assert response.success is False

    @pytest.mark.asyncio
    async def test_block_self(
        self,
        personal_access_service,
        personal_repository,
        sample_chat_entity,
        sample_user_uuid,
    ):
        personal_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)

        response = await personal_access_service.block_user_in_chat(
            sample_chat_entity.uuid, sample_user_uuid, sample_user_uuid
        )

        assert response.success is False

    @pytest.mark.asyncio
    async def test_block_user_not_in_chat(
        self,
        personal_access_service,
        personal_repository,
        sample_chat_entity,
        sample_user_uuid,
    ):
        personal_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)

        response = await personal_access_service.block_user_in_chat(
            sample_chat_entity.uuid, sample_user_uuid, str(uuid4())
        )

        assert response.success is False

    @pytest.mark.asyncio
    async def test_unblock_user_in_chat_success(
        self,
        personal_access_service,
        personal_repository,
        sample_chat_entity,
        sample_user_uuid,
        sample_companion_uuid,
    ):
        for access in sample_chat_entity.accesses:
            if access.user_uuid == sample_companion_uuid:
                access.is_blocked = True
                access.blocked_at = datetime.now()
                access.blocked_by = sample_user_uuid

        personal_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)
        personal_repository.save = AsyncMock(
            return_value=ChatEntity(
                uuid=str(uuid4()),
                accesses=[
                    PersonalAccessType(user_uuid=sample_user_uuid),
                    PersonalAccessType(user_uuid=sample_companion_uuid),
                ],
            )
        )

        response = await personal_access_service.unblock_user_in_chat(
            sample_chat_entity.uuid, sample_companion_uuid, sample_user_uuid
        )

        assert response.success is True
        personal_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_unblock_user_not_blocked(
        self,
        personal_access_service,
        personal_repository,
        sample_chat_entity,
        sample_user_uuid,
        sample_companion_uuid,
    ):
        personal_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)

        response = await personal_access_service.unblock_user_in_chat(
            sample_chat_entity.uuid, sample_companion_uuid, sample_user_uuid
        )

        assert response.success is False

    @pytest.mark.asyncio
    async def test_delete_chat_success(
        self,
        personal_access_service,
        personal_repository,
        sample_chat_entity,
        sample_user_uuid,
    ):
        personal_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)
        personal_repository.delete = AsyncMock(return_value=1)

        response = await personal_access_service.delete_chat(
            sample_chat_entity.uuid, sample_user_uuid
        )

        assert response.success is True
        personal_repository.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_chat_not_found(
        self, personal_access_service, personal_repository
    ):
        personal_repository.get_by_uuid = AsyncMock(return_value=None)

        response = await personal_access_service.delete_chat(str(uuid4()), str(uuid4()))

        assert response.success is False

    @pytest.mark.asyncio
    async def test_delete_chat_user_not_in_chat(
        self, personal_access_service, personal_repository, sample_chat_entity
    ):
        personal_repository.get_by_uuid = AsyncMock(return_value=sample_chat_entity)

        response = await personal_access_service.delete_chat(
            sample_chat_entity.uuid, str(uuid4())
        )

        assert response.success is False

    def test_get_personal_access_service(self):
        service = get_personal_access_service()
        assert isinstance(service, PersonalAccessService)

    def test_is_user_in_chat(
        self, personal_access_service, sample_chat_entity, sample_user_uuid
    ):
        result = personal_access_service._is_user_in_chat(
            sample_chat_entity, sample_user_uuid
        )
        assert result is True

    def test_is_user_in_chat_false(self, personal_access_service, sample_chat_entity):
        result = personal_access_service._is_user_in_chat(
            sample_chat_entity, str(uuid4())
        )
        assert result is False

    def test_get_user_access(
        self, personal_access_service, sample_chat_entity, sample_user_uuid
    ):
        access = personal_access_service._get_user_access(
            sample_chat_entity, sample_user_uuid
        )
        assert access is not None
        assert access.user_uuid == sample_user_uuid

    def test_get_user_access_not_found(
        self, personal_access_service, sample_chat_entity
    ):
        access = personal_access_service._get_user_access(
            sample_chat_entity, str(uuid4())
        )
        assert access is None

    def test_validate_personal_chat_valid(
        self, personal_access_service, sample_chat_entity
    ):
        result = personal_access_service._validate_personal_chat(sample_chat_entity)
        assert result is True

    def test_validate_personal_chat_invalid(
        self, personal_access_service, sample_chat_entity, sample_user_uuid
    ):
        sample_chat_entity.accesses.append(PersonalAccessType(user_uuid=str(uuid4())))
        result = personal_access_service._validate_personal_chat(sample_chat_entity)
        assert result is False

    def test_validate_personal_chat_duplicate_users(
        self, personal_access_service, sample_chat_entity, sample_user_uuid
    ):
        sample_chat_entity.accesses.append(
            PersonalAccessType(user_uuid=sample_user_uuid)
        )
        result = personal_access_service._validate_personal_chat(sample_chat_entity)
        assert result is False
