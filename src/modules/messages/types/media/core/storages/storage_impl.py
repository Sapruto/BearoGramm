from typing import Optional, Tuple
import boto3
from botocore.config import Config

from ..utils.media_utils import MediaUtils

from src.core.settings import Settings
from src.core.logger import get_logger

logger = get_logger(__name__)

class StorageImpl:
    def __init__(self):
        self.media_utils = MediaUtils()
        self.upload_dir = Settings.MEDIA_STORAGE.UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.use_s3 = Settings.MEDIA_STORAGE.BOTO_3.USE_S3
        self.endpoint_url = Settings.MEDIA_STORAGE.BOTO_3.S3_ENDPOINT
        self.access_key = Settings.MEDIA_STORAGE.BOTO_3.S3_ACCESS_KEY
        self.secret_key = Settings.MEDIA_STORAGE.BOTO_3.S3_SECRET_KEY
        self.bucket_name = Settings.MEDIA_STORAGE.BOTO_3.S3_BUCKET_NAME
        self.region = Settings.MEDIA_STORAGE.BOTO_3.S3_REGION

        self.s3_client = None
        if self.use_s3:
            if not self.access_key or not self.secret_key:
                logger.warning("S3 credentials not configured. Falling back to local storage.")
                self.use_s3 = False
            else:
                try:
                    self.s3_client = boto3.client(
                        's3',
                        endpoint_url=self.endpoint_url,
                        aws_access_key_id=self.access_key,
                        aws_secret_access_key=self.secret_key,
                        config=Config(signature_version='s3v4'),
                        region_name=self.region
                    )
                    logger.info("S3 client initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize S3 client: {e}")
                    self.use_s3 = False

    async def _s3_file_exists(self, filename: str) -> bool:
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            return True
        except Exception:
            return False

    async def _local_file_exists(self, filename: str) -> bool:
        file_path = self.upload_dir / filename
        return file_path.exists()

    async def _upload_to_s3(self, file_content: bytes, filename: str, content_type: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        try:
            file_path = self.media_utils.generate_path(filename)

            if not content_type:
                content_type = self.media_utils.get_content_type(filename)

            extra_args = {'ContentType': content_type} if content_type else {}

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file_content,
                **extra_args
            )

            base_url = self.endpoint_url.replace('https://', '').replace('http://', '')
            file_url = f"https://{self.bucket_name}.{base_url}/{file_path}"

            logger.info(f"File uploaded to S3: {file_path}")
            return True, file_url

        except Exception as e:
            logger.error(f"S3 upload error: {e}")
            return False, f"S3 upload failed: {str(e)}"

    async def _delete_from_s3(self, filename: str) -> bool:
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )

            logger.info(f"File deleted from S3: {filename}")
            return True

        except Exception as e:
            logger.error(f"S3 delete error: {e}")
            return False

    async def _upload_local(self, file_content: bytes, filename: str, content_type: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        try:
            file_path = self.media_utils.generate_path(filename)

            full_path = self.upload_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'wb') as f:
                f.write(file_content)

            url = f"/media/{file_path}"
            logger.info(f"File saved locally: {file_path}")

            return True, url

        except Exception as e:
            logger.error(f"Local upload error: {e}")
            return False, f"Local upload failed: {str(e)}"

    async def _delete_local(self, filename: str) -> bool:
        try:
            file_path = self.upload_dir / filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Local file deleted: {filename}")
                return True
            else:
                logger.warning(f"Local file not found: {filename}")
                return False

        except Exception as e:
            logger.error(f"Local delete error: {e}")
            return False

    async def upload_file(self, file_content: bytes, filename: str, content_type: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        if self.use_s3 and self.s3_client:
            return await self._upload_to_s3(file_content, filename, content_type)
        else:
            return await self._upload_local(file_content, filename, content_type)

    async def unload_file(self, filename: str) -> bool:
        if self.use_s3 and self.s3_client:
            return await self._delete_from_s3(filename)
        else:
            return await self._delete_local(filename)

    async def file_exists(self, filename: str) -> bool:
        if self.use_s3 and self.s3_client:
            return await self._s3_file_exists(filename)
        else:
            return await self._local_file_exists(filename)

    def get_file_url(self, file_path: str) -> str:
        if self.use_s3:
            base_url = self.endpoint_url.replace('https://', '').replace('http://', '')
            return f"https://{self.bucket_name}.{base_url}/{file_path}"
        else:
            return f"/media/{file_path}"

def get_storage_impl() -> StorageImpl:
    return StorageImpl()
