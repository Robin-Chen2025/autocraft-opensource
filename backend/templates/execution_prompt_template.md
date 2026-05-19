# 🎯 项目归属

**目标项目**: {{project_name}}
**项目根目录**: {{project_path}}

---

⚠️ **首先读取以下skill文件获取你的角色定义和行为规范**：
- `~/.openclaw/workspace/skills/autocraft-dev/references/ac-agent-guide/SKILL.md`
- 根据任务类型（{{workflow_type}}），读取对应子文档

---

## 任务信息
- 编号: {{task_no}}
- 名称: {{task_name}}
- 类型: {{task_type}}
- 工作流: {{workflow_type}}

## 任务要求
{{requirements}}

## 输入文件
{{#each input_files}}
- {{this}}
{{/each}}

## 预期输出
{{expected_output}}

## 输出文件
{{#each expected_output_files}}
- {{this}}
{{/each}}

## 执行结果回传（必须）

任务完成后，将结果写入：`/tmp/autocraft_output/{{task_id}}_execution_result.json`

格式：
```json
{
  "success": true,
  "output_files": ["实际生成的文件路径"],
  "execution_log": "执行过程摘要",
  "key_changes": ["关键变更"],
  "issues": []
}
```

⚠️ `success` 仅表示执行是否完成，质量由验证子代理评判。
