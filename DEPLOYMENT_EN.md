# AutoCraft Deployment Guide

[中文文档](DEPLOYMENT.md)

This guide explains how to fully deploy the AutoCraft system, including OpenClaw environment configuration and sub-agent creation.

## 📋 System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended) / macOS
- **Python**: 3.10+
- **Node.js**: 18+
- **OpenClaw**: Latest version

## 🚀 Quick Deployment

### 1. Install OpenClaw

```bash
# Install OpenClaw globally
npm install -g openclaw

# Verify installation
openclaw --version
```

### 2. Clone Project

```bash
git clone https://github.com/your-username/autocraft.git
cd autocraft
```

### 3. Backend Deployment

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start service
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

### 4. Frontend Deployment

```bash
# Install dependencies
npm install

# Development mode
npm run dev

# Or production build
npm run build
```

## 🔧 OpenClaw Sub-Agent Configuration

### ⚠️ Important: Apply Patches

AutoCraft requires OpenClaw patches to fix the `--agent` and `--session-id explicit` conflict issue.

```bash
# Apply patches
bash openclaw-config/patches/apply-patch.sh
```

**Patch Purpose**: Enable explicit sessions to correctly achieve session isolation, ensuring each task uses an independent session.

See [openclaw-config/patches/README.md](openclaw-config/patches/README.md) for details.

### Sub-Agent List

AutoCraft depends on the following OpenClaw sub-agents:

| Agent ID | Purpose | Recommended Model |
|----------|---------|-------------------|
| `ac-executor` | Task execution | General-purpose conversational model recommended |
| `ac-validator` | Task verification | Reasoning-enhanced model recommended |
| `ac-builder` | Code building | Strong coding ability model recommended |
| `ac-planner` | Task planning | Large context window model recommended |

### Create Sub-Agents

```bash
# Create executor agent
openclaw agent create ac-executor

# Create validator agent
openclaw agent create ac-validator

# Create builder agent
openclaw agent create ac-builder

# Create planner agent
openclaw agent create ac-planner
```

### Configure Models

Edit `~/.openclaw/agents/ac-executor/agent/models.json`:

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

## 📝 Model Provider Configuration

### Model Provider Examples

Here are some common model provider configuration examples. Choose according to your actual situation:

#### DeepSeek

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

### Zhipu AI

Example configuration, adjust according to actual API:

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

## 🌐 Production Deployment

### Using systemd (Linux)

Create service file `/etc/systemd/system/autocraft-backend.service`:

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

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable autocraft-backend
sudo systemctl start autocraft-backend
```

### Using Docker

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

### Using Nginx Reverse Proxy

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

## ✅ Verify Deployment

```bash
# Check backend
curl http://localhost:9001/health

# Check API docs
open http://localhost:9001/docs

# Test sub-agent
openclaw agent run ac-executor --message "test message"
```

## 🔒 Security Recommendations

1. **API Key Protection**: Never commit API Keys to code repositories
2. **Environment Variables**: Use `.env` files for sensitive configuration
3. **Access Control**: Add authentication middleware in production
4. **HTTPS**: Use HTTPS in production environments
5. **Firewall**: Restrict port access

## 🐛 Troubleshooting

### Q: OpenClaw command not found

```bash
# Ensure OpenClaw is in PATH
export PATH="$HOME/.npm-global/bin:$PATH"

# Or add to .bashrc
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
```

### Q: Sub-agent call failed

Check:
1. Sub-agent created (`openclaw agent list`)
2. models.json configured correctly
3. API Key is valid

### Q: Database locked

```bash
# Restart backend service
pkill -f uvicorn
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

## 📚 Related Documentation

- [OpenClaw Official Docs](https://docs.openclaw.ai)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Vue 3 Documentation](https://vuejs.org)