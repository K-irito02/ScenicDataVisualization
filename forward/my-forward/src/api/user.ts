import request from './axios';

/**
 * 用户登录
 * @param username 用户名
 * @param password 密码
 */
export function login(username: string, password: string) {
  return request({
    url: '/login/',
    method: 'post',
    data: { username, password }
  });
}

/**
 * 用户注册
 * @param username 用户名
 * @param email 邮箱
 * @param password 密码
 * @param code 邮箱验证码
 */
export function register(username: string, email: string, password: string, code: string) {
  return request({
    url: '/register/',
    method: 'post',
    data: {
      username,
      email,
      password,
      code
    }
  });
}

/**
 * 更新用户资料
 * @param profileData 用户资料数据
 */
export function updateProfile(profileData: any) {
  return request({
    url: '/users/profile/',
    method: 'put',
    data: profileData
  });
}

/**
 * 添加或移除收藏
 * @param scenicId 景区ID
 */
export function toggleFavorite(scenicId: string) {
  return request({
    url: '/favorites/toggle/',
    method: 'post',
    data: { scenic_id: scenicId }
  });
}

/**
 * 获取用户收藏列表
 */
export function getFavorites() {
  return request({
    url: '/favorites/',
    method: 'get'
  });
} 