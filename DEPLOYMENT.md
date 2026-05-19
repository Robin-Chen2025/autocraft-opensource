# AutoCraft 部署指南

本文档介绍如何完整部署 AutoCraft 系统，包括 OpenClaw 环境配置和子代理创建。

## 📋 系统要求

- **操作系统**: Linux (推荐 Ubuntu 20.04+) / macOS
- **Python**: 3.10+
- **Node.js**: 18+
- **OpenClaw**: 最新版本

## 🚀 快速部署

### 1. 安装 OpenClaw

```bash
# 全局安装 OpenClaw
npm install -g openclaw

# 验证安装
openclaw --version
```

### 2. 克隆项目

```bash
git clone https://github.com/your-username/autocraft.git
cd autocraft
```

### 3. 后端部署

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

### 4. 前端部署

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 或生产构建
npm run build
```

## 🔧 OpenClaw 子代理配置

### ⚠️ 重要：应用补丁

AutoCraft 需要 OpenClaw 补丁来修复 `--agent` 与 `--session-id explicit` 冲突问题。

```bash
# 应用补丁
bash openclaw-config/patches/apply-patch.sh
```

**补丁作用：** 使 explicit session 能正确实现会话隔离，确保每个任务使用独立的会话。

详见 [openclaw-config/patches/README.md](openclaw-config/patches/README.md)

### 子代理列表

AutoCraft 依赖以下 OpenClaw 子代理：

| 代理 ID | 用途 | 推荐模型 |
|---------|------|----------|
| `ac-executor` | 任务执行 | GLM-5, DeepSeek-V3 |
| `ac-validator` | 任务验证 | DeepSeek-V4-Pro, GLM-5 |
| `ac-builder` | 代码构建 | GLM-5 |
| `ac-planner` | 任务规划 | GLM-5 |

### 创建子代理

```bash
# 创建执行代理
openclaw agent create ac-executor

# 创建验证代理
openclaw agent create ac-validator

# 创建构建代理
openclaw agent create ac-builder

# 创建规划代理
openclaw agent create ac-planner
```

### 配置模型

编辑 `~/.openclaw/agents/ac-executor/agent/models.json`：

```json
{
  "providers": {
    "deepseek": {
      "baseUrl": "https://api.deepseek.com/v1",
      "api": "openai-completions",
      "apiKey": "YOUR_DEEPSEEK_API_KEY",
      "models": [
        {
          "id": "deepseek-chat",
          "name": "DeepSeek Chat",
          "contextWindow": 64000,
          "maxTokens": 8192,
          "input": ["text"],
          "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}
        }
      ]
    },
    "zhipu": {
      "baseUrl": "https://open.bigmodel.cn/api/paas/v4",
      "api": "openai-completions",
      "apiKey": "YOUR_ZHIPU_API_KEY",
      "models": [
        {
          "id": "glm-4",
          "name": "GLM-4",
          "contextWindow": 128000,
          "maxTokens": 8192,
          "input": ["text"],
          "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}
        }
      ]
    }
  }
}
```

## 📝 模型提供商配置

### DeepSeek

```json
{
  "deepseek": {
    "baseUrl": "https://api.deepseek.com/v1",
    "api": "openai-completions",
    "apiKey": "sk-xxxxxxxx",
    "models": [
      {"id": "deepseek-chat", "contextWindow": 64000, "maxTokens": 8192},
      {"id": "deepseek-reasoner", "contextWindow": 64000, "maxTokens": 8192, "reasoning": true}
    ]
  }
}
```

### 智谱 AI (GLM)

```json
{
  "zhipu": {
    "baseUrl": "https://open.bigmodel.cn/api/paas/v4",
    "api": "openai-completions",
    "apiKey": "xxxxxxxx",
    "models": [
      {"id": "glm-4", "contextWindow": 128000, "maxTokens": 8192},
      {"id": "glm-4-flash", "contextWindow": 128000, "maxTokens": 8192}
    ]
  }
}
```

### SiliconFlow

```json
{
  "siliconflow": {
    "baseUrl": "https://api.siliconflow.cn/v1",
    "api": "openai-completions",
    "apiKey": "sk-xxxxxxxx",
    "models": [
      {"id": "Qwen/Qwen2.5-72B-Instruct", "contextWindow": 32768, "maxTokens": 8192}
    ]
  }
}
```

## 🌐 生产部署

### 使用 systemd (Linux)

创建服务文件 `/etc/systemd/system/autocraft-backend.service`：

```ini
[Unit]
Description=AutoCraft Backend
After=network.target

[Service]
Type=simple
User=autocraft
WorkingDirectory=/opt/autocraft/backend
ExecStart=/opt/autocraft/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 9001
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable autocraft-backend
sudo systemctl start autocraft-backend
```

### 使用 Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 9001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9001"]
```

```bash
docker build -t autocraft-backend .
docker run -d -p 9001:9001 autocraft-backend
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://127.0.0.1:9001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /opt/autocraft/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

## ✅ 验证部署

```bash
# 检查后端
curl http://localhost:9001/health

# 检查 API 文档
open http://localhost:9001/docs

# 测试子代理
openclaw agent run ac-executor --message "测试消息"
```

## 🔒 安全建议

1. **API Key 保护**：不要将 API Key 提交到代码仓库
2. **环境变量**：使用 `.env` 文件管理敏感配置
3. **访问控制**：生产环境建议添加认证中间件
4. **HTTPS**：生产环境使用 HTTPS
5. **防火墙**：限制端口访问

## 🐛 常见问题

### Q: OpenClaw 命令找不到

```bash
# 确保 OpenClaw 在 PATH 中
export PATH="$HOME/.npm-global/bin:$PATH"

# 或添加到 .bashrc
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
```

### Q: 子代理调用失败

检查：
1. 子代理是否已创建 (`openclaw agent list`)
2. models.json 配置是否正确
3. API Key 是否有效

### Q: 数据库锁定

```bash
# 重启后端服务
pkill -f uvicorn
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

## 📚 相关文档

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [FastAPI 文档](https://fastapi.tiangolo.com)
- [Vue 3 文档](https://vuejs.org)
