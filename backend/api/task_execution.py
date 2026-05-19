"""
任务执行引擎 - 集成到AutoCraft主后端

从 simple_flowticket_service_optimized.py 迁移而来，
将原始 sqlite3 操作替换为 SQLAlchemy ORM。

核心功能：
- AI子代理调用（openclaw agent命令）
- 任务执行（读取任务→渲染模板→调用子代理→读JSON结果→更新状态→启动验证）
- 自动验证（验证子代理→读JSON结果→更新状态）
- 通知回调（callback_target）
"""

import os
import json
import logging
import asyncio
import subprocess
import tempfile
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db, SessionLocal
from models.task_v2 import TaskV2
from crud.task import lock_task, unlock_task
from template_engine import render_template_string

try:
    from model_agent_mapping import get_agent_for_model
    MODEL_MAPPING_AVAILABLE = True
except ImportError:
    MODEL_MAPPING_AVAILABLE = False

    def get_agent_for_model(model_name: str) -> str:
        model_lower = model_name.lower()
        if 'deepseek' in model_lower and 'thinking' in model_lower:
            return 'ac-validator'
        elif 'glm' in model_lower:
            return 'ac-glm5'
        elif 'minimax' in model_lower:
            return 'ac-minimax'
        elif 'kimi' in model_lower:
            return 'ac-kimi'
        else:
            return 'ac-glm5'

logger = logging.getLogger("task_execution")

# ============================================
# 配置
# ============================================
UNIFIED_TIMEOUT = 1800  # 30分钟
TEMPLATE_DIR = "/data/projects/autocraft/templates"
OUTPUT_DIR = "/tmp/autocraft_output"

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================
# Pydantic 模型
# ============================================

class TaskExecutionRequest(BaseModel):
    task_id: int
    model: Optional[str] = "glm-5.1"
    label: Optional[str] = None
    timeout: Optional[int] = None
    callback_target: Optional[str] = None


class TaskExecutionResponse(BaseModel):
    success: bool
    task_id: int
    task_no: Optional[str] = None
    task_name: Optional[str] = None
    status: Optional[str] = None
    execution_plan: Optional[Dict[str, Any]] = None
    sessions_spawn_params: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    estimated_timeout: Optional[int] = None


# webhook相关模型已删除（架构改为JSON文件驱动，不再需要webhook回调）


# ============================================
# 路由
# ============================================
router = APIRouter(prefix="/api/v2/tasks", tags=["任务执行引擎"])


# ============================================
# 辅助函数：数据库操作
# ============================================

def _get_db_session() -> Session:
    """获取独立的数据库会话（用于后台任务）"""
    db = SessionLocal()
    try:
        return db
    except:
        db.close()
        raise


def _get_task_from_db(task_id: int, db: Session = None) -> Optional[TaskV2]:
    """从数据库获取任务"""
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        return db.query(TaskV2).filter(TaskV2.id == task_id).first()
    finally:
        if own_session:
            db.close()


def _update_task_status(task_id: int, status: str):
    """更新任务状态"""
    db = SessionLocal()
    try:
        task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
        if task:
            task.status = status
            task.updated_at = datetime.now()
            db.commit()
            logger.info(f"任务{task_id}状态更新为: {status}")
        else:
            logger.warning(f"任务{task_id}不存在，无法更新状态")
    except Exception as e:
        db.rollback()
        logger.error(f"更新任务状态失败: {e}")
    finally:
        db.close()


def _update_task_callback_target(task_id: int, callback_target: str):
    """更新任务的callback_target（可能不在ORM模型中，用原始SQL）"""
    db = SessionLocal()
    try:
        db.execute(
            text("UPDATE tasks_v2 SET callback_target = :val WHERE id = :id"),
            {"val": callback_target, "id": task_id}
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"更新callback_target失败（字段可能不存在）: {e}")
    finally:
        db.close()


def _get_callback_target(task_id: int) -> Optional[str]:
    """获取任务的callback_target"""
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT callback_target FROM tasks_v2 WHERE id = :id"),
            {"id": task_id}
        ).fetchone()
        return result[0] if result else None
    except Exception as e:
        logger.warning(f"获取callback_target失败: {e}")
        return None
    finally:
        db.close()


