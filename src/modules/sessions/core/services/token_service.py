import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from src.core.logger import get_logger
from src.core.settings import Settings

logger = get_logger(__name__)

class TokenService:
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or Settings.JWT.SECRET_KEY
        self.algorithm_type = Settings.JWT.ALGORITHM
        self.token_live_time_expire_minuts = Settings.JWT.EXPIRE_MINUTES

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.token_live_time_expire_minuts)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm_type)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm_type])
            return payload

        except jwt.ExpiredSignatureError as e:
            logger.error(e)
            return None

        except jwt.InvalidTokenError as e:
            logger.error(e)
            return None

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm_type], options={"verify_exp": False})

        except Exception as e:
            logger.error(e)
            return None

def get_token_service() -> TokenService:
    return TokenService()
