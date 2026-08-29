from redis.asyncio import Redis
from typing import Optional
import asyncio

from src.core.settings import Settings
from src.core.logger import get_logger

logger = get_logger(__name__)

_redis_client: Optional[Redis] = None
_loop: Optional[asyncio.AbstractEventLoop] = None

def init_redis(host: Optional[str] = None, port: Optional[int] = None, db: Optional[int] = None, password: Optional[str] = None, decode_responses: bool = True) -> Redis:
    global _redis_client, _loop

    if _redis_client is not None:
        logger.warning("Redis already initialized")
        return _redis_client

    _redis_client = Redis(
        host=host or Settings.REDIS.REDIS_HOST,
        port=port or Settings.REDIS.REDIS_PORT,
        db=db or Settings.REDIS.REDIS_DB,
        password=password or Settings.REDIS.REDIS_PASSWORD,
        decode_responses=decode_responses
    )

    _loop = asyncio.get_running_loop() if asyncio._get_running_loop() else None

    logger.info(f"Redis initialized")
    return _redis_client

def get_redis() -> Redis:
    global _redis_client

    if _redis_client is None:
        logger.info("Redis not initialized, initializing with default config...")
        init_redis()

    return _redis_client

async def close_redis() -> None:
    global _redis_client

    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")

async def ping_redis() -> bool:
    try:
        client = get_redis()
        await client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis ping failed: {e}")
        return False

def is_redis_connected() -> bool:
    return _redis_client is not None

def get_loop() -> Optional[asyncio.AbstractEventLoop]:
    global _loop
    try:
        _loop = asyncio.get_running_loop()
        return _loop
    except RuntimeError:
        return None

async def ensure_redis_connected() -> Redis:
    client = get_redis()
    try:
        await client.ping()
        return client
    except Exception as e:
        logger.error(f"Redis connection lost, reconnecting... {e}")
        await close_redis()
        return get_redis()
