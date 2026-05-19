#!/bin/bash
# AutoCraft 子代理创建脚本
# 用于创建执行和验证子代理
# 
# 注意：模型配置由 OpenClaw 统一管理，无需单独配置

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
done

echo ""
echo "==================================="
echo " 创建完成"
echo "==================================="
echo ""
echo "已创建代理: ${AGENTS[*]}"
echo ""
echo "模型配置请在 OpenClaw 主配置中管理:"
echo "  ~/.openclaw/openclaw.json"
echo ""
echo "测试代理:"
echo "  openclaw agent run ac-executor --message '测试'"
