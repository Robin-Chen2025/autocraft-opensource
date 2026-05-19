<template>
  <div class="task-detail-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      <h2 class="page-title">{{ task?.task_no || '任务详情' }}</h2>
    </div>

    <!-- 加载中 -->
    <el-skeleton v-if="loading" :rows="10" animated />

    <!-- 任务不存在 -->
    <el-empty v-else-if="!task" description="任务不存在" />

    <!-- 任务详情 -->
    <template v-else>
      <!-- 基本信息卡片 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span class="card-title">基本信息</span>
        </template>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="任务单号">
            {{ task.task_no }}
          </el-descriptions-item>
          <el-descriptions-item label="任务名称">
            {{ task.task_name }}
          </el-descriptions-item>
          <el-descriptions-item label="任务类型">
            <el-tag size="small">{{ task.task_type || '-' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(task.priority)" size="small">
              {{ getPriorityLabel(task.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="任务状态">
            <el-tag :type="getStatusType(task.status)">
              {{ getStatusLabel(task.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="验证结果">
            <el-tag :type="getVerifyResultType(task.verification_result)">
              {{ getVerifyResultLabel(task.verification_result) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(task.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(task.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 关联信息卡片 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span class="card-title">关联信息</span>
        </template>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="所属计划">
            {{ task.plan_id || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="所属阶段">
            {{ task.phase_record_id || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="执行Agent">
            {{ task.agent_id || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="内部ID">
            {{ task.id }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 计划时间卡片 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span class="card-title">计划时间</span>
        </template>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="计划日期">
            {{ formatDate(task.plan_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="计划完成时间">
            {{ formatDate(task.plan_complete_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="执行人">
            {{ task.executor || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="执行日期">
            {{ formatDate(task.execution_date) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 锁定状态卡片 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span class="card-title">锁定状态</span>
        </template>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="锁定者">
            {{ task.locked_by || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="锁定时间">
            {{ formatDate(task.locked_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="锁定状态">
            <el-tag :type="task.locked_by ? 'warning' : 'info'" size="small">
              {{ task.locked_by ? '已锁定' : '未锁定' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 输入数据卡片 -->
      <el-card class="info-card" shadow="never" v-if="task.input_data">
        <template #header>
          <span class="card-title">输入数据</span>
        </template>
        <div class="json-content">
          <pre>{{ formatJson(task.input_data) }}</pre>
        </div>
      </el-card>

      <!-- 扩展数据卡片 -->
      <el-card class="info-card" shadow="never" v-if="task.extra_data">
        <template #header>
          <span class="card-title">扩展数据</span>
        </template>
        <div class="json-content">
          <pre>{{ formatJson(task.extra_data) }}</pre>
        </div>
      </el-card>

      <!-- 执行步骤卡片 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span class="card-title">执行步骤</span>
        </template>
        <div class="execution-steps">
          <ol v-if="task.execution_steps && task.execution_steps.trim()">
            <li v-for="(step, index) in task.execution_steps.split(';').filter(s => s.trim())" :key="index">
              {{ step.trim() }}
            </li>
          </ol>
          <p v-else class="empty-content">暂无执行步骤</p>
        </div>
      </el-card>

      <!-- 预期结果卡片 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span class="card-title">预期结果</span>
        </template>
        <div class="expected-result">
          <p v-if="task.expected_result && task.expected_result.trim()">{{ task.expected_result }}</p>
          <p v-else class="empty-content">暂无预期结果</p>
        </div>
      </el-card>

      <!-- 执行记录卡片 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span class="card-title">执行记录</span>
        </template>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="执行人">
            {{ task.executor || task.locked_by || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDate(task.exec_start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="预计完成">
            {{ formatDate(task.exec_estimated_complete) }}
          </el-descriptions-item>
          <el-descriptions-item label="实际完成">
            {{ formatDate(task.exec_complete_time) }}
          </el-descriptions-item>
        </el-descriptions>
        <div class="log-section">
          <div class="log-label">执行日志：</div>
          <el-input
            :model-value="task.execution_log || '无执行日志'"
            type="textarea"
            :rows="6"
            readonly
            class="log-textarea"
          />
        </div>
        <div class="log-section" v-if="task.output_result">
          <div class="log-label">输出结果：</div>
          <div class="output-result">{{ task.output_result }}</div>
        </div>
      </el-card>

      <!-- 验证记录卡片 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span class="card-title">验证记录</span>
        </template>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="验证人">
            {{ task.verifier || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="验证结果">
            <el-tag :type="getVerifyResultType(task.verification_result)">
              {{ getVerifyResultLabel(task.verification_result) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDate(task.verify_start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="预计完成">
            {{ formatDate(task.verify_estimated_complete) }}
          </el-descriptions-item>
          <el-descriptions-item label="实际完成">
            {{ formatDate(task.verify_complete_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="验证时间">
            {{ formatDate(task.verification_time) }}
          </el-descriptions-item>
        </el-descriptions>
        <div class="log-section">
          <div class="log-label">验证日志：</div>
          <el-input
            :model-value="task.verification_log || '无验证日志'"
            type="textarea"
            :rows="4"
            readonly
            class="log-textarea"
          />
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Refresh } from '@element-plus/icons-vue'
import { getTask, type Task } from '@/api/profiles'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

// 数据
const loading = ref(false)
const task = ref<Task | null>(null)

// 加载数据
const loadData = async () => {
  const taskNo = route.params.task_no as string
  if (!taskNo) {
    ElMessage.error('缺少任务单号')
    return
  }

  loading.value = true
  try {
    task.value = await getTask(taskNo)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载失败')
    task.value = null
  } finally {
    loading.value = false
  }
}

// 返回
const handleBack = () => {
  router.back()
}

// 刷新
const handleRefresh = () => {
  loadData()
  ElMessage.success('数据已刷新')
}

// 状态类型映射
const getStatusType = (status?: string): 'success' | 'warning' | 'danger' | 'info' | '' => {
  if (!status) return 'info'
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info' | ''> = {
    new: 'info',
    pending: 'info',
    executing: 'warning',
    in_progress: 'warning',
    verifying: '',
    verified: 'success',
    completed: 'warning',
    failed: 'danger',
    blocked: 'danger',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

// 状态标签映射
const getStatusLabel = (status?: string): string => {
  if (!status) return '-'
  const labelMap: Record<string, string> = {
    new: '新建',
    pending: '待执行',
    executing: '执行中',
    in_progress: '进行中',
    verifying: '验证中',
    verified: '已验证',
    verification_failed: '验证失败',
    completed: '待验证',
    failed: '失败',
    blocked: '已阻塞',
    cancelled: '已取消'
  }
  return labelMap[status] || status
}

// 优先级类型映射
const getPriorityType = (priority?: string): 'success' | 'warning' | 'danger' | 'info' | '' => {
  if (!priority) return 'info'
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info' | ''> = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    critical: 'danger',
    中: 'warning',
    高: 'danger',
    低: 'info'
  }
  return typeMap[priority] || 'info'
}

// 优先级标签映射
const getPriorityLabel = (priority?: string): string => {
  if (!priority) return '-'
  const labelMap: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '紧急',
    中: '中',
    高: '高',
    低: '低'
  }
  return labelMap[priority] || priority
}

// 验证结果类型映射
const getVerifyResultType = (result?: string): 'success' | 'warning' | 'danger' | 'info' | '' => {
  if (!result) return 'info'
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info' | ''> = {
    pending: 'warning',
    待验证: 'warning',
    pass: 'success',
    passed: 'success',
    通过: 'success',
    fail: 'danger',
    failed: 'danger',
    不通过: 'danger'
  }
  return typeMap[result] || 'info'
}

// 验证结果标签映射
const getVerifyResultLabel = (result?: string): string => {
  if (!result) return '待验证'
  const labelMap: Record<string, string> = {
    pending: '待验证',
    pass: '通过',
    passed: '通过',
    fail: '不通过',
    failed: '不通过'
  }
  return labelMap[result] || result
}

// 格式化日期
const formatDate = (dateString?: string): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化 JSON
const formatJson = (jsonString?: string): string => {
  if (!jsonString) return '-'
  try {
    const obj = JSON.parse(jsonString)
    return JSON.stringify(obj, null, 2)
  } catch {
    return jsonString
  }
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.task-detail-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  gap: 10px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.info-card {
  margin-bottom: 20px;
}

.empty-content {
  color: #909399;
  font-size: 14px;
  margin: 8px 0;
}

.execution-steps {
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
}

.execution-steps ol {
  margin: 0;
  padding-left: 24px;
}

.execution-steps li {
  margin: 8px 0;
}

.expected-result {
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
}

.expected-result p {
  margin: 4px 0;
}

.output-result {
  padding: 12px;
  background: #f0f9eb;
  border-radius: 4px;
  border-left: 3px solid #67c23a;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.log-section {
  margin-top: 16px;
}

.log-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.log-textarea :deep(.el-textarea__inner) {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.5;
  background-color: #f5f7fa;
}

.json-content {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.json-content pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 状态徽章样式 */
:deep(.el-tag) {
  font-size: 12px;
  padding: 2px 8px;
}

:deep(.el-tag--success) {
  background-color: rgba(103, 194, 58, 0.1);
  border-color: rgba(103, 194, 58, 0.2);
  color: #67c23a;
}

:deep(.el-tag--warning) {
  background-color: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.2);
  color: #409eff;
}

:deep(.el-tag--info) {
  background-color: rgba(144, 147, 153, 0.1);
  border-color: rgba(144, 147, 153, 0.2);
  color: #909399;
}

:deep(.el-tag--danger) {
  background-color: rgba(245, 108, 108, 0.1);
  border-color: rgba(245, 108, 108, 0.2);
  color: #f56c6c;
}
</style>
