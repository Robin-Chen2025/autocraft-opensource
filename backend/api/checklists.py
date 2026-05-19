"""
Checklist 管理基础 API 接口模块
AutoCraft 检查清单系统 - Checklist RESTful API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from crud.checklist import (
    create_checklist,
    get_checklist,
    get_checklists,
    update_checklist,
    delete_checklist
)
from schemas.checklist import (
    ChecklistCreate,
    ChecklistUpdate,
    ChecklistResponse,
    ChecklistListResponse,
    ChecklistDetailResponse,
    MessageResponse,
    ChecklistFilter
)

router = APIRouter(prefix="/checklists", tags=["检查清单管理"])


# ============================================================================
# 创建 Checklist
# ============================================================================

@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_checklist_api(checklist_data: ChecklistCreate, db: Session = Depends(get_db)):
    """
    创建检查清单

    - checklist_id 为语义化 ID（如 "api-design", "code-quality"）
    - 名称和分类为必填项
    - 检查项默认为空 JSON 数组
    """
    try:
        checklist = create_checklist(db, checklist_data)
        return MessageResponse(
            message="检查清单创建成功",
            checklist_id=checklist.checklist_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建检查清单失败：{str(e)}"
        )


# ============================================================================
# 获取 Checklist 列表
# ============================================================================

@router.get("", response_model=ChecklistListResponse)
def get_checklists_api(
    page: int = Query(1, ge=1, le=1000, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类筛选"),
    keyword: Optional[str] = Query(None, description="关键字搜索（名称/描述）"),
    db: Session = Depends(get_db)
):
    """
    获取 Checklist 列表

    - 支持分页
    - 支持分类筛选
    - 支持关键字搜索（名称/描述）
    - 返回结果按创建时间倒序排列
    """
    # 构建查询参数
    params = ChecklistFilter(
        page=page,
        page_size=page_size,
        category=category,
        keyword=keyword
    )

    try:
        checklists, total = get_checklists(db, params)
        total_pages = (total + page_size - 1) // page_size

        return ChecklistListResponse(
            total=total,
            items=checklists,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取检查清单列表失败：{str(e)}"
        )


# ============================================================================
# 获取 Checklist 详情
# ============================================================================

@router.get("/{checklist_id}", response_model=ChecklistDetailResponse)
def get_checklist_api(checklist_id: str, db: Session = Depends(get_db)):
    """
    获取 Checklist 详情

    - 根据 Checklist ID 查询
    - 返回完整的检查清单信息
    """
    checklist = get_checklist(db, checklist_id)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"检查清单不存在：{checklist_id}"
        )
    return ChecklistDetailResponse(data=checklist)


# ============================================================================
# 更新 Checklist
# ============================================================================

@router.put("/{checklist_id}", response_model=MessageResponse)
def update_checklist_api(checklist_id: str, checklist_update: ChecklistUpdate, db: Session = Depends(get_db)):
    """
    更新 Checklist

    - 根据 Checklist ID 更新
    - 只更新提供的字段
    - 自动更新 updated_at 时间戳
    """
    checklist = get_checklist(db, checklist_id)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"检查清单不存在：{checklist_id}"
        )

    try:
        update_checklist(db, checklist, checklist_update)
        return MessageResponse(
            message="检查清单更新成功",
            checklist_id=checklist.checklist_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新检查清单失败：{str(e)}"
        )


# ============================================================================
# 删除 Checklist
# ============================================================================

@router.delete("/{checklist_id}", response_model=MessageResponse)
def delete_checklist_api(checklist_id: str, db: Session = Depends(get_db)):
    """
    删除 Checklist

    - 根据 Checklist ID 删除
    - 删除检查清单记录
    """
    checklist = get_checklist(db, checklist_id)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"检查清单不存在：{checklist_id}"
        )

    try:
        delete_checklist(db, checklist)
        return MessageResponse(
            message="检查清单删除成功",
            checklist_id=checklist.checklist_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除检查清单失败：{str(e)}"
        )
