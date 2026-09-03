from sqlalchemy.orm import InstrumentedAttribute
from src.general.db.base_manager import BaseManager

from ...models.orm.participant_orm import ParticipantORM


class ParticipantManager(BaseManager[ParticipantORM]):
    def __init__(self):
        super().__init__(model=ParticipantORM, immutable_fields=["uuid"])

    @property
    def identifier_field(self) -> InstrumentedAttribute:
        return ParticipantORM.uuid
