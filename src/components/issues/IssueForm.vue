<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑问题单' : '新建问题单'"
    width="700px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      size="default"
    >
      <!-- 问题标题 -->
      <el-form-item label="问题标题" prop="title">
        <el-input
          v-model="form.title"
          placeholder="请输入问题标题"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <!-- 问题描述 -->
      <el-form-item label="问题描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="5"
          placeholder="请详细描述问题现象、影响范围、复现步骤等"
          maxlength="2000"
          show-word-limit
        />
      </el-form-item>

      <!-- 问题分类 -->
      <el-form-item label="问题分类" prop="category">
        <el-select
          v-model="form.category"
          placeholder="请选择问题分类"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="option in categoryOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          >
            <span>{{ option.label }}</span>
            <el-tag
              :type="option.type"
              size="small"
              style="margin-left: 8px"
            >
              {{ option.label }}
            </el-tag>
          </el-option>
        </el-select>
      </el-form-item>

      <!-- 优先级 -->
      <el-form-item label="优先级" prop="priority">
        <el-radio-group v-model="form.priority">
          <el-radio-button
            v-for="option in priorityOptions"
            :key="option.value"
            :value="option.value"
          >
            <el-tag :type="option.type" size="small">{{ option.label }}</el-tag>
          </el-radio-button>
        </el-radio-group>
      </el-form-item>

      <!-- 关联项目 -->
      <el-form-item label="关联项目" prop="project_name">
        <el-select
          v-model="form.project_name"
          placeholder="请选择关联项目"
          clearable
          filterable
          style="width: 100%"
          @change="handleProjectChange"
        >
          <el-option
            v-for="project in projectOptions"
            :key="project.profile_id"
            :label="project.profile_name"
            :value="project.profile_name"
          >
            <span>{{ project.profile_name }}</span>
            <span v-if="project.project_type" style="color: #8492a6; font-size: 12px; margin-left: 8px">
              ({{ project.project_type }})
            </span>
          </el-option>
        </el-select>
      </el-form-item>

      <!-- 关联阶段 -->
      <el-form-item label="关联阶段" prop="stage_name">
        <el-select
          v-model="form.stage_name"
          placeholder="请选择关联阶段"
          clearable
          filterable
          style="width: 100%"
          :disabled="!form.project_name"
          @change="handleStageChange"
        >
          <el-option
            v-for="stage in stageOptions"
            :key="stage.phase_id"
            :label="stage.phase_name"
            :value="stage.phase_name"
          />
        </el-select>
      </el-form-item>

      <!-- 关联工作流 -->
      <el-form-item label="关联工作流" prop="workflow_name">
        <el-select
          v-model="form.workflow_name"
          placeholder="请选择关联工作流"
          clearable
          filterable
          style="width: 100%"
          :disabled="!form.stage_name"
        >
          <el-option
            v-for="workflow in workflowOptions"
            :key="workflow.workflow_id"
            :label="workflow.workflow_name"
            :value="workflow.workflow_name"
          />
        </el-select>
      </el-form-item>

      <!-- 关联任务单号 -->
      <el-form-item label="关联任务" prop="related_task_id">
        <el-input
          v-model="form.related_task_id"
          placeholder="请输入关联任务单号（可选）"
          clearable
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="form-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { Issue, CreateIssueRequest, IssuePriority, IssueCategory } from '@/types/issue'
import { priorityOptions, categoryOptions } from '@/types/issue'
import { getProfiles, getProfilePhases } from '@/api/profiles'

// ==================== Props & Emits ====================

interface Props {
  visible: boolean
  issue?: Issue | null
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: CreateIssueRequest): void
}

const props = withDefaults(defineProps<Props>(), {
  issue: null
})

const emit = defineEmits<Emits>()

// ==================== 表单引用与状态 ====================

const formRef = ref<FormInstance>()
const submitting = ref(false)

// ==================== 表单数据 ====================

interface IssueFormModel {
  title: string
  description: string
  priority: IssuePriority
  category?: IssueCategory | ''
  related_task_id?: string
  project_name?: string
  stage_name?: string
  workflow_name?: string
}

const form = ref<IssueFormModel>({
  title: '',
  description: '',
  priority: '中',
  category: undefined,
  related_task_id: undefined,
  project_name: undefined,
  stage_name: undefined,
  workflow_name: undefined
})

