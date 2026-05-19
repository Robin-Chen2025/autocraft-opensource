"""
Knowledge Reference 数据库 CRUD 操作模块
AutoCraft 知识库系统 - Knowledge Reference 数据操作层
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.knowledge_reference import KnowledgeReference
from models.knowledge_base import KnowledgeBase


def create_reference(
    db: Session,
    knowledge_id: int,
    referenced_by: str,
    reference_context: Optional[str] = None
) -> KnowledgeReference:
    """
    创建知识引用记录并自动更新 knowledge_base 的 reference_count
    
    Args:
        db: 数据库会话
        knowledge_id: 被引用的知识条目 ID
        referenced_by: 引用者标识（如 issue_id 或其他资源 ID）
        reference_context: 引用上下文，描述引用的具体场景或内容
    
    Returns:
        创建的 KnowledgeReference 对象
    
    Raises:
        ValueError: 如果知识条目不存在
    """
    # 检查知识条目是否存在
    knowledge = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id).first()
    if not knowledge:
        raise ValueError(f"Knowledge entry with id {knowledge_id} does not exist")
    
    # 创建引用记录
    db_reference = KnowledgeReference(
        knowledge_id=knowledge_id,
        referenced_by=referenced_by,
        reference_context=reference_context,
        created_at=datetime.now()
    )
    db.add(db_reference)
    
    # 自动更新 knowledge_base 的 reference_count
    knowledge.reference_count = knowledge.reference_count + 1
    knowledge.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_reference)
    return db_reference


def get_references_by_knowledge_id(
    db: Session,
    knowledge_id: int,
    limit: int = 100
) -> list[KnowledgeReference]:
    """
    根据知识 ID 获取引用记录列表
    
    Args:
        db: 数据库会话
        knowledge_id: 知识 ID
        limit: 返回数量限制，默认 100
    
    Returns:
        KnowledgeReference 对象列表
    """
    return db.query(KnowledgeReference).filter(
        KnowledgeReference.knowledge_id == knowledge_id
    ).order_by(
        desc(KnowledgeReference.created_at)
    ).limit(limit).all()
