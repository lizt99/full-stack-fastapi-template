"""
TradingView API路由测试
"""
import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.tradingview import create_random_tradingview, create_random_tradingview_data


def test_create_tradingview(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """测试创建TradingView"""
    data = create_random_tradingview_data()
    response = client.post(
        f"{settings.API_V1_STR}/tradingview/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_read_tradingview(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """测试读取单个TradingView"""
    tradingview = create_random_tradingview(db)
    response = client.get(
        f"{settings.API_V1_STR}/tradingview/{tradingview.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == tradingview.name
    assert content["description"] == tradingview.description
    assert content["id"] == str(tradingview.id)
    assert content["owner_id"] == str(tradingview.owner_id)


def test_read_tradingview_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """测试读取不存在的TradingView"""
    response = client.get(
        f"{settings.API_V1_STR}/tradingview/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


def test_read_tradingview_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """测试普通用户读取其他人的TradingView"""
    tradingview = create_random_tradingview(db)
    response = client.get(
        f"{settings.API_V1_STR}/tradingview/{tradingview.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_tradingviews(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """测试读取TradingView列表"""
    create_random_tradingview(db)
    create_random_tradingview(db)
    response = client.get(
        f"{settings.API_V1_STR}/tradingview/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert isinstance(content["data"], list)
    assert content["count"] >= 2


def test_update_tradingview(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """测试更新TradingView"""
    tradingview = create_random_tradingview(db)
    data = {
        "name": "Updated Trading Strategy", 
        "description": "Updated description for trading strategy"
    }
    response = client.put(
        f"{settings.API_V1_STR}/tradingview/{tradingview.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["id"] == str(tradingview.id)
    assert content["owner_id"] == str(tradingview.owner_id)


def test_update_tradingview_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """测试更新不存在的TradingView"""
    data = {
        "name": "Updated Trading Strategy", 
        "description": "Updated description"
    }
    response = client.put(
        f"{settings.API_V1_STR}/tradingview/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


def test_update_tradingview_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """测试普通用户更新其他人的TradingView"""
    tradingview = create_random_tradingview(db)
    data = {
        "name": "Updated Trading Strategy", 
        "description": "Updated description"
    }
    response = client.put(
        f"{settings.API_V1_STR}/tradingview/{tradingview.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_tradingview(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """测试删除TradingView"""
    tradingview = create_random_tradingview(db)
    response = client.delete(
        f"{settings.API_V1_STR}/tradingview/{tradingview.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Item deleted successfully"


def test_delete_tradingview_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """测试删除不存在的TradingView"""
    response = client.delete(
        f"{settings.API_V1_STR}/tradingview/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


def test_delete_tradingview_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """测试普通用户删除其他人的TradingView"""
    tradingview = create_random_tradingview(db)
    response = client.delete(
        f"{settings.API_V1_STR}/tradingview/{tradingview.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_search_tradingviews(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """测试搜索TradingView"""
    # 创建一个特定名称的TradingView用于搜索
    tradingview = create_random_tradingview(db)
    search_term = tradingview.name.split()[0]  # 使用名称的第一个词作为搜索关键词
    
    response = client.get(
        f"{settings.API_V1_STR}/tradingview/search",
        headers=superuser_token_headers,
        params={"q": search_term}
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert isinstance(content["data"], list)


def test_tradingview_stats(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """测试TradingView统计信息"""
    # 创建一些TradingView记录
    create_random_tradingview(db)
    create_random_tradingview(db)
    
    response = client.get(
        f"{settings.API_V1_STR}/tradingview/stats",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    # 根据TradingViewModule中的实际字段名修改
    assert "total_items" in content
    assert "active_users" in content
    assert isinstance(content["total_items"], int)
    assert isinstance(content["active_users"], int)
    assert content["total_items"] >= 2
