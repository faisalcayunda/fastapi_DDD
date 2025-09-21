# app/platform/fastapi/dependencies.py

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.features.auth.api.deps import get_token_service, get_user_repo
from app.features.auth.entities.user import User
from app.features.auth.use_cases.ports import TokenService, UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    tokens: TokenService = Depends(get_token_service),
    repo: UserRepository = Depends(get_user_repo),
) -> User:
    claims = tokens.parse(token)
    if not claims:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await repo.by_id(claims["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_roles(*allowed_role_ids: int):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role_id not in allowed_role_ids:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return dependency
