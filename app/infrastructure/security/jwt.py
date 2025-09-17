from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationFailedException


def create_access_token(
    subject: str, expires_delta: Optional[timedelta] = None, claims: Optional[Dict[str, Any]] = None
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.security.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}

    if claims:
        to_encode.update(claims)

    try:
        encoded_jwt = jwt.encode(to_encode, settings.security.SECRET_KEY, algorithm=settings.security.ALGORITHM)
        return encoded_jwt
    except JWTError as e:
        raise AuthenticationFailedException(f"Failed to create access token: {str(e)}")


def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.security.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}

    try:
        encoded_jwt = jwt.encode(to_encode, settings.security.SECRET_KEY, algorithm=settings.security.ALGORITHM)
        return encoded_jwt
    except JWTError as e:
        raise AuthenticationFailedException(f"Failed to create refresh token: {str(e)}")


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.security.SECRET_KEY, algorithms=[settings.security.ALGORITHM])
        return payload
    except JWTError as e:
        raise AuthenticationFailedException(f"Invalid token: {str(e)}")


def verify_token(token: str) -> bool:
    """Verify if token is valid."""
    try:
        decode_token(token)
        return True
    except AuthenticationFailedException:
        return False
