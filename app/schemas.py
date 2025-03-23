from typing import Literal, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Great observation! While it may seem like we can create a shared config class to reduce repetition,
# Pydantic doesn’t support directly inheriting or sharing the Config class across multiple schemas.
# Each schema needs its own Config class, since the Config is tightly coupled with the schema's behavior.
# However, if you're looking to reduce duplication,
# here's a clean trick: you can use a base schema class with shared configuration.
# Let me show you how:


# Base class for shared config
class ConfigBase(BaseModel):
    class Config:
        from_attributes = True  # Allows ORM conversion for SQLAlchemy models


# User Schemas
class UserCreate(ConfigBase):
    email: EmailStr
    password: str


class UserResponse(ConfigBase):
    id: int
    email: EmailStr
    created_at: datetime


class UserLogin(ConfigBase):
    email: EmailStr
    password: str


class Token(ConfigBase):
    access_token: str
    token_type: str


class TokenData(ConfigBase):
    id: Optional[str] = None


# Post Schemas - Base schema for Post (shared fields)
class PostBase(ConfigBase):
    title: str
    content: str
    published: bool = True


# Schema for creating a new post (inherits from PostBase)
class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    pass
    created_at: datetime
    owner_id: int
    owner: UserResponse

class PostOut(ConfigBase):
    post: PostResponse
    votes: int


class Vote(ConfigBase):
    post_id: int
    dir: Literal[0, 1]   # 0 = downvote, 1 = upvote
