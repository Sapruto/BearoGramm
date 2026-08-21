import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from logging import getLogger

import os
from dotenv import load_dotenv, find_dotenv

env_path = find_dotenv()
if not env_path:
    raise FileNotFoundError("Not found .env")
load_dotenv(dotenv_path=env_path)

logger = getLogger(__name__)

secret_key_jwt = os.getenv("JWT_SECRET_KEY")
if not secret_key_jwt:
    raise ValueError("JWT_SECRET_KEY not set in .env")

class TokenService:
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secret_key_jwt
        self.algorithm_type = "HS256"
        self.token_live_time_expire_minuts = 60 * 24

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
