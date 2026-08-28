import pytest
from unittest.mock import AsyncMock, MagicMock

from src.modules.messages.types.media.core.storages.storage_api import StorageAPI
from src.modules.messages.types.media.core.storages.storage_impl import StorageImpl


@pytest.mark.unit
class TestStorageAPI:
    @pytest.mark.asyncio
    async def test_upload_file(self):
        mock_impl = MagicMock(spec=StorageImpl)
        mock_impl.upload_file = AsyncMock(return_value=(True, "https://example.com/test.jpg"))

        api = StorageAPI(storage_impl=mock_impl)
        result = await api.upload_file(b"content", "test.jpg")

        assert result == (True, "https://example.com/test.jpg")
        mock_impl.upload_file.assert_called_once_with(b"content", "test.jpg", None)

    @pytest.mark.asyncio
    async def test_unload_file(self):
        mock_impl = MagicMock(spec=StorageImpl)
        mock_impl.unload_file = AsyncMock(return_value=True)

        api = StorageAPI(storage_impl=mock_impl)
        result = await api.unload_file("test.jpg")

        assert result is True
        mock_impl.unload_file.assert_called_once_with("test.jpg")

    def test_get_storage_api(self):
        from src.modules.messages.types.media.core.storages.storage_api import get_storage_api
        api = get_storage_api()
        assert isinstance(api, StorageAPI)
