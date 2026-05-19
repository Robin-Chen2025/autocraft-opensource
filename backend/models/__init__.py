"""
数据库模型包
"""
# 从原来的 models.py 导入 AutoCraft 核心模型
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入原始模型（通过 models_old 别名避免循环导入）
from database import Base

# 手动定义核心模型的导入
# 注意：这里需要从 models.py（同级文件）导入
# 由于 models/ 目录存在，需要用 importlib
import importlib.util
spec = importlib.util.spec_from_file_location("models_original", 
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "models.py"))
models_original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models_original)

# 导出核心模型
ProjectProfile = models_original.ProjectProfile
ProjectPhase = models_original.ProjectPhase
WorkPlan = models_original.WorkPlan
Task = models_original.Task
AgentProfile = models_original.AgentProfile

# 导入新的 Issue 相关模型
from models.issue import Issue
from models.issue_status_log import IssueStatusLog
from models.issue_task_relation import IssueTaskRelation
from models.issue_summary import IssueSummary
from models.issue_assign_log import IssueAssignLog
from models.knowledge_base import KnowledgeBase
from models.knowledge_reference import KnowledgeReference
from models.checklist import Checklist

__all__ = [
    # AutoCraft 核心模型
    "Base", "ProjectProfile", "ProjectPhase", 
    "WorkPlan", "Task", "AgentProfile",
    # Issue 相关模型
    "Issue", "IssueStatusLog", "IssueTaskRelation", 
    "IssueSummary", "IssueAssignLog",
    "KnowledgeBase", "KnowledgeReference",
    # Checklist 模型
    "Checklist"
]