"""
模块基类 - 所有模块必须继承此类
提供标准的模块接口和生命周期管理
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Type, Dict, Any
from fastapi import APIRouter
from sqlmodel import SQLModel
import logging

logger = logging.getLogger(__name__)


class BaseModule(ABC):
    """所有模块的基类"""
    
    def __init__(self, name: str, prefix: Optional[str] = None):
        self.name = name
        self.prefix = prefix or f"/{name}"
        self.router = APIRouter(prefix=self.prefix, tags=[name])
        self.config: Dict[str, Any] = {}
        self.dependencies: List[str] = []  # 依赖的其他模块
        self.provides: List[str] = []      # 提供的服务/功能
        self._initialized = False
        
        # 初始化模块
        self._setup_router()
        self._initialized = True
        logger.info(f"模块 {self.name} 初始化完成")
    
    @abstractmethod
    def get_router(self) -> APIRouter:
        """返回模块的FastAPI路由"""
        return self.router
    
    @abstractmethod 
    def get_models(self) -> List[Type[SQLModel]]:
        """返回模块的数据模型列表"""
        return []
    
    @abstractmethod
    def _setup_router(self):
        """设置路由 - 子类必须实现"""
        pass
    
    @property
    def migration_path(self) -> Optional[str]:
        """返回模块迁移文件路径（可选）"""
        return f"app/modules/{self.name}/migrations"
    
    def check_dependencies(self, available_modules: List[str]) -> bool:
        """检查模块依赖是否满足"""
        for dep in self.dependencies:
            if dep not in available_modules:
                logger.error(f"模块 {self.name} 缺少依赖: {dep}")
                return False
        return True
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证模块配置（子类可重写）"""
        return True
    
    def on_enable(self):
        """模块启用时的回调（子类可重写）"""
        logger.info(f"模块 {self.name} 启用")
    
    def on_disable(self):
        """模块禁用时的回调（子类可重写）"""
        logger.info(f"模块 {self.name} 禁用")
    
    def get_info(self) -> Dict[str, Any]:
        """获取模块信息"""
        return {
            'name': self.name,
            'prefix': self.prefix,
            'dependencies': self.dependencies,
            'provides': self.provides,
            'initialized': self._initialized,
            'migration_path': self.migration_path,
            'models_count': len(self.get_models()),
            'config': self.config
        }


class CRUDModule(BaseModule):
    """带CRUD功能的模块基类"""
    
    def __init__(self, name: str, prefix: Optional[str] = None):
        super().__init__(name, prefix)
    
    def setup_crud_routes(self, model_class: Type[SQLModel], 
                         create_model: Type[SQLModel],
                         update_model: Type[SQLModel],
                         public_model: Type[SQLModel]):
        """设置标准CRUD路由"""
        from app.api.deps import CurrentUser, SessionDep
        from sqlmodel import func, select
        from fastapi import HTTPException
        import uuid
        from typing import Any
        
        # 推断复数形式的公共模型名称
        public_model_name = public_model.__name__ 
        if public_model_name.endswith('Public'):
            # ItemPublic -> ItemsPublic
            plural_model_name = public_model_name[:-6] + 'sPublic'  # 移除'Public'，添加's'和'Public'
        else:
            plural_model_name = public_model_name + 's'
            
        # 动态导入复数模型
        try:
            from app.modules.models_config import ItemsPublic, TradingViewsPublic
            if plural_model_name == 'ItemsPublic':
                list_model = ItemsPublic
            elif plural_model_name == 'TradingViewsPublic':
                list_model = TradingViewsPublic
            else:
                # 如果找不到对应的复数模型，使用简单列表
                list_model = List[public_model]
        except ImportError:
            list_model = List[public_model]
        
        # 获取所有记录
        @self.router.get("/", response_model=list_model)
        def read_items(
            session: SessionDep, 
            current_user: CurrentUser, 
            skip: int = 0, 
            limit: int = 100
        ) -> Any:
            """获取所有记录"""
            if current_user.is_superuser:
                # 获取总数
                count_statement = select(func.count()).select_from(model_class)
                count = session.exec(count_statement).one()
                
                # 获取数据
                statement = select(model_class).offset(skip).limit(limit)
                items = session.exec(statement).all()
            else:
                # 普通用户只能看到自己的记录（如果模型有owner_id字段）
                if hasattr(model_class, 'owner_id'):
                    count_statement = select(func.count()).select_from(model_class).where(
                        model_class.owner_id == current_user.id
                    )
                    count = session.exec(count_statement).one()
                    
                    statement = select(model_class).where(
                        model_class.owner_id == current_user.id
                    ).offset(skip).limit(limit)
                    items = session.exec(statement).all()
                else:
                    count_statement = select(func.count()).select_from(model_class)
                    count = session.exec(count_statement).one()
                    
                    statement = select(model_class).offset(skip).limit(limit)
                    items = session.exec(statement).all()
            
            # 根据模型类型返回适当的格式
            if hasattr(list_model, '__name__') and list_model.__name__.endswith('sPublic'):
                return list_model(data=items, count=count)
            else:
                return items
        
        # 创建记录
        @self.router.post("/", response_model=public_model)
        def create_item(
            *, session: SessionDep, current_user: CurrentUser, item_in: create_model
        ) -> Any:
            """创建新记录"""
            item_data = item_in.model_dump()
            # 如果模型有owner_id字段，设置为当前用户
            if hasattr(model_class, 'owner_id'):
                item_data['owner_id'] = current_user.id
            
            db_item = model_class.model_validate(item_data)
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return db_item
        
        # 获取单个记录
        @self.router.get("/{id}", response_model=public_model)
        def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
            """获取单个记录"""
            item = session.get(model_class, id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            
            # 检查权限
            if not current_user.is_superuser and hasattr(item, 'owner_id'):
                if item.owner_id != current_user.id:
                    raise HTTPException(status_code=403, detail="Not enough permissions")
            
            return item
        
        # 更新记录
        @self.router.put("/{id}", response_model=public_model)
        def update_item(
            *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID, item_in: update_model
        ) -> Any:
            """更新记录"""
            item = session.get(model_class, id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            
            # 检查权限
            if not current_user.is_superuser and hasattr(item, 'owner_id'):
                if item.owner_id != current_user.id:
                    raise HTTPException(status_code=403, detail="Not enough permissions")
            
            update_dict = item_in.model_dump(exclude_unset=True)
            item.sqlmodel_update(update_dict)
            session.add(item)
            session.commit()
            session.refresh(item)
            return item
        
        # 删除记录
        @self.router.delete("/{id}")
        def delete_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
            """删除记录"""
            item = session.get(model_class, id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            
            # 检查权限
            if not current_user.is_superuser and hasattr(item, 'owner_id'):
                if item.owner_id != current_user.id:
                    raise HTTPException(status_code=403, detail="Not enough permissions")
            
            session.delete(item)
            session.commit()
            return {"message": "Item deleted successfully"}
