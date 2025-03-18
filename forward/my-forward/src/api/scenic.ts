import request from './axios';

/**
 * 获取省份景区分布数据
 */
export function getProvinceDistribution() {
  return request({
    url: '/data/province-distribution/',
    method: 'get'
  });
}

/**
 * 获取景区等级与分类数据
 */
export function getScenicLevels() {
  return request({
    url: '/data/scenic-levels/',
    method: 'get'
  });
}

/**
 * 获取门票价格数据
 */
export function getTicketPrices() {
  return request({
    url: '/data/ticket-prices/',
    method: 'get'
  });
}

/**
 * 获取开放时间数据
 */
export function getOpenTimes() {
  return request({
    url: '/data/open-times/',
    method: 'get'
  });
}

/**
 * 获取评论情感分析数据
 */
export function getCommentAnalysis() {
  return request({
    url: '/data/comment-analysis/',
    method: 'get'
  });
}

/**
 * 获取景区词云数据
 * @param scenicId 景区ID
 */
export function getWordCloud(scenicId: string) {
  return request({
    url: `/data/word-cloud/${scenicId}/`,
    method: 'get'
  });
}

/**
 * 获取交通方式数据
 */
export function getTransportation() {
  return request({
    url: '/data/transportation/',
    method: 'get'
  });
}

/**
 * 搜索景区
 * @param keyword 搜索关键词
 * @param filters 筛选条件
 */
export function searchScenic(keyword: string, filters?: any) {
  return request({
    url: '/scenic/search/',
    method: 'get',
    params: {
      query: keyword,
      ...filters
    }
  });
}

/**
 * 获取筛选选项数据
 */
export function getFilterOptions() {
  return request({
    url: '/data/filter-options/',
    method: 'get'
  });
}

/**
 * 获取景区详情
 * @param scenicId 景区ID
 */
export function getScenicDetail(scenicId: string) {
  return request({
    url: `/scenic/${scenicId}/`,
    method: 'get'
  });
} 