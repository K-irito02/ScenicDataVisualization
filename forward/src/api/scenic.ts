import type { 
  AttributeAnalysis, 
  TrafficAnalysis, 
  CommentAnalysis,
  PriceAnalysis,
  DistributionStatistics,
  IdentityAnalysisData,
  ScenicSpot,
  SearchResult,
  SearchParams
} from '@/types/scenic'

// 模拟API请求延迟
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * 获取景区分布统计数据
 */
export const getScenicDistribution = async (): Promise<DistributionStatistics> => {
  try {
    // 模拟API请求延迟
    await delay(500)
    
    // 返回模拟数据
    return {
      provinceData: [
        { name: '北京', value: 89, a5Count: 12, a4Count: 35, a3Count: 42 },
        { name: '天津', value: 45, a5Count: 5, a4Count: 18, a3Count: 22 },
        { name: '河北', value: 125, a5Count: 15, a4Count: 45, a3Count: 65 },
        { name: '山西', value: 98, a5Count: 8, a4Count: 32, a3Count: 58 },
        { name: '内蒙古', value: 108, a5Count: 10, a4Count: 38, a3Count: 60 },
        { name: '辽宁', value: 95, a5Count: 12, a4Count: 35, a3Count: 48 },
        { name: '吉林', value: 85, a5Count: 8, a4Count: 32, a3Count: 45 },
        { name: '黑龙江', value: 78, a5Count: 7, a4Count: 28, a3Count: 43 },
        { name: '上海', value: 65, a5Count: 10, a4Count: 25, a3Count: 30 },
        { name: '江苏', value: 168, a5Count: 22, a4Count: 58, a3Count: 88 },
        { name: '浙江', value: 178, a5Count: 25, a4Count: 60, a3Count: 93 },
        { name: '安徽', value: 145, a5Count: 18, a4Count: 48, a3Count: 79 },
        { name: '福建', value: 138, a5Count: 16, a4Count: 45, a3Count: 77 },
        { name: '江西', value: 125, a5Count: 12, a4Count: 42, a3Count: 71 },
        { name: '山东', value: 158, a5Count: 20, a4Count: 52, a3Count: 86 },
        { name: '河南', value: 145, a5Count: 15, a4Count: 48, a3Count: 82 },
        { name: '湖北', value: 138, a5Count: 18, a4Count: 45, a3Count: 75 },
        { name: '湖南', value: 142, a5Count: 17, a4Count: 46, a3Count: 79 },
        { name: '广东', value: 188, a5Count: 28, a4Count: 62, a3Count: 98 },
        { name: '广西', value: 148, a5Count: 18, a4Count: 48, a3Count: 82 },
        { name: '海南', value: 75, a5Count: 12, a4Count: 25, a3Count: 38 },
        { name: '重庆', value: 98, a5Count: 12, a4Count: 36, a3Count: 50 },
        { name: '四川', value: 168, a5Count: 22, a4Count: 55, a3Count: 91 },
        { name: '贵州', value: 108, a5Count: 10, a4Count: 38, a3Count: 60 },
        { name: '云南', value: 155, a5Count: 20, a4Count: 52, a3Count: 83 },
        { name: '西藏', value: 65, a5Count: 8, a4Count: 22, a3Count: 35 },
        { name: '陕西', value: 128, a5Count: 16, a4Count: 42, a3Count: 70 },
        { name: '甘肃', value: 95, a5Count: 8, a4Count: 32, a3Count: 55 },
        { name: '青海', value: 68, a5Count: 5, a4Count: 23, a3Count: 40 },
        { name: '宁夏', value: 55, a5Count: 4, a4Count: 18, a3Count: 33 },
        { name: '新疆', value: 98, a5Count: 10, a4Count: 32, a3Count: 56 },
        { name: '台湾', value: 85, a5Count: 12, a4Count: 28, a3Count: 45 },
        { name: '香港', value: 28, a5Count: 5, a4Count: 10, a3Count: 13 },
        { name: '澳门', value: 15, a5Count: 3, a4Count: 5, a3Count: 7 }
      ],
      levelDistribution: [
        { name: '5A级', value: 302 },
        { name: '4A级', value: 688 },
        { name: '3A级', value: 1245 },
        { name: '2A级', value: 876 },
        { name: '其他', value: 451 }
      ]
    }
  } catch (error) {
    console.error('获取景区分布数据失败:', error)
    throw error
  }
}

/**
 * 获取景区热力图数据
 */
