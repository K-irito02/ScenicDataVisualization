import { createPinia } from 'pinia'

// 导出所有store
export { useUserStore } from './user'
export { useScenicStore } from './scenic'
export { useAdminStore } from './admin'

const pinia = createPinia()

export default pinia 