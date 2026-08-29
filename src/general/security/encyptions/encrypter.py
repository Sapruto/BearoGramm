import os
import base64
import secrets
import json
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

import asyncio

from src.core.settings import Settings
from src.core.logger import get_logger

logger = get_logger(__name__)

class EncryptionMetadata(BaseModel):
    key_id: str
    salt: Optional[str] = None
    nonce: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class KeyConfig(BaseModel):
    key_id: str
    master_key_b64: str
    salt_b64: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    iterations: int = 600000
    is_active: bool = True

    @property
    def master_key(self) -> bytes:
        return base64.b64decode(self.master_key_b64)

    @property
    def salt(self) -> Optional[bytes]:
        if self.salt_b64:
            return base64.b64decode(self.salt_b64)
        return None

    model_config = {"json_encoders": {
            bytes: lambda v: base64.b64encode(v).decode('utf-8')
        }
    }

class EncryptedData(BaseModel):
    data: str
    metadata: EncryptionMetadata

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> 'EncryptedData':
        return cls.model_validate_json(json_str)

class Encrypter:
    def __init__(self, keys_config: Optional[Dict[str, Union[str, bytes]]] = None, default_key_id: Optional[str] = None, encrypted_fields: Optional[List[str]] = None, salt_length: int = 32, nonce_length: int = 12, iterations: int = 600000, enable_rotation: bool = True):
        self.salt_length = salt_length
        self.nonce_length = nonce_length
        self.iterations = iterations
        self.enable_rotation = enable_rotation
        self.encrypted_fields = encrypted_fields or []

        self._keys: Dict[str, KeyConfig] = {}
        self._ciphers: Dict[str, AESGCM] = {}
        self._default_key_id = default_key_id

        if keys_config:
            self._load_keys(keys_config)
        else:
            self._load_keys_from_env()

        if not self._keys:
            self._generate_default_key()

        if not self._default_key_id:
            self._default_key_id = list(self._keys.keys())[0]

        logger.info(
            f"SecureEncrypter initialized with {len(self._keys)} keys, "
            f"default: {self._default_key_id}, rotation: {enable_rotation}"
        )

    def _load_keys(self, keys_config: Dict[str, Union[str, bytes]]):
        for key_id, master_key in keys_config.items():
            if isinstance(master_key, str):
                try:
                    master_key_b64 = master_key
                    master_key_bytes = base64.b64decode(master_key)
                except Exception:
                    master_key_b64 = base64.b64encode(master_key.encode('utf-8')).decode('utf-8')
                    master_key_bytes = master_key.encode('utf-8')
            else:
                master_key_b64 = base64.b64encode(master_key).decode('utf-8')
                master_key_bytes = master_key

            salt = os.urandom(self.salt_length)
            salt_b64 = base64.b64encode(salt).decode('utf-8')

            derived_key = self._derive_key(master_key_bytes, salt)

            self._keys[key_id] = KeyConfig(
                key_id=key_id,
                master_key_b64=master_key_b64,
                salt_b64=salt_b64,
                iterations=self.iterations
            )
            self._ciphers[key_id] = AESGCM(derived_key)

    def _load_keys_from_env(self):
        master_key = Settings.ENCRYPTER.MASTER_KEY
        if master_key:
            self._load_keys({"default": master_key})

        rotation_keys = Settings.ENCRYPTER.ROTATION_KEYS
        if rotation_keys:
            try:
                keys_dict = json.loads(rotation_keys)
                self._load_keys(keys_dict)
            except json.JSONDecodeError:
                logger.warning("Invalid ROTATION_KEYS format, skipping")

    def _generate_default_key(self):
        key_id = f"key_{int(datetime.now().timestamp())}"
        master_key = secrets.token_bytes(32)
        master_key_b64 = base64.b64encode(master_key).decode('utf-8')
        salt = os.urandom(self.salt_length)
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        derived_key = self._derive_key(master_key, salt)

        self._keys[key_id] = KeyConfig(
            key_id=key_id,
            master_key_b64=master_key_b64,
            salt_b64=salt_b64,
            iterations=self.iterations
        )
        self._ciphers[key_id] = AESGCM(derived_key)
        self._default_key_id = key_id

        logger.warning(
            f"NEW KEY GENERATED! Save these values:\n"
            f"MASTER_KEY_{key_id.upper()}={master_key_b64}\n"
            f"SALT_{key_id.upper()}={salt_b64}"
        )

    def _derive_key(self, master_key: bytes, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.iterations,
            backend=default_backend()
        )
        return kdf.derive(master_key)

    def _generate_nonce(self) -> bytes:
        return os.urandom(self.nonce_length)

    async def _decrypt_legacy(self, to_decrypt: str) -> Optional[str]:
        try:
            encrypted_data = base64.b64decode(to_decrypt.encode('utf-8'))
            nonce = base64.b64decode(Settings.ENCRYPTER.ENCRYPT_NONCE)
            if len(nonce) != 12:
                raise ValueError("Invalid nonce length")

            cipher = self._ciphers[self._default_key_id]
            result = await asyncio.to_thread(
                cipher.decrypt,
                nonce,
                encrypted_data,
                None
            )
            return result.decode('utf-8')

        except Exception as e:
            logger.error(f"Legacy decryption failed: {e}")
            raise

    async def encrypt(self, to_encrypt: Any, key_id: Optional[str] = None, use_salt: bool = True) -> Optional[str]:
        if to_encrypt is None:
            return None

        if not isinstance(to_encrypt, str):
            to_encrypt = str(to_encrypt)

        key_id = key_id or self._default_key_id
        if key_id not in self._ciphers:
            raise ValueError(f"Key '{key_id}' not found")

        cipher = self._ciphers[key_id]
        key_config = self._keys[key_id]

        nonce = self._generate_nonce()

        encrypted_data = await asyncio.to_thread(
            cipher.encrypt,
            nonce,
            to_encrypt.encode('utf-8'),
            None
        )

        metadata = EncryptionMetadata(
            key_id=key_id,
            salt=key_config.salt_b64 if use_salt else None,
            nonce=base64.b64encode(nonce).decode('utf-8')
        )

        encrypted_package = EncryptedData(
            data=base64.b64encode(encrypted_data).decode('utf-8'),
            metadata=metadata
        )

        return base64.b64encode(
            encrypted_package.to_json().encode('utf-8')
        ).decode('utf-8')

    async def decrypt(self, to_decrypt: Any) -> Optional[str]:
        if to_decrypt is None:
            return None

        if not isinstance(to_decrypt, str):
            to_decrypt = str(to_decrypt)

        try:
            json_data = base64.b64decode(to_decrypt.encode('utf-8'))
            encrypted_package = EncryptedData.model_validate_json(json_data.decode('utf-8'))

            key_id = encrypted_package.metadata.key_id
            if key_id not in self._ciphers:
                raise ValueError(f"Key '{key_id}' not found for decryption")

            cipher = self._ciphers[key_id]

            encrypted_data = base64.b64decode(
                encrypted_package.data.encode('utf-8')
            )
            nonce = base64.b64decode(
                encrypted_package.metadata.nonce.encode('utf-8')
            )

            result = await asyncio.to_thread(
                cipher.decrypt,
                nonce,
                encrypted_data,
                None
            )

            return result.decode('utf-8')

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return await self._decrypt_legacy(to_decrypt)

    async def encrypt_field( self, value: Any, key_id: Optional[str] = None) -> Optional[str]:
        if value is None:
            return None
        return await self.encrypt(value, key_id)

    async def decrypt_field(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        return await self.decrypt(value)

    async def encrypt_sensitive_data(self, data: Dict, encrypt_fields: Optional[List[str]] = None, key_id: Optional[str] = None) -> Dict:
        encrypt_fields = encrypt_fields or self.encrypted_fields
        result = data.copy()

        for field in encrypt_fields:
            if field in result and result[field] is not None:
                result[field] = await self.encrypt_field(result[field], key_id)

        return result

    async def decrypt_sensitive_data(self, data: Dict, decrypt_fields: Optional[List[str]] = None) -> Dict:
        decrypt_fields = decrypt_fields or self.encrypted_fields
        result = data.copy()

        for field in decrypt_fields:
            if field in result and result[field] is not None:
                try:
                    result[field] = await self.decrypt_field(result[field])
                except Exception as e:
                    logger.warning(f"Failed to decrypt {field}: {e}")
                    result[field] = None

        return result

    def add_key(self, master_key: Union[str, bytes], key_id: Optional[str] = None) -> str:
        if key_id is None:
            key_id = f"key_{int(datetime.now().timestamp())}"

        self._load_keys({key_id: master_key})

        if self.enable_rotation:
            logger.info(f"New key added: {key_id}")

        return key_id

    def rotate_default_key(self, new_key_id: Optional[str] = None):
        if new_key_id and new_key_id in self._keys:
            self._default_key_id = new_key_id
        else:
            key_id = self.add_key(secrets.token_bytes(32))
            self._default_key_id = key_id

        logger.info(f"Default key rotated to: {self._default_key_id}")

    async def migrate_data(self, encrypted_data: str) -> str:
        decrypted = await self.decrypt(encrypted_data)

        return await self.encrypt(decrypted)

_encrypter_instance: Optional[Encrypter] = None

def get_encrypter() -> Encrypter:
    global _encrypter_instance
    if _encrypter_instance is None:
        _encrypter_instance = Encrypter()
    return _encrypter_instance

class GenerateKeyPairResult(BaseModel):
    master_key: str
    encrypt_salt: str
    nonce_length: int
    iterations: int

def generate_key_pair() -> GenerateKeyPairResult:
    master_key = secrets.token_bytes(32)
    salt = os.urandom(32)

    return GenerateKeyPairResult(
        master_key=base64.b64encode(master_key).decode('utf-8'),
        encrypt_salt=base64.b64encode(salt).decode('utf-8'),
        nonce_length=12,
        iteration=600000
    )
