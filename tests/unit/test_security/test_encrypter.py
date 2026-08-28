import pytest
import os
import base64
import json
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone

from src.general.security.encyptions.encrypter import (
    Encrypter,
    EncryptionMetadata,
    KeyConfig,
    EncryptedData,
    generate_key_pair,
    get_encrypter
)


@pytest.mark.unit
class TestEncryptionMetadata:
    def test_metadata_creation(self):
        metadata = EncryptionMetadata(
            key_id="test_key",
            nonce="test_nonce"
        )
        assert metadata.key_id == "test_key"
        assert metadata.nonce == "test_nonce"
        assert metadata.salt is None
        assert metadata.timestamp is not None

    def test_metadata_with_salt(self):
        metadata = EncryptionMetadata(
            key_id="test_key",
            salt="test_salt",
            nonce="test_nonce"
        )
        assert metadata.salt == "test_salt"


@pytest.mark.unit
class TestKeyConfig:
    def test_key_config_creation(self):
        config = KeyConfig(
            key_id="test_key",
            master_key_b64="dGVzdF9rZXk=",
            iterations=600000
        )
        assert config.key_id == "test_key"
        assert config.master_key_b64 == "dGVzdF9rZXk="
        assert config.iterations == 600000
        assert config.is_active is True

    def test_master_key_property(self):
        config = KeyConfig(
            key_id="test_key",
            master_key_b64="dGVzdF9rZXk="
        )
        assert config.master_key == b"test_key"

    def test_salt_property(self):
        config = KeyConfig(
            key_id="test_key",
            master_key_b64="dGVzdF9rZXk=",
            salt_b64="dGVzdF9zYWx0"
        )
        assert config.salt == b"test_salt"


@pytest.mark.unit
class TestEncryptedData:
    def test_encrypted_data_creation(self):
        metadata = EncryptionMetadata(key_id="test", nonce="nonce")
        data = EncryptedData(data="encrypted", metadata=metadata)
        assert data.data == "encrypted"
        assert data.metadata == metadata

    def test_to_json(self):
        metadata = EncryptionMetadata(key_id="test", nonce="nonce")
        data = EncryptedData(data="encrypted", metadata=metadata)
        json_str = data.to_json()
        assert isinstance(json_str, str)
        assert "encrypted" in json_str

    def test_from_json(self):
        metadata = EncryptionMetadata(key_id="test", nonce="nonce")
        original = EncryptedData(data="encrypted", metadata=metadata)
        json_str = original.to_json()
        restored = EncryptedData.from_json(json_str)
        assert restored.data == original.data
        assert restored.metadata.key_id == original.metadata.key_id


