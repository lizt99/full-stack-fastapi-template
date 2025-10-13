"""
物品管理模块定义
"""
from typing import List, Type
from fastapi import APIRouter
from sqlmodel import SQLModel

from ..base import CRUDModule
from .models import Item, ItemCreate, ItemUpdate, ItemPublic, ItemsPublic


class ItemsModule(CRUDModule):
    """物品管理模块 - 提供物品的CRUD功能"""
    
    def __init__(self):
        super().__init__(name="items", prefix="/items")
        self.dependencies = ["core"]  # 依赖核心模块（用户认证）
        self.provides = ["item_management"]
    
    def get_router(self) -> APIRouter:
        """返回物品管理路由"""
        return self.router
    
    def get_models(self) -> List[Type[SQLModel]]:
        """返回物品管理模块的数据模型"""
        return [
            Item,
            ItemCreate,
            ItemUpdate, 
            ItemPublic,
            ItemsPublic
        ]
    
    def _setup_router(self):
        """设置CRUD路由"""
        # 使用基类的setup_crud_routes方法自动生成CRUD路由
        self.setup_crud_routes(
            model_class=Item,
            create_model=ItemCreate,
            update_model=ItemUpdate,
            public_model=ItemPublic
        )
        
        # 可以添加额外的自定义路由
        self._setup_custom_routes()
    
    def _setup_custom_routes(self):
        """设置自定义路由"""
        from app.api.deps import CurrentUser, SessionDep
        from sqlmodel import func, select
        from typing import Any
        
        @self.router.get("/count", response_model=dict)
        def get_items_count(session: SessionDep, current_user: CurrentUser) -> Any:
            """获取物品数量统计"""
            if current_user.is_superuser:
                count_statement = select(func.count()).select_from(Item)
                total_count = session.exec(count_statement).one()
                return {"total": total_count}
            else:
                count_statement = select(func.count()).select_from(Item).where(
                    Item.owner_id == current_user.id
                )
                user_count = session.exec(count_statement).one()
                return {"user_items": user_count}
    
    @property
    def migration_path(self) -> str:
        """物品模块迁移路径"""
        return "app/modules/items/migrations"
