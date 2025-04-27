import request from './axios';

/**
 * 用户登录
 * @param username_or_email 用户名或邮箱
 * @param password 密码
 */
export function login(username_or_email: string, password: string) {
  return request({
    url: '/api/login/',
    method: 'post',
    data: { username_or_email, password },
    withCredentials: true, // 允许跨域请求携带身份凭证
    headers: {
      'Content-Type': 'application/json',
    }
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
    url: '/api/register/',
    method: 'post',
    data: {
      username,
      email,
      password,
      code
    },
    withCredentials: true, // 允许跨域请求携带身份凭证
    headers: {
      'Content-Type': 'application/json',
    }
  });
}

/**
 * 发送忘记密码验证码
 * @param email 邮箱
 */
export function forgotPassword(email: string) {
  return request({
    url: '/api/forgot-password/',
    method: 'post',
    data: { email }
  });
}

/**
 * 重置密码
 * @param email 邮箱
 * @param code 验证码
 * @param password 新密码
 */
export function resetPassword(email: string, code: string, password: string) {
  return request({
    url: '/api/reset-password/',
    method: 'post',
    data: {
      email,
      code,
      password
    }
  });
}

/**
 * 更新用户资料
 * @param profileData 用户资料数据
 */
export function updateProfile(profileData: any) {
  console.log('准备更新个人资料:', profileData);
  
  // 添加调试日志显示传入的头像URL
  if (profileData.avatar) {
    console.log('更新资料时的头像URL:', profileData.avatar);
  }
  
  // 检查 avatar 是否是完整 URL
  let avatar = profileData.avatar || '';
  
  // 分析头像URL的路径组成
  console.log('头像URL分析:');
  if (avatar.includes('?')) {
    console.log('- 包含查询参数:', avatar.split('?')[0], '参数:', avatar.split('?')[1]);
    // 移除时间戳查询参数，只保留基础URL
    avatar = avatar.split('?')[0];
    console.log('- 移除查询参数后:', avatar);
  }
  
  // 如果是完整 URL，尝试提取路径部分
  if (avatar && avatar.startsWith('http')) {
    try {
      const url = new URL(avatar);
      // 只发送路径部分，不包括域名
      avatar = url.pathname;
      console.log('提取的头像路径:', avatar);
    } catch (e) {
      console.error('无法解析头像 URL:', e);
      // 错误时保留原始值
      avatar = profileData.avatar;
    }
  } else if (avatar && !avatar.startsWith('/')) {
    // 确保以斜杠开头的相对路径
    avatar = '/' + avatar;
    console.log('调整后的头像路径:', avatar);
  }
  
  // 创建一个格式化的请求对象，方便调试
  const requestData = {
    username: profileData.username,
    email: profileData.email,
    location: profileData.location || '',
    avatar: avatar
  };
  
  console.log('发送到服务器的更新资料数据:', requestData);
  
  return request({
    url: '/api/users/profile/',
    method: 'put',
    data: requestData
  }).catch(error => {
    console.error('更新个人资料失败:', error);
    
    // 详细记录错误信息
    if (error.response) {
      console.error('服务器响应错误状态码:', error.response.status);
      console.error('服务器响应错误数据:', error.response.data);
      
      // 针对具体字段错误提供更多信息
      if (error.response.data && error.response.data.errors) {
        const errors = error.response.data.errors;
        for (const field in errors) {
          console.error(`字段 ${field} 错误:`, errors[field]);
        }
      }
    } else if (error.request) {
      console.error('请求已发送但没有收到响应:', error.request);
    } else {
      console.error('请求配置错误:', error.message);
    }
    
    throw error; // 继续抛出错误，让上层组件处理
  });
}

/**
 * 添加或移除收藏
 * @param scenicId 景区ID
 */
export function toggleFavorite(scenicId: string) {
  return request({
    url: '/api/favorites/toggle/',
    method: 'post',
    data: { scenic_id: scenicId }
  });
}

/**
 * 获取用户收藏列表
 */
export function getFavorites() {
  return request({
    url: '/api/favorites/',
    method: 'get'
  });
}

/**
 * 删除用户账户
 * @param password 用户密码，用于确认操作
 */
export function deleteAccount(password: string) {
  return request({
    url: '/api/users/delete-account/',
    method: 'post',
    data: { password }
  });
}

/**
 * 发送邮箱验证码
 * @param email 邮箱
 * @param isProfileUpdate 是否为个人资料更新场景
 */
export function sendEmailCode(email: string, isProfileUpdate: boolean = false) {
  return request({
    url: '/api/email/send-code/',
    method: 'post',
    data: { 
      email,
      is_profile_update: isProfileUpdate
    }
  });
} 