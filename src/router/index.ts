import { createRouter, createWebHistory } from 'vue-router'
import TaskListView from '../views/TaskListView.vue'

const routes = [
  {
    path: '/',
    redirect: '/projects'
  },
  {
    path: '/tasks',
    name: 'TaskListView',
    component: TaskListView,
    meta: {
      title: '任务列表',
      icon: 'List'
    }
  },
  {
    path: '/issues',
    name: 'IssueList',
    component: () => import('../views/issues/IssueList.vue'),
    meta: {
      title: '问题记录单',
      icon: 'Warning'
    }
  },
  {
    path: '/issues/create',
    name: 'IssueCreate',
    component: () => import('../views/issues/IssueDetail.vue'),
    meta: {
      title: '新建问题单',
      icon: 'Warning'
    }
  },
  {
    path: '/issues/:id',
    name: 'IssueDetail',
    component: () => import('../views/issues/IssueDetail.vue'),
    meta: {
      title: '问题单详情',
      icon: 'Warning'
    }
  },
  {
    path: '/knowledge',
    name: 'KnowledgeSearch',
    component: () => import('../views/knowledge/KnowledgeSearch.vue'),
    meta: {
      title: '知识库',
      icon: 'Collection'
    }
  },
  {
    path: '/projects',
    name: 'ProjectList',
    component: () => import('../views/ProjectList.vue'),
    meta: {
      title: '项目列表',
      icon: 'Folder'
    }
  },
  {
    path: '/projects/:profile_id',
    name: 'ProjectDetail',
    component: () => import('../views/ProjectDetail.vue'),
    meta: {
      title: '项目详情',
      icon: 'Folder'
    }
  },
  {
    path: '/plans/:plan_id',
    name: 'PlanDetail',
    component: () => import('../views/PlanDetail.vue'),
    meta: {
      title: '计划详情',
      icon: 'Document'
    }
  },
  {
    path: '/tasks/:task_no',
    name: 'TaskDetail',
    component: () => import('../views/TaskDetail.vue'),
    meta: {
      title: '任务详情',
      icon: 'Document'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router