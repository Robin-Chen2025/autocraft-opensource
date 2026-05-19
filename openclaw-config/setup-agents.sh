#!/bin/bash
# AutoCraft 子代理创建脚本
# 用于创建执行和验证子代理

set -e

echo "==================================="
echo " AutoCraft 子代理创建脚本"
echo "==================================="

# 检查 OpenClaw 是否安装
if ! command -v openclaw &> /dev/null; then
    echo "❌ OpenClaw 未安装"
    echo "请运行: npm install -g openclaw"
    exit 1
fi

echo "✅ OpenClaw 已安装"

# 创建代理列表
AGENTS=("ac-executor" "ac-validator" "ac-builder" "ac-planner")

for agent in "${AGENTS[@]}"; do
    echo ""
    echo "创建代理: $agent"
    
    # 检查是否已存在
    if [ -d "$HOME/.openclaw/agents/$agent" ]; then
        echo "⚠️  代理 $agent 已存在，跳过"
        continue
    fi
    
    # 创建代理
    openclaw agent create "$agent"
    echo "✅ 代理 $agent 创建成功"
    
    # 复制模型配置模板
    mkdir -p "$HOME/.openclaw/agents/$agent/agent"
    if [ -f "openclaw-config/agents/models.json.example" ]; then
        cp "openclaw-config/agents/models.json.example" "$HOME/.openclaw/agents/$agent/agent/models.json"
        echo "✅ 已复制模型配置模板"
        echo "⚠️  请编辑 models.json 填入您的 API Key"
    fi
done

echo ""
echo "==================================="
echo " 创建完成"
echo "==================================="
echo ""
echo "下一步操作:"
echo "1. 编辑各代理的模型配置:"
echo "   ~/.openclaw/agents/ac-executor/agent/models.json"
echo "   ~/.openclaw/agents/ac-validator/agent/models.json"
echo ""
echo "2. 填入您的 API Key"
echo ""
echo "3. 测试代理:"
echo "   openclaw agent run ac-executor --message '测试'"
