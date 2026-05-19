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
openclaw agent create ac-executor
openclaw agent create ac-validator
openclaw agent create ac-builder
openclaw agent create ac-planner
```

### 2. 配置模型

复制模板到代理目录：

```bash
cp openclaw-config/agents/models.json.example ~/.openclaw/agents/ac-executor/agent/models.json
cp openclaw-config/agents/models.json.example ~/.openclaw/agents/ac-validator/agent/models.json
```

### 3. 填入 API Key

编辑 `~/.openclaw/agents/ac-executor/agent/models.json`，将 `YOUR_DEEPSEEK_API_KEY` 等占位符替换为实际的 API Key。

### 4. 验证配置

```bash
openclaw agent run ac-executor --message "你好"
```

## 支持的模型提供商

- **DeepSeek**: https://platform.deepseek.com
- **智谱 AI**: https://open.bigmodel.cn
- **SiliconFlow**: https://siliconflow.cn
- **OpenAI**: https://platform.openai.com

## 自动配置脚本

```bash
bash openclaw-config/setup-agents.sh
```

该脚本会自动创建所有需要的子代理并复制配置模板。

## 模型选择建议

| 用途 | 推荐模型 | 原因 |
|------|----------|------|
| 任务执行 | GLM-4, DeepSeek-Chat | 性价比高，响应快 |
| 任务验证 | DeepSeek-Reasoner | 推理能力强 |
| 代码生成 | GLM-4, GPT-4 | 代码质量高 |
| 任务规划 | GLM-4 | 上下文窗口大 |
