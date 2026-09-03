from typing import Optional, List, Dict
from src.general.repository.sql.sql_base_repository import BaseRepository
from src.general.repository.sql.sql_query import SqlQuery

from .mappers.participant_mapper import ParticipantMapper
from ..db.participant_db import ParticipantManager
from ...models.entities.participant_entity import ParticipantEntity, ParticipantFields
from ...models.enums import ResourceType


class ParticipantRepository(BaseRepository[ParticipantManager, ParticipantFields, ParticipantEntity]):
    def __init__(self):
        super().__init__(ParticipantManager(), ParticipantMapper())

    async def get_by_uuid(self, uuid: str) -> Optional[ParticipantEntity]:
        return await self.get(SqlQuery().add_filter(ParticipantFields.UUID, uuid))

    async def find_by_user(self, user_uuid: str) -> List[ParticipantEntity]:
        return await self.get_all(SqlQuery().add_filter(ParticipantFields.USER_UUID, user_uuid))

    async def find_by_resource(self, resource_uuid: str) -> List[ParticipantEntity]:
        return await self.get_all(SqlQuery().add_filter(ParticipantFields.RESOURCE_UUID, resource_uuid))

    async def find_user_resource(
        self,
        user_uuid: str,
        resource_uuid: str,
        resource_type: ResourceType
    ) -> Optional[ParticipantEntity]:
        return await self.get(
            SqlQuery()
            .add_filter(ParticipantFields.USER_UUID, user_uuid)
            .add_filter(ParticipantFields.RESOURCE_UUID, resource_uuid)
            .add_filter(ParticipantFields.RESOURCE_TYPE, resource_type.value)
        )

    async def update_permissions(
        self,
        uuid: str,
        permissions: Dict[str, bool]
    ) -> Optional[ParticipantEntity]:
        result = await self.update(
            SqlQuery().add_filter(ParticipantFields.UUID, uuid),
            permissions=permissions
        )
        return result
