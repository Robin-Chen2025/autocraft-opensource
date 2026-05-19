---
name: project-init
description: AutoCraft project initialization workflow. Four-level structure creation: Project → Phase → Plan → Task. Trigger scenarios: (1) New project startup (2) Project phase division (3) Development plan import
---

# AutoCraft Project Initialization Workflow

**Version:** v1.0  
**Updated:** 2026-05-19

---

## Four-Level Management Structure

```
Project
  └── Phase
        └── Plan
              └── Task
```

| Level | Identifier Field | Description |
|-------|------------------|-------------|
| Project | `profile_id` | Project profile, defines basic info |
| Phase | `phase_record_id` | Development phase division (e.g., M-01, M-02) |
| Plan | `plan_id` | Collection of related tasks |
| Task | `task_no` | Minimum execution unit |

---

## Your Role

**You are the Project Manager** — make decisions, break down tasks, verify deliverables. Don't write code.

| You Do | You Don't |
|--------|-----------|
| Create projects, divide phases | Directly operate database |
| Import development plans | Skip verification steps |
| Verify deliverables | Trust sub-agent's "completed" |

---

## Phase Zero: Project Initialization

### Creation Flow

```
1. Create project profile (POST /profiles)
2. Create phase (POST /profiles/{profile_id}/phases)
3. Create plan (POST /plans)
4. Import tasks (POST /tasks or batch import)
```

---

## 1. Create Project Profile

### API

**POST /profiles**

### Request Body

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

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `profile_type` | ✅ | `template`=template, `instance`=instance |
| `profile_name` | ✅ | Project name |
| `project_type` | ❌ | Project type (Web App, CLI Tool, etc.) |
| `description` | ❌ | Project description |
| `tech_stack` | ❌ | Technology stack |
| `root_path` | ❌ | Project root path |
| `profile_id` | ❌ | Custom ID, auto-generated if not provided |
| `template_profile_id` | ❌ | Used when copying from template |

### Response

```json
{
  "message": "Project profile created successfully",
  "profile_id": "deeptutor-lite"
}
```

### Naming Conventions

- **profile_id**: lowercase letters + hyphens, e.g., `deeptutor-lite`, `autocraft`
- **profile_name**: Full name, e.g., "DeepTutor-Lite AI Learning System"

### Decision Points

**Confirm before project creation:**

1. Is the project name clear?
2. Is the tech stack determined?
3. Does the project root path exist?
4. Do you need to copy from a template?

---

## 2. Create Phase

### API

**POST /profiles/{profile_id}/phases**

### Request Body

```json
{
  "phase_id": "m01-be",
  "phase_name": "M-01 Backend Development",
  "phase_order": 1,
  "status": "pending"
}
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `phase_id` | ✅ | Phase identifier (e.g., m01-be) |
| `phase_name` | ✅ | Phase name (e.g., M-01 Backend Development) |
| `phase_order` | ✅ | Phase order (starting from 0) |
| `status` | ❌ | Status: pending/in_progress/completed |

### Response

```json
{
  "message": "Phase created successfully",
  "phase_record_id": "deeptuto-m01-be-phase"
}
```

### Naming Conventions

- **phase_id**: lowercase letters + hyphens, e.g., `infra`, `m01-be`, `m02-fe`
- **phase_record_id**: Auto-generated, format `{profile_id-prefix}-{phase_id}-phase`
- **phase_name**: Numbered name, e.g., "M-01 Backend Development"

### Phase Division Recommendations

| Order | Phase | Description |
|-------|-------|-------------|
| 0 | INFRA | Infrastructure (database, config) |
| 1 | M-01 | First development iteration |
| 2 | M-02 | Second development iteration |
| ... | ... | ... |

---

## 3. Create Plan

### API

**POST /plans**

### Request Body

```json
{
  "profile_id": "deeptutor-lite",
  "phase_record_id": "deeptuto-m01-be-phase",
  "plan_name": "WP-M01-BE-001: User Authentication Module",
  "description": "Implement user login, registration, permission verification",
  "status": "pending"
}
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `profile_id` | ✅ | Parent project ID |
| `phase_record_id` | ❌ | Parent phase ID |
| `plan_name` | ✅ | Plan name |
| `description` | ❌ | Plan description |
| `status` | ❌ | Status: pending/in_progress/completed |

### Response

```json
{
  "message": "Plan created successfully",
  "plan_id": "plan_b4ffaa5474b44734"
}
```

### Naming Conventions

- **plan_id**: Auto-generated, format `plan_{uuid-first-16-chars}`
- **plan_name**: Format `WP-{phase}-{seq}: {feature-name}`

### Plan Creation Timing

