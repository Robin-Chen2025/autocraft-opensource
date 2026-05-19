---
name: autocraft-dev
description: AutoCraft-assisted software development workflow. Two-phase mode: (1) Design Phase - Generate PRD/System Feature Design/API Design/Database Design/Development Plan documents per design specs, sub-agent generation + review loop; (2) Execution Phase - Import development plan to AutoCraft, call execution engine to execute AI sub-agents task by task + auto verification. Trigger scenarios: (1) New feature development (2) Project initialization (3) Design document generation and review (4) Task breakdown and execution (5) AI generation and verification of code/documents
---

# AutoCraft Assisted Software Development

**Version:** v1.1  
**Updated:** 2026-05-08  
**Changes:** Added architecture check dimension, standardized template library, architecture rationality verification

---

## Two-Phase Model

```
Phase One: Design Phase (Not using AutoCraft)
    │
    │  PRD → Feature Design → Tech Solution → API/DB/UI Design
    │  → Test Plan → Development Plan (Overview + Work Plan Lists)
    │  → Integrity Verification
    │
    ▼  Development Plan Finalized
Phase Two: Execution Phase (Enter AutoCraft)
    │
    │  Break down tasks one by one → API import to AutoCraft
    │  → Execution engine executes task by task (AI sub-agents)
    │  → Auto verification → Main agent acceptance → Status cascade
    │
    ▼  Project Complete
```

---

## Your Role

**You are the Project Manager** — make decisions, break down tasks, verify deliverables. Don't write code.

| You Do | You Don't |
|--------|-----------|
| Clarify requirements, choose solutions | Write specific code |
| Review and approve documents | Directly operate database |
| Task breakdown and scheduling | Trust sub-agent's "completed" |
| Accept deliverables | Skip verification steps |

---

## Phase One: Design Phase

### Design Document System

Execute per `references/design-specs/设计阶段文档规范-总纲.md`.

**Required Documents**:

| No. | Document | Code | Detailed Spec | Review Checklist |
|-----|----------|------|---------------|------------------|
| 01 | PRD | PRD | [01-PRD-Spec](references/design-specs/doc-specs/01-PRD规范.md) | [09-PRD-Review](references/design-specs/doc-specs/09-PRD审核Checklist.md) |
| 03 | System Feature Design | FUNC | [03-Feature-Design](references/design-specs/doc-specs/03-系统功能设计文档规范.md) | [11-Feature-Review](references/design-specs/doc-specs/11-系统功能设计审核Checklist.md) |
| 04 | Tech Solution | TECH | [04-Tech-Solution](references/design-specs/doc-specs/04-技术方案文档规范.md) | [12-Tech-Review](references/design-specs/doc-specs/12-技术方案审核Checklist.md) |
| 07 | API Design | API | [07-API-Design](references/design-specs/doc-specs/07-API设计文档规范.md) | [14-API-Review](references/design-specs/doc-specs/14-API设计审核Checklist.md) |
| 08 | Database Design | DB | [08-DB-Design](references/design-specs/doc-specs/08-数据库设计文档规范.md) | [15-DB-Review](references/design-specs/doc-specs/15-数据库设计审核Checklist.md) |
| 18 | Integrity Verification | VERIFY | - | [18-Integrity-Verify](references/design-specs/doc-specs/18-设计阶段整体性验证Checklist.md) |

**On-Demand Documents**:

| No. | Document | Code | Detailed Spec | Review Checklist |
|-----|----------|------|---------------|------------------|
| 00 | Requirements List | REQ | [00-Requirements](references/design-specs/doc-specs/00-需求清单规范.md) | See Spec Chapter 6 |
| 02 | Business Flow | FLOW | [02-Business-Flow](references/design-specs/doc-specs/02-业务流程文档规范.md) | [10-Flow-Review](references/design-specs/doc-specs/10-业务流程审核Checklist.md) |
| 05 | UI Design | UI | [05-UI-Design](references/design-specs/doc-specs/05-UI设计文档规范.md) | [13-UI-Review](references/design-specs/doc-specs/13-UI设计审核Checklist.md) |
| 06 | Component Spec | COMP | [06-Component-Spec](references/design-specs/doc-specs/06-组件规范文档规范.md) | [16-Component-Review](references/design-specs/doc-specs/16-组件规范审核Checklist.md) |

