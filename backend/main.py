"""
FastAPI 主应用模块
"""
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from database import engine, Base, get_db
from models import Task
from models.task_v2 import TaskV2, FlowTicketInstance, FlowTicketLog
from schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskDetailResponse, MessageResponse, TaskQueryParams,
    ProfileCreate, ProfileUpdate, ProfileResponse, ProfileListResponse,
    PhaseCreate, PhaseUpdate, PhaseResponse,
    PlanCreate, PlanUpdate, PlanResponse, PlanListResponse, PlanDetailResponse,
    TaskLockRequest, TaskUnlockRequest, TaskVerifyRequest,
    TaskLockResponse, TaskVerifyResponse
)
from crud import create_task, get_task_by_no, get_tasks, update_task, delete_task
from crud.task import lock_task, unlock_task, update_task_verification
from crud.profiles import (
    get_profiles, get_profile, create_profile, update_profile, delete_profile,
    get_profile_phases, create_phase
)
from crud.plans import get_plans, get_plan, create_plan, get_plan_tasks
from utils import TASK_STATUS_OPTIONS, TASK_PRIORITY_OPTIONS, VERIFICATION_RESULT_OPTIONS
from api import issues_router, issue_status_router, issue_assignment_router, issue_tasks_router, issue_resolution_router, issue_summary_router, knowledge_router, checklists_router
# from api.flowticket_v2 import router as flowticket_v2_router  # 已禁用FlowTicket v2
from api.tasks_v2 import router as tasks_v2_router  # 任务CRUD API
from api.flowticket_resume_api import router as flowticket_resume_router
from api.task_execution import router as task_execution_router
from src.api.plans_fixed import router as plans_router

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI(
    title="任务执行管理系统",
    description="任务执行管理后端 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境应限制具体域名）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(issues_router, prefix="/api")
app.include_router(issue_status_router, prefix="/api")
app.include_router(issue_assignment_router, prefix="/api")
app.include_router(issue_tasks_router, prefix="/api")
app.include_router(issue_resolution_router, prefix="/api")
app.include_router(issue_summary_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")
app.include_router(checklists_router, prefix="/api")
# app.include_router(flowticket_v2_router)  # 已禁用FlowTicket v2
app.include_router(tasks_v2_router, prefix="/api/v2/tasks")  # 任务CRUD API
app.include_router(flowticket_resume_router, prefix="/api")
app.include_router(task_execution_router)
app.include_router(plans_router)


# ==================== 服务信息 ====================

@app.get("/", tags=["系统"])
async def root():
    """服务根路径"""
    from datetime import datetime
    return {
        "service": "AutoCraft 任务执行管理系统",
        "version": "1.0.0 + FlowTicket v2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "v1_api": "/api",
            "v2_api": "/api/v2",
            "flowticket_v2": "/api/v2/flowticket",
            "tasks_v2": "/api/v2/tasks",
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# ==================== 健康检查 ====================

@app.get("/health", tags=["系统"])
def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "服务正常运行"}


# ==================== 任务管理 API ====================

@app.post("/tasks", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["任务管理"])
def api_create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """
    创建新任务（已禁用 - tasks表已删除，请使用 /api/v2/tasks）
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="此API已禁用。tasks表已删除，请使用新的 /api/v2/tasks API"
    )


@app.get("/tasks", response_model=TaskListResponse, tags=["任务管理"])
def api_get_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（任务名称）"),
    task_no: Optional[str] = Query(None, description="任务单号搜索"),
    executor: Optional[str] = Query(None, description="执行人搜索"),
    verifier: Optional[str] = Query(None, description="验证人搜索"),
    status: Optional[str] = Query(None, description="状态筛选（支持多值，逗号分隔）"),
    priority: Optional[str] = Query(None, description="优先级筛选（支持多值，逗号分隔）"),
    verification_result: Optional[str] = Query(None, description="验证结论筛选（支持多值，逗号分隔）"),
    plan_date_start: Optional[str] = Query(None, description="计划日期开始"),
    plan_date_end: Optional[str] = Query(None, description="计划日期结束"),
    plan_complete_start: Optional[str] = Query(None, description="计划完成时间开始"),
    plan_complete_end: Optional[str] = Query(None, description="计划完成时间结束"),
    verification_time_start: Optional[str] = Query(None, description="验证时间开始"),
    verification_time_end: Optional[str] = Query(None, description="验证时间结束"),
    exec_start_time_start: Optional[str] = Query(None, description="执行开始时间开始"),
    exec_start_time_end: Optional[str] = Query(None, description="执行开始时间结束"),
    exec_complete_time_start: Optional[str] = Query(None, description="执行完成时间开始"),
    exec_complete_time_end: Optional[str] = Query(None, description="执行完成时间结束"),
    verify_start_time_start: Optional[str] = Query(None, description="验证开始时间开始"),
    verify_start_time_end: Optional[str] = Query(None, description="验证开始时间结束"),
    verify_complete_time_start: Optional[str] = Query(None, description="验证完成时间开始"),
    verify_complete_time_end: Optional[str] = Query(None, description="验证完成时间结束"),
    db: Session = Depends(get_db)
):
    """
    获取任务列表（简化版 - 从tasks_v2表读取）

    - 支持分页
    - 只支持基本查询
    """
    from tasks_v2_compat import get_tasks_compat
    
    try:
        # 简化版：只获取最近的任务
        offset = (page - 1) * page_size
        tasks = get_tasks_compat(db, limit=page_size, offset=offset)
        
        # 获取总数（简化）
        from sqlalchemy import func, select
        from models.task_v2 import TaskV2
        count_query = select(func.count(TaskV2.id))
        total_result = db.execute(count_query)
        total = total_result.scalar()
        
        return TaskListResponse(
            total=total,
            items=tasks,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务列表失败: {str(e)}"
        )


@app.get("/tasks/v2-compat", response_model=TaskListResponse, tags=["任务管理"])
def api_get_tasks_v2_compat(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    plan_id: Optional[str] = Query(None, description="计划ID筛选"),
    status: Optional[str] = Query(None, description="状态筛选（支持多值，逗号分隔）"),
    db: Session = Depends(get_db)
):
    """
    获取tasks_v2表的数据（兼容前端格式）
    
    专门用于显示FlowTicket v2的任务数据
    """
    try:
        from sqlalchemy import and_
        
        # 构建查询
        query = db.query(TaskV2)
        
        # 应用筛选条件
        if plan_id:
            query = query.filter(TaskV2.plan_id == plan_id)
        
        if status:
            status_list = [s.strip() for s in status.split(",") if s.strip()]
            query = query.filter(TaskV2.status.in_(status_list))
        
        # 计算总数
        total = query.count()
        
        # 应用分页
        offset = (page - 1) * page_size
        tasks_v2 = query.order_by(TaskV2.task_no).offset(offset).limit(page_size).all()
        
        # 将TaskV2对象转换为前端期望的格式
        from models import Task
        tasks = []
        for task_v2 in tasks_v2:
            # 创建Task对象（兼容前端格式）
            task = Task(
                id=task_v2.id,
                task_no=task_v2.task_no,
                task_name=task_v2.task_name,
                plan_id=task_v2.plan_id,
                status=task_v2.status,
                priority="medium",  # 默认值
                verification_result="待验证",  # 默认值
                created_at=task_v2.created_at,
                updated_at=task_v2.updated_at,
                task_type=task_v2.task_type,
                input_data=task_v2.input_data,
            )
            tasks.append(task)
        
        return TaskListResponse(
            total=total,
            items=tasks,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取tasks_v2数据失败: {str(e)}"
        )


@app.get("/tasks/overdue", response_model=TaskListResponse, tags=["任务管理"])
def api_get_overdue_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取超时任务列表

    超时定义：
    - 当前时间 > exec_estimated_complete 且 exec_complete_time 为空
    - 或者：当前时间 > verify_estimated_complete 且 verify_complete_time 为空
    """
    from sqlalchemy import desc
    now = datetime.now()

    query = db.query(Task).filter(
        (
            (Task.exec_estimated_complete < now) &
            (Task.exec_complete_time == None)
        ) |
        (
            (Task.verify_estimated_complete < now) &
            (Task.verify_complete_time == None)
        )
    )

    total = query.count()
    offset = (page - 1) * page_size
    tasks = query.order_by(desc(Task.created_at)).offset(offset).limit(page_size).all()

    return TaskListResponse(
        total=total,
        items=tasks,
        page=page,
        page_size=page_size
    )


@app.get("/tasks/{task_no}", response_model=TaskDetailResponse, tags=["任务管理"])
def api_get_task(task_no: str, db: Session = Depends(get_db)):
    """
    获取任务详情（兼容层 - 从tasks_v2表读取）

    - 根据任务单号查询
    """
    from tasks_v2_compat import get_task_by_no_compat
    
    task = get_task_by_no_compat(db, task_no)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在: {task_no}"
        )
    return TaskDetailResponse(data=task)


@app.put("/tasks/{task_no}", response_model=MessageResponse, tags=["任务管理"])
def api_update_task(task_no: str, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """
    更新任务

    - 根据任务单号更新
    - 只更新提供的字段
    """
    task = get_task_by_no(db, task_no)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在: {task_no}"
        )

    try:
        update_task(db, task, task_update)
        return MessageResponse(
            message="任务更新成功",
            task_no=task_no
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新任务失败: {str(e)}"
        )


@app.delete("/tasks/{task_no}", response_model=MessageResponse, tags=["任务管理"])
def api_delete_task(task_no: str, db: Session = Depends(get_db)):
    """
    删除任务

    - 根据任务单号删除
    """
    task = get_task_by_no(db, task_no)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在: {task_no}"
        )

    try:
        delete_task(db, task)
        return MessageResponse(
            message="任务删除成功",
            task_no=task_no
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除任务失败: {str(e)}"
        )



