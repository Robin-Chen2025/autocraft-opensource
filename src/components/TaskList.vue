<template>
  <div class="task-list-container">
    <!-- 查询条件区域 -->
    <el-card class="query-card" shadow="hover">
      <el-form :model="queryForm" inline>
        <el-row :gutter="20">
          <!-- 字段1 - 任务单号 -->
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="任务单号">
              <el-input
                v-model="queryForm.task_no"
                placeholder="请输入任务单号"
                clearable
                class="form-input"
              />
            </el-form-item>
          </el-col>
          
          <!-- 字段2 - 任务名称 -->
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="任务名称">
              <el-input
                v-model="queryForm.task_name"
                placeholder="请输入任务名称"
                clearable
                class="form-input"
              />
            </el-form-item>
          </el-col>
          
          <!-- 字段3 - 状态 -->
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="状态">
              <el-select
                v-model="queryForm.status"
                multiple
                placeholder="请选择状态"
                clearable
                collapse-tags
                class="form-select"
              >
                <el-option
                  v-for="item in statusOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </el-col>
          
          <!-- 字段4 - 优先级 -->
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="优先级">
              <el-select
                v-model="queryForm.priority"
                multiple
                placeholder="请选择优先级"
                clearable
                collapse-tags
                class="form-select"
              >
                <el-option
                  v-for="item in priorityOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 第二行查询条件 -->
        <el-row :gutter="20">
          <!-- 字段5 - 执行人 -->
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="执行人">
              <el-input
                v-model="queryForm.executor"
                placeholder="请输入执行人"
                clearable
                class="form-input"
              />
            </el-form-item>
          </el-col>
          
          <!-- 字段6 - 验证人 -->
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="验证人">
              <el-input
                v-model="queryForm.verifier"
                placeholder="请输入验证人"
                clearable
                class="form-input"
              />
            </el-form-item>
          </el-col>
          
          <!-- 字段7 - 验证结论 -->
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="验证结论">
              <el-select
                v-model="queryForm.verification_result"
                multiple
                placeholder="请选择验证结论"
                clearable
                collapse-tags
                class="form-select"
              >
                <el-option
                  v-for="item in verificationOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 第三行查询条件 - 时间查询 -->
        <el-row :gutter="20">
          <!-- 字段8 - 计划日期 -->
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="计划日期">
              <el-date-picker
                v-model="queryForm.plan_date_range"
                type="daterange"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                clearable
                class="form-date-picker"
              />
            </el-form-item>
          </el-col>
          
          <!-- 字段9 - 计划完成时间 -->
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="计划完成时间">
              <el-date-picker
                v-model="queryForm.plan_complete_range"
                type="datetimerange"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm"
                clearable
                class="form-date-picker"
              />
            </el-form-item>
          </el-col>
          
          <!-- 字段10 - 验证时间 -->
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="验证时间">
              <el-date-picker
                v-model="queryForm.verification_time_range"
                type="datetimerange"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm"
                clearable
                class="form-date-picker"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 第四行查询条件 - 执行和验证开始时间 -->
        <el-row :gutter="20">
          <!-- 字段 11 - 执行开始时间范围 -->
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="执行开始时间">
              <el-date-picker
                v-model="queryForm.exec_start_time_range"
                type="datetimerange"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                clearable
                class="form-date-picker"
              />
            </el-form-item>
          </el-col>
          
          <!-- 字段 12 - 验证开始时间范围 -->
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="验证开始时间">
              <el-date-picker
                v-model="queryForm.verify_start_time_range"
                type="datetimerange"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                clearable
                class="form-date-picker"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 第五行 - 查询/重置按钮 -->
        <el-row :gutter="20">
          <el-col :span="24">
            <div class="button-container">
              <el-button type="primary" :icon="Search" @click="handleSearch">
                查询
              </el-button>
              <el-button @click="handleReset">
                重置
              </el-button>
            </div>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 表格区域 -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <el-button type="primary" @click="loadTasks">刷新</el-button>
        </div>
      </template>
      
      <!-- 空数据提示 -->
      <el-empty v-if="!loading && tasks.length === 0" description="暂无任务数据" />
      
      <!-- 表格内容 -->
      <div v-else class="table-wrapper">
        <el-table 
          :data="tasks" 
          v-loading="loading" 
          stripe 
          highlight-current-row
          class="task-table"
        >
          <!-- 1. 任务单号 -->
          <el-table-column prop="task_no" label="任务单号" min-width="140" align="left" show-overflow-tooltip />
          
          <!-- 2. 任务名称 -->
          <el-table-column prop="task_name" label="任务名称" min-width="180" align="left" show-overflow-tooltip />
          
          <!-- 3. 执行步骤 -->
          <el-table-column prop="execution_steps" label="执行步骤" min-width="250" align="left" show-overflow-tooltip />
          
          <!-- 4. 执行人 - 小屏幕隐藏 -->
          <el-table-column prop="executor" label="执行人" min-width="100" align="center" class-name="hidden-xs-only" />
          
          <!-- 4. 状态 -->
          <el-table-column prop="status" label="状态" min-width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" effect="light" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          
          <!-- 5. 优先级 -->
          <el-table-column prop="priority" label="优先级" min-width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="getPriorityType(row.priority)" effect="light" size="small">{{ row.priority }}</el-tag>
            </template>
          </el-table-column>
          
          <!-- 6. 计划日期 - 小屏幕隐藏 -->
          <el-table-column prop="plan_date" label="计划日期" min-width="110" align="center" :formatter="(row: Task) => formatDate(row.plan_date)" class-name="hidden-sm-only" />
          
          <!-- 7. 计划完成时间 - 小屏幕隐藏 -->
          <el-table-column prop="plan_complete_time" label="计划完成时间" min-width="150" align="center" :formatter="(row: Task) => formatDateTime(row.plan_complete_time)" class-name="hidden-md-only" />
          
          <!-- 8. 验证结论 -->
          <el-table-column prop="verification_result" label="验证结论" min-width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="getVerificationType(row.verification_result)" effect="light" size="small">{{ row.verification_result || '-' }}</el-tag>
            </template>
          </el-table-column>
          
          <!-- 9. 验证人 - 小屏幕隐藏 -->
          <el-table-column prop="verifier" label="验证人" min-width="100" align="center" class-name="hidden-sm-only">
            <template #default="{ row }">
              {{ row.verifier || '-' }}
            </template>
          </el-table-column>
          
          <!-- 10. 验证时间 - 小屏幕隐藏 -->
          <el-table-column prop="verification_time" label="验证时间" min-width="150" align="center" :formatter="(row: Task) => formatDateTime(row.verification_time)" class-name="hidden-md-only" />
          
          <!-- 11. 执行开始时间 - 小屏幕隐藏 -->
          <el-table-column prop="exec_start_time" label="执行开始时间" width="160" align="center" :formatter="(row: Task) => formatDateTime(row.exec_start_time)" class-name="hidden-md-only" />
          
          <!-- 12. 预计执行完成时间 - 小屏幕隐藏 -->
          <el-table-column prop="exec_estimated_complete" label="预计执行完成" width="160" align="center" :formatter="(row: Task) => formatDateTime(row.exec_estimated_complete)" class-name="hidden-md-only" />
          
          <!-- 13. 实际执行完成时间 - 小屏幕隐藏 -->
          <el-table-column prop="exec_complete_time" label="实际执行完成" width="160" align="center" :formatter="(row: Task) => formatDateTime(row.exec_complete_time)" class-name="hidden-md-only" />
          
          <!-- 14. 验证开始时间 - 小屏幕隐藏 -->
          <el-table-column prop="verify_start_time" label="验证开始时间" width="160" align="center" :formatter="(row: Task) => formatDateTime(row.verify_start_time)" class-name="hidden-md-only" />
          
          <!-- 15. 预计验证完成时间 - 小屏幕隐藏 -->
          <el-table-column prop="verify_estimated_complete" label="预计验证完成" width="160" align="center" :formatter="(row: Task) => formatDateTime(row.verify_estimated_complete)" class-name="hidden-md-only" />
          
          <!-- 16. 实际验证完成时间 - 小屏幕隐藏 -->
          <el-table-column prop="verify_complete_time" label="实际验证完成" width="160" align="center" :formatter="(row: Task) => formatDateTime(row.verify_complete_time)" class-name="hidden-md-only" />
          
          <!-- 17. 操作 -->
          <el-table-column label="操作" min-width="150" align="center" fixed="right">
            <template #default="{ row }">
              <el-button-group>
                <el-button size="small" @click="handleView(row)">
                  <el-icon><View /></el-icon>
                </el-button>
                <el-button type="primary" size="small" @click="handleEdit(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryForm.page"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadTasks"
        />
      </div>
    </el-card>
    
    <!-- 任务详情对话框 -->
    <TaskDetailDialog
      v-model:visible="detailVisible"
      :task="selectedTask"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, View, Edit, Delete } from '@element-plus/icons-vue'
