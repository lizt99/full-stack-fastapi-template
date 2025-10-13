"""
初始用户表迁移

模块: core
创建时间: 2024-10-13T12:00:00
"""
from sqlmodel import Session, text


def upgrade(session: Session):
    """升级迁移 - 创建用户表"""
    session.exec(text("""
        CREATE TABLE IF NOT EXISTS "user" (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            is_active BOOLEAN DEFAULT true,
            is_superuser BOOLEAN DEFAULT false
        );
        
        CREATE INDEX IF NOT EXISTS idx_user_email ON "user" (email);
    """))


def downgrade(session: Session):
    """降级迁移 - 删除用户表"""
    session.exec(text("""
        DROP TABLE IF EXISTS "user";
    """))