export const getScenicHeatmap = async (): Promise<number[][]> => {
  try {
    // 模拟API请求延迟
    await delay(500)
    
    // 生成一些随机热力点数据 [经度, 纬度, 强度]
    const points: number[][] = []
    // 生成150个随机点
    for (let i = 0; i < 150; i++) {
      // 中国大致范围：经度73-135，纬度3-53
      const longitude = 73 + Math.random() * 62
      const latitude = 3 + Math.random() * 50
      // 强度1-100之间的随机值
      const intensity = Math.floor(Math.random() * 100) + 1
      points.push([longitude, latitude, intensity])
    }
    
    return points
  } catch (error) {
    console.error('获取景区热力图数据失败:', error)
    throw error
  }
}

/**
 * 获取价格分析数据
 */
export const getPriceAnalysis = async (): Promise<PriceAnalysis> => {
  try {
    // 模拟API请求延迟
    await delay(500)
    
    // 返回模拟数据
    return {
      levelPriceDistribution: [
        { 
          level: '5A', 
          min: 50, 
          q1: 95, 
          median: 120, 
          q3: 150, 
          max: 200,
          outliers: [225, 240, 260]
        },
        { 
          level: '4A', 
          min: 30, 
          q1: 60, 
          median: 85, 
          q3: 110, 
          max: 150,
          outliers: [180, 190]
        },
        { 
          level: '3A', 
          min: 20, 
          q1: 35, 
          median: 50, 
          q3: 75, 
          max: 100,
          outliers: [120, 130]
        },
        { 
          level: '其他', 
          min: 10, 
          q1: 20, 
          median: 35, 
          q3: 45, 
          max: 70,
          outliers: [85, 95]
        }
      ]
    }
  } catch (error) {
    console.error('获取价格分析数据失败:', error)
    throw error
  }
}

/**
 * 获取评论分析数据
 */
export const getCommentAnalysis = async (): Promise<CommentAnalysis> => {
  try {
    // 模拟API请求延迟
    await delay(500)
    
    // 返回模拟数据
    return {
      keywordCloud: [
        { word: '景色', weight: 100 },
        { word: '服务', weight: 75 },
        { word: '环境', weight: 95 },
        { word: '价格', weight: 80 },
        { word: '交通', weight: 70 },
        { word: '人多', weight: 65 },
        { word: '排队', weight: 60 },
        { word: '美丽', weight: 85 },
        { word: '干净', weight: 75 },
        { word: '拥挤', weight: 60 },
        { word: '壮观', weight: 90 },
        { word: '推荐', weight: 80 },
        { word: '值得', weight: 85 },
        { word: '特色', weight: 70 },
        { word: '文化', weight: 75 },
        { word: '历史', weight: 80 },
        { word: '自然', weight: 85 },
        { word: '方便', weight: 65 },
        { word: '体验', weight: 75 },
        { word: '传统', weight: 70 }
      ],
      frequencyCloud: [
        { word: '推荐', weight: 250 },
        { word: '值得一去', weight: 220 },
        { word: '景色优美', weight: 180 },
        { word: '人山人海', weight: 160 },
        { word: '服务态度', weight: 140 },
        { word: '环境优美', weight: 135 },
        { word: '交通便利', weight: 130 },
        { word: '历史悠久', weight: 128 },
        { word: '文化底蕴', weight: 120 },
        { word: '价格合理', weight: 115 },
        { word: '游客众多', weight: 112 },
        { word: '风景如画', weight: 110 },
        { word: '特色小吃', weight: 105 },
        { word: '自然景观', weight: 100 },
        { word: '人文景观', weight: 98 },
        { word: '气候宜人', weight: 95 },
        { word: '环境整洁', weight: 90 },
        { word: '适合拍照', weight: 88 },
        { word: '门票贵', weight: 85 },
        { word: '性价比高', weight: 80 }
      ]
    }
  } catch (error) {
    console.error('获取评论分析数据失败:', error)
    throw error
  }
}

/**
 * 获取交通分析数据
 */
export const getTrafficAnalysis = async (): Promise<TrafficAnalysis> => {
  try {
    // 模拟API请求延迟
    await delay(500)
    
    // 返回模拟数据
    return {
      methodsCount: {
        '公交': 150,
        '地铁': 120,
        '出租车': 100,
        '自驾': 200,
        '旅游大巴': 80,
        '火车': 90,
        '飞机': 60
      },
      sentimentByTrafficCount: [
        { methodsCount: 1, positive: 30, neutral: 50, negative: 20, mainMethod: '自驾' },
        { methodsCount: 2, positive: 45, neutral: 40, negative: 15, mainMethod: '公交+出租车' },
        { methodsCount: 3, positive: 60, neutral: 30, negative: 10, mainMethod: '地铁+公交+出租车' },
        { methodsCount: 4, positive: 70, neutral: 25, negative: 5, mainMethod: '地铁+公交+出租车+自驾' },
        { methodsCount: 5, positive: 80, neutral: 15, negative: 5, mainMethod: '全部交通方式' }
      ]
    }
  } catch (error) {
    console.error('获取交通分析数据失败:', error)
    throw error
  }
}

