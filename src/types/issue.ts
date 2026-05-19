/**
 * 问题记录单类型定义
 * 用于问题跟踪和管理功能
 */

// ============================================================================
// 基础类型定义
// ============================================================================

/**
 * 问题状态枚举值
 */
export type IssueStatus = '新建' | '处理中' | '已解决' | '已关闭' | 'open' | 'resolved' | 'closed';

/**
 * 优先级枚举值
 */
export type IssuePriority = '高' | '中' | '低';

/**
 * 问题分类枚举值
 */
export type IssueCategory = 'Bug' | '优化' | '需求' | '其他';

// ============================================================================
// Element Plus Tag 类型映射
// ============================================================================

/**
 * Element Plus Tag 组件的类型
 * 用于不同状态/优先级的视觉区分
 */
export type TagType = 'success' | 'warning' | 'danger' | 'info' | 'primary' | '';

// ============================================================================
// 选项常量接口
// ============================================================================

/**
 * 下拉选项接口定义
 * 用于表单中的选择器组件
 */
export interface OptionItem {
  /** 显示标签 */
  label: string;
  /** 实际值 */
  value: string;
  /** Element Plus Tag 类型 */
  type: TagType;
}

// ============================================================================
// 核心数据模型
// ============================================================================

/**
 * 问题记录单完整接口
 * 包含 16 个字段，覆盖问题全生命周期
 */
export interface Issue {
  /** 问题单号，格式：ISSUE-YYYYMMDD-NNNN */
  id: string;
  
  /** 问题标题 */
  title: string;
  
  /** 问题描述 */
  description: string;
  
  /** 状态：新建 | 处理中 | 已解决 | 已关闭 */
  status: IssueStatus;
  
  /** 优先级：高 | 中 | 低 */
  priority: IssuePriority;
  
  /** 问题分类 */
  category: IssueCategory | '';
  
  /** 创建人 */
  creator: string;
  
  /** 创建时间，ISO 8601 格式 */
  created_at: string;
  
  /** 解决时间，ISO 8601 格式 */
  resolved_at: string;
  
  /** 解决人 */
  resolved_by: string;
  
  /** 解决方案总结 */
  solution: string;
  
  /** 根因分析 */
  root_cause: string;
  
  /** 解决过程 */
  solution_process: string;
  
  /** 经验教训 */
  lesson_learned: string;
  
  /** 关闭原因 */
  closed_reason: string;
  
  /** 关联任务单号 */
  related_task_id: string;
  
  // ========== 关联信息 ==========
  
  /** 关联项目名称 */
  project_name?: string;
  
  /** 关联阶段名称 */
  stage_name?: string;
  
  /** 关联工作流名称 */
  workflow_name?: string;
  
  // ========== 处理信息 ==========
  
  /** 处理人 */
  assignee?: string;
  
  /** 分配时间 */
  assigned_at?: string;
  
  /** 预期完成时间 */
  due_date?: string;
  
  /** 分配说明 */
  assign_note?: string;
  
  // ========== 解决信息（兼容字段） ==========
  
  /** 解决人（兼容字段） */
  resolver?: string;
  
  /** 解决方案总结（兼容字段） */
  resolution_summary?: string;
}

// ============================================================================
// 请求接口定义
// ============================================================================

/**
 * 创建问题请求接口
 * 创建时不需要填写解决相关字段
 */
export interface CreateIssueRequest {
  /** 问题标题 */
  title: string;
  
  /** 问题描述 */
  description: string;
  
  /** 优先级 */
  priority: IssuePriority;
  
  /** 问题分类 */
  category: IssueCategory | '';
  
  /** 关联任务单号（可选） */
  related_task_id?: string;
}

/**
 * 更新问题请求接口
 * 所有字段可选，支持部分更新
 */
export interface UpdateIssueRequest {
  /** 问题标题 */
  title?: string;
  
  /** 问题描述 */
  description?: string;
  
  /** 优先级 */
  priority?: IssuePriority;
  
  /** 问题分类 */
  category?: IssueCategory | '';
  
  /** 关联任务单号 */
  related_task_id?: string;
}

/**
 * 解决问题请求接口
 * 用于将问题状态从 open 更新为 resolved
 */
export interface ResolveIssueRequest {
  /** 解决人 */
  resolved_by: string;
  
  /** 解决方案总结 */
  solution: string;
  
  /** 根因分析 */
  root_cause: string;
  
  /** 解决过程 */
  solution_process: string;
  
  /** 经验教训 */
  lesson_learned: string;
  
  // ========== 兼容字段 ==========
  
  /** 解决人（兼容字段） */
  resolver?: string;
  
