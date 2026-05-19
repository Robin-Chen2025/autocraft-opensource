"""
问题管理基础 API 接口模块
AutoCraft 问题跟踪系统 - Issue RESTful API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from crud.issue import (
    create_issue,
    get_issue_by_id,
    get_issues,
    update_issue,
    delete_issue
)
from schemas.issue import (
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueListResponse,
    IssueDetailResponse,
    MessageResponse,
    IssueFilter,
    FlowTicketIssueCreate,
    IssueCategory,
    IssuePriority
)

router = APIRouter(prefix="/issues", tags=["问题管理"])


# ============================================================================
# 创建 Issue
# ============================================================================

@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_issue_api(issue_data: IssueCreate, db: Session = Depends(get_db)):
    """
    创建新问题

    - 自动生成问题编号（格式：ISSUE-YYYYMMDD-NNNN）
    - 标题和创建人为必填项
    - 初始状态为"新建"
    """
    try:
        issue = create_issue(db, issue_data)
        return MessageResponse(
            message="问题创建成功",
            issue_no=issue.issue_no
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建问题失败：{str(e)}"
        )


# ============================================================================
# 获取 Issue 列表
# ============================================================================

@router.get("", response_model=IssueListResponse)
def get_issues_api(
    page: int = Query(1, ge=1, le=1000, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    priority: Optional[str] = Query(None, description="优先级筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    creator: Optional[str] = Query(None, description="创建人筛选"),
    assignee: Optional[str] = Query(None, description="处理人筛选"),
    keyword: Optional[str] = Query(None, description="关键字搜索（标题/描述）"),
    project_id: Optional[int] = Query(None, description="项目 ID 筛选"),
    stage_id: Optional[int] = Query(None, description="阶段 ID 筛选"),
    workflow_id: Optional[int] = Query(None, description="工作流 ID 筛选"),
    related_task_id: Optional[str] = Query(None, description="关联任务单号筛选"),
    created_at_from: Optional[str] = Query(None, description="创建时间起始"),
    created_at_to: Optional[str] = Query(None, description="创建时间结束"),
    db: Session = Depends(get_db)
):
    """
    获取 Issue 列表

    - 支持分页
    - 支持多字段组合查询（状态、优先级、分类、创建人、处理人）
    - 支持关键字搜索（标题/描述）
    - 支持日期范围查询
    - 返回结果按创建时间倒序排列
    """
    from datetime import datetime

    # 解析日期参数
    created_at_from_dt = None
    created_at_to_dt = None

    if created_at_from:
        try:
            created_at_from_dt = datetime.fromisoformat(created_at_from)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="created_at_from 格式错误，应为 ISO 格式（如：2024-01-01T00:00:00）"
            )

    if created_at_to:
        try:
            created_at_to_dt = datetime.fromisoformat(created_at_to)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="created_at_to 格式错误，应为 ISO 格式（如：2024-01-01T00:00:00）"
            )

    # 构建查询参数
    params = IssueFilter(
        page=page,
        page_size=page_size,
        status=status_filter,
        priority=priority,
        category=category,
        creator=creator,
        assignee=assignee,
        keyword=keyword,
        project_id=project_id,
        stage_id=stage_id,
        workflow_id=workflow_id,
        related_task_id=related_task_id,
        created_at_from=created_at_from_dt,
        created_at_to=created_at_to_dt
    )

    try:
        issues, total = get_issues(db, params)
        total_pages = (total + page_size - 1) // page_size

        return IssueListResponse(
            total=total,
            items=issues,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取问题列表失败：{str(e)}"
        )


# ============================================================================
# 获取 Issue 详情
# ============================================================================

@router.get("/{issue_id}", response_model=IssueDetailResponse)
def get_issue_api(issue_id: int, db: Session = Depends(get_db)):
    """
    获取 Issue 详情

    - 根据 Issue ID 查询
    - 返回完整的问题信息
    """
    issue = get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题不存在：{issue_id}"
        )
    return IssueDetailResponse(data=issue)


# ============================================================================
# 更新 Issue
# ============================================================================

@router.put("/{issue_id}", response_model=MessageResponse)
def update_issue_api(issue_id: int, issue_update: IssueUpdate, db: Session = Depends(get_db)):
    """
    更新 Issue

    - 根据 Issue ID 更新
    - 只更新提供的字段
    - 状态变更时自动记录时间（处理中→分配时间，已解决→解决时间，已关闭→关闭时间）
    """
    issue = get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题不存在：{issue_id}"
        )

    try:
        update_issue(db, issue, issue_update)
        return MessageResponse(
            message="问题更新成功",
            issue_no=issue.issue_no
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新问题失败：{str(e)}"
        )


# ============================================================================
# 删除 Issue
# ============================================================================

@router.delete("/{issue_id}", response_model=MessageResponse)
def delete_issue_api(issue_id: int, db: Session = Depends(get_db)):
    """
    删除 Issue

    - 根据 Issue ID 删除
    - 级联删除相关的状态日志、分配日志、任务关联等
    """
    issue = get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题不存在：{issue_id}"
        )

    try:
        delete_issue(db, issue)
        return MessageResponse(
            message="问题删除成功",
            issue_no=issue.issue_no
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除问题失败：{str(e)}"
        )


# ============================================================================
# FlowTicket 自动创建 Issue
# ============================================================================

@router.post("/auto-create", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_flow_ticket_issue_api(
    flow_ticket_data: FlowTicketIssueCreate, 
    db: Session = Depends(get_db)
):
    """
    FlowTicket 自动创建问题单
    
    - 供 FlowTicket 引擎调用创建问题单
    - 接收标准化的异常信息
    - 自动映射错误类型到 category 枚举
    - 自动设置优先级（基于错误类型）
    """
    try:
        # 映射错误类型到 IssueCategory
        category_map = {
            "pytest_limit": IssueCategory.PYTEST_LIMIT,
            "guardian_limit": IssueCategory.GUARDIAN_LIMIT,
            "verify_limit": IssueCategory.VERIFY_LIMIT,
            "timeout": IssueCategory.TIMEOUT,
            "execution_timeout": IssueCategory.EXECUTION_TIMEOUT,
            "retry_limit": IssueCategory.RETRY_LIMIT,
            "config_missing": IssueCategory.CONFIG_MISSING,
            "code_error": IssueCategory.CODE_ERROR,
            "env_error": IssueCategory.ENV_ERROR,
            "manual_intervention": IssueCategory.MANUAL_INTERVENTION
        }
        
        # 获取对应的 category，如果不在映射表中，使用 OTHER
        category = category_map.get(flow_ticket_data.error_type, IssueCategory.OTHER)
        
        # 基于错误类型设置优先级
        priority_map = {
            IssueCategory.TIMEOUT.value: IssuePriority.HIGH,
            IssueCategory.EXECUTION_TIMEOUT.value: IssuePriority.HIGH,
            IssueCategory.MANUAL_INTERVENTION.value: IssuePriority.HIGH,
            IssueCategory.CODE_ERROR.value: IssuePriority.MEDIUM,
            IssueCategory.ENV_ERROR.value: IssuePriority.MEDIUM,
            IssueCategory.CONFIG_MISSING.value: IssuePriority.MEDIUM,
            IssueCategory.PYTEST_LIMIT.value: IssuePriority.LOW,
            IssueCategory.GUARDIAN_LIMIT.value: IssuePriority.LOW,
            IssueCategory.VERIFY_LIMIT.value: IssuePriority.LOW,
            IssueCategory.RETRY_LIMIT.value: IssuePriority.LOW
        }
        priority = priority_map.get(category.value, IssuePriority.MEDIUM)
        
        # 构建 IssueCreate 数据
        issue_title = f"FlowTicket异常: {flow_ticket_data.error_type}"
        
        # 构建详细的描述信息
        description_lines = [
            f"**异常来源:** {flow_ticket_data.source}",
            f"**错误类型:** {flow_ticket_data.error_type}",
            f"**异常消息:** {flow_ticket_data.error_message}",
        ]
        
        if flow_ticket_data.task_id:
            description_lines.append(f"**关联任务:** {flow_ticket_data.task_id}")
        
        if flow_ticket_data.node_id:
            description_lines.append(f"**当前节点:** {flow_ticket_data.node_id}")
        
        if flow_ticket_data.recovery_info:
            description_lines.append(f"**恢复信息:** {flow_ticket_data.recovery_info}")
        
        issue_description = "\n\n".join(description_lines)
        
        # 创建 IssueCreate 对象
        issue_data = IssueCreate(
            title=issue_title,
            description=issue_description,
            category=category,
            priority=priority,
            related_task_id=flow_ticket_data.task_id,
            project_id=flow_ticket_data.project_id,
            stage_id=None,
            workflow_id=None,
            created_by=flow_ticket_data.created_by
        )
        
        # 调用现有的创建接口
        issue = create_issue(db, issue_data)
        
        return MessageResponse(
            message="FlowTicket问题单创建成功",
            issue_no=issue.issue_no
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"请求数据验证失败：{str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建FlowTicket问题单失败：{str(e)}"
        )
