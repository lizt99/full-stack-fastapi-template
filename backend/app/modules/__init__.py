"""
模块化系统核心
支持动态加载、启用/禁用模块，模块独立迁移
"""
from typing import Dict, List, Optional, Type
from fastapi import APIRouter
from sqlmodel import SQLModel
import logging

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """模块注册器 - 管理所有模块的注册、启用、禁用"""
    
    def __init__(self):
        self.modules: Dict[str, dict] = {}
        self._initialized = False
    
    def register_module(self, name: str, module_instance) -> bool:
        """注册模块"""
        try:
            self.modules[name] = {
                'instance': module_instance,
                'router': module_instance.get_router(),
                'models': module_instance.get_models(),
                'config': getattr(module_instance, 'config', {}),
                'enabled': True,
                'migration_path': getattr(module_instance, 'migration_path', None)
            }
            logger.info(f"模块 {name} 注册成功")
            return True
        except Exception as e:
            logger.error(f"模块 {name} 注册失败: {e}")
            return False
    
    def enable_module(self, name: str) -> bool:
        """启用模块"""
        if name in self.modules:
            self.modules[name]['enabled'] = True
            if hasattr(self.modules[name]['instance'], 'on_enable'):
                self.modules[name]['instance'].on_enable()
            logger.info(f"模块 {name} 已启用")
            return True
        logger.warning(f"模块 {name} 不存在")
        return False
    
    def disable_module(self, name: str) -> bool:
        """禁用模块"""
        if name in self.modules and name != 'core':  # 核心模块不能禁用
            self.modules[name]['enabled'] = False
            if hasattr(self.modules[name]['instance'], 'on_disable'):
                self.modules[name]['instance'].on_disable()
            logger.info(f"模块 {name} 已禁用")
            return True
        return False
    
    def get_active_routers(self) -> List[APIRouter]:
        """获取所有启用模块的路由"""
        routers = []
        for name, module in self.modules.items():
            if module['enabled']:
                routers.append(module['router'])
        return routers
    
    def get_all_models(self) -> List[Type[SQLModel]]:
        """获取所有启用模块的数据模型"""
        models = []
        for name, module in self.modules.items():
            if module['enabled']:
                models.extend(module['models'])
        return models
    
    def get_module_info(self, name: str) -> Optional[dict]:
        """获取模块信息"""
        return self.modules.get(name)
    
    def list_modules(self) -> Dict[str, dict]:
        """列出所有模块"""
        return {
            name: {
                'enabled': module['enabled'],
                'has_migration': module['migration_path'] is not None,
                'models_count': len(module['models']),
                'config': module['config']
            }
            for name, module in self.modules.items()  
        }


# 全局模块注册器实例
registry = ModuleRegistry()
