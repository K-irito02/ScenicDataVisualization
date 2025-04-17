import { logFrontendError } from './admin';

/**
 * 前端错误日志记录服务
 */
class ErrorLogger {
  private isLogging = false; // 添加标志，防止递归记录日志
  
  /**
   * 记录错误
   * @param message 错误消息
   * @param level 错误级别
   * @param error 错误对象
   * @param location 错误位置/页面路径
   */
  logError(message: string, error?: Error | unknown, level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL' = 'ERROR', location?: string) {
    let errorMessage = message;
    let errorStack = '';
    
    // 如果提供了错误对象，获取更多信息
    if (error instanceof Error) {
      errorMessage = `${message}: ${error.message}`;
      errorStack = error.stack || '';
    } else if (error) {
      try {
        errorMessage = `${message}: ${JSON.stringify(error)}`;
      } catch (e) {
        errorMessage = `${message}: [无法序列化的错误对象]`;
      }
    }
    
    // 记录到控制台
    if (level === 'DEBUG') {
      console.debug(errorMessage);
    } else if (level === 'INFO') {
      console.info(errorMessage);
    } else if (level === 'WARNING') {
      console.warn(errorMessage);
    } else {
      console.error(errorMessage);
      if (errorStack) console.error(errorStack);
    }
    
    // 仅对WARNING、ERROR和CRITICAL级别发送到服务器
    if (['WARNING', 'ERROR', 'CRITICAL'].includes(level)) {
      // 防止递归日志记录，避免在记录日志时产生更多日志
      if (this.isLogging) {
        console.warn('已经在记录日志过程中，跳过发送到服务器');
        return;
      }
      
      // 修复路径检测逻辑，精确区分登录页面和管理后台页面
      const isLoginPage = window.location.pathname.includes('/login') || 
                          window.location.pathname.includes('/register') || 
                          window.location.pathname === '/admin' ||
                          window.location.pathname === '/';
                          
      // 检查是否在管理后台页面
      const isOnAdminDashboard = window.location.pathname.startsWith('/admin-dashboard');
      
      // 在登录页时跳过向服务器发送日志，但允许在管理后台页面发送
      if (isLoginPage && !isOnAdminDashboard) {
        console.info('在登录页面，跳过发送错误日志到服务器');
        return;
      }
      
      // 当前页面路径
      const currentLocation = location || window.location.pathname;
      
      // 设置标志，防止递归
      this.isLogging = true;
      
      // 发送到后端
      logFrontendError({
        level,
        message: errorMessage,
        traceback: errorStack,
        location: currentLocation
      }).catch(err => {
        // 如果发送失败，记录到控制台
        console.error('发送错误日志到服务器失败:', err);
      }).finally(() => {
        // 无论成功失败，最后都要重置标志
        this.isLogging = false;
      });
    }
  }
  
  /**
   * 记录调试信息
   */
  debug(message: string, details?: any, location?: string) {
    this.logError(message, details, 'DEBUG', location);
  }
  
  /**
   * 记录信息
   */
  info(message: string, details?: any, location?: string) {
    this.logError(message, details, 'INFO', location);
  }
  
  /**
   * 记录警告
   */
  warning(message: string, error?: Error | unknown, location?: string) {
    this.logError(message, error, 'WARNING', location);
  }
  
  /**
   * 记录错误
   */
  error(message: string, error?: Error | unknown, location?: string) {
    this.logError(message, error, 'ERROR', location);
  }
  
  /**
   * 记录严重错误
   */
  critical(message: string, error?: Error | unknown, location?: string) {
    this.logError(message, error, 'CRITICAL', location);
  }
}

// 创建单例
const errorLogger = new ErrorLogger();

export default errorLogger; 