from datetime import datetime

from fastapi_async_sqlalchemy import db
from pytz import timezone
from sqlalchemy import select
from uuid6 import UUID

from app.core.config import settings
from app.models import RefreshTokenModel
from app.repositories import BaseRepository


class TokenRepository(BaseRepository[RefreshTokenModel]):
    def __init__(self, model):
        super().__init__(model)

    async def find_valid_token(self, token: str, user_id: str):
        query = select(self.model).where(
            self.model.token == token,
            self.model.user_id == user_id,
            self.model.expires_at > datetime.now(timezone(settings.TIMEZONE)),
            self.model.revoked == False,
        )
        result = await db.session.execute(query)
        return result.scalars().first()

    async def revoke_token(self, token: str):
        token_obj = await self.find_by_token(token)
        if token_obj:
            token_obj.revoked = True
            db.session.add(token_obj)
            await db.session.commit()
            return True
        return False

    async def find_by_token(self, token: str):
        query = select(self.model).where(self.model.token == token)
        result = await db.session.execute(query)
        return result.scalars().first()
