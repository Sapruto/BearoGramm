from typing import Optional

from src.general.repository.sql.sql_base_repository import BaseRepository

from .media_mapper import MediaMapper
from ..db.media_db import MediaManager, get_media_manager
from ...models.media_entity import MediaFields, MediaEntity


class MediaRepository(BaseRepository[MediaManager, MediaFields, MediaEntity]):
    def __init__(self, manager: Optional[MediaManager] = None):
        mapper = MediaMapper()
        super().__init__(manager=manager or get_media_manager(), mapper=mapper)


def get_media_repository() -> MediaRepository:
    return MediaRepository()
