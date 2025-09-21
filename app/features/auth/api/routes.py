# app/features/auth/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.features.auth.adapters.presenters.auth_presenter import AuthPresenter
from app.features.auth.api.deps import (
    get_password_hasher,
    get_token_service,
    get_user_repo,
)
from app.features.auth.api.schemas import TokenOut
from app.features.auth.use_cases.login import Login

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def issue_token(
    form: OAuth2PasswordRequestForm = Depends(),
    repo=Depends(get_user_repo),
    hasher=Depends(get_password_hasher),
    tokens=Depends(get_token_service),
):
    try:
        result = Login(repo=repo, hasher=hasher, tokens=tokens).execute(username=form.username, password=form.password)
        return AuthPresenter().present(result["access_token"])
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
