# AutoCraft - AI驱动的任务管理与执行平台

AutoCraft 是一个基于 AI 的任务管理系统，支持项目、阶段、计划、任务的四级管理结构，集成 AI 子代理自动执行和验证任务。

## ✨ 核心功能

- **四级项目管理**: 项目(Project) → 阶段(Phase) → 计划(Plan) → 任务(Task)
- **AI 任务执行**: 集成 OpenClaw AI 代理，自动执行任务
- **自动验证**: 任务执行完成后自动触发验证流程
- **任务锁定机制**: 防止并发冲突，确保任务执行安全
- **模板驱动**: 执行和验证提示词模板化，灵活可配置

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
├── openclaw-config/         # OpenClaw 配置
│   ├── patches/             # 补丁文件
│   └── setup-agents.sh      # 子代理创建脚本
└── scripts/                 # 部署脚本
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
# 1. 应用补丁（重要）
bash openclaw-config/patches/apply-patch.sh

# 2. 创建子代理
bash openclaw-config/setup-agents.sh

# 3. 模型配置由 OpenClaw 统一管理
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

### 任务执行
- `POST /api/v2/tasks/{task_id}/execute` - 执行任务
- `GET /api/v2/tasks/{task_id}/status` - 获取执行状态

## 📝 开发路线

### 已完成 ✅
- [x] 四级项目管理结构
- [x] AI 任务执行引擎
- [x] 自动验证流程
- [x] 任务锁定机制
- [x] 模板化提示词

### 进行中 🔄
- [ ] 任务执行日志详情页
- [ ] 执行进度实时推送

### 计划中 📋
- [ ] **Issue 跟踪系统** - 问题跟踪与解决方案管理
- [ ] **知识库管理** - 知识点、知识图谱管理
- [ ] **检查清单** - 任务执行检查清单
- [ ] **用户权限管理** - 多用户、角色权限
- [ ] **数据统计报表** - 项目进度、执行效率统计
- [ ] **任务模板** - 常用任务模板库
- [ ] **批量操作** - 批量创建、执行、验证
- [ ] **Webhook 通知** - 任务状态变更通知
- [ ] **Docker 部署** - 一键 Docker 部署

## 🔧 配置说明

### 后端配置
数据库文件默认为 `backend/tasks.db`，可在 `database.py` 中修改。

### 前端配置
API 基础路径配置在 `src/api/` 目录下的各个文件中。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发指南
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

MIT License

## 🙏 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) - AI 代理运行时
- [FastAPI](https://fastapi.tiangolo.com) - 现代化 API 框架
- [Vue.js](https://vuejs.org) - 渐进式前端框架
