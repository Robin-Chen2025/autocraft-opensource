---
name: project-init
description: AutoCraft 项目初始化流程。四层结构创建：项目(Project) → 阶段(Phase) → 计划单(Plan) → 任务单(Task)。触发场景：(1)新项目启动 (2)项目阶段划分 (3)开发计划导入
---

# AutoCraft 项目初始化流程

**版本：** v1.0  
**更新：** 2026-05-19

---

## 四层管理结构

```
项目 (Project)
  └── 阶段 (Phase)
        └── 计划单 (Plan)
              └── 任务单 (Task)
```

| 层级 | 标识字段 | 说明 |
|------|----------|------|
| 项目 | `profile_id` | 项目档案，定义项目基本信息 |
| 阶段 | `phase_record_id` | 开发阶段划分（如 M-01, M-02） |
| 计划单 | `plan_id` | 一组相关任务的集合 |
| 任务单 | `task_no` | 最小执行单元 |

---

## 你的角色

**你是项目经理**——做决策、拆任务、验收。不写代码。

| 你做 | 你不做 |
|------|--------|
| 创建项目、划分阶段 | 直接操作数据库 |
| 导入开发计划 | 跳过验证步骤 |
| 验收产出物 | 信任子代理的"完成" |

---

## 阶段零：项目初始化

### 创建流程

```
1. 创建项目档案 (POST /profiles)
2. 创建阶段 (POST /profiles/{profile_id}/phases)
3. 创建计划单 (POST /plans)
4. 导入任务单 (POST /tasks 或批量导入)
```

---

## 1. 创建项目档案

### API

**POST /profiles**

### 请求体

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

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `profile_type` | ✅ | `template`=模板，`instance`=实例 |
| `profile_name` | ✅ | 项目名称 |
| `project_type` | ❌ | 项目类型（Web应用、CLI工具等） |
| `description` | ❌ | 项目描述 |
| `tech_stack` | ❌ | 技术栈 |
| `root_path` | ❌ | 项目根路径 |
| `profile_id` | ❌ | 自定义ID，不传则自动生成 |
| `template_profile_id` | ❌ | 从模板复制时使用 |

### 响应

```json
{
  "message": "项目档案创建成功",
  "profile_id": "deeptutor-lite"
}
```

### 命名规范

- **profile_id**: 小写字母+连字符，如 `deeptutor-lite`、`autocraft`
- **profile_name**: 中文全称，如 "DeepTutor-Lite AI辅助学习系统"

### 决策点

**项目创建前确认：**

1. 项目名称是否明确？
2. 技术栈是否确定？
3. 项目根路径是否存在？
4. 是否需要从模板复制？

---

## 2. 创建阶段

### API

**POST /profiles/{profile_id}/phases**

### 请求体

