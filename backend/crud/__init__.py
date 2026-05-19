"""
CRUD 操作模块
"""
from crud.task import create_task, get_task_by_no, get_tasks, update_task, delete_task
from crud.profiles import (
    get_profiles, get_profile, create_profile, update_profile, delete_profile,
    get_profile_phases
)
from crud.plans import get_plans, get_plan, create_plan, get_plan_tasks
from crud.issue import (
    create_issue, get_issue_by_id, get_issue_by_no, get_issues,
    update_issue, delete_issue, assign_issue, resolve_issue, close_issue
)
from crud.issue_status_log import create_status_log
from crud.issue_assign_log import create_assign_log
from crud.knowledge_base import (
    create_knowledge, get_knowledge_by_id, get_knowledge_by_issue_id,
    get_knowledge_by_issue_no, search_knowledge, update_knowledge,
    mark_as_featured, increment_view_count, delete_knowledge
)
from crud.knowledge_reference import get_references_by_knowledge_id, create_reference