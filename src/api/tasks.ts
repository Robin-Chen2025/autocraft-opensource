/**
 * 任务管理 API 封装
 */
import axios, { type AxiosResponse } from 'axios'

// API 基础配置
const API_BASE_URL = '/api'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000
})

// ==================== 类型定义 ====================

/** 任务状态 */
export type TaskStatus = '新建' | '待执行' | '进行中' | '待验证' | '完成' | '失败'

/** 任务优先级 */
export type TaskPriority = '高' | '中' | '低'

/** 验证结论 */
export type VerificationResult = '待验证' | '通过' | '不通过'

/** 任务数据 */
export interface Task {
  id: number
  task_no: string
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
  // === 新增字段：执行与验证时间线追踪 ===
  verification_log?: string
  exec_start_time?: string
  exec_estimated_complete?: string
  exec_complete_time?: string
  verify_start_time?: string
  verify_estimated_complete?: string
  verify_complete_time?: string
  created_at: string
  updated_at: string
}

/** 创建任务请求 */
export interface CreateTaskRequest {
  task_name: string
  plan_date?: string
  plan_complete_time?: string
  executor?: string
  status?: TaskStatus
  priority?: TaskPriority
  execution_steps?: string
  expected_result?: string
  execution_log?: string
  output_result?: string
  execution_date?: string
  verification_result?: VerificationResult
  verifier?: string
  verification_time?: string
  // === 新增字段：执行与验证时间线追踪 ===
  verification_log?: string
  exec_start_time?: string
  exec_estimated_complete?: string
  exec_complete_time?: string
  verify_start_time?: string
  verify_estimated_complete?: string
  verify_complete_time?: string
}

/** 更新任务请求 */
export interface UpdateTaskRequest {
  task_name?: string
  plan_date?: string
  plan_complete_time?: string
  executor?: string
  status?: TaskStatus
  priority?: TaskPriority
  execution_steps?: string
  expected_result?: string
  execution_log?: string
  output_result?: string
  execution_date?: string
  verification_result?: VerificationResult
  verifier?: string
  verification_time?: string
  // === 新增字段：执行与验证时间线追踪 ===
  verification_log?: string
  exec_start_time?: string
  exec_estimated_complete?: string
  exec_complete_time?: string
  verify_start_time?: string
  verify_estimated_complete?: string
  verify_complete_time?: string
}

/** 任务列表响应 */
export interface TaskListResponse {
  total: number
  items: Task[]
  page: number
  page_size: number
}

/** 任务详情响应 */
export interface TaskDetailResponse {
  data: Task
}

/** 通用消息响应 */
export interface MessageResponse {
  message: string
  task_no?: string
}

/** 查询参数 */
export interface TaskQueryParams {
  page?: number
  page_size?: number
  keyword?: string
  status?: string
  priority?: string
  // === 新增时间范围查询参数 ===
  plan_date_start?: string
  plan_date_end?: string
  plan_complete_start?: string
  plan_complete_end?: string
  verification_time_start?: string
  verification_time_end?: string
  exec_start_time_start?: string
  exec_start_time_end?: string
  exec_complete_time_start?: string
  exec_complete_time_end?: string
  verify_start_time_start?: string
  verify_start_time_end?: string
  verify_complete_time_start?: string
  verify_complete_time_end?: string
}

/** 任务列表查询参数（组件用） */
export interface TaskListQueryParams {
  page: number
  page_size: number
  keyword?: string
  status?: string | string[]
  priority?: string | string[]
  // === 新增时间范围查询参数 ===
  plan_date_start?: string
  plan_date_end?: string
  plan_complete_start?: string
  plan_complete_end?: string
  verification_time_start?: string
  verification_time_end?: string
  exec_start_time_start?: string
  exec_start_time_end?: string
  exec_complete_time_start?: string
  exec_complete_time_end?: string
  verify_start_time_start?: string
  verify_start_time_end?: string
  verify_complete_time_start?: string
  verify_complete_time_end?: string
}

// ==================== API 方法 ====================

/**
 * 创建任务
 */
export const createTask = async (data: CreateTaskRequest): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.post('/tasks', data)
  return response.data
}

/**
 * 获取任务列表
 */
export const getTasks = async (params: TaskQueryParams = {}): Promise<TaskListResponse> => {
  const response: AxiosResponse<TaskListResponse> = await apiClient.get('/tasks', { params })
  return response.data
}

/**
 * 获取任务详情
 */
export const getTaskDetail = async (taskNo: string): Promise<Task> => {
  const response: AxiosResponse<TaskDetailResponse> = await apiClient.get(`/tasks/${taskNo}`)
  return response.data.data
}

/**
 * 更新任务
 */
export const updateTask = async (taskNo: string, data: UpdateTaskRequest): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.put(`/tasks/${taskNo}`, data)
  return response.data
}

/**
 * 删除任务
 */
export const deleteTask = async (taskNo: string): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.delete(`/tasks/${taskNo}`)
  return response.data
}

/**
 * 获取状态选项
 */
export const getStatusOptions = async (): Promise<string[]> => {
  const response: AxiosResponse<{ data: string[] }> = await apiClient.get('/dict/status')
  return response.data.data
}

/**
 * 获取优先级选项
 */
export const getPriorityOptions = async (): Promise<string[]> => {
  const response: AxiosResponse<{ data: string[] }> = await apiClient.get('/dict/priority')
  return response.data.data
}

/**
 * 获取验证结论选项
 */
export const getVerificationOptions = async (): Promise<string[]> => {
  const response: AxiosResponse<{ data: string[] }> = await apiClient.get('/dict/verification')
  return response.data.data
}

export default {
  createTask,
  getTasks,
  getTaskDetail,
  updateTask,
  deleteTask,
  getStatusOptions,
  getPriorityOptions,
  getVerificationOptions
}
