/**
 * 知识库 API 封装
 * 基于 Vue3 + TypeScript + Axios
 */
import axios, { type AxiosResponse, type AxiosError } from 'axios'
import type {
  Knowledge,
  CreateKnowledgeRequest,
  UpdateKnowledgeRequest,
  SearchKnowledgeRequest,
  KnowledgeListResponse,
  KnowledgeDetailResponse,
  MessageResponse,
  MarkAsFeaturedRequest,
  RecordReferenceRequest
} from '@/types/knowledge'

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
// API 方法
// ============================================================================

/**
 * 搜索知识库
 * @param params 查询参数
 * @returns 知识库列表
 */
export const searchKnowledge = async (params: SearchKnowledgeRequest = {}): Promise<KnowledgeListResponse> => {
  const response: AxiosResponse<KnowledgeListResponse> = await apiClient.get('/knowledge', { params })
  return response.data
}

/**
 * 获取知识库详情
 * @param knowledgeId 知识库 ID
 * @returns 知识库详情
 */
export const getKnowledgeDetail = async (knowledgeId: string): Promise<Knowledge> => {
  const response: AxiosResponse<KnowledgeDetailResponse> = await apiClient.get(`/knowledge/${knowledgeId}`)
  return response.data.data
}

/**
 * 创建知识库
 * @param data 创建知识库请求数据
 * @returns 创建结果
 */
export const createKnowledge = async (data: CreateKnowledgeRequest): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.post('/knowledge', data)
  return response.data
}

/**
 * 更新知识库
 * @param knowledgeId 知识库 ID
 * @param data 更新数据
 * @returns 更新结果
 */
export const updateKnowledge = async (knowledgeId: string, data: UpdateKnowledgeRequest): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.put(`/knowledge/${knowledgeId}`, data)
  return response.data
}

/**
 * 删除知识库
 * @param knowledgeId 知识库 ID
 * @returns 删除结果
 */
export const deleteKnowledge = async (knowledgeId: string): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.delete(`/knowledge/${knowledgeId}`)
  return response.data
}

/**
 * 标记优质内容
 * @param knowledgeId 知识库 ID
 * @param data 标记数据
 * @returns 标记结果
 */
export const markAsFeatured = async (knowledgeId: string, data: MarkAsFeaturedRequest): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.post(`/knowledge/${knowledgeId}/featured`, data)
  return response.data
}

/**
 * 记录引用
 * @param knowledgeId 知识库 ID
 * @param data 引用数据
 * @returns 记录结果
 */
export const recordReference = async (knowledgeId: string, data: RecordReferenceRequest): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await apiClient.post(`/knowledge/${knowledgeId}/reference`, data)
  return response.data
}

// ============================================================================
// 默认导出
// ============================================================================

export default {
  searchKnowledge,
  getKnowledgeDetail,
  createKnowledge,
  updateKnowledge,
  deleteKnowledge,
  markAsFeatured,
  recordReference
}
