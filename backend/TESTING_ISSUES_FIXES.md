# 测试相关问题修复记录

## 问题 1: 测试清理导致超级用户被删除

### 🐛 问题描述
运行API测试后，测试清理过程会删除数据库中的所有用户，包括系统初始化的超级用户 `admin@example.com`，导致无法登录前端系统。

### 📍 问题位置
- 文件: `tests/conftest.py`
- 行数: 24-26
- 原始代码:
```python
statement = delete(User)
session.execute(statement)
session.commit()
```

### 🔧 解决方案
修改测试清理逻辑，只删除测试过程中创建的用户，保留系统超级用户：

```python
# 只删除非超级用户，保留系统管理员
statement = delete(User).where(User.email != settings.FIRST_SUPERUSER)
session.execute(statement)
session.commit()

# 确保超级用户仍然存在，如果不存在则重新创建
from sqlmodel import select
superuser = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
if not superuser:
    print("⚠️ 重新创建超级用户...")
    init_db(session)
```

### ✅ 修复效果
1. **保留超级用户**: 测试运行后超级用户账户不会被删除
2. **自动恢复**: 如果超级用户意外丢失，会自动重新创建
3. **正常清理**: 测试创建的用户仍会被正确清理
4. **登录正常**: 前端登录功能恢复正常

### 🧪 验证方法
```bash
# 运行测试
python run_tests.py --core

# 验证超级用户存在
python -c "
from sqlmodel import Session, select
from app.core.db import engine
from app.models import User
from app.core.config import settings

with Session(engine) as session:
    superuser = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
    print(f'超级用户存在: {superuser is not None}')
"

# 测试登录
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=-EhzmyyMFZHqlSTJ"
```

### 📚 相关知识点
- **SQLAlchemy删除过滤**: 使用 `where()` 条件过滤删除操作
- **测试数据清理**: 在pytest中正确管理测试数据生命周期
- **用户管理**: 系统管理员账户的保护策略

## 恢复超级用户的应急方法

如果超级用户已经被删除，可以手动恢复：

```python
# 方法1: 使用init_db重新初始化
from sqlmodel import Session
from app.core.db import engine, init_db

with Session(engine) as session:
    init_db(session)

# 方法2: 手动创建超级用户  
from app.models import User, UserCreate
from app import crud
from app.core.config import settings

with Session(engine) as session:
    user_in = UserCreate(
        email=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        is_superuser=True,
    )
    user = crud.create_user(session=session, user_create=user_in)
```

## 最佳实践建议

1. **测试隔离**: 使用测试专用数据库，避免影响开发数据
2. **数据清理**: 明确区分系统数据和测试数据
3. **用户保护**: 重要的系统账户应该有特殊保护机制
4. **自动恢复**: 实现自动检查和恢复机制
5. **文档记录**: 记录重要问题和解决方案

## 登录凭据

修复后的系统登录信息：
- **邮箱**: admin@example.com
- **密码**: -EhzmyyMFZHqlSTJ
- **前端地址**: http://localhost:5173
- **后端API**: http://localhost:8000
