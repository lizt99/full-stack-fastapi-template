"""
CRUD兼容性文件 - 重新导出模块化的CRUD操作
"""
# 从各个模块导入CRUD操作，保持向后兼容
from app.modules.core.crud import (
    create_user, update_user, get_user_by_email, authenticate, get_user_by_id
)

from app.modules.items.crud import (
    create_item, get_item_by_id, get_items_by_owner, get_all_items,
    update_item, delete_item
)

# 为了完全兼容，重新导出一些函数别名
def get_user_by_email_old(*args, **kwargs):
    """兼容旧接口"""
    return get_user_by_email(*args, **kwargs)

__all__ = [
    # User CRUD
    "create_user", "update_user", "get_user_by_email", "authenticate", "get_user_by_id",
    
    # Item CRUD
    "create_item", "get_item_by_id", "get_items_by_owner", "get_all_items",
    "update_item", "delete_item",
    
    # Compatibility
    "get_user_by_email_old",
]
