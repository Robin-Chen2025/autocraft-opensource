.PHONY: help install dev build clean test

help:
	@echo "AutoCraft 命令"
	@echo ""
	@echo "  make install    - 安装依赖"
	@echo "  make dev        - 启动开发服务器"
	@echo "  make build      - 构建生产版本"
	@echo "  make clean      - 清理构建文件"
	@echo "  make test       - 运行测试"

install:
	@echo "安装后端依赖..."
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "安装前端依赖..."
	npm install
	@echo "创建子代理..."
	bash openclaw-config/setup-agents.sh

dev-backend:
	cd backend && . venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 9001 --reload

dev-frontend:
	npm run dev

dev:
	@echo "请分别在两个终端运行:"
	@echo "  make dev-backend"
	@echo "  make dev-frontend"

build:
	npm run build
	@echo "构建完成: dist/"

clean:
	rm -rf backend/__pycache__ backend/**/__pycache__
	rm -rf node_modules dist
	rm -f backend/tasks.db

test:
	cd backend && . venv/bin/activate && pytest
