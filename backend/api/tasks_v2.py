"""
FlowTicket v2 任务单API实现
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database import get_db
from models.task_v2 import TaskV2

# 创建路由
router = APIRouter(tags=["FlowTicket v2 API"])


# 错误码定义（符合API规范）
ERROR_CODES = {
    "TASK_NOT_FOUND": {
        "code": "TASK_NOT_FOUND",
        "message": "任务不存在",
        "http_status": status.HTTP_404_NOT_FOUND
    },
    "INVALID_STATUS_TRANSITION": {
        "code": "INVALID_STATUS_TRANSITION",
        "message": "状态流转无效",
        "http_status": status.HTTP_400_BAD_REQUEST
    },
    "MISSING_REQUIRED_FIELD": {
        "code": "MISSING_REQUIRED_FIELD",
        "message": "缺少必要字段",
        "http_status": status.HTTP_400_BAD_REQUEST
    },
    "INVALID_STATUS_VALUE": {
        "code": "INVALID_STATUS_VALUE",
        "message": "无效的状态值",
        "http_status": status.HTTP_400_BAD_REQUEST
    },
    "TASK_STATUS_INCORRECT": {
        "code": "TASK_STATUS_INCORRECT",
        "message": "任务状态不正确",
        "http_status": status.HTTP_400_BAD_REQUEST
    },
    "TASK_NO_DUPLICATE": {
        "code": "TASK_NO_DUPLICATE",
        "message": "任务单号已存在",
        "http_status": status.HTTP_400_BAD_REQUEST
    },
    "DATABASE_ERROR": {
        "code": "DATABASE_ERROR",
        "message": "数据库错误",
        "http_status": status.HTTP_500_INTERNAL_SERVER_ERROR
    },
    "INTERNAL_ERROR": {
        "code": "INTERNAL_ERROR",
        "message": "内部错误",
        "http_status": status.HTTP_500_INTERNAL_SERVER_ERROR
    }
}


def create_error_response(error_code: str, details: str = None) -> Dict[str, Any]:
    """创建标准错误响应"""
    error_info = ERROR_CODES.get(error_code, ERROR_CODES["INTERNAL_ERROR"])
    
    response = {
        "status": "error",
        "error_code": error_info["code"],
        "message": error_info["message"],
        "details": details
    }
    
    return response, error_info["http_status"]


# 状态流转验证
VALID_STATUS_TRANSITIONS = {
    "pending": ["in_progress", "paused"],
    "in_progress": ["pending_verification", "paused", "failed"],
    "pending_verification": ["completed", "paused", "failed"],
    "completed": [],  # 已完成状态不可更改
    "paused": ["in_progress", "pending_verification", "failed"],
    "failed": []  # 已失败状态不可更改
}

VALID_STATUSES = list(VALID_STATUS_TRANSITIONS.keys())


def validate_status_transition(current_status: str, new_status: str) -> bool:
    """验证状态流转是否有效"""
    allowed_transitions = VALID_STATUS_TRANSITIONS.get(current_status, [])
    return new_status in allowed_transitions


@router.put("/{task_id}/status", response_model=Dict[str, Any])
async def update_task_status(
    task_id: int,
    status_update: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    更新任务状态
    
    状态值: 
    - pending: 待执行
    - in_progress: 进行中
    - pending_verification: 待验证
    - completed: 已完成
    - paused: 已暂停
    - failed: 已失败
    """
    # 获取任务
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        error_response, http_status = create_error_response(
            "TASK_NOT_FOUND", 
            f"task_id={task_id}"
        )
        error_response, http_status = create_error_response("INTERNAL_ERROR", "未知错误")
        raise HTTPException(status_code=http_status, detail=error_response)
    
    # 验证状态字段
    new_status = status_update.get("status")
    if not new_status:
        error_response, http_status = create_error_response(
            "MISSING_REQUIRED_FIELD", 
            "缺少必要字段: status"
        )
        raise HTTPException(status_code=http_status, detail=error_response)
    
    if new_status not in VALID_STATUSES:
        error_response, http_status = create_error_response(
            "INVALID_STATUS_VALUE", 
            f"无效的状态值: {new_status}，有效值: {VALID_STATUSES}"
        )
        raise HTTPException(status_code=http_status, detail=error_response)
    
    # 验证状态流转
    if not validate_status_transition(task.status, new_status):
        error_response, http_status = create_error_response(
            "INVALID_STATUS_TRANSITION", 
            f"无效的状态流转: {task.status} -> {new_status}"
        )
        raise HTTPException(status_code=http_status, detail=error_response)
    
    # 更新状态
    task.status = new_status
    
    # 更新extra_data
    extra_data = status_update.get("extra_data")
    if extra_data:
        # 合并extra_data到task.extra_data字段
        current_extra = {}
        if task.extra_data:
            try:
                current_extra = json.loads(task.extra_data)
            except:
                current_extra = {}
        
        # 合并新数据
        if isinstance(extra_data, dict):
            current_extra.update(extra_data)
        task.extra_data = json.dumps(current_extra, ensure_ascii=False)
    
    task.updated_at = datetime.now()
    
    # 保存到数据库
    db.commit()
    db.refresh(task)
    
    return {
        "status": "success",
        "task_id": task_id,
        "new_status": new_status,
        "updated_at": task.updated_at.isoformat()
    }


