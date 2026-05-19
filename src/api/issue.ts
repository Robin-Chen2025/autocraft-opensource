/**
 * 问题跟踪 API 封装
 * 基于 Vue3 + TypeScript + Axios
 */
import axios, { type AxiosResponse, type AxiosError } from 'axios'
import type {
  Issue,
  CreateIssueRequest,
  UpdateIssueRequest,
  IssueQueryParams,
  IssueListResponse
} from '@/types/issue'

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
          errorMessage = data?.message || '请求参数错误'
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
          errorMessage = data?.message || `请求失败 (${status})`
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
// 类型定义
// ============================================================================

/** 通用消息响应 */
export interface MessageResponse {
  message: string
  id?: string
}

/** 问题详情响应 */
export interface IssueDetailResponse {
  data: Issue
}

// ============================================================================
// API 方法
// ============================================================================

/**
 * 创建问题
 * @param data 创建问题请求数据
 * @returns 创建结果
 */
export const createIssue = async (data: CreateIssueRequest): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.post('/issues', data)
  return response.data
}

/**
 * 获取问题列表
 * @param params 查询参数
 * @returns 问题列表
 */
export const getIssues = async (params: IssueQueryParams = {}): Promise<IssueListResponse> => {
  const response: AxiosResponse<IssueListResponse> = await apiClient.get('/issues', { params })
  return response.data
}

/**
 * 获取问题详情
 * @param issueId 问题单号
 * @returns 问题详情
 */
export const getIssueById = async (issueId: string): Promise<Issue> => {
  const response: AxiosResponse<IssueDetailResponse> = await apiClient.get(`/issues/${issueId}`)
  return response.data.data
}

/**
 * 更新问题
 * @param issueId 问题单号
 * @param data 更新数据
 * @returns 更新结果
 */
export const updateIssue = async (issueId: string, data: UpdateIssueRequest): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.put(`/issues/${issueId}`, data)
  return response.data
}

/**
 * 删除问题
 * @param issueId 问题单号
 * @returns 删除结果
 */
export const deleteIssue = async (issueId: string): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.delete(`/issues/${issueId}`)
  return response.data
}

// ============================================================================
// 默认导出
// ============================================================================

export default {
  createIssue,
  getIssues,
  getIssueById,
  updateIssue,
  deleteIssue
}