import { getTasks, getStatusOptions, getPriorityOptions, getVerificationOptions, deleteTask } from '../api/tasks'
import { useRouter } from 'vue-router'
import TaskDetailDialog from './TaskDetailDialog.vue'
import type { Task, TaskListResponse, TaskListQueryParams } from '../api/tasks'

// 响应式数据
const tasks = ref<Task[]>([])
const loading = ref(false)
const total = ref(0)
const statusOptions = ref<string[]>([])
const priorityOptions = ref<string[]>([])
const verificationOptions = ref<string[]>([])
const router = useRouter()

// 详情对话框
const detailVisible = ref(false)
const selectedTask = ref<Task | null>(null)

// 查询表单
const queryForm = ref<TaskListQueryParams & { 
  task_no?: string; 
  task_name?: string; 
  executor?: string; 
  verifier?: string; 
  verification_result?: string[];
  plan_date_range?: string[];
  plan_complete_range?: string[];
  verification_time_range?: string[];
  exec_start_time_range?: string[];
  verify_start_time_range?: string[];
}>({
  page: 1,
  page_size: 10,
  keyword: '',
  status: [],
  priority: [],
  task_no: '',
  task_name: '',
  executor: '',
  verifier: '',
  verification_result: [],
  plan_date_range: [],
  plan_complete_range: [],
  verification_time_range: [],
  exec_start_time_range: [],
  verify_start_time_range: []
})