# ============================================
# 模板相关
# ============================================

def read_template(template_name: str) -> str:
    """读取模板文件"""
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"模板文件不存在: {template_path}")
        return """# 任务执行指令\n\n## 任务基本信息\n- 任务编号: {{task_no}}\n- 任务名称: {{task_name}}\n\n## 任务要求\n{{requirements}}\n\n## 执行指令\n请完成以上任务，生成相应的输出文件。"""


def _parse_input_data_str(input_data_raw) -> dict:
    """解析 input_data（str或dict）为 dict"""
    if not input_data_raw:
        return {}
    if isinstance(input_data_raw, dict):
        return input_data_raw
    if isinstance(input_data_raw, str):
        try:
            return json.loads(input_data_raw)
        except:
            return {}
    return {}


def _extract_input_files(input_data: dict) -> List[str]:
    """统一提取输入文件路径（新格式 + 旧格式兼容）"""
    input_files = []
    raw = input_data.get('input_files', [])
    if raw:
        if isinstance(raw, list):
            input_files.extend(f.strip() for f in raw if isinstance(f, str) and f.strip())
        elif isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    input_files.extend(f.strip() for f in parsed if isinstance(f, str) and f.strip())
            except:
                input_files.extend(f.strip() for f in raw.split(',') if f.strip())
    # 旧格式：单个文件字段
    if not input_files:
        for field in ['design_doc_path', 'plan_doc_path', 'doc_path', 'file_path', 'input_path']:
            val = input_data.get(field)
            if val and isinstance(val, str) and val.strip():
                input_files.append(val.strip())
    return list(set(input_files))


def _parse_json_field(value, default=None):
    """解析可能是JSON字符串的字段"""
    if value is None:
        return default or []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else default or []
        except:
            return default or []
    return default or []


def parse_input_data(task: TaskV2) -> Dict[str, Any]:
    """
    统一解析任务的 input_data，返回标准化上下文。
    消除 build_execution_context 和 build_verification_prompt 中的重复逻辑。
    """
    input_data = _parse_input_data_str(task.input_data)
    input_files = _extract_input_files(input_data)

    # 兼容字段映射
    requirements = input_data.get('requirements') or input_data.get('description', '无具体要求')
    expected_output = input_data.get('expected_output') or '根据任务描述生成相应产出物'
    expected_output_files = _parse_json_field(input_data.get('expected_output_files') or input_data.get('deliverables'), [])
    deliverables = _parse_json_field(input_data.get('deliverables'), [])
    project_path = input_data.get('project_path', '未知')
    project_name = os.path.basename(project_path.rstrip('/')) if project_path and project_path != '未知' else '未知'

    return {
        "task_id": task.id,
        "task_no": task.task_no,
        "task_name": task.task_name,
        "task_type": task.task_type or '未知',
        "created_at": task.created_at.isoformat() if task.created_at else '',
        "plan_id": task.plan_id or '未知',
        "requirements": requirements,
        "expected_output": expected_output,
        "input_files": input_files,
        "expected_output_files": expected_output_files,
        "workflow_type": input_data.get('workflow_type', '未知'),
        "project_path": project_path,
        "project_name": project_name,
        "deliverables": deliverables,
        "source_file": input_data.get('source_file', '未知'),
    }


def build_execution_context(task: TaskV2) -> Dict[str, Any]:
    """构建执行上下文（基于统一解析）"""
    return parse_input_data(task)


def _format_execution_log_summary(execution_log: Dict[str, Any]) -> str:
    """将execution_log dict格式化为人类可读摘要"""
    if not execution_log:
        return "无执行日志"
    
    if isinstance(execution_log, str):
        return execution_log
    
    parts = []
    if execution_log.get('execution_log'):
        parts.append(f"执行过程: {execution_log['execution_log']}")
    if execution_log.get('output_files'):
        parts.append(f"产出文件: {', '.join(execution_log['output_files'])}")
    if execution_log.get('key_changes'):
        parts.append(f"关键变更: {', '.join(execution_log['key_changes'])}")
    if execution_log.get('issues'):
        # issues 是 dict 列表，需要提取 description 或转为字符串
        issue_summaries = [i.get('description', str(i)) if isinstance(i, dict) else str(i) for i in execution_log['issues']]
        parts.append(f"发现问题: {'; '.join(issue_summaries)}")
    
    return '\n'.join(parts) if parts else str(execution_log)