  /** 解决方案总结（兼容字段） */
  resolution_summary?: string;
}

/**
 * 关闭问题请求接口
 * 用于将问题状态从 resolved 更新为 closed
 */
export interface CloseIssueRequest {
  /** 关闭原因 */
  closed_reason: string;
}

// ============================================================================
// 查询与响应接口
// ============================================================================

/**
 * 问题查询参数接口
 * 用于列表分页和筛选
 */
export interface IssueQueryParams {
  /** 页码，从 1 开始 */
  page?: number;
  
  /** 每页数量 */
  page_size?: number;
  
  /** 状态筛选 */
  status?: IssueStatus;
  
  /** 优先级筛选 */
  priority?: IssuePriority;
  
  /** 分类筛选 */
  category?: IssueCategory;
  
  /** 创建人筛选 */
  creator?: string;
  
  /** 关键字搜索（标题/描述） */
  keyword?: string;
  
  /** 关联任务单号筛选 */
  related_task_id?: string;
  
  /** 创建时间起始 */
  created_at_from?: string;
  
  /** 创建时间结束 */
  created_at_to?: string;
}

/**
 * 问题列表响应接口
 */
export interface IssueListResponse {
  /** 问题列表 */
  items: Issue[];
  
  /** 总数量 */
  total: number;
  
  /** 当前页码 */
  page: number;
  
  /** 每页数量 */
  page_size: number;
  
  /** 总页数 */
  total_pages: number;
}

// ============================================================================
// 问题总结相关接口
// ============================================================================

/**
 * 问题总结接口
 */
export interface IssueSummary {
  /** 问题单号 */
  issue_no: string;
  
  /** 根因分析 */
  root_cause: string;
  
  /** 解决方案 */
  solution_approach: string;
  
  /** 经验教训 */
  lessons_learned: string;
  
  /** 预防措施 */
  prevention_measures: string;
  
  /** 创建时间 */
  created_at: string;
  
  /** 更新时间 */
  updated_at: string;
}

/**
 * 提交总结请求接口
 */
export interface SubmitSummaryRequest {
  /** 根因分析 */
  root_cause: string;
  
  /** 解决方案 */
  solution_approach: string;
  
  /** 经验教训 */
  lessons_learned: string;
  
  /** 预防措施 */
  prevention_measures?: string;
}

/**
 * 编辑总结请求接口
 */
export interface EditSummaryRequest {
  /** 根因分析 */
  root_cause?: string;
  
  /** 解决方案 */
  solution_approach?: string;
  
  /** 经验教训 */
  lessons_learned?: string;
  
  /** 预防措施 */
  prevention_measures?: string;
}

/**
 * 问题总结响应接口
 */
export interface IssueSummaryResponse {
  /** 是否成功 */
  success: boolean;
  
  /** 消息 */
  message: string;
  
  /** 总结数据 */
  data?: IssueSummary;
}

// ============================================================================
// 选项常量数组
// ============================================================================

/**
 * 状态选项常量数组
 * 用于下拉选择器和状态标签显示
 */
export const statusOptions: OptionItem[] = [
  { label: '新建', value: '新建', type: 'info' },
  { label: '处理中', value: '处理中', type: 'primary' },
  { label: '已解决', value: '已解决', type: 'success' },
  { label: '已关闭', value: '已关闭', type: '' },
];

/**
 * 优先级选项常量数组
 * 用于下拉选择器和优先级标签显示
 */
export const priorityOptions: OptionItem[] = [
  { label: '高', value: '高', type: 'danger' },
  { label: '中', value: '中', type: 'warning' },
  { label: '低', value: '低', type: 'success' },
];

/**
 * 分类选项常量数组
 * 可根据实际业务需求扩展
 */
export const categoryOptions: OptionItem[] = [
  { label: 'Bug', value: 'Bug', type: 'danger' },
  { label: '优化', value: '优化', type: 'primary' },
  { label: '需求', value: '需求', type: 'success' },
  { label: '其他', value: '其他', type: 'info' },
];

// ============================================================================
// 工具函数类型（可选）
// ============================================================================

/**
 * 获取状态标签类型
 * @param status 问题状态
 * @returns Element Plus Tag 类型
 */
export function getStatusTagType(status?: IssueStatus): TagType {
  if (!status) return '';
  const option = statusOptions.find(opt => opt.value === status);
  return option?.type || '';
}

/**
 * 获取优先级标签类型
 * @param priority 优先级
 * @returns Element Plus Tag 类型
 */
export function getPriorityTagType(priority?: IssuePriority): TagType {
  if (!priority) return '';
  const option = priorityOptions.find(opt => opt.value === priority);
  return option?.type || '';
}