/**
 * 获取景区属性分析数据
 */
export const getAttributeAnalysis = async (): Promise<AttributeAnalysis> => {
  try {
    // 模拟API请求延迟
    await delay(500)
    
    // 返回模拟数据
    return {
      levelPriceData: [
        { level: '5A', priceRange: '0-50', count: 5 },
        { level: '5A', priceRange: '51-100', count: 25 },
        { level: '5A', priceRange: '101-150', count: 40 },
        { level: '5A', priceRange: '151-200', count: 20 },
        { level: '5A', priceRange: '201+', count: 10 },
        
        { level: '4A', priceRange: '0-50', count: 30 },
        { level: '4A', priceRange: '51-100', count: 50 },
        { level: '4A', priceRange: '101-150', count: 30 },
        { level: '4A', priceRange: '151-200', count: 10 },
        { level: '4A', priceRange: '201+', count: 5 },
        
        { level: '3A', priceRange: '0-50', count: 60 },
        { level: '3A', priceRange: '51-100', count: 30 },
        { level: '3A', priceRange: '101-150', count: 15 },
        { level: '3A', priceRange: '151-200', count: 5 },
        { level: '3A', priceRange: '201+', count: 0 },
        
        { level: '其他', priceRange: '0-50', count: 80 },
        { level: '其他', priceRange: '51-100', count: 20 },
        { level: '其他', priceRange: '101-150', count: 5 },
        { level: '其他', priceRange: '151-200', count: 0 },
        { level: '其他', priceRange: '201+', count: 0 }
      ],
      attributeHeatData: [
        { name: '自然风光', value: [0, 0, 90] },
        { name: '人文历史', value: [0, 1, 80] },
        { name: '主题乐园', value: [0, 2, 75] },
        { name: '温泉度假', value: [0, 3, 45] },
        { name: '海滨沙滩', value: [0, 4, 65] },
        
        { name: '自然风光', value: [1, 0, 85] },
        { name: '人文历史', value: [1, 1, 70] },
        { name: '主题乐园', value: [1, 2, 60] },
        { name: '温泉度假', value: [1, 3, 55] },
        { name: '海滨沙滩', value: [1, 4, 50] },
        
        { name: '自然风光', value: [2, 0, 70] },
        { name: '人文历史', value: [2, 1, 80] },
        { name: '主题乐园', value: [2, 2, 90] },
        { name: '温泉度假', value: [2, 3, 65] },
        { name: '海滨沙滩', value: [2, 4, 40] },
        
        { name: '自然风光', value: [3, 0, 50] },
        { name: '人文历史', value: [3, 1, 60] },
        { name: '主题乐园', value: [3, 2, 75] },
        { name: '温泉度假', value: [3, 3, 85] },
        { name: '海滨沙滩', value: [3, 4, 60] }
      ]
    }
  } catch (error) {
    console.error('获取景区属性分析数据失败:', error)
    throw error
  }
}

/**
 * 获取身份分析数据
 */
export const getIdentityAnalysis = async (): Promise<IdentityAnalysisData> => {
  try {
    // 模拟API请求延迟
    await delay(500)
    
    // 返回模拟数据
    return {
      sets: [
        { name: '5A景区', value: 588 },
        { name: '国家级自然保护区', value: 224 },
        { name: '国家级森林公园', value: 441 },
        { name: '国家级地质公园', value: 193 },
        { name: '国家级水利风景区', value: 219 },
        { name: '国家级文物保护单位', value: 831 },
        { name: '国家级湿地公园', value: 87 },
        { name: '国家级博物馆', value: 306 },
        { name: '5A景区 ∩ 国家级自然保护区', value: 45 },
        { name: '5A景区 ∩ 国家级森林公园', value: 78 },
        { name: '5A景区 ∩ 国家级地质公园', value: 52 },
        { name: '国家级自然保护区 ∩ 国家级森林公园', value: 65 },
        { name: '国家级自然保护区 ∩ 国家级地质公园', value: 38 },
        { name: '国家级森林公园 ∩ 国家级地质公园', value: 42 },
        { name: '5A景区 ∩ 国家级自然保护区 ∩ 国家级森林公园', value: 25 },
        { name: '5A景区 ∩ 国家级自然保护区 ∩ 国家级地质公园', value: 18 },
        { name: '5A景区 ∩ 国家级森林公园 ∩ 国家级地质公园', value: 22 },
        { name: '国家级自然保护区 ∩ 国家级森林公园 ∩ 国家级地质公园', value: 15 },
        { name: '5A景区 ∩ 国家级自然保护区 ∩ 国家级森林公园 ∩ 国家级地质公园', value: 10 }
      ],
      relations: [
        { source: '5A景区', target: '国家级自然保护区', value: 45 },
        { source: '5A景区', target: '国家级森林公园', value: 78 },
        { source: '5A景区', target: '国家级地质公园', value: 52 },
        { source: '5A景区', target: '国家级水利风景区', value: 35 },
        { source: '5A景区', target: '国家级文物保护单位', value: 120 },
        { source: '国家级自然保护区', target: '国家级森林公园', value: 65 },
        { source: '国家级自然保护区', target: '国家级地质公园', value: 38 },
        { source: '国家级自然保护区', target: '国家级水利风景区', value: 28 },
        { source: '国家级森林公园', target: '国家级地质公园', value: 42 },
        { source: '国家级森林公园', target: '国家级水利风景区', value: 32 },
        { source: '国家级地质公园', target: '国家级水利风景区', value: 25 },
        { source: '国家级文物保护单位', target: '国家级博物馆', value: 45 }
      ]
    }
  } catch (error) {
    console.error('获取身份分析数据失败:', error)
    throw error
  }
}

