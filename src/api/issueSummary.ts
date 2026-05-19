/**
 * 问题总结 API 封装
 * 基于 Vue3 + TypeScript + Axios
 */
import axios, { type AxiosResponse, type AxiosError } from 'axios'
import type {
  IssueSummary,
  SubmitSummaryRequest,
  EditSummaryRequest,
  IssueSummaryResponse
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

// ============================================================================
// API 方法
// ============================================================================

/**
 * 提交问题总结
 * 首次提交问题解决方案总结
 * @param issueId 问题单号
 * @param data 问题总结数据
 * @returns 提交结果
 */
export const submitSummary = async (
  issueId: string,
  data: SubmitSummaryRequest
): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.post(
    `/issues/${issueId}/summary`,
    data
  )
  return response.data
}

/**
 * 编辑问题总结
 * 更新已提交的问题解决方案总结
 * @param issueId 问题单号
 * @param data 编辑数据
 * @returns 编辑结果
 */
export const editSummary = async (
  issueId: string,
  data: EditSummaryRequest
): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.put(
    `/issues/${issueId}/summary`,
    data
  )
  return response.data
}

/**
 * 获取问题总结
 * 获取问题的解决方案总结详细信息
 * @param issueId 问题单号
 * @returns 问题总结详情
 */
export const getSummary = async (issueId: string): Promise<IssueSummary> => {
  const response: AxiosResponse<IssueSummaryResponse> = await apiClient.get(
    `/issues/${issueId}/summary`
  )
  if (!response.data.data) {
    throw new Error('问题总结不存在')
  }
  return response.data.data
}

// ============================================================================
// 默认导出
// ============================================================================

export default {
  submitSummary,
  editSummary,
  getSummary
}
