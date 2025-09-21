# app/features/auth/adapters/crypto/hasher_argon2.py
from argon2 import PasswordHasher as A2

from app.features.auth.use_cases.ports import PasswordHasher


class Argon2Hasher(PasswordHasher):
    def __init__(self, time_cost=2, memory_cost=102400, parallelism=8):
        self._ph = A2(time_cost=time_cost, memory_cost=memory_cost, parallelism=parallelism)

    def hash(self, raw: str) -> str:
        return self._ph.hash(raw)

    def verify(self, raw: str, hashed: str) -> bool:
        try:
            return self._ph.verify(hashed, raw)
        except Exception:
            return False

    def needs_rehash(self, hashed: str) -> bool:
        return self._ph.check_needs_rehash(hashed)