### Document Output Order

```
PRD → Business Flow (on-demand) → System Feature Design → Tech Solution
    → Vue Skeleton Prototype (user confirm) → UI Design + API Design + Component Spec + DB Design
    → Integrity Verification
```

**Dependencies**: Each document depends on prerequisite documents' feature ID trace chain (FR-001 → F-001 → API → DB).

### Document Generation Flow

Use **sub-agents** to generate documents (replacing Crush):

```
1. Prepare input materials (prerequisite docs + spec files)
2. Sub-agent generates first version document
3. Sub-agent reviews per Review Checklist
4. Fix based on issue list
5. Re-review to confirm
6. Finalize (user review)
```

**Sub-agent Call Method**:

**Design Phase Uses Multi-turn Session Mode**:
```bash
# Create persistent session (supports multi-turn review-fix loop)
openclaw agent --session-id explicit:doc_session_{project_name}_{timestamp} \
  --agent-id ac-glm5 \
  --model glm-5 \
  --message "Read the following spec files and input materials, generate {document_type} document..."

# Review in same session
openclaw agent --session-id explicit:doc_session_{project_name}_{timestamp} \
  --message "Review the generated document per Review Checklist..."

# Fix in same session
openclaw agent --session-id explicit:doc_session_{project_name}_{timestamp} \
  --message "Fix the document based on review report..."
```

**Key Requirements**:
- Design phase document generation uses **multi-turn session mode**, supporting same sub-agent for generate→review→fix loop
- Sub-agent must read corresponding **spec file** and **Review Checklist** before generating
- Immediately self-review with Checklist after generation
- Score ≥80 before submitting for user review, <70 regenerate
- Use **GLM-5 model** for design phase document work

### Test Plan

Generate per `references/design-specs/质量检测方案/`:

| Document | Path | Purpose |
|----------|------|---------|
| Test Plan Overview | [21-Overview-Spec](references/design-specs/质量检测方案/21-测试方案总纲生成规范.md) | Project overall test strategy |
| BE-L2 Test Plan | [22-BE-L2-Spec](references/design-specs/质量检测方案/22-BE-L2测试方案规范.md) | Backend integration test |
| FE-L2 Test Plan | [23-FE-L2-Spec](references/design-specs/质量检测方案/23-FE-L2测试方案规范.md) | Frontend integration test |
| L3-E2E Test Plan | [24-L3-E2E-Spec](references/design-specs/质量检测方案/24-L3-E2E测试方案规范.md) | End-to-end test |
| L1 Test Plan | [30/31-Spec](references/design-specs/质量检测方案/30-L1-BE测试方案规范.md) | Unit test |

### Development Plan

Generate per `references/design-specs/开发计划方案/`:

**Two-Layer Structure**:
- **Development Plan Overview**: Batch order, module dependencies, feature overview
- **Work Plan List**: Task structure summary for each work plan

| Document | Spec | Review |
|----------|------|--------|
| Overview | [40-Gen-Spec](references/design-specs/开发计划方案/40-开发计划生成规范.md) | [43-Overview-Review](references/design-specs/开发计划方案/43-开发计划总览审核Checklist.md) |
| Overview Detail | [41-Overview-Gen](references/design-specs/开发计划方案/41-开发计划总览生成规范.md) | - |
| List | [42-List-Gen](references/design-specs/开发计划方案/42-工作计划清单生成规范.md) | [44-List-Review](references/design-specs/开发计划方案/44-工作计划清单审核Checklist.md) |
| Integrity | - | [45-Integrity-Review](references/design-specs/开发计划方案/45-开发计划整体性审核Checklist.md) |

**Key Principles**:
- Work plan count determined by specific project, not hardcoded
- Numbering constraints defined in lists, FlowTicket execution must follow
- Task detail JSON generated dynamically at FlowTicket startup, not pre-generated

---

## Phase Two: Execution Phase

### Import to AutoCraft

After development plan finalized, main agent breaks down tasks one by one, import via API:

