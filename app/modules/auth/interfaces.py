from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IAuth(ABC):
    """Authentication interface."""

    @abstractmethod
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token."""
        pass

    @abstractmethod
    async def create_access_token(self, subject: str, claims: Optional[Dict[str, Any]] = None) -> str:
        """Create access token."""
        pass

    @abstractmethod
    async def create_refresh_token(self, subject: str) -> str:
        """Create refresh token."""
        pass

    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """Hash password."""
        pass

    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        pass

    @abstractmethod
    async def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength."""
        pass
