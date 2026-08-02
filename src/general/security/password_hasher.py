import hashlib
import asyncio
from src.core.logger import get_logger

logger = get_logger(__name__)

class PasswordHasher:
    def __init__(self):
        self.iterations = 670000

    def _pbkdf2_hash(self, password: str, salt_hex: str) -> str:
        salt = bytes.fromhex(salt_hex)
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            self.iterations
        )
        return hashed.hex()

    async def hash_password(self, password: str, salt_hex: str) -> str:
        return await asyncio.to_thread(self._pbkdf2_hash, password, salt_hex)

    async def verify_password(self, password: str, stored_hash: str, stored_salt: str) -> bool:
        try:
            new_hash = await asyncio.to_thread(self._pbkdf2_hash, password, stored_salt)
            return new_hash == stored_hash
        except Exception as e:
            logger.error(f"Invalid salt format for user: {e}")
            return False