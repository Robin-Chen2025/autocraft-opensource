#!/bin/bash
# OpenClaw 补丁应用脚本
# 修复 --agent 与 --session-id explicit 冲突问题

set -e

echo "==================================="
echo " OpenClaw 补丁应用"
echo "==================================="

# 定位 OpenClaw 安装目录
OPENCLAW_DIR="$HOME/.npm-global/lib/node_modules/openclaw/dist"
PATCH_DIR="$(dirname "$0")"

if [ ! -d "$OPENCLAW_DIR" ]; then
    echo "❌ OpenClaw 未找到: $OPENCLAW_DIR"
    exit 1
fi

echo "✅ OpenClaw 目录: $OPENCLAW_DIR"

# 补丁文件
PATCH_FILE="$PATCH_DIR/live-model-switch-DHqPme9r.js"
TARGET_FILE="$OPENCLAW_DIR/live-model-switch-DHqPme9r.js"
BACKUP_FILE="$TARGET_FILE.bak"

if [ ! -f "$PATCH_FILE" ]; then
    echo "❌ 补丁文件不存在: $PATCH_FILE"
    exit 1
fi

echo ""
echo "补丁说明:"
echo "  修复 --agent 与 --session-id explicit 冲突问题"
echo "  使 explicit session 能正确实现会话隔离"
echo ""

# 检查是否已应用
if cmp -s "$PATCH_FILE" "$TARGET_FILE"; then
    echo "✅ 补丁已应用，无需重复操作"
    exit 0
fi

# 备份原文件
if [ ! -f "$BACKUP_FILE" ]; then
    echo "备份原文件..."
    cp "$TARGET_FILE" "$BACKUP_FILE"
    echo "✅ 已备份: $BACKUP_FILE"
else
    echo "⚠️  备份文件已存在: $BACKUP_FILE"
fi

# 应用补丁
echo "应用补丁..."
cp "$PATCH_FILE" "$TARGET_FILE"
echo "✅ 补丁已应用"

# 重启 Gateway
echo ""
echo "重启 OpenClaw Gateway..."
openclaw gateway restart 2>/dev/null || echo "⚠️  请手动重启: openclaw gateway restart"

echo ""
echo "==================================="
echo " 补丁应用完成"
echo "==================================="
echo ""
echo "验证方法:"
echo "  openclaw agent --agent ac-glm5 --session-id explicit:test_001 --message '测试'"
