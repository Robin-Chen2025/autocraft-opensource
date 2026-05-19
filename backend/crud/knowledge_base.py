"""
Knowledge Base 数据库 CRUD 操作模块
AutoCraft 知识库系统 - Knowledge Base 数据操作层
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_
from models.knowledge_base import KnowledgeBase
from schemas.knowledge import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseSearchFilter


def create_knowledge(db: Session, knowledge_data: KnowledgeBaseCreate) -> KnowledgeBase:
    """
    创建知识条目
    
    Args:
        db: 数据库会话
        knowledge_data: 知识创建数据
    
    Returns:
        创建的 KnowledgeBase 对象
    """
    db_knowledge = KnowledgeBase(
        issue_id=knowledge_data.issue_id,
        issue_no=knowledge_data.issue_no,
        title=knowledge_data.title,
        description=knowledge_data.description,
        category=knowledge_data.category.value if hasattr(knowledge_data.category, 'value') else str(knowledge_data.category),
        solution=knowledge_data.solution,
        solution_process=knowledge_data.solution_process,
        root_cause=knowledge_data.root_cause,
        solution_approach=knowledge_data.solution_approach,
        lessons_learned=knowledge_data.lessons_learned,
        prevention_measures=knowledge_data.prevention_measures,
        is_featured=knowledge_data.is_featured or False,
        view_count=0,
        reference_count=0,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_knowledge)
    db.commit()
    db.refresh(db_knowledge)
    return db_knowledge


def get_knowledge_by_id(db: Session, knowledge_id: int) -> Optional[KnowledgeBase]:
    """
    根据知识 ID 获取知识条目
    
    Args:
        db: 数据库会话
        knowledge_id: 知识 ID
    
    Returns:
        KnowledgeBase 对象，不存在则返回 None
    """
    return db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id).first()


def get_knowledge_by_issue_id(db: Session, issue_id: int) -> Optional[KnowledgeBase]:
    """
    根据 Issue ID 获取知识条目
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
    
    Returns:
        KnowledgeBase 对象，不存在则返回 None
    """
    return db.query(KnowledgeBase).filter(KnowledgeBase.issue_id == issue_id).first()


def get_knowledge_by_issue_no(db: Session, issue_no: str) -> Optional[KnowledgeBase]:
    """
    根据 Issue 编号获取知识条目
    
    Args:
        db: 数据库会话
        issue_no: Issue 编号
    
    Returns:
        KnowledgeBase 对象，不存在则返回 None
    """
    return db.query(KnowledgeBase).filter(KnowledgeBase.issue_no == issue_no).first()


def search_knowledge(db: Session, params: KnowledgeBaseSearchFilter) -> tuple[list[KnowledgeBase], int]:
    """
    搜索知识条目（支持分页和多字段组合搜索）
    
    Args:
        db: 数据库会话
        params: 搜索参数
    
    Returns:
        (KnowledgeBase 列表，总记录数)
    """
    query = db.query(KnowledgeBase)
    
    # 关键词搜索（标题、描述、解决方案、经验总结）
    if params.keyword:
        query = query.filter(
            or_(
                KnowledgeBase.title.contains(params.keyword),
                KnowledgeBase.description.contains(params.keyword),
                KnowledgeBase.solution.contains(params.keyword),
                KnowledgeBase.solution_process.contains(params.keyword),
                KnowledgeBase.root_cause.contains(params.keyword),
                KnowledgeBase.solution_approach.contains(params.keyword),
                KnowledgeBase.lessons_learned.contains(params.keyword),
                KnowledgeBase.prevention_measures.contains(params.keyword)
            )
        )
    
    # 分类筛选
    if params.category:
        category_value = params.category.value if hasattr(params.category, 'value') else str(params.category)
        query = query.filter(KnowledgeBase.category == category_value)
    
    # 是否精选筛选
    if params.is_featured is not None:
        query = query.filter(KnowledgeBase.is_featured == params.is_featured)
    
    # 计算总记录数
    total = query.count()
    
    # 分页和排序（按创建时间倒序）
    offset = (params.page - 1) * params.page_size
    knowledge_list = query.order_by(desc(KnowledgeBase.created_at)).offset(offset).limit(params.page_size).all()
    
    return knowledge_list, total


def update_knowledge(db: Session, knowledge: KnowledgeBase, knowledge_update: KnowledgeBaseUpdate) -> KnowledgeBase:
    """
    更新知识条目
    
    Args:
        db: 数据库会话
        knowledge: KnowledgeBase 对象
        knowledge_update: 知识更新数据
    
    Returns:
        更新后的 KnowledgeBase 对象
    """
    update_data = knowledge_update.model_dump(exclude_unset=True)
    
    # 处理枚举类型的转换
    if 'category' in update_data and update_data['category'] is not None:
        update_data['category'] = update_data['category'].value if hasattr(update_data['category'], 'value') else str(update_data['category'])
    
    # 更新时间
    update_data['updated_at'] = datetime.now()
    
    # 更新字段
    for field, value in update_data.items():
        setattr(knowledge, field, value)
    
    db.commit()
    db.refresh(knowledge)
    return knowledge


def mark_as_featured(db: Session, knowledge: KnowledgeBase, is_featured: bool, 
                     featured_by: Optional[str] = None) -> KnowledgeBase:
    """
    标记知识条目为精选
    
    Args:
        db: 数据库会话
        knowledge: KnowledgeBase 对象
        is_featured: 是否精选
        featured_by: 操作人
    
    Returns:
        更新后的 KnowledgeBase 对象
    """
    knowledge.is_featured = is_featured
    knowledge.updated_at = datetime.now()
    
    # 可以记录操作人和操作时间（如果模型中有这些字段）
    # 这里根据实际需求可以扩展
    
    db.commit()
    db.refresh(knowledge)
    return knowledge


def increment_view_count(db: Session, knowledge: KnowledgeBase) -> KnowledgeBase:
    """
    增加浏览次数
    
    Args:
        db: 数据库会话
        knowledge: KnowledgeBase 对象
    
    Returns:
        更新后的 KnowledgeBase 对象
    """
    knowledge.view_count = knowledge.view_count + 1
    knowledge.updated_at = datetime.now()
    db.commit()
    db.refresh(knowledge)
    return knowledge


def delete_knowledge(db: Session, knowledge: KnowledgeBase) -> None:
    """
    删除知识条目
    
    Args:
        db: 数据库会话
        knowledge: KnowledgeBase 对象
    """
    db.delete(knowledge)
    db.commit()


def knowledge_exists(db: Session, knowledge_id: int) -> bool:
    """
    检查知识条目是否存在
    
    Args:
        db: 数据库会话
        knowledge_id: 知识 ID
    
    Returns:
        True 如果存在，否则 False
    """
    return get_knowledge_by_id(db, knowledge_id) is not None


def get_featured_knowledge(db: Session, category: Optional[str] = None, 
                           limit: int = 10) -> list[KnowledgeBase]:
    """
    获取精选知识条目
    
    Args:
        db: 数据库会话
        category: 可选的分类筛选
        limit: 返回数量限制
    
    Returns:
        精选知识条目列表
    """
    query = db.query(KnowledgeBase).filter(KnowledgeBase.is_featured == True)
    
    if category:
        query = query.filter(KnowledgeBase.category == category)
    
    return query.order_by(desc(KnowledgeBase.created_at)).limit(limit).all()


def get_knowledge_by_category(db: Session, category: str, 
                              status: Optional[str] = None) -> list[KnowledgeBase]:
    """
    按分类获取知识条目
    
    Args:
        db: 数据库会话
        category: 分类
        status: 可选的状态筛选
    
    Returns:
        知识条目列表
    """
    query = db.query(KnowledgeBase).filter(KnowledgeBase.category == category)
    
    # 注意：KnowledgeBase 模型中没有 status 字段，这里保留参数供未来扩展
    # 如果后续添加该字段，可以取消注释
    # if status:
    #     query = query.filter(KnowledgeBase.status == status)
    
    return query.order_by(desc(KnowledgeBase.created_at)).all()


def get_popular_knowledge(db: Session, limit: int = 10) -> list[KnowledgeBase]:
    """
    获取热门知识条目（按浏览次数排序）
    
    Args:
        db: 数据库会话
        limit: 返回数量限制
    
    Returns:
        热门知识条目列表
    """
    return db.query(KnowledgeBase).order_by(
        desc(KnowledgeBase.view_count)
    ).limit(limit).all()
