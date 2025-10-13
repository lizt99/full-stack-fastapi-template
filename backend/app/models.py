"""
SQLModel models for the application.
统一导入所有模型，避免循环导入问题
"""

from app.modules.models_config import (
    # Core 模块
    User,
    UserCreate,
    UserPublic,
    UsersPublic,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
    UpdatePassword,
    Token,
    TokenPayload,
    NewPassword,
    Message,
    # Items 模块
    Item,
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUpdate,
    # TradingView 模块
    TradingView,
    TradingViewCreate,
    TradingViewPublic,
    TradingViewsPublic,
    TradingViewUpdate,
)