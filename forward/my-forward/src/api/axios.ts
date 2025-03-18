import axios from 'axios';
import { useUserStore } from '../stores/user';

// 创建axios实例
const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
instance.interceptors.request.use(
  config => {
    const userStore = useUserStore();
    const token = userStore.token;
    
    // 如果有token，在请求头中添加token
    if (token) {
      config.headers.Authorization = `Token ${token}`;
      console.log(`发送请求到: ${config.url}，已添加Token认证`, token.substring(0, 10) + '...');
    } else {
      console.log(`发送请求到: ${config.url}，未添加Token认证`);
    }
    
    return config;
  },
  error => {
    console.error('请求拦截器错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  response => {
    console.log(`请求 ${response.config.url} 成功:`, response.status);
    return response;
  },
  error => {
    console.error('API请求错误:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data
    });
    
    // 处理401未授权错误
    if (error.response && error.response.status === 401) {
      console.warn('收到401未授权响应，即将注销用户并重定向');
      const userStore = useUserStore();
      userStore.logout(); // 登出用户
      window.location.href = '/login'; // 重定向到登录页
    }
    
    return Promise.reject(error);
  }
);

export default instance; 