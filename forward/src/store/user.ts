import { defineStore } from 'pinia'

export interface UserState {
  token: string
  username: string
  isAdmin: boolean
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || '',
    isAdmin: localStorage.getItem('isAdmin') === 'true'
  }),
  
  actions: {
    login(token: string, username: string, isAdmin: boolean = false) {
      this.token = token
      this.username = username
      this.isAdmin = isAdmin
      
      localStorage.setItem('token', token)
      localStorage.setItem('username', username)
      localStorage.setItem('isAdmin', isAdmin.toString())
    },
    
    logout() {
      this.token = ''
      this.username = ''
      this.isAdmin = false
      
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('isAdmin')
    }
  }
}) 