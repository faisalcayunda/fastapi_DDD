# app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import HTTPException
from jose import ExpiredSignatureError, JWTError, jwt
from pytz import timezone

from app.core.config import app_settings as settings


def create_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None, token_type: str = "access"
) -> str:
    """Buat JWT token."""
    if expires_delta:
        expire = datetime.now(timezone(settings.TIMEZONE)) + expires_delta
    else:
        if token_type == "access":
            expire = datetime.now(timezone(settings.TIMEZONE)) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        elif token_type == "refresh":
            expire = datetime.now(timezone(settings.TIMEZONE)) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            expire = datetime.now(timezone(settings.TIMEZONE)) + timedelta(minutes=15)

    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone(settings.TIMEZONE)),
        "sub": str(subject),
        "type": token_type,
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def create_access_token(subject: Union[str, Any]) -> str:
    """Buat access token."""
    return create_token(subject, token_type="access")


def create_refresh_token(subject: Union[str, Any]) -> str:
    """Buat refresh token."""
    return create_token(subject, token_type="refresh")


def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
            },
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
