<!-- TASK_METADATA_START
{
  "task_id": {{task_id}},
  "task_no": "{{task_no}}",
  "task_name": {{task_name_json}},
  "task_type": {{task_type_json}},
  "workflow_type": {{workflow_type_json}},
  "project_path": {{project_path_json}},
  "project_name": {{project_name_json}},
  "input_files": {{input_files_json}},
  "requirements": {{requirements_json}},
  "expected_output": {{expected_output_json}},
  "expected_output_files": {{expected_output_files_json}},
  "deliverables": {{deliverables_json}},
  "source_file": {{source_file_json}}
}
TASK_METADATA_END -->

# 🎯 项目归属

**目标项目**: {{project_name}}
**项目根目录**: {{project_path}}

---

⚠️ **首先读取以下skill文件获取你的角色定义和验证规范**：
- `~/.openclaw/workspace/skills/autocraft-dev/references/ac-agent-guide/SKILL.md`
- 读取 `references/ac-agent-guide/validator-guide.md`

---

## 任务信息
- 编号: {{task_no}} | 名称: {{task_name}} | 类型: {{task_type}} | 工作流: {{workflow_type}}
- 项目路径: {{project_path}}
- 执行模型: {{model_used}} | 会话: {{session_id}}

## 任务要求
{{requirements}}

## 输入文件（设计文档）
{{#each input_files}}
- {{this}}
{{/each}}

## 预期输出
{{expected_output}}

## 预期输出文件
{{#each expected_output_files}}
- {{this}}
{{/each}}

## 执行产出物（待验证）
{{#each output_files}}
- {{this}}
{{/each}}

## 执行日志摘要
{{execution_log_summary}}

## 验证结果回传（必须）

验证完成后，将结果写入：`/tmp/autocraft_output/{{task_id}}_verification_result.json`

格式：
```json
{
  "verification_success": true,
  "dimension_results": {"完整性":"PASS","正确性":"PASS","可运行性":"PASS","一致性":"PASS","安全性":"PASS","架构合理性":"PASS"},
  "issues_found": [],
  "improvements_suggested": []
}
```

⛔ 任一维度FAIL → `verification_success: false`
