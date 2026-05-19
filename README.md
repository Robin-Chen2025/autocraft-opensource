# AutoCraft - AI驱动的项目执行平台

[English](README_EN.md) | [中文](README.md)

> **🚀 让不懂代码的产品经理也能驱动复杂软件开发项目，效率提升3-6倍**

AutoCraft是一个将人类项目管理智慧与AI自动执行能力完美结合的平台。**人类专注设计决策，AI专注编码执行**，让创意快速变成可运行的产品。

## ✨ 核心价值

### 🎯 解决什么问题？
- **产品经理有创意但没技术团队？**
- **开发项目周期长、沟通成本高？**
- **想验证想法但不想投入大量资源？**

### 💡 提供什么方案？
- **人类**：专注于设计、决策、创意
- **AI**：自动完成编码、测试、验证
- **结果**：更快、更便宜、质量更高的产品

## 📊 真实案例：10天建成完整教育平台

我们使用AutoCraft在**10天内**完成了DeepTutor-Lite教育平台的完整开发：

### 执行数据
```
📈 项目规模：
   计划单：19个
   任务数：71个
   成功数：70个（99%成功率）

🔧 质量指标：
   发现程序BUG：7个（全部自动修复）
   测试覆盖率：100%（L1+L2+L3）
   人工干预：仅3次关键决策

⏱️ 效率对比：
   传统估计：1-2个月
   AutoCraft：10天（3-6倍提升）
```

### 技术产出
- **后端**：FastAPI + SQLite（完整REST API）
- **前端**：Vue 3 + TypeScript（现代化界面）
- **功能模块**：知识图谱、题目管理、AI学习报告、图片识别等
- **测试体系**：单元测试 + 集成测试 + 端到端测试

## 🏗️ 技术架构

### 后端
- **框架**: FastAPI（现代化、高性能）
- **数据库**: SQLite（轻量级、易部署）
- **ORM**: SQLAlchemy
- **AI集成**: OpenClaw Agent系统

### 前端
- **框架**: Vue 3 + TypeScript
- **UI组件**: Element Plus
- **构建工具**: Vite
- **状态管理**: Pinia

## 🎯 四大技术创新

### 1. 四级项目管理体系
```
项目(Project) → 阶段(Phase) → 计划(Plan) → 任务(Task)
```
清晰的层级结构，支持复杂项目的拆解和管理。

### 2. 职责分离的执行模型
```
BUILD-TEST（写测试） → TEST-RUN（跑测试） → BUILD-CODE（修BUG）
```
防止AI在测试中"作弊"，确保测试的真实性和代码质量。

### 3. 智能验证体系
每个任务完成后自动进行验证，包括：
- 语法检查
- 测试运行
- 文档一致性检查
- 综合评分（≥80分通过）

### 4. 任务锁定机制
- 执行前锁定 → 执行 → 解锁
- 验证前锁定 → 验证 → 解锁
- 防止并发冲突，确保执行安全

## 🚀 快速开始

### 一键部署（5分钟）
```bash
# 克隆项目
git clone https://github.com/Robin-Chen2025/autocraft-opensource.git
cd autocraft-opensource

# 运行部署脚本
bash scripts/deploy.sh
```

### 手动部署
```bash
# 后端启动
cd backend
pip install -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 9001

# 前端启动
cd ..
npm install
npm run dev
```

### 访问系统
- **前端界面**：http://localhost:8080
- **API文档**：http://localhost:9001/docs

## 👥 谁适合使用？

### 👨‍💼 产品经理/创业者
- 有创意但缺乏技术资源
- 想快速验证产品想法
- 需要控制开发成本和时间

### 👨‍💻 开发团队
- 解放重复性编码工作
- 提高代码质量和一致性
- 知识沉淀和流程标准化

### 🧠 技术爱好者
- 探索AI在实际项目中的应用
- 学习现代开发最佳实践
- 参与前沿开源项目贡献

