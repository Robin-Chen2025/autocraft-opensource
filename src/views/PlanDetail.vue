<template>
  <div class="plan-detail-page">
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
    </div>

    <!-- 加载中 -->
    <el-skeleton v-if="loading" :rows="10" animated />

    <!-- 计划不存在 -->
    <el-empty v-else-if="!plan" description="计划不存在" />

    <!-- 计划详情 -->
    <template v-else>
      <!-- 计划信息卡片 -->
      <el-card class="plan-info-card" shadow="never">
        <template #header>
          <span class="card-title">{{ plan.plan_name }}</span>
        </template>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="计划名称">
            {{ plan.plan_name }}
          </el-descriptions-item>
          <el-descriptions-item label="所属项目">
            {{ projectName }}
          </el-descriptions-item>
          <el-descriptions-item label="所属阶段">
            {{ phaseName }}
          </el-descriptions-item>
          <el-descriptions-item label="计划状态">
            <el-tag :type="getStatusType(plan.status)">
              {{ getStatusLabel(plan.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(plan.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 进度统计卡片 -->
      <el-card class="progress-card" shadow="never">
        <template #header>
          <span class="card-title">进度统计</span>
        </template>
        <div class="progress-content">
          <div class="progress-bar-container">
            <el-progress
              :percentage="completionPercentage"
              :stroke-width="20"
              :text-inside="true"
            />
          </div>
          <div class="statistics">
            <div class="stat-item">
              <span class="stat-value completed">{{ statistics.completed }}</span>
              <span class="stat-label">已完成</span>
            </div>
            <div class="stat-item">
              <span class="stat-value in-progress">{{ statistics.inProgress }}</span>
              <span class="stat-label">进行中</span>
            </div>
            <div class="stat-item">
              <span class="stat-value pending">{{ statistics.pending }}</span>
              <span class="stat-label">待执行</span>
            </div>
            <div class="stat-item">
              <span class="stat-value total">{{ statistics.total }}</span>
              <span class="stat-label">总计</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 任务列表卡片 -->
      <el-card class="task-list-card" shadow="never">
        <template #header>
          <span class="card-title">任务列表</span>
        </template>
        <el-table :data="taskList" style="width: 100%" @row-click="handleRowClick">
          <el-table-column prop="task_no" label="任务单号" width="150" />
          <el-table-column prop="task_name" label="任务名称" min-width="200" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="80">
            <template #default="{ row }">
              <el-tag :type="getPriorityType(row.priority)" size="small">
                {{ getPriorityLabel(row.priority) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="task_type" label="任务类型" width="100">
            <template #default="{ row }">
              <el-tag size="small">
                {{ row.task_type || '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click.stop="handleViewTask(row)">
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="taskList.length === 0" description="暂无任务" :image-size="60" />
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Refresh } from '@element-plus/icons-vue'
import { getPlan, getPlanTasks, getProfile, type Plan, type Task } from '@/api/profiles'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

// 数据
const loading = ref(false)
const plan = ref<Plan | null>(null)
const taskList = ref<Task[]>([])
const projectName = ref('')
const phaseName = ref('')

// 进度统计
const statistics = computed(() => {
  const total = taskList.value.length
  // 支持中英文状态
  const completed = taskList.value.filter(t => 
    t.status === 'completed' || t.status === '已完成'
  ).length
  const inProgress = taskList.value.filter(t => 
    t.status === 'in_progress' || t.status === 'executing' || 
    t.status === '进行中' || t.status === '执行中'
  ).length
  const pending = taskList.value.filter(t => 
    t.status === 'pending' || t.status === 'new' || 
    t.status === '待执行' || t.status === '新建'
  ).length

  return { completed, inProgress, pending, total }
})

// 完成百分比
const completionPercentage = computed(() => {
  if (statistics.value.total === 0) return 0
  return Math.round((statistics.value.completed / statistics.value.total) * 100)
})

// 加载数据
const loadData = async () => {
  const planId = route.params.plan_id as string
  if (!planId) {
    ElMessage.error('缺少计划 ID')
    return
  }

  loading.value = true
  try {
    // 加载计划信息（包含关联的 profile 和 phase）
    const result = await getPlan(planId)
    plan.value = result.plan
    projectName.value = result.profile.profile_name
    phaseName.value = result.phase?.phase_name || ''

    // 加载任务
    taskList.value = await getPlanTasks(planId)
    // 按 task_no 升序排序
    taskList.value.sort((a, b) => a.task_no.localeCompare(b.task_no))
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载失败')
    plan.value = null
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

// 查看任务
const handleViewTask = (task: Task) => {
  router.push(`/tasks/${task.task_no}`)
}

// 点击行
const handleRowClick = (row: Task) => {
  router.push(`/tasks/${row.task_no}`)
}

// 状态类型映射
const getStatusType = (status?: string): 'success' | 'warning' | 'danger' | 'info' | '' => {
  if (!status) return 'info'
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info' | ''> = {
    new: 'info',
    pending: 'info',
    executing: 'warning',
    in_progress: 'warning',
    verifying: 'warning',
    completed: 'success',
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
    completed: '已完成',
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
    critical: 'danger'
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
    critical: '紧急'
  }
  return labelMap[priority] || priority
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

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.plan-detail-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  gap: 10px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.plan-info-card {
  margin-bottom: 20px;
}

.progress-card {
  margin-bottom: 20px;
}

.progress-content {
  padding: 10px 0;
}

.progress-bar-container {
  margin-bottom: 20px;
  padding: 0 10px;
}

.statistics {
  display: flex;
  justify-content: space-around;
  padding: 10px 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
}

.stat-value.completed {
  color: #67c23a;
}

.stat-value.in-progress {
  color: #409eff;
}

.stat-value.pending {
  color: #909399;
}

.stat-value.total {
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.task-list-card {
  background-color: #fff;
}

:deep(.el-table) {
  cursor: pointer;
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