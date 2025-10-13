"""
模型配置 - 统一管理所有模型定义和关系
避免循环导入问题
"""
import uuid
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING

# 使用 TYPE_CHECKING 避免运行时循环导入
if TYPE_CHECKING:
    pass


# ===== Core 模块模型 =====
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# ===== Items 模块模型 =====
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)


# ===== TradingView 模块模型 =====
class TradingViewBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, description="TradingView项目名称")
    description: str | None = Field(default=None, max_length=1000, description="项目描述")


class TradingViewCreate(TradingViewBase):
    pass


class TradingViewUpdate(TradingViewBase):
    name: str | None = Field(default=None, min_length=1, max_length=255)


# ===== 数据库表模型 =====
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    tradingviews: list["TradingView"] = Relationship(back_populates="owner", cascade_delete=True)


class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User = Relationship(back_populates="items")


class TradingView(TradingViewBase, table=True):
    __tablename__ = "tradingview"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User = Relationship(back_populates="tradingviews")


# ===== 公共API模型 =====
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


class TradingViewPublic(TradingViewBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class TradingViewsPublic(SQLModel):
    data: list[TradingViewPublic]
    count: int


# ===== 通用模型 =====
class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# 重建所有模型以确保关系正确
User.model_rebuild()
Item.model_rebuild()
TradingView.model_rebuild()
