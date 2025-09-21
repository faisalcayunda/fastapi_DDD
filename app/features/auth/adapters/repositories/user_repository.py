from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.entities.user import User
from app.features.auth.use_cases.ports import UserRepository
from app.platform.db.models import UserModel

from .mappers import to_entity


class UserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def by_id(self, user_id: str) -> Optional[User]:
        user = await self.session.get(UserModel, user_id)
        return to_entity(user) if user else None

    async def by_email(self, email: str) -> Optional[User]:
        user = await self.session.scalar(select(UserModel).where(UserModel.email == email))
        return to_entity(user) if user else None

    async def by_username(self, username: str) -> Optional[User]:
        user = await self.session.scalar(select(UserModel).where(UserModel.name == username))
        return to_entity(user) if user else None

    async def save(self, u: User):
        await self.session.add(u)

    async def update(self, u: User):
        await self.session.merge(u)
