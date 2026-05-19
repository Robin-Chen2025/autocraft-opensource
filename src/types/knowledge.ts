/**
 * 知识库类型定义
 * 用于知识库管理和引用功能
 */

// ============================================================================
// 基础类型定义
// ============================================================================

/**
 * 知识库分类枚举值
 */
export type KnowledgeCategory = '技术文档' | '最佳实践' | '问题解决方案' | '培训资料' | '其他';

/**
 * 知识库状态枚举值
 */
export type KnowledgeStatus = '草稿' | '已发布' | '已归档';

// ============================================================================
// Element Plus Tag 类型映射
// ============================================================================

/**
 * Element Plus Tag 组件的类型
 * 用于不同状态/分类的视觉区分
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
 * 知识库条目完整接口
 * 包含知识库的所有字段
 */
export interface Knowledge {
  /** 知识库 ID */
  id: string;
  
  /** 标题 */
  title: string;
  
  /** 内容摘要 */
  summary: string;
  
  /** 详细内容 */
  content: string;
  
  /** 分类 */
  category: KnowledgeCategory;
  
  /** 状态 */
  status: KnowledgeStatus;
  
  /** 作者 */
  author: string;
  
  /** 创建时间，ISO 8601 格式 */
  created_at: string;
  
  /** 最后更新时间，ISO 8601 格式 */
  updated_at: string;
  
  /** 发布时间，ISO 8601 格式 */
  published_at?: string;
  
  /** 标签列表 */
  tags: string[];
  
  /** 是否优质内容 */
  is_featured: boolean;
  
  /** 浏览次数 */
  view_count: number;
  
  /** 引用次数 */
  reference_count: number;
  
  /** 关联问题单号（可选） */
  related_issue_id?: string;
  
  /** 关联任务单号（可选） */
  related_task_id?: string;
}

// ============================================================================
// 请求接口定义
// ============================================================================

/**
 * 搜索知识库请求接口
 */
export interface SearchKnowledgeRequest {
  /** 页码，从 1 开始 */
  page?: number;
  
  /** 每页数量 */
  page_size?: number;
  
  /** 关键字搜索（标题/内容/标签） */
  keyword?: string;
  
  /** 分类筛选 */
  category?: KnowledgeCategory;
  
  /** 状态筛选 */
  status?: KnowledgeStatus;
  
  /** 作者筛选 */
  author?: string;
  
  /** 标签筛选 */
  tag?: string;
  
  /** 仅查询优质内容 */
  is_featured?: boolean;
}

/**
 * 知识库查询参数接口
 * 用于列表分页和筛选
 */
export interface KnowledgeQueryParams {
  /** 页码，从 1 开始 */
  page?: number;
  
  /** 每页数量 */
  page_size?: number;
  
  /** 关键字搜索（标题/内容/标签） */
  keyword?: string;
  
  /** 分类筛选 */
  category?: KnowledgeCategory;
  
  /** 状态筛选 */
  status?: KnowledgeStatus;
  
  /** 作者筛选 */
  author?: string;
  
  /** 标签筛选 */
  tag?: string;
  
  /** 仅查询优质内容 */
  is_featured?: boolean;
  
  /** 创建时间起始 */
  created_at_from?: string;
  
  /** 创建时间结束 */
  created_at_to?: string;
}

/**
 * 创建知识库请求接口
 */
export interface CreateKnowledgeRequest {
  /** 标题 */
  title: string;
  
  /** 内容摘要 */
  summary: string;
  
  /** 详细内容 */
  content: string;
  
  /** 分类 */
  category: KnowledgeCategory;
  
  /** 标签列表 */
  tags?: string[];
  
  /** 关联问题单号（可选） */
  related_issue_id?: string;
  
  /** 关联任务单号（可选） */
  related_task_id?: string;
}

/**
 * 更新知识库请求接口
 * 所有字段可选，支持部分更新
 */
export interface UpdateKnowledgeRequest {
  /** 标题 */
  title?: string;
  
  /** 内容摘要 */
  summary?: string;
  
  /** 详细内容 */
  content?: string;
  
  /** 分类 */
  category?: KnowledgeCategory;
  
  /** 标签列表 */
  tags?: string[];
  
  /** 关联问题单号 */
  related_issue_id?: string;
  
  /** 关联任务单号 */
  related_task_id?: string;
}

/**
 * 标记优质内容请求接口
 */
export interface MarkAsFeaturedRequest {
  /** 是否优质 */
  is_featured: boolean;
  
  /** 标记说明（可选） */
  note?: string;
}

/**
 * 记录引用请求接口
 */
export interface RecordReferenceRequest {
  /** 引用来源描述 */
  source?: string;
  
  /** 引用说明 */
  note?: string;
}

// ============================================================================
// 响应接口定义
// ============================================================================

/**
 * 知识库列表响应接口
 */
export interface KnowledgeListResponse {
  /** 知识库列表 */
  items: Knowledge[];
  
  /** 总数量 */
  total: number;
  
  /** 当前页码 */
  page: number;
  
  /** 每页数量 */
  page_size: number;
  
  /** 总页数 */
  total_pages: number;
}

/**
 * 知识库详情响应接口
 */
export interface KnowledgeDetailResponse {
  /** 知识库数据 */
  data: Knowledge;
}

/**
 * 通用消息响应接口
 */
export interface MessageResponse {
  /** 消息内容 */
  message: string;
  
  /** 相关 ID（可选） */
  id?: string;
}

// ============================================================================
// 选项常量数组
// ============================================================================

/**
 * 分类选项常量数组
 */
export const categoryOptions: OptionItem[] = [
  { label: '技术文档', value: '技术文档', type: 'primary' },
  { label: '最佳实践', value: '最佳实践', type: 'success' },
  { label: '问题解决方案', value: '问题解决方案', type: 'warning' },
  { label: '培训资料', value: '培训资料', type: 'info' },
  { label: '其他', value: '其他', type: '' },
];

/**
 * 状态选项常量数组
 */
export const statusOptions: OptionItem[] = [
  { label: '草稿', value: '草稿', type: 'info' },
  { label: '已发布', value: '已发布', type: 'success' },
  { label: '已归档', value: '已归档', type: '' },
];

// ============================================================================
// 工具函数
// ============================================================================

/**
 * 获取分类标签类型
 * @param category 知识库分类
 * @returns Element Plus Tag 类型
 */
export function getCategoryTagType(category: KnowledgeCategory): TagType {
  const option = categoryOptions.find(opt => opt.value === category);
  return option?.type || '';
}

/**
 * 获取状态标签类型
 * @param status 知识库状态
 * @returns Element Plus Tag 类型
 */
export function getStatusTagType(status: KnowledgeStatus): TagType {
  const option = statusOptions.find(opt => opt.value === status);
  return option?.type || '';
}
