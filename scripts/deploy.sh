#!/bin/bash
# AutoCraft 一键部署脚本

set -e

echo "==================================="
echo " AutoCraft 一键部署"
echo "==================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装"
    exit 1
fi
echo "✅ npm: $(npm --version)"

# 检查 OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo ""
    echo "⚠️  OpenClaw 未安装，正在安装..."
    npm install -g openclaw
fi
echo "✅ OpenClaw: $(openclaw --version 2>/dev/null || echo '已安装')"

# 后端部署
echo ""
echo "=== 后端部署 ==="
cd backend

if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "安装依赖..."
pip install -r requirements.txt -q

echo "初始化数据库..."
python init_db.py

echo "✅ 后端部署完成"

# 创建子代理
echo ""
echo "=== 创建 OpenClaw 子代理 ==="
cd ..
bash openclaw-config/setup-agents.sh

# 前端部署
echo ""
echo "=== 前端部署 ==="
echo "安装依赖..."
npm install

echo "✅ 前端部署完成"

# 完成
echo ""
echo "==================================="
echo " 部署完成！"
echo "==================================="
echo ""
echo "启动服务:"
echo "  后端: cd backend && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 9001 --reload"
echo "  前端: npm run dev"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:5173"
echo "  API:  http://localhost:9001/docs"
