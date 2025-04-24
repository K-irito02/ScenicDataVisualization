import request from './axios';

/**
 * 获取所有用户信息(管理员接口)
 * @param params 分页参数
 */
export function getUsers(params: { page?: number, pageSize?: number } = {}) {
  return request({
    url: '/api/admin/users/',
    method: 'get',
    params
  });
}

/**
 * 获取用户操作记录(管理员接口)
 * @param params 查询参数：分页、用户ID筛选、记录类型、时间范围等
 */
export function getUserRecords(params: { 
  page?: number, 
  pageSize?: number, 
  user_id?: number,
  record_type?: string, 
  start_date?: string,
  end_date?: string,
  export?: boolean
} = {}) {
  return request({
    url: '/api/admin/user-records/',
    method: 'get',
    params,
    ...(params.export ? { responseType: 'blob' } : {})
  });
}

/**
 * 获取系统错误日志
 * @param params 查询参数：分页、日志级别、时间范围(天数)
 */
export function getSystemErrorLogs(params: { page?: number, pageSize?: number, level?: string, error_type?: string, days?: number } = {}) {
  return request({
    url: '/api/admin/error-logs/',
    method: 'get',
    params
  });
}

/**
 * 获取用户列表（管理员接口，与getUsers相同，保留兼容）
 * @param params 分页参数
 */
export function getAdminUsers(params: { page?: number, pageSize?: number } = {}) {
  return request({
    url: '/api/admin/users/',
    method: 'get',
    params
  });
}

/**
 * 记录前端错误
 * @param errorData 错误数据对象
 */
export function logFrontendError(errorData: { 
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL', 
  message: string, 
  traceback?: string,
  location?: string
}) {
  return request({
    url: '/api/admin/frontend-error/',
    method: 'post',
    data: errorData,
    headers: {
      'X-Anonymous-Error-Log': 'true'
    }
  });
}

/**
 * 删除用户操作记录
 * @param recordId 记录ID
 */
export function deleteUserRecord(recordId: number) {
  return request({
    url: `/api/admin/user-records/${recordId}/`,
    method: 'delete'
  });
}

/**
 * 切换用户状态（启用/禁用）
 * @param userId 用户ID
 */
export function toggleUserStatus(userId: number) {
  return request({
    url: '/api/admin/users/',
    method: 'post',
    data: { user_id: userId }
  });
}

/**
 * 更新用户信息
 * @param userId 用户ID
 * @param userData 用户数据
 */
export function updateUser(userId: number, userData: {
  username?: string;
  email?: string;
  location?: string;
  status?: 'active' | 'disabled';
}) {
  return request({
    url: `/api/admin/users/${userId}/`,
    method: 'put',
    data: userData
  });
}

/**
 * 获取用户统计信息
 * @param userId 用户ID
 */
export function getUserStats(userId: number) {
  return request({
    url: `/api/admin/users/${userId}/stats/`,
    method: 'get'
  });
} 