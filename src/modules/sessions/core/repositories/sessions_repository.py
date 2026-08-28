from redis.asyncio import Redis
from typing import Optional

from src.core.redis import get_redis
from src.general.repository.redis.redis_base_repository import BaseRedisRepository

from .mappers.sessions_mapper import SessionMapper
from ...models.entities.session_entity import SessionEntity, SessionFields

class SessionRepository(BaseRedisRepository[SessionMapper, SessionFields, SessionEntity]):
    def __init__(self, redis_client: Optional[Redis] = None):
        mapper = SessionMapper()
        super().__init__(redis_client or get_redis(), mapper, ttl=86400)
        self.enable_indexes()

def get_session_repository() -> SessionRepository:
    return SessionRepository()
