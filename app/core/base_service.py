from functools import lru_cache
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union

from sqlalchemy import or_

from app.core.database import Base
from app.core.exceptions import (
    DuplicateValueException,
    NotFoundException,
    UnprocessableEntity,
    ValidationException,
)
from app.repositories import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[ModelType, RepositoryType]):
    """Optimized base service dengan caching dan performance improvements."""

    def __init__(self, model: Type[ModelType], repository: RepositoryType):
        self.model_class = model
        self.repository = repository
        # inspector sebaiknya diakses dari instance repository, bukan class
        if hasattr(self.repository, "inspector"):
            self._valid_columns = set(self.repository.inspector.c.keys())
        else:
            self._valid_columns = set()
        self._has_soft_delete = hasattr(self.model_class, "is_deleted")

    @staticmethod
    @lru_cache(maxsize=256)
    def _parse_filter_item(filter_item: str) -> Tuple[str, str, str]:
        """Cache parsing filter. Mendukung operator '=', '>=', '<='."""
        for op in ("!=", ">=", "<=", "="):
            if op in filter_item:
                try:
                    col, value = filter_item.split(op, 1)
                    return col.strip(), op, value.strip()
                except ValueError:
                    raise ValidationException(f"Invalid filter {filter_item} must be 'name{op}value'")
        raise ValidationException(f"Invalid filter {filter_item}. Must use '=', '>=', or '<=' as separator.")

    @staticmethod
    @lru_cache(maxsize=256)
    def _parse_sort_item(sort_item: str) -> Tuple[str, str]:
        """Cache parsing sort."""
        try:
            col, order = sort_item.split(":", 1)
            return col.strip(), order.strip().lower()
        except ValueError:
            raise ValidationException(f"Invalid sort {sort_item}. Must be 'name:asc' or 'name:desc'")

    def _validate_column(self, col: str) -> None:
        """Validate column dengan cache."""
        if col not in self._valid_columns:
            raise ValidationException(f"Invalid column: {col}")

    def _convert_value(self, col: str, value: str) -> Any:
        """Convert value ke tipe yang sesuai."""
        if col == "id":
            return str(value)

        if isinstance(value, str) and value.lower() in {"true", "false", "t", "f"}:
            return value.lower() in {"true", "t"}

        if isinstance(value, str) and value.isdigit():
            return int(value)

        try:
            return float(value)
        except (ValueError, TypeError):
            return value

    def _build_filters(self, filters: Union[str, List[str], None]) -> List[Any]:
        """Build filters dengan optimization."""
        list_model_filters: List[Any] = []

        # Pastikan filters adalah list
        if filters is None:
            filters = []
        elif isinstance(filters, str):
            filters = [filters]

        # Soft delete: tambahkan filter is_deleted jika ada kolomnya
        if self._has_soft_delete and "is_deleted" not in [
            f.split("=")[0].strip() if isinstance(f, str) else "" for f in filters
        ]:
            filters.append("is_deleted=false")

        for filter_item in filters:
            # Mendukung OR: filter_item bisa berupa list
            if isinstance(filter_item, list):
                or_conditions = []
                for value_item in filter_item:
                    col, operator, value = self._parse_filter_item(value_item)
                    self._validate_column(col)
                    converted_value = self._convert_value(col, value)

                    if isinstance(converted_value, bool):
                        or_conditions.append(getattr(self.model_class, col).is_(converted_value))
                    else:
                        if operator == "=":
                            or_conditions.append(getattr(self.model_class, col) == converted_value)
                        elif operator == "!=":
                            or_conditions.append(getattr(self.model_class, col) != converted_value)
                        elif operator == ">=":
                            or_conditions.append(getattr(self.model_class, col) >= converted_value)
                        elif operator == "<=":
                            or_conditions.append(getattr(self.model_class, col) <= converted_value)
                        else:
                            raise ValidationException(f"Invalid operator '{operator}' for {col}")
                if or_conditions:
                    list_model_filters.append(or_(*or_conditions))
            else:
                col, operator, value = self._parse_filter_item(filter_item)
                self._validate_column(col)
                converted_value = self._convert_value(col, value)

                if isinstance(converted_value, bool):
                    list_model_filters.append(getattr(self.model_class, col).is_(converted_value))
                else:
                    if operator == "=":
                        list_model_filters.append(getattr(self.model_class, col) == converted_value)
                    elif operator == "!=":
                        list_model_filters.append(getattr(self.model_class, col) != converted_value)
                    elif operator == ">=":
                        list_model_filters.append(getattr(self.model_class, col) >= converted_value)
                    elif operator == "<=":
                        list_model_filters.append(getattr(self.model_class, col) <= converted_value)
                    else:
                        raise ValidationException(f"Invalid operator '{operator}' for {col}")

        return list_model_filters

    def _build_sort(self, sort: Union[str, List[str], None]) -> List[Any]:
        """Build sort dengan optimization."""
        if not sort:
            return []

        list_sort: List[Any] = []

        if isinstance(sort, str):
            sort = [sort]

        for sort_item in sort:
            col, order = self._parse_sort_item(sort_item)
            self._validate_column(col)

            if order == "asc":
                list_sort.append(getattr(self.model_class, col).asc())
            elif order == "desc":
                list_sort.append(getattr(self.model_class, col).desc())
            else:
                raise ValidationException(f"Invalid sort order '{order}' for {col}")

        return list_sort

    async def find_by_id(self, id: str, relationships: Optional[List[str]] = None) -> ModelType:
        """Find record by ID dengan optional eager loading."""
        record = await self.repository.find_by_id(id, relationships=relationships or [])
        if not record:
            raise NotFoundException(f"{self.model_class.__name__} with id {id} not found.")
        return record

    async def find_all(
        self,
        filters: Optional[Union[str, List[str]]] = None,
        sort: Optional[Union[str, List[str]]] = None,
        search: str = "",
        group_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        relationships: Optional[List[str]] = None,
        searchable_columns: Optional[List[str]] = None,
    ) -> Tuple[List[ModelType], int]:
        """Optimized find_all."""

        if group_by:
            self._validate_column(group_by)

        list_model_filters = self._build_filters(filters)
        list_sort = self._build_sort(sort)

        return await self.repository.find_all(
            filters=list_model_filters,
            sort=list_sort,
            search=search,
            group_by=group_by,
            limit=limit,
            offset=offset,
            relationships=relationships or [],
            searchable_columns=searchable_columns or [],
        )

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """Create new record."""
        try:
            return await self.repository.create(data)
        except Exception as e:
            # Handle duplicate key errors
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateValueException(f"Record already exists: {str(e)}")
            raise

    async def update(self, id: str, data: Dict[str, Any], refresh: bool = True) -> ModelType:
        """Update existing record."""
        # Check existence first
        if not await self.repository.exists(id):
            raise NotFoundException(f"{self.model_class.__name__} with id {id} not found.")

        try:
            updated = await self.repository.update(id, data, refresh=refresh)
            if not updated:
                raise NotFoundException(f"{self.model_class.__name__} with id {id} not found.")
            return updated
        except Exception as e:
            # Handle duplicate key errors
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateValueException(f"Update would create duplicate: {str(e)}")
            raise

    async def delete(self, id: str, permanent: bool = False) -> None:
        """Delete record dengan soft delete support."""
        if not await self.repository.exists(id):
            raise NotFoundException(f"{self.model_class.__name__} with id {id} not found.")

        if self._has_soft_delete and not permanent:
            delete_data = {"is_deleted": True}
            if hasattr(self.model_class, "is_active"):
                delete_data["is_active"] = False
            await self.repository.update(id, delete_data, refresh=False)
        else:
            await self.repository.delete(id)

    async def bulk_create(self, data_list: List[Dict[str, Any]], batch_size: int = 1000) -> List[ModelType]:
        """Bulk create dengan validation."""
        return await self.repository.bulk_create(data_list, batch_size=batch_size, return_records=True)

    async def exists_by_id(self, id: str) -> bool:
        """Check existence tanpa fetch object."""
        return await self.repository.exists(id)

    async def count_by_filters(self, filters: Optional[Union[str, List[str]]] = None) -> int:
        """Count records dengan filters."""
        list_model_filters = self._build_filters(filters)
        return await self.repository.count(list_model_filters)
