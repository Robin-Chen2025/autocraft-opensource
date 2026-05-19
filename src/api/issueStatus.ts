/**
 * 问题状态流转 API 封装
 * 基于 Vue3 + TypeScript + Axios
 */
import axios, { type AxiosResponse, type AxiosError } from 'axios'
import type { IssueStatus } from '@/types/issue'

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
    return response
  },
  (error: AxiosError) => {
    let errorMessage = '请求失败，请稍后重试'

    if (error.response) {
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
          errorMessage = '无权访问该资源'
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
      errorMessage = '网络错误，请检查网络连接'
    } else {
      errorMessage = error.message || '未知错误'
    }

    return Promise.reject(new Error(errorMessage))
  }
)

// ============================================================================
// 类型定义
// ============================================================================

/**
 * 状态变更请求接口
 */
export interface IssueStatusChangeRequest {
  /** 目标状态 */
  to_status: IssueStatus
  /** 变更原因（可选） */
  reason?: string
}

/**
 * 状态变更响应接口
 */
export interface IssueStatusChangeResponse {
  /** 操作消息 */
  message: string
  /** 问题单号 */
  issue_no?: string
}

/**
 * 状态日志记录接口
 */
export interface IssueStatusLog {
  /** 日志 ID */
  id: number
  /** 问题 ID */
  issue_id: number
  /** 变更前状态 */
  from_status: string
  /** 变更后状态 */
  to_status: string
  /** 操作人 */
  operator: string
  /** 操作人角色（可选） */
  operator_role?: string
  /** 变更原因（可选） */
  reason?: string
  /** 创建时间 */
  created_at: string
}

/**
 * 状态日志列表响应接口
 */
export interface IssueStatusLogListResponse {
  /** 总记录数 */
  total: number
  /** 日志列表 */
  items: IssueStatusLog[]
}

/**
 * 状态流转规则接口（可选，用于前端校验）
 */
export interface StatusTransitionRule {
  /** 当前状态 */
  from: IssueStatus
  /** 允许的目标状态列表 */
  allowedTo: IssueStatus[]
  /** 流转说明 */
  description: string
}

// ============================================================================
// 状态流转规则常量（与后端保持一致）
// ============================================================================

/**
 * 状态流转规则映射
 * key=当前状态，value=允许流转的目标状态列表
 */
export const STATUS_TRANSITION_RULES: Record<IssueStatus, IssueStatus[]> = {
  '新建': ['处理中', '已关闭'],
  '处理中': ['已解决', '新建'],
  '已解决': ['已关闭', '处理中'],
  '已关闭': ['处理中'],
  'open': ['resolved', 'closed'],
  'resolved': ['closed', 'open'],
  'closed': ['open']
}

/**
 * 状态流转说明映射
 */
export const STATUS_TRANSITION_DESCRIPTION: Record<string, string> = {
  '新建 - 处理中': '问题开始处理',
  '新建 - 已关闭': '问题直接关闭（无需处理）',
  '处理中 - 已解决': '问题已解决',
  '处理中 - 新建': '问题重新打开',
  '已解决 - 已关闭': '问题确认关闭',
  '已解决 - 处理中': '问题重新处理',
  '已关闭 - 处理中': '问题重新激活'
}

// ============================================================================
// 工具函数
// ============================================================================

/**
 * 校验状态流转是否合法
 * @param fromStatus 当前状态
 * @param toStatus 目标状态
 * @returns { valid: 是否合法，message: 错误信息/说明 }
 */
export function validateStatusTransition(
  fromStatus: IssueStatus,
  toStatus: IssueStatus
): { valid: boolean; message: string } {
  // 状态相同，不允许
  if (fromStatus === toStatus) {
    return { valid: false, message: '目标状态与当前状态相同，无需变更' }
  }

  // 检查流转规则
  const allowedTransitions = STATUS_TRANSITION_RULES[fromStatus]
  if (!allowedTransitions || !allowedTransitions.includes(toStatus)) {
    return {
      valid: false,
      message: `不允许从状态'${fromStatus}'流转到'${toStatus}'，允许的目标状态：${allowedTransitions?.join('、') || '无'}`
    }
  }

  // 获取流转说明
  const transitionDesc = STATUS_TRANSITION_DESCRIPTION[`${fromStatus} - ${toStatus}`] || '状态变更'
  return { valid: true, message: transitionDesc }
}

/**
 * 获取状态流转说明
 * @param fromStatus 当前状态
 * @param toStatus 目标状态
 * @returns 流转说明
 */
export function getStatusTransitionDescription(
  fromStatus: IssueStatus,
  toStatus: IssueStatus
): string {
  const result = validateStatusTransition(fromStatus, toStatus)
  return result.message
}

// ============================================================================
// API 方法
// ============================================================================

/**
 * 变更问题状态
 * @param issueId 问题 ID
 * @param data 状态变更请求数据
 * @param operator 操作人（可选，默认 system）
 * @returns 变更结果
 */
export const changeIssueStatus = async (
  issueId: number,
  data: IssueStatusChangeRequest,
  operator?: string
): Promise<IssueStatusChangeResponse> => {
  const response: AxiosResponse<IssueStatusChangeResponse> = await apiClient.post(
    `/api/issues/${issueId}/status`,
    data,
    {
      params: {
        operator: operator || 'system'
      }
    }
  )
  return response.data
}

/**
 * 获取问题状态变更日志
 * @param issueId 问题 ID
 * @param limit 返回记录数量限制（可选，默认 50，最大 500）
 * @returns 状态日志列表
 */
export const getStatusLogs = async (
  issueId: number,
  limit?: number
): Promise<IssueStatusLogListResponse> => {
  const params: Record<string, any> = {}
  if (limit !== undefined) {
    params.limit = limit
  }

  const response: AxiosResponse<IssueStatusLogListResponse> = await apiClient.get(
    `/api/issues/${issueId}/status-logs`,
    { params }
  )
  return response.data
}

// ============================================================================
// 默认导出
// ============================================================================

export default {
  changeIssueStatus,
  getStatusLogs,
  validateStatusTransition,
  getStatusTransitionDescription,
  STATUS_TRANSITION_RULES,
  STATUS_TRANSITION_DESCRIPTION
}
