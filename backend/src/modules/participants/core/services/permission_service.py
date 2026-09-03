from typing import Optional, List

from src.core.logger import get_logger
from src.general.repository.sql.sql_query import SqlQuery

from ..exceptions import ParticipantNotFoundError, PermissionAlreadyExistsError
from ..repositories.participant_repository import ParticipantRepository
from ...models.enums import ResourceType, ActionTypification
from ...models.entities.participant_entity import ParticipantEntity
from ...models.entities.permission import Permission

logger = get_logger(__name__)


class PermissionService:
    def __init__(
        self,
        participant_repository: Optional[ParticipantRepository] = None
    ):
        self.participant_repository = participant_repository or ParticipantRepository()

    async def create(
        self,
        user_uuid: str,
        resource_uuid: str,
        resource_type: ResourceType,
        permissions: Optional[List[Permission]] = None
    ) -> ParticipantEntity:
        existing = await self.participant_repository.find_user_resource(
            user_uuid, resource_uuid, resource_type
        )
        if existing:
            raise PermissionAlreadyExistsError(
                f"User {user_uuid} already has permissions on {resource_type.value} {resource_uuid}"
            )

        perms_dict = {p.action.value: p.enabled for p in permissions} if permissions else {}
        entity = ParticipantEntity.create(
            user_uuid=user_uuid,
            resource_uuid=resource_uuid,
            resource_type=resource_type,
            permissions=perms_dict
        )
        return await self.participant_repository.save(entity)

    async def get(
        self,
        uuid: str
    ) -> ParticipantEntity:
        entity = await self.participant_repository.get_by_uuid(uuid)
        if not entity:
            raise ParticipantNotFoundError(f"Participant {uuid} not found")
        return entity

    async def get_by_user_resource(
        self,
        user_uuid: str,
        resource_uuid: str,
        resource_type: ResourceType
    ) -> Optional[ParticipantEntity]:
        return await self.participant_repository.find_user_resource(
            user_uuid, resource_uuid, resource_type
        )

    async def get_by_user(
        self,
        user_uuid: str
    ) -> List[ParticipantEntity]:
        return await self.participant_repository.find_by_user(user_uuid)

    async def get_by_resource(
        self,
        resource_uuid: str
    ) -> List[ParticipantEntity]:
        return await self.participant_repository.find_by_resource(resource_uuid)

    async def update(
        self,
        uuid: str,
        permissions: List[Permission]
    ) -> ParticipantEntity:
        await self.get(uuid)
        perms_dict = {p.action.value: p.enabled for p in permissions}
        result = await self.participant_repository.update_permissions(uuid, perms_dict)
        if not result:
            raise ParticipantNotFoundError(f"Participant {uuid} not found")
        return result

    async def delete(
        self,
        uuid: str
    ) -> bool:
        await self.get(uuid)
        return await self.participant_repository.delete(
            SqlQuery().add_filter("uuid", uuid)
        ) > 0


    async def validate(
        self,
        user_uuid: str,
        resource_uuid: str,
        resource_type: ResourceType,
        action: ActionTypification
    ) -> bool:
        participant = await self.participant_repository.find_user_resource(
            user_uuid, resource_uuid, resource_type
        )
        if not participant:
            return False
        if not participant.permissions.get(action, False):
            return False
        return True


def get_permission_service(participant_repository: Optional[ParticipantRepository] = None) -> PermissionService:
    return PermissionService(participant_repository or ParticipantRepository())
