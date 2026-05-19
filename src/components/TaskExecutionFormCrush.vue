<template>
  <div class="task-form-container">
    <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
      <!-- 基础信息区域 -->
      <el-card>
        <template #header>基础信息</template>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="任务单号">
              <el-input v-model="formData.task_no" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="任务名称" prop="task_name">
              <el-input v-model="formData.task_name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计划日期">
              <el-date-picker v-model="formData.plan_date" type="date" placeholder="选择日期" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划完成时间">
              <el-date-picker v-model="formData.plan_complete_time" type="datetime" placeholder="选择时间" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="执行人">
              <el-input v-model="formData.executor" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" placeholder="选择状态">
                <el-option
                  v-for="option in statusOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="formData.priority" placeholder="选择优先级">
                <el-option
                  v-for="option in priorityOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 执行信息区域 -->
      <el-card style="margin-top: 20px;">
        <template #header>执行信息</template>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="执行步骤">
              <el-input v-model="formData.execution_steps" type="textarea" :rows="4" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="预期结果">
              <el-input v-model="formData.expected_result" type="textarea" :rows="3" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="执行日志">
              <el-input v-model="formData.execution_log" type="textarea" :rows="4" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="输出结果">
              <el-input v-model="formData.output_result" type="textarea" :rows="3" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="执行日期">
              <el-date-picker v-model="formData.execution_date" type="date" placeholder="选择日期" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 验证信息区域 -->
      <el-card style="margin-top: 20px;">
        <template #header>验证信息</template>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="验证结论" prop="verification_result">
              <el-select v-model="formData.verification_result" placeholder="选择验证结果">
                <el-option
                  v-for="option in verificationOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="验证人">
              <el-input v-model="formData.verifier" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="验证时间">
              <el-date-picker v-model="formData.verification_time" type="datetime" placeholder="选择时间" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 底部按钮 -->
      <div style="margin-top: 20px; text-align: center;">
        <el-button type="primary" @click="handleSubmit">保存</el-button>
        <el-button @click="handleCancel">取消</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import {
  createTask,
  updateTask,
  getTaskDetail,
  getStatusOptions,
  getPriorityOptions,
  getVerificationOptions,
} from '../api/tasks'
import type {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  TaskStatus,
  TaskPriority,
  VerificationResult,
} from '../api/tasks'

// Props 定义
export interface TaskExecutionFormProps {
  taskNo?: string // 传入则编辑模式
}

// Emits 定义
export interface TaskExecutionFormEmits {
  (e: 'success', taskNo: string): void
  (e: 'cancel'): void
}

// Form 数据类型
export interface FormData {
  task_no?: string
  task_name: string
  plan_date?: string
  plan_complete_time?: string
  executor?: string
  status: TaskStatus
  priority: TaskPriority
  execution_steps?: string
  expected_result?: string
  execution_log?: string
  output_result?: string
  execution_date?: string
  verification_result: VerificationResult
  verifier?: string
  verification_time?: string
}

// 表单验证规则
export const formRules = {
  task_name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur' },
  ],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  verification_result: [
    { required: true, message: '请选择验证结果', trigger: 'change' },
  ],
}

// Props 和 emits
const props = withDefaults(defineProps<TaskExecutionFormProps>(), {
  taskNo: undefined,
})

const emit = defineEmits<TaskExecutionFormEmits>()

// 表单 ref
const formRef = ref<FormInstance>()

// 是否为编辑模式
const isEditMode = computed(() => !!props.taskNo)

// 选项数据
const statusOptions = ref<{ label: string; value: TaskStatus }[]>([])
const priorityOptions = ref<{ label: string; value: TaskPriority }[]>([])
const verificationOptions = ref<
  { label: string; value: VerificationResult }[]
>([])

// 表单数据
const formData = ref<FormData>({
  task_name: '',
  status: 'pending' as TaskStatus,
  priority: 'medium' as TaskPriority,
  verification_result: 'unverified' as VerificationResult,
})

