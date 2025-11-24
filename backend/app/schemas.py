from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator


class PostBase(BaseModel):
    title: str
    excerpt: Optional[str] = None
    tags: List[str] = []
    slug: Optional[str] = None
    visibility: str = "registered"

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return []


class PostCreate(PostBase):
    content_path: str


class PostUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content_path: Optional[str] = None
    tags: Optional[List[str] | str] = None
    slug: Optional[str] = None
    visibility: Optional[str] = None

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value):
        if value is None:
            return value
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


class PostOut(PostBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PostDetail(PostOut):
    content: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    email: str
    role: str
    membership_expires_at: datetime | None = None


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str
