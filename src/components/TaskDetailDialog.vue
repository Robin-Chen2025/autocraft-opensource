<template>
  <el-dialog
    v-model="dialogVisible"
    title="任务详情"
    width="800px"
    destroy-on-close
    class="task-detail-dialog"
  >
    <template v-if="task">
      <!-- 基础信息 -->
      <el-descriptions title="基础信息" :column="2" border>
        <el-descriptions-item label="ID" :span="1">
          {{ task.id }}
        </el-descriptions-item>
        <el-descriptions-item label="任务单号" :span="1">
          {{ task.task_no }}
        </el-descriptions-item>
        <el-descriptions-item label="任务名称" :span="2">
          {{ task.task_name }}
        </el-descriptions-item>
        <el-descriptions-item label="状态" :span="1">
          <el-tag :type="getStatusType(task.status)">{{ task.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="优先级" :span="1">
          <el-tag :type="getPriorityType(task.priority)">{{ task.priority }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="计划日期" :span="1">
          {{ formatDate(task.plan_date) }}
        </el-descriptions-item>
        <el-descriptions-item label="计划完成时间" :span="1">
          {{ formatDateTime(task.plan_complete_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="1">
          {{ formatDateTime(task.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间" :span="1">
          {{ formatDateTime(task.updated_at) }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 执行步骤 -->
      <div class="execution-steps-card mt-20">
        <div class="card-title">执行步骤</div>
        <div class="steps-content">
          <template v-if="task.execution_steps && task.execution_steps.trim()">
            <div
              v-for="(step, index) in parsedExecutionSteps"
              :key="index"
              class="step-item"
            >
              <span class="step-number">{{ index + 1 }}.</span>
              <span class="step-text">{{ step }}</span>
            </div>
          </template>
          <template v-else>
            <div class="empty-steps">暂无执行步骤</div>
          </template>
        </div>
      </div>

      <!-- 执行信息 -->
      <el-descriptions title="执行信息" :column="1" border class="mt-20">
        <el-descriptions-item label="执行人">
          {{ task.executor || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="执行日期">
          {{ formatDate(task.execution_date) }}
        </el-descriptions-item>

        <!-- 执行时间组 -->
        <el-descriptions-item label="执行开始时间">
          {{ formatDateTime(task.exec_start_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="预计执行完成时间">
          {{ formatDateTime(task.exec_estimated_complete) }}
        </el-descriptions-item>
        <el-descriptions-item label="实际执行完成时间">
          {{ formatDateTime(task.exec_complete_time) }}
        </el-descriptions-item>

        <el-descriptions-item label="预期结果">
          <el-input
            v-model="task.expected_result"
            type="textarea"
            :rows="3"
            readonly
            resize="none"
          />
        </el-descriptions-item>
        <el-descriptions-item label="执行日志">
          <el-input
            v-model="task.execution_log"
            type="textarea"
            :rows="3"
            readonly
            resize="none"
          />
        </el-descriptions-item>
        <el-descriptions-item label="输出结果">
          <el-input
            v-model="task.output_result"
            type="textarea"
            :rows="3"
            readonly
            resize="none"
          />
        </el-descriptions-item>
      </el-descriptions>

      <!-- 验证信息 -->
      <el-descriptions title="验证信息" :column="2" border class="mt-20">
        <el-descriptions-item label="验证结论" :span="1">
          <el-tag :type="getVerificationType(task.verification_result)" class="verification-tag">
            {{ task.verification_result || '待验证' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="验证人" :span="1">
          {{ task.verifier || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="验证时间" :span="2">
          {{ formatDateTime(task.verification_time) }}
        </el-descriptions-item>

        <!-- 验证时间组 -->
        <el-descriptions-item label="验证开始时间" :span="1">
          {{ formatDateTime(task.verify_start_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="预计验证完成时间" :span="1">
          {{ formatDateTime(task.verify_estimated_complete) }}
        </el-descriptions-item>
        <el-descriptions-item label="实际验证完成时间" :span="1">
          {{ formatDateTime(task.verify_complete_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="验证日志" :span="2">
          <el-input
            v-model="task.verification_log"
            type="textarea"
            :rows="3"
            readonly
            resize="none"
          />
        </el-descriptions-item>
      </el-descriptions>
    </template>

    <template #footer>
      <el-button @click="dialogVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Task } from '../api/tasks'

// 解析执行步骤（按分号拆分）
const parsedExecutionSteps = computed(() => {
  if (!props.task?.execution_steps) return []
  const steps = props.task.execution_steps.split(';').filter(step => step.trim())
  return steps.map(step => step.trim())
})

interface Props {
  task: Task | null
  visible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 获取状态标签类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    '新建': 'info',
    '待执行': 'warning',
    '进行中': 'primary',
    '待验证': 'warning',
    '完成': 'success',
    '失败': 'danger'
  }
  return map[status] || 'info'
}

// 获取优先级标签类型
const getPriorityType = (priority: string) => {
  const map: Record<string, string> = {
    '高': 'danger',
    '中': 'warning',
    '低': 'success'
  }
  return map[priority] || 'info'
}

// 获取验证结论标签类型
const getVerificationType = (result: string | null | undefined) => {
  const map: Record<string, string> = {
    '通过': 'success',
    '不通过': 'danger',
    '待验证': 'info'
  }
  return map[result || ''] || 'info'
}

// 格式化日期 (YYYY-MM-DD)
const formatDate = (dateStr: string | null | undefined) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  return date.toISOString().split('T')[0]
}

// 格式化日期时间 (YYYY-MM-DD HH:mm)
const formatDateTime = (dateStr: string | null | undefined) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}
</script>

<style scoped>
.task-detail-dialog :deep(.el-dialog__header) {
  background: linear-gradient(90deg, rgba(0, 212, 255, 0.1) 0%, transparent 100%);
  border-bottom: 1px solid #30363d;
  padding: 20px;
  margin-right: 0;
}

.task-detail-dialog :deep(.el-dialog__title) {
  color: #00d4ff;
  font-weight: 600;
}

.task-detail-dialog :deep(.el-dialog__body) {
  background: linear-gradient(145deg, #1a1f2e 0%, #21283a 100%);
  padding: 20px;
  max-height: 600px;
  overflow-y: auto;
}

.task-detail-dialog :deep(.el-dialog__footer) {
  background: linear-gradient(145deg, #1a1f2e 0%, #21283a 100%);
  border-top: 1px solid #30363d;
  padding: 15px 20px;
}

.task-detail-dialog :deep(.el-descriptions__header) {
  color: #00d4ff;
  font-weight: 600;
  margin-bottom: 10px;
}

.task-detail-dialog :deep(.el-descriptions__label) {
  background: rgba(0, 212, 255, 0.1);
  color: #00d4ff;
  font-weight: 500;
}

.task-detail-dialog :deep(.el-descriptions__content) {
  color: #c9d1d9;
}

.task-detail-dialog :deep(.el-descriptions__body) {
  background: transparent;
}

.task-detail-dialog :deep(.el-descriptions__cell) {
  border-color: #30363d;
}

.mt-20 {
  margin-top: 20px;
}

.task-detail-dialog :deep(.el-textarea__inner) {
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid #30363d;
  color: #c9d1d9;
  cursor: default;
}

.task-detail-dialog :deep(.el-textarea__inner:focus) {
  border-color: #00d4ff;
}

/* 验证结论标签样式 */
.verification-tag {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
  padding: 4px 8px;
  height: auto;
}

/* 执行步骤卡片样式 */
.execution-steps-card {
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 16px 20px;
}

.card-title {
  color: #00d4ff;
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 12px;
}

.steps-content {
  color: #c9d1d9;
  line-height: 1.8;
}

.step-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
}

.step-item:last-child {
  margin-bottom: 0;
}

.step-number {
  color: #00d4ff;
  font-weight: 600;
  margin-right: 8px;
  min-width: 24px;
}

.step-text {
  flex: 1;
  word-break: break-word;
}

.empty-steps {
  color: #8b949e;
  font-style: italic;
  text-align: center;
  padding: 10px 0;
}
</style>
