import request from './axios';

/**
 * 获取所有用户信息(管理员接口)
 */
export function getUsers() {
  return request({
    url: '/admin/users/',
    method: 'get'
  });
}

/**
 * 获取用户操作记录(管理员接口)
 */
export function getUserRecords() {
  return request({
    url: '/admin/user-records/',
    method: 'get'
  });
} 