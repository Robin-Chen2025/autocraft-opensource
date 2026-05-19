<template>
  <div class="knowledge-search-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">知识库搜索</h1>
    </div>

    <!-- 筛选区域 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="关键词">
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索标题、内容或标签"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select
            v-model="filterForm.category"
            placeholder="全部"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="opt in categoryOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="作者">
          <el-input
            v-model="filterForm.author"
            placeholder="请输入作者"
            clearable
            style="width: 150px"
          />
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
        <el-form-item>
          <el-checkbox v-model="filterForm.is_featured" :label="false" border>
            <el-icon><Star /></el-icon>
            仅看优质
          </el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="action-left">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          创建知识条目
        </el-button>
      </div>
      <div class="action-right">
        <el-radio-group v-model="viewMode" size="default">
          <el-radio-button label="card">
            <el-icon><Grid /></el-icon>
            卡片
          </el-radio-button>
          <el-radio-button label="list">
            <el-icon><List /></el-icon>
            列表
          </el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 列表区域 -->
    <el-card class="content-card" shadow="never">
      <div v-loading="loading">
        <!-- 卡片视图 -->
        <div v-if="viewMode === 'card'" class="card-view">
          <el-row :gutter="20">
            <el-col
              v-for="item in tableData"
              :key="item.id"
              :xs="24"
              :sm="12"
              :md="8"
              :lg="6"
            >
              <el-card
                class="knowledge-card"
                shadow="hover"
                @click="handleView(item)"
              >
                <template #header>
                  <div class="card-header">
                    <span class="card-title">{{ item.title }}</span>
                    <el-tag
                      v-if="item.is_featured"
                      type="warning"
                      size="small"
                      effect="dark"
                    >
                      <el-icon><StarFilled /></el-icon>
                      优质
                    </el-tag>
                  </div>
                </template>
                <div class="card-body">
                  <p class="card-summary">{{ item.summary }}</p>
                  <div class="card-meta">
                    <el-tag :type="getCategoryType(item.category)" size="small">
                      {{ getCategoryLabel(item.category) }}
                    </el-tag>
                    <span class="card-author">{{ item.author }}</span>
                  </div>
                  <div class="card-stats">
                    <span class="stat-item">
                      <el-icon><View /></el-icon>
                      {{ item.view_count }}
                    </span>
                    <span class="stat-item">
                      <el-icon><Star /></el-icon>
                      {{ item.reference_count }}
                    </span>
                    <span class="stat-time">{{ formatDate(item.created_at) }}</span>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 列表视图 -->
        <div v-else class="list-view">
          <div
            v-for="item in tableData"
            :key="item.id"
            class="knowledge-list-item"
            @click="handleView(item)"
          >
            <div class="list-item-main">
              <div class="list-item-header">
                <h3 class="list-item-title">
                  {{ item.title }}
                  <el-tag
                    v-if="item.is_featured"
                    type="warning"
                    size="small"
                    effect="dark"
                    style="margin-left: 8px"
                  >
                    <el-icon><StarFilled /></el-icon>
                    优质
                  </el-tag>
                </h3>
                <div class="list-item-meta">
                  <el-tag :type="getCategoryType(item.category)" size="small">
                    {{ getCategoryLabel(item.category) }}
                  </el-tag>
                  <span class="meta-item">
                    <el-icon><User /></el-icon>
                    {{ item.author }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Clock /></el-icon>
                    {{ formatDate(item.created_at) }}
                  </span>
                </div>
              </div>
              <p class="list-item-summary">{{ item.summary }}</p>
              <div class="list-item-stats">
                <span class="stat-item">
                  <el-icon><View /></el-icon>
                  {{ item.view_count }} 浏览
                </span>
                <span class="stat-item">
                  <el-icon><Star /></el-icon>
                  {{ item.reference_count }} 引用
                </span>
              </div>
            </div>
            <div class="list-item-action">
              <el-button type="primary" link @click.stop="handleView(item)">
                查看详情
              </el-button>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty
          v-if="tableData.length === 0 && !loading"
          description="暂无数据"
        />
      </div>

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
import { Plus, Star, StarFilled, Grid, List, View, User, Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { Knowledge, KnowledgeCategory, KnowledgeQueryParams } from '@/types/knowledge'
import { categoryOptions } from '@/types/knowledge'

const router = useRouter()

// ============================================================================
// 视图模式
// ============================================================================
const viewMode = ref<'card' | 'list'>('card')

// ============================================================================
// 筛选表单
// ============================================================================
const filterForm = reactive({
  keyword: '',
  category: '' as KnowledgeCategory | '',
  author: '',
  dateRange: null as [Date, Date] | null,
  is_featured: false
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
const tableData = ref<Knowledge[]>([])

// ============================================================================
// 分类映射
// ============================================================================
const getCategoryType = (category: KnowledgeCategory) => {
  const option = categoryOptions.find(opt => opt.value === category)
  return option?.type || ''
}

const getCategoryLabel = (category: KnowledgeCategory) => {
  const option = categoryOptions.find(opt => opt.value === category)
  return option?.label || category
}

// ============================================================================
// 日期格式化
// ============================================================================
const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// ============================================================================
// 数据加载
// ============================================================================
const loadData = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params: KnowledgeQueryParams = {
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }

    // 添加筛选条件
    if (filterForm.keyword) {
      params.keyword = filterForm.keyword
    }
    if (filterForm.category) {
      params.category = filterForm.category
    }
    if (filterForm.author) {
      params.author = filterForm.author
    }
    if (filterForm.is_featured) {
      params.is_featured = true
    }
    if (filterForm.dateRange) {
      params.created_at_from = filterForm.dateRange[0].toISOString()
      params.created_at_to = filterForm.dateRange[1].toISOString()
    }

    // TODO: 调用实际 API
    // const response = await searchKnowledge(params)
    // tableData.value = response.items
    // pagination.total = response.total

    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 300))
    tableData.value = [
      {
        id: 'KB-20260324-0001',
        title: 'Vue3 + TypeScript 最佳实践指南',
        summary: '本文档详细介绍了在 Vue3 项目中使用 TypeScript 的最佳实践，包括组件定义、Props 类型、Emits 类型等核心内容。',
        content: '详细内容...',
        category: '技术文档',
        status: '已发布',
        author: '张三',
        created_at: '2026-03-20T10:30:00Z',
        updated_at: '2026-03-22T14:00:00Z',
        view_count: 1256,
        is_featured: true,
        tags: ['Vue3', 'TypeScript', '前端'],
        reference_count: 23,
        related_task_id: ''
      },
      {
        id: 'KB-20260324-0002',
        title: '数据库性能优化实战案例',
        summary: '通过实际案例分析，分享数据库查询优化的常用技巧和工具，包括索引优化、查询重写、执行计划分析等。',
        content: '详细内容...',
        category: '最佳实践',
        status: '已发布',
        author: '李四',
        created_at: '2026-03-19T09:15:00Z',
        updated_at: '2026-03-21T16:30:00Z',
        view_count: 892,
        is_featured: true,
        tags: ['数据库', '性能优化', 'MySQL'],
        reference_count: 15,
        related_task_id: ''
      },
      {
        id: 'KB-20260324-0003',
        title: '常见登录问题排查手册',
        summary: '汇总了常见的登录相关问题及其解决方案，包括密码错误、账号锁定、验证码问题等。',
        content: '详细内容...',
        category: '问题解决方案',
        status: '已发布',
        author: '王五',
        created_at: '2026-03-18T14:20:00Z',
        updated_at: '2026-03-20T11:00:00Z',
        view_count: 2341,
        is_featured: false,
        tags: ['登录', '问题排查', 'FAQ'],
        reference_count: 42,
        related_task_id: ''
      },
      {
        id: 'KB-20260324-0004',
        title: '新员工入职培训资料',
        summary: '包含公司技术栈介绍、开发环境搭建指南、代码规范说明等内容，帮助新员工快速融入团队。',
        content: '详细内容...',
        category: '培训资料',
        status: '已发布',
        author: '赵六',
        created_at: '2026-03-15T08:00:00Z',
        updated_at: '2026-03-18T10:00:00Z',
        view_count: 567,
        is_featured: false,
        tags: ['培训', '入职', '文档'],
        reference_count: 8,
        related_task_id: ''
      }
    ]
    pagination.total = tableData.value.length
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// ============================================================================
// 操作函数
// ============================================================================

// 查询
const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

// 重置
const handleReset = () => {
  filterForm.keyword = ''
  filterForm.category = ''
  filterForm.author = ''
  filterForm.dateRange = null
  filterForm.is_featured = false
  pagination.currentPage = 1
  loadData()
}

// 创建知识条目
const handleCreate = () => {
  router.push('/knowledge/create')
}

// 查看详情
const handleView = (row: Knowledge) => {
  router.push(`/knowledge/${row.id}`)
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
.knowledge-search-page {
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.action-left {
  display: flex;
  gap: 10px;
}

.action-right {
  display: flex;
  gap: 10px;
}

.content-card {
  background-color: #fff;
}

/* ============================================================================
   卡片视图样式
   ============================================================================ */
.card-view {
  padding: 10px 0;
}

.knowledge-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.knowledge-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.card-body {
  padding: 10px 0;
}

.card-summary {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.card-author {
  font-size: 12px;
  color: #909399;
}

.card-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-stats .stat-time {
  margin-left: auto;
}

/* ============================================================================
   列表视图样式
   ============================================================================ */
.list-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.knowledge-list-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.knowledge-list-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.list-item-main {
  flex: 1;
}

.list-item-header {
  margin-bottom: 12px;
}

.list-item-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.list-item-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

.list-item-summary {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.list-item-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: #909399;
}

.list-item-action {
  margin-left: 20px;
}

/* ============================================================================
   分页样式
   ============================================================================ */
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* ============================================================================
   响应式设计
   ============================================================================ */
@media (max-width: 768px) {
  .filter-form .el-form-item {
    margin-right: 10px;
  }

  .action-bar {
    flex-direction: column;
    gap: 10px;
  }

  .knowledge-list-item {
    flex-direction: column;
  }

  .list-item-action {
    margin-left: 0;
    margin-top: 12px;
    align-self: flex-end;
  }
}
</style>