/**
 * 搜索景区
 */
export const searchScenic = async (params: SearchParams): Promise<SearchResult> => {
  try {
    // 模拟API请求延迟
    await delay(500)
    
    // 返回模拟数据
    const list: ScenicSpot[] = Array(10).fill(0).map((_, index) => ({
      id: 1000 + index,
      name: `${params.keyword || ''}景区${index + 1}`,
      level: ['5A', '4A', '3A', '2A', '其他'][Math.floor(Math.random() * 5)],
      price: Math.floor(Math.random() * 200) + 50,
      location: {
        province: params.province || '北京',
        city: params.city || '北京市',
        address: '某区某街道',
        latitude: 116.3 + Math.random() * 0.5,
        longitude: 39.9 + Math.random() * 0.5
      },
      description: '这是一个风景优美的景区，拥有丰富的自然和人文景观...',
      mainImage: `https://example.com/images/scenic_${index + 1}.jpg`,
      tags: ['自然风光', '人文历史', '亲子游', '情侣游'],
      score: 4.5,
      commentCount: Math.floor(Math.random() * 5000) + 500,
      collected: Math.random() > 0.5,
      trafficMethods: ['公交', '地铁', '出租车', '自驾'].slice(0, Math.floor(Math.random() * 4) + 1)
    }))
    
    return {
      totalCount: 135,
      list
    }
  } catch (error) {
    console.error('搜索景区失败:', error)
    throw error
  }
}

/**
 * 获取景区详情
 */
export const getScenicDetail = async (id: number): Promise<ScenicSpot> => {
  try {
    // 模拟API请求延迟
    await delay(500)
    
    // 返回模拟数据
    return {
      id,
      name: `景区${id}`,
      level: ['5A', '4A', '3A', '2A', '其他'][Math.floor(Math.random() * 5)],
      price: Math.floor(Math.random() * 200) + 50,
      location: {
        province: '北京',
        city: '北京市',
        address: '某区某街道',
        latitude: 116.397428,
        longitude: 39.90923
      },
      description: '这是一个风景优美的景区，拥有丰富的自然和人文景观...',
      mainImage: `https://example.com/images/scenic_${id}.jpg`,
      tags: ['自然风光', '人文历史', '亲子游', '情侣游'],
      score: 4.5,
      commentCount: 2500,
      collected: false,
      trafficMethods: ['公交', '地铁', '出租车', '自驾'],
      comments: [
        {
          id: 1,
          user: '用户A',
          avatar: 'https://example.com/avatars/user1.jpg',
          content: '景色非常美丽，服务也很好，值得一去！',
          score: 5,
          date: '2023-05-15'
        },
        {
          id: 2,
          user: '用户B',
          avatar: 'https://example.com/avatars/user2.jpg',
          content: '人有点多，但整体体验不错。',
          score: 4,
          date: '2023-05-10'
        },
        {
          id: 3,
          user: '用户C',
          avatar: 'https://example.com/avatars/user3.jpg',
          content: '门票略贵，但景色确实很美。',
          score: 4,
          date: '2023-05-05'
        }
      ]
    }
  } catch (error) {
    console.error('获取景区详情失败:', error)
    throw error
  }
}

/**
 * 收藏景区
 */
export const favoriteScenicSpot = async (id: number): Promise<boolean> => {
  try {
    // 模拟API请求延迟
    await delay(500)
    
    console.log(`收藏景区ID: ${id}`)
    // 返回模拟结果
    return true
  } catch (error) {
    console.error('收藏景区失败:', error)
    throw error
  }
}

/**
 * 取消收藏景区
 */
export const unfavoriteScenicSpot = async (id: number): Promise<boolean> => {
  try {
    // 模拟API请求延迟
    await delay(500)
    
    console.log(`取消收藏景区ID: ${id}`)
    // 返回模拟结果
    return true
  } catch (error) {
    console.error('取消收藏景区失败:', error)
    throw error
  }
} 