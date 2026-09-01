import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv
from .paths import PROJECT_ROOT, CONFIG_ROOT

load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


class ConfigLoader:
    def __init__(self, config_dir: Path = CONFIG_ROOT):
        self.config_dir = config_dir
        self._cache: Dict[str, Dict[str, Any]] = {}

    def load_config(self, config_name: str) -> Dict[str, Any]:
        if config_name in self._cache:
            return self._cache[config_name]
        config_path = self.config_dir / f"{config_name}.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            self._cache[config_name] = config
            return config

    def load_merged_configs(self, env: str = "development") -> Dict[str, Any]:
        merged = {}
        try:
            merged.update(self.load_config("default"))
        except FileNotFoundError:
            pass
        try:
            merged.update(self.load_config(env))
        except FileNotFoundError:
            pass
        try:
            merged.update(self.load_config("local"))
        except FileNotFoundError:
            pass
        return merged


config_loader = ConfigLoader()


class RedisSettings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    model_config = {"extra": "ignore"}


class DatabaseSettings(BaseSettings):
    SQL_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 3600
    INIT_DB: bool = False
    DATABASE_URL: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None

    model_config = {"extra": "ignore"}


class Boto3Settings(BaseSettings):
    USE_S3: bool = False
    S3_ENDPOINT: str = "https://s3.ru1.storage.beget.cloud"
    S3_BUCKET_NAME: str = "your-bucket"
    S3_REGION: str = "ru1"
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None

    model_config = {"extra": "ignore"}


class MediaStorageSettings(BaseSettings):
    UPLOAD_DIR: Path = Path("uploads")
    BOTO_3: Boto3Settings = Field(default_factory=Boto3Settings)

    model_config = {"extra": "ignore"}


class AppSettings(BaseSettings):
    APP_NAME: str = "My App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    model_config = {"extra": "ignore"}


class CorsSettings(BaseSettings):
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_METHODS: List[str] = ["*"]
    ALLOWED_HEADERS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True

    model_config = {"extra": "ignore"}


class RateLimitSettings(BaseSettings):
    ENABLED: bool = True
    REQUESTS_PER_MINUTE: int = 60
    BURST: int = 10

    model_config = {"extra": "ignore"}


class JWTSettings(BaseSettings):
    SECRET_KEY: Optional[str] = Field(default=None)
    EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"

    model_config = {"extra": "ignore"}


class EncrypterSettings(BaseSettings):
    MASTER_KEY: Optional[str] = None
    ROTATION_KEYS: Optional[str] = None
    ENCRYPT_NONCE: Optional[str] = None

    model_config = {"extra": "ignore"}


class PhoneSettings(BaseSettings):
    HASH_SALT: Optional[str] = Field(default=None)
    ASYNC_CLIENT_API_ID: Optional[str] = None

    model_config = {"extra": "ignore"}


class SettingsModel(BaseSettings):
    ENV: str = "development"
    BASE_URL: str = "http://localhost:8000"
    APP: AppSettings = Field(default_factory=AppSettings)
    CORS: CorsSettings = Field(default_factory=CorsSettings)
    RATE_LIMIT: RateLimitSettings = Field(default_factory=RateLimitSettings)
    REDIS: RedisSettings = Field(default_factory=RedisSettings)
    DATABASE: DatabaseSettings = Field(default_factory=DatabaseSettings)
    MEDIA_STORAGE: MediaStorageSettings = Field(default_factory=MediaStorageSettings)
    JWT: JWTSettings = Field(default_factory=JWTSettings)
    ENCRYPTER: EncrypterSettings = Field(default_factory=EncrypterSettings)
    PHONE: PhoneSettings = Field(default_factory=PhoneSettings)

    @field_validator("BASE_URL")
    @classmethod
    def validate_base_url(cls, v: str, info) -> str:
        v = v.rstrip("/")
        env = info.data.get("ENV", "development")
        if env == "production" and not v:
            raise ValueError("BASE_URL must be set in .env for production")
        return v

    @classmethod
    def load_from_configs(cls, env: Optional[str] = None) -> "SettingsModel":
        env = env or os.getenv("ENV", "development")
        config_data = config_loader.load_merged_configs(env)
        if "JWT" not in config_data:
            config_data["JWT"] = {}
        config_data["JWT"]["SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
        if "PHONE" not in config_data:
            config_data["PHONE"] = {}
        config_data["PHONE"]["HASH_SALT"] = os.getenv("PHONE_HASH_SALT")
        config_data["PHONE"]["ASYNC_CLIENT_API_ID"] = os.getenv(
            "PHONE_ASYNC_CLIENT_API_ID"
        )
        if "REDIS" not in config_data:
            config_data["REDIS"] = {}
        config_data["REDIS"]["REDIS_PASSWORD"] = os.getenv("REDIS_PASSWORD")
        if "DATABASE" not in config_data:
            config_data["DATABASE"] = {}
        config_data["DATABASE"]["DB_USER"] = os.getenv("DATABASE_DB_USER")
        config_data["DATABASE"]["DB_PASSWORD"] = os.getenv("DATABASE_DB_PASSWORD")
        config_data["DATABASE"]["DB_HOST"] = os.getenv("DATABASE_DB_HOST")
        config_data["DATABASE"]["DB_PORT"] = os.getenv("DATABASE_DB_PORT")
        config_data["DATABASE"]["DB_NAME"] = os.getenv("DATABASE_DB_NAME")
        config_data["DATABASE"]["DATABASE_URL"] = os.getenv("DATABASE_DATABASE_URL")
        if "ENCRYPTER" not in config_data:
            config_data["ENCRYPTER"] = {}
        config_data["ENCRYPTER"]["MASTER_KEY"] = os.getenv("MASTER_KEY")
        config_data["ENCRYPTER"]["ENCRYPT_NONCE"] = os.getenv("ENCRYPT_NONCE")
        return cls(**config_data)

    model_config = {
        "extra": "ignore",
        "case_sensitive": True,
    }


Settings = SettingsModel.load_from_configs()
