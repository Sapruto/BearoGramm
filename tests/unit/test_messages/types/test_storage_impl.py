import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from src.modules.messages.types.media.core.storages.storage_impl import StorageImpl


@pytest.mark.unit
class TestStorageImpl:
    @pytest.fixture
    def storage_impl(self):
        with patch('src.modules.messages.types.media.core.storages.storage_impl.Path.mkdir'):
            with patch('src.modules.messages.types.media.core.storages.storage_impl.os.getenv') as mock_getenv:
                mock_getenv.return_value = "uploads"
                return StorageImpl()

    @pytest.mark.asyncio
    async def test_upload_local(self, storage_impl):
        with patch('src.modules.messages.types.media.core.storages.storage_impl.open') as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = await storage_impl._upload_local(b"test content", "test.jpg")

            assert result[0] is True
            assert "/media/" in result[1]

    @pytest.mark.asyncio
    async def test_delete_local_not_found(self, storage_impl):
        mock_path = MagicMock()
        mock_path.exists.return_value = False

        with patch('src.modules.messages.types.media.core.storages.storage_impl.Path') as mock_path_class:
            mock_path_class.return_value = mock_path

            result = await storage_impl._delete_local("test.jpg")

            assert result is False

    @pytest.mark.asyncio
    async def test_delete_local_exception(self, storage_impl):
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.unlink.side_effect = Exception("Delete error")

        with patch('src.modules.messages.types.media.core.storages.storage_impl.Path') as mock_path_class:
            mock_path_class.return_value = mock_path

            result = await storage_impl._delete_local("test.jpg")

            assert result is False

    @pytest.mark.asyncio
    async def test_upload_s3(self, storage_impl):
        with patch.dict('os.environ', {
            'USE_S3': 'true',
            'S3_ENDPOINT': 'https://s3.test.com',
            'S3_ACCESS_KEY': 'test_key',
            'S3_SECRET_KEY': 'test_secret',
            'S3_BUCKET_NAME': 'test_bucket',
            'S3_REGION': 'ru1'
        }):
            with patch('src.modules.messages.types.media.core.storages.storage_impl.boto3.client') as mock_client:
                mock_s3 = MagicMock()
                mock_s3.put_object = MagicMock(return_value={})
                mock_client.return_value = mock_s3

                impl = StorageImpl()
                impl.use_s3 = True
                impl.s3_client = mock_s3

                result = await impl._upload_to_s3(b"test", "test.jpg")

                assert result[0] is True
                assert "test_bucket" in result[1]

    @pytest.mark.asyncio
    async def test_delete_s3_success(self, storage_impl):
        mock_s3 = MagicMock()
        mock_s3.delete_object = MagicMock(return_value={})
        storage_impl.s3_client = mock_s3
        storage_impl.use_s3 = True

        result = await storage_impl._delete_from_s3("test.jpg")

        assert result is True
        mock_s3.delete_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_s3_exception(self, storage_impl):
        mock_s3 = MagicMock()
        mock_s3.delete_object = MagicMock(side_effect=Exception("S3 error"))
        storage_impl.s3_client = mock_s3
        storage_impl.use_s3 = True

        result = await storage_impl._delete_from_s3("test.jpg")

        assert result is False

    @pytest.mark.asyncio
    async def test_file_exists_s3(self, storage_impl):
        mock_s3 = MagicMock()
        mock_s3.head_object = MagicMock(return_value={})
        storage_impl.s3_client = mock_s3
        storage_impl.use_s3 = True

        result = await storage_impl._s3_file_exists("test.jpg")

        assert result is True

    @pytest.mark.asyncio
    async def test_file_exists_s3_not_found(self, storage_impl):
        mock_s3 = MagicMock()
        mock_s3.head_object = MagicMock(side_effect=Exception("Not found"))
        storage_impl.s3_client = mock_s3
        storage_impl.use_s3 = True

        result = await storage_impl._s3_file_exists("test.jpg")

        assert result is False

    @pytest.mark.asyncio
    async def test_upload_file_local(self, storage_impl):
        storage_impl.use_s3 = False
        storage_impl._upload_local = AsyncMock(return_value=(True, "/media/test.jpg"))

        result = await storage_impl.upload_file(b"test", "test.jpg")

        assert result[0] is True
        storage_impl._upload_local.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_file_s3(self, storage_impl):
        storage_impl.use_s3 = True
        storage_impl.s3_client = MagicMock()
        storage_impl._upload_to_s3 = AsyncMock(return_value=(True, "https://s3.com/test.jpg"))

        result = await storage_impl.upload_file(b"test", "test.jpg")

        assert result[0] is True
        storage_impl._upload_to_s3.assert_called_once()

    @pytest.mark.asyncio
    async def test_unload_file_local(self, storage_impl):
        storage_impl.use_s3 = False
        storage_impl._delete_local = AsyncMock(return_value=True)

        result = await storage_impl.unload_file("test.jpg")

        assert result is True
        storage_impl._delete_local.assert_called_once()

    @pytest.mark.asyncio
    async def test_unload_file_s3(self, storage_impl):
        storage_impl.use_s3 = True
        storage_impl.s3_client = MagicMock()
        storage_impl._delete_from_s3 = AsyncMock(return_value=True)

        result = await storage_impl.unload_file("test.jpg")

        assert result is True
        storage_impl._delete_from_s3.assert_called_once()

    @pytest.mark.asyncio
    async def test_file_exists_local_call(self, storage_impl):
        storage_impl.use_s3 = False
        storage_impl._local_file_exists = AsyncMock(return_value=True)

        result = await storage_impl.file_exists("test.jpg")

        assert result is True
        storage_impl._local_file_exists.assert_called_once()

    @pytest.mark.asyncio
    async def test_file_exists_s3_call(self, storage_impl):
        storage_impl.use_s3 = True
        storage_impl.s3_client = MagicMock()
        storage_impl._s3_file_exists = AsyncMock(return_value=True)

        result = await storage_impl.file_exists("test.jpg")

        assert result is True
        storage_impl._s3_file_exists.assert_called_once()

    def test_get_file_url_s3(self, storage_impl):
        storage_impl.use_s3 = True
        storage_impl.bucket_name = "test_bucket"
        storage_impl.endpoint_url = "https://s3.test.com"

        url = storage_impl.get_file_url("test.jpg")

        assert "test_bucket" in url
        assert "test.jpg" in url

    def test_get_file_url_local(self, storage_impl):
        storage_impl.use_s3 = False

        url = storage_impl.get_file_url("test.jpg")

        assert url == "/media/test.jpg"

    def test_get_storage_impl(self):
        with patch('src.modules.messages.types.media.core.storages.storage_impl.StorageImpl') as mock_impl:
            from src.modules.messages.types.media.core.storages.storage_impl import get_storage_impl
            get_storage_impl()
            mock_impl.assert_called_once()
