```vue
<template>
  <el-dialog
    :model-value="visible"
    :title="mode === 'edit' ? '编辑问题单' : '新建问题单'"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      size="default"
    >
      <!-- 标题 -->
      <el-form-item label="标题" prop="title">
        <el-input
          v-model="formData.title"
          placeholder="请输入问题标题"
          maxlength="200"
          show-word-limit
          clearable
        />
      </el-form-item>

      <!-- 描述 -->
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="5"
          placeholder="请详细描述问题现象、影响范围、复现步骤等"
          maxlength="2000"
          show-word-limit
          resize="vertical"
        />
      </el-form-item>

      <!-- 分类 -->
      <el-form-item label="分类" prop="category">
        <el-select
          v-model="formData.category"
          placeholder="请选择问题分类"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="option in categoryOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>

      <!-- 优先级 -->
      <el-form-item label="优先级" prop="priority">
        <el-select
          v-model="formData.priority"
          placeholder="请选择优先级"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="option in priorityOptions"
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

      <!-- 关联任务 -->
      <el-form-item label="关联任务" prop="related_task_id">
        <el-input
          v-model="formData.related_task_id"
          placeholder="请输入关联任务单号（可选）"
          clearable
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="form-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          {{ mode === 'edit' ? '保存' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { Issue, CreateIssueRequest, IssuePriority, IssueCategory, OptionItem } from '@/types/issue'
import { priorityOptions, categoryOptions } from '@/types/issue'

// ============================================================================
// Props & Emits 定义
// ============================================================================

type FormMode = 'create' | 'edit'

interface Props {
  visible: boolean
  mode: FormMode
  initialData?: Partial<Issue> | null
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'submit', data: CreateIssueRequest): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'create',
  initialData: null
})

const emit = defineEmits<Emits>()

// ============================================================================
// 表单引用与状态
// ============================================================================

const formRef = ref<FormInstance>()
const loading = ref(false)

// ============================================================================
// 表单数据
// ============================================================================

interface IssueFormData {
  title: string
  description: string
  priority: IssuePriority | ''
  category: IssueCategory | ''
  related_task_id: string
}

const formData = reactive<IssueFormData>({
  title: '',
  description: '',
  priority: '',
  category: '',
  related_task_id: ''
})

// ============================================================================
// 表单验证规则
// ============================================================================

const formRules = computed<FormRules<IssueFormData>>(() => ({
  title: [
    { required: true, message: '请输入问题标题', trigger: 'blur' },
    { min: 5, max: 200, message: '标题长度在 5 到 200 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入问题描述', trigger: 'blur' },
    { min: 10, max: 2000, message: '描述长度在 10 到 2000 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择问题分类', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}))

// ============================================================================
// 选项数据（响应式）
// ============================================================================

const priorityOptionsReactive = reactive<OptionItem[]>(priorityOptions)
const categoryOptionsReactive = reactive<OptionItem[]>(categoryOptions)

// ============================================================================
// 初始化表单数据
// ============================================================================

const initFormData = () => {
  if (props.mode === 'edit' && props.initialData) {
    formData.title = props.initialData.title || ''
    formData.description = props.initialData.description || ''
    formData.priority = props.initialData.priority || ''
    formData.category = props.initialData.category || ''
    formData.related_task_id = props.initialData.related_task_id || ''
  } else {
    resetFormData()
  }
}

const resetFormData = () => {
  formData.title = ''
  formData.description = ''
  formData.priority = ''
  formData.category = ''
  formData.related_task_id = ''
}

// ============================================================================
// 事件处理函数
// ============================================================================

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
  formRef.value?.resetFields()
  emit('cancel')
  handleClose()
}

/**
 * 提交表单
 */
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid, fields) => {
    if (valid) {
      loading.value = true
      try {
        const submitData: CreateIssueRequest = {
          title: formData.title,
          description: formData.description,
          priority: formData.priority as IssuePriority,
          category: formData.category as IssueCategory,
          related_task_id: formData.related_task_id || undefined
        }
        emit('submit', submitData)
        ElMessage.success(props.mode === 'edit' ? '问题单已更新' : '问题单已创建')
      } catch (error) {
        console.error('提交失败:', error)
        ElMessage.error('提交失败，请稍后重试')
      } finally {
        loading.value = false
      }
    } else {
      console.error('表单验证失败:', fields)
      ElMessage.warning('请完善表单信息')
    }
  })
}

// ============================================================================
// 监听器
// ============================================================================

// 监听 visible 变化，初始化表单数据
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      initFormData()
    }
  },
  { immediate: true }
)

// 监听 mode 或 initialData 变化，重新初始化表单
watch(
  () => [props.mode, props.initialData],
  () => {
    if (props.visible) {
      initFormData()
    }
  },
  { deep: true }
)
</script>

<style scoped>
.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式适配 */
@media screen and (max-width: 768px) {
  :deep(.el-dialog) {
    width: 90% !important;
  }

  :deep(.el-form-item__label) {
    width: 80px !important;
  }
}

@media screen and (max-width: 480px) {
  :deep(.el-dialog) {
    width: 95% !important;
  }

  :deep(.el-form-item__label) {
    width: 60px !important;
  }

  .form-footer {
    flex-direction: column;
    gap: 8px;
  }

  .form-footer .el-button {
    width: 100%;
  }
}
</style>
```
