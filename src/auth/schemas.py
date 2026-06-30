from datetime import datetime

from pydantic import BaseModel

from src.users.schemas import UserRead


class LoginIn(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    user: UserRead
    access_token: str


class TokenData(BaseModel):
    username_or_email: str


class TokenBlacklistBase(BaseModel):
    token: str
    expires_at: datetime


class TokenBlacklistRead(TokenBlacklistBase):
    id: int


class TokenBlacklistCreate(TokenBlacklistBase):
    pass


class TokenBlacklistUpdate(TokenBlacklistBase):
    pass
