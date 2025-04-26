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