// 加载选项数据
const loadOptions = async () => {
  try {
    const [statusList, priorityList, verificationList] = await Promise.all([
      getStatusOptions(),
      getPriorityOptions(),
      getVerificationOptions(),
    ])
    // API 返回 string[]，需要转换为 { label, value } 格式
    statusOptions.value = statusList.map((item) => ({ label: item, value: item as TaskStatus }))
    priorityOptions.value = priorityList.map((item) => ({ label: item, value: item as TaskPriority }))
    verificationOptions.value = verificationList.map((item) => ({
      label: item,
      value: item as VerificationResult,
    }))
  } catch (error) {
    ElMessage.error('加载选项数据失败')
    console.error('加载选项数据失败:', error)
  }
}

// 加载任务详情（编辑模式）
const loadTaskData = async () => {
  if (!props.taskNo) return

  try {
    // API 直接返回 Task，不需要访问 .data
    const task: Task = await getTaskDetail(props.taskNo)

    // 填充表单数据
    formData.value = {
      task_no: task.task_no,
      task_name: task.task_name,
      plan_date: task.plan_date,
      plan_complete_time: task.plan_complete_time,
      executor: task.executor,
      status: task.status,
      priority: task.priority,
      execution_steps: task.execution_steps,
      expected_result: task.expected_result,
      execution_log: task.execution_log,
      output_result: task.output_result,
      execution_date: task.execution_date,
      verification_result: task.verification_result,
      verifier: task.verifier,
      verification_time: task.verification_time,
    }
  } catch (error) {
    ElMessage.error('加载任务详情失败')
    console.error('加载任务详情失败:', error)
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    if (isEditMode.value) {
      // 更新任务
      const updateData: UpdateTaskRequest = {
        task_name: formData.value.task_name,
        plan_date: formData.value.plan_date,
        plan_complete_time: formData.value.plan_complete_time,
        executor: formData.value.executor,
        status: formData.value.status,
        priority: formData.value.priority,
        execution_steps: formData.value.execution_steps,
        expected_result: formData.value.expected_result,
        execution_log: formData.value.execution_log,
        output_result: formData.value.output_result,
        execution_date: formData.value.execution_date,
        verification_result: formData.value.verification_result,
        verifier: formData.value.verifier,
        verification_time: formData.value.verification_time,
      }
      await updateTask(props.taskNo!, updateData)
      ElMessage.success('任务更新成功')
      emit('success', props.taskNo!)
    } else {
      // 创建任务
      const createData: CreateTaskRequest = {
        task_name: formData.value.task_name,
        plan_date: formData.value.plan_date,
        plan_complete_time: formData.value.plan_complete_time,
        executor: formData.value.executor,
        status: formData.value.status,
        priority: formData.value.priority,
        execution_steps: formData.value.execution_steps,
        expected_result: formData.value.expected_result,
        execution_log: formData.value.execution_log,
        output_result: formData.value.output_result,
        execution_date: formData.value.execution_date,
        verification_result: formData.value.verification_result,
        verifier: formData.value.verifier,
        verification_time: formData.value.verification_time,
      }
      const res = await createTask(createData)
      ElMessage.success('任务创建成功')
      // API 直接返回 MessageResponse，task_no 在 res.task_no
      emit('success', res.task_no!)
    }
  } catch (error: any) {
    if (error?.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error(isEditMode.value ? '任务更新失败' : '任务创建失败')
    }
    console.error('表单提交失败:', error)
  }
}

// 取消操作
const handleCancel = () => {
  emit('cancel')
}

// 初始化
onMounted(() => {
  loadOptions()
  if (isEditMode.value) {
    loadTaskData()
  }
})
</script>

<style scoped>
/* CSS 变量 */
:root {
  --tech-primary: #00d4ff;
  --tech-primary-glow: rgba(0, 212, 255, 0.3);
  --tech-bg-dark: #0d1117;
  --tech-bg-card: #1a1f2e;
  --tech-border: #30363d;
  --tech-text-primary: #c9d1d9;
  --tech-text-secondary: #8b949e;
}

