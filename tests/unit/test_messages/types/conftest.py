import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.modules.messages.types.base.base_message_data import BaseMessageData
from src.modules.messages.types.text.text_message_data import TextMessageData, TextMessageTypeName
from src.modules.messages.types.media.models.media_message_data import MediaMessageData, MediaMessageTypeName
from src.modules.messages.types.text.text_message_service import TextMessageService
from src.modules.messages.types.media.core.media_message_service import MediaMessageService
from src.modules.messages.types.media.core.validator.media_validator import MediaValidator, MediaValidatorConfig
from src.modules.messages.types.media.core.utils.media_utils import MediaUtils
from src.modules.messages.types.media.core.storages.storage_api import StorageAPI
from src.general.security.encyptions.encrypter import Encrypter


@pytest.fixture
def sample_text_data():
    return TextMessageData(
        text="Hello world",
        data_type=TextMessageTypeName
    )


@pytest.fixture
def sample_media_data():
    return MediaMessageData(
        media_url="https://example.com/media/test.jpg",
        data_type=MediaMessageTypeName
    )


@pytest.fixture
def mock_encrypter():
    encrypter = MagicMock(spec=Encrypter)
    encrypter.encrypt = AsyncMock(return_value="encrypted_text")
    encrypter.decrypt = AsyncMock(return_value="decrypted_text")
    return encrypter


@pytest.fixture
def text_message_service(mock_encrypter):
    return TextMessageService(encrypter=mock_encrypter, max_chars=10000)


@pytest.fixture
def mock_storage():
    storage = MagicMock(spec=StorageAPI)
    storage.upload_file = AsyncMock(return_value=(True, "https://example.com/media/test.jpg"))
    storage.unload_file = AsyncMock(return_value=True)
    return storage


@pytest.fixture
def media_utils():
    return MediaUtils()


@pytest.fixture
def media_validator():
    return MediaValidator()


@pytest.fixture
def media_message_service(mock_storage, media_utils, media_validator):
    return MediaMessageService(
        storage=mock_storage,
        media_utils=media_utils,
        validator=media_validator
    )
