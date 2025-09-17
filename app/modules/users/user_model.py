from datetime import datetime

from pytz import timezone
from sqlalchemy import CHAR, Boolean, Column, DateTime, Integer, String

from app.core.config import settings

from . import Base


class UserModel(Base):
    __tablename__ = "user_account"

    id = Column("acc_id", String(36), primary_key=True, index=True)
    name = Column("acc_name", String(256), nullable=False)
    address = Column("acc_address", String(512), nullable=True)
    phone = Column("acc_phone", String(20), nullable=True)
    gender = Column("acc_gender", String(10), nullable=True)
    agency_name = Column("acc_agency_name", String(256), nullable=True)
    agency_type = Column("acc_agency_type", String(100), nullable=True)
    file = Column("acc_file", String(512), nullable=True)
    avatar = Column("acc_avatar", String(512), nullable=True)
    email = Column("acc_email", String(256), unique=True, nullable=False)
    password = Column("acc_password", String(256), nullable=False)
    enable = Column("acc_enable", CHAR(1), default=True)
    role_id = Column(Integer)
    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
        default=datetime.now(timezone(settings.TIMEZONE)),
    )
    created_by = Column("create_by", String(36), nullable=True)
    updated_by = Column("update_by", String(36), nullable=True)
    created_at = Column(
        "create_at",
        DateTime(timezone=True),
        default=datetime.now(timezone(settings.TIMEZONE)),
    )
    updated_at = Column(
        "update_at",
        DateTime(timezone=True),
        default=datetime.now(timezone(settings.TIMEZONE)),
        onupdate=datetime.now(timezone(settings.TIMEZONE)),
    )
    is_verified = Column(Boolean, default=False)
