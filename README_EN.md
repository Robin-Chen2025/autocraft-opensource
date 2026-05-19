# AutoCraft - AI-Powered Task Management & Execution Platform

[中文文档](README.md)

AutoCraft is an AI-based task management system that supports a four-level management structure (Project → Phase → Plan → Task), with integrated AI sub-agent automatic execution and task verification.

> **💡 Scope**: AutoCraft itself is a **general-purpose task management platform**, suitable for any scenario requiring structured task decomposition and AI automated execution (software development, content creation, data analysis, operations workflows, etc.). The built-in `autocraft-dev` Skill currently focuses on **software development projects**, with more domain-specific Skills coming soon.

## ✨ Core Features

- **Four-Level Project Management**: Project → Phase → Plan → Task hierarchy
- **AI Task Execution**: Integrated OpenClaw AI agents for automated task execution
- **Automatic Verification**: Verification workflow triggered automatically after task completion
- **Task Locking Mechanism**: Prevents concurrent conflicts, ensures safe task execution
- **Template-Driven**: Execution and verification prompt templates are configurable

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite (via SQLAlchemy ORM)
- **AI Integration**: OpenClaw Agent

### Frontend
- **Framework**: Vue 3 + TypeScript
- **Build Tool**: Vite
- **UI Components**: Element Plus

## 📁 Project Structure

```
autocraft/
├── backend/                 # Backend code
│   ├── api/                 # API routes
│   ├── crud/                # Database operations
│   ├── models/              # Data models
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic
│   ├── templates/           # Execution/verification templates
│   └── main.py              # Application entry
├── src/                     # Frontend code
│   ├── api/                 # API calls
│   ├── components/          # Vue components
│   ├── views/               # Page views
│   ├── router/              # Router configuration
│   └── types/               # TypeScript types
├── openclaw-config/         # OpenClaw configuration
│   ├── patches/             # Patch files
│   └── setup-agents.sh      # Sub-agent creation script
└── scripts/                 # Deployment scripts
```

## 🚀 Quick Start

### Requirements
- Python 3.10+
- Node.js 18+
- npm or pnpm
- OpenClaw (for AI sub-agents)

### One-Click Deployment

```bash
# Clone the project
git clone https://github.com/your-username/autocraft.git
cd autocraft

# Run deployment script
bash scripts/deploy.sh
```

### Manual Deployment

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start service
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

Backend API docs: http://localhost:9001/docs

#### Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend interface: http://localhost:5173

### OpenClaw Sub-Agent Configuration

AutoCraft uses OpenClaw to run AI sub-agents. Configuration required:

```bash
# 1. Apply patches (Important)
bash openclaw-config/patches/apply-patch.sh

# 2. Create sub-agents
bash openclaw-config/setup-agents.sh

# 3. Model configuration managed by OpenClaw
```

See [Deployment Guide](DEPLOYMENT_EN.md) and [OpenClaw Configuration](openclaw-config/README.md) for details.

## 📖 API Documentation

### Project Management
- `GET /profiles` - Get project list
- `POST /profiles` - Create project
- `GET /profiles/{id}` - Get project details
- `PUT /profiles/{id}` - Update project
- `DELETE /profiles/{id}` - Delete project

### Phase Management
- `GET /profiles/{profile_id}/phases` - Get phase list
- `POST /profiles/{profile_id}/phases` - Create phase
- `PUT /phases/{phase_id}` - Update phase
- `DELETE /phases/{phase_id}` - Delete phase

### Plan Management
- `GET /plans` - Get plan list
- `POST /plans` - Create plan
- `GET /plans/{plan_id}` - Get plan details
- `PUT /plans/{plan_id}` - Update plan
- `DELETE /plans/{plan_id}` - Delete plan

### Task Management
- `GET /tasks` - Get task list
- `GET /tasks/{task_no}` - Get task details
- `PUT /tasks/{task_no}` - Update task

### Task Execution
- `POST /api/v2/tasks/{task_id}/execute` - Execute task
- `GET /api/v2/tasks/{task_id}/status` - Get execution status

## 📝 Development Roadmap

### Completed ✅
- [x] Four-level project management structure
- [x] AI task execution engine
- [x] Automatic verification workflow
- [x] Task locking mechanism
- [x] Template-based prompts

### In Progress 🔄
- [ ] Task execution log details page
- [ ] Real-time execution progress push

### Planned 📋
- [ ] **Issue Tracking System** - Issue tracking and resolution management
- [ ] **Knowledge Base Management** - Knowledge points and knowledge graph management
- [ ] **Checklists** - Task execution checklists
- [ ] **User Permission Management** - Multi-user, role-based permissions
- [ ] **Data Statistics Reports** - Project progress, execution efficiency statistics
- [ ] **Task Templates** - Common task template library
- [ ] **Batch Operations** - Batch create, execute, verify
- [ ] **Webhook Notifications** - Task status change notifications
- [ ] **Docker Deployment** - One-click Docker deployment

## 🔧 Configuration

### Backend Configuration
Database file defaults to `backend/tasks.db`, configurable in `database.py`.

### Frontend Configuration
API base path configured in each file under `src/api/` directory.

## 📚 Documentation

- [System Operation Manual](docs/OPERATION_MANUAL_EN.md) - Complete usage guide
- [Deployment Guide](DEPLOYMENT_EN.md) - Production deployment

## 🤝 Contributing

Issues and Pull Requests are welcome!

### Development Guide
1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Create Pull Request

## 📄 License

MIT License

## 🙏 Acknowledgments

- [OpenClaw](https://github.com/openclaw/openclaw) - AI agent runtime
- [FastAPI](https://fastapi.tiangolo.com) - Modern API framework
- [Vue.js](https://vuejs.org) - Progressive frontend framework