/* 表单容器 */
.task-form-container {
  background: linear-gradient(135deg, var(--tech-bg-dark) 0%, #161b22 100%);
  padding: 24px;
}

/* 卡片样式 */
.el-card {
  background: linear-gradient(145deg, var(--tech-bg-card) 0%, #21283a 100%);
  border: 1px solid var(--tech-primary);
  border-radius: 12px;
  box-shadow: 0 0 20px var(--tech-primary-glow), 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* 卡片头部 */
.el-card__header {
  background: linear-gradient(90deg, rgba(0, 212, 255, 0.1) 0%, transparent 100%);
  border-bottom: 1px solid var(--tech-border);
}

.el-card__header h3 {
  color: var(--tech-primary);
  text-shadow: 0 0 10px var(--tech-primary-glow);
  margin: 0;
}

/* 表单标签 */
.el-form-item__label {
  color: var(--tech-text-primary);
}

/* 输入框和选择器样式 */

/* 1. 输入框 */
.el-input__inner,
.el-textarea__inner {
  background-color: #0d1117 !important;
  border: 1px solid #30363d !important;
  color: #c9d1d9 !important;
  border-radius: 8px !important;
}

.el-input__inner:hover,
.el-textarea__inner:hover {
  border-color: #00d4ff !important;
}

.el-input__inner:focus,
.el-textarea__inner:focus {
  border-color: #00d4ff !important;
  box-shadow: 0 0 8px rgba(0, 212, 255, 0.4) !important;
}

/* 2. 只读输入框 */
.el-input.is-disabled .el-input__inner {
  background-color: #161b22 !important;
  color: #6e7681 !important;
}

/* 3. 选择器 */
.el-select .el-input__inner {
  background-color: #0d1117 !important;
  border: 1px solid #30363d !important;
  color: #c9d1d9 !important;
  border-radius: 8px !important;
}

.el-select .el-input__inner:hover {
  border-color: #00d4ff !important;
}

.el-select .el-input__inner:focus {
  border-color: #00d4ff !important;
  box-shadow: 0 0 8px rgba(0, 212, 255, 0.4) !important;
}

/* 4. 日期选择器 */
.el-date-editor.el-input__inner {
  background-color: #0d1117 !important;
  border: 1px solid #30363d !important;
  color: #c9d1d9 !important;
  border-radius: 8px !important;
}

.el-date-editor.el-input__inner:hover {
  border-color: #00d4ff !important;
}

.el-date-editor.el-input__inner:focus {
  border-color: #00d4ff !important;
  box-shadow: 0 0 8px rgba(0, 212, 255, 0.4) !important;
}

/* 按钮和下拉菜单样式 */

/* 1. 主按钮 */
.el-button--primary {
  background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%) !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4) !important;
}

.el-button--primary:hover {
  background: linear-gradient(135deg, #33ddff 0%, #00aadd 100%) !important;
  box-shadow: 0 6px 20px rgba(0, 212, 255, 0.6) !important;
}

/* 2. 默认按钮 */
.el-button:not(.el-button--primary) {
  background: #21262d !important;
  border: 1px solid #30363d !important;
  color: #c9d1d9 !important;
}

.el-button:not(.el-button--primary):hover {
  border-color: #00d4ff !important;
  color: #00d4ff !important;
}

/* 3. 下拉菜单 */
.el-select-dropdown {
  background: #1c2128 !important;
  border: 1px solid #30363d !important;
  border-radius: 8px !important;
}

/* 4. 下拉选项 */
.el-select-dropdown__item {
  color: #c9d1d9 !important;
}

.el-select-dropdown__item:hover {
  background: rgba(0, 212, 255, 0.15) !important;
  color: #00d4ff !important;
}

.el-select-dropdown__item.selected {
  background: rgba(0, 212, 255, 0.15) !important;
  color: #00d4ff !important;
  font-weight: 600 !important;
}

/* 5. 日期弹出层 */
.el-picker-panel {
  background: #1c2128 !important;
  border: 1px solid #30363d !important;
  border-radius: 12px !important;
}

/* 6. 日期选中 */
.el-date-table td.current span {
  background: #00d4ff !important;
  color: #0d1117 !important;
}
</style>
