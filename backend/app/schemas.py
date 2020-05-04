from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class Msg(BaseModel):
    msg: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: UUID


class NestedUser(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None


class NestedItem(BaseModel):
    id: UUID
    title: str


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class User(UserBase):
    id: UUID
    email: EmailStr
    num_items: int
    items: List[NestedItem]


class UserInDB(UserBase):
    id: UUID
    hashed_password: str


class ItemBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ItemCreate(ItemBase):
    title: str


class ItemUpdate(ItemBase):
    pass


class Item(ItemBase):
    id: UUID
    owner: NestedUser


class PaginatedUsers(BaseModel):
    count: int
    data: List[User]


class PaginatedItems(BaseModel):
    count: int
    data: List[Item]
