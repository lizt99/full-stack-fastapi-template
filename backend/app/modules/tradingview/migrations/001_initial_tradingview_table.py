"""
初始TradingView表迁移

模块: tradingview
创建时间: 2024-10-13T12:00:00
"""
from sqlmodel import Session, text


def upgrade(session: Session):
    """升级迁移 - 创建TradingView表"""
    session.exec(text("""
        CREATE TABLE IF NOT EXISTS tradingview (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            description VARCHAR(1000),
            owner_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
        );
        
        CREATE INDEX IF NOT EXISTS idx_tradingview_owner ON tradingview (owner_id);
        CREATE INDEX IF NOT EXISTS idx_tradingview_name ON tradingview (name);
    """))


def downgrade(session: Session):
    """降级迁移 - 删除TradingView表"""
    session.exec(text("""
        DROP TABLE IF EXISTS tradingview;
    """))
