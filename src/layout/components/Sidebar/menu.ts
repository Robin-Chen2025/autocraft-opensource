import type { RouteRecordRaw } from 'vue-router'

export interface MenuItem {
  path: string
  title: string
  icon: string
  children?: MenuItem[]
}

/**
 * 侧边栏菜单配置
 * 从路由配置中自动提取 menu: true 的路由
 */
export const menuConfig: MenuItem[] = [
  {
    path: '/issues',
    title: '问题管理',
    icon: 'Warning',
    children: [
      {
        path: '/issues',
        title: '问题列表',
        icon: 'List'
      }
    ]
  },
  {
    path: '/knowledge',
    title: '知识库',
    icon: 'Reading'
  }
]

/**
 * 从路由配置生成菜单
 * @param routes 路由配置数组
 * @returns 菜单配置数组
 */
export function generateMenuFromRoutes(routes: RouteRecordRaw[]): MenuItem[] {
  const menuItems: MenuItem[] = []
  
  routes.forEach(route => {
    if (route.meta?.menu && route.path && !route.path.includes(':')) {
      const menuItem: MenuItem = {
        path: route.path,
        title: String(route.meta?.title || ''),
        icon: String(route.meta?.icon || 'Document')
      }
      
      if (route.children && route.children.length > 0) {
        menuItem.children = route.children
          .filter(child => child.meta?.menu)
          .map(child => ({
            path: child.path || '',
            title: String(child.meta?.title || ''),
            icon: String(child.meta?.icon || 'Document')
          }))
      }
      
      menuItems.push(menuItem)
    }
  })
  
  return menuItems
}

export default menuConfig
