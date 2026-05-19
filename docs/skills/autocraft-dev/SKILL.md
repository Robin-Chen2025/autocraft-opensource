---
name: autocraft-dev
description: AutoCraft辅助软件开发工作流。两阶段模式：(1)设计阶段——按设计规范生成PRD/系统功能设计/API设计/数据库设计/开发计划等文档，子代理生成+审核闭环；(2)执行阶段——开发计划导入AutoCraft，调用执行引擎逐任务单执行AI子代理+自动验证。触发场景：(1)新功能开发 (2)项目初始化 (3)设计文档生成与审核 (4)任务拆解与执行 (5)代码/文档的AI生成与验证
---

# AutoCraft 辅助软件开发

**版本：** v1.2  
**更新：** 2026-05-19  
**更新内容：** 新增系统安装指引

---

## ⚡ 快速开始

### 1. 安装 AutoCraft 系统

本 Skill 需要 AutoCraft 系统支持，请先部署系统：

```bash
# 从 GitHub 克隆
git clone https://github.com/Robin-Chen2025/autocraft-opensource.git
cd autocraft-opensource

# 或从 Gitee 克隆（国内更快）
git clone https://gitee.com/robin1985/autocraft-opensource.git
cd autocraft-opensource
```

### 2. 部署系统

详见 [DEPLOYMENT.md](https://github.com/Robin-Chen2025/autocraft-opensource/blob/main/DEPLOYMENT.md)

```bash
# 后端
cd backend
pip install -r requirements.txt
cp .env.example .env  # 编辑配置
python3 -m uvicorn main:app --host 0.0.0.0 --port 9001

# 前端
cd ..
npm install
npm run dev
```

### 3. 安装本 Skill

```bash
clawhub install autocraft
```

### 4. 访问系统

- 前端界面：http://localhost:8080
- API 文档：http://localhost:9001/docs

---

## 两阶段模型

```
阶段一：设计阶段（不用AutoCraft）
    │
    │  PRD → 功能设计 → 技术方案 → API/DB/UI设计
    │  → 测试方案 → 开发计划（总览 + 工作计划清单）
    │  → 整体性验证
    │
    ▼  开发计划定稿
阶段二：执行阶段（进入AutoCraft）
    │
    │  逐个拆解任务单 → API导入AutoCraft
    │  → 执行引擎逐任务单执行（AI子代理）
    │  → 自动验证 → 主代理验收 → 状态级联
    │
    ▼  项目完成
```

---

## 你的角色

**你是项目经理**——做决策、拆任务、验收。不写代码。

| 你做 | 你不做 |
|------|--------|
| 需求澄清、方案选择 | 写具体代码 |
| 文档审核把关 | 直接操作数据库 |
| 任务拆解和调度 | 信任子代理的"完成" |
| 验收产出物 | 跳过验证步骤 |

---

## 阶段一：设计阶段

### 设计文档体系

按 `references/design-specs/设计阶段文档规范-总纲.md` 执行。

**必产文档**：

| 序号 | 文档 | 编码 | 详细规范 | 审核Checklist |
|------|------|------|---------|---------------|
| 01 | PRD | PRD | [01-PRD规范](references/design-specs/doc-specs/01-PRD规范.md) | [09-PRD审核](references/design-specs/doc-specs/09-PRD审核Checklist.md) |
| 03 | 系统功能设计 | FUNC | [03-系统功能设计](references/design-specs/doc-specs/03-系统功能设计文档规范.md) | [11-功能设计审核](references/design-specs/doc-specs/11-系统功能设计审核Checklist.md) |
| 04 | 技术方案 | TECH | [04-技术方案](references/design-specs/doc-specs/04-技术方案文档规范.md) | [12-技术方案审核](references/design-specs/doc-specs/12-技术方案审核Checklist.md) |
| 07 | API设计 | API | [07-API设计](references/design-specs/doc-specs/07-API设计文档规范.md) | [14-API设计审核](references/design-specs/doc-specs/14-API设计审核Checklist.md) |
| 08 | 数据库设计 | DB | [08-数据库设计](references/design-specs/doc-specs/08-数据库设计文档规范.md) | [15-数据库设计审核](references/design-specs/doc-specs/15-数据库设计审核Checklist.md) |
| 18 | 整体性验证 | VERIFY | - | [18-整体性验证](references/design-specs/doc-specs/18-设计阶段整体性验证Checklist.md) |

**按需产出**：

| 序号 | 文档 | 编码 | 详细规范 | 审核Checklist |
|------|------|------|---------|---------------|
| 00 | 需求清单 | REQ | [00-需求清单](references/design-specs/doc-specs/00-需求清单规范.md) | 见规范第六章 |
| 02 | 业务流程 | FLOW | [02-业务流程](references/design-specs/doc-specs/02-业务流程文档规范.md) | [10-业务流程审核](references/design-specs/doc-specs/10-业务流程审核Checklist.md) |
| 05 | UI设计 | UI | [05-UI设计](references/design-specs/doc-specs/05-UI设计文档规范.md) | [13-UI设计审核](references/design-specs/doc-specs/13-UI设计审核Checklist.md) |
| 06 | 组件规范 | COMP | [06-组件规范](references/design-specs/doc-specs/06-组件规范文档规范.md) | [16-组件规范审核](references/design-specs/doc-specs/16-组件规范审核Checklist.md) |

### 文档产出顺序

```
PRD → 业务流程(按需) → 系统功能设计 → 技术方案
    → Vue骨架原型(用户确认) → UI设计 + API设计 + 组件规范 + 数据库设计
    → 整体性验证
```

**依赖关系**：每个文档依赖前置文档的功能ID追溯链（FR-001 → F-001 → API → DB）。

### 文档生成流程

用**子代理**生成文档（替代Crush）：

```
1. 准备输入材料（前置文档 + 规范文件）
2. 子代理生成第一版文档
3. 子代理按审核Checklist审核
4. 根据问题清单修复
5. 再审核确认
6. 定稿（用户审阅）
```

**子代理调用方式**：

**设计阶段启用多轮会话模式**：
```bash
# 创建持久会话（支持多轮审核修复）
openclaw agent --session-id explicit:doc_session_{project_name}_{timestamp} \
  --agent-id ac-glm5 \
  --model glm-5 \
  --message "读取以下规范文件和输入材料，生成{文档类型}文档..."

# 同一会话中进行审核
openclaw agent --session-id explicit:doc_session_{project_name}_{timestamp} \
  --message "根据审核Checklist审核生成的文档..."

# 同一会话中进行修复
openclaw agent --session-id explicit:doc_session_{project_name}_{timestamp} \
  --message "根据审核报告修复文档..."
```

**关键要求**：
- 设计阶段文档生成使用**多轮会话模式**，支持同一子代理完成生成→审核→修复闭环
- 子代理必须读取对应的**规范文件**和**审核Checklist**再生成
- 生成后立即用Checklist自审
- 评分≥80才提交用户审阅，<70则重新生成
- 使用**GLM-5模型**进行设计阶段文档工作

### 测试方案

按 `references/design-specs/质量检测方案/` 生成：

| 文档 | 路径 | 用途 |
|------|------|------|
| 测试方案总纲 | [21-总纲生成规范](references/design-specs/质量检测方案/21-测试方案总纲生成规范.md) | 项目整体测试策略 |
| BE-L2测试方案 | [22-BE-L2规范](references/design-specs/质量检测方案/22-BE-L2测试方案规范.md) | 后端集成测试 |
| FE-L2测试方案 | [23-FE-L2规范](references/design-specs/质量检测方案/23-FE-L2测试方案规范.md) | 前端集成测试 |
| L3-E2E测试方案 | [24-L3-E2E规范](references/design-specs/质量检测方案/24-L3-E2E测试方案规范.md) | 端到端测试 |
| L1测试方案 | [30/31规范](references/design-specs/质量检测方案/30-L1-BE测试方案规范.md) | 单元测试 |

### 开发计划

按 `references/design-specs/开发计划方案/` 生成：

**两层结构**：
- **开发计划总览**：批次顺序、模块依赖、功能概览
- **工作计划清单**：每个工作计划的任务单结构概要

| 文档 | 规范 | 审核 |
|------|------|------|
| 总览 | [40-生成规范](references/design-specs/开发计划方案/40-开发计划生成规范.md) | [43-总览审核](references/design-specs/开发计划方案/43-开发计划总览审核Checklist.md) |
| 总览详情 | [41-总览生成](references/design-specs/开发计划方案/41-开发计划总览生成规范.md) | - |
| 清单 | [42-清单生成](references/design-specs/开发计划方案/42-工作计划清单生成规范.md) | [44-清单审核](references/design-specs/开发计划方案/44-工作计划清单审核Checklist.md) |
| 整体性 | - | [45-整体性审核](references/design-specs/开发计划方案/45-开发计划整体性审核Checklist.md) |

**关键原则**：
- 工作计划数量由具体项目决定，不硬编码
- 编号约束在清单中定义，FlowTicket执行时必须遵守
- 任务单详情JSON在FlowTicket启动时动态生成，不预生成

---

## 阶段二：执行阶段

### 导入AutoCraft

开发计划定稿后，主代理逐个拆解任务单，通过API导入：

```bash
# 1. 创建项目档案
curl -X POST http://localhost:9001/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"profile_id":"...", "profile_name":"...", ...}'

# 2. 创建阶段和工作流
curl -X POST http://localhost:9001/api/profiles/{id}/phases -d '...'
curl -X POST http://localhost:9001/api/profiles/{id}/workflows -d '...'

# 3. 创建工作计划
curl -X POST http://localhost:9001/plans -d '...'

# 4. 逐个创建任务单
curl -X POST http://localhost:9001/tasks -d '...'
```

### 任务创建

⚠️ **按 `references/task-creator/SKILL.md` 执行**，包含完整的：
- input_data 标准格式和必填字段
- workflow_type 与 task_type 映射表
- input_files 配置指南
- 批量创建示例代码
- 常见错误与检查清单

**核心铁律**：
1. 所有路径必须是**绝对路径**
2. `project_path` 必须指向正确的项目根目录
3. `input_files` 至少包含1个设计文档
4. `requirements` 必须详细具体
5. `expected_output_files` 必须列出所有预期文件
6. `input_data` 必须通过 `json.dumps()` 转为JSON字符串

### Simple FlowTicket 执行任务单

**调用方式**：

```bash
# 1. 提交执行请求（异步）
curl -X POST http://localhost:9001/api/v2/tasks/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": <task_id>,
    "model": "glm-5.1",
    "label": "执行任务XXX",
    "timeout": 1800
  }'

# 2. 查询任务状态（轮询）
curl -X GET "http://localhost:9001/api/v2/tasks/{task_id}/status"

# 3. 检查执行结果
# - 状态为 "completed" 或 "verified" 表示成功
# - 状态为 "failed" 或 "verification_failed" 表示失败
# - execution_log 和 verification_log 包含详细信息
```

**任务状态流转**：
```
pending → in_progress → completed → verifying → verified
                     ↓
                   failed → (可重新执行)
                                  ↓
                          verification_failed
```

**任务数据格式要求**：

⚠️ **input_data 字段必须完整**，确保子代理能正确执行任务：

```json
{
  "input_files": [
    "/data/projects/{project}/docs/design/07-API设计-{project}.md",
    "/data/projects/{project}/docs/design/03-系统功能设计-{project}.md"
  ],
  "requirements": "详细的任务要求描述...",
  "expected_output": "详细的预期输出描述...",
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

**关键要求**：
- ✅ **input_files 必须是绝对路径**（不要使用相对路径）
- ✅ **requirements 必须详细描述任务要求**（不能是"无具体要求"）
- ✅ **expected_output 必须详细描述预期输出**（不能是"根据任务描述生成相应产出物"）
- ✅ **expected_output_files 必须列出预期输出文件路径**（绝对路径）
- ✅ **workflow_type 必须正确**（BUILD/DOC/TEST等）

**⚠️ 路径配置教训**：
- ❌ **错误示例**：`backend/api/routers/knowledge_graph.py`（相对路径）
- ✅ **正确示例**：`/data/projects/deeptutor-lite/backend/api/routers/knowledge_graph.py`（绝对路径）
- ❌ **问题**：相对路径会导致文件生成到错误目录（如 autocraft 项目）
- ✅ **解决方案**：所有路径必须从项目根目录 `/data/projects/{project}/` 开始

**执行机制**：

1. **异步执行**：提交执行请求后立即返回，不等待完成
2. **状态轮询**：通过状态查询端点检查任务进度
3. **自动验证**：执行完成后自动启动验证子代理
4. **结果通知**：验证完成后可通过 callback_target 接收通知

**执行闭环**：
```
读取任务 → 渲染模板 → 调用执行子代理(GLM-5)
→ 产出物写入项目目录（按expected_output_files指定路径）
→ JSON结果写入/tmp/autocraft_output/{task_id}_execution_result.json
→ 引擎读取JSON → 更新状态 → 自动启动验证子代理(DeepSeek-V3.2)
→ 验证结果写入/tmp/autocraft_output/{task_id}_verification_result.json
→ 引擎读取JSON → 更新最终状态（verified/verification_failed）
```

**模型配置**：

| 用途 | 模型 | Agent ID |
|------|------|----------|
| 执行 | GLM-5.1 | ac-glm5 |
| 验证 | DeepSeek-V3.2-thinking | ac-validator |

**注意事项**：

1. **不监控执行过程**：提交任务后，Simple FlowTicket 会自动执行和验证，完成或失败时会通知
2. **验证机制有效**：能够识别执行子代理的虚假报告（如声称创建文件但实际未创建）
3. **产出物验证**：验证子代理会检查文件是否真实存在，代码是否符合设计文档
4. **架构检查**：验证包含6个维度，其中"架构合理性"检查代码是否符合单一职责原则
5. **路径配置验证**：验证子代理会检查产出物是否在正确目录，避免生成到错误项目

### 验收铁律

1. **不信任子代理的"完成"**——必须检查产出物文件
2. **验证由引擎自动执行**——PASS/FAIL 逐项判定，维度全 PASS 才通过
3. **产出物路径必须对照**——检查文件是否在 deliverables 指定位置
4. **架构合理性强制检查**——新增第6维度"架构合理性"，违反SRP原则直接FAIL
5. **设计符合性强制检查**——新增第7维度"设计符合性"，检查实现是否符合设计文档

### 验证维度（7个）

| 维度 | 检查内容 | FAIL条件 |
|------|---------|----------|
| 1. 完整性 | 产出物文件是否存在 | 文件不存在 |
| 2. 正确性 | 代码语法是否正确 | 编译/解析失败 |
| 3. 功能性 | 是否实现requirements要求 | 核心功能缺失 |
| 4. 规范性 | 是否符合代码规范 | 严重规范违规 |
| 5. 可测试性 | 是否可运行测试 | 测试无法执行 |
| 6. 架构合理性 | 是否符合单一职责原则 | 违反SRP |
| **7. 设计符合性** | **是否符合设计文档定义** | **偏离设计文档** |

### 设计符合性检查细则

**检查时机**：所有BUILD-CODE和BUILD-TEST任务

**检查内容**：

1. **前端任务**：
   - API调用路径是否与API设计文档一致
   - 通信方式是否与设计文档一致（HTTP API vs WebSocket）
   - 组件Props/Events是否与组件规范一致

2. **后端任务**：
   - API端点路径是否与API设计文档一致
   - 请求/响应格式是否与API设计文档一致
   - 数据库表/字段是否与数据库设计文档一致

3. **测试任务**：
   - 测试场景是否覆盖测试方案定义的用例
   - 断言是否与测试方案验收标准一致

**FAIL判定**：
- 前端用了设计文档未定义的通信方式（如WebSocket直连Gateway）
- API路径与设计文档不一致
- 数据库表结构与设计文档不一致
- 组件接口与组件规范不一致

**教训来源**：LRN-20260514-005
- **问题**：M01-FE-DEV任务requirements明确要求"调用POST /api/chat/messages"，input_files包含API设计.md，但子代理自行选择WebSocket直连Gateway方案，导致所有测试失败
- **根因**：验证环节只检查"功能是否实现"，未检查"是否符合设计文档"
- **修复**：验证维度增加"设计符合性"，强制检查实现与设计文档的一致性

### 状态级联

任务完成触发级联更新：

```bash
POST /status/cascade/{task_no}
```

任务 → 工作计划 → 工作流 → 阶段 → 项目

---

## AutoCraft 系统信息

| 组件 | 地址 | 管理方式 |
|------|------|---------|
| 统一后端 | `http://localhost:9001` | systemd: `autocraft-backend` |
| 前端（查看窗口） | `http://localhost:8080` | systemd: `autocraft-frontend` |
| API文档 | `http://localhost:9001/docs` | OpenAPI交互文档 |

**服务管理**：
```bash
sudo systemctl restart autocraft-backend autocraft-frontend
sudo systemctl status autocraft-backend autocraft-frontend
curl http://localhost:9001/health  # 健康检查
```

---

## 铁律

| 规则 | 说明 |
|------|------|
| **行动前必须与用户确认** | 每个关键步骤（启动项目、生成文档、执行任务、验收等）开始前必须向用户说明计划并等待确认，未获确认不得执行 |
| **设计阶段多轮会话** | 设计阶段文档生成使用多轮会话模式，同一子代理（GLM-5）完成生成→审核→修复闭环 |
| 主代理不写代码 | 你是项目经理，子代理干活 |
| 所有操作走API | 禁止直接操作数据库 |
| 验证产出物 | 不信任"完成"二字 |
| Git规范 | 禁止 `reset --hard`、`push --force` |
| 模型隔离 | **设计阶段：GLM-5**，执行阶段：GLM-5（执行）+ DeepSeek-V3.2（验证） |
| 会话隔离 | 执行阶段每个任务独立session，设计阶段多轮会话 |
| 设计规范优先 | 文档生成必须读规范文件，不凭印象写 |
| **路径必须绝对** | 所有文件路径必须是绝对路径，禁止使用相对路径 |
| **项目目录明确** | 必须指定正确的 project_path，确保文件生成到正确位置 |

---

## 从旧skill迁移

本skill替代 `auto-coding-workflow`（v3.0）：

| 旧 | 新 |
|----|-----|
| Crush生成文档 | 子代理生成文档 |
| 两套服务(9001+9002) | 统一后端9001 + systemd |
| webhook回调 | JSON文件驱动 |
| 手动执行流程 | API触发 + 自动验证闭环 |
| 设计规范外置 | 设计规范内置references |

---

## 子代理指引

ac-glm5（执行子代理）和 ac-validator（验证子代理）的综合指引：

- **ac-agent-guide**：`references/ac-agent-guide/SKILL.md`
  - 角色识别（根据Agent ID自动判断执行/验证角色）
  - 执行子代理：5种任务类型（BUILD-CODE/BUILD-TEST/BUILD-ENV/DOC/DESIGN）
  - 验证子代理：3种任务类型 + PASS/FAIL判定 + 验证维度
  - 辅助skill索引：根据技术栈自动选择对应skill
  - JSON结果文件格式规范
  - 共享规范（文件操作、产出物目录、常用命令）

> 当子代理被AutoCraft执行引擎调用时，应读取此skill获取角色定义和行为规范。

---

## 架构检查与模板库

### 架构检查工具

新增第6个验证维度：**架构合理性**，检查代码是否符合设计原则：

| 维度 | 检查项 | 判定标准 |
|------|--------|----------|
| 架构合理性 | 文件职责是否单一（SRP），代码结构是否清晰，功能边界是否分明 | 违反SRP原则 → FAIL |

**架构检查脚本**：`scripts/architecture-check/architecture_check.py`
- 检查文件职责单一性（SRP原则）
- 检查代码结构合理性（分层架构）
- 检查功能边界分明性（耦合度）
- 生成架构健康度报告

**使用方式**：
```bash
python3 scripts/architecture-check/architecture_check.py --path /path/to/code --report architecture_report.json
```

### 标准化模板库

提供标准代码模板，确保架构一致性：

| 模板 | 路径 | 用途 |
|------|------|------|
| FastAPI路由模板 | `templates/fastapi-module/router_template.py` | 路由层代码模板 |
| 服务层模板 | `templates/fastapi-module/service_template.py` | 业务逻辑层模板 |
| 测试模板 | `templates/fastapi-module/test_template.py` | 测试代码模板 |
| pytest配置 | `templates/config-templates/pytest.ini` | 测试配置模板 |
| 架构规则 | `templates/architecture-rules/architecture_rules.md` | 架构规范文档 |

### 验证子代理集成

验证子代理（ac-validator）现在需要检查6个维度：
1. ✅ 完整性
2. ✅ 正确性
3. ✅ 可运行性
4. ✅ 一致性
5. ✅ 安全性
6. ✅ **架构合理性**（新增）

**架构合理性检查清单**：
- 文件职责单一性（SRP原则）
- 代码结构合理性（分层架构）
- 功能边界分明性（耦合度控制）
- 代码复杂度控制（文件大小/函数复杂度）

### 验证结果JSON格式更新

```json
{
  "verification_success": true,
  "verification_report": "完整验证报告",
  "dimension_results": {
    "完整性": "PASS",
    "正确性": "PASS",
    "可运行性": "PASS",
    "一致性": "PASS",
    "安全性": "PASS",
    "架构合理性": "PASS"  // 新增维度
  },
  "issues_found": [],
  "improvements_suggested": []
}
```

## 参考文档索引

| 类别 | 目录 | 文件数 |
|------|------|--------|
| 设计规范-文档规范 | `references/design-specs/doc-specs/` | 20 |
| 设计规范-开发计划 | `references/design-specs/开发计划方案/` | 9 |
| 设计规范-质量检测 | `references/design-specs/质量检测方案/` | 28 |
| 设计规范-总纲 | `references/design-specs/设计阶段文档规范-总纲.md` | 1 |
| 子代理指引 | `references/ac-agent-guide/SKILL.md` | 1 |
| **任务单创建** | `references/task-creator/SKILL.md` | 1 |
| 架构检查工具 | `scripts/architecture-check/` | 3 |
| 标准化模板库 | `templates/` | 5 |
