"""
Checklist 数据库 CRUD 操作模块
AutoCraft 检查清单管理 - Checklist 数据操作层
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from models.checklist import Checklist
from schemas.checklist import ChecklistCreate, ChecklistUpdate, ChecklistFilter


def create_checklist(db: Session, checklist_data: ChecklistCreate) -> Checklist:
    """
    创建 Checklist

    Args:
        db: 数据库会话
        checklist_data: Checklist 创建数据

    Returns:
        创建的 Checklist 对象
    """
    db_checklist = Checklist(
        checklist_id=checklist_data.checklist_id,
        name=checklist_data.name,
        description=checklist_data.description,
        category=checklist_data.category.value if hasattr(checklist_data.category, 'value') else str(checklist_data.category),
        items=checklist_data.items,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_checklist)
    db.commit()
    db.refresh(db_checklist)
    return db_checklist


def get_checklist(db: Session, checklist_id: str) -> Optional[Checklist]:
    """
    根据 Checklist ID 获取 Checklist

    Args:
        db: 数据库会话
        checklist_id: Checklist ID

    Returns:
        Checklist 对象，不存在则返回 None
    """
    return db.query(Checklist).filter(Checklist.checklist_id == checklist_id).first()


def get_checklists(db: Session, params: ChecklistFilter) -> tuple[list[Checklist], int]:
    """
    获取 Checklist 列表（支持分页和多字段组合搜索）

    Args:
        db: 数据库会话
        params: Checklist 查询参数

    Returns:
        (Checklist 列表，总记录数)
    """
    query = db.query(Checklist)

    # 关键词搜索（名称和描述）
    if params.keyword:
        query = query.filter(
            or_(
                Checklist.name.contains(params.keyword),
                Checklist.description.contains(params.keyword)
            )
        )

    # 分类筛选
    if params.category:
        category_value = params.category.value if hasattr(params.category, 'value') else str(params.category)
        query = query.filter(Checklist.category == category_value)

    # 计算总记录数
    total = query.count()

    # 分页和排序（按创建时间倒序）
    offset = (params.page - 1) * params.page_size
    checklists = query.order_by(desc(Checklist.created_at)).offset(offset).limit(params.page_size).all()

    return checklists, total


def update_checklist(db: Session, checklist: Checklist, checklist_update: ChecklistUpdate) -> Checklist:
    """
    更新 Checklist

    Args:
        db: 数据库会话
        checklist: Checklist 对象
        checklist_update: Checklist 更新数据

    Returns:
        更新后的 Checklist 对象
    """
    update_data = checklist_update.model_dump(exclude_unset=True)

    # 处理枚举类型的转换
    if 'category' in update_data and update_data['category'] is not None:
        update_data['category'] = update_data['category'].value if hasattr(update_data['category'], 'value') else str(update_data['category'])

    # 更新时间
    update_data['updated_at'] = datetime.now()

    # 更新字段
    for field, value in update_data.items():
        setattr(checklist, field, value)

    db.commit()
    db.refresh(checklist)
    return checklist


def delete_checklist(db: Session, checklist: Checklist) -> None:
    """
    删除 Checklist

    Args:
        db: 数据库会话
        checklist: Checklist 对象

    Note:
        删除 Checklist 记录
    """
    db.delete(checklist)
    db.commit()


def checklist_exists(db: Session, checklist_id: str) -> bool:
    """
    检查 Checklist 是否存在

    Args:
        db: 数据库会话
        checklist_id: Checklist ID

    Returns:
        True 如果存在，否则 False
    """
    return get_checklist(db, checklist_id) is not None


def get_checklists_by_category(db: Session, category: str) -> list[Checklist]:
    """
    按分类查询 Checklist

    Args:
        db: 数据库会话
        category: 分类

    Returns:
        Checklist 列表
    """
    return db.query(Checklist).filter(Checklist.category == category).order_by(desc(Checklist.created_at)).all()