def build_verification_prompt(task_id: int, task_no: str, task_name: str, execution_log: Dict[str, Any], task_info: Optional[Dict[str, Any]] = None) -> str:
    """构建验证提示词（基于统一解析）"""
    template_content = read_template("verification_prompt_template_fixed.md")
    
    # 从任务对象获取标准化上下文
    task_obj = _get_task_from_db(task_id)
    if task_obj:
        context = parse_input_data(task_obj)
    else:
        # task不存在时使用最小上下文
        logger.error(f"验证时无法获取任务{task_id}信息")
        context = {
            "task_id": task_id, "task_no": task_no, "task_name": task_name,
            "task_type": "未知", "workflow_type": "未知", "project_path": "未知",
            "project_name": "未知", "requirements": "无", "expected_output": "无",
            "input_files": [], "expected_output_files": [], "deliverables": [],
            "source_file": "未知", "created_at": "", "plan_id": "未知",
        }
    
    # 追加验证专用字段
    context.update({
        "execution_log": execution_log,
        "execution_log_summary": _format_execution_log_summary(execution_log),
        "output_files": execution_log.get('output_files', []),
        "execution_success": execution_log.get('success', False),
        "model_used": execution_log.get('metadata', {}).get('model_used', '未知'),
        "session_id": execution_log.get('session_id', '未知'),
        "execution_time": execution_log.get('execution_time', '未知'),
        "timestamp": datetime.now().isoformat(),
    })
    
    # JSON序列化字段（用于TASK_METADATA块）
    for field in ['requirements', 'expected_output', 'source_file', 'project_path',
                  'task_name', 'task_type', 'workflow_type', 'project_name']:
        context[f"{field}_json"] = json.dumps(context.get(field, ''), ensure_ascii=False)
    for field in ['input_files', 'expected_output_files', 'deliverables']:
        context[f"{field}_json"] = json.dumps(context.get(field, []), ensure_ascii=False)
    
    prompt = render_template_string(template_content, context)
    return prompt


# ============================================
# AI子代理调用
# ============================================

