import { defineStore } from 'pinia'
import axios from 'axios'

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
  state: (): UserState => ({
    token: localStorage.getItem('token') || '',
    userId: localStorage.getItem('userId') || '',
    username: localStorage.getItem('username') || '',
    email: localStorage.getItem('email') || '',
    avatar: localStorage.getItem('avatar') || '',
    location: localStorage.getItem('location') || '',
    isAdmin: localStorage.getItem('isAdmin') === 'true',
    favorites: JSON.parse(localStorage.getItem('favorites') || '[]')
  }),
  
  actions: {
    login(username: string, password: string) {
      return new Promise((resolve, reject) => {
        axios.post('/api/login/', { username, password })
          .then(response => {
            const { token, user_id, username: name, email, avatar, location, is_admin } = response.data
            
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
            reject(error)
          })
      })
    },
    
    register(username: string, email: string, password: string, code: string) {
      return new Promise((resolve, reject) => {
        axios.post('/api/register/', { username, email, password, code })
          .then(response => {
            resolve(response)
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    
    logout() {
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
    },
    
    updateProfile(profileData: Partial<UserState>) {
      return new Promise((resolve, reject) => {
        axios.put('/api/users/profile/', profileData, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
          .then(response => {
            this.setUserInfo({
              ...this.getUserInfo(),
              ...profileData
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
      
      if (index > -1) {
        // 移除收藏
        this.favorites.splice(index, 1)
      } else {
        // 添加收藏
        this.favorites.push(scenicId)
      }
      
      localStorage.setItem('favorites', JSON.stringify(this.favorites))
      
      return axios.post('/api/favorites/toggle/', { scenic_id: scenicId }, {
        headers: { Authorization: `Bearer ${this.token}` }
      })
    },
    
    setUserInfo(user: Partial<UserState>) {
      if (user.token) {
        this.token = user.token
        localStorage.setItem('token', user.token)
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