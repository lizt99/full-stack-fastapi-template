"""
TradingView测试工具函数
"""
from sqlmodel import Session

from app.modules.tradingview.models import TradingView, TradingViewCreate
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_tradingview(db: Session) -> TradingView:
    """创建随机TradingView对象用于测试"""
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    
    name = f"Trading Strategy {random_lower_string()}"
    description = f"Description for {random_lower_string()} trading strategy"
    
    tradingview_in = TradingViewCreate(name=name, description=description)
    # 直接使用SQLModel创建，因为TradingView使用CRUDModule基类
    tradingview = TradingView.model_validate(
        tradingview_in,
        update={"owner_id": owner_id}
    )
    db.add(tradingview)
    db.commit()
    db.refresh(tradingview)
    return tradingview


def create_random_tradingview_data() -> dict[str, str]:
    """创建随机TradingView数据字典用于API测试"""
    return {
        "name": f"Test Strategy {random_lower_string()}",
        "description": f"Test description {random_lower_string()}"
    }