@pytest.mark.unit
class TestEncrypter:
    @pytest.fixture
    def encrypter(self):
        with patch.dict('os.environ', {'MASTER_KEY': base64.b64encode(b"test_master_key_32_bytes").decode('utf-8')}):
            return Encrypter()

    @pytest.fixture
    def encrypter_with_keys(self):
        master_key = base64.b64encode(b"test_master_key_32_bytes").decode('utf-8')
        return Encrypter(keys_config={"default": master_key})

    @pytest.mark.asyncio
    async def test_encrypt_decrypt(self, encrypter):
        original = "Hello World"
        encrypted = await encrypter.encrypt(original)
        assert encrypted is not None
        assert encrypted != original
        decrypted = await encrypter.decrypt(encrypted)
        assert decrypted == original

    @pytest.mark.asyncio
    async def test_encrypt_none(self, encrypter):
        result = await encrypter.encrypt(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_encrypt_non_string(self, encrypter):
        result = await encrypter.encrypt(123)
        assert result is not None
        decrypted = await encrypter.decrypt(result)
        assert decrypted == "123"

    @pytest.mark.asyncio
    async def test_encrypt_with_key_id(self, encrypter_with_keys):
        original = "Hello World"
        encrypted = await encrypter_with_keys.encrypt(original, key_id="default")
        assert encrypted is not None
        decrypted = await encrypter_with_keys.decrypt(encrypted)
        assert decrypted == original

    @pytest.mark.asyncio
    async def test_encrypt_invalid_key(self, encrypter):
        with pytest.raises(ValueError):
            await encrypter.encrypt("test", key_id="invalid_key")

    @pytest.mark.asyncio
    async def test_decrypt_invalid_data(self, encrypter):
        with pytest.raises(Exception):
            await encrypter.decrypt("invalid_data")

    @pytest.mark.asyncio
    async def test_encrypt_field(self, encrypter):
        result = await encrypter.encrypt_field("Hello World")
        assert result is not None
        decrypted = await encrypter.decrypt_field(result)
        assert decrypted == "Hello World"

    @pytest.mark.asyncio
    async def test_encrypt_field_none(self, encrypter):
        result = await encrypter.encrypt_field(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_decrypt_field_none(self, encrypter):
        result = await encrypter.decrypt_field(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_encrypt_sensitive_data(self, encrypter):
        data = {
            "id": "1",
            "name": "John",
            "email": "john@example.com",
            "phone": "123456"
        }
        encrypted_data = await encrypter.encrypt_sensitive_data(
            data,
            encrypt_fields=["email", "phone"]
        )
        assert encrypted_data["id"] == "1"
        assert encrypted_data["name"] == "John"
        assert encrypted_data["email"] != "john@example.com"
        assert encrypted_data["phone"] != "123456"

    @pytest.mark.asyncio
    async def test_encrypt_sensitive_data_empty_fields(self, encrypter):
        data = {"id": "1", "name": "John"}
        encrypted_data = await encrypter.encrypt_sensitive_data(data)
        assert encrypted_data == data

    @pytest.mark.asyncio
    async def test_decrypt_sensitive_data(self, encrypter):
        data = {"id": "1", "name": "John"}
        encrypted_data = await encrypter.encrypt_sensitive_data(
            data,
            encrypt_fields=["name"]
        )
        decrypted_data = await encrypter.decrypt_sensitive_data(
            encrypted_data,
            decrypt_fields=["name"]
        )
        assert decrypted_data["id"] == "1"
        assert decrypted_data["name"] == "John"

    @pytest.mark.asyncio
    async def test_decrypt_sensitive_data_no_fields(self, encrypter):
        data = {"id": "1", "name": "John"}
        result = await encrypter.decrypt_sensitive_data(data)
        assert result == data

    def test_add_key(self, encrypter):
        new_key = base64.b64encode(b"new_master_key_32_bytes").decode('utf-8')
        key_id = encrypter.add_key(new_key)
        assert key_id in encrypter._keys
        assert key_id in encrypter._ciphers

    def test_add_key_with_id(self, encrypter):
        new_key = base64.b64encode(b"new_master_key_32_bytes").decode('utf-8')
        key_id = encrypter.add_key(new_key, "custom_key")
        assert key_id == "custom_key"
        assert key_id in encrypter._keys

    def test_rotate_default_key(self, encrypter):
        old_default = encrypter._default_key_id
        encrypter.rotate_default_key()
        assert encrypter._default_key_id != old_default

    def test_rotate_default_key_to_existing(self, encrypter):
        encrypter.add_key(
            base64.b64encode(b"new_master_key_32_bytes").decode('utf-8'),
            "new_key"
        )
        encrypter.rotate_default_key("new_key")
        assert encrypter._default_key_id == "new_key"

    @pytest.mark.asyncio
    async def test_migrate_data(self, encrypter):
        original = "Hello World"
        encrypted = await encrypter.encrypt(original)
        migrated = await encrypter.migrate_data(encrypted)
        assert migrated != encrypted
        decrypted = await encrypter.decrypt(migrated)
        assert decrypted == original

    def test_get_encrypter(self):
        encrypter = get_encrypter()
        assert isinstance(encrypter, Encrypter)

    @patch.dict('os.environ', {})
    def test_encrypter_generates_default_key(self):
        encrypter = Encrypter()
        assert len(encrypter._keys) >= 1
        assert encrypter._default_key_id is not None

    @patch.dict('os.environ', {'MASTER_KEY': base64.b64encode(b"test_key").decode('utf-8')})
    def test_encrypter_loads_from_env(self):
        encrypter = Encrypter()
        assert "default" in encrypter._keys

    @patch.dict('os.environ', {
        'MASTER_KEY': base64.b64encode(b"test_key").decode('utf-8'),
        'ROTATION_KEYS': json.dumps({"rot1": base64.b64encode(b"rot_key").decode('utf-8')})
    })
    def test_encrypter_loads_rotation_keys(self):
        encrypter = Encrypter()
        assert "default" in encrypter._keys
        assert "rot1" in encrypter._keys

    @pytest.mark.asyncio
    async def test_encrypt_without_salt(self, encrypter):
        original = "Hello World"
        encrypted = await encrypter.encrypt(original, use_salt=False)
        assert encrypted is not None
        decrypted = await encrypter.decrypt(encrypted)
        assert decrypted == original

    @pytest.mark.asyncio
    async def test_encrypted_data_structure(self, encrypter):
        original = "Hello World"
        encrypted = await encrypter.encrypt(original)

        json_data = base64.b64decode(encrypted.encode('utf-8'))
        encrypted_package = EncryptedData.model_validate_json(json_data.decode('utf-8'))

        assert encrypted_package.data is not None
        assert encrypted_package.metadata.key_id is not None
        assert encrypted_package.metadata.nonce is not None

    @pytest.mark.asyncio
    async def test_encrypt_sensitive_data_with_default_fields(self, encrypter):
        encrypter.encrypted_fields = ["email", "phone"]
        data = {
            "id": "1",
            "name": "John",
            "email": "john@example.com",
            "phone": "123456"
        }
        encrypted_data = await encrypter.encrypt_sensitive_data(data)
        assert encrypted_data["email"] != "john@example.com"
        assert encrypted_data["phone"] != "123456"

    def test_key_config_encoders(self):
        config = KeyConfig(
            key_id="test",
            master_key_b64=base64.b64encode(b"test").decode('utf-8')
        )
        json_data = config.model_dump_json()
        assert "master_key_b64" in json_data
