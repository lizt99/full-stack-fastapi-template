"""
TradingView模块定义
"""
from typing import List, Type
from fastapi import APIRouter
from sqlmodel import SQLModel

from ..base import CRUDModule
from .models import TradingView, TradingViewCreate, TradingViewUpdate, TradingViewPublic, TradingViewsPublic


class TradingViewModule(CRUDModule):
    """TradingView模块 - 提供交易视图项目的CRUD功能"""
    
    def __init__(self):
        super().__init__(name="tradingview", prefix="/tradingview")
        self.dependencies = ["core"]  # 依赖核心模块（用户认证）
        self.provides = ["tradingview_management"]
        
        # 模块特定配置
        self.config = {
            "max_items_per_user": 100,
            "allow_public_view": False,
            "enable_analytics": True
        }
    
    def get_router(self) -> APIRouter:
        """返回TradingView管理路由"""
        return self.router
    
    def get_models(self) -> List[Type[SQLModel]]:
        """返回TradingView模块的数据模型"""
        return [
            TradingView,
            TradingViewCreate,
            TradingViewUpdate,
            TradingViewPublic,
            TradingViewsPublic
        ]
    
    def _setup_router(self):
        """设置CRUD路由和自定义路由"""
        # 使用基类的setup_crud_routes方法自动生成CRUD路由
        self.setup_crud_routes(
            model_class=TradingView,
            create_model=TradingViewCreate,
            update_model=TradingViewUpdate,
            public_model=TradingViewPublic
        )
        
        # 添加自定义路由
        self._setup_custom_routes()
    
    def _setup_custom_routes(self):
        """设置自定义路由"""
        from app.api.deps import CurrentUser, SessionDep
        from sqlmodel import func, select
        from typing import Any
        import uuid
        from fastapi import HTTPException
        
        @self.router.get("/search", response_model=TradingViewsPublic)
        def search_tradingviews(
            session: SessionDep,
            current_user: CurrentUser,
            q: str = "",
            skip: int = 0,
            limit: int = 100
        ) -> Any:
            """搜索TradingView项目"""
            base_query = select(TradingView)
            
            # 非超级用户只能搜索自己的项目
            if not current_user.is_superuser:
                base_query = base_query.where(TradingView.owner_id == current_user.id)
            
            # 添加搜索条件
            if q:
                search_filter = (
                    TradingView.name.contains(q) | 
                    TradingView.description.contains(q)
                )
                base_query = base_query.where(search_filter)
            
            # 获取总数
            count_query = select(func.count()).select_from(base_query.subquery())
            count = session.exec(count_query).one()
            
            # 获取数据
            items_query = base_query.offset(skip).limit(limit)
            items = session.exec(items_query).all()
            
            return TradingViewsPublic(data=items, count=count)
        
        @self.router.get("/stats", response_model=dict)
        def get_tradingview_stats(session: SessionDep, current_user: CurrentUser) -> Any:
            """获取TradingView统计信息"""
            if current_user.is_superuser:
                # 管理员可以看到全部统计
                total_count = session.exec(select(func.count()).select_from(TradingView)).one()
                users_with_items = session.exec(
                    select(func.count(func.distinct(TradingView.owner_id))).select_from(TradingView)
                ).one()
                
                return {
                    "total_items": total_count,
                    "active_users": users_with_items,
                    "average_per_user": round(total_count / max(users_with_items, 1), 2)
                }
            else:
                # 普通用户只能看到自己的统计
                user_count = session.exec(
                    select(func.count()).select_from(TradingView).where(
                        TradingView.owner_id == current_user.id
                    )
                ).one()
                
                return {
                    "user_items": user_count,
                    "max_allowed": self.config.get("max_items_per_user", 100)
                }
        
        @self.router.post("/{id}/duplicate", response_model=TradingViewPublic)
        def duplicate_tradingview(
            *,
            session: SessionDep,
            current_user: CurrentUser,
            id: uuid.UUID
        ) -> Any:
            """复制TradingView项目"""
            # 获取原项目
            original = session.get(TradingView, id)
            if not original:
                raise HTTPException(status_code=404, detail="TradingView项目未找到")
            
            # 检查权限
            if not current_user.is_superuser and original.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="无权限操作此项目")
            
            # 创建副本
            duplicate_data = TradingViewCreate(
                name=f"{original.name} (副本)",
                description=original.description
            )
            
            new_item = TradingView.model_validate(
                duplicate_data,
                update={"owner_id": current_user.id}
            )
            session.add(new_item)
            session.commit()
            session.refresh(new_item)
            
            return new_item
    
    @property
    def migration_path(self) -> str:
        """TradingView模块迁移路径"""
        return "app/modules/tradingview/migrations"
    
    def on_enable(self):
        """模块启用时的回调"""
        super().on_enable()
        # 动态添加User模型的反向关系
        from app.modules.core.models import User
        from sqlmodel import Relationship
        
        # 为User模型添加tradingviews字段
        if not hasattr(User, 'tradingviews'):
            User.tradingviews = Relationship(back_populates="owner", cascade_delete=True)
            User.model_rebuild()
    
    def on_disable(self):
        """模块禁用时的回调"""
        super().on_disable()
        # 可以在这里清理资源或记录日志
