from typing import Any, Dict, Generic, List, Optional, Sequence, Tuple, Type, TypeVar

from fastapi_async_sqlalchemy import db
from sqlalchemy import String, cast
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import func, inspect, or_, select
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Optimized base repository with fastapi-async-sqlalchemy."""

    def __init__(self, model: Type[ModelType], session: Optional[AsyncSession] = None):
        self.model: Type[ModelType] = model
        self.inspector = inspect(self.model)
        self._session = session or db.session

    @property
    def session(self) -> AsyncSession:
        """Get database session."""
        return self._session

    def build_base_query(self, include_deleted: bool = False):
        """Build base query dengan soft delete handling."""
        query = select(self.model)
        if hasattr(self.model, "is_deleted") and not include_deleted:
            query = query.where(self.model.is_deleted.is_(False))
        return query

    async def find_by_id(self, id: str, relationships: Optional[List[str]] = None) -> Optional[ModelType]:
        """Find record by ID dengan optional eager loading."""
        query = self.build_base_query().where(self.model.id == id)

        if relationships:
            for rel in relationships:
                if hasattr(self.model, rel):
                    attr = getattr(self.model, rel)
                    if hasattr(attr.property, "collection_class"):
                        query = query.options(selectinload(attr))
                    else:
                        query = query.options(joinedload(attr))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_all(
        self,
        filters: Optional[List[Any]] = None,
        sort: Optional[List[Any]] = None,
        search: str = "",
        group_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        relationships: Optional[List[str]] = None,
        searchable_columns: Optional[List[str]] = None,
    ) -> Tuple[List[ModelType], int]:
        """Optimized find_all method."""

        filters = filters or []
        sort = sort or []
        relationships = relationships or []
        searchable_columns = searchable_columns or []

        query = self.build_base_query().filter(*filters)

        # Optimized search
        if search:
            if searchable_columns:
                search_conditions = [
                    cast(getattr(self.model, col), String).ilike(f"%{search}%")
                    for col in searchable_columns
                    if hasattr(self.model, col)
                ]
            else:
                search_conditions = [
                    cast(getattr(self.model, col_name), String).ilike(f"%{search}%")
                    for col_name in self.inspector.c.keys()
                ]

            if search_conditions:
                query = query.where(or_(*search_conditions))

        if group_by:
            query = query.group_by(getattr(self.model, group_by))

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        if total is None:
            total = 0

        # Data query
        if sort:
            query = query.order_by(*sort)
        else:
            query = query.order_by(self.model.id)

        if relationships:
            for rel in relationships:
                if hasattr(self.model, rel):
                    attr = getattr(self.model, rel)
                    if hasattr(attr.property, "collection_class"):
                        query = query.options(selectinload(attr))
                    else:
                        query = query.options(joinedload(attr))

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        records_seq: Sequence[ModelType] = result.scalars().all()
        records: List[ModelType] = list(records_seq)

        return records, total

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """Create new record."""
        new_record = self.model(**data)
        self.session.add(new_record)
        await self.session.commit()
        await self.session.refresh(new_record)
        return new_record

    async def bulk_create(
        self,
        data: List[Dict[str, Any]],
        batch_size: int = 1000,
        return_records: bool = False,
    ) -> Optional[List[ModelType]]:
        """Bulk create dengan batching."""
        if not data:
            return [] if return_records else None

        created_records: List[ModelType] = []

        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]

            if return_records:
                batch_records = [self.model(**item) for item in batch]
                self.session.add_all(batch_records)
                created_records.extend(batch_records)
            else:
                await self.session.execute(self.model.__table__.insert(), batch)

        await self.session.commit()

        if return_records:
            for record in created_records:
                await self.session.refresh(record)
            return created_records

        return None

    async def update(self, id: str, data: Dict[str, Any], refresh: bool = True) -> Optional[ModelType]:
        """Update record dengan optimization."""
        clean_data = {k: v for k, v in data.items() if v is not None}

        if not clean_data:
            return await self.find_by_id(id) if refresh else None

        query = (
            sqlalchemy_update(self.model)
            .where(self.model.id == id)
            .values(**clean_data)
            .execution_options(synchronize_session="fetch")
        )

        result = await self.session.execute(query)
        await self.session.commit()

        if result.rowcount == 0:
            return None

        return await self.find_by_id(id) if refresh else None

    async def delete(self, id: str) -> bool:
        """Delete record."""
        query = sqlalchemy_delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def exists(self, id: str) -> bool:
        """Check if record exists."""
        query = select(1).where(self.model.id == id)
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted.is_(False))

        result = await self.session.scalar(query)
        return result is not None