@app.put("/tasks/{task_no}/lock", response_model=TaskLockResponse, tags=["任务管理"])
def api_lock_task(task_no: str, request: TaskLockRequest, db: Session = Depends(get_db)):
    """
    锁定任务

    - 用于并发控制
    - 如果任务已被锁定，返回错误和当前锁定者信息
    """
    result = lock_task(db, task_no, request.agent_id)
    
    if not result["success"]:
        return TaskLockResponse(
            success=False,
            task_no=task_no,
            locked_by=result.get("locked_by"),
            locked_at=result.get("locked_at"),
            error=result.get("error")
        )
    
    return TaskLockResponse(
        success=True,
        task_no=task_no,
        locked_by=result["locked_by"],
        locked_at=result["locked_at"]
    )


@app.put("/tasks/{task_no}/unlock", response_model=TaskLockResponse, tags=["任务管理"])
def api_unlock_task(task_no: str, request: TaskUnlockRequest, db: Session = Depends(get_db)):
    """
    解锁任务

    - 只有锁定者才能解锁
    """
    result = unlock_task(db, task_no, request.agent_id)
    
    if not result["success"]:
        return TaskLockResponse(
            success=False,
            task_no=task_no,
            error=result.get("error")
        )
    
    return TaskLockResponse(
        success=True,
        task_no=task_no
    )


