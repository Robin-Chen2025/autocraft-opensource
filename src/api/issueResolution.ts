/**
 * 问题解决 API 封装
 * 基于 Vue3 + TypeScript + Axios
 */
import axios, { type AxiosResponse, type AxiosError } from 'axios'
import type { Issue, ResolveIssueRequest } from '@/types/issue'

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

/**
 * 提交解决方案请求接口
 * 用于首次提交问题解决信息
 */
export interface SubmitSolutionRequest {
  /** 解决人 */
  resolver: string
  
  /** 解决方案总结 */
  resolution_summary: string
  
  /** 根因分析 */
  root_cause: string
  
  /** 解决过程 */
  solution_process: string
  
  /** 经验教训 */
  lesson_learned: string
}

/**
 * 编辑解决方案请求接口
 * 用于更新已提交的解决方案
 */
export interface EditSolutionRequest {
  /** 解决方案总结 */
  resolution_summary?: string
  
  /** 根因分析 */
  root_cause?: string
  
  /** 解决过程 */
  solution_process?: string
  
  /** 经验教训 */
  lesson_learned?: string
}

/** 解决方案详情响应 */
export interface SolutionDetailResponse {
  data: Issue
}

// ============================================================================
// API 方法
// ============================================================================

/**
 * 提交解决方案
 * 将问题状态从"处理中"更新为"已解决"
 * @param issueId 问题单号
 * @param data 解决方案数据
 * @returns 提交结果
 */
export const submitSolution = async (
  issueId: string,
  data: SubmitSolutionRequest
): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.post(
    `/issues/${issueId}/resolve`,
    data
  )
  return response.data
}

/**
 * 编辑解决方案
 * 更新已提交的问题解决方案
 * @param issueId 问题单号
 * @param data 编辑数据
 * @returns 编辑结果
 */
export const editSolution = async (
  issueId: string,
  data: EditSolutionRequest
): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.put(
    `/issues/${issueId}/resolve`,
    data
  )
  return response.data
}

/**
 * 获取解决方案详情
 * 获取问题的解决方案详细信息
 * @param issueId 问题单号
 * @returns 解决方案详情
 */
export const getSolutionDetail = async (issueId: string): Promise<Issue> => {
  const response: AxiosResponse<SolutionDetailResponse> = await apiClient.get(
    `/issues/${issueId}/resolve`
  )
  return response.data.data
}

// ============================================================================
// 默认导出
// ============================================================================

export default {
  submitSolution,
  editSolution,
  getSolutionDetail
}
