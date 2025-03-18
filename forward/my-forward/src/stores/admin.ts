import { defineStore } from 'pinia'
import { getUsers, getUserRecords } from '../api'

interface AdminState {
  users: any[]
  userRecords: any[]
  loading: boolean
}

export const useAdminStore = defineStore('admin', {
  state: (): AdminState => ({
    users: [],
    userRecords: [],
    loading: false
  }),
  
  actions: {
    // 获取所有用户信息
    async getAllUsers() {
      this.loading = true
      try {
        const response = await getUsers()
        this.users = response.data
        this.loading = false
        return response.data
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.loading = false
        return []
      }
    },
    
    // 获取用户操作记录
    async getUserRecords() {
      this.loading = true
      try {
        const response = await getUserRecords()
        this.userRecords = response.data
        this.loading = false
        return response.data
      } catch (error) {
        console.error('获取用户操作记录失败:', error)
        this.loading = false
        return []
      }
    }
  }
}) 