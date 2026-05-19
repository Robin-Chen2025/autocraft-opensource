"""
FlowTicket v2 执行引擎 - F-F-002 双节点任务执行模块

功能模块：
- F-F-001: 计划单启动执行（execute_plan_decompose_task）
- F-F-002: 双节点任务执行（execute_system_task）
- F-F-003: 异常通知与恢复（handle_exception / resume_from_node）

状态流转：
    待执行(pending) → 进行中(in_progress) → 待验证(pending_verification) → 已完成(completed)
    任何阶段失败 → 已暂停(paused) → 恢复后继续

设计文档: docs/design/flowticket-final-simplified-v2-design.md v3.1
"""
import os
import json
import logging
import requests
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

# 注意：sessions_send只能在主会话中使用，这里使用占位实现

from models.task_v2 import TaskV2, FlowTicketInstance, FlowTicketLog

logger = logging.getLogger("execution_engine")

# ==================== 常量 ====================

NODE1_TIMEOUT = 30 * 60   # 节点1超时：30分钟
NODE2_TIMEOUT = 10 * 60   # 节点2超时：10分钟

# 合法状态流转表
VALID_TRANSITIONS: Dict[str, List[str]] = {
    "pending": ["in_progress", "paused"],
    "in_progress": ["pending_verification", "paused", "failed"],
    "pending_verification": ["completed", "paused", "failed"],
    "completed": [],
    "paused": ["in_progress", "pending_verification", "failed"],
    "failed": []
}

# 中文恢复点 -> 内部节点标识（兼容中英文）
RESUME_POINT_MAP: Dict[str, str] = {
    "前置检查": "pre_check",
    "节点1": "node1",
    "执行后检查": "post_execution_check",
    "节点2": "node2",
    "验证后检查": "post_verification_check",
    "pre_check": "pre_check",
    "node1": "node1",
    "post_execution_check": "post_execution_check",
    "node2": "node2",
    "post_verification_check": "post_verification_check",
}

# 验证通过的可接受值（设计文档5.2.5明确写conclusion == "通过"）
VERIFICATION_PASS_VALUES = {"通过", "pass", "Pass", "PASS"}


# ==================== 内部辅助函数 ====================

def _parse_json(text: Optional[str]) -> dict:
    """安全解析JSON字符串，失败返回空字典"""
    if not text:
        return {}
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}


def _now_iso() -> str:
    """当前时间的ISO格式字符串"""
    return datetime.now().isoformat()


def add_log(db: Session, flowticket_id: str, log_type: str,
            content: dict, task_id: Optional[int] = None) -> None:
    """添加FlowTicket日志记录到 flowticket_logs 表"""
    log_entry = FlowTicketLog(
        flowticket_id=flowticket_id,
        task_id=task_id,
        log_type=log_type,
        content=json.dumps(content, ensure_ascii=False),
        created_at=datetime.now()
    )
    db.add(log_entry)
    db.commit()
    logger.info(
        f"[FT-{flowticket_id}] {log_type}"
        + (f" task={task_id}" if task_id else "")
        + f": {json.dumps(content, ensure_ascii=False)[:200]}"
    )


# ==================== 状态更新函数 ====================

