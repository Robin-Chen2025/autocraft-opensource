<template>
  <div class="issue-list-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">问题管理</h1>
    </div>

    <!-- 筛选区域 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.statuses"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="全部"
            clearable
            style="width: 180px"
          >
            <el-option label="新建" value="新建" />
            <el-option label="处理中" value="处理中" />
            <el-option label="已解决" value="已解决" />
            <el-option label="已关闭" value="已关闭" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select
            v-model="filterForm.categories"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="全部"
            clearable
            style="width: 180px"
          >
            <el-option label="Bug" value="Bug" />
            <el-option label="优化" value="优化" />
            <el-option label="需求" value="需求" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select
            v-model="filterForm.priorities"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="全部"
            clearable
            style="width: 180px"
          >
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理人">
          <el-select
            v-model="filterForm.assignee"
            placeholder="全部"
            clearable
            style="width: 150px"
          >
            <el-option label="张三" value="zhangsan" />
            <el-option label="李四" value="lisi" />
            <el-option label="王五" value="wangwu" />
            <el-option label="赵六" value="zhaoliu" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目">
          <el-select
            v-model="filterForm.project"
            placeholder="全部"
            clearable
            style="width: 150px"
          >
            <el-option label="项目 A" value="project_a" />
            <el-option label="项目 B" value="project_b" />
            <el-option label="项目 C" value="project_c" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索标题或编号"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        创建问题单
      </el-button>
    </div>

    <!-- 列表表格 -->
    <el-card class="table-card" shadow="never">
      <el-table :data="tableData" style="width: 100%" border v-loading="loading">
        <el-table-column prop="id" label="问题编号" min-width="160" fixed>
          <template #default="{ row }">
            <el-link type="primary" @click="handleView(row)">{{ row.id }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="250" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignee" label="处理人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

// ============================================================================
// 筛选表单
// ============================================================================
const filterForm = reactive({
  statuses: [] as string[],
  categories: [] as string[],
  priorities: [] as string[],
  assignee: '',
  project: '',
  dateRange: null as [Date, Date] | null,
  keyword: ''
})

// ============================================================================
// 分页配置
// ============================================================================
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// ============================================================================
// 表格数据
// ============================================================================
const loading = ref(false)
const tableData = ref<IssueItem[]>([])

interface IssueItem {
  id: string
  title: string
  category: string
  priority: string
  status: string
  assignee: string
  created_at: string
}

// ============================================================================
// 状态映射
// ============================================================================
const statusConfig: Record<string, { type: 'info' | 'primary' | 'success' | ''; label: string }> = {
  '新建': { type: 'info', label: '新建' },
  '处理中': { type: 'primary', label: '处理中' },
  '已解决': { type: 'success', label: '已解决' },
  '已关闭': { type: '', label: '已关闭' }
}

const getStatusType = (status: string): 'info' | 'primary' | 'success' | '' => {
  return statusConfig[status]?.type || 'info'
}

const getStatusLabel = (status: string): string => {
  return statusConfig[status]?.label || status
}

// ============================================================================
// 优先级映射
// ============================================================================
const priorityConfig: Record<string, { type: 'danger' | 'warning' | ''; label: string }> = {
  '高': { type: 'danger', label: '高' },
  '中': { type: 'warning', label: '中' },
  '低': { type: '', label: '低' }
}

const getPriorityType = (priority: string): 'danger' | 'warning' | '' => {
  return priorityConfig[priority]?.type || ''
}

const getPriorityLabel = (priority: string): string => {
  return priorityConfig[priority]?.label || priority
}

// ============================================================================
// 分类映射
// ============================================================================
const categoryConfig: Record<string, { type: 'danger' | 'primary' | 'success' | ''; label: string }> = {
  'Bug': { type: 'danger', label: 'Bug' },
  '优化': { type: 'primary', label: '优化' },
  '需求': { type: 'success', label: '需求' },
  '其他': { type: '', label: '其他' }
}

const getCategoryType = (category: string): 'danger' | 'primary' | 'success' | '' => {
  return categoryConfig[category]?.type || ''
}

const getCategoryLabel = (category: string): string => {
  return categoryConfig[category]?.label || category
}

// ============================================================================
// 模拟数据加载
// ============================================================================
const loadData = () => {
  loading.value = true
  // 模拟 API 调用
  setTimeout(() => {
    tableData.value = [
      {
        id: 'ISSUE-20260324-0001',
        title: '登录页面在移动端显示异常',
        category: 'Bug',
        priority: '高',
        status: '新建',
        assignee: '张三',
        created_at: '2026-03-24 10:30:00'
      },
      {
        id: 'ISSUE-20260324-0002',
        title: '优化数据库查询性能',
        category: '优化',
        priority: '中',
        status: '处理中',
        assignee: '李四',
        created_at: '2026-03-24 11:00:00'
      },
      {
        id: 'ISSUE-20260324-0003',
        title: '新增用户导出功能',
        category: '需求',
        priority: '低',
        status: '已解决',
        assignee: '王五',
        created_at: '2026-03-24 09:15:00'
      },
      {
        id: 'ISSUE-20260324-0004',
        title: '修复数据导入时的编码问题',
        category: 'Bug',
        priority: '高',
        status: '处理中',
        assignee: '赵六',
        created_at: '2026-03-24 14:20:00'
      },
      {
        id: 'ISSUE-20260324-0005',
        title: '界面主题颜色调整',
        category: '优化',
        priority: '低',
        status: '已关闭',
        assignee: '张三',
        created_at: '2026-03-23 16:45:00'
      }
    ]
    pagination.total = tableData.value.length
    loading.value = false
  }, 500)
}

// ============================================================================
// 操作函数
// ============================================================================

// 查询
const handleSearch = () => {
  ElMessage.success('查询成功')
  pagination.currentPage = 1
  loadData()
}

// 重置
const handleReset = () => {
  filterForm.statuses = []
  filterForm.categories = []
  filterForm.priorities = []
  filterForm.assignee = ''
  filterForm.project = ''
  filterForm.dateRange = null
  filterForm.keyword = ''
  pagination.currentPage = 1
  ElMessage.success('已重置筛选条件')
  loadData()
}

// 创建问题单
const handleCreate = () => {
  router.push('/issues/create')
}

// 查看详情
const handleView = (row: IssueItem) => {
  router.push(`/issues/${row.id}`)
}

// 编辑
const handleEdit = (row: IssueItem) => {
  router.push(`/issues/${row.id}?mode=edit`)
}

// 删除
const handleDelete = (row: IssueItem) => {
  ElMessageBox.confirm(
    `确定要删除问题单 ${row.id} 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // TODO: 调用删除 API
    ElMessage.success('删除成功')
    loadData()
  }).catch(() => {
    // 取消删除
  })
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadData()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
  loadData()
}

// ============================================================================
// 生命周期
// ============================================================================
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.issue-list-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
}

.filter-form .el-form-item {
  margin-bottom: 10px;
  margin-right: 20px;
}

.action-bar {
  margin-bottom: 20px;
}

.table-card {
  background-color: #fff;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>
