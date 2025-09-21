from typing import Optional

from pydantic import BaseModel, EmailStr


class UserIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    address: Optional[str]
    phone: Optional[str]
    gender: Optional[str]
    avatar: Optional[str]
    role_id: Optional[int]
    is_enabled: bool
    is_verified: bool
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: str
    updated_at: str


class OAuth2PasswordRequestFormIn(BaseModel):
    username: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str
