"""
知识库管理 API 接口模块
AutoCraft 知识库系统 - Knowledge RESTful API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from crud.knowledge_base import search_knowledge, get_knowledge_by_id, increment_view_count, mark_as_featured
from crud.knowledge_reference import create_reference
from schemas.knowledge import KnowledgeBaseSearchFilter, KnowledgeBaseListResponse, KnowledgeBaseResponse, KnowledgeFeatureRequest, KnowledgeReferenceRequest

router = APIRouter(prefix="/knowledge", tags=["知识库管理"])


# ============================================================================
# 搜索知识库
# ============================================================================

@router.get("", response_model=KnowledgeBaseListResponse)
def search_knowledge_api(
    keyword: Optional[str] = Query(None, description="关键词搜索（标题/描述/解决方案等）"),
    category: Optional[str] = Query(None, description="分类筛选"),
    is_featured: Optional[bool] = Query(None, description="仅优质"),
    page: int = Query(1, ge=1, le=1000, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    搜索知识库

    - 支持分页
    - 支持关键词全文搜索（标题、描述、解决方案、解决过程、根本原因、解决方法、经验总结、预防措施）
    - 支持分类筛选
    - 支持仅显示优质内容
    - 返回结果按创建时间倒序排列
    """
    # 构建搜索参数
    params = KnowledgeBaseSearchFilter(
        page=page,
        page_size=page_size,
        keyword=keyword,
        category=category,
        is_featured=is_featured
    )

    try:
        knowledge_list, total = search_knowledge(db, params)
        total_pages = (total + page_size - 1) // page_size

        return KnowledgeBaseListResponse(
            total=total,
            items=knowledge_list,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索知识库失败：{str(e)}"
        )


# ============================================================================
# 获取知识详情
# ============================================================================

@router.get("/{id}", response_model=KnowledgeBaseResponse)
def get_knowledge_detail(
    id: int,
    db: Session = Depends(get_db)
):
    """
    获取知识详情

    - 根据知识 ID 获取完整知识信息
    - 自动增加浏览次数
    - 返回知识条目的所有字段信息
    """
    knowledge = get_knowledge_by_id(db, id)
    
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"知识条目不存在：ID={id}"
        )
    
    try:
        # 自动增加浏览次数
        increment_view_count(db, knowledge)
        
        return knowledge
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识详情失败：{str(e)}"
        )


# ============================================================================
# 标记优质知识
# ============================================================================

@router.put("/{id}/feature", response_model=KnowledgeBaseResponse)
def mark_knowledge_feature(
    id: int,
    request: KnowledgeFeatureRequest,
    db: Session = Depends(get_db),
    x_agent_role: Optional[str] = Header(None, alias="X-Agent-Role", description="代理角色")
):
    """
    标记知识条目为优质内容

    - 需要权限校验：仅管理员 可操作
    - 支持标记/取消标记优质
    - 自动记录操作人和操作时间
    """
    # 权限校验：仅允许管理员 操作
    if not x_agent_role or x_agent_role not in ["主代理", "管理员"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：仅管理员 可标记优质知识"
        )
    
    # 获取知识条目
    knowledge = get_knowledge_by_id(db, id)
    
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"知识条目不存在：ID={id}"
        )
    
    try:
        # 标记优质
        updated_knowledge = mark_as_featured(db, knowledge, request.is_featured, featured_by=x_agent_role)
        
        return updated_knowledge
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"标记优质知识失败：{str(e)}"
        )


# ============================================================================
# 记录知识引用
# ============================================================================

@router.post("/{id}/reference", response_model=KnowledgeBaseResponse)
def record_knowledge_reference(
    id: int,
    request: KnowledgeReferenceRequest,
    db: Session = Depends(get_db)
):
    """
    记录知识引用

    - 记录知识条目被引用的情况
    - 自动更新知识条目的引用次数
    - 引用上下文描述引用的具体场景或内容
    """
    # 获取知识条目（验证是否存在）
    knowledge = get_knowledge_by_id(db, id)
    
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"知识条目不存在：ID={id}"
        )
    
    try:
        # 创建引用记录（自动更新 reference_count）
        reference = create_reference(
            db=db,
            knowledge_id=id,
            referenced_by=request.referenced_by,
            reference_context=request.reference_context
        )
        
        # 返回更新后的知识条目（包含最新的引用次数）
        return knowledge
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录知识引用失败：{str(e)}"
        )
