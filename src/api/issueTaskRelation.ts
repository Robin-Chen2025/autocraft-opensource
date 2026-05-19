/**
 * Issue Task Relation API 封装
 * 基于 Vue3 + TypeScript + Axios
 */
import axios, { type AxiosResponse, type AxiosError } from 'axios'

// ============================================================================
// 类型定义
// ============================================================================

/**
 * Issue 与 Task 关联关系
 */
export interface IssueTaskRelation {
  /** 关联关系 ID */
  id: number
  /** Issue ID */
  issue_id: number
  /** Task ID */
  task_id: number
  /** 创建人 */
  created_by: string
  /** 创建时间 */
  created_at: string
}

/**
 * 任务基本信息
 */
export interface TaskInfo {
  /** 任务 ID */
  id: number
  /** 任务单号 */
  task_no: string
  /** 任务名称 */
  task_name: string
  /** 任务状态 */
  status: string
  /** 优先级 */
  priority: string
  /** 执行人 */
  executor?: string | null
}

/**
 * 关联任务列表响应
 */
export interface IssueTaskListResponse {
  /** 总记录数 */
  total: number
  /** 任务列表 */
  items: TaskInfo[]
}

/**
 * 通用消息响应
 */
export interface MessageResponse {
  /** 响应消息 */
  message: string
  /** 问题单号（可选） */
  issue_no?: string
}

/**
 * 关联任务请求参数
 */
export interface LinkTaskRequest {
  /** 任务 ID */
  task_id: number
  /** 创建人 */
  created_by: string
}

// ============================================================================
// API 基础配置
// ============================================================================

const API_BASE_URL = '/api'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000
})

// ============================================================================
// 响应拦截器
// ============================================================================

/**
 * 响应拦截器：统一处理响应数据
 */
apiClient.interceptors.response.use(
  (response) => {
    // 直接返回响应数据
    return response
  },
  (error: AxiosError) => {
    // 统一错误处理
    let errorMessage = '请求失败，请稍后重试'

    if (error.response) {
      // 服务器返回错误响应
      const status = error.response.status
      const data: any = error.response.data

      switch (status) {
        case 400:
          errorMessage = data?.message || data?.detail || '请求参数错误'
          break
        case 401:
          errorMessage = '未授权，请登录后重试'
          break
        case 403:
          errorMessage = '无权访问该资源'
          break
        case 404:
          // 从 detail 中提取错误信息
          errorMessage = data?.detail || '请求的资源不存在'
          break
        case 409:
          // 冲突（关联已存在）
          errorMessage = data?.detail || '资源冲突'
          break
        case 500:
          errorMessage = data?.detail || '服务器内部错误'
          break
        default:
          errorMessage = data?.message || data?.detail || `请求失败 (${status})`
      }
    } else if (error.request) {
      // 请求已发送但未收到响应
      errorMessage = '网络错误，请检查网络连接'
    } else {
      // 其他错误
      errorMessage = error.message || '未知错误'
    }

    // 抛出错误，供调用方处理
    return Promise.reject(new Error(errorMessage))
  }
)

// ============================================================================
// API 方法
// ============================================================================

/**
 * 关联任务到 Issue
 * @param issueId Issue ID
 * @param data 关联任务请求数据
 * @returns 关联结果
 */
export const linkTask = async (
  issueId: number,
  data: LinkTaskRequest
): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.post(
    `/api/issues/${issueId}/tasks`,
    null,
    {
      params: {
        task_id: data.task_id,
        created_by: data.created_by
      }
    }
  )
  return response.data
}

/**
 * 取消 Issue 与 Task 的关联
 * @param issueId Issue ID
 * @param taskId Task ID
 * @returns 取消关联结果
 */
export const unlinkTask = async (
  issueId: number,
  taskId: number
): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.delete(
    `/api/issues/${issueId}/tasks/${taskId}`
  )
  return response.data
}

/**
 * 获取 Issue 关联的任务列表
 * @param issueId Issue ID
 * @returns 关联任务列表
 */
export const getLinkedTasks = async (
  issueId: number
): Promise<IssueTaskListResponse> => {
  const response: AxiosResponse<IssueTaskListResponse> = await apiClient.get(
    `/api/issues/${issueId}/tasks`
  )
  return response.data
}

// ============================================================================
// 默认导出
// ============================================================================

export default {
  linkTask,
  unlinkTask,
  getLinkedTasks
}