```bash
# 1. Create project profile
curl -X POST http://localhost:9001/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"profile_id":"...", "profile_name":"...", ...}'

# 2. Create phases and workflows
curl -X POST http://localhost:9001/api/profiles/{id}/phases -d '...'
curl -X POST http://localhost:9001/api/profiles/{id}/workflows -d '...'

# 3. Create work plans
curl -X POST http://localhost:9001/plans -d '...'

# 4. Create tasks one by one
curl -X POST http://localhost:9001/tasks -d '...'
```

### Task Creation

⚠️ **Execute per `references/task-creator/SKILL.md`**, including complete:
- input_data standard format and required fields
- workflow_type and task_type mapping table
- input_files configuration guide
- Batch creation example code
- Common errors and checklist

**Core Rules**:
1. All paths must be **absolute paths**
2. `project_path` must point to correct project root directory
3. `input_files` must contain at least 1 design document
4. `requirements` must be detailed and specific
5. `expected_output_files` must list all expected files
6. `input_data` must be converted to JSON string via `json.dumps()`

### Simple FlowTicket Execute Task

**Call Method**:

```bash
# 1. Submit execution request (async)
curl -X POST http://localhost:9001/api/v2/tasks/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": <task_id>,
    "model": "glm-5.1",
    "label": "Execute task XXX",
    "timeout": 1800
  }'

# 2. Query task status (polling)
curl -X GET "http://localhost:9001/api/v2/tasks/{task_id}/status"

# 3. Check execution result
# - Status "completed" or "verified" means success
# - Status "failed" or "verification_failed" means failure
# - execution_log and verification_log contain details
```

**Task Status Flow**:
```
pending → in_progress → completed → verifying → verified
                     ↓
                   failed → (can re-execute)
                                  ↓
                          verification_failed
```

**Task Data Format Requirements**:

⚠️ **input_data field must be complete**, ensuring sub-agent can correctly execute task:

```json
{
  "input_files": [
    "/data/projects/{project}/docs/design/07-API-Design-{project}.md",
    "/data/projects/{project}/docs/design/03-System-Feature-Design-{project}.md"
  ],
  "requirements": "Detailed task requirement description...",
  "expected_output": "Detailed expected output description...",
  "expected_output_files": [
    "/data/projects/{project}/backend/services/xxx.py",
    "/data/projects/{project}/backend/schemas/xxx.py"
  ],
  "workflow_type": "BUILD",
  "project_path": "/data/projects/{project}",
  "deliverables": ["..."],
  "source_file": "..."
}
```

**Key Requirements**:
- ✅ **input_files must be absolute paths** (do not use relative paths)
- ✅ **requirements must describe task requirements in detail** (cannot be "no specific requirements")
- ✅ **expected_output must describe expected output in detail** (cannot be "generate corresponding deliverables per task description")
- ✅ **expected_output_files must list expected output file paths** (absolute paths)
- ✅ **workflow_type must be correct** (BUILD/DOC/TEST etc.)

**⚠️ Path Configuration Lesson**:
- ❌ **Wrong Example**: `backend/api/routers/knowledge_graph.py` (relative path)
- ✅ **Correct Example**: `/data/projects/deeptutor-lite/backend/api/routers/knowledge_graph.py` (absolute path)
- ❌ **Problem**: Relative paths cause files to be generated in wrong directory (e.g., autocraft project)
- ✅ **Solution**: All paths must start from project root `/data/projects/{project}/`

**Execution Mechanism**:

1. **Async Execution**: Submit execution request returns immediately, doesn't wait for completion
2. **Status Polling**: Check task progress via status query endpoint
3. **Auto Verification**: Verification sub-agent automatically starts after execution completes
4. **Result Notification**: Can receive notification via callback_target after verification completes

**Execution Loop**:
```
Read task → Render template → Call execution sub-agent (GLM-5)
→ Deliverables written to project directory (per expected_output_files specified paths)
→ JSON result written to /tmp/autocraft_output/{task_id}_execution_result.json
→ Engine reads JSON → Updates status → Auto starts verification sub-agent (DeepSeek-V3.2)
→ Verification result written to /tmp/autocraft_output/{task_id}_verification_result.json
→ Engine reads JSON → Updates final status (verified/verification_failed)
```

**Model Configuration**:

| Purpose | Model | Agent ID |
|---------|-------|----------|
| Execution | GLM-5.1 | ac-glm5 |
| Verification | DeepSeek-V3.2-thinking | ac-validator |

