import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

project_root = Path(__file__).parent.parent
src_path = project_root / "src"

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    session.add = AsyncMock()
    session.refresh = AsyncMock()
    return session

@pytest.fixture
def mock_redis():
    mock = MagicMock()
    mock.get = AsyncMock()
    mock.setex = AsyncMock()
    mock.zadd = AsyncMock()
    mock.zrem = AsyncMock()
    mock.zrevrange = AsyncMock()
    mock.pipeline = MagicMock()
    mock.close = AsyncMock()
    return mock