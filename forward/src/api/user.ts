import request from './request'

// 用户登录
export function login(account: string, password: string) {
  return request({
    url: '/user/login',
    method: 'post',
    data: { account, password }
  })
}

// 用户注册
export function register(username: string, password: string, email: string, verifyCode: string) {
  return request({
    url: '/user/register',
    method: 'post',
    data: { username, password, email, verifyCode }
  })
}

// 获取注册验证码
export function getVerifyCode(email: string) {
  return request({
    url: '/user/verify-code',
    method: 'get',
    params: { email }
  })
}

// 管理员登录
export function adminLogin(username: string, password: string) {
  return request({
    url: '/admin/login',
    method: 'post',
    data: { username, password }
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/user/info',
    method: 'get'
  })
}

// 获取用户收藏列表
export function getUserFavorites() {
  return request({
    url: '/user/favorites',
    method: 'get'
  })
}

// 获取用户搜索记录
export function getUserSearchHistory() {
  return request({
    url: '/user/search-history',
    method: 'get'
  })
}

// 管理员: 获取所有用户列表
export function getAllUsers() {
  return request({
    url: '/admin/users',
    method: 'get'
  })
}

// 管理员: 获取用户活动记录
export function getUserActivities(userId: string) {
  return request({
    url: '/admin/user-activities',
    method: 'get',
    params: { userId }
  })
}

// 发送重置密码验证码
export function getResetPasswordCode(email: string) {
  return request({
    url: '/user/reset-password-code',
    method: 'get',
    params: { email }
  })
}

// 重置密码
export function resetPassword(email: string, verifyCode: string, newPassword: string) {
  return request({
    url: '/user/reset-password',
    method: 'post',
    data: { email, verifyCode, newPassword }
  })
} 