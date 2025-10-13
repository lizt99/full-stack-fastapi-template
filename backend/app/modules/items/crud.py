"""
物品管理模块CRUD操作
"""
import uuid
from typing import Any

from sqlmodel import Session, select

from .models import Item, ItemCreate, ItemUpdate


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    """创建物品"""
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_item_by_id(*, session: Session, item_id: uuid.UUID) -> Item | None:
    """根据ID获取物品"""
    return session.get(Item, item_id)


def get_items_by_owner(*, session: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Item]:
    """获取用户的物品列表"""
    statement = select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_all_items(*, session: Session, skip: int = 0, limit: int = 100) -> list[Item]:
    """获取所有物品（管理员用）"""
    statement = select(Item).offset(skip).limit(limit)
    return session.exec(statement).all()


def update_item(*, session: Session, db_item: Item, item_in: ItemUpdate) -> Item:
    """更新物品"""
    item_data = item_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(item_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_item(*, session: Session, db_item: Item) -> None:
    """删除物品"""
    session.delete(db_item)
    session.commit()