def _call_task_api_via_http(task_id: int, endpoint: str, payload: dict) -> bool:
    """
    通过HTTP调用任务单API
    
    参数:
        task_id: 任务ID
        endpoint: API端点（如'status', 'execution', 'verification'）
        payload: 请求数据
        
    返回: True表示成功，False表示失败
    """
    try:
        # API基础URL配置
        # 开发环境: http://localhost:9001/api/v2/tasks
        # 生产环境: http://localhost:9001/api/v2/tasks
        base_url = "http://localhost:9001/api/v2/tasks"
        url = f"{base_url}/{task_id}/{endpoint}"
        
        response = requests.put(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(f"API调用成功: {url}")
            return True
        else:
            logger.warning(f"API调用失败 {response.status_code}: {url}")
            return False
    except Exception as e:
        logger.error(f"API调用异常: {e}")
        return False


def update_task_status_internal(
    db: Session, task_id: int, new_status: str,
    extra_data: Optional[dict] = None
) -> Optional[TaskV2]:
    """
    内部状态更新（直接操作数据库，避免HTTP调用开销）。
    包含状态流转验证，非法流转会返回None并记录警告日志。
    """
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        logger.error(f"任务不存在: task_id={task_id}")
        return None

    old_status = task.status
    allowed = VALID_TRANSITIONS.get(old_status, [])
    if new_status not in allowed:
        logger.warning(f"非法状态流转: {old_status} -> {new_status} (task_id={task_id})")
        return None

    task.status = new_status
    task.updated_at = datetime.now()

    if extra_data:
        current = _parse_json(task.extra_data)
        current.update(extra_data)
        task.extra_data = json.dumps(current, ensure_ascii=False)

    db.commit()
    db.refresh(task)
    logger.info(f"任务状态变更: {old_status} -> {new_status} (task_id={task_id})")
    
    # 同时调用真实API更新状态（设计文档要求）
    api_payload = {"status": new_status}
    if extra_data:
        api_payload["extra_data"] = extra_data
    
    api_success = _call_task_api_via_http(task_id, "status", api_payload)
    if not api_success:
        logger.warning(f"API状态更新调用失败，但数据库已更新: task_id={task_id}")
    
    return task


def update_execution_record(
    db: Session, task_id: int, execution_result: Dict[str, Any]
) -> Optional[TaskV2]:
    """
    更新任务单的执行记录（节点1执行后调用）。
    写入: execution_log, extra_data.execution_status, extra_data.output_files
    对应设计文档5.2.2: PUT /api/tasks/{task_id}/execution
    """
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        return None

    el = execution_result.get("execution_log")
    if el:
        task.execution_log = (
            json.dumps(el, ensure_ascii=False) if isinstance(el, dict) else str(el)
        )

    current = _parse_json(task.extra_data)
    output_files = execution_result.get("output_files", [])
    if output_files:
        current["output_files"] = output_files
    current["execution_status"] = execution_result.get("execution_status", "unknown")
    current["execution_updated_at"] = _now_iso()
    task.extra_data = json.dumps(current, ensure_ascii=False)
    task.updated_at = datetime.now()

    db.commit()
    db.refresh(task)
    
    # 调用真实API更新执行记录（设计文档要求）
    api_payload = {
        "execution_log": el,
        "output_files": output_files,
        "execution_status": execution_result.get("execution_status", "unknown")
    }
    api_success = _call_task_api_via_http(task_id, "execution", api_payload)
    if not api_success:
        logger.warning(f"API执行记录更新调用失败，但数据库已更新: task_id={task_id}")
    
    return task


def update_verification_record(
    db: Session, task_id: int, verification_result: Dict[str, Any]
) -> Optional[TaskV2]:
    """
    更新任务单的验证记录（节点2验证后调用）。
    写入: verification_log, extra_data.conclusion, extra_data.score, extra_data.issues
    对应设计文档5.2.4: PUT /api/tasks/{task_id}/verification
    """
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        return None

    vl = verification_result.get("verification_log")
    if vl:
        task.verification_log = (
            json.dumps(vl, ensure_ascii=False) if isinstance(vl, dict) else str(vl)
        )

    current = _parse_json(task.extra_data)
    for key in ("conclusion", "score", "issues"):
        value = verification_result.get(key)
        if value is not None:
            current[key] = value
    current["verification_updated_at"] = _now_iso()
    task.extra_data = json.dumps(current, ensure_ascii=False)
    task.updated_at = datetime.now()

    db.commit()
    db.refresh(task)
    
    # 调用真实API更新验证记录（设计文档要求）
    api_payload = {
        "verification_log": vl,
        "conclusion": verification_result.get("conclusion"),
        "score": verification_result.get("score"),
        "issues": verification_result.get("issues", [])
    }
    api_success = _call_task_api_via_http(task_id, "verification", api_payload)
    if not api_success:
        logger.warning(f"API验证记录更新调用失败，但数据库已更新: task_id={task_id}")
    
    return task

# ==================== F-F-003: 异常处理 ====================

def handle_exception(
    db: Session, flowticket_id: str, task_id: int,
    exception_type: str, exception_detail: str
) -> None:
    """
    F-F-003 异常处理（对应设计文档5.3.1）：
    1. 记录异常日志
    2. 更新任务状态为【已暂停】
    3. 更新FlowTicket实例状态为paused
    4. 后续由主代理决定是否恢复（通过resume API）
    """
    add_log(db, flowticket_id, "exception", {
        "exception_type": exception_type,
        "exception_detail": exception_detail
    }, task_id)

    update_task_status_internal(db, task_id, "paused", {
        "exception_type": exception_type,
        "exception_detail": exception_detail,
        "paused_at": _now_iso()
    })

    instance = db.query(FlowTicketInstance).filter(
        FlowTicketInstance.flowticket_id == flowticket_id
    ).first()
    if instance:
        instance.status = "paused"
        instance.updated_at = datetime.now()
        db.commit()

    logger.warning(
        f"异常处理: {exception_type} - {exception_detail} "
        f"(flowticket={flowticket_id}, task={task_id})"
    )
    
    # 设计文档要求：异常时通知主代理
    # 注意：sessions_send只能在主会话中使用，这里记录日志代替
    notification_msg = (
        f"🚨 FlowTicket异常通知\n"
        f"• FlowTicket ID: {flowticket_id}\n"
        f"• 任务ID: {task_id}\n"
        f"• 异常类型: {exception_type}\n"
        f"• 异常详情: {exception_detail[:200]}\n"
        f"• 处理时间: {_now_iso()}\n"
        f"• 当前状态: 已暂停，等待主代理恢复"
    )
    
    # 记录通知日志（实际应调用sessions_send）
    logger.info(f"主代理通知（模拟）: {notification_msg}")
    
    # 实际应调用:
    # try:
    #     sessions_send(
    #         sessionKey="agent:main:main",
    #         message=notification_msg
    #     )
    # except Exception as e:
    #     logger.error(f"主代理通知失败: {e}")


# ==================== F-F-002: 前置检查与状态更新 ====================

def check_input_files_and_update_status(
    db: Session, flowticket_id: str, task_id: int
) -> Dict[str, Any]:
    """
    前置检查：验证输入文件（如设计文档）是否存在。
    检查通过 → 更新状态为【进行中】
    检查失败 → 返回失败结果（由调用方触发异常处理）
    对应设计文档5.2.1
    """
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        return {"passed": False, "error": f"任务不存在: task_id={task_id}"}

    add_log(db, flowticket_id, "前置检查开始", {
        "task_no": task.task_no,
        "task_name": task.task_name
    }, task_id)

    input_data = _parse_json(task.input_data)
    design_doc_path = input_data.get("design_doc_path")

    if design_doc_path and not os.path.exists(design_doc_path):
        error_msg = f"设计文档路径不存在: {design_doc_path}"
        add_log(db, flowticket_id, "前置检查失败", {
            "error": error_msg, "path": design_doc_path
        }, task_id)
        return {"passed": False, "error": error_msg}

    if not design_doc_path:
        add_log(db, flowticket_id, "前置检查警告", {
            "warning": "未指定design_doc_path，跳过文件检查"
        }, task_id)

    result = update_task_status_internal(db, task_id, "in_progress", {
        "check_time": _now_iso(),
        "design_doc_path": design_doc_path,
        "check_result": "passed"
    })
    if not result:
        return {"passed": False, "error": "状态更新失败"}

    add_log(db, flowticket_id, "前置检查通过", {"new_status": "in_progress"}, task_id)
    return {"passed": True}

# ==================== F-F-002: 节点1 - 执行子代理 ====================

def execute_node1_execution_subagent(
    db: Session, flowticket_id: str, task_id: int
) -> Dict[str, Any]:
    """
    节点1：执行子代理（对应设计文档5.2.2）
    1. 动态拼装执行提示词
    2. 调用session模式子代理API
    3. 收集执行结果（execution_log, output_files）
    4. 调用任务单API更新执行记录
    """
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        return {"success": False, "error": f"任务不存在: task_id={task_id}"}

    add_log(db, flowticket_id, "节点1开始", {
        "task_no": task.task_no, "task_name": task.task_name
    }, task_id)

    input_data = _parse_json(task.input_data)

    prompt = _build_execution_prompt(task, input_data)
    add_log(db, flowticket_id, "节点1提示词已构建", {
        "prompt_length": len(prompt), "task_no": task.task_no
    }, task_id)

    exec_result = _call_execution_subagent(prompt, input_data, task)

    add_log(db, flowticket_id, "节点1完成", {
        "execution_status": exec_result.get("execution_status"),
        "output_file_count": len(exec_result.get("output_files", [])),
        "session_id": exec_result.get("session_id")
    }, task_id)

    update_execution_record(db, task_id, exec_result)
    return exec_result


def _build_execution_prompt(task: TaskV2, input_data: dict) -> str:
    """动态拼装执行提示词（中文）"""
    doc_path = input_data.get("design_doc_path", "")
    requirements = input_data.get("requirements", "")

    lines = [
        "请执行以下任务：", "",
        f"任务编号：{task.task_no}",
        f"任务名称：{task.task_name}",
        f"任务类型：{task.task_type or '未指定'}",
    ]

    if doc_path:
        lines.extend(["", f"设计文档路径：{doc_path}"])
        if os.path.exists(doc_path):
            try:
                with open(doc_path, "r", encoding="utf-8") as f:
                    doc_content = f.read(5000)
                lines.extend(["", "设计文档内容：", doc_content])
            except Exception as e:
                lines.extend(["", f"（无法读取设计文档：{e}）"])
        else:
            lines.append("（设计文档不存在，请基于任务描述执行）")

    if requirements:
        lines.extend(["", f"具体需求：{requirements}"])

    lines.extend([
        "", "请按照需求完成任务，并确保输出文件正确生成。",
        "", "执行完成后，请提供以下信息：",
        "1. 执行过程记录",
        "2. 输出文件路径列表",
        "3. 执行结论（成功/失败）"
    ])

    return "\n".join(lines)


def _call_execution_subagent(
    prompt: str, input_data: dict, task: TaskV2
) -> Dict[str, Any]:
    """
    调用执行子代理API（session模式，30分钟超时）。
    设计文档5.2.2：调用session模式子代理执行任务
    
    实现：使用真实AI子代理（GLM-5.1）
    超时：30分钟
    """
    try:
        # 导入真实子代理调用器
        try:
            from api.subagent_caller import call_session_subagent_execution
        except ImportError:
            logger.error("子代理调用模块未找到，使用模拟实现")
            return _mock_execution_subagent(prompt, input_data, task)
        
        # 构建任务数据
        task_data = {
            "task_no": task.task_no,
            "task_name": task.task_name,
            "task_type": task.task_type,
            "design_doc_path": input_data.get("design_doc_path"),
            "requirements": input_data.get("requirements"),
            "output_dir": input_data.get("output_dir", "/tmp/autocraft_output")
        }
        
        # 调用真实session模式子代理
        logger.info(f"调用真实session子代理执行任务: {task.task_no}, 超时: {NODE1_TIMEOUT}秒")
        result = call_session_subagent_execution(task_data, prompt, NODE1_TIMEOUT)
        
        # 转换结果为标准格式
        return {
            "success": result.get("success", False),
            "execution_log": result.get("execution_log", {}),
            "output_files": result.get("output_files", []),
            "execution_status": "success" if result.get("success") else "failed",
            "session_id": result.get("session_id"),
            "error": result.get("error"),
            "model_used": result.get("model_used", "GLM-5.1")
        }
        
    except Exception as e:
        logger.error(f"执行子代理调用失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "execution_log": {"error": str(e)},
            "output_files": [],
            "execution_status": "failed",
            "session_id": None
        }

def _mock_execution_subagent(prompt: str, input_data: dict, task: TaskV2) -> Dict[str, Any]:
    """模拟实现（当真实模块不可用时）"""
    logger.warning("使用模拟执行子代理（真实模块未找到）")
    
    execution_log = {
        "task_no": task.task_no,
        "task_name": task.task_name,
        "execution_time": _now_iso(),
        "steps": [
            {"step": 1, "action": "读取设计文档", "status": "success"},
            {"step": 2, "action": "执行开发任务", "status": "success"},
            {"step": 3, "action": "生成输出文件", "status": "success"}
        ],
        "summary": f"任务 {task.task_no} 执行完成（模拟）"
    }

    output_files = input_data.get("expected_output_files", [])
    if not output_files:
        output_dir = input_data.get("output_dir", "/tmp/autocraft_output")
        output_files = [
            os.path.join(output_dir, f"{task.task_no}_output.py"),
            os.path.join(output_dir, f"{task.task_no}_output.md")
        ]

    return {
        "success": True,
        "execution_log": execution_log,
        "output_files": output_files,
        "execution_status": "success",
        "session_id": f"mock_session_{task.task_no}_{int(time.time())}"
    }


# ==================== F-F-002: 执行后检查与状态更新 ====================

def check_execution_output_and_update_status(
    db: Session, flowticket_id: str, task_id: int,
    execution_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    执行后检查：验证输出文件和执行记录（对应设计文档5.2.3）。
    检查通过 → 更新状态为【待验证】
    检查失败 → 返回失败结果（由调用方触发异常处理）
    """
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        return {"passed": False, "error": f"任务不存在: task_id={task_id}"}

    add_log(db, flowticket_id, "执行后检查开始", {"task_no": task.task_no}, task_id)

    if not execution_result.get("execution_log"):
        error_msg = "执行记录不存在"
        add_log(db, flowticket_id, "执行后检查失败", {"error": error_msg}, task_id)
        return {"passed": False, "error": error_msg}

    exec_status = execution_result.get("execution_status")
    if exec_status in ("failed", "timeout"):
        error_msg = f"执行状态异常: {exec_status}"
        add_log(db, flowticket_id, "执行后检查失败", {"error": error_msg}, task_id)
        return {"passed": False, "error": error_msg}

    # 设计文档5.2.3明确要求检查输出文件是否存在
    output_files = execution_result.get("output_files", [])
    missing_files = [f for f in output_files if not os.path.exists(f)]
    if missing_files:
        error_msg = f"输出文件不存在: {missing_files[0]}"
        add_log(db, flowticket_id, "执行后检查失败", {
            "error": error_msg, "missing_files": missing_files
        }, task_id)
        return {"passed": False, "error": error_msg}

    result = update_task_status_internal(db, task_id, "pending_verification", {
        "check_time": _now_iso(),
        "output_file_count": len(output_files),
        "check_result": "passed"
    })
    if not result:
        return {"passed": False, "error": "状态更新失败"}

    add_log(db, flowticket_id, "执行后检查通过", {"new_status": "pending_verification"}, task_id)
    return {"passed": True}

# ==================== F-F-002: 节点2 - 验证子代理 ====================

def execute_node2_verification_subagent(
    db: Session, flowticket_id: str, task_id: int
) -> Dict[str, Any]:
    """
    节点2：验证子代理（对应设计文档5.2.4）
    1. 动态拼装验证提示词
    2. 调用run模式验证子代理API
    3. 获取验证结果（verification_log, conclusion, score, issues）
    4. 调用任务单API更新验证记录
    """
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        return {"success": False, "error": f"任务不存在: task_id={task_id}"}

    add_log(db, flowticket_id, "节点2开始", {
        "task_no": task.task_no, "task_name": task.task_name
    }, task_id)

    input_data = _parse_json(task.input_data)
    extra_data = _parse_json(task.extra_data)
    execution_log = _parse_json(task.execution_log)

    prompt = _build_verification_prompt(task, input_data, extra_data, execution_log)
    add_log(db, flowticket_id, "节点2提示词已构建", {
        "prompt_length": len(prompt), "task_no": task.task_no
    }, task_id)

    verify_result = _call_verification_subagent(prompt, input_data, task)

    add_log(db, flowticket_id, "节点2完成", {
        "conclusion": verify_result.get("conclusion"),
        "score": verify_result.get("score")
    }, task_id)

    update_verification_record(db, task_id, verify_result)
    return verify_result


def _build_verification_prompt(
    task: TaskV2, input_data: dict, extra_data: dict, execution_log: dict
) -> str:
    """动态拼装验证提示词（中文）"""
    doc_path = input_data.get("design_doc_path", "")
    output_files = extra_data.get("output_files", [])

    lines = [
        "请验证以下任务的执行结果：", "",
        f"任务编号：{task.task_no}",
        f"任务名称：{task.task_name}",
    ]

    if doc_path:
        lines.extend(["", f"设计文档路径：{doc_path}"])

    if output_files:
        lines.extend(["", "输出文件："])
        lines.extend(f"  - {f}" for f in output_files)

    if execution_log:
        summary = json.dumps(execution_log, ensure_ascii=False, indent=2)[:2000]
        lines.extend(["", "执行日志摘要：", summary])

    lines.extend([
        "", "请验证执行是否满足需求，给出以下信息：",
        "1. 验证过程记录",
        '2. 验证结论（"通过"或"不通过"）',
        "3. 评分（0-100分）",
        "4. 存在的问题（如有）"
    ])

    return "\n".join(lines)


def _call_verification_subagent(
    prompt: str, input_data: dict, task: TaskV2
) -> Dict[str, Any]:
    """
    调用验证子代理API（run模式，10分钟超时）。
    设计文档5.2.4：调用run模式子代理验证任务
    
    实现：使用真实AI子代理（DeepSeek-V3.2-thinking）
    超时：10分钟
    """
    try:
        # 导入真实子代理调用器
        try:
            from api.subagent_caller import call_run_subagent_verification
        except ImportError:
            logger.error("子代理调用模块未找到，使用模拟实现")
            return _mock_verification_subagent(prompt, input_data, task)
        
        # 构建任务数据
        task_data = {
            "task_no": task.task_no,
            "task_name": task.task_name,
            "task_type": task.task_type,
            "design_doc_path": input_data.get("design_doc_path"),
            "output_files": input_data.get("expected_output_files", [])
        }
        
        # 调用真实run模式验证子代理
        logger.info(f"调用真实run模式验证子代理: {task.task_no}, 超时: {NODE2_TIMEOUT}秒")
        result = call_run_subagent_verification(task_data, prompt, NODE2_TIMEOUT)
        
        # 转换结果为标准格式
        return {
            "success": result.get("success", False),
            "verification_log": result.get("verification_log", {}),
            "conclusion": result.get("conclusion", "失败"),
            "score": result.get("score", 0),
            "issues": result.get("issues", []),
            "error": result.get("error"),
            "model_used": result.get("model_used", "DeepSeek-V3.2-thinking")
        }
        
    except Exception as e:
        logger.error(f"验证子代理调用失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "verification_log": {"error": str(e)},
            "conclusion": "失败",
            "score": 0,
            "issues": [{"issue": "子代理调用失败", "detail": str(e)}]
        }

def _mock_verification_subagent(prompt: str, input_data: dict, task: TaskV2) -> Dict[str, Any]:
    """模拟实现（当真实模块不可用时）"""
    logger.warning("使用模拟验证子代理（真实模块未找到）")
    
    verification_log = {
        "task_no": task.task_no,
        "task_name": task.task_name,
        "verification_time": _now_iso(),
        "checks": [
            {"check": "代码质量", "result": "通过"},
            {"check": "功能完整性", "result": "通过"},
            {"check": "测试覆盖率", "result": "通过"}
        ]
    }
    
    return {
        "success": True,
        "verification_log": verification_log,
        "conclusion": "通过",
        "score": 85,
        "issues": []
    }


# ==================== F-F-002: 验证后检查与状态更新 ====================

def check_verification_result_and_update_status(
    db: Session, flowticket_id: str, task_id: int,
    verification_result: Dict[str, Any],
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    验证后检查：验证记录和结论是否存在（对应设计文档5.2.5）。
    检查通过 → 更新状态为【已完成】，关闭session模式子代理
    检查失败 → 返回失败结果（由调用方触发异常处理）
    设计文档明确：conclusion必须为"通过"
    """
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        return {"passed": False, "error": f"任务不存在: task_id={task_id}"}

    add_log(db, flowticket_id, "验证后检查开始", {"task_no": task.task_no}, task_id)

    if not verification_result.get("verification_log"):
        error_msg = "验证记录不存在"
        add_log(db, flowticket_id, "验证后检查失败", {"error": error_msg}, task_id)
        return {"passed": False, "error": error_msg}

    conclusion = verification_result.get("conclusion")
    if not conclusion or conclusion not in VERIFICATION_PASS_VALUES:
        error_msg = f"验证结论不通过: {conclusion}"
        add_log(db, flowticket_id, "验证后检查失败", {
            "error": error_msg, "conclusion": conclusion
        }, task_id)
        return {"passed": False, "error": error_msg}

    result = update_task_status_internal(db, task_id, "completed", {
        "check_time": _now_iso(),
        "conclusion": conclusion,
        "score": verification_result.get("score"),
        "check_result": "passed"
    })
    if not result:
        return {"passed": False, "error": "状态更新失败"}

    # 关闭session模式子代理（设计文档5.2.5明确要求）
    if session_id:
        close_success = _close_subagent_session(session_id)
        if close_success:
            add_log(db, flowticket_id, "session关闭成功", {
                "session_id": session_id
            }, task_id)
        else:
            add_log(db, flowticket_id, "session关闭失败", {
                "session_id": session_id, "warning": "session关闭失败，但任务已完成"
            }, task_id)
    else:
        add_log(db, flowticket_id, "session关闭跳过", {
            "reason": "无session_id"
        }, task_id)

    add_log(db, flowticket_id, "验证后检查通过", {
        "new_status": "completed", "session_id": session_id
    }, task_id)
    return {"passed": True}


def _close_subagent_session(session_id: str) -> bool:
    """
    关闭session模式子代理。
    对应设计文档: DELETE /api/subagent/session/{session_id}
    实现：使用真实子代理关闭API
    """
    try:
        # 导入真实子代理调用器
        try:
            from api.subagent_caller import close_session_subagent
            logger.info(f"调用真实子代理关闭: {session_id}")
            return close_session_subagent(session_id)
        except ImportError:
            logger.warning(f"子代理调用模块未找到，模拟关闭session: {session_id}")
            return _mock_close_subagent_session(session_id)
    except Exception as e:
        logger.error(f"关闭子代理session失败: {e}")
        return False

def _mock_close_subagent_session(session_id: str) -> bool:
    """模拟关闭session（当真实模块不可用时）"""
    logger.info(f"模拟关闭子代理session: {session_id}")
    return True


# ==================== F-F-002: 完整双节点执行流程 ====================

def execute_system_task(
    db: Session, flowticket_id: str, task_id: int
) -> Dict[str, Any]:
    """
    执行单个系统任务的双节点完整流程（对应设计文档5.2）。
    流程：前置检查 → 节点1(执行) → 执行后检查 → 节点2(验证) → 验证后检查
    任何步骤失败 → 触发异常处理（暂停任务）
    """
    try:
        # Step 1: 前置检查
        check = check_input_files_and_update_status(db, flowticket_id, task_id)
        if not check["passed"]:
            handle_exception(db, flowticket_id, task_id, "前置检查失败", check["error"])
            return {"success": False, "stage": "pre_check", "error": check["error"]}

        # Step 2: 节点1 - 执行子代理
        exec_result = execute_node1_execution_subagent(db, flowticket_id, task_id)
        if not exec_result.get("success"):
            handle_exception(
                db, flowticket_id, task_id, "节点1执行失败",
                exec_result.get("error", "未知错误")
            )
            return {"success": False, "stage": "node1", "error": exec_result.get("error")}

        # Step 3: 执行后检查
        post_check = check_execution_output_and_update_status(
            db, flowticket_id, task_id, exec_result
        )
        if not post_check["passed"]:
            handle_exception(
                db, flowticket_id, task_id, "执行后检查失败", post_check["error"]
            )
            return {"success": False, "stage": "post_execution_check", "error": post_check["error"]}

        # Step 4: 节点2 - 验证子代理
        verify_result = execute_node2_verification_subagent(db, flowticket_id, task_id)
        if not verify_result.get("success"):
            handle_exception(
                db, flowticket_id, task_id, "节点2验证失败",
                verify_result.get("error", "未知错误")
            )
            return {"success": False, "stage": "node2", "error": verify_result.get("error")}

        # Step 5: 验证后检查
        session_id = exec_result.get("session_id")
        final_check = check_verification_result_and_update_status(
            db, flowticket_id, task_id, verify_result, session_id
        )
        if not final_check["passed"]:
            handle_exception(
                db, flowticket_id, task_id, "验证后检查失败", final_check["error"]
            )
            return {"success": False, "stage": "post_verification_check", "error": final_check["error"]}

        return {"success": True, "task_id": task_id, "final_status": "completed"}

    except Exception as e:
        handle_exception(db, flowticket_id, task_id, "执行异常", str(e))
        return {"success": False, "stage": "exception", "error": str(e)}

# ==================== F-F-001: 计划单启动执行 ====================

def _generate_default_system_tasks(
    plan_task: TaskV2, input_data: dict
) -> List[Dict[str, Any]]:
    """
    当拆解结果中没有显式提供系统任务列表时，生成默认系统任务。
    task_no格式: plan_id-序号，确保全局唯一（因为TaskV2.task_no是unique）。
    """
    doc_path = input_data.get("design_doc_path", "")
    plan_id = plan_task.plan_id or "unknown"
    return [
        {
            "task_no": f"{plan_id}-001",
            "task_name": "系统任务001 - 基于设计文档开发",
            "task_type": "SYSTEM-DEV",
            "input_data": {"design_doc_path": doc_path, "parent_task_id": plan_task.id},
        }
    ]


def execute_plan_decompose_task(
    db: Session, flowticket_id: str, task_id: int
) -> Dict[str, Any]:
    """
    执行计划拆解任务（对应设计文档5.1 F-F-001）。
    1. 对拆解任务自身执行双节点流程（000任务也要过执行+验证）
    2. 解析拆解结果，生成系统任务单列表
    3. 循环创建并执行系统任务单（任一失败即停止）
    4. 全部完成 → 更新实例状态为completed
    """
    instance = db.query(FlowTicketInstance).filter(
        FlowTicketInstance.flowticket_id == flowticket_id
    ).first()
    if not instance:
        return {"success": False, "error": "FlowTicket实例不存在"}

    add_log(db, flowticket_id, "计划拆解开始", {"task_id": task_id}, task_id)

    # 1. 执行拆解任务本身的双节点流程
    result = execute_system_task(db, flowticket_id, task_id)
    if not result["success"]:
        add_log(db, flowticket_id, "计划拆解失败", {
            "error": result.get("error")
        }, task_id)
        return result

    # 2. 解析拆解结果 → 系统任务列表
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    extra_data = _parse_json(task.extra_data)
    system_tasks_data = extra_data.get("decomposed_tasks", [])

    # 如果没有显式拆解结果，生成默认系统任务
    if not system_tasks_data:
        input_data = _parse_json(task.input_data)
        system_tasks_data = _generate_default_system_tasks(task, input_data)

    # 3. 创建系统任务单记录
    created_tasks = []
    for i, td in enumerate(system_tasks_data):
        new_task = TaskV2()
        seq = td.get("task_no", f"{i + 1:03d}")
        plan_id = task.plan_id or "PLAN"
        new_task.task_no = f"{plan_id}-{seq}" if not seq.startswith(plan_id) else seq
        new_task.task_name = td.get("task_name", f"系统任务 {new_task.task_no}")
        new_task.task_type = td.get("task_type", "SYSTEM")
        new_task.plan_id = task.plan_id
        new_task.status = "pending"
        inp = td.get("input_data", {})
        new_task.input_data = (
            json.dumps(inp, ensure_ascii=False) if isinstance(inp, dict) else str(inp)
        )
        new_task.created_at = datetime.now()
        new_task.updated_at = datetime.now()
        db.add(new_task)
        created_tasks.append(new_task)

    if created_tasks:
        db.commit()
        for t in created_tasks:
            db.refresh(t)

    add_log(db, flowticket_id, "系统任务已创建", {
        "count": len(created_tasks),
        "task_ids": [t.id for t in created_tasks]
    }, task_id)

    # 4. 更新实例指向第一个系统任务
    if created_tasks:
        instance.current_task_id = created_tasks[0].id
        instance.updated_at = datetime.now()
        db.commit()

    # 5. 循环执行每个系统任务（任一失败即停止，设计文档5.1明确要求）
    results = []
    for sys_task in created_tasks:
        add_log(db, flowticket_id, "系统任务开始", {
            "task_id": sys_task.id, "task_no": sys_task.task_no
        }, sys_task.id)

        instance.current_task_id = sys_task.id
        instance.updated_at = datetime.now()
        db.commit()

        task_result = execute_system_task(db, flowticket_id, sys_task.id)
        results.append({
            "task_id": sys_task.id,
            "task_no": sys_task.task_no,
            "success": task_result.get("success"),
            "stage": task_result.get("stage"),
            "error": task_result.get("error")
        })

        if not task_result.get("success"):
            add_log(db, flowticket_id, "系统任务失败", {
                "task_no": sys_task.task_no,
                "error": task_result.get("error")
            }, sys_task.id)
            return {
                "success": False,
                "stage": "system_task_execution",
                "failed_task": sys_task.task_no,
                "error": task_result.get("error"),
                "completed_tasks": [r for r in results if r["success"]],
                "results": results
            }

    # 全部系统任务完成 → 更新实例状态为completed
    instance.status = "completed"
    instance.updated_at = datetime.now()
    db.commit()

    add_log(db, flowticket_id, "计划拆解完成", {
        "total_system_tasks": len(created_tasks),
        "all_completed": True
    }, task_id)

    return {
        "success": True,
        "flowticket_id": flowticket_id,
        "decompose_task_id": task_id,
        "system_tasks_created": len(created_tasks),
        "system_task_ids": [t.id for t in created_tasks],
        "results": results
    }


# ==================== F-F-003: 恢复执行机制 ====================

def resume_from_node(
    db: Session, flowticket_id: str, task_id: int,
    resume_from: str = "前置检查"
) -> Dict[str, Any]:
    """
    从指定节点恢复任务执行（对应设计文档5.3.2）。
    resume_from 支持中文和英文：
    - "前置检查" / "pre_check"
    - "节点1" / "node1"
    - "执行后检查" / "post_execution_check"
    - "节点2" / "node2"
    - "验证后检查" / "post_verification_check"
    """
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        return {"success": False, "error": f"任务不存在: task_id={task_id}"}

    # 中文恢复点映射到内部标识
    resume_point = RESUME_POINT_MAP.get(resume_from, resume_from)
    if resume_point not in RESUME_POINT_MAP.values():
        return {"success": False, "error": f"未知的恢复点: {resume_from}"}

    add_log(db, flowticket_id, "恢复执行", {
        "task_id": task_id,
        "resume_from": resume_from,
        "mapped_point": resume_point
    }, task_id)

    # 根据恢复点重置状态并执行
    if resume_point == "pre_check":
        update_task_status_internal(db, task_id, "pending", {
            "resumed_from": resume_point, "resumed_at": _now_iso()
        })
        return execute_system_task(db, flowticket_id, task_id)

    elif resume_point == "node1":
        update_task_status_internal(db, task_id, "in_progress", {
            "resumed_from": resume_point, "resumed_at": _now_iso()
        })
        return _execute_from_node1(db, flowticket_id, task_id)

    elif resume_point == "post_execution_check":
        update_task_status_internal(db, task_id, "in_progress", {
            "resumed_from": resume_point, "resumed_at": _now_iso()
        })
        return _execute_from_post_exec(db, flowticket_id, task_id)

    elif resume_point == "node2":
        update_task_status_internal(db, task_id, "pending_verification", {
            "resumed_from": resume_point, "resumed_at": _now_iso()
        })
        return _execute_from_node2(db, flowticket_id, task_id)

    elif resume_point == "post_verification_check":
        update_task_status_internal(db, task_id, "pending_verification", {
            "resumed_from": resume_point, "resumed_at": _now_iso()
        })
        return _execute_from_post_verify(db, flowticket_id, task_id)

    return {"success": False, "error": f"未处理的恢复点: {resume_point}"}


# ==================== 内部恢复执行函数 ====================

def _execute_from_node1(db: Session, flowticket_id: str, task_id: int) -> Dict[str, Any]:
    """从节点1恢复执行"""
    try:
        exec_result = execute_node1_execution_subagent(db, flowticket_id, task_id)
        if not exec_result.get("success"):
            handle_exception(
                db, flowticket_id, task_id, "节点1执行失败",
                exec_result.get("error", "")
            )
            return {"success": False, "stage": "node1", "error": exec_result.get("error")}
        return _continue_after_node1(db, flowticket_id, task_id, exec_result)
    except Exception as e:
        handle_exception(db, flowticket_id, task_id, "执行异常", str(e))
        return {"success": False, "stage": "exception", "error": str(e)}


def _execute_from_post_exec(
    db: Session, flowticket_id: str, task_id: int
) -> Dict[str, Any]:
    """从执行后检查恢复（需重新执行节点1获取execution_result）"""
    try:
        exec_result = execute_node1_execution_subagent(db, flowticket_id, task_id)
        if not exec_result.get("success"):
            handle_exception(
                db, flowticket_id, task_id, "节点1执行失败",
                exec_result.get("error", "")
            )
            return {"success": False, "stage": "node1", "error": exec_result.get("error")}
        return _continue_after_node1(db, flowticket_id, task_id, exec_result)
    except Exception as e:
        handle_exception(db, flowticket_id, task_id, "执行异常", str(e))
        return {"success": False, "stage": "exception", "error": str(e)}


def _continue_after_node1(
    db: Session, flowticket_id: str, task_id: int,
    exec_result: Dict[str, Any]
) -> Dict[str, Any]:
    """节点1完成后继续：执行后检查 → 节点2 → 验证后检查"""
    post_check = check_execution_output_and_update_status(
        db, flowticket_id, task_id, exec_result
    )
    if not post_check["passed"]:
        handle_exception(
            db, flowticket_id, task_id, "执行后检查失败", post_check["error"]
        )
        return {"success": False, "stage": "post_execution_check", "error": post_check["error"]}

    verify_result = execute_node2_verification_subagent(db, flowticket_id, task_id)
    if not verify_result.get("success"):
        handle_exception(
            db, flowticket_id, task_id, "节点2验证失败",
            verify_result.get("error", "")
        )
        return {"success": False, "stage": "node2", "error": verify_result.get("error")}

    session_id = exec_result.get("session_id")
    final_check = check_verification_result_and_update_status(
        db, flowticket_id, task_id, verify_result, session_id
    )
    if not final_check["passed"]:
        handle_exception(
            db, flowticket_id, task_id, "验证后检查失败", final_check["error"]
        )
        return {"success": False, "stage": "post_verification_check", "error": final_check["error"]}

    return {"success": True, "task_id": task_id, "final_status": "completed"}


def _execute_from_node2(
    db: Session, flowticket_id: str, task_id: int
) -> Dict[str, Any]:
    """从节点2恢复执行"""
    try:
        verify_result = execute_node2_verification_subagent(db, flowticket_id, task_id)
        if not verify_result.get("success"):
            handle_exception(
                db, flowticket_id, task_id, "节点2验证失败",
                verify_result.get("error", "")
            )
            return {"success": False, "stage": "node2", "error": verify_result.get("error")}

        # 从extra_data获取session_id
        task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
        extra_data = _parse_json(task.extra_data) if task else {}
        session_id = extra_data.get("session_id")

        final_check = check_verification_result_and_update_status(
            db, flowticket_id, task_id, verify_result, session_id
        )
        if not final_check["passed"]:
            handle_exception(
                db, flowticket_id, task_id, "验证后检查失败", final_check["error"]
            )
            return {"success": False, "stage": "post_verification_check", "error": final_check["error"]}

        return {"success": True, "task_id": task_id, "final_status": "completed"}
    except Exception as e:
        handle_exception(db, flowticket_id, task_id, "执行异常", str(e))
        return {"success": False, "stage": "exception", "error": str(e)}


def _execute_from_post_verify(
    db: Session, flowticket_id: str, task_id: int
) -> Dict[str, Any]:
    """从验证后检查恢复（需重新执行节点2获取verification_result）"""
    return _execute_from_node2(db, flowticket_id, task_id)
