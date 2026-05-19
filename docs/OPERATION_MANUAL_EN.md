# AutoCraft System Operation Manual

**Version**: 1.0  
**Updated**: 2026-05-19  
**Audience**: OpenClaw Main Agent

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Four-Level Management Structure](#2-four-level-management-structure)
3. [Project Management](#3-project-management)
4. [Phase Management](#4-phase-management)
5. [Plan Management](#5-plan-management)
6. [Task Management](#6-task-management)
7. [Task Execution Engine](#7-task-execution-engine)
8. [Common Operation Workflows](#8-common-operation-workflows)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. System Overview

### 1.1 System Positioning

AutoCraft is an AI-driven task management and execution platform with core capabilities:

- **Four-Level Management**: Project → Phase → Plan → Task
- **AI Execution**: Automatic task execution via OpenClaw sub-agents
- **Automatic Verification**: Verification workflow triggered after execution completion

### 1.2 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw Main Agent                   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │              AutoCraft Frontend (Vue3)           │    │
│  │              http://localhost:8080               │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │                                │
│  ┌──────────────────────▼──────────────────────────┐    │
│  │              AutoCraft Backend (FastAPI)         │    │
│  │              http://localhost:9001               │    │
│  │  ┌─────────────────────────────────────────┐    │    │
│  │  │  Four-Level: Project/Phase/Plan/Task    │    │    │
│  │  ├─────────────────────────────────────────┤    │    │
│  │  │  Execution Engine: Task + Auto Verify   │    │    │
│  │  └─────────────────────────────────────────┘    │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │                                │
│  ┌──────────────────────▼──────────────────────────┐    │
│  │           OpenClaw Sub-Agent Cluster             │    │
│  │  ac-executor │ ac-validator │ ac-builder         │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 1.3 Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Backend API | 9001 | FastAPI service |
| Frontend UI | 8080 | Vue3 dev server |
| API Docs | 9001/docs | Swagger UI |

---

## 2. Four-Level Management Structure

### 2.1 Hierarchy

```
Project
  └── Phase
        └── Plan
              └── Task
```

### 2.2 Level Responsibilities

| Level | Identifier | Responsibility | Example |
|--------|------------|----------------|---------|
| **Project** | `profile_id` | Project overview, basic info | DeepTutor-Lite |
| **Phase** | `phase_record_id` | Development phase division | M-01 Backend Dev |
| **Plan** | `plan_id` | Related task collection | WP-M01-BE-001 |
| **Task** | `task_no` | Minimum execution unit | DTL-INFRA-001-001 |

### 2.3 Naming Conventions

**Project ID**: `{project-abbr}`
```
deeptutor-lite
autocraft
```

**Phase ID**: `{project-id}-{phase-abbr}-phase`
```
deeptuto-infra-phase      # Infrastructure phase
deeptuto-m01-be-phase     # M-01 Backend phase
```

**Plan ID**: `plan_{uuid-first-16-chars}`
```
plan_5e9039a1665c47ab
plan_b4ffaa5474b44734
```

**Task Number**: `{project-prefix}-{phase}-{seq}-{sub-seq}`
```
DTL-INFRA-001-001
DTL-M01-BE-002-003
```

---

## 3. Project Management

### 3.1 Create Project

**API**: `POST /profiles`

**Request Body**:
```json
{
  "profile_type": "instance",
  "profile_name": "DeepTutor-Lite AI Learning System",
  "project_type": "Web Application",
  "description": "AI-powered intelligent learning system",
  "tech_stack": "Vue3 + FastAPI + SQLite",
  "root_path": "/data/projects/deeptutor-lite"
}
```

**Response**:
```json
{
  "message": "Project created successfully",
  "profile_id": "deeptutor-lite"
}
```

### 3.2 List Projects

**API**: `GET /profiles?page=1&page_size=10`

**Response**:
```json
{
  "total": 5,
  "items": [
    {
      "profile_id": "deeptutor-lite",
      "profile_name": "DeepTutor-Lite AI Learning System",
      "status": "active",
      ...
    }
  ],
  "page": 1,
  "page_size": 10
}
```

### 3.3 Get Project Details

**API**: `GET /profiles/{profile_id}`

**Example**: `GET /profiles/deeptutor-lite`

### 3.4 Update Project

**API**: `PUT /profiles/{profile_id}`

**Request Body**:
```json
{
  "profile_name": "New Project Name",
  "status": "active"
}
```

### 3.5 Delete Project

**API**: `DELETE /profiles/{profile_id}`

**⚠️ Warning**: Deleting a project cascades to delete all phases, plans, and tasks.

---

## 4. Phase Management

### 4.1 Create Phase

**API**: `POST /profiles/{profile_id}/phases`

**Request Body**:
```json
{
  "phase_id": "m01-be",
  "phase_name": "M-01 Backend Development",
  "phase_order": 1,
  "status": "pending"
}
```

**Response**:
```json
{
  "message": "Phase created successfully",
  "phase_record_id": "deeptuto-m01-be-phase"
}
```

### 4.2 List Phases

**API**: `GET /profiles/{profile_id}/phases`

**Response**:
```json
[
  {
    "phase_record_id": "deeptuto-infra-phase",
    "phase_id": "infra",
    "phase_name": "INFRA Infrastructure",
    "phase_order": 0,
    "status": "completed"
  },
  {
    "phase_record_id": "deeptuto-m01-be-phase",
    "phase_id": "m01-be",
    "phase_name": "M-01 Backend Development",
    "phase_order": 1,
    "status": "in_progress"
  }
]
```

### 4.3 Update Phase

**API**: `PUT /phases/{phase_record_id}`

**Request Body**:
```json
{
  "phase_name": "M-01 Backend Development (In Progress)",
  "status": "in_progress"
}
```

### 4.4 Delete Phase

**API**: `DELETE /phases/{phase_record_id}`

---

## 5. Plan Management

### 5.1 Create Plan

**API**: `POST /plans`

**Request Body**:
```json
{
  "profile_id": "deeptutor-lite",
  "phase_record_id": "deeptuto-m01-be-phase",
  "plan_name": "WP-M01-BE-001: User Authentication Module",
  "description": "Implement user login, registration, permission verification",
  "status": "pending"
}
```

**Response**:
```json
{
  "message": "Plan created successfully",
  "plan_id": "plan_b4ffaa5474b44734"
}
```

### 5.2 List Plans

**API**: `GET /plans`

**Parameters**:
- `profile_id`: Filter by project
- `phase_record_id`: Filter by phase
- `status`: Filter by status

### 5.3 Get Plan Details

**API**: `GET /plans/{plan_id}`

**Response**: Contains plan info and associated project/phase info

### 5.4 Get Tasks Under Plan

**API**: `GET /plans/{plan_id}/tasks`

### 5.5 Update Plan

**API**: `PUT /plans/{plan_id}`

**Request Body**:
```json
{
  "plan_name": "Updated Plan Name",
  "status": "in_progress"
}
```

### 5.6 Delete Plan

**API**: `DELETE /plans/{plan_id}`

---

## 6. Task Management

### 6.1 Task Structure

**Tasks contain 33 fields**, core fields:

| Field | Type | Description |
|-------|------|-------------|
| `task_no` | string | Task number (unique identifier) |
| `task_name` | string | Task name |
| `task_type` | string | Task type |
| `status` | string | Status: pending/locked/executing/completed/failed |
| `priority` | string | Priority: high/medium/low |
| `plan_id` | string | Parent plan |
| `phase_record_id` | string | Parent phase |
| `executor` | string | Executor |
| `verifier` | string | Verifier |
| `input_data` | json | Input data |
| `execution_log` | json | Execution log |
| `verification_result` | string | Verification result |

### 6.2 List Tasks

**API**: `GET /tasks`

**Parameters**:
- `page`: Page number
- `page_size`: Page size
- `status`: Status filter
- `plan_id`: Filter by plan
- `keyword`: Keyword search

**Response**:
```json
{
  "total": 659,
  "items": [...],
  "page": 1,
  "page_size": 20
}
```

### 6.3 Get Task Details

**API**: `GET /tasks/{task_no}`

**Response**: Contains all 33 task fields

### 6.4 Update Task

**API**: `PUT /tasks/{task_no}`

**Request Body**:
```json
{
  "status": "pending",
  "priority": "high",
  "executor": "ac-executor"
}
```

### 6.5 Task Status Flow

```
pending → locked → executing → completed
                    ↓
                  failed
```

| Status | Description |
|--------|-------------|
| `pending` | Waiting for execution |
| `locked` | Locked, waiting for execution |
| `executing` | Executing |
| `completed` | Execution completed |
| `failed` | Execution failed |

---

## 7. Task Execution Engine

### 7.1 Execution Flow

```
┌─────────────┐
│  1. Lock Task │  Prevent concurrent conflicts
└──────┬──────┘
       ↓
┌─────────────┐
│  2. Read Task │  Parse input_data
└──────┬──────┘
       ↓
┌─────────────┐
│  3. Render   │  Generate execution prompt
│    Template  │
└──────┬──────┘
       ↓
┌─────────────┐
│  4. Call Sub │  openclaw agent
│    Agent     │
└──────┬──────┘
       ↓
┌─────────────┐
│  5. Parse    │  Read JSON output
│    Result    │
└──────┬──────┘
       ↓
┌─────────────┐
│  6. Update   │  Record execution log
│    Status    │
└──────┬──────┘
       ↓
┌─────────────┐
│  7. Unlock   │  Hand to verification
│    Task      │
└──────┬──────┘
       ↓
┌─────────────┐
│  8. Start    │  Auto trigger verification
│    Verify    │
└─────────────┘
```

### 7.2 Execute Task

**API**: `POST /api/v2/tasks/execute`

**Request Body**:
```json
{
  "task_id": 123,
  "model": "glm-5",
  "label": "exec-session-001",
  "timeout": 1800
}
```

**Response**:
```json
{
  "success": true,
  "task_id": 123,
  "task_no": "DTL-INFRA-001-001",
  "status": "completed",
  "execution_plan": {...},
  "sessions_spawn_params": {
    "session_key": "agent:ac-executor:explicit:exec-001"
  }
}
```

### 7.3 Get Execution Status

**API**: `GET /api/v2/tasks/{task_id}/status`

**Response**:
```json
{
  "task_id": 123,
  "task_no": "DTL-INFRA-001-001",
  "status": "completed",
  "execution_log": {
    "success": true,
    "output_files": ["src/api/auth.py", "src/models/user.py"],
    "key_changes": ["Added user model", "Implemented login API"]
  }
}
```

### 7.4 input_data Structure

Task execution depends on `input_data` field, standard structure:

```json
{
  "requirements": "Implement user login with email and phone support",
  "expected_output": "Generate auth.py and related test files",
  "input_files": ["/docs/api-design.md", "/docs/db-schema.md"],
  "expected_output_files": ["src/api/auth.py", "tests/test_auth.py"],
  "project_path": "/data/projects/deeptutor-lite",
  "workflow_type": "BUILD-CODE"
}
```

### 7.5 Execution Template

Execution engine uses templates to generate prompts:

**Template Location**: `backend/templates/execution_prompt_template.md`

**Template Variables**:
- `{{task_no}}` - Task number
- `{{task_name}}` - Task name
- `{{requirements}}` - Task requirements
- `{{input_files}}` - Input file list
- `{{expected_output}}` - Expected output

### 7.6 Verification Flow

Verification triggered automatically after successful execution:

1. **Lock Task** - Verification phase lock
2. **Build Verification Prompt** - Based on execution results
3. **Call Verification Agent** - `ac-validator`
4. **Parse Verification Result** - Pass/Fail
5. **Update Verification Status** - Record verification log

---

## 8. Common Operation Workflows

### 8.1 Complete New Project Creation Flow

```bash
# 1. Create project
POST /profiles
{
  "profile_type": "instance",
  "profile_name": "New Project Name",
  "project_type": "Web Application"
}

# 2. Create phase
POST /profiles/{profile_id}/phases
{
  "phase_id": "phase-1",
  "phase_name": "First Phase",
  "phase_order": 1
}

# 3. Create plan
POST /plans
{
  "profile_id": "{profile_id}",
  "phase_record_id": "{phase_record_id}",
  "plan_name": "First Plan"
}

# 4. Create tasks (via import or manual)
# Tasks typically created via batch import script
```

### 8.2 Task Execution Flow

```bash
# 1. View pending tasks
GET /tasks?status=pending

# 2. Execute task
POST /api/v2/tasks/execute
{
  "task_id": 123,
  "model": "glm-5"
}

# 3. Query execution status
GET /api/v2/tasks/123/status

# 4. View execution result
GET /tasks/DTL-INFRA-001-001
```

### 8.3 Batch Task Execution

```bash
# Get all pending tasks under a plan
GET /plans/{plan_id}/tasks?status=pending

# Execute one by one (or in parallel, note locking mechanism)
for task in tasks:
    POST /api/v2/tasks/execute
    {
      "task_id": task.id,
      "model": "glm-5"
    }
```

---

## 9. Troubleshooting

### 9.1 Task Execution Failed

**Symptom**: Task status becomes `failed`

**Troubleshooting Steps**:
1. Check execution log: `GET /tasks/{task_no}` → `execution_log`
2. Check sub-agent config: `openclaw agent list`
3. Check model config: `~/.openclaw/openclaw.json`
4. Check if OpenClaw patches applied

### 9.2 Task Locked Cannot Unlock

**Symptom**: Task status is `locked`, cannot execute

**Solution**:
```bash
# Manual unlock
PUT /tasks/{task_no}
{
  "status": "pending",
  "locked_by": null,
  "locked_at": null
}
```

### 9.3 Sub-Agent Call Failed

**Symptom**: `openclaw agent` command fails

**Troubleshooting**:
1. Check OpenClaw installation: `openclaw --version`
2. Check sub-agent exists: `openclaw agent list`
3. Check PATH environment variable
4. Apply patches: `bash openclaw-config/patches/apply-patch.sh`

### 9.4 Database Locked

**Symptom**: API returns 500 error, logs show database lock

**Solution**:
```bash
# Restart backend service
pkill -f "uvicorn.*9001"
cd /data/projects/autocraft/backend
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

---

## Appendix

### A. API Quick Reference

| Function | Method | Path |
|----------|--------|------|
| List Projects | GET | `/profiles` |
| Create Project | POST | `/profiles` |
| Get Project | GET | `/profiles/{id}` |
| Update Project | PUT | `/profiles/{id}` |
| Delete Project | DELETE | `/profiles/{id}` |
| List Phases | GET | `/profiles/{id}/phases` |
| Create Phase | POST | `/profiles/{id}/phases` |
| Update Phase | PUT | `/phases/{id}` |
| Delete Phase | DELETE | `/phases/{id}` |
| List Plans | GET | `/plans` |
| Create Plan | POST | `/plans` |
| Get Plan | GET | `/plans/{id}` |
| Update Plan | PUT | `/plans/{id}` |
| Delete Plan | DELETE | `/plans/{id}` |
| List Tasks | GET | `/tasks` |
| Get Task | GET | `/tasks/{no}` |
| Update Task | PUT | `/tasks/{no}` |
| Execute Task | POST | `/api/v2/tasks/execute` |
| Execution Status | GET | `/api/v2/tasks/{id}/status` |

### B. Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |

---

**Maintained by**: AutoCraft Team  
**Last Updated**: 2026-05-19