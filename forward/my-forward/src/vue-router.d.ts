declare module 'vue-router' {
  import type { DefineComponent } from 'vue'
  
  export interface RouteLocationNormalized {
    path: string
    name?: string | null
    params: Record<string, string>
    query: Record<string, string>
    hash: string
    fullPath: string
    matched: any[]
    meta: Record<string, any>
    [key: string]: any
  }
  
  export type NavigationGuardNext = (to?: any) => void

  export interface RouteRecordRaw {
    path: string
    name?: string
    component: any
    components?: Record<string, any>
    redirect?: string | { name?: string }
    children?: RouteRecordRaw[]
    meta?: Record<string, any>
    [key: string]: any
  }

  export function createRouter(options: any): any
  export function createWebHistory(base?: string): any
  export function useRouter(): any
  export function useRoute(): any
} 
/** 
 * 
 * 如果这些方法都不能解决问题，可以尝试：
 * 1. 清除node_modules并重新安装：
 *    npm cache clean --force
 *    rm -rf node_modules
 *    npm install
 * 2. 检查package.json中的vue和vue-router版本是否一致
 * 3. 确保在Vue项目中使用的是Vue Router 4.x版本
 * 4. 检查是否存在其他依赖冲突
 * 5. 如果问题依然存在，可以考虑使用Vue Router 3.x版本
 * 
 * 
 * 
 */