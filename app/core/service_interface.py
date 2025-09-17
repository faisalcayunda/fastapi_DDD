from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar
from uuid import UUID

from app.domain.interfaces.repository_interface import IRepository

from ..models.base_model import Base

ModelType = TypeVar("ModelType", bound=Base)
RepositoryType = TypeVar("RepositoryType", bound=IRepository)


class IService(Generic[ModelType, RepositoryType], ABC):
    """Base Service Interface."""

    @abstractmethod
    async def find_by_id(self, id: UUID) -> ModelType:
        """Find by ID."""
        pass

    @abstractmethod
    async def find_all(
        self,
        filters: Optional[List[Any]] = None,
        sort: Optional[List[Any]] = None,
        search: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[ModelType], int]:
        """Find all records."""
        pass

    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> ModelType:
        """Create new record."""
        pass

    @abstractmethod
    async def update(self, id: UUID, data: Dict[str, Any]) -> ModelType:
        """Update existing record."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete record."""
        pass

    @abstractmethod
    async def exists_by_id(self, id: UUID) -> bool:
        """Check if record exists."""
        pass
