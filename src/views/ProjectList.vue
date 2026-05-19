<template>
  <div class="project-list-page">
    <!-- 页面标题和操作按钮 -->
    <div class="page-header">
      <h1 class="page-title">项目概览</h1>
      <el-button @click="handleRefresh">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 筛选区域 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="项目名称">
          <el-input v-model="filterForm.name" placeholder="项目名称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filterForm.type" placeholder="全部" clearable style="width: 120px">
            <el-option label="模板" value="template" />
            <el-option label="实例" value="instance" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="进行中" value="active" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已完成" value="completed" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="filterForm.created_at_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table :data="paginatedData" style="width: 100%" border v-loading="loading" @row-click="handleRowClick">
        <el-table-column prop="profile_id" label="项目 ID" min-width="120" />
        <el-table-column prop="profile_name" label="项目名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="profile_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.profile_type === 'template' ? 'warning' : 'primary'">
              {{ row.profile_type === 'template' ? '模板' : '实例' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="project_type" label="项目类型" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="handleView(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页组件 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { getProfiles, type Profile } from '@/api/profiles'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 筛选表单
const filterForm = ref({
  name: '',
  type: '',
  status: '',
  created_at_range: null as [Date, Date] | null
})

// 表格数据
const tableData = ref<Profile[]>([])
const loading = ref(false)

// 分页配置
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 加载数据（从 API）
const loadData = async () => {
  loading.value = true
  try {
    // 处理日期范围参数
    let start_date: string | undefined
    let end_date: string | undefined
    
    if (filterForm.value.created_at_range && filterForm.value.created_at_range.length === 2) {
      const [start, end] = filterForm.value.created_at_range
      start_date = start.toISOString()
      end_date = end.toISOString()
    }
    
    const response = await getProfiles({
      page: pagination.value.currentPage,
      page_size: pagination.value.pageSize,
      profile_type: filterForm.value.type || undefined,
      status: filterForm.value.status || undefined,
      name: filterForm.value.name || undefined,
      start_date,
      end_date
    })
    tableData.value = response.items
    pagination.value.total = response.total
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 分页后的数据（直接使用 API 返回的数据）
const paginatedData = computed(() => tableData.value)

// 状态类型映射
const getStatusType = (status: string): 'success' | 'warning' | 'danger' | 'info' | '' => {
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info' | ''> = {
    draft: 'info',
    active: 'success',
    paused: 'warning',
    completed: 'success',
    archived: 'info'
  }
  return typeMap[status] || 'info'
}

// 状态标签映射
const getStatusLabel = (status: string): string => {
  const labelMap: Record<string, string> = {
    draft: '草稿',
    active: '进行中',
    paused: '已暂停',
    completed: '已完成',
    archived: '已归档'
  }
  return labelMap[status] || status
}

// 格式化日期
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 查询
const handleSearch = () => {
  pagination.value.currentPage = 1
  loadData()
  ElMessage.success('查询成功')
}

// 重置
const handleReset = () => {
  filterForm.value = {
    name: '',
    type: '',
    status: '',
    created_at_range: null
  }
  pagination.value.currentPage = 1
  loadData()
  ElMessage.success('已重置筛选条件')
}

// 刷新
const handleRefresh = () => {
  loadData()
  ElMessage.success('数据已刷新')
}

// 查看项目详情
const handleView = (row: Profile) => {
  router.push(`/projects/${row.profile_id}`)
}

// 行点击
const handleRowClick = (row: Profile) => {
  router.push(`/projects/${row.profile_id}`)
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  pagination.value.currentPage = 1
  loadData()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  pagination.value.currentPage = page
}

// 初始化加载
loadData()
</script>

<style scoped>
.project-list-page {
  padding: 20px;
  background-color: var(--page-bg);
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.filter-card {
  margin-bottom: 20px;
  background-color: var(--card-bg);
  border-color: var(--card-border);
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
}

.filter-form .el-form-item {
  margin-bottom: 10px;
  margin-right: 20px;
}

.table-card {
  background-color: var(--card-bg);
  border-color: var(--card-border);
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-light);
}

/* 状态徽章样式 - emoji + 文字 */
:deep(.el-tag) {
  font-size: 12px;
  padding: 2px 8px;
}

/* 已完成 - 绿色文字 */
:deep(.el-tag--success) {
  background-color: rgba(103, 194, 58, 0.1);
  border-color: rgba(103, 194, 58, 0.2);
  color: var(--status-success);
}

/* 进行中 - 蓝色文字 */
:deep(.el-tag--warning) {
  background-color: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.2);
  color: var(--status-processing);
}

/* 待执行 - 灰色文字 */
:deep(.el-tag--info) {
  background-color: rgba(144, 147, 153, 0.1);
  border-color: rgba(144, 147, 153, 0.2);
  color: var(--status-pending);
}

/* 已阻塞 - 橙色文字 */
:deep(.el-tag--danger) {
  background-color: rgba(230, 162, 60, 0.1);
  border-color: rgba(230, 162, 60, 0.2);
  color: var(--status-blocked);
}
</style>
