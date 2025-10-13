"""
核心模块 - 用户管理、认证等核心功能的模块定义
"""
from typing import List, Type
from fastapi import APIRouter
from sqlmodel import SQLModel

from ..base import BaseModule
from .models import User, UserCreate, UserUpdate, UserPublic, UsersPublic, Message, Token, TokenPayload, NewPassword, UpdatePassword, UserUpdateMe, UserRegister
from .routes import router


class CoreModule(BaseModule):
    """核心模块 - 负责用户管理、认证等基础功能"""
    
    def __init__(self):
        super().__init__(name="core", prefix="")  # 核心模块不需要前缀
        self.dependencies = []  # 核心模块没有依赖
        self.provides = ["authentication", "user_management"]
    
    def get_router(self) -> APIRouter:
        """返回核心模块路由"""
        return router
    
    def get_models(self) -> List[Type[SQLModel]]:
        """返回核心模块的数据模型"""
        return [
            User,
            UserCreate, 
            UserUpdate,
            UserPublic,
            UsersPublic,
            Message,
            Token,
            TokenPayload,
            NewPassword,
            UpdatePassword,
            UserUpdateMe,
            UserRegister
        ]
    
    def _setup_router(self):
        """设置路由 - 核心模块路由已在routes.py中定义"""
        # 核心模块的路由已经在routes.py中完全定义
        # 这里不需要额外设置
        pass
    
    @property
    def migration_path(self) -> str:
        """核心模块迁移路径"""
        return "app/modules/core/migrations"
    
    def on_enable(self):
        """核心模块启用回调"""
        super().on_enable()
        # 核心模块启用时的特殊逻辑
        
    def on_disable(self):
        """核心模块不能被禁用"""
        raise RuntimeError("核心模块不能被禁用")
