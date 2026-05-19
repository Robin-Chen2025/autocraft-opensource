"""
Issue 模块 Pydantic Schema 定义
AutoCraft 问题跟踪系统 - Pydantic v2 数据验证模型
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# 枚举定义
# ============================================================================

class IssueStatus(str, Enum):
    """问题状态枚举"""
    NEW = "新建"
    IN_PROGRESS = "处理中"
    RESOLVED = "已解决"
    CLOSED = "已关闭"


class IssuePriority(str, Enum):
    """优先级枚举"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class IssueCategory(str, Enum):
    """问题分类枚举"""
    BUG = "Bug"
    OPTIMIZATION = "优化"
    REQUIREMENT = "需求"
    OTHER = "其他"
    
    # FlowTicket 异常分类
    PYTEST_LIMIT = "pytest_limit"
    GUARDIAN_LIMIT = "guardian_limit"
    VERIFY_LIMIT = "verify_limit"
    TIMEOUT = "timeout"
    EXECUTION_TIMEOUT = "execution_timeout"
    RETRY_LIMIT = "retry_limit"
    CONFIG_MISSING = "config_missing"
    CODE_ERROR = "code_error"
    ENV_ERROR = "env_error"
    MANUAL_INTERVENTION = "manual_intervention"


# ============================================================================
# 基础模型
# ============================================================================

class IssueBase(BaseModel):
    """Issue 基础模型"""
    title: str = Field(..., max_length=100, description="问题标题")
    description: Optional[str] = Field(None, description="问题描述")
    category: IssueCategory = Field(..., description="问题分类")
    priority: IssuePriority = Field(..., description="优先级")
    related_task_id: Optional[str] = Field(None, description="关联任务单号")


# ============================================================================
# 请求模型
# ============================================================================

class IssueCreate(IssueBase):
    """创建 Issue 请求模型"""
    project_id: int = Field(..., description="项目 ID")
    stage_id: Optional[int] = Field(None, description="阶段 ID")
    workflow_id: Optional[int] = Field(None, description="工作流 ID")
    created_by: str = Field(..., description="创建人")


class IssueUpdate(BaseModel):
    """更新 Issue 请求模型（所有字段可选）"""
    title: Optional[str] = Field(None, max_length=100, description="问题标题")
    description: Optional[str] = Field(None, description="问题描述")
    category: Optional[IssueCategory] = Field(None, description="问题分类")
    priority: Optional[IssuePriority] = Field(None, description="优先级")
    status: Optional[IssueStatus] = Field(None, description="状态")
    related_task_id: Optional[str] = Field(None, description="关联任务单号")
    assignee: Optional[str] = Field(None, max_length=100, description="处理人")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    assign_note: Optional[str] = Field(None, description="分配说明")


class IssueResolveRequest(BaseModel):
    """解决 Issue 请求模型"""
    solution: str = Field(..., description="解决方案")
    solution_process: Optional[str] = Field(None, description="解决过程")
    resolved_by: str = Field(..., description="解决人")


class IssueCloseRequest(BaseModel):
    """关闭 Issue 请求模型"""
    closed_by: str = Field(..., description="关闭人")
    closed_reason: Optional[str] = Field(None, description="关闭原因")


class FlowTicketIssueCreate(BaseModel):
    """FlowTicket 自动创建问题单请求模型"""
    source: str = Field(default="flow_ticket", description="来源，固定为 flow_ticket")
    error_type: str = Field(..., description="错误类型 (pytest_limit/timeout等)")
    error_message: str = Field(..., description="异常消息")
    task_id: Optional[str] = Field(None, description="关联任务ID")
    node_id: Optional[str] = Field(None, description="当前节点ID")
    recovery_info: Optional[str] = Field(None, description="恢复信息")
    project_id: int = Field(..., description="项目 ID")
    created_by: str = Field(default="system_auto", description="创建人，默认为 system_auto")


class IssueAssignRequest(BaseModel):
    """分配 Issue 请求模型"""
    assignee: str = Field(..., max_length=100, description="处理人")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    assign_note: Optional[str] = Field(None, description="分配说明")


# ============================================================================
# 响应模型
# ============================================================================

class IssueResponse(IssueBase):
    """Issue 响应模型"""
    id: int = Field(..., description="Issue ID")
    issue_no: str = Field(..., description="问题编号")
    status: IssueStatus = Field(..., description="状态")
    project_id: int = Field(..., description="项目 ID")
    stage_id: Optional[int] = Field(None, description="阶段 ID")
    workflow_id: Optional[int] = Field(None, description="工作流 ID")
    assignee: Optional[str] = Field(None, description="处理人")
    assigned_at: Optional[datetime] = Field(None, description="分配时间")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    assign_note: Optional[str] = Field(None, description="分配说明")
    solution_process: Optional[str] = Field(None, description="解决过程")
    solution: Optional[str] = Field(None, description="解决方案")
    resolved_by: Optional[str] = Field(None, description="解决人")
    resolved_at: Optional[datetime] = Field(None, description="解决时间")
    closed_by: Optional[str] = Field(None, description="关闭人")
    closed_at: Optional[datetime] = Field(None, description="关闭时间")
    created_by: str = Field(..., description="创建人")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class IssueListResponse(BaseModel):
    """Issue 列表响应模型"""
    total: int = Field(..., description="总记录数")
    items: List[IssueResponse] = Field(..., description="Issue 列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class IssueDetailResponse(BaseModel):
    """Issue 详情响应模型"""
    data: IssueResponse = Field(..., description="Issue 详情")


# ============================================================================
# 查询参数模型
# ============================================================================

class IssueFilter(BaseModel):
    """Issue 筛选条件模型"""
    page: int = Field(default=1, ge=1, le=1000, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    status: Optional[IssueStatus] = Field(None, description="状态筛选")
    priority: Optional[IssuePriority] = Field(None, description="优先级筛选")
    category: Optional[IssueCategory] = Field(None, description="分类筛选")
    creator: Optional[str] = Field(None, description="创建人筛选")
    assignee: Optional[str] = Field(None, description="处理人筛选")
    keyword: Optional[str] = Field(None, description="关键字搜索（标题/描述）")
    project_id: Optional[int] = Field(None, description="项目 ID 筛选")
    stage_id: Optional[int] = Field(None, description="阶段 ID 筛选")
    workflow_id: Optional[int] = Field(None, description="工作流 ID 筛选")
    related_task_id: Optional[str] = Field(None, description="关联任务单号筛选")
    created_at_from: Optional[datetime] = Field(None, description="创建时间起始")
    created_at_to: Optional[datetime] = Field(None, description="创建时间结束")


# ============================================================================
# 通用响应模型
# ============================================================================

class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str = Field(..., description="消息内容")
    issue_no: Optional[str] = Field(None, description="问题编号")