@app.put("/tasks/{task_no}/verify", response_model=TaskVerifyResponse, tags=["任务管理"])
def api_verify_task(task_no: str, request: TaskVerifyRequest, db: Session = Depends(get_db)):
    """
    记录验证信息

    - 更新验证结果
    - 自动更新任务状态：通过→已完成，不通过→需返工
    - 默认不级联更新上级状态（由代理决定）
    """
    task = get_task_by_no(db, task_no)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在：{task_no}"
        )
    
    updated_task = update_task_verification(
        db, task_no, 
        request.verification_result, 
        request.verification_log, 
        request.verifier,
        cascade_update=False  # 默认不自动级联更新
    )
    
    return TaskVerifyResponse(
        success=True,
        task_no=task_no,
        status=updated_task.status,
        verification_result=updated_task.verification_result
    )


@app.post("/status/cascade/{task_no}", tags=["状态管理"])
def api_cascade_status_update(task_no: str, db: Session = Depends(get_db)):
    """
    级联更新状态（代理调用）

    当任务验证通过后，代理可以调用此接口触发状态级联更新：
    任务 → 计划 → 工作流 → 阶段 → 项目
    """
    from crud.status_update import cascade_status_update
    
    task = get_task_by_no(db, task_no)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在：{task_no}"
        )
    
    result = cascade_status_update(db, task_no)
    
    return {
        "success": True,
        "task_no": task_no,
        "status_chain": result
    }


