import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from uuid import uuid4
from redis.asyncio import Redis

from src.modules.calls.models.entities.call_state_entity import (
    CallStateEntity,
    CallStatus,
    CallType,
    CallStateFields,
)
from src.modules.calls.core.repositories.mappers.calls_state_mapper import (
    CallsStateMapper,
)
from src.modules.calls.core.repositories.calls_state_repository import (
    CallsStateRepository,
)
from src.modules.calls.core.services.calls_state_service import CallsStateService
from src.modules.calls.core.clients.push_client_api import PushClientAPI
from src.modules.calls.core.clients.push_client_impl import PushClientImpl


@pytest.fixture
def sample_user_uuid():
    return str(uuid4())


@pytest.fixture
def sample_callee_uuid():
    return str(uuid4())


@pytest.fixture
def sample_room_id():
    return str(uuid4())


@pytest.fixture
def sample_call_state_entity(sample_user_uuid, sample_callee_uuid):
    return CallStateEntity(
        user_uuid=sample_user_uuid,
        caller_uuid=sample_user_uuid,
        callee_uuid=sample_callee_uuid,
        status=CallStatus.WAITING,
        call_type=CallType.P2P,
        sdp_offer="test_offer",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_room_call_entity(sample_user_uuid, sample_room_id):
    return CallStateEntity(
        user_uuid=sample_user_uuid,
        room_id=sample_room_id,
        call_type=CallType.ROOM,
        status=CallStatus.WAITING,
        participants=[sample_user_uuid],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_redis():
    redis = MagicMock(spec=Redis)
    redis.hset = AsyncMock(return_value=1)
    redis.hgetall = AsyncMock()
    redis.delete = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    redis.scan = AsyncMock(return_value=(0, []))
    redis.set = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.exists = AsyncMock(return_value=1)
    redis.publish = AsyncMock(return_value=1)
    redis.pubsub = MagicMock()
    return redis


@pytest.fixture
def calls_state_mapper():
    return CallsStateMapper()


@pytest.fixture
def calls_state_repository(mock_redis):
    repo = CallsStateRepository(redis_client=mock_redis)
    repo._index_enabled = False
    return repo


@pytest.fixture
def mock_push_client():
    client = MagicMock(spec=PushClientAPI)
    client.send_push_notification = AsyncMock(return_value=True)
    client.send_call_push = AsyncMock(return_value=True)
    return client


@pytest.fixture
def mock_push_impl():
    impl = MagicMock(spec=PushClientImpl)
    impl.send = AsyncMock(return_value=True)
    return impl


@pytest.fixture
def calls_state_service(mock_redis, mock_push_client):
    mock_repo = MagicMock(spec=CallsStateRepository)
    mock_repo.save = AsyncMock()
    mock_repo.get_all = AsyncMock()
    mock_repo.get_by_id = AsyncMock()
    mock_repo.delete_by_id = AsyncMock()
    mock_repo.notify_user = AsyncMock()
    mock_repo.pubsub = MagicMock()

    service = CallsStateService(
        calls_state_repository=mock_repo, push_client_api=mock_push_client
    )
    service.CALL_TIMEOUT = 1
    return service


@pytest.fixture
def mock_ws_send():
    return AsyncMock()


@pytest.fixture
def mock_ws_receive():
    return AsyncMock()
