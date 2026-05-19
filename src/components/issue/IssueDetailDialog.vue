<template>
  <el-dialog
    v-model="visible"
    title="问题单详情"
    width="800px"
    :close-on-click-modal="false"
  >
    <div v-if="issue" class="issue-detail">
      <!-- 基本信息区域 -->
      <el-descriptions :column="2" border>
        <el-descriptions-item label="问题单号">{{ issue.id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(issue.status)">{{ getStatusLabel(issue.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityType(issue.priority)">{{ getPriorityLabel(issue.priority) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="分类">{{ issue.category || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ issue.creator }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ issue.created_at }}</el-descriptions-item>
        <el-descriptions-item label="关联任务" :span="2">
          <el-link v-if="issue.related_task_id" type="primary">{{ issue.related_task_id }}</el-link>
          <span v-else>-</span>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 问题描述区域 -->
      <div class="section">
        <h4>问题描述</h4>
        <el-card shadow="never">
          {{ issue.description }}
        </el-card>
      </div>

      <!-- 可展开区域：解决信息（仅 resolved/closed 状态显示） -->
      <template v-if="issue.status === 'resolved' || issue.status === 'closed'">
        <div class="section">
          <el-collapse>
            <el-collapse-item title="解决信息" name="resolution">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="解决人">{{ issue.resolver || '-' }}</el-descriptions-item>
                <el-descriptions-item label="解决时间">{{ issue.resolved_at || '-' }}</el-descriptions-item>
              </el-descriptions>
            </el-collapse-item>

            <el-collapse-item title="解决方案" name="solution">
              {{ issue.resolution_summary || '-' }}
            </el-collapse-item>

            <el-collapse-item title="根因分析" name="root-cause">
              {{ issue.root_cause || '-' }}
            </el-collapse-item>

            <el-collapse-item title="解决过程" name="process">
              {{ issue.solution_process || '-' }}
            </el-collapse-item>

            <el-collapse-item title="经验教训" name="lesson">
              {{ issue.lesson_learned || '-' }}
            </el-collapse-item>
          </el-collapse>
        </div>
      </template>

      <!-- 关闭信息区域（仅 closed 状态显示） -->
      <template v-if="issue.status === 'closed'">
        <div class="section">
          <h4>关闭信息</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="关闭原因">{{ issue.closed_reason || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </template>
    </div>

    <!-- 底部操作按钮 -->
    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
      <el-button
        v-if="issue?.status === 'open'"
        type="success"
        @click="handleResolve"
      >
        解决
      </el-button>
      <el-button
        v-if="issue?.status === 'resolved'"
        type="warning"
        @click="handleClose"
      >
        关闭问题
      </el-button>
      <el-button
        v-if="issue?.status === 'closed'"
        type="primary"
        @click="handleReopen"
      >
        重新打开
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Issue } from '@/types/issue'

const props = defineProps<{
  visible: boolean
  issue: Issue | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  resolve: []
  close: []
  reopen: []
}>()

const visible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const getStatusType = (status: string) => {
  const map: Record<string, string> = { open: 'danger', resolved: 'warning', closed: 'success' }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = { open: '待处理', resolved: '已解决', closed: '已关闭' }
  return map[status] || status
}

const getPriorityType = (priority: string) => {
  const map: Record<string, string> = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const getPriorityLabel = (priority: string) => {
  const map: Record<string, string> = { high: '高', medium: '中', low: '低' }
  return map[priority] || priority
}

const handleResolve = () => emit('resolve')
const handleClose = () => emit('close')
const handleReopen = () => emit('reopen')
</script>

<style scoped>
.issue-detail {
  max-height: 600px;
  overflow-y: auto;
}

.section {
  margin-top: 20px;
}

.section h4 {
  margin-bottom: 10px;
  color: #303133;
  font-weight: 600;
}
</style>
