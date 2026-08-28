import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from uuid import uuid4

from src.modules.user.models.entities.user_entity import UserEntity
from src.modules.user.models.orm.user_orm import UserORM
from src.modules.user.core.repositories.mappers.user_mapper import UserMapper
from src.modules.user.core.repositories.user_repository import UserRepository
from src.modules.user.core.services.user_service import UserService
from src.modules.user.core.services.verify_service import VerifyService
from src.modules.user.core.client.client_sms_api import ClientSMS
from src.modules.sessions.api.session_service_api import SessionAPIService
from src.modules.sessions.api.models import (
    CreateSessionRequest,
    CreateSessionResponse,
    ValidateSessionResponse,
    DeleteSessionResponse
)
from src.general.security.encyptions.encrypter import Encrypter


@pytest.fixture
def sample_user_entity():
    return UserEntity(
        uuid=str(uuid4()),
        phone_number="+79001234567",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def sample_user_orm():
    return UserORM(
        uuid=str(uuid4()),
        phone_number_encrypted="encrypted_phone_data",
        phone_number_hash="hash_of_phone",
        phone_number_mask="+79***4567",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def mock_encrypter():
    encrypter = MagicMock(spec=Encrypter)
    encrypter.encrypt_field = AsyncMock(return_value="encrypted_data")
    encrypter.decrypt_field = AsyncMock(return_value="+79001234567")
    return encrypter


@pytest.fixture
def user_mapper(mock_encrypter):
    with patch.dict('os.environ', {'PHONE_HASH_SALT': 'test_salt'}):
        return UserMapper(encrypter=mock_encrypter)


@pytest.fixture
def mock_session_repository():
    repo = MagicMock()
    repo.save = AsyncMock()
    repo.get_by_field = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_session_service():
    service = MagicMock(spec=SessionAPIService)

    create_response = CreateSessionResponse(
        token="test_token_123456",
        user_uuid=str(uuid4()),
        expires_at=datetime.now() + timedelta(minutes=5),
        expires_in_seconds=300
    )
    service.create_session = AsyncMock(return_value=create_response)

    validate_response = ValidateSessionResponse(
        is_valid=True,
        user_uuid=str(uuid4()),
        expired_at=datetime.now() + timedelta(minutes=5)
    )
    service.validate_session = AsyncMock(return_value=validate_response)

    delete_response = DeleteSessionResponse(success=True)
    service.delete_session = AsyncMock(return_value=delete_response)
    service.delete_all_user_sessions = AsyncMock(return_value=1)
    service.get_user_sessions = AsyncMock(return_value=MagicMock(sessions=[], total=0))
    return service


@pytest.fixture
def mock_sms_client():
    client = MagicMock(spec=ClientSMS)
    client.send_verify_code = AsyncMock(return_value=True)
    client.send_login_code = AsyncMock(return_value=True)
    client.send_custom_sms = AsyncMock(return_value=True)
    return client


@pytest.fixture
def user_repository():
    repo = MagicMock(spec=UserRepository)
    repo.get_by_field = AsyncMock()
    repo.save = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def verify_service(mock_session_service, mock_sms_client):
    return VerifyService(
        session_service=mock_session_service,
        sms_api=mock_sms_client
    )


@pytest.fixture
def user_service(user_repository, verify_service):
    return UserService(
        user_repository=user_repository,
        verify_service=verify_service
    )


@pytest.fixture
def mock_request():
    request = MagicMock()
    request.headers = {"Authorization": "Bearer test_token_123456"}
    request.state = MagicMock()
    return request
