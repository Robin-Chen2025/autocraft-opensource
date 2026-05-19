"""
Pydantic 模型定义（请求/响应数据验证）
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ==================== 基础模型 ====================

class TaskBase(BaseModel):
    """任务基础模型"""
    plan_id: Optional[str] = Field(None, description="工作计划ID")
    task_name: str = Field(..., min_length=1, max_length=200, description="任务名称")
    task_type: Optional[str] = Field(None, description="任务类型")
    plan_date: Optional[datetime] = Field(None, description="计划日期")
    plan_complete_time: Optional[datetime] = Field(None, description="计划完成时间")
    executor: Optional[str] = Field(None, max_length=100, description="执行人")
    status: str = Field(default="pending", description="状态")
    priority: str = Field(default="medium", description="优先级")
    execution_steps: Optional[str] = Field(None, description="执行步骤")
    expected_result: Optional[str] = Field(None, description="预期结果")
    execution_log: Optional[str] = Field(None, description="执行日志")
    output_result: Optional[str] = Field(None, description="输出结果")
    execution_date: Optional[datetime] = Field(None, description="执行日期")
    verification_result: str = Field(default="待验证", description="验证结论")
    verifier: Optional[str] = Field(None, max_length=100, description="验证人")
    verification_time: Optional[datetime] = Field(None, description="验证时间")
    verification_log: Optional[str] = Field(None, description="验证日志")
    exec_start_time: Optional[datetime] = Field(None, description="执行开始时间")
    exec_estimated_complete: Optional[datetime] = Field(None, description="执行预计完成时间")
    exec_complete_time: Optional[datetime] = Field(None, description="执行实际完成时间")
    verify_start_time: Optional[datetime] = Field(None, description="验证开始时间")
    verify_estimated_complete: Optional[datetime] = Field(None, description="验证预计完成时间")
    verify_complete_time: Optional[datetime] = Field(None, description="验证实际完成时间")


# ==================== 请求模型 ====================

class TaskCreate(TaskBase):
    """创建任务请求模型"""
    task_no: Optional[str] = Field(None, description='任务单号，可选，不传则自动生成')


class TaskUpdate(BaseModel):
    """更新任务请求模型（所有字段可选）"""
    task_name: Optional[str] = Field(None, min_length=1, max_length=200, description="任务名称")
    plan_date: Optional[datetime] = Field(None, description="计划日期")
    plan_complete_time: Optional[datetime] = Field(None, description="计划完成时间")
    executor: Optional[str] = Field(None, max_length=100, description="执行人")
    status: Optional[str] = Field(None, description="状态")
    priority: Optional[str] = Field(None, description="优先级")
    execution_steps: Optional[str] = Field(None, description="执行步骤")
    expected_result: Optional[str] = Field(None, description="预期结果")
    execution_log: Optional[str] = Field(None, description="执行日志")
    output_result: Optional[str] = Field(None, description="输出结果")
    execution_date: Optional[datetime] = Field(None, description="执行日期")
    verification_result: Optional[str] = Field(None, description="验证结论")
    verifier: Optional[str] = Field(None, max_length=100, description="验证人")
    verification_time: Optional[datetime] = Field(None, description="验证时间")
    verification_log: Optional[str] = Field(None, description="验证日志")
    exec_start_time: Optional[datetime] = Field(None, description="执行开始时间")
    exec_estimated_complete: Optional[datetime] = Field(None, description="执行预计完成时间")
    exec_complete_time: Optional[datetime] = Field(None, description="执行实际完成时间")
    verify_start_time: Optional[datetime] = Field(None, description="验证开始时间")
    verify_estimated_complete: Optional[datetime] = Field(None, description="验证预计完成时间")
    verify_complete_time: Optional[datetime] = Field(None, description="验证实际完成时间")


# ==================== 响应模型 ====================

class TaskResponse(TaskBase):
    """任务响应模型"""
    task_type: Optional[str] = Field(None, description="任务类型")
    plan_id: Optional[str] = Field(None, description="工作计划 ID")
    phase_record_id: Optional[str] = Field(None, description="阶段记录 ID")
    agent_id: Optional[str] = Field(None, description="Agent ID")
    locked_by: Optional[str] = Field(None, description="锁定者")
    locked_at: Optional[datetime] = Field(None, description="锁定时间")
    id: int = Field(..., description="任务 ID")
    task_no: str = Field(..., description="任务单号")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    total: int = Field(..., description="总记录数")
    items: list[TaskResponse] = Field(..., description="任务列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class TaskDetailResponse(BaseModel):
    """任务详情响应模型"""
    data: TaskResponse = Field(..., description="任务详情")


class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str = Field(..., description="消息内容")
    task_no: Optional[str] = Field(None, description="任务单号")
    profile_id: Optional[str] = Field(None, description="项目档案ID")
    plan_id: Optional[str] = Field(None, description="计划ID")
    phase_record_id: Optional[str] = Field(None, description="阶段记录ID")


# ==================== 项目档案相关模型 ====================

class ProfileBase(BaseModel):
    """项目档案基础模型"""
    profile_type: str = Field(..., description="档案类型：template=模板，instance=实例")
    profile_name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    project_type: Optional[str] = Field(None, max_length=50, description="项目类型")
    description: Optional[str] = Field(None, description="项目描述")
    tech_stack: Optional[str] = Field(None, max_length=200, description="技术栈")
    root_path: Optional[str] = Field(None, max_length=500, description="项目根路径")
    status: str = Field(default='active', description="状态")


class ProfileCreate(ProfileBase):
    """创建项目档案请求模型"""
    profile_id: Optional[str] = Field(None, max_length=50, description="项目档案 ID（可选，不传则自动生成）")
    # 从模板复制时使用
    template_profile_id: Optional[str] = Field(None, description="模板档案 ID（从模板复制时使用）")


class ProfileUpdate(BaseModel):
    """更新项目档案请求模型（所有字段可选）"""
    profile_name: Optional[str] = Field(None, min_length=1, max_length=100, description="项目名称")
    project_type: Optional[str] = Field(None, max_length=50, description="项目类型")
    description: Optional[str] = Field(None, description="项目描述")
    tech_stack: Optional[str] = Field(None, max_length=200, description="技术栈")
    root_path: Optional[str] = Field(None, max_length=500, description="项目根路径")
    status: Optional[str] = Field(None, description="状态")


class ProfileResponse(ProfileBase):
    """项目档案响应模型"""
    profile_id: str = Field(..., description="项目档案 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class ProfileListResponse(BaseModel):
    """项目档案列表响应模型"""
    total: int = Field(..., description="总记录数")
    items: list[ProfileResponse] = Field(..., description="项目档案列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class PhaseResponse(BaseModel):
    """项目阶段响应模型"""
    phase_record_id: str = Field(..., description="阶段记录 ID")
    profile_id: str = Field(..., description="项目档案 ID")
    phase_id: str = Field(..., description="阶段 ID")
    phase_name: str = Field(..., description="阶段名称")
    phase_order: int = Field(..., description="阶段顺序")
    status: str = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True





# ==================== 查询参数模型 ====================

class TaskQueryParams(BaseModel):
    """任务查询参数模型"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(None, description="搜索关键词（任务名称）")
    task_no: Optional[str] = Field(None, description="任务单号搜索")
    executor: Optional[str] = Field(None, description="执行人搜索")
    verifier: Optional[str] = Field(None, description="验证人搜索")
    status: Optional[str] = Field(None, description="状态筛选（支持多值，逗号分隔）")
    priority: Optional[str] = Field(None, description="优先级筛选（支持多值，逗号分隔）")
    verification_result: Optional[str] = Field(None, description="验证结论筛选（支持多值，逗号分隔）")
    plan_date_start: Optional[str] = Field(None, description="计划日期开始")
    plan_date_end: Optional[str] = Field(None, description="计划日期结束")
    plan_complete_start: Optional[str] = Field(None, description="计划完成时间开始")
    plan_complete_end: Optional[str] = Field(None, description="计划完成时间结束")
    verification_time_start: Optional[str] = Field(None, description="验证时间开始")
    verification_time_end: Optional[str] = Field(None, description="验证时间结束")
    exec_start_time_start: Optional[str] = Field(None, description="执行开始时间开始")
    exec_start_time_end: Optional[str] = Field(None, description="执行开始时间结束")
    exec_complete_time_start: Optional[str] = Field(None, description="执行完成时间开始")
    exec_complete_time_end: Optional[str] = Field(None, description="执行完成时间结束")
    verify_start_time_start: Optional[str] = Field(None, description="验证开始时间开始")
    verify_start_time_end: Optional[str] = Field(None, description="验证开始时间结束")
    verify_complete_time_start: Optional[str] = Field(None, description="验证完成时间开始")
    verify_complete_time_end: Optional[str] = Field(None, description="验证完成时间结束")