**Important Notes**:

1. **Don't Monitor Execution Process**: After submitting task, Simple FlowTicket will automatically execute and verify, notify when complete or failed
2. **Verification Mechanism Effective**: Can identify execution sub-agent's false reports (e.g., claiming file created but actually not)
3. **Deliverable Verification**: Verification sub-agent checks if files actually exist, if code matches design documents
4. **Architecture Check**: Verification includes 6 dimensions, "Architecture Rationality" checks if code follows Single Responsibility Principle
5. **Path Configuration Verification**: Verification sub-agent checks if deliverables are in correct directory, avoiding generation to wrong project

### Acceptance Rules

1. **Don't trust sub-agent's "completed"** — must check deliverable files
2. **Verification executed automatically by engine** — PASS/FAIL determined item by item, all dimensions PASS to pass
3. **Deliverable paths must be checked** — verify files are in deliverables specified locations
4. **Architecture rationality mandatory check** — added 6th dimension "Architecture Rationality", SRP violation directly FAIL
5. **Design conformance mandatory check** — added 7th dimension "Design Conformance", check if implementation matches design documents

### Verification Dimensions (7)

| Dimension | Check Content | FAIL Condition |
|-----------|---------------|----------------|
| 1. Completeness | Do deliverable files exist | Files don't exist |
| 2. Correctness | Is code syntax correct | Compile/parse failure |
| 3. Functionality | Does it implement requirements | Core features missing |
| 4. Standards | Does it follow code conventions | Severe convention violations |
| 5. Testability | Can tests run | Tests cannot execute |
| 6. Architecture Rationality | Does it follow Single Responsibility Principle | SRP violation |
| **7. Design Conformance** | **Does it match design document definitions** | **Deviates from design documents** |

### Design Conformance Check Details

**Check Timing**: All BUILD-CODE and BUILD-TEST tasks

**Check Content**:

1. **Frontend Tasks**:
   - API call paths match API design documents
   - Communication method matches design documents (HTTP API vs WebSocket)
   - Component Props/Events match component specifications

2. **Backend Tasks**:
   - API endpoint paths match API design documents
   - Request/Response formats match API design documents
   - Database tables/fields match database design documents

3. **Test Tasks**:
   - Test scenarios cover test plan defined use cases
   - Assertions match test plan acceptance criteria

**FAIL Determination**:
- Frontend uses communication method not defined in design documents (e.g., WebSocket direct to Gateway)
- API paths don't match design documents
- Database table structure doesn't match design documents
- Component interfaces don't match component specifications

**Lesson Source**: LRN-20260514-005
- **Problem**: M01-FE-DEV task requirements explicitly required "call POST /api/chat/messages", input_files included API-Design.md, but sub-agent chose WebSocket direct to Gateway solution, causing all tests to fail
- **Root Cause**: Verification only checked "is feature implemented", didn't check "does it match design documents"
- **Fix**: Added "Design Conformance" verification dimension, mandatory check of implementation consistency with design documents

### Status Cascade

Task completion triggers cascade update:

```bash
POST /status/cascade/{task_no}
```

Task → Work Plan → Workflow → Phase → Project

---

## AutoCraft System Info

| Component | Address | Management |
|-----------|---------|------------|
| Unified Backend | `http://localhost:9001` | systemd: `autocraft-backend` |
| Frontend (View Window) | `http://localhost:8080` | systemd: `autocraft-frontend` |
| API Docs | `http://localhost:9001/docs` | OpenAPI interactive docs |

**Service Management**:
```bash
sudo systemctl restart autocraft-backend autocraft-frontend
sudo systemctl status autocraft-backend autocraft-frontend
curl http://localhost:9001/health  # Health check
```

---

## Rules

| Rule | Description |
|------|-------------|
| **Must confirm with user before action** | Each key step (start project, generate docs, execute tasks, acceptance etc.) must explain plan to user and wait for confirmation, cannot execute without confirmation |
| **Design phase multi-turn session** | Design phase document generation uses multi-turn session mode, same sub-agent (GLM-5) completes generate→review→fix loop |
| Main agent doesn't write code | You are project manager, sub-agents do the work |
| All operations via API | No direct database operations |
| Verify deliverables | Don't trust "completed" word |
| Git standards | No `reset --hard`, `push --force` |
| Model isolation | **Design Phase: GLM-5**, Execution Phase: GLM-5 (execution) + DeepSeek-V3.2 (verification) |
| Session isolation | Execution phase each task independent session, design phase multi-turn session |
| Design specs priority | Document generation must read spec files, don't write from memory |
| **Paths must be absolute** | All file paths must be absolute paths, no relative paths |
| **Project directory explicit** | Must specify correct project_path, ensure files generated to correct location |