### 🏢 中小企业
- 降低技术团队成本
- 加速产品迭代速度
- 提高项目成功率

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
│   ├── api/                 # 调用
│   ├── components/          # Vue 组件
│   ├── views/               # 页面视图
│   ├── router/              # 路由配置
│   └── types/               # TypeScript 类型
├── openclaw-config/         # OpenClaw 配置
│   ├── patches/             # 补丁文件
│   └── setup-agents.sh      # 子代理创建脚本
└── scripts/                 # 部署脚本
```

## 📝 开发路线图

### 已完成 ✅
- [x] **四级项目管理结构** - 项目→阶段→计划→任务四级体系
- [x] **AI 任务执行引擎** - 集成OpenClaw AI代理自动执行
- [x] **自动验证流程** - 任务完成后智能验证
- [x] **任务锁定机制** - 防止并发冲突，确保执行安全
- [x] **模板化提示词** - 可配置的执行和验证模板
- [x] **职责分离模型** - BUILD-TEST/TEST-RUN/BUILD-CODE分离
- [x] **真实案例验证** - DeepTutor-Lite项目完整开发（10天，99%成功率）

### 进行中 🔄
- [ ] **任务执行日志详情页** - 详细的执行过程追踪
- [ ] **执行进度实时推送** - WebSocket实时状态更新
- [ ] **多语言支持** - 国际化界面和文档

### 短期计划 (v2.1.0) 📋
- [ ] **Issue 跟踪系统** - 问题跟踪与解决方案管理
- [ ] **知识库管理** - 知识点、知识图谱管理
- [ ] **检查清单系统** - 任务执行标准化检查清单
- [ ] **用户权限管理** - 多用户、角色权限控制
- [ ] **数据统计报表** - 项目进度、执行效率统计分析

### 中期计划 (v3.0.0) 🚀
- [ ] **任务模板库** - 常用任务模板快速复用
- [ ] **批量操作功能** - 批量创建、执行、验证任务
- [ ] **Webhook 通知系统** - 任务状态变更实时通知
- [ ] **Docker 部署方案** - 一键Docker容器化部署
- [ ] **云原生支持** - Kubernetes部署和运维

### 长期愿景 🌟
- [ ] **智能任务拆分** - AI自动分析需求并拆解任务
- [ ] **自适应学习** - 系统根据历史执行优化模板
- [ ] **联邦学习支持** - 跨项目知识共享和学习
- [ ] **多模态任务支持** - 图像、音频等非文本任务

## 📚 文档

- [系统操作手册](docs/OPERATION_MANUAL.md) - 完整功能使用指南
- [部署指南](DEPLOYMENT.md) - 生产环境部署
- [API参考手册](docs/api-reference.md) - 完整API文档
- [模板编写指南](docs/template-guide.md) - 如何创建自定义模板

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发指南
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 贡献类型
- **代码改进**：优化现有功能或添加新功能
- **文档完善**：改进使用文档或添加教程
- **模板贡献**：分享你领域的执行模板
- **案例分享**：提交成功应用案例

## 🌟 社区与支持

### 获取帮助
- **GitHub Issues**：报告BUG或请求功能
- **GitHub Discussions**：技术讨论和问题解答
- **邮件列表**：更新通知和重要公告

### 成功案例征集
我们正在收集各行各业的AutoCraft应用案例。如果你：
- 使用AutoCraft完成了实际项目
- 在特定领域有创新应用
- 有性能优化或功能扩展的经验

**欢迎联系我们**，你的案例将帮助更多人了解和使用AutoCraft！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) - AI 代理运行时
- [FastAPI](https://fastapi.tiangolo.com) - 现代化 API 框架
- [Vue.js](https://vuejs.org) - 渐进式前端框架
- 所有贡献者和用户的支持

---

## 💭 作者的话

作为一名解决方案顾问，我深刻理解非技术背景的创业者和产品经理在驱动技术项目时面临的挑战。AutoCraft正是为了解决这个问题而生。

**我们相信**：未来的工作模式，是人类的创造力加上AI的执行力。AutoCraft就是这个未来的第一步。

欢迎加入我们，一起探索AI时代的全新工作模式！

*—— AutoCraft项目发起人，Robin Chen*