# ==================== 项目档案管理 API ====================

@app.post("/profiles", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["项目档案管理"])
def api_create_profile(profile_data: ProfileCreate, db: Session = Depends(get_db)):
    """
    创建项目档案

    - 自动生成 profile_id（如果不提供）
    - 支持从模板复制阶段和工作流（通过 template_profile_id）
    - profile_type 必填（template=模板，instance=实例）
    """
    try:
        profile = create_profile(db, profile_data)
        return MessageResponse(
            message="项目档案创建成功",
            profile_id=profile.profile_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建项目档案失败：{str(e)}"
        )


@app.get("/profiles", response_model=ProfileListResponse, tags=["项目档案管理"])
def api_get_profiles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    profile_type: Optional[str] = Query(None, description="档案类型（template/instance）"),
    status: Optional[str] = Query(None, description="状态筛选"),
    name: Optional[str] = Query(None, description="项目名称模糊搜索"),
    start_date: Optional[str] = Query(None, description="创建时间起始"),
    end_date: Optional[str] = Query(None, description="创建时间结束"),
    db: Session = Depends(get_db)
):
    """
    获取项目档案列表

    - 支持分页
    - 支持按类型、状态筛选
    - 支持项目名称模糊搜索
    - 支持创建时间范围查询
    """
    from datetime import datetime
    
    # 解析日期参数
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date 格式错误，应为 ISO 格式（如：2024-01-01T00:00:00）"
            )
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_date 格式错误，应为 ISO 格式（如：2024-01-01T00:00:00）"
            )
    
    try:
        offset = (page - 1) * page_size
        total, profiles = get_profiles(
            db,
            profile_type=profile_type,
            status=status,
            name=name,
            start_date=start_dt,
            end_date=end_dt,
            skip=offset,
            limit=page_size
        )
        
        return ProfileListResponse(
            total=total,
            items=profiles,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目档案列表失败：{str(e)}"
        )


@app.get("/profiles/{profile_id}", response_model=ProfileResponse, tags=["项目档案管理"])
def api_get_profile(profile_id: str, db: Session = Depends(get_db)):
    """
    获取项目档案详情

    - 根据 profile_id 查询
    """
    profile = get_profile(db, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目档案不存在：{profile_id}"
        )
    return ProfileResponse.model_validate(profile)


@app.put("/profiles/{profile_id}", response_model=MessageResponse, tags=["项目档案管理"])
def api_update_profile(profile_id: str, profile_data: ProfileUpdate, db: Session = Depends(get_db)):
    """
    更新项目档案

    - 根据 profile_id 更新
    - 只更新提供的字段
    """
    profile = get_profile(db, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目档案不存在：{profile_id}"
        )

    try:
        update_profile(db, profile_id, profile_data)
        return MessageResponse(
            message="项目档案更新成功",
            profile_id=profile_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新项目档案失败：{str(e)}"
        )