@router.put("/{task_id}/execution", response_model=Dict[str, Any])
async def update_task_execution(
    task_id: int,
    execution_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    更新任务执行记录
    """
    # 获取任务
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        error_response, http_status = create_error_response(
            "TASK_NOT_FOUND", 
            f"task_id={task_id}"
        )
        error_response, http_status = create_error_response("INTERNAL_ERROR", "未知错误")
        raise HTTPException(status_code=http_status, detail=error_response)
    
    # 验证任务状态
    if task.status != "in_progress":
        error_response, http_status = create_error_response(
            "TASK_STATUS_INCORRECT", 
            f"任务状态不正确，当前状态: {task.status}，预期: in_progress"
        )
        raise HTTPException(status_code=http_status, detail=error_response)
    
    # 更新执行记录
    execution_log = execution_data.get("execution_log")
    if execution_log:
        if isinstance(execution_log, dict):
            task.execution_log = json.dumps(execution_log, ensure_ascii=False)
        else:
            task.execution_log = execution_log
    
    # 更新output_files（存储在extra_data中）
    output_files = execution_data.get("output_files", [])
    execution_status = execution_data.get("execution_status", "success")
    
    if output_files or execution_status != "success":
        current_extra = {}
        if task.extra_data:
            try:
                current_extra = json.loads(task.extra_data)
            except:
                current_extra = {}
        
        if output_files:
            current_extra["output_files"] = output_files
        
        current_extra["execution_status"] = execution_status
        current_extra["execution_updated_at"] = datetime.now().isoformat()
        
        task.extra_data = json.dumps(current_extra, ensure_ascii=False)
    
    task.updated_at = datetime.now()
    
    # 保存到数据库
    db.commit()
    db.refresh(task)
    
    return {
        "status": "success",
        "task_id": task_id,
        "execution_updated": True,
        "output_file_count": len(output_files) if isinstance(output_files, list) else 0
    }


@router.put("/{task_id}/verification", response_model=Dict[str, Any])
async def update_task_verification(
    task_id: int,
    verification_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    更新任务验证记录
    """
    # 获取任务
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        error_response, http_status = create_error_response(
            "TASK_NOT_FOUND", 
            f"task_id={task_id}"
        )
        error_response, http_status = create_error_response("INTERNAL_ERROR", "未知错误")
        raise HTTPException(status_code=http_status, detail=error_response)
    
    # 验证任务状态
    if task.status != "pending_verification":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务状态不正确，当前状态: {task.status}，预期: pending_verification"
        )
    
    # 更新验证记录
    verification_log = verification_data.get("verification_log")
    if verification_log:
        if isinstance(verification_log, dict):
            task.verification_log = json.dumps(verification_log, ensure_ascii=False)
        else:
            task.verification_log = verification_log
    
    # 更新验证结论、分数、问题（存储在extra_data中）
    conclusion = verification_data.get("conclusion")
    score = verification_data.get("score")
    issues = verification_data.get("issues", [])
    
    if conclusion:
        current_extra = {}
        if task.extra_data:
            try:
                current_extra = json.loads(task.extra_data)
            except:
                current_extra = {}
        
        current_extra["conclusion"] = conclusion
        if score is not None:
            current_extra["score"] = score
        if issues:
            current_extra["issues"] = issues
        current_extra["verification_updated_at"] = datetime.now().isoformat()
        
        task.extra_data = json.dumps(current_extra, ensure_ascii=False)
    
    task.updated_at = datetime.now()
    
    # 保存到数据库
    db.commit()
    db.refresh(task)
    
    return {
        "status": "success",
        "task_id": task_id,
        "verification_updated": True,
        "conclusion": conclusion
    }


