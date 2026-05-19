# AutoCraft - AI-Powered Project Execution Platform

[English](README_EN.md) | [中文](README.md)

> **🚀 Empower non-technical product managers to drive complex software development projects, 3-6x faster**

AutoCraft is a platform that perfectly combines human project management wisdom with AI automatic execution capabilities. **Humans focus on design decisions, AI focuses on coding execution**, turning ideas into running products quickly.

## ✨ Core Value

### 🎯 What Problems Does It Solve?
- **Product managers have ideas but no tech team?**
- **Development projects take too long with high communication costs?**
- **Want to validate ideas without heavy resource investment?**

### 💡 What Solution Does It Provide?
- **Humans**: Focus on design, decisions, creativity
- **AI**: Automatically handles coding, testing, verification
- **Result**: Faster, cheaper, higher quality products

## 📊 Real Case Study: Complete Education Platform Built in 10 Days

We used AutoCraft to complete the full development of DeepTutor-Lite education platform in **just 10 days**:

### Execution Data
```
📈 Project Scale:
   Plan Sheets: 19
   Tasks: 71
   Successful: 70 (99% success rate)

🔧 Quality Metrics:
   Program BUGs Found: 7 (all automatically fixed)
   Test Coverage: 100% (L1+L2+L3)
   Human Intervention: Only 3 key decisions

⏱️ Efficiency Comparison:
   Traditional Estimate: 1-2 months
   AutoCraft: 10 days (3-6x faster)
```

### Technical Output
- **Backend**: FastAPI + SQLite (complete REST API)
- **Frontend**: Vue 3 + TypeScript (modern interface)
- **Function Modules**: Knowledge Graph, Question Management, AI Learning Reports, Image Recognition, etc.
- **Testing System**: Unit Tests + Integration Tests + End-to-End Tests

## 🏗️ Technical Architecture

### Backend
- **Framework**: FastAPI (modern, high-performance)
- **Database**: SQLite (lightweight, easy deployment)
- **ORM**: SQLAlchemy
- **AI Integration**: OpenClaw Agent System

### Frontend
- **Framework**: Vue 3 + TypeScript
- **UI Components**: Element Plus
- **Build Tool**: Vite
- **State Management**: Pinia

## 🎯 Four Major Technological Innovations

### 1. Four-Level Project Management System
```
Project → Phase → Plan → Task
```
Clear hierarchical structure supporting complex project decomposition and management.

### 2. Separated Responsibility Execution Model
```
BUILD-TEST (write tests) → TEST-RUN (run tests) → BUILD-CODE (fix bugs)
```
Prevents AI "cheating" in testing, ensuring test authenticity and code quality.

### 3. Intelligent Verification System
Each task is automatically verified upon completion, including:
- Syntax checking
- Test execution
- Documentation consistency checking
- Comprehensive scoring (≥80 points to pass)

### 4. Task Locking Mechanism
- Lock before execution → Execute → Unlock
- Lock before verification → Verify → Unlock
- Prevents concurrency conflicts, ensures execution safety

## 🚀 Quick Start

### One-Click Deployment (5 minutes)
```bash
# Clone the project
git clone https://github.com/Robin-Chen2025/autocraft-opensource.git
cd autocraft-opensource

# Run deployment script
bash scripts/deploy.sh
```

### Manual Deployment
```bash
# Backend startup
cd backend
pip install -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 9001

# Frontend startup
cd ..
npm install
npm run dev
```

### Access System
- **Frontend Interface**: http://localhost:8080
- **API Documentation**: http://localhost:9001/docs
- **Online Demo**: http://116.205.236.25:8080

## 👥 Who Should Use It?

### 👨‍💼 Product Managers / Entrepreneurs
- Have ideas but lack technical resources
- Want to quickly validate product ideas
- Need to control development costs and timelines

### 👨‍💻 Development Teams
- Liberate repetitive coding work
- Improve code quality and consistency
- Knowledge沉淀 and process standardization

### 🧠 Tech Enthusiasts
- Explore practical AI applications in real projects
- Learn modern development best practices
- Contribute to cutting-edge open source projects

### 🏢 Small and Medium Enterprises
- Reduce technical team costs
- Accelerate product iteration speed
- Improve project success rate

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
│   ├── router/              # Routing configuration
│   └── types/               # TypeScript types
├── openclaw-config/         # OpenClaw configuration
│   ├── patches/             # Patch files
│   └── setup-agents.sh      # Sub-agent creation script
└── scripts/                 # Deployment scripts
```

## 📝 Development Roadmap

### Completed ✅
- [x] Four-level project management structure
- [x] AI task execution engine
- [x] Automatic verification process
- [x] Task locking mechanism
- [x] Templated prompts

### In Progress 🔄
- [ ] Task execution log details page
- [ ] Real-time execution progress push

### Planned 📋
- [ ] **Issue Tracking System** - Problem tracking and solution management
- [ ] **Knowledge Base Management** - Knowledge points, knowledge graph management
- [ ] **Checklist System** - Task execution checklists
- [ ] **User Permission Management** - Multi-user, role permissions
- [ ] **Data Statistical Reports** - Project progress, execution efficiency statistics
- [ ] **Task Templates** - Common task template library
- [ ] **Batch Operations** - Batch creation, execution, verification
- [ ] **Webhook Notifications** - Task status change notifications
- [ ] **Docker Deployment** - One-click Docker deployment

## 📚 Documentation

- [System Operation Manual](docs/OPERATION_MANUAL.md) - Complete functionality usage guide
- [Deployment Guide](DEPLOYMENT.md) - Production environment deployment
- [API Reference Manual](docs/api-reference.md) - Complete API documentation
- [Template Writing Guide](docs/template-guide.md) - How to create custom templates

## 🤝 Contribution Guidelines

Welcome to submit Issues and Pull Requests!

### Development Guide
1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

### Contribution Types
- **Code Improvements**: Optimize existing features or add new features
- **Documentation Enhancement**: Improve usage documentation or add tutorials
- **Template Contributions**: Share execution templates for your domain
- **Case Studies**: Submit successful application cases

## 🌟 Community & Support

### Getting Help
- **GitHub Issues**: Report BUGs or request features
- **GitHub Discussions**: Technical discussions and Q&A
- **Mailing List**: Update notifications and important announcements

### Success Case Collection
We are collecting AutoCraft application cases from various industries. If you:
- Have completed actual projects using AutoCraft
- Have innovative applications in specific domains
- Have experience with performance optimization or feature expansion

**Contact us**, your case will help more people understand and use AutoCraft!

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [OpenClaw](https://github.com/openclaw/openclaw) - AI agent runtime
- [FastAPI](https://fastapi.tiangolo.com) - Modern API framework
- [Vue.js](https://vuejs.org) - Progressive frontend framework
- All contributors and users for their support

---

## 💭 Words from the Author

As a solutions consultant, I deeply understand the challenges faced by non-technical entrepreneurs and product managers when driving technology projects. AutoCraft was born to solve this very problem.

**We believe**: The future of work is human creativity plus AI execution. AutoCraft is the first step toward that future.

Welcome to join us in exploring new work modes in the AI era!

*—— AutoCraft Project Founder, Robin Chen*