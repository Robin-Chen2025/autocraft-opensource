/**
 * Issue Assignment 问题分配 API 封装
 * 基于 Vue3 + TypeScript + Axios
 */
import axios, { type AxiosResponse, type AxiosError } from 'axios'

// ============================================================================
// 类型定义
// ============================================================================

/**
 * 分配 Issue 请求参数
 */
export interface IssueAssignRequest {
  /** 处理人 */
  assignee: string
  /** 截止日期（可选） */
  due_date?: string
  /** 分配说明（可选） */
  assign_note?: string
}

/**
 * 分配日志记录
 */
export interface IssueAssignLog {
  /** 日志 ID */
  id: number
  /** Issue ID */
  issue_id: number
  /** 变更前的被指派人（首次分配时为 null） */
  from_assignee: string | null
  /** 变更后的被指派人 */
  to_assignee: string | null
  /** 指派操作人 */
  assigned_by: string
  /** 截止日期 */
  due_date: string | null
  /** 指派备注 */
  note: string | null
  /** 创建时间，ISO 8601 格式 */
  created_at: string
}

/**
 * 通用消息响应
 */
export interface MessageResponse {
  /** 消息内容 */
  message: string
  /** 问题编号 */
  issue_no?: string
}

// ============================================================================
// API 基础配置
// ============================================================================

const API_BASE_URL = '/api'

// 创建 axios 实例（复用 issue.ts 的配置）
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
          errorMessage = data?.detail || data?.message || '请求参数错误'
          break
        case 401:
          errorMessage = '未授权，请登录后重试'
          break
        case 403:
          errorMessage = '无权执行该操作'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        default:
          errorMessage = data?.detail || data?.message || `请求失败 (${status})`
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
 * 分配 Issue（首次分配）
 * @param issueId Issue ID
 * @param data 分配请求数据
 * @param assignedBy 分配操作人
 * @returns 分配结果
 */
export const assignIssue = async (
  issueId: number,
  data: IssueAssignRequest,
  assignedBy: string
): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.post(
    `/api/issues/${issueId}/assign`,
    data,
    {
      params: { assigned_by: assignedBy }
    }
  )
  return response.data
}

/**
 * 重新分配 Issue（变更处理人）
 * @param issueId Issue ID
 * @param data 重新分配请求数据
 * @param assignedBy 分配操作人
 * @returns 重新分配结果
 */
export const reassignIssue = async (
  issueId: number,
  data: IssueAssignRequest,
  assignedBy: string
): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.put(
    `/api/issues/${issueId}/assign`,
    data,
    {
      params: { assigned_by: assignedBy }
    }
  )
  return response.data
}

/**
 * 获取 Issue 分配历史记录
 * @param issueId Issue ID
 * @param limit 返回记录数量限制（可选）
 * @returns 分配日志列表
 */
export const getAssignLogs = async (
  issueId: number,
  limit?: number
): Promise<IssueAssignLog[]> => {
  const params: { limit?: number } = {}
  if (limit !== undefined && limit > 0) {
    params.limit = limit
  }

  const response: AxiosResponse<IssueAssignLog[]> = await apiClient.get(
    `/api/issues/${issueId}/assign/logs`,
    { params }
  )
  return response.data
}

/**
 * 取消 Issue 分配
 * @param issueId Issue ID
 * @param unassignedBy 取消分配操作人
 * @param reason 取消原因（可选）
 * @returns 取消分配结果
 */
export const unassignIssue = async (
  issueId: number,
  unassignedBy: string,
  reason?: string
): Promise<MessageResponse> => {
  const params: { unassigned_by: string; reason?: string } = {
    unassigned_by: unassignedBy
  }
  if (reason !== undefined && reason !== '') {
    params.reason = reason
  }

  const response: AxiosResponse<MessageResponse> = await apiClient.delete(
    `/api/issues/${issueId}/assign`,
    { params }
  )
  return response.data
}

// ============================================================================
// 默认导出
// ============================================================================

export default {
  assignIssue,
  reassignIssue,
  getAssignLogs,
  unassignIssue
}