// 加载选项数据
const loadOptions = async () => {
  try {
    const [statusRes, priorityRes, verificationRes] = await Promise.all([
      getStatusOptions(),
      getPriorityOptions(),
      getVerificationOptions()
    ])
    statusOptions.value = statusRes
    priorityOptions.value = priorityRes
    verificationOptions.value = verificationRes
  } catch (error: any) {
    ElMessage.error('加载选项失败：' + error.message)
    console.error('加载选项失败:', error)
  }
}

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

// 格式化日期时间 (YYYY-MM-DD HH:mm:ss)
const formatDateTimeWithSeconds = (dateStr: string | null | undefined) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 加载任务列表
const loadTasks = async () => {
  loading.value = true
  try {
    // 构建查询参数 - 支持多字段组合查询
    const params: any = {
      page: queryForm.value.page,
      page_size: queryForm.value.page_size
    }
    
    // 任务名称搜索（使用keyword）
    if (queryForm.value.task_name) {
      params.keyword = queryForm.value.task_name
    }
    
    // 任务单号搜索
    if (queryForm.value.task_no) {
      params.task_no = queryForm.value.task_no
    }
    
    // 执行人搜索
    if (queryForm.value.executor) {
      params.executor = queryForm.value.executor
    }
    
    // 验证人搜索
    if (queryForm.value.verifier) {
      params.verifier = queryForm.value.verifier
    }
    
    // 处理状态参数（数组转字符串）
    if (queryForm.value.status && Array.isArray(queryForm.value.status) && queryForm.value.status.length > 0) {
      params.status = queryForm.value.status.join(',')
    }
    
    // 处理优先级参数（数组转字符串）
    if (queryForm.value.priority && Array.isArray(queryForm.value.priority) && queryForm.value.priority.length > 0) {
      params.priority = queryForm.value.priority.join(',')
    }
    
    // 处理验证结论参数（数组转字符串）
    if (queryForm.value.verification_result && queryForm.value.verification_result.length > 0) {
      params.verification_result = queryForm.value.verification_result.join(',')
    }
    
    // 计划日期范围
    if (queryForm.value.plan_date_range && queryForm.value.plan_date_range.length === 2) {
      params.plan_date_start = queryForm.value.plan_date_range[0]
      params.plan_date_end = queryForm.value.plan_date_range[1]
    }
    
    // 计划完成时间范围
    if (queryForm.value.plan_complete_range && queryForm.value.plan_complete_range.length === 2) {
      params.plan_complete_start = queryForm.value.plan_complete_range[0]
      params.plan_complete_end = queryForm.value.plan_complete_range[1]
    }
    
    // 验证时间范围
    if (queryForm.value.verification_time_range && queryForm.value.verification_time_range.length === 2) {
      params.verification_time_start = queryForm.value.verification_time_range[0]
      params.verification_time_end = queryForm.value.verification_time_range[1]
    }
    
    // 执行开始时间范围
    if (queryForm.value.exec_start_time_range && queryForm.value.exec_start_time_range.length === 2) {
      params.exec_start_time_start = queryForm.value.exec_start_time_range[0]
      params.exec_start_time_end = queryForm.value.exec_start_time_range[1]
    }
    
    // 验证开始时间范围
    if (queryForm.value.verify_start_time_range && queryForm.value.verify_start_time_range.length === 2) {
      params.verify_start_time_start = queryForm.value.verify_start_time_range[0]
      params.verify_start_time_end = queryForm.value.verify_start_time_range[1]
    }
    
    const res: TaskListResponse = await getTasks(params)
    tasks.value = res.items
    total.value = res.total
  } catch (error: any) {
    ElMessage.error('加载失败：' + error.message)
    console.error('加载任务列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 初始化加载
onMounted(() => {
  loadOptions()
  loadTasks()
})

// 查询按钮处理
const handleSearch = async () => {
  try {
    // 构建查询参数，重置到第1页
    const params = {
      ...queryForm.value,
      page: 1
    }
    queryForm.value.page = 1
    await loadTasks()
    ElMessage.success('查询成功')
  } catch (error: any) {
    ElMessage.error('查询失败：' + error.message)
    console.error('查询失败:', error)
  }
}

// 重置按钮处理
const handleReset = async () => {
  try {
    // 重置查询表单为初始值
    queryForm.value = {
      page: 1,
      page_size: 10,
      keyword: '',
      status: [],
      priority: [],
      task_no: '',
      task_name: '',
      executor: '',
      verifier: '',
      verification_result: [],
      plan_date_range: [],
      plan_complete_range: [],
      verification_time_range: [],
      exec_start_time_range: [],
      verify_start_time_range: []
    }
    await loadTasks()
    ElMessage.success('已重置')
  } catch (error: any) {
    ElMessage.error('重置失败：' + error.message)
    console.error('重置失败:', error)
  }
}

// 查看任务详情
const handleView = (row: Task) => {
  selectedTask.value = row
  detailVisible.value = true
}

// 编辑任务
const handleEdit = (row: Task) => {
  router.push(`/task/edit?taskNo=${row.task_no}`)
}

// 删除任务
const handleDelete = async (row: Task) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 ${row.task_no} 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteTask(row.task_no)
    ElMessage.success('删除成功')
    await loadTasks()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
      console.error('删除失败:', error)
    }
  }
}
</script>

