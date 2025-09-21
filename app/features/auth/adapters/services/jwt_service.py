from datetime import datetime, timedelta
from typing import List, Optional

from jose import JWTError, jwt
from pytz import timezone

from app.features.auth.entities.user import User
from app.features.auth.use_cases.ports import TokenService
from app.platform.config import app_settings, security_settings


class JWTService(TokenService):
    def __init__(self):
        self.app_settings = app_settings
        self.security_settings = security_settings

    def issue_access(self, user: User, scopes: Optional[List[str]] = None) -> str:
        now = datetime.now(timezone(self.app_settings.TIMEZONE))
        expire = now + timedelta(minutes=self.security_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user.id,
            "iat": now,
            "exp": expire,
            "type": "access",
        }
        if scopes:
            payload["scopes"] = scopes
        return jwt.encode(
            payload,
            self.security_settings.SECRET_KEY,
            algorithm=self.security_settings.ALGORITHM,
        )

    def issue_refresh(self, user: User) -> str:
        now = datetime.now(timezone(self.app_settings.TIMEZONE))
        expire = now + timedelta(days=self.security_settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": user.id,
            "iat": now,
            "exp": expire,
            "type": "refresh",
        }
        return jwt.encode(
            payload,
            self.security_settings.SECRET_KEY,
            algorithm=self.security_settings.ALGORITHM,
        )

    def parse(self, token: str):
        try:
            return jwt.decode(
                token,
                self.security_settings.SECRET_KEY,
                algorithms=[self.security_settings.ALGORITHM],
            )
        except JWTError:
            return None
