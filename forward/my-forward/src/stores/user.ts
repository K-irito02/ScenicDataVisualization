import { defineStore } from 'pinia'
import { login as apiLogin, register as apiRegister, updateProfile as apiUpdateProfile, toggleFavorite as apiToggleFavorite, getFavorites as apiGetFavorites } from '../api'

interface UserState {
  token: string
  userId: string
  username: string
  email: string
  avatar: string
  location: string
  isAdmin: boolean
  favorites: string[]
}

export const useUserStore = defineStore('user', {
  state: (): UserState => {
    const token = localStorage.getItem('token') || ''
    console.log('初始化用户store状态，获取到token:', token ? `${token.substring(0, 10)}...` : 'null')
    
    return {
      token,
      userId: localStorage.getItem('userId') || '',
      username: localStorage.getItem('username') || '',
      email: localStorage.getItem('email') || '',
      avatar: localStorage.getItem('avatar') || '',
      location: localStorage.getItem('location') || '',
      isAdmin: localStorage.getItem('isAdmin') === 'true',
      favorites: JSON.parse(localStorage.getItem('favorites') || '[]')
    }
  },
  
  actions: {
    login(username: string, password: string) {
      console.log('用户store: 开始登录流程', { username })
      
      return new Promise((resolve, reject) => {
        apiLogin(username, password)
          .then(response => {
            console.log('用户store: 登录API返回成功', { status: response.status })
            
            const { token, user_id, username: name, email, avatar, location, is_admin } = response.data
            console.log('用户store: 解析用户数据', { 
              token: token ? `${token.substring(0, 10)}...` : 'null',
              user_id, 
              name
            })
            
            this.setUserInfo({
              token,
              userId: user_id,
              username: name,
              email,
              avatar,
              location,
              isAdmin: is_admin
            })
            
            resolve(response)
          })
          .catch(error => {
            console.error('用户store: 登录API返回错误', error)
            reject(error)
          })
      })
    },
    
    register(username: string, email: string, password: string, code: string) {
      return new Promise((resolve, reject) => {
        apiRegister(username, email, password, code)
          .then(response => {
            resolve(response)
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    
    logout() {
      console.log('用户store: 执行注销操作')
      
      this.token = ''
      this.userId = ''
      this.username = ''
      this.email = ''
      this.avatar = ''
      this.location = ''
      this.isAdmin = false
      this.favorites = []
      
      localStorage.removeItem('token')
      localStorage.removeItem('userId')
      localStorage.removeItem('username')
      localStorage.removeItem('email')
      localStorage.removeItem('avatar')
      localStorage.removeItem('location')
      localStorage.removeItem('isAdmin')
      localStorage.removeItem('favorites')
      
      console.log('用户store: 注销完成，清除了所有用户数据')
    },
    
    updateProfile(profileData: Partial<UserState>) {
      return new Promise((resolve, reject) => {
        apiUpdateProfile(profileData)
          .then(response => {
            const userData = response.data.user
            this.setUserInfo({
              userId: userData.id,
              username: userData.username,
              email: userData.email,
              avatar: userData.avatar,
              location: userData.location,
              isAdmin: userData.isAdmin
            })
            resolve(response)
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    
    toggleFavorite(scenicId: string) {
      const index = this.favorites.indexOf(scenicId)
      
      return new Promise((resolve, reject) => {
        apiToggleFavorite(scenicId)
          .then(response => {
            if (response.data.is_favorite) {
              // 添加收藏
              if (index === -1) {
                this.favorites.push(scenicId)
              }
            } else {
              // 取消收藏
              if (index > -1) {
                this.favorites.splice(index, 1)
              }
            }
            
            localStorage.setItem('favorites', JSON.stringify(this.favorites))
            resolve(response)
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    
    fetchFavorites() {
      return new Promise((resolve, reject) => {
        apiGetFavorites()
          .then(response => {
            const favoriteIds = response.data.map((item: any) => item.scenic_id)
            this.favorites = favoriteIds
            localStorage.setItem('favorites', JSON.stringify(favoriteIds))
            resolve(response)
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    
    setUserInfo(user: Partial<UserState>) {
      console.log('用户store: 设置用户信息', {
        hasToken: !!user.token,
        userId: user.userId,
        username: user.username
      })
      
      if (user.token) {
        this.token = user.token
        localStorage.setItem('token', user.token)
        console.log('用户store: 已保存token到localStorage')
      }
      
      if (user.userId) {
        this.userId = user.userId
        localStorage.setItem('userId', user.userId)
      }
      
      if (user.username) {
        this.username = user.username
        localStorage.setItem('username', user.username)
      }
      
      if (user.email) {
        this.email = user.email
        localStorage.setItem('email', user.email)
      }
      
      if (user.avatar) {
        this.avatar = user.avatar
        localStorage.setItem('avatar', user.avatar)
      }
      
      if (user.location) {
        this.location = user.location
        localStorage.setItem('location', user.location)
      }
      
      if (user.isAdmin !== undefined) {
        this.isAdmin = user.isAdmin
        localStorage.setItem('isAdmin', user.isAdmin.toString())
      }
      
      if (user.favorites) {
        this.favorites = user.favorites
        localStorage.setItem('favorites', JSON.stringify(user.favorites))
      }
    },
    
    getUserInfo(): UserState {
      return {
        token: this.token,
        userId: this.userId,
        username: this.username,
        email: this.email,
        avatar: this.avatar,
        location: this.location,
        isAdmin: this.isAdmin,
        favorites: this.favorites
      }
    }
  }
}) 