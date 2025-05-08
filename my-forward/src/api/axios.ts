import axios from 'axios';
import { useUserStore } from '../stores/user';
import { ElMessage } from 'element-plus';
import errorLogger from './error-logger';

// 获取CSRF令牌函数
function getCsrfToken() {
  // 从cookie中获取csrf token
  const name = 'csrftoken=';
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookieArray = decodedCookie.split(';');
  
  for (let i = 0; i < cookieArray.length; i++) {
    let cookie = cookieArray[i].trim();
    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length, cookie.length);
    }
  }
  return '';
}

// 创建axios实例
const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  },
  // 设置跨域请求携带凭证
  withCredentials: true
});

// 请求拦截器
instance.interceptors.request.use(
  config => {
    const userStore = useUserStore();
    
    // 对于登录、注册等公开API，不需要检查token
    const publicAPIs = ['/api/login/', '/api/register/', '/api/email/send-code/', '/api/forgot-password/', '/api/reset-password/', '/api/admin/frontend-error-log/', '/api/scenic/search/', '/api/statistics/summary/'];
    const isPublicAPI = publicAPIs.some(api => config.url?.includes(api));
    
    // 添加CSRF令牌到请求头
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    // 如果是景区搜索API且用户已登录，添加身份认证信息
    if (config.url?.includes('/api/scenic/search/') && userStore.isAuthenticated()) {
      const token = userStore.token;
      if (token) {
        config.headers.Authorization = `Token ${token}`;
        console.log('[请求拦截器] 景区搜索API，用户已登录，添加身份认证');
      }
      return config;
    }
    
    if (isPublicAPI) {
      // 请求公开API，跳过token验证
      return config;
    }
    
    // 避免在登录页面进行API请求从而产生循环
    // 修复路径检测逻辑，精确区分登录页面和管理后台页面
    const isOnLoginPage = window.location.pathname.startsWith('/login') || 
                          window.location.pathname.startsWith('/register') || 
                          window.location.pathname === '/admin' || // 只匹配精确的 /admin 路径
                          window.location.pathname === '/';
    
    // 修改判断，排除管理后台路径                      
    const isOnAdminDashboard = window.location.pathname.startsWith('/admin-dashboard');
    
    // 特殊处理在登录页但不是公开API的情况 - 这可能是循环请求的根源
    if (isOnLoginPage && !isPublicAPI && !isOnAdminDashboard) {
      // 在登录页面时，直接拒绝非公开API的请求，避免循环
      return Promise.reject(new Error('在登录页面不应请求需要认证的API'));
    }
    
    // 检查token是否有效
    if (!userStore.isAuthenticated()) {
      console.warn('Token已过期或无效');
      
      // 避免在拦截器中直接重定向，而是抛出错误，让业务代码处理
      // 这样可以避免某些场景下的循环重定向
      if (isOnLoginPage) {
        // 如果已经在登录页，不再触发重定向和登出操作
        return Promise.reject(new Error('需要登录'));
      }
      
      // 仅在非登录页面使用logout重定向
      userStore.logout({ redirectToLogin: true, reason: 'expired' });
      
      return Promise.reject(new Error('身份验证已过期，请重新登录'));
    }
    
    const token = userStore.token;
    
    // 如果有token，在请求头中添加token
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    // 不要覆盖已设置的Content-Type
    if (!config.headers['Content-Type'] && config.data && !(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json';
    }
    
    // 如果是FormData类型的数据，确保Content-Type被正确处理
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']; // 让浏览器自动设置
    }
    
    return config;
  },
  error => {
    errorLogger.error('请求拦截器错误', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  response => {
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
    
    // 检查是否是登录请求
    const isLoginRequest = error.config?.url?.includes('/api/login/');
    
    // 修复路径检测逻辑，精确区分登录页面和管理后台页面
    const isLoginPage = window.location.pathname.includes('/login') || 
                       window.location.pathname.includes('/register') || 
                       window.location.pathname === '/admin' ||
                       window.location.pathname === '/';
    
    // 检查是否在管理后台页面                       
    const isOnAdminDashboard = window.location.pathname.startsWith('/admin-dashboard');
    
    // 只在非登录请求或非登录页时记录错误详情
    if (!isLoginRequest && (!isLoginPage || isOnAdminDashboard)) {
      errorLogger.error('API请求错误', {
        details: errorDetails,
        stack: error.stack
      });
    } else {
      // 在登录请求时只进行简单的控制台记录
      console.error('登录请求失败:', {
        status: error.response?.status,
        data: error.response?.data
      });
    }
    
    // 处理用户被禁用的情况 (403 Forbidden)
    if (error.response && error.response.status === 403 && 
        error.response.data && error.response.data.detail === '用户已被禁用') {
      
      // 如果是登录请求，不执行重定向，让登录组件自己处理错误
      if (isLoginRequest) {
        return Promise.reject(error);
      }
      
      console.warn('用户账号已被禁用');
      const userStore = useUserStore();
      
      // 避免在登录页面进行注销操作
      if (!isLoginPage || isOnAdminDashboard) {
        userStore.logout({ redirectToLogin: true, reason: 'disabled' }); // 登出用户并指定原因
        
        // 向用户显示友好的错误消息
        ElMessage({
          message: '您的账号已被管理员禁用，请联系管理员',
          type: 'error',
          duration: 5000
        });
      }
      
      return Promise.reject(error);
    }
    
    // 处理401未授权错误
    if (error.response && error.response.status === 401) {
      // 如果是登录请求，不执行重定向，让登录组件自己处理错误
      if (isLoginRequest) {
        return Promise.reject(error);
      }
      
      console.warn('收到401未授权响应');
      const userStore = useUserStore();
      
      // 避免在登录页面进行注销操作
      if (!isLoginPage || isOnAdminDashboard) {
        userStore.logout({ redirectToLogin: true, reason: 'unauthorized' }); // 登出用户并指定原因
        
        // 向用户显示友好的错误消息
        ElMessage({
          message: '您的登录已过期，请重新登录',
          type: 'warning',
          duration: 5000
        });
      }
    }
    
    // 处理400错误 - 参数验证失败
    if (error.response && error.response.status === 400) {
      errorLogger.error('参数验证失败', error.response.data);
      
      // 尝试提取具体的错误字段和消息
      const errorData = error.response.data;
      if (errorData.errors) {
        Object.keys(errorData.errors).forEach(field => {
          errorLogger.error(`字段 ${field} 错误`, errorData.errors[field]);
        });
      }
    }
    
    // 处理500内部服务器错误
    if (error.response && error.response.status === 500) {
      errorLogger.error('服务器内部错误，请检查后端日志');
      
      // 如果错误信息中包含HTML，可能是Django的错误页面
      if (typeof error.response.data === 'string' && error.response.data.includes('<!DOCTYPE html>')) {
        errorLogger.error('收到HTML错误页面，可能是Django的调试信息');
      }
    }
    
    return Promise.reject(error);
  }
);

export default instance; 