# ==================== 工作计划相关模型 ====================

class PlanBase(BaseModel):
    """工作计划基础模型"""
    plan_name: str = Field(..., min_length=1, max_length=100, description="计划名称")
    description: Optional[str] = Field(None, description="计划描述")
    status: str = Field(default='pending', description="状态")


class PlanCreate(PlanBase):
    """创建工作计划请求模型"""
    profile_id: str = Field(..., description="项目档案 ID")
    phase_record_id: Optional[str] = Field(None, description="阶段记录 ID")


class PlanUpdate(BaseModel):
    """更新工作计划请求模型（所有字段可选）"""
    plan_name: Optional[str] = Field(None, min_length=1, max_length=100, description="计划名称")
    description: Optional[str] = Field(None, description="计划描述")
    status: Optional[str] = Field(None, description="状态")


class PlanResponse(PlanBase):
    """工作计划响应模型"""
    plan_id: str = Field(..., description="计划 ID")
    profile_id: str = Field(..., description="项目档案 ID")
    phase_record_id: Optional[str] = Field(None, description="阶段记录 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class PlanListResponse(BaseModel):
    """工作计划列表响应模型"""
    total: int = Field(..., description="总记录数")
    items: list[PlanResponse] = Field(..., description="工作计划列表")


class PlanDetailResponse(BaseModel):
    """工作计划详情响应模型（含关联信息）"""
    data: PlanResponse = Field(..., description="计划详情")
    profile: Optional[ProfileResponse] = Field(None, description="关联的项目档案信息")
    phase: Optional[PhaseResponse] = Field(None, description="关联的阶段信息")


# ==================== 任务锁定/验证相关模型 ====================

class TaskLockRequest(BaseModel):
    """任务锁定请求模型"""
    agent_id: str = Field(..., description="请求锁定的 Agent ID")


class TaskUnlockRequest(BaseModel):
    """任务解锁请求模型"""
    agent_id: str = Field(..., description="请求解锁的 Agent ID")


class TaskVerifyRequest(BaseModel):
    """任务验证请求模型"""
    verification_result: str = Field(..., description="验证结果：通过/不通过")
    verification_log: Optional[str] = Field(None, description="验证日志")
    verifier: str = Field(..., description="验证人")


class TaskLockResponse(BaseModel):
    """任务锁定响应模型"""
    success: bool = Field(..., description="是否成功")
    task_no: str = Field(..., description="任务单号")
    locked_by: Optional[str] = Field(None, description="锁定者")
    locked_at: Optional[datetime] = Field(None, description="锁定时间")
    error: Optional[str] = Field(None, description="错误信息")


class TaskVerifyResponse(BaseModel):
    """任务验证响应模型"""
    success: bool = Field(..., description="是否成功")
    task_no: str = Field(..., description="任务单号")
    status: str = Field(..., description="任务状态")
    verification_result: str = Field(..., description="验证结果")

# ==================== 阶段创建 ====================
class PhaseCreate(BaseModel):
    phase_id: str
    phase_name: str
    phase_order: int
    status: str = "pending"

# ==================== Checklist 相关模型 ====================

class ChecklistBase(BaseModel):
    """检查清单基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="清单名称")
    description: Optional[str] = Field(None, description="清单描述")
    category: Optional[str] = Field(None, max_length=50, description="分类：代码审查/文档审查/安全审查")
    items: str = Field(default='[]', description="检查项（JSON 数组）")


class ChecklistCreate(ChecklistBase):
    """创建检查清单请求模型"""
    checklist_id: Optional[str] = Field(None, max_length=50, description="清单 ID（可选，不传则自动生成）")


class ChecklistUpdate(BaseModel):
    """更新检查清单请求模型（所有字段可选）"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="清单名称")
    description: Optional[str] = Field(None, description="清单描述")
    category: Optional[str] = Field(None, max_length=50, description="分类：代码审查/文档审查/安全审查")
    items: Optional[str] = Field(None, description="检查项（JSON 数组）")


class ChecklistResponse(ChecklistBase):
    """检查清单响应模型"""
    checklist_id: str = Field(..., description="清单 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
