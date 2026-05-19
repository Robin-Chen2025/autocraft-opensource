# OpenClaw 补丁：--agent 与 --session-id explicit 冲突修复

**日期：** 2026-04-28
**版本：** OpenClaw 2026.4.15 (041266a)
**文件：** `live-model-switch-DHqPme9r.js`

---

## 问题描述

使用 `openclaw agent --agent ac-glm5 --session-id explicit:flowticket_xxx --message "..."` 时，`--agent` 参数会覆盖 `--session-id`，导致所有任务都路由到同一个 `agent:ac-glm5:main` 会话，无法实现会话隔离。

## 根因分析

文件 `live-model-switch-DHqPme9r.js` 中的 `resolveSessionKeyForRequest` 函数：

```js
// 原始逻辑：--agent 直接生成 main session key，跳过 --session-id
const explicitSessionKey = opts.sessionKey?.trim() || resolveExplicitAgentSessionKey({
    cfg: opts.cfg,
    agentId: opts.agentId
});
```

当 `--agent` 传入时，`resolveExplicitAgentSessionKey` 返回 `agent:ac-glm5:main`，使 `explicitSessionKey` 非空，后续 `--session-id` 的处理逻辑被跳过（条件 `!explicitSessionKey` 为 false）。

## 修复方案

当同时传入 `--session-id` 和 `--agent` 时，优先用 `--session-id` 构建 explicit session key：

```js
const explicitSessionKey = opts.sessionKey?.trim() 
    || (opts.sessionId ? buildExplicitSessionIdSessionKey({
        sessionId: opts.sessionId,
        agentId: opts.agentId
    }) : null) 
    || resolveExplicitAgentSessionKey({
        cfg: opts.cfg,
        agentId: opts.agentId
    });
```

**优先级链：**
1. `opts.sessionKey`（最高，直接指定）
2. `opts.sessionId` → 构建 `agent:{agentId}:explicit:{sessionId}`
3. `--agent` → 回退到 `agent:{agentId}:main`

## 修改前

```js
const explicitSessionKey = opts.sessionKey?.trim() || resolveExplicitAgentSessionKey({
    cfg: opts.cfg,
    agentId: opts.agentId
});
```

## 修改后

```js
const explicitSessionKey = opts.sessionKey?.trim() || (opts.sessionId ? buildExplicitSessionIdSessionKey({
    sessionId: opts.sessionId,
    agentId: opts.agentId
}) : null) || resolveExplicitAgentSessionKey({
    cfg: opts.cfg,
    agentId: opts.agentId
});
```

## 验证结果

| 测试项 | 命令 | 结果 |
|--------|------|------|
| 模型指定 | `--agent ac-glm5 --session-id explicit:test_001` | ✅ 使用 GLM-5.1 |
| 会话隔离 | 不同 session-id 创建不同会话 | ✅ 不再走 main |
| 多轮对话 | 同一 session-id 第二次调用 | ✅ 历史上下文保留 |

## 注意事项

- ⚠️ **OpenClaw 升级后此补丁会丢失**，需要重新应用
- 备份文件：`live-model-switch-DHqPme9r.js.bak`（原始未修改版本）
- 修补文件：`live-model-switch-DHqPme9r.js`（已修改版本）
- 修改后需重启 Gateway：`openclaw gateway restart`

## 应用补丁

```bash
# 1. 备份原文件
cp ~/.npm-global/lib/node_modules/openclaw/dist/live-model-switch-DHqPme9r.js \
   ~/.npm-global/lib/node_modules/openclaw/dist/live-model-switch-DHqPme9r.js.bak

# 2. 复制补丁文件
cp /home/robin/.openclaw/workspace/projects/openclaw-patches/live-model-switch-DHqPme9r.js \
   ~/.npm-global/lib/node_modules/openclaw/dist/live-model-switch-DHqPme9r.js

# 3. 重启 Gateway
openclaw gateway restart
```

## 恢复原始版本

```bash
cp ~/.npm-global/lib/node_modules/openclaw/dist/live-model-switch-DHqPme9r.js.bak \
   ~/.npm-global/lib/node_modules/openclaw/dist/live-model-switch-DHqPme9r.js
openclaw gateway restart
```
