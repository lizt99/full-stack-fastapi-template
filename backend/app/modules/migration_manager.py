"""
模块独立迁移管理器
支持每个模块有独立的迁移文件和版本控制
"""
import os
import importlib
import logging
from typing import Dict, List, Optional
from pathlib import Path
from sqlmodel import Session, create_engine, text
from app.core.config import settings
from app.core.db import engine

logger = logging.getLogger(__name__)


class ModuleMigrationManager:
    """模块迁移管理器"""
    
    def __init__(self):
        self.engine = engine
        self.migrations_table = "module_migrations"
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """确保模块迁移记录表存在"""
        with Session(self.engine) as session:
            session.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                    id SERIAL PRIMARY KEY,
                    module_name VARCHAR(255) NOT NULL,
                    migration_name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(module_name, migration_name)
                )
            """))
            session.commit()
    
    def get_applied_migrations(self, module_name: str) -> List[str]:
        """获取已应用的迁移列表"""
        with Session(self.engine) as session:
            stmt = text(f"""
                SELECT migration_name FROM {self.migrations_table} 
                WHERE module_name = :module_name 
                ORDER BY applied_at
            """)
            result = session.execute(stmt, {"module_name": module_name})
            return [row[0] for row in result.fetchall()]
    
    def mark_migration_applied(self, module_name: str, migration_name: str):
        """标记迁移为已应用"""
        with Session(self.engine) as session:
            stmt = text(f"""
                INSERT INTO {self.migrations_table} (module_name, migration_name)
                VALUES (:module_name, :migration_name)
                ON CONFLICT (module_name, migration_name) DO NOTHING
            """)
            session.execute(stmt, {"module_name": module_name, "migration_name": migration_name})
            session.commit()
    
    def remove_migration_record(self, module_name: str, migration_name: str):
        """移除迁移记录"""
        with Session(self.engine) as session:
            stmt = text(f"""
                DELETE FROM {self.migrations_table} 
                WHERE module_name = :module_name AND migration_name = :migration_name
            """)
            session.execute(stmt, {"module_name": module_name, "migration_name": migration_name})
            session.commit()
    
    def get_pending_migrations(self, module_name: str) -> List[str]:
        """获取待应用的迁移"""
        module_migrations_dir = Path(f"app/modules/{module_name}/migrations")
        if not module_migrations_dir.exists():
            return []
        
        # 获取所有迁移文件
        migration_files = []
        for file in module_migrations_dir.glob("*.py"):
            if file.name != "__init__.py":
                migration_files.append(file.stem)
        
        migration_files.sort()  # 按文件名排序
        
        # 获取已应用的迁移
        applied = set(self.get_applied_migrations(module_name))
        
        # 返回未应用的迁移
        return [m for m in migration_files if m not in applied]
    
    def run_migration(self, module_name: str, migration_name: str) -> bool:
        """运行单个迁移"""
        try:
            migration_module = importlib.import_module(
                f"app.modules.{module_name}.migrations.{migration_name}"
            )
            
            if hasattr(migration_module, 'upgrade'):
                with Session(self.engine) as session:
                    migration_module.upgrade(session)
                    session.commit()
                
                self.mark_migration_applied(module_name, migration_name)
                logger.info(f"迁移 {module_name}.{migration_name} 应用成功")
                return True
            else:
                logger.error(f"迁移文件 {migration_name} 缺少 upgrade 函数")
                return False
                
        except Exception as e:
            logger.error(f"运行迁移 {module_name}.{migration_name} 失败: {e}")
            return False
    
    def rollback_migration(self, module_name: str, migration_name: str) -> bool:
        """回滚单个迁移"""
        try:
            migration_module = importlib.import_module(
                f"app.modules.{module_name}.migrations.{migration_name}"
            )
            
            if hasattr(migration_module, 'downgrade'):
                with Session(self.engine) as session:
                    migration_module.downgrade(session)
                    session.commit()
                
                self.remove_migration_record(module_name, migration_name)
                logger.info(f"迁移 {module_name}.{migration_name} 回滚成功")
                return True
            else:
                logger.error(f"迁移文件 {migration_name} 缺少 downgrade 函数")
                return False
                
        except Exception as e:
            logger.error(f"回滚迁移 {module_name}.{migration_name} 失败: {e}")
            return False
    
    def migrate_module(self, module_name: str) -> bool:
        """运行模块的所有待应用迁移"""
        pending = self.get_pending_migrations(module_name)
        if not pending:
            logger.info(f"模块 {module_name} 没有待应用的迁移")
            return True
        
        logger.info(f"开始为模块 {module_name} 应用 {len(pending)} 个迁移")
        
        for migration in pending:
            if not self.run_migration(module_name, migration):
                logger.error(f"模块 {module_name} 迁移在 {migration} 处失败")
                return False
        
        logger.info(f"模块 {module_name} 所有迁移应用完成")
        return True
    
    def migrate_all_modules(self, module_names: List[str]) -> Dict[str, bool]:
        """运行所有模块的迁移"""
        results = {}
        for module_name in module_names:
            results[module_name] = self.migrate_module(module_name)
        return results
    
    def get_migration_status(self) -> Dict[str, Dict[str, any]]:
        """获取所有模块的迁移状态"""
        status = {}
        
        # 检查所有已知模块
        modules_dir = Path("app/modules")
        for module_dir in modules_dir.iterdir():
            if module_dir.is_dir() and module_dir.name not in ["__pycache__"]:
                module_name = module_dir.name
                migrations_dir = module_dir / "migrations"
                
                if migrations_dir.exists():
                    applied = self.get_applied_migrations(module_name)
                    pending = self.get_pending_migrations(module_name)
                    
                    status[module_name] = {
                        "applied_count": len(applied),
                        "pending_count": len(pending),
                        "applied_migrations": applied,
                        "pending_migrations": pending
                    }
        
        return status
    
    def create_migration_file(self, module_name: str, migration_name: str, 
                            up_sql: str = "", down_sql: str = "") -> str:
        """创建迁移文件"""
        migrations_dir = Path(f"app/modules/{module_name}/migrations")
        migrations_dir.mkdir(exist_ok=True)
        
        # 创建__init__.py文件
        init_file = migrations_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
        
        # 生成迁移文件名（带时间戳前缀）
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}_{migration_name}.py"
        file_path = migrations_dir / file_name
        
        # 迁移文件模板
        template = f'''"""
{migration_name} 迁移

模块: {module_name}
创建时间: {datetime.datetime.now().isoformat()}
"""
from sqlmodel import Session, text


def upgrade(session: Session):
    """升级迁移"""
    # 在这里添加升级逻辑
{f"    session.exec(text('''{up_sql}'''))" if up_sql else "    pass"}


def downgrade(session: Session):
    """降级迁移"""
    # 在这里添加降级逻辑
{f"    session.exec(text('''{down_sql}'''))" if down_sql else "    pass"}
'''
        
        file_path.write_text(template)
        logger.info(f"迁移文件已创建: {file_path}")
        return str(file_path)


# 全局迁移管理器实例
migration_manager = ModuleMigrationManager()