@app.delete("/profiles/{profile_id}", response_model=MessageResponse, tags=["项目档案管理"])
def api_delete_profile(profile_id: str, db: Session = Depends(get_db)):
    """
    删除项目档案

    - 根据 profile_id 删除
    - 级联删除相关阶段、工作流、计划
    """
    profile = get_profile(db, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目档案不存在：{profile_id}"
        )

    try:
        delete_profile(db, profile_id)
        return MessageResponse(
            message="项目档案删除成功",
            profile_id=profile_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除项目档案失败：{str(e)}"
        )


@app.post("/profiles/{profile_id}/phases", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["项目档案管理"])
def api_create_profile_phase(profile_id: str, phase_data: PhaseCreate, db: Session = Depends(get_db)):
    """
    创建项目阶段

    - 为指定项目创建一个新阶段
    """
    profile = get_profile(db, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目档案不存在：{profile_id}"
        )
    
    try:
        phase_record_id = create_phase(db, profile_id, phase_data)
        return MessageResponse(message=f"阶段创建成功", task_no=phase_record_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建阶段失败：{str(e)}"
        )


@app.put("/phases/{phase_record_id}", response_model=PhaseResponse, tags=["项目档案管理"])
def api_update_phase(phase_record_id: str, phase_data: PhaseUpdate, db: Session = Depends(get_db)):
    """
    更新项目阶段
    """
    from crud.profiles import get_phase, update_phase
    phase = get_phase(db, phase_record_id)
    if not phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"阶段不存在：{phase_record_id}"
        )
    
    try:
        updated_phase = update_phase(db, phase_record_id, phase_data.model_dump(exclude_unset=True))
        return PhaseResponse.model_validate(updated_phase)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新阶段失败：{str(e)}"
        )


@app.delete("/phases/{phase_record_id}", response_model=MessageResponse, tags=["项目档案管理"])
def api_delete_phase(phase_record_id: str, db: Session = Depends(get_db)):
    """
    删除项目阶段
    """
    from crud.profiles import get_phase, delete_phase
    phase = get_phase(db, phase_record_id)
    if not phase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"阶段不存在：{phase_record_id}"
        )
    
    try:
        delete_phase(db, phase_record_id)
        return MessageResponse(message=f"阶段已删除：{phase_record_id}", task_no=None)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除阶段失败：{str(e)}"
        )


@app.get("/profiles/{profile_id}/phases", response_model=list[PhaseResponse], tags=["项目档案管理"])
def api_get_profile_phases(profile_id: str, db: Session = Depends(get_db)):
    """
    获取项目阶段列表

    - 根据 profile_id 获取所有阶段
    - 按阶段顺序排序
    """
    profile = get_profile(db, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目档案不存在：{profile_id}"
        )
    
    try:
        phases = get_profile_phases(db, profile_id)
        return [PhaseResponse.model_validate(phase) for phase in phases]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目阶段列表失败：{str(e)}"
        )


# ==================== 工作计划管理 API ====================

@app.get("/plans", response_model=PlanListResponse, tags=["工作计划管理"])
def api_get_plans(
    profile_id: Optional[str] = Query(None, description="项目档案 ID（可选，用于筛选）"),
    status: Optional[str] = Query(None, description="状态（可选，用于筛选）"),
    db: Session = Depends(get_db)
):
    """
    获取工作计划列表

    - 支持按 profile_id 筛选
    - 支持按 status 筛选
    """
    try:
        plans = get_plans(db, profile_id=profile_id, status=status)
        return PlanListResponse(
            total=len(plans),
            items=[PlanResponse.model_validate(plan) for plan in plans]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取工作计划列表失败：{str(e)}"
        )