---

## Sub-Agent Guide

Comprehensive guide for ac-glm5 (execution sub-agent) and ac-validator (verification sub-agent):

- **ac-agent-guide**: `references/ac-agent-guide/SKILL.md`
  - Role identification (auto-detect execution/verification role by Agent ID)
  - Execution sub-agent: 5 task types (BUILD-CODE/BUILD-TEST/BUILD-ENV/DOC/DESIGN)
  - Verification sub-agent: 3 task types + PASS/FAIL determination + verification dimensions
  - Auxiliary skill index: Auto-select corresponding skill by tech stack
  - JSON result file format specification
  - Shared rules (file operations, deliverable directory, common commands)

> When sub-agent is called by AutoCraft execution engine, should read this skill to get role definition and behavior specification.

---

## Architecture Check and Template Library

### Architecture Check Tool

Added 6th verification dimension: **Architecture Rationality**, checks if code follows design principles:

| Dimension | Check Item | Criteria |
|-----------|------------|----------|
| Architecture Rationality | Is file responsibility single (SRP), is code structure clear, are functional boundaries distinct | SRP violation → FAIL |

**Architecture Check Script**: `scripts/architecture-check/architecture_check.py`
- Check file responsibility singularity (SRP principle)
- Check code structure rationality (layered architecture)
- Check functional boundary distinctness (coupling degree)
- Generate architecture health report

**Usage**:
```bash
python3 scripts/architecture-check/architecture_check.py --path /path/to/code --report architecture_report.json
```

### Standardized Template Library

Provides standard code templates, ensures architecture consistency:

| Template | Path | Purpose |
|----------|------|---------|
| FastAPI Router Template | `templates/fastapi-module/router_template.py` | Router layer code template |
| Service Layer Template | `templates/fastapi-module/service_template.py` | Business logic layer template |
| Test Template | `templates/fastapi-module/test_template.py` | Test code template |
| pytest Config | `templates/config-templates/pytest.ini` | Test config template |
| Architecture Rules | `templates/architecture-rules/architecture_rules.md` | Architecture spec document |

### Verification Sub-agent Integration

Verification sub-agent (ac-validator) now needs to check 6 dimensions:
1. ✅ Completeness
2. ✅ Correctness
3. ✅ Runnability
4. ✅ Consistency
5. ✅ Security
6. ✅ **Architecture Rationality** (new)

**Architecture Rationality Checklist**:
- File responsibility singularity (SRP principle)
- Code structure rationality (layered architecture)
- Functional boundary distinctness (coupling control)
- Code complexity control (file size/function complexity)

### Verification Result JSON Format Updated

```json
{
  "verification_success": true,
  "verification_report": "Full verification report",
  "dimension_results": {
    "Completeness": "PASS",
    "Correctness": "PASS",
    "Runnability": "PASS",
    "Consistency": "PASS",
    "Security": "PASS",
    "Architecture Rationality": "PASS"  // New dimension
  },
  "issues_found": [],
  "improvements_suggested": []
}
```

## Reference Document Index

| Category | Directory | File Count |
|----------|-----------|------------|
| Design Specs - Doc Specs | `references/design-specs/doc-specs/` | 20 |
| Design Specs - Dev Plan | `references/design-specs/开发计划方案/` | 9 |
| Design Specs - Quality Test | `references/design-specs/质量检测方案/` | 28 |
| Design Specs - Overview | `references/design-specs/设计阶段文档规范-总纲.md` | 1 |
| Sub-agent Guide | `references/ac-agent-guide/SKILL.md` | 1 |
| **Task Creation** | `references/task-creator/SKILL.md` | 1 |
| Architecture Check Tool | `scripts/architecture-check/` | 3 |
| Standardized Template Library | `templates/` | 5 |