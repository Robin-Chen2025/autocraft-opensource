"""
API 路由模块
"""
from api.issues import router as issues_router
from api.issue_status import router as issue_status_router
from api.issue_assignment import router as issue_assignment_router
from api.issue_tasks import router as issue_tasks_router
from api.issue_resolution import router as issue_resolution_router
from api.issue_summary import router as issue_summary_router
from api.knowledge import router as knowledge_router
from api.checklists import router as checklists_router

__all__ = ["issues_router", "issue_status_router", "issue_assignment_router", "issue_tasks_router", "issue_resolution_router", "issue_summary_router", "knowledge_router", "checklists_router"]