@router.post("/", response_model=Dict[str, Any])
async def create_system_tasks(
    tasks_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    创建系统任务单（批量）
    """
    created_tasks = []
    errors = []
    
    for task_data in tasks_data:
        try:
            # 验证必要字段
            required_fields = ["task_no", "task_name"]
            for field in required_fields:
                if field not in task_data:
                    errors.append(f"任务缺少必要字段: {field}")
                    continue
            
            # 验证业务必填字段（数据库允许为空，但业务必须）
            business_required = {"task_type": "任务类型", "plan_id": "工作计划ID", "input_data": "任务数据"}
            missing_business = [f"{v}({k})" for k, v in business_required.items() if not task_data.get(k)]
            if missing_business:
                logger.warning(f"任务{task_data.get('task_no', '?')}缺少业务必填字段: {', '.join(missing_business)}")
            
            # 检查task_no在plan_id内是否唯一
            plan_id = task_data.get("plan_id")
            task_no = task_data["task_no"]
            
            if plan_id:
                existing_task = db.query(TaskV2).filter(
                    and_(TaskV2.plan_id == plan_id, TaskV2.task_no == task_no)
                ).first()
                
                if existing_task:
                    errors.append(f"任务单号已存在: plan_id={plan_id}, task_no={task_no}")
                    continue
            
            # 创建任务
            new_task = TaskV2()
            
            # 设置基本字段
            new_task.task_no = task_data["task_no"]
            new_task.task_name = task_data["task_name"]
            new_task.task_type = task_data.get("task_type")
            new_task.plan_id = task_data.get("plan_id")
            new_task.status = task_data.get("status", "pending")
            
            # 处理JSON字段
            json_fields = ["input_data", "extra_data"]
            for field in json_fields:
                value = task_data.get(field)
                if value:
                    if isinstance(value, dict):
                        setattr(new_task, field, json.dumps(value, ensure_ascii=False))
                    else:
                        setattr(new_task, field, value)
            
            new_task.created_at = datetime.now()
            new_task.updated_at = datetime.now()
            
            db.add(new_task)
            created_tasks.append(new_task)
            
        except Exception as e:
            errors.append(f"创建任务失败: {str(e)}")
    
    # 批量提交
    if created_tasks:
        db.commit()
        for task in created_tasks:
            db.refresh(task)
    
    return {
        "status": "success",
        "created_count": len(created_tasks),
        "task_ids": [task.id for task in created_tasks],
        "errors": errors if errors else None
    }


@router.get("/{task_id}", response_model=Dict[str, Any])
async def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取任务详情"""
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        error_response, http_status = create_error_response(
            "TASK_NOT_FOUND", 
            f"task_id={task_id}"
        )
        error_response, http_status = create_error_response("INTERNAL_ERROR", "未知错误")
        raise HTTPException(status_code=http_status, detail=error_response)
    
    return {
        "status": "success",
        "task": task.to_dict()
    }


@router.get("/", response_model=Dict[str, Any])
async def list_tasks(
    plan_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    query = db.query(TaskV2)
    
    # 过滤条件
    if plan_id:
        query = query.filter(TaskV2.plan_id == plan_id)
    
    if status:
        query = query.filter(TaskV2.status == status)
    
    # 分页
    total = query.count()
    tasks = query.order_by(TaskV2.id.desc()) \
                .offset((page - 1) * page_size) \
                .limit(page_size) \
                .all()
    
    return {
        "status": "success",
        "total": total,
        "page": page,
        "page_size": page_size,
        "tasks": [task.to_dict() for task in tasks]
    }