class SmartCLIClient:
    """智能CLI客户端，支持重试机制"""

    def __init__(self, max_retries: int = 1):
        self.max_retries = max_retries

    async def spawn_subagent(
        self,
        task: str,
        model: str = "glm-5.1",
        label: str = None,
        timeout: Optional[int] = None,
        task_id: Optional[int] = None,
        role: str = "exec",
        task_no: str = ""
    ) -> Tuple[bool, str, str, int, str]:
        """
        调用OpenClaw子代理
        返回: (success, session_key, error_message, actual_timeout_used, reply_text)
        """
        actual_timeout = timeout or UNIFIED_TIMEOUT
        logger.info(f"使用统一超时: {actual_timeout}秒 (30分钟)")

        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"尝试 {attempt + 1}/{self.max_retries + 1}: 通过CLI创建子代理")
                success, session_key, error_msg, reply_text = await self._spawn_subagent_attempt(
                    task=task, model=model, label=label,
                    timeout=actual_timeout, attempt=attempt, task_id=task_id,
                    role=role, task_no=task_no
                )
                if success:
                    return True, session_key, "", actual_timeout, reply_text
                elif attempt < self.max_retries:
                    logger.warning(f"尝试失败，将在{2 ** attempt}秒后重试: {error_msg}")
                    await asyncio.sleep(2 ** attempt)
                else:
                    return False, "", error_msg, actual_timeout, ""
            except Exception as e:
                error_msg = f"尝试{attempt + 1}异常: {str(e)}"
                logger.error(error_msg)
                if attempt >= self.max_retries:
                    return False, "", error_msg, actual_timeout, ""

        return False, "", "所有尝试都失败", actual_timeout, ""

    async def _spawn_subagent_attempt(
        self,
        task: str,
        model: str,
        label: str,
        timeout: int,
        attempt: int,
        task_id: Optional[int] = None,
        role: str = "exec",
        task_no: str = ""
    ) -> Tuple[bool, str, str, str]:
        """单次尝试调用"""
        start_time = time.time()

        # 可读的session ID
        if task_no:
            session_id = f"explicit:{role}-{task_no}-{attempt + 1:02d}"
        else:
            timestamp_ms = int(time.time() * 1000)
            random_suffix = os.urandom(4).hex()
            session_id = f"explicit:flowticket_{timestamp_ms:x}_{random_suffix}_a{attempt}"

        task_file = None
        try:
            agent_id = get_agent_for_model(model)

            task_content = task  # 直接使用模板渲染后的提示词，不再拼接元信息

            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(task_content)
                task_file = f.name

            cmd = [
                "openclaw", "agent",
                "--agent", agent_id,
                "--session-id", session_id,
                "--json",
                "--message", f"@file:{task_file}"
            ]

            logger.info(f"使用指定Agent: {agent_id} 对应模型: {model}")
            logger.info(f"会话ID: {session_id}")

            # 设置环境变量，确保openclaw命令可执行
            env = os.environ.copy()
            # 确保PATH包含openclaw的安装路径
            openclaw_path = "/home/robin/.npm-global/bin"
            if openclaw_path not in env.get('PATH', ''):
                env['PATH'] = f"{openclaw_path}:{env.get('PATH', '')}"
            # 设置HOME环境变量
            env['HOME'] = "/home/robin"
            # 设置OPENCLAW相关环境变量
            env['OPENCLAW_SERVICE_KIND'] = 'gateway'
            env['OPENCLAW_CLI'] = '1'
            
            logger.info(f"环境PATH: {env.get('PATH', '')[:100]}...")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                execution_time = time.time() - start_time

                if process.returncode == 0:
                    logger.info(f"✅ CLI命令执行成功: 耗时{execution_time:.1f}秒")
                    reply_text = ""
                    try:
                        json_output = json.loads(stdout.decode('utf-8', errors='ignore'))
                        payloads = json_output.get('result', {}).get('payloads', [])
                        if payloads:
                            reply_text = payloads[0].get('text', '')
                            logger.info(f"AI回复文本长度: {len(reply_text)} 字符")
                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        logger.warning(f"解析--json输出失败: {e}")
                    return True, session_id, "", reply_text
                else:
                    error_output = stderr.decode('utf-8', errors='ignore')[:200]
                    error_msg = f"CLI命令失败 (code {process.returncode}): {error_output}"
                    logger.error(f"❌ {error_msg}")
                    return False, "", error_msg, ""

            except asyncio.TimeoutError:
                logger.warning(f"⏱️ CLI命令执行超时({timeout}秒)，终止进程...")
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                return False, "", f"CLI命令执行超时({timeout}秒)", ""

        except Exception as e:
            error_msg = f"CLI调用异常: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, "", error_msg, ""
        finally:
            # 延迟删除临时文件，避免子代理还没读完就被删
            if task_file and os.path.exists(task_file):
                def _delayed_cleanup(path, delay=300):
                    import time as _time
                    _time.sleep(delay)
                    try:
                        if os.path.exists(path):
                            os.unlink(path)
                    except:
                        pass
                import threading
                threading.Thread(target=_delayed_cleanup, args=(task_file,), daemon=True).start()


# 全局客户端实例
smart_cli_client = SmartCLIClient(max_retries=1)


# ============================================
# JSON结果解析 + 返工
# ============================================

async def parse_json_result(json_file_path: str, session_id: str, task_id: int, retry_prompt: str = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """读取并解析AI生成的JSON结果文件，失败则返工1次"""
    for attempt in range(2):
        if os.path.exists(json_file_path):
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"✅ JSON结果文件解析成功: {json_file_path}")
                return True, data
            except json.JSONDecodeError as e:
                logger.warning(f"JSON解析失败(尝试{attempt+1}): {e}")
                if attempt == 0:
                    rework_msg = f"你生成的JSON文件格式有误，请修正后重新生成到: {json_file_path}\n错误: {str(e)}"
                    if retry_prompt:
                        rework_msg += f"\n{retry_prompt}"
                    await _send_message_to_session(session_id, rework_msg)
                    continue
                else:
                    return False, None
        else:
            logger.warning(f"JSON结果文件不存在(尝试{attempt+1}): {json_file_path}")
            if attempt == 0:
                rework_msg = f"请按要求生成JSON结果文件到: {json_file_path}"
                if retry_prompt:
                    rework_msg += f"\n{retry_prompt}"
                await _send_message_to_session(session_id, rework_msg)
                continue
            else:
                return False, None

    return False, None


