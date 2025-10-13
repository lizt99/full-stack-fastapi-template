"""
初始物品表迁移

模块: items
创建时间: 2024-10-13T12:00:00
"""
from sqlmodel import Session, text


def upgrade(session: Session):
    """升级迁移 - 创建物品表"""
    session.exec(text("""
        CREATE TABLE IF NOT EXISTS item (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(255) NOT NULL,
            description VARCHAR(255),
            owner_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
        );
        
        CREATE INDEX IF NOT EXISTS idx_item_owner ON item (owner_id);
    """))


def downgrade(session: Session):
    """降级迁移 - 删除物品表"""
    session.exec(text("""
        DROP TABLE IF EXISTS item;
    """))
