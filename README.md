# AutoCraft - AI驱动的任务管理与执行平台

AutoCraft 是一个基于 AI 的任务管理系统，支持项目、阶段、计划、任务的四级管理结构，集成 AI 子代理自动执行和验证任务。

## ✨ 核心功能

- **四级项目管理**: 项目(Project) → 阶段(Phase) → 计划(Plan) → 任务(Task)
- **AI 任务执行**: 集成 OpenClaw AI 代理，自动执行任务
- **自动验证**: 任务执行完成后自动触发验证流程
- **知识库管理**: 支持知识点、知识图谱的管理
- **Issue 跟踪**: 完整的问题跟踪和解决方案管理

## 🏗️ 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: SQLite (通过 SQLAlchemy ORM)
- **AI 集成**: OpenClaw Agent

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI 组件**: Element Plus

## 📁 项目结构

```
autocraft/
├── backend/                 # 后端代码
│   ├── api/                 # API 路由
│   ├── crud/                # 数据库操作
│   ├── models/              # 数据模型
│   ├── schemas/             # Pydantic 模型
│   ├── services/            # 业务逻辑
│   ├── templates/           # 执行/验证模板
│   └── main.py              # 应用入口
├── src/                     # 前端代码
│   ├── api/                 # API 调用
│   ├── components/          # Vue 组件
│   ├── views/               # 页面视图
│   ├── router/              # 路由配置
│   └── types/               # TypeScript 类型
├── templates/               # 模板文件
└── public/                  # 静态资源
```

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- npm 或 pnpm
- OpenClaw (用于 AI 子代理)

### 一键部署

```bash
# 克隆项目
git clone https://github.com/your-username/autocraft.git
cd autocraft

# 运行部署脚本
bash scripts/deploy.sh
```

### 手动部署

#### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

后端 API 文档: http://localhost:9001/docs

#### 前端启动

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端界面: http://localhost:5173

### OpenClaw 子代理配置

AutoCraft 使用 OpenClaw 运行 AI 子代理，需要先配置：

```bash
# 创建子代理
bash openclaw-config/setup-agents.sh

# 编辑模型配置，填入 API Key
vim ~/.openclaw/agents/ac-executor/agent/models.json
```

详见 [部署指南](DEPLOYMENT.md) 和 [OpenClaw 配置](openclaw-config/README.md)。

## 📖 API 文档

### 项目管理
- `GET /profiles` - 获取项目列表
- `POST /profiles` - 创建项目
- `GET /profiles/{id}` - 获取项目详情
- `PUT /profiles/{id}` - 更新项目
- `DELETE /profiles/{id}` - 删除项目

### 阶段管理
- `GET /profiles/{profile_id}/phases` - 获取阶段列表
- `POST /profiles/{profile_id}/phases` - 创建阶段
- `PUT /phases/{phase_id}` - 更新阶段
- `DELETE /phases/{phase_id}` - 删除阶段

### 计划管理
- `GET /plans` - 获取计划列表
- `POST /plans` - 创建计划
- `GET /plans/{plan_id}` - 获取计划详情
- `PUT /plans/{plan_id}` - 更新计划
- `DELETE /plans/{plan_id}` - 删除计划

### 任务管理
- `GET /tasks` - 获取任务列表
- `GET /tasks/{task_no}` - 获取任务详情
- `PUT /tasks/{task_no}` - 更新任务

## 🔧 配置说明

### 后端配置
数据库文件默认为 `backend/tasks.db`，可在 `database.py` 中修改。

### 前端配置
API 基础路径配置在 `src/api/` 目录下的各个文件中。

## 📝 开发路线

- [x] 四级项目管理结构
- [x] AI 任务执行引擎
- [x] 自动验证流程
- [x] 知识库管理
- [x] Issue 跟踪
- [ ] 用户权限管理
- [ ] 任务执行日志详情
- [ ] 数据统计与报表

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
