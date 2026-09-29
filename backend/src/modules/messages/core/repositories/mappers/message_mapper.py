from typing import Any, Tuple, List, Optional
from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.general.repository.exception import NotConvertableValue
from src.core.logger import get_logger
from src.general.security.encyptions.encrypter import get_encrypter

from ....models.orm.message_orm import MessageORM
from ....models.entities.message_entity import MessageFields, MessageEntity
from ....models.entities.message_data_entity import MessageDataEntity
from ....models.entities.message_reference_entity import MessageReferenceEntity
from ....models.message_load_options import MessageLoadOptions

from .message_data_mapper import MessageDataMapper
from .message_reference_mapper import MessageReferenceMapper

logger = get_logger(__name__)


class MessageMapper(BaseMapper[MessageEntity, MessageORM, MessageFields]):
    field_mapping = {
        MessageFields.UUID: MessageORM.uuid,
        MessageFields.MESSAGE_TEXT: MessageORM.message_text,
        MessageFields.CREATED_AT: MessageORM.created_at,
        MessageFields.UPDATED_AT: MessageORM.updated_at,
        MessageFields.HAS_EXTRA_DATA: MessageORM.has_extra_data,
        MessageFields.CHAT_UUID: MessageORM.chat_uuid,
        MessageFields.USER_UUID: MessageORM.user_uuid,
        MessageFields.EXTRA_DATA: MessageORM.extra_data,
        MessageFields.REFERENCES: MessageORM.references,
    }

    reverse_field_mapping = {v: k for k, v in field_mapping.items()}

    def __init__(self):
        super().__init__()
        self.data_mapper = MessageDataMapper()
        self.reference_mapper = MessageReferenceMapper()
        self.encrypter = get_encrypter()

    async def encrypt_text(self, text: Optional[str]) -> Optional[str]:
        if text is None:
            return None
        return await self.encrypter.encrypt(text)

    async def _decrypt_text(self, text: Optional[str]) -> Optional[str]:
        if text is None:
            return None
        return await self.encrypter.decrypt(text)

    async def to_orm(self, entity: MessageEntity) -> MessageORM:
        orm = MessageORM(
            uuid=entity.uuid,
            message_text=await self.encrypt_text(entity.message_text),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            has_extra_data=entity.extra_data is not None,
            chat_uuid=entity.chat_uuid,
            user_uuid=entity.user_uuid,
        )

        if entity.extra_data is not None:
            orm.extra_data = await self.data_mapper.to_orm(entity.extra_data)

        if entity.references:
            orm.references = [
                await self.reference_mapper.to_orm(r) for r in entity.references
            ]

        return orm

    async def to_entity(
        self,
        orm: MessageORM,
        load_options: Optional[MessageLoadOptions] = None,
    ) -> MessageEntity:
        load_options = load_options or MessageLoadOptions()

        extra_entity: Optional[MessageDataEntity] = None
        if load_options.extra and orm.has_extra_data:
            extra_orm = orm.__dict__.get("extra_data")
            if extra_orm is not None:
                extra_entity = await self.data_mapper.to_entity(extra_orm)

        references_entity: List[MessageReferenceEntity] = []
        if load_options.references:
            refs = orm.__dict__.get("references") or []
            for r in refs:
                references_entity.append(await self.reference_mapper.to_entity(r))

        return MessageEntity(
            uuid=orm.uuid,
            message_text=await self._decrypt_text(orm.message_text),
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            has_extra_data=orm.has_extra_data,
            chat_uuid=orm.chat_uuid,
            user_uuid=orm.user_uuid,
            extra_data=extra_entity,
            references=references_entity,
        )

    async def to_entity_many(
        self,
        orms: List[MessageORM],
        load_options: Optional[MessageLoadOptions] = None,
    ) -> List[MessageEntity]:
        return [await self.to_entity(o, load_options) for o in orms]

    async def to_orm_value(
        self, field: MessageFields, value: Any
    ) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = await self.to_orm_field(field)

        if field == MessageFields.MESSAGE_TEXT:
            return MessageORM.message_text, await self.encrypt_text(value)

        if field == MessageFields.EXTRA_DATA and value is not None:
            if not isinstance(value, MessageDataEntity):
                raise NotConvertableValue(
                    value, "extra_data", "Must be MessageDataEntity"
                )
            return MessageORM.extra_data, await self.data_mapper.to_orm(value)

        if field == MessageFields.REFERENCES and value is not None:
            if not isinstance(value, list):
                raise NotConvertableValue(value, "references", "Must be a list")
            orm_refs = [await self.reference_mapper.to_orm(r) for r in value]
            return MessageORM.references, orm_refs

        return orm_field, value

    async def to_entity_value(
        self, field: InstrumentedAttribute, value: Any
    ) -> Tuple[MessageFields, Any]:
        entity_field = await self.to_entity_field(field)

        if entity_field == MessageFields.MESSAGE_TEXT:
            return entity_field, await self._decrypt_text(value)

        if entity_field == MessageFields.EXTRA_DATA and value is not None:
            return entity_field, await self.data_mapper.to_entity(value)

        if entity_field == MessageFields.REFERENCES and value is not None:
            return entity_field, [
                await self.reference_mapper.to_entity(r) for r in value
            ]

        return entity_field, value

    async def to_orm_field(self, field: MessageFields) -> InstrumentedAttribute:
        orm_field = self.field_mapping.get(field)
        if not orm_field:
            raise ValueError(f"No mapping found for field: {field}")
        return orm_field

    async def to_entity_field(self, field: InstrumentedAttribute) -> MessageFields:
        entity_field = self.reverse_field_mapping.get(field)
        if entity_field:
            return entity_field
        field_name = str(field).split(".")[-1]
        for orm_attr, entity_enum in self.reverse_field_mapping.items():
            if str(orm_attr).split(".")[-1] == field_name:
                return entity_enum
        raise ValueError(f"No reverse mapping found for field: {field}")
