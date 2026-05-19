<template>
  <div class="issue-detail-container">
    <!-- 页面标题栏 -->
    <div class="page-header">
      <h2 class="page-title">
        {{ isCreateMode ? '新建问题单' : '问题单详情' }}
      </h2>
      <div class="header-actions">
        <el-button
          v-if="isViewMode"
          type="primary"
          @click="enterEditMode"
        >
          编辑
        </el-button>
      </div>
    </div>

    <!-- 基本信息卡片 -->
    <el-card class="section-card">
      <template #header>
        <span class="section-title">基本信息</span>
      </template>
      <el-form :model="formData" label-width="100px" size="default">
        <el-row :gutter="20">
          <!-- 问题单号 -->
          <el-col :span="12">
            <el-form-item label="问题单号">
              <span v-if="isViewMode || isCreateMode" class="readonly-text">
                {{ formData.id || '待生成' }}
              </span>
              <el-input v-else v-model="formData.id" disabled />
            </el-form-item>
          </el-col>

          <!-- 状态 -->
          <el-col :span="12">
            <el-form-item label="状态">
              <el-tag v-if="formData.status" :type="getStatusTagType(formData.status)">
                {{ formData.status }}
              </el-tag>
              <span v-else class="readonly-text">待生成</span>
            </el-form-item>
          </el-col>

          <!-- 优先级 -->
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-radio-group
                v-if="isEditMode || isCreateMode"
                v-model="formData.priority"
              >
                <el-radio value="高">高</el-radio>
                <el-radio value="中">中</el-radio>
                <el-radio value="低">低</el-radio>
              </el-radio-group>
              <el-tag v-else :type="getPriorityTagType(formData.priority)">
                {{ formData.priority }}
              </el-tag>
            </el-form-item>
          </el-col>

          <!-- 分类 -->
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select
                v-if="isEditMode || isCreateMode"
                v-model="formData.category"
                placeholder="请选择"
                style="width: 100%"
              >
                <el-option
                  v-for="opt in categoryOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
              <span v-else class="readonly-text">
                {{ formData.category || '未选择' }}
              </span>
            </el-form-item>
          </el-col>

          <!-- 创建人 -->
          <el-col :span="12">
            <el-form-item label="创建人">
              <span class="readonly-text">{{ formData.creator || '执行子代理' }}</span>
            </el-form-item>
          </el-col>

          <!-- 创建时间 -->
          <el-col :span="12">
            <el-form-item label="创建时间">
              <span class="readonly-text">
                {{ formData.created_at ? formatDate(formData.created_at) : '待生成' }}
              </span>
            </el-form-item>
          </el-col>

          <!-- 关联任务 -->
          <el-col :span="12">
            <el-form-item label="关联任务">
              <el-input
                v-if="isEditMode || isCreateMode"
                v-model="formData.related_task_id"
                placeholder="例如：TSK-20260324-0001"
                clearable
              />
              <span v-else class="readonly-text">
                {{ formData.related_task_id || '无' }}
              </span>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 问题标题 -->
        <el-form-item label="问题标题">
          <el-input
            v-if="isEditMode || isCreateMode"
            v-model="formData.title"
            placeholder="请输入问题标题"
            maxlength="200"
            show-word-limit
          />
          <span v-else class="readonly-text">{{ formData.title || '无' }}</span>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 问题描述卡片 -->
    <el-card class="section-card">
      <template #header>
        <span class="section-title">问题描述</span>
      </template>
      <el-input
        v-if="isEditMode || isCreateMode"
        v-model="formData.description"
        type="textarea"
        :rows="6"
        placeholder="请详细描述问题现象、影响范围、复现步骤等"
        maxlength="5000"
        show-word-limit
      />
      <div v-else class="readonly-content">
        {{ formData.description || '无描述' }}
      </div>
    </el-card>

    <!-- 关联信息卡片（仅查看模式显示） -->
    <el-card v-if="!isCreateMode && !isEditMode" class="section-card">
      <template #header>
        <span class="section-title">关联信息</span>
      </template>
      <el-form label-width="100px" size="default">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="关联项目">
              <span class="readonly-text">{{ formData.project_name || '无' }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联阶段">
              <span class="readonly-text">{{ formData.stage_name || '无' }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联工作流">
              <span class="readonly-text">{{ formData.workflow_name || '无' }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联任务">
              <span class="readonly-text">{{ formData.related_task_id || '无' }}</span>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 处理信息卡片（仅查看模式显示） -->
    <el-card v-if="!isCreateMode && !isEditMode" class="section-card">
      <template #header>
        <span class="section-title">处理信息</span>
      </template>
      <el-form label-width="100px" size="default">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="处理人">
              <span class="readonly-text">{{ formData.assignee || '未分配' }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分配时间">
              <span class="readonly-text">{{ formData.assigned_at ? formatDate(formData.assigned_at) : '无' }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预期完成">
              <span class="readonly-text">{{ formData.due_date || '无' }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分配说明">
              <span class="readonly-text">{{ formData.assign_note || '无' }}</span>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 解决信息卡片（仅已解决/已关闭显示） -->
    <el-card v-if="formData.status === '已解决' || formData.status === '已关闭'" class="section-card">
      <template #header>
        <span class="section-title">解决信息</span>
      </template>
      <el-form label-width="100px" size="default">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="解决人">
              <span class="readonly-text">{{ formData.resolved_by || '无' }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="解决时间">
              <span class="readonly-text">
                {{ formData.resolved_at ? formatDate(formData.resolved_at) : '无' }}
              </span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="解决方案">
          <div class="readonly-content">{{ formData.solution || '无' }}</div>
        </el-form-item>
        <el-form-item label="根因分析">
          <div class="readonly-content">{{ formData.root_cause || '无' }}</div>
        </el-form-item>
        <el-form-item label="解决过程">
          <div class="readonly-content">{{ formData.solution_process || '无' }}</div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 问题总结卡片（仅已解决/已关闭显示） -->
    <el-card v-if="formData.status === '已解决' || formData.status === '已关闭'" class="section-card">
      <template #header>
        <span class="section-title">问题总结</span>
      </template>
      <el-form label-width="100px" size="default">
        <el-form-item label="经验教训">
          <div class="readonly-content">{{ formData.lesson_learned || '无' }}</div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 关闭信息卡片（仅已关闭显示） -->
    <el-card v-if="formData.status === '已关闭'" class="section-card">
      <template #header>
        <span class="section-title">关闭信息</span>
      </template>
      <el-form label-width="100px" size="default">
        <el-form-item label="关闭原因">
          <div class="readonly-content">{{ formData.closed_reason || '无' }}</div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 状态流转记录卡片（仅查看模式显示） -->
    <el-card v-if="!isCreateMode && !isEditMode" class="section-card">
      <template #header>
        <span class="section-title">状态流转记录</span>
      </template>
      <el-table :data="statusLogs" style="width: 100%" border size="small">
        <el-table-column prop="time" label="时间" width="140" />
        <el-table-column prop="operation" label="操作" width="100" />
        <el-table-column prop="from_status" label="原状态" width="90">
          <template #default="{ row }">
            <span>{{ row.from_status || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="to_status" label="新状态" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusTagType(row.to_status)">
              {{ row.to_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作人" width="100" />
        <el-table-column prop="note" label="备注" show-overflow-tooltip />
      </el-table>
    </el-card>

    <!-- 底部操作按钮 -->
    <div class="action-bar">
      <el-button @click="handleCancel">取消</el-button>
      <el-button
        v-if="isEditMode || isCreateMode"
        type="primary"
        @click="handleSave"
        :loading="saving"
      >
        保存
      </el-button>
      <el-button
        v-if="isViewMode && formData.status === '新建'"
        type="primary"
        @click="handleStartProgress"
      >
        开始处理
      </el-button>
      <el-button
        v-if="isViewMode && formData.status === '处理中'"
        type="success"
        @click="handleResolve"
      >
        解决
      </el-button>
      <el-button
        v-if="isViewMode && formData.status === '已解决'"
        type="warning"
        @click="handleClose"
      >
        关闭
      </el-button>
      <el-button
        v-if="isViewMode && formData.status === '已关闭'"
        type="info"
        @click="handleReopen"
      >
        重开
      </el-button>
    </div>

    <!-- 解决对话框 -->
    <el-dialog
      v-model="resolveDialogVisible"
      title="解决问题"
      width="600px"
      @close="resetResolveForm"
    >
      <el-form :model="resolveForm" label-width="100px" size="default">
        <el-form-item label="解决方案" required>
          <el-input
            v-model="resolveForm.solution"
            type="textarea"
            :rows="4"
            placeholder="请总结解决方案"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="根因分析" required>
          <el-input
            v-model="resolveForm.root_cause"
            type="textarea"
            :rows="3"
            placeholder="请分析根本原因"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="解决过程" required>
          <el-input
            v-model="resolveForm.solution_process"
            type="textarea"
            :rows="4"
            placeholder="请描述解决过程"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="经验教训">
          <el-input
            v-model="resolveForm.lesson_learned"
            type="textarea"
            :rows="3"
            placeholder="请总结经验教训（可选）"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmResolve" :loading="saving">确认解决</el-button>
      </template>
    </el-dialog>

    <!-- 关闭对话框 -->
    <el-dialog
      v-model="closeDialogVisible"
      title="关闭问题"
      width="500px"
      @close="resetCloseForm"
    >
      <el-form :model="closeForm" label-width="100px" size="default">
        <el-form-item label="关闭原因" required>
          <el-input
            v-model="closeForm.closed_reason"
            type="textarea"
            :rows="4"
            placeholder="请输入关闭原因"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmClose" :loading="saving">确认关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { Issue, CreateIssueRequest, UpdateIssueRequest, ResolveIssueRequest, CloseIssueRequest } from '@/types/issue'
import {
  statusOptions,
  priorityOptions,
  categoryOptions,
  getStatusTagType,
  getPriorityTagType
} from '@/types/issue'

// ============================================================================
// 路由与模式
// ============================================================================

const route = useRoute()
const router = useRouter()

// 判断当前模式
const isCreateMode = computed(() => route.path === '/issues/create')
const isViewMode = computed(() => route.params.id && !isEditMode.value)
const isEditMode = ref(false)

const issueId = computed(() => route.params.id as string)

// ============================================================================
// 表单数据
// ============================================================================

const formData = reactive<Partial<Issue>>({
  id: '',
  title: '',
  description: '',
  status: '新建',
  priority: '中',
  category: '',
  creator: '',
  created_at: '',
  resolved_at: '',
  resolved_by: '',
  solution: '',
  root_cause: '',
  solution_process: '',
  lesson_learned: '',
  closed_reason: '',
  related_task_id: '',
  // 关联信息
  project_name: '',
  stage_name: '',
  workflow_name: '',
  // 处理信息
  assignee: '',
  assigned_at: '',
  due_date: '',
  assign_note: ''
})

const saving = ref(false)

// ============================================================================
// 状态流转记录
// ============================================================================

interface StatusLog {
  time: string
  operation: string
  from_status: string
  to_status: string
  operator: string
  note: string
}

const statusLogs = ref<StatusLog[]>([])

// ============================================================================
// 折叠面板
// ============================================================================

const activeCollapse = ref<string>('')

// ============================================================================
// 对话框
// ============================================================================

const resolveDialogVisible = ref(false)
const closeDialogVisible = ref(false)

const resolveForm = reactive<ResolveIssueRequest>({
  resolved_by: '',
  solution: '',
  root_cause: '',
  solution_process: '',
  lesson_learned: '',
  resolver: '',
  resolution_summary: ''
})

const closeForm = reactive<CloseIssueRequest>({
  closed_reason: ''
})

// ============================================================================
// 工具函数
// ============================================================================

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 生成问题单号：ISSUE-YYYYMMDD-NNNN
const generateIssueId = () => {
  const now = new Date()
  const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '')
  const randomNum = Math.floor(Math.random() * 10000).toString().padStart(4, '0')
  return `ISSUE-${dateStr}-${randomNum}`
}

// ============================================================================
// 数据加载
// ============================================================================

const loadIssue = async () => {
  if (isCreateMode.value) {
    // 新建模式：初始化空表单
    resetFormData()
    return
  }

  if (!issueId.value) {
    ElMessage.error('问题单号不存在')
    router.push('/issues')
    return
  }

  try {
    // TODO: 替换为实际 API 调用
    // const response = await issueApi.getById(issueId.value)
    // Object.assign(formData, response.data)

    // 模拟数据
    const mockIssue: Issue = {
      id: issueId.value,
      title: '示例问题标题',
      description: '这是一个示例问题描述，用于展示页面效果。',
      status: '新建',
      priority: '高',
      category: 'Bug',
      creator: '执行子代理',
      created_at: '2026-03-24T10:00:00Z',
      resolved_at: '',
      resolved_by: '',
      solution: '',
      root_cause: '',
      solution_process: '',
      lesson_learned: '',
      closed_reason: '',
      related_task_id: 'TSK-20260324-0001'
    }
    Object.assign(formData, mockIssue)
    
    // 模拟状态流转记录
    statusLogs.value = [
      {
        time: '2026-03-24 10:30',
        operation: '创建',
        from_status: '',
        to_status: '新建',
        operator: '执行子代理',
        note: '提交问题单'
      }
    ]
  } catch (error) {
    ElMessage.error('加载问题单失败')
    console.error(error)
  }
}

const resetFormData = () => {
  formData.id = generateIssueId()
  formData.title = ''
  formData.description = ''
  formData.status = '新建'
  formData.priority = '中'
  formData.category = ''
  formData.creator = ''
  formData.created_at = ''
  formData.resolved_at = ''
  formData.resolved_by = ''
  formData.solution = ''
  formData.root_cause = ''
  formData.solution_process = ''
  formData.lesson_learned = ''
  formData.closed_reason = ''
  formData.related_task_id = ''
}

// ============================================================================
// 操作函数
// ============================================================================

const enterEditMode = () => {
  isEditMode.value = true
}

const handleCancel = () => {
  if (isCreateMode.value) {
    router.push('/issues')
  } else {
    isEditMode.value = false
    loadIssue() // 重新加载原始数据
  }
}

const handleSave = async () => {
  if (!formData.title?.trim()) {
    ElMessage.warning('请输入问题标题')
    return
  }

  saving.value = true
  try {
    if (isCreateMode.value) {
      // 新建
      const createData: CreateIssueRequest = {
        title: formData.title!,
        description: formData.description || '',
        priority: formData.priority || '中',
        category: formData.category || '',
        related_task_id: formData.related_task_id
      }
      // TODO: 调用 API
      // await issueApi.create(createData)
      
      // 模拟生成单号
      formData.id = generateIssueId()
      formData.created_at = new Date().toISOString()
      formData.creator = '执行子代理'
      
      ElMessage.success('问题单创建成功')
    } else {
      // 编辑
      const updateData: UpdateIssueRequest = {
        title: formData.title,
        description: formData.description,
        priority: formData.priority,
        category: formData.category,
        related_task_id: formData.related_task_id
      }
      // TODO: 调用 API
      // await issueApi.update(issueId.value, updateData)
      ElMessage.success('问题单保存成功')
    }

    if (isCreateMode.value) {
      router.push('/issues')
    } else {
      isEditMode.value = false
      loadIssue()
    }
  } catch (error) {
    ElMessage.error('操作失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const handleStartProgress = async () => {
  saving.value = true
  try {
    // TODO: 调用 API
    // await issueApi.updateStatus(issueId.value, '处理中')
    formData.status = '处理中'
    ElMessage.success('问题已开始处理')
  } catch (error) {
    ElMessage.error('操作失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const resetResolveForm = () => {
  resolveForm.resolved_by = ''
  resolveForm.solution = ''
  resolveForm.root_cause = ''
  resolveForm.solution_process = ''
  resolveForm.lesson_learned = ''
  resolveForm.resolver = ''
  resolveForm.resolution_summary = ''
}

const handleResolve = () => {
  resolveDialogVisible.value = true
}

const confirmResolve = async () => {
  if (!resolveForm.solution.trim()) {
    ElMessage.warning('请填写解决方案')
    return
  }
  if (!resolveForm.root_cause.trim()) {
    ElMessage.warning('请填写根因分析')
    return
  }
  if (!resolveForm.solution_process.trim()) {
    ElMessage.warning('请填写解决过程')
    return
  }

  saving.value = true
  try {
    const data: ResolveIssueRequest = {
      resolved_by: '当前用户', // TODO: 从用户信息获取
      solution: resolveForm.solution,
      root_cause: resolveForm.root_cause,
      solution_process: resolveForm.solution_process,
      lesson_learned: resolveForm.lesson_learned,
      resolver: '当前用户',
      resolution_summary: resolveForm.solution
    }
    // TODO: 调用 API
    // await issueApi.resolve(issueId.value, data)
    formData.status = '已解决'
    formData.resolved_by = data.resolved_by
    formData.solution = data.solution
    formData.root_cause = data.root_cause
    formData.solution_process = data.solution_process
    formData.lesson_learned = data.lesson_learned
    formData.resolved_at = new Date().toISOString()
    
    ElMessage.success('问题已解决')
    resolveDialogVisible.value = false
    loadIssue()
  } catch (error) {
    ElMessage.error('解决失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const resetCloseForm = () => {
  closeForm.closed_reason = ''
}

const handleClose = () => {
  closeDialogVisible.value = true
}

const confirmClose = async () => {
  if (!closeForm.closed_reason.trim()) {
    ElMessage.warning('请填写关闭原因')
    return
  }

  saving.value = true
  try {
    const data: CloseIssueRequest = {
      closed_reason: closeForm.closed_reason
    }
    // TODO: 调用 API
    // await issueApi.close(issueId.value, data)
    formData.status = '已关闭'
    formData.closed_reason = data.closed_reason
    
    ElMessage.success('问题已关闭')
    closeDialogVisible.value = false
    loadIssue()
  } catch (error) {
    ElMessage.error('关闭失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const handleReopen = async () => {
  saving.value = true
  try {
    // TODO: 调用 API
    // await issueApi.reopen(issueId.value)
    formData.status = '处理中'
    ElMessage.success('问题已重开')
    loadIssue()
  } catch (error) {
    ElMessage.error('重开失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

// ============================================================================
// 生命周期
// ============================================================================

onMounted(() => {
  loadIssue()
})
</script>

<style scoped>
.issue-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.section-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.section-card :deep(.el-card__header) {
  background-color: #fafafa;
  border-bottom: 1px solid #ebeef5;
  padding: 14px 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.readonly-text {
  color: #606266;
  font-size: 14px;
  line-height: 32px;
}

.readonly-content {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-top: 20px;
}

:deep(.el-collapse-item__header) {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  background-color: #fafafa;
  padding: 12px 20px;
}

:deep(.el-collapse-item__content) {
  padding: 16px 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-radio-group) {
  line-height: 32px;
}
</style>
