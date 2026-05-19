/**
 * 项目档案 API 封装
 */
import axios, { type AxiosResponse } from 'axios'

const API_BASE_URL = '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000
})

// ==================== 类型定义 ====================

export interface Profile {
  profile_id: string
  profile_type: 'template' | 'instance'
  profile_name: string
  project_type?: string
  description?: string
  tech_stack?: string
  root_path?: string
  status: string
  created_at: string
  updated_at: string
}

export interface ProfileListResponse {
  total: number
  items: Profile[]
  page: number
  page_size: number
}

export interface ProfileQueryParams {
  page?: number
  page_size?: number
  profile_type?: string
  status?: string
  name?: string
  start_date?: string
  end_date?: string
}

// ==================== API 方法 ====================

export const getProfiles = async (params: ProfileQueryParams = {}): Promise<ProfileListResponse> => {
  const response = await apiClient.get<ProfileListResponse>('/profiles', { params })
  return response.data
}

export const getProfile = async (profileId: string): Promise<Profile> => {
  const response = await apiClient.get<Profile>(`/profiles/${profileId}`)
  return response.data
}

export const getProfilePhases = async (profileId: string): Promise<any[]> => {
  const response = await apiClient.get<any[]>(`/profiles/${profileId}/phases`)
  return response.data
}

// ==================== 工作计划 API ====================

export interface Plan {
  plan_id: string
  profile_id: string
  phase_record_id?: string
  plan_name: string
  description?: string
  status: string
  created_at: string
  updated_at: string
}

export interface PlanListResponse {
  total: number
  items: Plan[]
}

export const getPlans = async (profileId?: string): Promise<Plan[]> => {
  const params = profileId ? { profile_id: profileId } : {}
  const response = await apiClient.get<PlanListResponse>('/plans', { params })
  return response.data.items || []
}

export const getPlan = async (planId: string): Promise<{ plan: Plan; profile: Profile; phase: any }> => {
  const response = await apiClient.get<any>(`/plans/${planId}`)
  return {
    plan: response.data.data,
    profile: response.data.profile,
    phase: response.data.phase
  }
}

// ==================== 任务 API ====================

export interface Task {
  id: number
  task_no: string
  task_name: string
  plan_date?: string
  plan_complete_time?: string
  executor?: string
  status: string
  priority: string
  execution_steps?: string
  expected_result?: string
  execution_log?: string
  output_result?: string
  execution_date?: string
  verification_result: string
  verifier?: string
  verification_time?: string
  verification_log?: string
  exec_start_time?: string
  exec_estimated_complete?: string
  exec_complete_time?: string
  verify_start_time?: string
  verify_estimated_complete?: string
  verify_complete_time?: string
  created_at: string
  updated_at: string
  task_type?: string
  plan_id?: string
  phase_record_id?: string
  agent_id?: string
  locked_by?: string
  locked_at?: string
  input_data?: string
  extra_data?: string
}

export const getPlanTasks = async (planId: string): Promise<Task[]> => {
  const response = await apiClient.get<Task[]>(`/plans/${planId}/tasks`)
  return response.data
}

export const getTask = async (taskNo: string): Promise<Task> => {
  const response = await apiClient.get<any>(`/tasks/${taskNo}`)
  return response.data.data
}

export default {
  getProfiles,
  getProfile,
  getProfilePhases,
  getPlans,
  getPlan,
  getPlanTasks,
  getTask
}