```json
{
  "phase_id": "m01-be",
  "phase_name": "M-01 后端开发",
  "phase_order": 1,
  "status": "pending"
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `phase_id` | ✅ | 阶段标识（如 m01-be） |
| `phase_name` | ✅ | 阶段名称（如 M-01 后端开发） |
| `phase_order` | ✅ | 阶段顺序（从0开始） |
| `status` | ❌ | 状态：pending/in_progress/completed |

### 响应

```json
{
  "message": "阶段创建成功",
  "phase_record_id": "deeptuto-m01-be-phase"
}
```

### 命名规范

- **phase_id**: 小写字母+连字符，如 `infra`、`m01-be`、`m02-fe`
- **phase_record_id**: 自动生成，格式为 `{profile_id前缀}-{phase_id}-phase`
- **phase_name**: 带序号的中文名称，如 "M-01 后端开发"

### 阶段划分建议

| 序号 | 阶段 | 说明 |
|------|------|------|
| 0 | INFRA | 基础设施（数据库、配置） |
| 1 | M-01 | 第一个开发迭代 |
| 2 | M-02 | 第二个开发迭代 |
| ... | ... | ... |

---

## 3. 创建计划单

### API

**POST /plans**

### 请求体

```json
{
  "profile_id": "deeptutor-lite",
  "phase_record_id": "deeptuto-m01-be-phase",
  "plan_name": "WP-M01-BE-001: 用户认证模块",
  "description": "实现用户登录、注册、权限验证功能",
  "status": "pending"
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `profile_id` | ✅ | 所属项目ID |
| `phase_record_id` | ❌ | 所属阶段ID |
| `plan_name` | ✅ | 计划名称 |
| `description` | ❌ | 计划描述 |
| `status` | ❌ | 状态：pending/in_progress/completed |

### 响应

```json
{
  "message": "计划单创建成功",
  "plan_id": "plan_b4ffaa5474b44734"
}
```

### 命名规范

- **plan_id**: 自动生成，格式为 `plan_{uuid前16位}`
- **plan_name**: 格式为 `WP-{阶段}-{序号}: {功能名称}`

### 计划单创建时机

- 设计阶段完成后
- 开发计划总览定稿后
- 每个计划单对应一组相关任务

---

## 4. 导入任务单

### 单个创建

**POST /tasks**

```json
{
  "task_no": "DTL-M01-BE-001-001",
  "task_name": "实现用户登录接口",
  "task_type": "BUILD-CODE",
  "plan_id": "plan_b4ffaa5474b44734",
  "phase_record_id": "deeptuto-m01-be-phase",
  "status": "pending",
  "priority": "high",
  "executor": "ac-executor",
  "expected_result": "生成 auth.py 包含登录接口",
  "input_data": "{\"requirements\": \"实现JWT登录\", \"expected_output_files\": [\"src/api/auth.py\"]}"
}
```

### 批量导入

使用 `scripts/import_tasks.py` 脚本：

```bash
python scripts/import_tasks.py \
  --plan-id plan_b4ffaa5474b44734 \
  --phase-record-id deeptuto-m01-be-phase \
  --input /path/to/tasks.json
```

### 任务单字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `task_no` | ❌ | 任务单号（不传则自动生成） |
| `task_name` | ✅ | 任务名称 |
| `task_type` | ❌ | 任务类型（BUILD-CODE等） |
| `plan_id` | ❌ | 所属计划单 |
| `phase_record_id` | ❌ | 所属阶段 |
| `status` | ❌ | 状态（默认pending） |
| `priority` | ❌ | 优先级（high/medium/low） |
| `executor` | ❌ | 执行者（ac-executor） |
| `expected_result` | ❌ | 预期结果 |
| `input_data` | ❌ | 输入数据（JSON字符串） |

### 命名规范

- **task_no**: 格式为 `{项目前缀}-{阶段}-{序号}-{子序号}`
  - 如：`DTL-M01-BE-001-001`
  - `DTL` = 项目前缀（DeepTutor-Lite）
  - `M01-BE` = 阶段标识
  - `001` = 计划单序号
  - `001` = 任务序号

---

## 完整示例：创建新项目

### 场景

创建一个名为 "MyProject" 的新项目，包含两个阶段。

### 步骤

```
# 1. 创建项目
POST /profiles
{
  "profile_type": "instance",
  "profile_name": "MyProject 示例项目",
  "project_type": "Web应用",
  "tech_stack": "Vue3 + FastAPI"
}
# 响应: profile_id = "myproject"

# 2. 创建阶段 INFRA
POST /profiles/myproject/phases
{
  "phase_id": "infra",
  "phase_name": "INFRA 基础设施",
  "phase_order": 0
}
# 响应: phase_record_id = "myproj-infra-phase"

# 3. 创建阶段 M-01
POST /profiles/myproject/phases
{
  "phase_id": "m01",
  "phase_name": "M-01 核心功能",
  "phase_order": 1
}
# 响应: phase_record_id = "myproj-m01-phase"

# 4. 创建计划单
POST /plans
{
  "profile_id": "myproject",
  "phase_record_id": "myproj-infra-phase",
  "plan_name": "WP-INFRA-001: 项目初始化"
}
# 响应: plan_id = "plan_xxx"

# 5. 导入任务单（批量）
python scripts/import_tasks.py --plan-id plan_xxx ...
```

---

## 查询 API

### 查询项目列表

```
GET /profiles?page=1&page_size=10
```

### 查询项目详情

```
GET /profiles/{profile_id}
```

### 查询阶段列表

```
GET /profiles/{profile_id}/phases
```

### 查询计划单列表

```
GET /plans?profile_id={profile_id}
GET /plans?phase_record_id={phase_record_id}
```

### 查询计划单详情

```
GET /plans/{plan_id}
```

### 查询任务单列表

```
GET /tasks?plan_id={plan_id}
GET /tasks?status=pending
```

---

## 状态流转

### 阶段状态

```
pending → in_progress → completed
```

### 计划单状态

```
pending → in_progress → completed
```

### 任务单状态

```
pending → locked → executing → completed
                    ↓
                  failed
```

---

## 注意事项

1. **先创建项目，再创建阶段**
2. **先创建阶段，再创建计划单**
3. **计划单可以不关联阶段**（兼容旧数据）
4. **任务单可以不关联计划单**（兼容旧数据）
5. **删除项目会级联删除阶段、计划单、任务单**

---

## 与设计阶段的关系

```
阶段零：项目初始化
    ↓
阶段一：设计阶段
    PRD → 功能设计 → 技术方案 → API/DB设计
    → 开发计划总览 + 工作计划清单
    ↓
阶段二：执行阶段
    导入计划单 → 导入任务单 → 执行引擎 → 验证
```

**项目初始化时机：**
- 设计阶段开始前（创建项目档案）
- 开发计划定稿后（创建阶段和计划单）
- 任务拆解完成后（导入任务单）

---

_最后更新: 2026-05-19_