async def _send_message_to_session(session_id: str, message: str):
    """向已有session发送返工消息（用于JSON解析失败后的返工）
    
    ⚠️ 注意：openclaw agent --session-id 对explicit session会创建新进程，
    这是一个已知限制（LRN-20260511-001）。返工消息可能产生重复进程。
    当前策略：仅返工1次，且记录warning。
    """
    logger.warning(f"⚠️ 向session {session_id} 发送返工消息（可能产生新进程）")
    try:
        cmd = [
            "openclaw", "agent",
            "--session-id", session_id,
            "--message", message
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        if process.returncode == 0:
            logger.info(f"✅ 返工消息发送并执行成功")
        else:
            error_output = stderr.decode('utf-8', errors='ignore')[:200]
            logger.error(f"❌ 返工消息执行失败: {error_output}")
    except asyncio.TimeoutError:
        logger.error(f"❌ 返工消息执行超时")
    except Exception as e:
        logger.error(f"❌ 返工消息发送异常: {str(e)}")


# ============================================
# 通知回调
# ============================================

async def notify_callback_target(task_id: int, task_no: str, task_name: str, final_status: str,
                                  dimension_results: Optional[dict] = None, verification_report: Optional[str] = None):
    """根据callback_target通知调用方"""
    callback_target = _get_callback_target(task_id)

    if not callback_target:
        logger.info(f"任务{task_id}无callback_target，跳过通知")
        return

    logger.info(f"准备通知调用方: {callback_target}")

    status_text = "✅ 验证通过" if final_status == 'verified' else "❌ 验证失败"
    dim_text = ""
    if dimension_results:
        passes = sum(1 for v in dimension_results.values() if v == 'PASS')
        fails = sum(1 for v in dimension_results.values() if v == 'FAIL')
        dim_text = f"，维度: {passes}PASS/{fails}FAIL"
    notification_message = f"📋 任务单完成通知\n\n任务编号: {task_no}\n任务名称: {task_name}\n最终状态: {status_text}{dim_text}\n\n"

    if final_status == 'verified':
        notification_message += "任务已通过验证，可以继续下一步工作。"
    else:
        notification_message += f"任务未通过验证，请检查并修复问题。"
        if verification_report:
            notification_message += f"\n\n验证报告摘要: {verification_report[:500]}"

    try:
        if callback_target.startswith("http://") or callback_target.startswith("https://"):
            import httpx
            payload = {
                "task_id": task_id,
                "task_no": task_no,
                "task_name": task_name,
                "final_status": final_status,
                "dimension_results": dimension_results,
                "verification_report": verification_report,
                "message": notification_message
            }
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(callback_target, json=payload)
                if response.status_code == 200:
                    logger.info(f"✅ HTTP回调通知成功: {callback_target}")
                else:
                    logger.error(f"❌ HTTP回调通知失败: status={response.status_code}")
        else:
            # OpenClaw会话消息
            cmd = [
                "openclaw", "agent",
                "--session-id", callback_target,
                "--message", notification_message
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
            if process.returncode == 0:
                logger.info(f"✅ OpenClaw会话通知成功: {callback_target}")
            else:
                error_output = stderr.decode('utf-8', errors='ignore')[:200]
                logger.error(f"❌ OpenClaw会话通知失败: {error_output}")
    except asyncio.TimeoutError:
        logger.error(f"❌ 通知超时: {callback_target}")
    except Exception as e:
        logger.error(f"❌ 通知异常: {str(e)}")


# ============================================
# 验证子代理
# ============================================

async def start_verification_agent(task_id: int, task_no: str, task_name: str, execution_log: Dict[str, Any]):
    """启动验证子代理验证执行结果，等待完成后读取JSON结果文件"""
    logger.info(f"🚀 开始验证任务{task_id} ({task_no}): {task_name}")

    # 0. 锁定任务（验证阶段）
    db_lock = SessionLocal()
    try:
        lock_result = lock_task(db_lock, task_no, "verify-agent")
        if not lock_result['success']:
            logger.warning(f"验证锁定失败: {lock_result.get('error')}")
        else:
            logger.info(f"任务已锁定: verify-agent")
    finally:
        db_lock.close()

    try:
        # 1. 构建验证提示词（parse_input_data内部会查询数据库）
        verification_prompt = build_verification_prompt(task_id, task_no, task_name, execution_log)
        logger.info(f"验证提示词构建完成，长度: {len(verification_prompt)} 字符")

        # 2. 更新状态为验证中
        _update_task_status(task_id, "verifying")

        # 3. 调用验证子代理
        global smart_cli_client
        if smart_cli_client is None:
            logger.error("smart_cli_client实例未初始化")
            _update_task_status(task_id, "verification_failed")
            await notify_callback_target(task_id, task_no, task_name, "verification_failed",
                                         verification_report="验证子代理客户端未初始化")
            return

        success, verification_session, error_msg, used_timeout, verification_reply = await smart_cli_client.spawn_subagent(
            task=verification_prompt,
            model="deepseek-v3.2-thinking",
            label=f"验证任务{task_id}",
            timeout=UNIFIED_TIMEOUT,
            task_id=task_id,
            role="verify",
            task_no=task_no
        )

        if not success:
            logger.error(f"验证子代理执行失败: {error_msg}")
            _update_task_status(task_id, "verification_failed")
            await notify_callback_target(task_id, task_no, task_name, "verification_failed",
                                         verification_report=f"验证子代理执行失败: {error_msg}")
            return

        logger.info(f"✅ 验证子代理执行完成: {verification_session}")

        # 4. 读取验证结果JSON文件
        json_result_path = f"/tmp/autocraft_output/{task_id}_verification_result.json"
        parse_success, verification_data = await parse_json_result(
            json_file_path=json_result_path,
            session_id=verification_session,
            task_id=task_id,
            retry_prompt="请按要求生成验证结果JSON文件"
        )

        if not parse_success:
            logger.error(f"验证结果JSON文件解析失败")
            _update_task_status(task_id, "verification_failed")
            await notify_callback_target(task_id, task_no, task_name, "verification_failed",
                                         verification_report=f"验证结果JSON文件解析失败")
            return

        logger.info(f"✅ 验证结果JSON解析成功")

        # 5. 提取验证结论
        verification_success = verification_data.get('verification_success', False)
        verification_report = verification_data.get('verification_report', '')
        dimension_results = verification_data.get('dimension_results', {})
        issues_found = verification_data.get('issues_found', [])
        improvements_suggested = verification_data.get('improvements_suggested', [])

        # 统计维度结果
        pass_count = sum(1 for v in dimension_results.values() if v == 'PASS')
        fail_count = sum(1 for v in dimension_results.values() if v == 'FAIL')
        total_dims = len(dimension_results)

        # 兜底检查：dimension_results 为空视为验证不完整
        if not dimension_results:
            logger.warning(f"⚠️ dimension_results 为空，验证子代理未按模板输出，视为验证失败")
            verification_success = False
            issues_found.insert(0, "验证子代理未按要求输出 dimension_results 字段")

        new_status = 'verified' if verification_success else 'verification_failed'
        logger.info(f"验证{'通过' if verification_success else '失败'}，维度: {pass_count}PASS/{fail_count}FAIL/{total_dims}总计")

        # 6. 更新数据库
        verification_log = {
            "verification_success": verification_success,
            "verification_report": verification_report,
            "dimension_results": dimension_results,
            "issues_found": issues_found,
            "improvements_suggested": improvements_suggested,
            "verification_time": datetime.now().isoformat(),
            "source": "json_file"
        }

        db = SessionLocal()
        try:
            task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
            if task:
                task.status = new_status
                task.verification_log = json.dumps(verification_log, ensure_ascii=False, indent=2)
                task.updated_at = datetime.now()
                db.commit()
                logger.info(f"任务{task_id}验证状态更新完成: {new_status}")
        except Exception as e:
            db.rollback()
            logger.error(f"更新验证结果失败: {e}")
        finally:
            db.close()

        # 6.5 解锁任务
        db_unlock = SessionLocal()
        try:
            unlock_task(db_unlock, task_no, "verify-agent")
            logger.info(f"验证完成，任务已解锁: {task_no}")
        except Exception as e:
            logger.warning(f"解锁任务失败: {e}")
        finally:
            db_unlock.close()

        # 7. 通知调用方
        await notify_callback_target(task_id, task_no, task_name, new_status,
                                     dimension_results=dimension_results,
                                     verification_report=verification_report)

        logger.info(f"📋 验证完成: 任务{task_id} ({task_no}) -> {new_status}, {pass_count}PASS/{fail_count}FAIL")

    except Exception as e:
        logger.error(f"验证子代理异常: {str(e)}")
        _update_task_status(task_id, "verification_failed")
        await notify_callback_target(task_id, task_no, task_name, "verification_failed",
                                     verification_report=f"验证子代理异常: {str(e)}")
        # 异常时也要解锁
        db_unlock = SessionLocal()
        try:
            unlock_task(db_unlock, task_no, "verify-agent")
        except:
            pass
        finally:
            db_unlock.close()


# ============================================
# API端点
# ============================================

@router.post("/execute", response_model=TaskExecutionResponse)
async def execute_task(request: TaskExecutionRequest, background_tasks: BackgroundTasks):
    """执行任务单"""

    task_id = request.task_id
    model = request.model
    label = request.label or f"执行任务{task_id}"
    custom_timeout = request.timeout

    logger.info(f"收到执行请求: 任务ID={task_id}, 模型={model}")

    # 1. 获取任务信息
    db = SessionLocal()
    try:
        task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail=f"任务单不存在: {task_id}")

        task_no = task.task_no
        task_name = task.task_name
        current_status = task.status

        logger.info(f"找到任务: {task_no} - {task_name}, 状态: {current_status}")

        # 2. 检查任务状态
        if current_status not in ['pending', 'failed']:
            logger.warning(f"任务状态不是pending或failed: {current_status}")

        # 2.1 检查锁定状态
        if task.locked_by:
            raise HTTPException(status_code=409, detail=f"任务已被 {task.locked_by} 锁定")

        # 3. 构建上下文
        context = build_execution_context(task)

        # 3.5 检查project_path
        if context.get('project_path') == '未知':
            logger.error(f"任务{task_id}缺少project_path，拒绝执行")
            raise HTTPException(status_code=400, detail="任务缺少project_path，无法执行")

        # 3.6 锁定任务
        lock_result = lock_task(db, task_no, f"exec-{model}")
        if not lock_result['success']:
            raise HTTPException(status_code=409, detail=f"任务锁定失败: {lock_result.get('error', '未知原因')}")
        logger.info(f"任务已锁定: exec-{model}")

        # 4. 读取模板并渲染
        template_content = read_template("execution_prompt_template.md")
        prompt = render_template_string(template_content, context)
        logger.info(f"提示词生成完成，长度: {len(prompt)} 字符")

        # 5. 更新任务状态为执行中
        task.status = "in_progress"
        task.updated_at = datetime.now()
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"数据库操作失败: {str(e)}")
    finally:
        db.close()

    # 6. 保存callback_target
    if request.callback_target:
        _update_task_callback_target(task_id, request.callback_target)
        logger.info(f"已保存callback_target: {request.callback_target}")

    # 7. 准备执行计划
    execution_plan = {
        "task_id": task_id,
        "task_no": task_no,
        "prompt_length": len(prompt),
        "model": model,
        "label": label,
        "custom_timeout": custom_timeout,
        "expected_output_files": context.get('expected_output_files', []),
        "template_used": True,
        "timestamp": datetime.now().isoformat()
    }

    # 8. 调用OpenClaw子代理
    logger.info(f"正在调用OpenClaw子代理...")

    success, session_key, error_msg, used_timeout, reply_text = await smart_cli_client.spawn_subagent(
        task=prompt,
        model=model,
        label=label,
        timeout=custom_timeout,
        task_id=task_id,
        role="exec",
        task_no=task_no
    )

    if not success:
        logger.error(f"子代理调用失败: {error_msg}")
        _update_task_status(task_id, "failed")
        await notify_callback_target(task_id, task_no, task_name, "failed",
                                     verification_report=f"执行子代理启动失败: {error_msg}")
        return TaskExecutionResponse(
            success=False, task_id=task_id, task_no=task_no, task_name=task_name,
            status="failed", execution_plan=execution_plan,
            sessions_spawn_params={"error": error_msg}, error=error_msg,
            estimated_timeout=used_timeout
        )

    logger.info(f"子代理执行成功: {session_key}")

    # 9. 读取AI生成的JSON结果文件
    json_result_path = f"/tmp/autocraft_output/{task_id}_execution_result.json"
    parse_success, execution_data = await parse_json_result(
        json_file_path=json_result_path,
        session_id=session_key,
        task_id=task_id,
        retry_prompt="请确保生成有效的JSON结果文件"
    )

    if not parse_success:
        logger.error(f"执行结果JSON文件解析失败")
        _update_task_status(task_id, "failed")
        await notify_callback_target(task_id, task_no, task_name, "failed",
                                     verification_report="执行结果JSON文件解析失败")
        return TaskExecutionResponse(
            success=False, task_id=task_id, task_no=task_no, task_name=task_name,
            status="failed", execution_plan=execution_plan,
            sessions_spawn_params={"session_key": session_key},
            error="执行结果JSON文件解析失败", estimated_timeout=used_timeout
        )

    logger.info(f"✅ 执行结果JSON解析成功: success={execution_data.get('success')}")

    # 10. 更新任务状态
    exec_success = execution_data.get('success', False)
    new_status = 'completed' if exec_success else 'failed'

    db = SessionLocal()
    try:
        task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
        if task:
            task.status = new_status
            task.execution_log = json.dumps(execution_data, ensure_ascii=False, indent=2)
            task.updated_at = datetime.now()
            db.commit()
            logger.info(f"任务{task_id}状态更新为: {new_status}")
    except Exception as e:
        db.rollback()
        logger.error(f"更新执行结果失败: {e}")
    finally:
        db.close()

    # 10.5 解锁任务（执行完成，交由验证阶段重新锁定）
    db_unlock = SessionLocal()
    try:
        unlock_task(db_unlock, task_no, f"exec-{model}")
        logger.info(f"执行完成，任务已解锁: {task_no}")
    except Exception as e:
        logger.warning(f"解锁任务失败: {e}")
    finally:
        db_unlock.close()

    # 11. 执行失败时通知
    if not exec_success:
        await notify_callback_target(task_id, task_no, task_name, "failed",
                                     verification_report=execution_data.get('error', '执行失败'))

    # 12. 执行成功时启动验证子代理
    if exec_success:
        logger.info(f"启动验证子代理验证任务{task_id}...")
        background_tasks.add_task(start_verification_agent, task_id, task_no, task_name, execution_data)

    # 13. 返回执行结果
    return TaskExecutionResponse(
        success=True, task_id=task_id, task_no=task_no, task_name=task_name,
        status=new_status, execution_plan=execution_plan,
        sessions_spawn_params={
            "session_key": session_key,
            "reply_text": reply_text[:500] if reply_text else None,
            "model": model, "label": label, "timeout_used": used_timeout
        },
        error=None, estimated_timeout=used_timeout
    )


@router.get("/{task_id}/status")
async def get_task_execution_status(task_id: int, db: Session = Depends(get_db)):
    """获取任务执行状态"""
    task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"任务单不存在: {task_id}")

    result = {
        "task_id": task.id,
        "task_no": task.task_no,
        "task_name": task.task_name,
        "status": task.status,
        "input_data": None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None
    }

    # 解析input_data
    if task.input_data:
        try:
            result["input_data"] = json.loads(task.input_data) if isinstance(task.input_data, str) else task.input_data
        except:
            result["input_data"] = task.input_data

    # 解析JSON字段
    for field in ['execution_log', 'verification_log']:
        value = getattr(task, field)
        if value:
            try:
                result[field] = json.loads(value) if isinstance(value, str) else value
            except:
                result[field] = value
        else:
            result[field] = None

    return result