// ==================== 表单验证规则 ====================

const rules = computed<FormRules<IssueFormModel>>(() => ({
  title: [
    { required: true, message: '请输入问题标题', trigger: 'blur' },
    { min: 5, max: 200, message: '标题长度在 5 到 200 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入问题描述', trigger: 'blur' },
    { min: 10, max: 2000, message: '描述长度在 10 到 2000 个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  category: [
    { required: true, message: '请选择问题分类', trigger: 'change' }
  ]
}))

// ==================== 选项数据 ====================

const projectOptions = ref<any[]>([])
const stageOptions = ref<any[]>([])
const workflowOptions = ref<any[]>([])

// ==================== 计算属性 ====================

const isEdit = computed(() => !!props.issue)

// ==================== 数据加载 ====================

onMounted(async () => {
  await loadProjects()
})

/**
 * 加载项目列表
 */
const loadProjects = async () => {
  try {
    const res = await getProfiles({ page: 1, page_size: 100 })
    projectOptions.value = res.items || []
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

/**
 * 加载阶段列表
 */
const loadStages = async (profileId: string) => {
  try {
    const res = await getProfilePhases(profileId)
    stageOptions.value = res || []
  } catch (error) {
    console.error('加载阶段列表失败:', error)
    stageOptions.value = []
  }
}

/**
 * 加载工作流列表（已禁用，工作流层已删除）
 */
const loadWorkflows = async (profileId: string, phaseId?: string) => {
  // 工作流层已删除，返回空列表
  workflowOptions.value = []
}

// ==================== 事件处理 ====================

/**
 * 项目变更处理
 */
const handleProjectChange = async (projectName: string) => {
  // 清空阶段和工作流选择
  form.value.stage_name = undefined
  form.value.workflow_name = undefined
  stageOptions.value = []
  workflowOptions.value = []

  if (projectName) {
    const project = projectOptions.value.find(p => p.profile_name === projectName)
    if (project) {
      await loadStages(project.profile_id)
    }
  }
}

/**
 * 阶段变更处理
 */
const handleStageChange = async (stageName: string) => {
  // 清空工作流选择
  form.value.workflow_name = undefined
  workflowOptions.value = []

  if (stageName && form.value.project_name) {
    const project = projectOptions.value.find(p => p.profile_name === form.value.project_name)
    const stage = stageOptions.value.find(s => s.phase_name === stageName)
    if (project && stage) {
      await loadWorkflows(project.profile_id, stage.phase_id)
    }
  }
}

/**
 * 关闭对话框
 */
const handleClose = () => {
  emit('update:visible', false)
}

/**
 * 取消操作
 */
const handleCancel = () => {
  handleClose()
}

/**
 * 提交表单
 */
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const submitData: CreateIssueRequest = {
          title: form.value.title,
          description: form.value.description,
          priority: form.value.priority,
          category: form.value.category!,
          related_task_id: form.value.related_task_id
        }
        emit('submit', submitData)
        handleClose()
        ElMessage.success(isEdit ? '问题单已更新' : '问题单已创建')
      } catch (error) {
        console.error('提交失败:', error)
        ElMessage.error('提交失败，请稍后重试')
      } finally {
        submitting.value = false
      }
    }
  })
}

/**
 * 重置表单
 */
const resetForm = () => {
  form.value = {
    title: '',
    description: '',
    priority: '中',
    category: undefined,
    related_task_id: undefined,
    project_name: undefined,
    stage_name: undefined,
    workflow_name: undefined
  }
  formRef.value?.clearValidate()
  stageOptions.value = []
  workflowOptions.value = []
}

// ==================== 监听器 ====================

watch(
  () => props.issue,
  (newIssue) => {
    if (newIssue) {
      form.value = {
        title: newIssue.title,
        description: newIssue.description,
        priority: newIssue.priority,
        category: newIssue.category,
        related_task_id: newIssue.related_task_id,
        project_name: newIssue.project_name,
        stage_name: newIssue.stage_name,
        workflow_name: newIssue.workflow_name
      }
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      loadProjects()
    }
  }
)
</script>

<style scoped>
.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-select-dropdown__item.selected) {
  font-weight: normal;
}
</style>
