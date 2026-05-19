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

// Composable 函数
export function useTaskForm(
  props: TaskExecutionFormProps,
  emit: TaskExecutionFormEmits
) {
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

  return {
    formData,
    formRef,
    isEditMode,
    statusOptions,
    priorityOptions,
    verificationOptions,
    handleSubmit,
    handleCancel,
    loadTaskData,
  }
}