- After design phase completion
- After development plan overview finalized
- Each plan corresponds to a group of related tasks

---

## 4. Import Tasks

### Single Creation

**POST /tasks**

```json
{
  "task_no": "DTL-M01-BE-001-001",
  "task_name": "Implement user login API",
  "task_type": "BUILD-CODE",
  "plan_id": "plan_b4ffaa5474b44734",
  "phase_record_id": "deeptuto-m01-be-phase",
  "status": "pending",
  "priority": "high",
  "executor": "ac-executor",
  "expected_result": "Generate auth.py with login API",
  "input_data": "{\"requirements\": \"Implement JWT login\", \"expected_output_files\": [\"src/api/auth.py\"]}"
}
```

### Batch Import

Use `scripts/import_tasks.py` script:

```bash
python scripts/import_tasks.py \
  --plan-id plan_b4ffaa5474b44734 \
  --phase-record-id deeptuto-m01-be-phase \
  --input /path/to/tasks.json
```

### Task Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `task_no` | ❌ | Task number (auto-generated if not provided) |
| `task_name` | ✅ | Task name |
| `task_type` | ❌ | Task type (BUILD-CODE, etc.) |
| `plan_id` | ❌ | Parent plan |
| `phase_record_id` | ❌ | Parent phase |
| `status` | ❌ | Status (default: pending) |
| `priority` | ❌ | Priority (high/medium/low) |
| `executor` | ❌ | Executor (ac-executor) |
| `expected_result` | ❌ | Expected result |
| `input_data` | ❌ | Input data (JSON string) |

### Naming Conventions

- **task_no**: Format `{project-prefix}-{phase}-{seq}-{sub-seq}`
  - e.g., `DTL-M01-BE-001-001`
  - `DTL` = Project prefix (DeepTutor-Lite)
  - `M01-BE` = Phase identifier
  - `001` = Plan sequence
  - `001` = Task sequence

---

## Complete Example: Create New Project

### Scenario

Create a new project named "MyProject" with two phases.

### Steps

```
# 1. Create project
POST /profiles
{
  "profile_type": "instance",
  "profile_name": "MyProject Example Project",
  "project_type": "Web Application",
  "tech_stack": "Vue3 + FastAPI"
}
# Response: profile_id = "myproject"

# 2. Create phase INFRA
POST /profiles/myproject/phases
{
  "phase_id": "infra",
  "phase_name": "INFRA Infrastructure",
  "phase_order": 0
}
# Response: phase_record_id = "myproj-infra-phase"

# 3. Create phase M-01
POST /profiles/myproject/phases
{
  "phase_id": "m01",
  "phase_name": "M-01 Core Features",
  "phase_order": 1
}
# Response: phase_record_id = "myproj-m01-phase"

# 4. Create plan
POST /plans
{
  "profile_id": "myproject",
  "phase_record_id": "myproj-infra-phase",
  "plan_name": "WP-INFRA-001: Project Initialization"
}
# Response: plan_id = "plan_xxx"

# 5. Import tasks (batch)
python scripts/import_tasks.py --plan-id plan_xxx ...
```

---

## Query APIs

### List Projects

```
GET /profiles?page=1&page_size=10
```

### Get Project Details

```
GET /profiles/{profile_id}
```

### List Phases

```
GET /profiles/{profile_id}/phases
```

### List Plans

```
GET /plans?profile_id={profile_id}
GET /plans?phase_record_id={phase_record_id}
```

### Get Plan Details

```
GET /plans/{plan_id}
```

### List Tasks

```
GET /tasks?plan_id={plan_id}
GET /tasks?status=pending
```

---

## Status Flow

### Phase Status

```
pending → in_progress → completed
```

### Plan Status

```
pending → in_progress → completed
```

### Task Status

```
pending → locked → executing → completed
                    ↓
                  failed
```

---

## Important Notes

1. **Create project first, then phases**
2. **Create phases first, then plans**
3. **Plans can exist without phases** (backward compatibility)
4. **Tasks can exist without plans** (backward compatibility)
5. **Deleting a project cascades to delete phases, plans, and tasks**

---

## Relationship with Design Phase

```
Phase Zero: Project Initialization
    ↓
Phase One: Design Phase
    PRD → Feature Design → Tech Solution → API/DB Design
    → Development Plan Overview + Work Plan Lists
    ↓
Phase Two: Execution Phase
    Import Plans → Import Tasks → Execution Engine → Verification
```

**Project Initialization Timing:**
- Before design phase starts (create project profile)
- After development plan finalized (create phases and plans)
- After task breakdown completed (import tasks)

---

_Last Updated: 2026-05-19_