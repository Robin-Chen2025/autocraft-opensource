# OpenClaw 配置说明

AutoCraft 使用 OpenClaw 作为 AI 子代理运行时，需要正确配置子代理。

## 子代理列表

| 代理 ID | 用途 | 说明 |
|---------|------|------|
| `ac-executor` | 任务执行 | 执行开发任务 |
| `ac-validator` | 任务验证 | 验证任务完成质量 |
| `ac-builder` | 代码构建 | 代码编写和重构 |
| `ac-planner` | 任务规划 | 拆解复杂任务 |

## 配置步骤

### 1. 创建子代理

```bash
bash openclaw-config/setup-agents.sh
```

或手动创建：

```bash
openclaw agent create ac-executor
openclaw agent create ac-validator
openclaw agent create ac-builder
openclaw agent create ac-planner
```

### 2. 模型配置

模型配置由 OpenClaw 统一管理，编辑 `~/.openclaw/openclaw.json`：

```json
{
  "agents": {
    "ac-executor": {
      "model": "your-model-id"  // 替换为实际使用的模型
    },
    "ac-validator": {
      "model": "your-model-id"  // 替换为实际使用的模型
    }
  }
}
```

### 3. 验证配置

```bash
openclaw agent run ac-executor --message "你好"
```

## 重要：应用补丁

AutoCraft 需要应用 OpenClaw 补丁才能正常工作：

```bash
bash openclaw-config/patches/apply-patch.sh
```

详见 [patches/README.md](patches/README.md)

## 模型选择建议

| 用途 | 推荐特性 | 说明 |
|------|----------|------|
| 任务执行 | 性价比高、响应快 | 通用对话模型 |
| 任务验证 | 推理能力强 | 推理增强模型 |
| 代码生成 | 代码质量高 | 代码专用模型 |
| 任务规划 | 上下文窗口大 | 长上下文模型 |
