import axios from 'axios';
import { useUserStore } from '../stores/user';
import { ElMessage } from 'element-plus';

// 创建axios实例
const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
instance.interceptors.request.use(
  config => {
    const userStore = useUserStore();
    
    // 对于登录、注册等公开API，不需要检查token
    const publicAPIs = ['/api/login/', '/api/register/', '/api/email/send-code/'];
    const isPublicAPI = publicAPIs.some(api => config.url?.includes(api));
    
    if (isPublicAPI) {
      console.log(`请求公开API: ${config.url}，跳过token验证`);
      return config;
    }
    
    // 检查token是否有效
    if (!userStore.isAuthenticated()) {
      console.warn('Token已过期或无效，跳转到登录页面');
      
      // 避免在拦截器中直接重定向，而是抛出错误，让业务代码处理
      // 这样可以避免某些场景下的循环重定向
      if (window.location.pathname.startsWith('/login')) {
        // 如果已经在登录页，不再触发重定向和登出操作
        console.log('已在登录页，不再重复重定向');
        return Promise.reject(new Error('需要登录'));
      }
      
      userStore.logout();
      setTimeout(() => {
        // 使用setTimeout确保当前请求完全结束后再重定向
        window.location.href = '/login';
      }, 100);
      
      return Promise.reject(new Error('身份验证已过期，请重新登录'));
    }
    
    const token = userStore.token;
    
    // 如果有token，在请求头中添加token
    if (token) {
      config.headers.Authorization = `Token ${token}`;
      console.log(`发送请求到: ${config.url}，已添加Token认证`, token.substring(0, 10) + '...');
    } else {
      console.log(`发送请求到: ${config.url}，未添加Token认证`);
    }
    
    // 不要覆盖已设置的Content-Type
    if (!config.headers['Content-Type'] && config.data && !(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json';
    }
    
    // 如果是FormData类型的数据，确保Content-Type被正确处理
    if (config.data instanceof FormData) {
      console.log('检测到FormData，确保Content-Type由浏览器自动设置');
      delete config.headers['Content-Type']; // 让浏览器自动设置
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
    // 记录详细的错误信息
    const errorDetails = {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      headers: error.response?.headers,
      request: {
        headers: error.config?.headers || {},
        data: error.config?.data || null
      }
    };
    
    // 过滤掉敏感信息，比如Authorization头
    if (errorDetails.request.headers.Authorization) {
      errorDetails.request.headers.Authorization = '[FILTERED]';
    }
    
    console.error('API请求错误详情:', errorDetails);
    console.error('错误堆栈:', error.stack);
    
    // 处理401未授权错误
    if (error.response && error.response.status === 401) {
      console.warn('收到401未授权响应，即将注销用户并重定向');
      const userStore = useUserStore();
      userStore.logout(); // 登出用户
      window.location.href = '/login'; // 重定向到登录页
      
      // 向用户显示友好的错误消息
      ElMessage({
        message: '您的登录已过期，请重新登录',
        type: 'warning',
        duration: 5000
      });
    }
    
    // 处理400错误 - 参数验证失败
    if (error.response && error.response.status === 400) {
      console.error('参数验证失败:', error.response.data);
      
      // 尝试提取具体的错误字段和消息
      const errorData = error.response.data;
      if (errorData.errors) {
        Object.keys(errorData.errors).forEach(field => {
          console.error(`字段 ${field} 错误:`, errorData.errors[field]);
        });
      }
    }
    
    // 处理500内部服务器错误
    if (error.response && error.response.status === 500) {
      console.error('服务器内部错误，请检查后端日志');
      
      // 如果错误信息中包含HTML，可能是Django的错误页面
      if (typeof error.response.data === 'string' && error.response.data.includes('<!DOCTYPE html>')) {
        console.error('收到HTML错误页面，可能是Django的调试信息');
      }
    }
    
    return Promise.reject(error);
  }
);

export default instance; 