<style scoped>
.task-list-container {
  background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
  padding: 24px;
  min-height: 100vh;
}

/* 查询卡片样式优化 */
.query-card {
  margin-bottom: 20px;
  background: linear-gradient(145deg, #1a1f2e 0%, #21283a 100%);
  border: 1px solid #00d4ff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.15), 0 0 30px rgba(0, 212, 255, 0.1);
  transition: all 0.3s ease;
}

.query-card:hover {
  box-shadow: 0 6px 30px rgba(0, 212, 255, 0.25), 0 0 40px rgba(0, 212, 255, 0.15);
}

.query-card :deep(.el-card__body) {
  padding: 24px;
}

/* 表格卡片样式优化 */
.table-card {
  background: linear-gradient(145deg, #1a1f2e 0%, #21283a 100%);
  border: 1px solid #00d4ff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.15), 0 0 30px rgba(0, 212, 255, 0.1);
  transition: all 0.3s ease;
}

.table-card:hover {
  box-shadow: 0 6px 30px rgba(0, 212, 255, 0.25), 0 0 40px rgba(0, 212, 255, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  color: #00d4ff;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
  font-size: 18px;
  font-weight: 600;
}

.table-card :deep(.el-card__header) {
  background: linear-gradient(90deg, rgba(0, 212, 255, 0.1) 0%, transparent 100%);
  border-bottom: 1px solid #30363d;
  padding: 16px 24px;
}

/* 表格包装器 - 响应式滚动 */
.table-wrapper {
  width: 100%;
  overflow-x: auto;
}

/* 表格样式优化 */
.task-table {
  width: 100%;
  min-width: 800px;
}

.task-table :deep(.el-table__header-wrapper th) {
  background: rgba(0, 212, 255, 0.15) !important;
  color: #00d4ff !important;
  font-weight: 600;
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
}

.task-table :deep(.el-table__row) {
  transition: all 0.2s ease;
}

.task-table :deep(.el-table__row:hover) {
  background: rgba(0, 212, 255, 0.08) !important;
}

.task-table :deep(.el-table__row--striped) {
  background: rgba(0, 212, 255, 0.03) !important;
}

.task-table :deep(.el-table__row--striped:hover) {
  background: rgba(0, 212, 255, 0.1) !important;
}

.task-table :deep(td) {
  color: #c9d1d9 !important;
  border-bottom: 1px solid rgba(48, 54, 61, 0.5);
}

.task-table :deep(.current-row) {
  background: rgba(0, 212, 255, 0.12) !important;
}

/* 空数据提示样式 */
:deep(.el-empty) {
  padding: 60px 0;
}

:deep(.el-empty__description) {
  color: #8b949e;
  margin-top: 16px;
}

/* 分页样式 */
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  padding: 10px 0;
}

/* 响应式样式 - 小屏幕隐藏列 */
@media screen and (max-width: 768px) {
  .task-list-container {
    padding: 12px;
  }
  
  .query-card :deep(.el-card__body) {
    padding: 16px;
  }
  
  .table-card :deep(.el-card__header) {
    padding: 12px 16px;
  }
  
  .task-table :deep(.hidden-xs-only) {
    display: none !important;
  }
}

@media screen and (max-width: 992px) {
  .task-table :deep(.hidden-sm-only) {
    display: none !important;
  }
}

@media screen and (max-width: 1200px) {
  .task-table :deep(.hidden-md-only) {
    display: none !important;
  }
}

/* 表单元素样式 */
.form-input,
.form-select,
.form-date-picker {
  width: 100%;
}

.el-form-item :deep(.el-form-item__label) {
  color: #00d4ff;
  font-weight: 500;
}

.el-input :deep(.el-input__wrapper) {
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid #30363d;
  box-shadow: none;
  transition: all 0.3s ease;
}

.el-input :deep(.el-input__wrapper:hover) {
  border-color: #00d4ff;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
}

.el-input :deep(.el-input__inner) {
  color: #c9d1d9;
}

.el-input :deep(.el-input__inner::placeholder) {
  color: #8b949e;
}

.el-select :deep(.el-input__wrapper) {
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid #30363d;
  box-shadow: none;
}

.el-select :deep(.el-select__tags) {
  background: transparent;
}

.el-select :deep(.el-tag) {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  color: #00d4ff;
}

/* 日期选择器样式 */
.el-date-editor :deep(.el-input__wrapper) {
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid #30363d;
  box-shadow: none;
}

.el-date-editor :deep(.el-range-input) {
  color: #c9d1d9;
  background: transparent;
}

.el-date-editor :deep(.el-range-separator) {
  color: #8b949e;
}

.el-date-editor :deep(.el-range__icon) {
  color: #00d4ff;
}

/* 按钮区域样式 */
.button-container {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid rgba(48, 54, 61, 0.5);
  margin-top: 8px;
}

.button-container .el-button {
  margin-left: 12px;
}

.el-button--primary {
  background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4) !important;
  transition: all 0.3s ease;
}

.el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5) !important;
}
</style>
