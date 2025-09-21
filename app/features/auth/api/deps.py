# app/features/auth/api/deps.py
from functools import lru_cache

from fastapi import Depends

from app.features.auth.adapters.crypto.hasher_argon2 import Argon2Hasher
from app.features.auth.adapters.repositories.user_repository import UserRepository
from app.features.auth.adapters.services.jwt_service import JWTService
from app.platform.db.engine import get_session


def get_user_repo(s=Depends(get_session)):
    return UserRepository(s)


@lru_cache
def get_password_hasher():
    return Argon2Hasher()


@lru_cache
def get_token_service():
    return JWTService()
