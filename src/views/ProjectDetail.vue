<template>
  <div class="project-detail-page">
    <!-- 返回按钮和刷新按钮 -->
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

    <!-- 项目不存在 -->
    <el-empty v-else-if="!project" description="项目不存在" />

    <!-- 项目详情 -->
    <template v-else>
      <!-- 项目基本信息卡片 -->
      <el-card class="project-info-card" shadow="never">
        <template #header>
          <span class="card-title">项目基本信息</span>
        </template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="项目名称">
            {{ project.profile_name }}
          </el-descriptions-item>
          <el-descriptions-item label="项目类型">
            <el-tag :type="project.profile_type === 'template' ? 'warning' : 'primary'">
              {{ project.profile_type === 'template' ? '模板' : '实例' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(project.status)">
              {{ getStatusLabel(project.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="技术栈">
            {{ project.tech_stack || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(project.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="项目路径">
            {{ project.root_path || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 阶段/计划折叠树 -->
      <el-card class="tree-card" shadow="never">
        <template #header>
          <span class="card-title">项目结构</span>
        </template>
        <div class="tree-container">
          <template v-for="phase in phases" :key="phase.phase_record_id">
            <!-- 阶段 -->
            <div class="phase-item">
              <div class="phase-header" @click="togglePhase(phase.phase_record_id)">
                <el-icon class="expand-icon" :class="{ expanded: expandedPhases.has(phase.phase_record_id) }">
                  <ArrowRight />
                </el-icon>
                <span class="phase-name">{{ phase.phase_name }}</span>
                <el-tag :type="getStatusType(phase.status)" size="small">
                  {{ getStatusLabel(phase.status) }}
                </el-tag>
              </div>

              <!-- 计划 -->
              <div v-show="expandedPhases.has(phase.phase_record_id)" class="plan-list">
                <template v-for="plan in getPlansByPhase(phase.phase_record_id)" :key="plan.plan_id">
                  <div class="plan-item" @click="handlePlanClick(plan.plan_id)">
                    <el-icon class="plan-icon"><Document /></el-icon>
                    <span class="plan-name">{{ plan.plan_name }}</span>
                    <el-tag :type="getStatusType(plan.status)" size="small">
                      {{ getStatusLabel(plan.status) }}
                    </el-tag>
                  </div>
                </template>
                <div v-if="getPlansByPhase(phase.phase_record_id).length === 0" class="no-data">
                  暂无工作计划
                </div>
              </div>
            </div>
          </template>
          <el-empty v-if="phases.length === 0" description="暂无阶段数据" :image-size="80" />
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, ArrowRight, Refresh, Document } from '@element-plus/icons-vue'
import { getProfile, getProfilePhases, getPlans, type Profile, type Plan } from '@/api/profiles'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

// 数据
const loading = ref(false)
const project = ref<Profile | null>(null)
const phases = ref<any[]>([])
const plans = ref<Plan[]>([])

// 展开状态
const expandedPhases = ref<Set<string>>(new Set())

// 加载数据
const loadData = async () => {
  const profileId = route.params.profile_id as string
  if (!profileId) {
    ElMessage.error('缺少项目 ID')
    return
  }

  loading.value = true
  try {
    // 并行加载所有数据
    const [profileData, phasesData, plansData] = await Promise.all([
      getProfile(profileId),
      getProfilePhases(profileId),
      getPlans(profileId)
    ])

    project.value = profileData
    phases.value = phasesData.sort((a, b) => (a.phase_order || 0) - (b.phase_order || 0))
    plans.value = plansData

    // 默认展开第一个阶段
    if (phases.value.length > 0) {
      expandedPhases.value.add(phases.value[0].phase_record_id)
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载失败')
    project.value = null
  } finally {
    loading.value = false
  }
}

// 根据阶段 ID 获取计划
const getPlansByPhase = (phaseRecordId: string) => {
  // 自定义排序：按执行顺序
  const moduleOrder = ['INFRA', 'M01', 'M06', 'M02', 'M04', 'M03', 'L3']
  const typeOrder = ['BE-DEV', 'BE-L2', 'FE-DEV', 'FE-L2', 'E2E']
  
  const getModuleIndex = (name: string) => {
    for (let i = 0; i < moduleOrder.length; i++) {
      if (name.includes(moduleOrder[i])) return i
    }
    return 99
  }
  
  const getTypeIndex = (name: string) => {
    for (let i = 0; i < typeOrder.length; i++) {
      if (name.includes(typeOrder[i])) return i
    }
    // L3-E2E特殊处理
    if (name.includes('E2E')) return 4
    return 99
  }
  
  const getSequence = (name: string) => {
    // 提取编号：WP-XXX-YYY-001 → 001
    const match = name.match(/-(\d+|Final)$/)
    return match ? (match[1] === 'Final' ? 999 : parseInt(match[1], 10)) : 0
  }
  
  return plans.value
    .filter(plan => plan.phase_record_id === phaseRecordId)
    .sort((a, b) => {
      const aName = a.plan_name || ''
      const bName = b.plan_name || ''
      
      // 先按模块排序
      const aModule = getModuleIndex(aName)
      const bModule = getModuleIndex(bName)
      if (aModule !== bModule) return aModule - bModule
      
      // 再按类型排序
      const aType = getTypeIndex(aName)
      const bType = getTypeIndex(bName)
      if (aType !== bType) return aType - bType
      
      // 最后按编号排序
      return getSequence(aName) - getSequence(bName)
    })
}

// 切换阶段展开/折叠
const togglePhase = (phaseRecordId: string) => {
  if (expandedPhases.value.has(phaseRecordId)) {
    expandedPhases.value.delete(phaseRecordId)
  } else {
    expandedPhases.value.add(phaseRecordId)
  }
}

// 点击计划
const handlePlanClick = (planId: string) => {
  router.push(`/plans/${planId}`)
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
    draft: 'info',
    pending: 'info',
    active: 'success',
    in_progress: 'warning',
    running: 'warning',
    completed: 'success',
    success: 'success',
    paused: 'warning',
    archived: 'info',
    failed: 'danger',
    blocked: 'danger',
    skipped: 'info'
  }
  return typeMap[status] || 'info'
}

// 状态标签映射
const getStatusLabel = (status?: string): string => {
  if (!status) return '-'
  const labelMap: Record<string, string> = {
    draft: '草稿',
    pending: '待开始',
    active: '进行中',
    in_progress: '进行中',
    running: '运行中',
    completed: '已完成',
    success: '成功',
    paused: '已暂停',
    archived: '已归档',
    failed: '失败',
    blocked: '已阻塞',
    skipped: '已跳过'
  }
  return labelMap[status] || status
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
.project-detail-page {
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

.project-info-card {
  margin-bottom: 20px;
}

.tree-card {
  background-color: #fff;
}

.tree-container {
  padding: 10px 0;
}

/* 阶段样式 */
.phase-item {
  margin-bottom: 10px;
}

.phase-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background-color: #fff;
  border-left: 4px solid #409eff;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.phase-header:hover {
  background-color: #f5f7fa;
}

.phase-name {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-left: 8px;
}

/* 计划样式 */
.plan-list {
  margin-left: 24px;
  margin-top: 8px;
}

.plan-item {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  background-color: #fafafa;
  border-left: 3px solid #67c23a;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: 6px;
}

.plan-item:hover {
  background-color: #f0f2f5;
}

.plan-icon {
  font-size: 14px;
  color: #909399;
  margin-right: 8px;
}

.plan-name {
  flex: 1;
  font-size: 13px;
  color: #606266;
}

/* 展开图标 */
.expand-icon {
  font-size: 14px;
  color: #909399;
  transition: transform 0.2s;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

/* 无数据提示 */
.no-data {
  padding: 8px 12px;
  color: #909399;
  font-size: 13px;
  font-style: italic;
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
  background-color: rgba(230, 162, 60, 0.1);
  border-color: rgba(230, 162, 60, 0.2);
  color: #e6a23c;
}
</style>
