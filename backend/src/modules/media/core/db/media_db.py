from sqlalchemy.orm import InstrumentedAttribute

from src.general.db.base_manager import BaseManager

from ...models.media_orm import MediaORM


class MediaManager(BaseManager[MediaORM]):
    def __init__(self):
        super().__init__(MediaORM, [MediaORM.uuid, MediaORM.created_at])

    @property
    def identifier_field(self) -> InstrumentedAttribute:
        return MediaORM.uuid


def get_media_manager() -> MediaManager:
    return MediaManager()
