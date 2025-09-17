import re
from typing import Tuple

from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import ValidationException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    Returns tuple of (is_valid, error_message).
    """
    if len(password) < settings.security.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {settings.security.PASSWORD_MIN_LENGTH} characters long"

    if len(password) > settings.security.PASSWORD_MAX_LENGTH:
        return False, f"Password must be at most {settings.security.PASSWORD_MAX_LENGTH} characters long"

    if settings.security.PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if settings.security.PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if settings.security.PASSWORD_REQUIRE_DIGITS and not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    if settings.security.PASSWORD_REQUIRE_SPECIAL and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"

    return True, ""


def validate_and_hash_password(password: str) -> str:
    """Validate password strength and hash it."""
    is_valid, error = validate_password(password)
    if not is_valid:
        raise ValidationException(error)
    return hash_password(password)
