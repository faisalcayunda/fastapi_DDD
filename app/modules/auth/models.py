from datetime import datetime

import uuid6
from pytz import timezone
from sqlalchemy import UUID, BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.config import settings

from . import Base


class RefreshTokenModel(Base):
    __tablename__ = "tokens"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        String(36),
        nullable=False,
        index=True,
    )
    token = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, server_default="false")
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone(settings.TIMEZONE))
    )
