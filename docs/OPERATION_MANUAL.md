# AutoCraft 系统操作手册

**版本**: 1.0  
**更新日期**: 2026-05-19  
**适用对象**: OpenClaw 主代理（皮皮虾 🦐）

---

## 目录

1. [系统概述](#1-系统概述)
2. [四级管理结构](#2-四级管理结构)
3. [项目管理](#3-项目管理)
4. [阶段管理](#4-阶段管理)
5. [计划单管理](#5-计划单管理)
6. [任务单管理](#6-任务单管理)
7. [任务执行引擎](#7-任务执行引擎)
8. [常见操作流程](#8-常见操作流程)
9. [故障排查](#9-故障排查)

---

## 1. 系统概述

### 1.1 系统定位

AutoCraft 是一个 AI 驱动的任务管理与执行平台，核心能力：

- **四级管理**: 项目 → 阶段 → 计划 → 任务
- **AI 执行**: 通过 OpenClaw 子代理自动执行任务
- **自动验证**: 执行完成后自动触发验证流程

### 1.2 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw 主代理                        │
│                      (皮皮虾 🦐)                          │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │              AutoCraft 前端 (Vue3)               │    │
│  │              http://localhost:8080               │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │                                │
│  ┌──────────────────────▼──────────────────────────┐    │
│  │              AutoCraft 后端 (FastAPI)            │    │
│  │              http://localhost:9001               │    │
│  │  ┌─────────────────────────────────────────┐    │    │
│  │  │  四级管理: 项目/阶段/计划/任务            │    │    │
│  │  ├─────────────────────────────────────────┤    │    │
│  │  │  执行引擎: 任务执行 + 自动验证           │    │    │
│  │  └─────────────────────────────────────────┘    │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │                                │
│  ┌──────────────────────▼──────────────────────────┐    │
│  │           OpenClaw 子代理集群                     │    │
│  │  ac-executor │ ac-validator │ ac-builder         │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 1.3 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| 后端 API | 9001 | FastAPI 服务 |
| 前端界面 | 8080 | Vue3 开发服务器 |
| API 文档 | 9001/docs | Swagger UI |

---

## 2. 四级管理结构

### 2.1 层级关系

```
项目 (Project)
  └── 阶段 (Phase)
        └── 计划单 (Plan)
              └── 任务单 (Task)
```

### 2.2 各层级职责

| 层级 | 标识 | 职责 | 示例 |
|------|------|------|------|
| **项目** | `profile_id` | 项目总览，定义项目基本信息 | DeepTutor-Lite |
| **阶段** | `phase_record_id` | 开发阶段划分 | M-01 后端开发 |
| **计划单** | `plan_id` | 一组相关任务的集合 | WP-M01-BE-001 |
| **任务单** | `task_no` | 最小执行单元 | DTL-INFRA-001-001 |

### 2.3 命名规范

**项目 ID**: `{项目名简称}`
```
deeptutor-lite
autocraft
```

**阶段 ID**: `{项目ID}-{阶段简称}-phase`
```
deeptuto-infra-phase      # 基础建设阶段
deeptuto-m01-be-phase     # M-01 后端阶段
```

**计划单 ID**: `plan_{uuid前16位}`
```
plan_5e9039a1665c47ab
plan_b4ffaa5474b44734
```

**任务单号**: `{项目前缀}-{阶段}-{序号}-{子序号}`
```
DTL-INFRA-001-001
DTL-M01-BE-002-003
```

---

## 3. 项目管理

### 3.1 创建项目

**API**: `POST /profiles`

**请求体**:
```json
{
  "profile_type": "instance",
  "profile_name": "DeepTutor-Lite AI辅助学习系统",
  "project_type": "Web应用",
  "description": "基于AI的智能学习辅助系统",
  "tech_stack": "Vue3 + FastAPI + SQLite",
  "root_path": "/data/projects/deeptutor-lite"
}
```

**响应**:
```json
{
  "message": "项目档案创建成功",
  "profile_id": "deeptutor-lite"
}
```

### 3.2 查询项目列表

**API**: `GET /profiles?page=1&page_size=10`

**响应**:
```json
{
  "total": 5,
  "items": [
    {
      "profile_id": "deeptutor-lite",
      "profile_name": "DeepTutor-Lite AI辅助学习系统",
      "status": "active",
      ...
    }
  ],
  "page": 1,
  "page_size": 10
}
```

### 3.3 查询项目详情

**API**: `GET /profiles/{profile_id}`

**示例**: `GET /profiles/deeptutor-lite`

### 3.4 更新项目

**API**: `PUT /profiles/{profile_id}`

**请求体**:
```json
{
  "profile_name": "新项目名称",
  "status": "active"
}
```

### 3.5 删除项目

**API**: `DELETE /profiles/{profile_id}`

**⚠️ 注意**: 删除项目会级联删除其下所有阶段、计划和任务。

---

## 4. 阶段管理

### 4.1 创建阶段

**API**: `POST /profiles/{profile_id}/phases`

**请求体**:
```json
{
  "phase_id": "m01-be",
  "phase_name": "M-01 后端开发",
  "phase_order": 1,
  "status": "pending"
}
```

**响应**:
```json
{
  "message": "阶段创建成功",
  "phase_record_id": "deeptuto-m01-be-phase"
}
```

### 4.2 查询阶段列表

**API**: `GET /profiles/{profile_id}/phases`

**响应**:
```json
[
  {
    "phase_record_id": "deeptuto-infra-phase",
    "phase_id": "infra",
    "phase_name": "INFRA 基础建设",
    "phase_order": 0,
    "status": "completed"
  },
  {
    "phase_record_id": "deeptuto-m01-be-phase",
    "phase_id": "m01-be",
    "phase_name": "M-01 后端开发",
    "phase_order": 1,
    "status": "in_progress"
  }
]
```

### 4.3 更新阶段

**API**: `PUT /phases/{phase_record_id}`

**请求体**:
```json
{
  "phase_name": "M-01 后端开发（进行中）",
  "status": "in_progress"
}
```

### 4.4 删除阶段

**API**: `DELETE /phases/{phase_record_id}`

---

## 5. 计划单管理

### 5.1 创建计划单

**API**: `POST /plans`

**请求体**:
```json
{
  "profile_id": "deeptutor-lite",
  "phase_record_id": "deeptuto-m01-be-phase",
  "plan_name": "WP-M01-BE-001: 用户认证模块",
  "description": "实现用户登录、注册、权限验证功能",
  "status": "pending"
}
```

**响应**:
```json
{
  "message": "计划单创建成功",
  "plan_id": "plan_b4ffaa5474b44734"
}
```

### 5.2 查询计划单列表

**API**: `GET /plans`

**参数**:
- `profile_id`: 按项目筛选
- `phase_record_id`: 按阶段筛选
- `status`: 按状态筛选

### 5.3 查询计划单详情

**API**: `GET /plans/{plan_id}`

**响应**: 包含计划信息及关联的项目、阶段信息

### 5.4 查询计划单下的任务

**API**: `GET /plans/{plan_id}/tasks`

### 5.5 更新计划单

**API**: `PUT /plans/{plan_id}`

**请求体**:
```json
{
  "plan_name": "更新后的计划名称",
  "status": "in_progress"
}
```

### 5.6 删除计划单

**API**: `DELETE /plans/{plan_id}`

---

## 6. 任务单管理

### 6.1 任务单结构

**任务单包含 33 个字段**，核心字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_no` | string | 任务单号（唯一标识） |
| `task_name` | string | 任务名称 |
| `task_type` | string | 任务类型 |
| `status` | string | 状态：pending/locked/executing/completed/failed |
| `priority` | string | 优先级：high/medium/low |
| `plan_id` | string | 所属计划单 |
| `phase_record_id` | string | 所属阶段 |
| `executor` | string | 执行者 |
| `verifier` | string | 验证者 |
| `input_data` | json | 输入数据 |
| `execution_log` | json | 执行日志 |
| `verification_result` | string | 验证结果 |

### 6.2 查询任务单列表

**API**: `GET /tasks`

**参数**:
- `page`: 页码
- `page_size`: 每页数量
- `status`: 状态筛选
- `plan_id`: 按计划单筛选
- `keyword`: 关键词搜索

**响应**:
```json
{
  "total": 659,
  "items": [...],
  "page": 1,
  "page_size": 20
}
```

### 6.3 查询任务单详情

**API**: `GET /tasks/{task_no}`

**响应**: 包含任务单所有 33 个字段

### 6.4 更新任务单

**API**: `PUT /tasks/{task_no}`

**请求体**:
```json
{
  "status": "pending",
  "priority": "high",
  "executor": "ac-executor"
}
```

### 6.5 任务状态流转

```
pending → locked → executing → completed
                    ↓
                  failed
```

| 状态 | 说明 |
|------|------|
| `pending` | 待执行 |
| `locked` | 已锁定，等待执行 |
| `executing` | 执行中 |
| `completed` | 执行完成 |
| `failed` | 执行失败 |

---

## 7. 任务执行引擎

### 7.1 执行流程

```
┌─────────────┐
│  1. 锁定任务  │  防止并发冲突
└──────┬──────┘
       ↓
┌─────────────┐
│  2. 读取任务  │  解析 input_data
└──────┬──────┘
       ↓
┌─────────────┐
│  3. 渲染模板  │  生成执行提示词
└──────┬──────┘
       ↓
┌─────────────┐
│  4. 调用子代理 │  openclaw agent
└──────┬──────┘
       ↓
┌─────────────┐
│  5. 解析结果  │  读取 JSON 输出
└──────┬──────┘
       ↓
┌─────────────┐
│  6. 更新状态  │  记录执行日志
└──────┬──────┘
       ↓
┌─────────────┐
│  7. 解锁任务  │  交由验证阶段
└──────┬──────┘
       ↓
┌─────────────┐
│  8. 启动验证  │  自动触发验证代理
└─────────────┘
```

### 7.2 执行任务

**API**: `POST /api/v2/tasks/execute`

**请求体**:
```json
{
  "task_id": 123,
  "model": "glm-5",
  "label": "exec-session-001",
  "timeout": 1800
}
```

**响应**:
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

### 7.3 查询执行状态

**API**: `GET /api/v2/tasks/{task_id}/status`

**响应**:
```json
{
  "task_id": 123,
  "task_no": "DTL-INFRA-001-001",
  "status": "completed",
  "execution_log": {
    "success": true,
    "output_files": ["src/api/auth.py", "src/models/user.py"],
    "key_changes": ["新增用户模型", "实现登录接口"]
  }
}
```

### 7.4 input_data 结构

任务执行依赖 `input_data` 字段，标准结构：

```json
{
  "requirements": "实现用户登录功能，支持邮箱和手机号登录",
  "expected_output": "生成 auth.py 和相关测试文件",
  "input_files": ["/docs/api-design.md", "/docs/db-schema.md"],
  "expected_output_files": ["src/api/auth.py", "tests/test_auth.py"],
  "project_path": "/data/projects/deeptutor-lite",
  "workflow_type": "BUILD-CODE"
}
```

### 7.5 执行模板

执行引擎使用模板生成提示词：

**模板位置**: `backend/templates/execution_prompt_template.md`

**模板变量**:
- `{{task_no}}` - 任务单号
- `{{task_name}}` - 任务名称
- `{{requirements}}` - 任务要求
- `{{input_files}}` - 输入文件列表
- `{{expected_output}}` - 预期输出

### 7.6 验证流程

执行成功后自动触发验证：

1. **锁定任务** - 验证阶段锁定
2. **构建验证提示词** - 基于执行结果
3. **调用验证代理** - `ac-validator`
4. **解析验证结果** - 通过/不通过
5. **更新验证状态** - 记录验证日志

---

## 8. 常见操作流程

### 8.1 创建新项目完整流程

```bash
# 1. 创建项目
POST /profiles
{
  "profile_type": "instance",
  "profile_name": "新项目名称",
  "project_type": "Web应用"
}

# 2. 创建阶段
POST /profiles/{profile_id}/phases
{
  "phase_id": "phase-1",
  "phase_name": "第一阶段",
  "phase_order": 1
}

# 3. 创建计划单
POST /plans
{
  "profile_id": "{profile_id}",
  "phase_record_id": "{phase_record_id}",
  "plan_name": "第一个计划单"
}

# 4. 创建任务单（通过导入或手动）
# 任务单通常通过导入脚本批量创建
```

### 8.2 执行任务流程

```bash
# 1. 查看待执行任务
GET /tasks?status=pending

# 2. 执行任务
POST /api/v2/tasks/execute
{
  "task_id": 123,
  "model": "glm-5"
}

# 3. 查询执行状态
GET /api/v2/tasks/123/status

# 4. 查看执行结果
GET /tasks/DTL-INFRA-001-001
```

### 8.3 批量执行任务

```bash
# 获取计划单下所有待执行任务
GET /plans/{plan_id}/tasks?status=pending

# 逐个执行（或并行执行，注意锁定机制）
for task in tasks:
    POST /api/v2/tasks/execute
    {
      "task_id": task.id,
      "model": "glm-5"
    }
```

---

## 9. 故障排查

### 9.1 任务执行失败

**现象**: 任务状态变为 `failed`

**排查步骤**:
1. 查看执行日志: `GET /tasks/{task_no}` → `execution_log`
2. 检查子代理配置: `openclaw agent list`
3. 检查模型配置: `~/.openclaw/openclaw.json`
4. 检查 OpenClaw 补丁是否应用

### 9.2 任务锁定无法解锁

**现象**: 任务状态为 `locked`，无法执行

**解决**:
```bash
# 手动解锁
PUT /tasks/{task_no}
{
  "status": "pending",
  "locked_by": null,
  "locked_at": null
}
```

### 9.3 子代理调用失败

**现象**: `openclaw agent` 命令失败

**排查**:
1. 检查 OpenClaw 安装: `openclaw --version`
2. 检查子代理存在: `openclaw agent list`
3. 检查 PATH 环境变量
4. 应用补丁: `bash openclaw-config/patches/apply-patch.sh`

### 9.4 数据库锁定

**现象**: API 返回 500 错误，日志显示数据库锁定

**解决**:
```bash
# 重启后端服务
pkill -f "uvicorn.*9001"
cd /data/projects/autocraft/backend
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

---

## 附录

### A. API 快速参考

| 功能 | 方法 | 路径 |
|------|------|------|
| 项目列表 | GET | `/profiles` |
| 创建项目 | POST | `/profiles` |
| 项目详情 | GET | `/profiles/{id}` |
| 更新项目 | PUT | `/profiles/{id}` |
| 删除项目 | DELETE | `/profiles/{id}` |
| 阶段列表 | GET | `/profiles/{id}/phases` |
| 创建阶段 | POST | `/profiles/{id}/phases` |
| 更新阶段 | PUT | `/phases/{id}` |
| 删除阶段 | DELETE | `/phases/{id}` |
| 计划列表 | GET | `/plans` |
| 创建计划 | POST | `/plans` |
| 计划详情 | GET | `/plans/{id}` |
| 更新计划 | PUT | `/plans/{id}` |
| 删除计划 | DELETE | `/plans/{id}` |
| 任务列表 | GET | `/tasks` |
| 任务详情 | GET | `/tasks/{no}` |
| 更新任务 | PUT | `/tasks/{no}` |
| 执行任务 | POST | `/api/v2/tasks/execute` |
| 执行状态 | GET | `/api/v2/tasks/{id}/status` |

### B. 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

**文档维护**: 皮皮虾 🦐  
**最后更新**: 2026-05-19
