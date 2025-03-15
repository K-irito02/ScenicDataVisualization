declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module '*.json' {
  const value: any
  export default value
}

// 声明Element Plus全局组件
declare module 'element-plus' {
  import { ElMessage } from 'element-plus'
  export { ElMessage }
  
  export interface FormInstance {
    validate: (callback?: (valid: boolean) => void) => Promise<boolean>
    validateField: (field: string) => Promise<void>
    resetFields: () => void
    scrollToField: (field: string) => void
    clearValidate: (fields?: string | string[]) => void
  }
  
  export interface FormRules {
    [key: string]: Array<{
      required?: boolean
      message?: string
      trigger?: string
      min?: number
      max?: number
      type?: string
      validator?: (rule: any, value: any, callback: any) => void
      len?: number
    }>
  }
} 