@app.get("/plans/{plan_id}", response_model=PlanDetailResponse, tags=["工作计划管理"])
def api_get_plan(plan_id: str, db: Session = Depends(get_db)):
    """
    获取工作计划详情

    - 根据 plan_id 查询
    - 返回计划详情及关联的 profile 和 workflow 信息
    """
    plan = get_plan(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作计划不存在：{plan_id}"
        )
    
    # 构建响应数据
    plan_data = PlanResponse.model_validate(plan)
    profile_data = ProfileResponse.model_validate(plan.profile) if plan.profile else None
    phase_data = PhaseResponse.model_validate(plan.phase) if plan.phase else None
    
    return PlanDetailResponse(
        data=plan_data,
        profile=profile_data,
        phase=phase_data
    )


@app.post("/plans", response_model=PlanResponse, tags=["工作计划管理"])
def api_create_plan(plan_data: PlanCreate, db: Session = Depends(get_db)):
    """
    创建工作计划

    - 创建新的工作计划
    - 需要 profile_id 和 phase_record_id（可选）
    """
    # 验证项目档案是否存在
    profile = get_profile(db, plan_data.profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目档案不存在：{plan_data.profile_id}"
        )
    
    try:
        # 创建计划
        plan_dict = plan_data.model_dump()
        new_plan = create_plan(db, plan_dict)
        return PlanResponse.model_validate(new_plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建工作计划失败：{str(e)}"
        )


@app.put("/plans/{plan_id}", response_model=PlanResponse, tags=["工作计划管理"])
def api_update_plan(plan_id: str, plan_data: PlanUpdate, db: Session = Depends(get_db)):
    """
    更新工作计划
    """
    plan = get_plan(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作计划不存在：{plan_id}"
        )
    
    try:
        update_dict = plan_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(plan, key, value)
        plan.updated_at = datetime.now()
        db.commit()
        db.refresh(plan)
        return PlanResponse.model_validate(plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新工作计划失败：{str(e)}"
        )


@app.delete("/plans/{plan_id}", response_model=MessageResponse, tags=["工作计划管理"])
def api_delete_plan(plan_id: str, db: Session = Depends(get_db)):
    """
    删除工作计划
    """
    plan = get_plan(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作计划不存在：{plan_id}"
        )
    
    try:
        # 删除关联的任务
        tasks = db.query(Task).filter(Task.plan_id == plan_id).all()
        for task in tasks:
            db.delete(task)
        # 删除计划
        db.delete(plan)
        db.commit()
        return MessageResponse(message=f"工作计划已删除：{plan_id}", task_no=None)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除工作计划失败：{str(e)}"
        )


@app.get("/plans/{plan_id}/tasks", response_model=list[TaskResponse], tags=["工作计划管理"])
def api_get_plan_tasks(
    plan_id: str,
    task_status: Optional[str] = Query(None, alias="status", description="状态（可选，用于筛选）"),
    db: Session = Depends(get_db)
):
    """
    获取计划的任务列表

    - 根据 plan_id 获取所有任务
    - 支持按 status 筛选
    """
    # 验证计划是否存在
    plan = get_plan(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作计划不存在：{plan_id}"
        )
    
    try:
        tasks = get_plan_tasks(db, plan_id, status=task_status)
        return [TaskResponse.model_validate(task) for task in tasks]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取计划任务列表失败：{str(e)}"
        )


# ==================== 数据字典 API ====================

@app.get("/dict/status", tags=["数据字典"])
def get_status_dict():
    """获取状态选项"""
    return {"data": TASK_STATUS_OPTIONS}


@app.get("/dict/priority", tags=["数据字典"])
def get_priority_dict():
    """获取优先级选项"""
    return {"data": TASK_PRIORITY_OPTIONS}


@app.get("/dict/verification", tags=["数据字典"])
def get_verification_dict():
    """获取验证结论选项"""
    return {"data": VERIFICATION_RESULT_OPTIONS}


# ==================== 启动入口 =====

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
