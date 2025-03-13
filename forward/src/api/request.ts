import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service = axios.create({
  baseURL: '/api',  // 后端API的基础路径
  timeout: 15000    // 请求超时时间（15秒）
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 从localStorage获取token，并添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果返回的状态码不是200，则判断为错误
    if (response.status !== 200) {
      ElMessage.error(res.message || '服务器错误')
      return Promise.reject(new Error(res.message || '服务器错误'))
    } else {
      return res
    }
  },
  error => {
    console.error('响应错误:', error)
    // 处理HTTP错误状态码
    if (error.response) {
      const status = error.response.status
      if (status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        // 可以在这里加入清除本地存储并跳转到登录页的逻辑
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        localStorage.removeItem('isAdmin')
        window.location.href = '/login'
      } else if (status === 403) {
        ElMessage.error('无权限访问')
      } else if (status === 404) {
        ElMessage.error('请求的资源不存在')
      } else if (status >= 500) {
        ElMessage.error('服务器内部错误')
      } else {
        ElMessage.error(error.response.data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败，请检查网络')
    }
    return Promise.reject(error)
  }
)

export default service 