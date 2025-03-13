// 模拟数据服务
import Mock from 'mockjs'
import type { ScenicSpot } from '@/types/scenic'

interface MockRequest {
  url: string;
  type: string;
  body: any;
}

// 用户登录API
Mock.mock('/api/user/login', 'post', (options: MockRequest) => {
  const { username, password } = JSON.parse(options.body)
  
  // 简单的用户名密码验证
  if (username && password) {
    return {
      code: 200,
      data: {
        token: 'user_mock_token_' + Mock.Random.guid(),
        username: username
      },
      message: '登录成功'
    }
  } else {
    return {
      code: 401,
      message: '用户名或密码错误'
    }
  }
})

// 管理员登录API
Mock.mock('/api/admin/login', 'post', (options: MockRequest) => {
  const { username, password } = JSON.parse(options.body)
  
  // 管理员验证，这里简单判断用户名是否包含admin
  if (username && password && username.includes('admin')) {
    return {
      code: 200,
      data: {
        token: 'admin_mock_token_' + Mock.Random.guid(),
        username: username
      },
      message: '管理员登录成功'
    }
  } else {
    return {
      code: 401,
      message: '管理员用户名或密码错误'
    }
  }
})

// 景区搜索API
Mock.mock(/\/api\/scenic\/search/, 'get', (options: MockRequest) => {
  // 解析查询参数
  const url = options.url
  const params = new URLSearchParams(url.split('?')[1])
  const keyword = params.get('keyword') || ''
  
  // 生成模拟数据
  const count = Mock.Random.integer(5, 15)
  const scenicSpots: ScenicSpot[] = []
  
  for (let i = 0; i < count; i++) {
    const level = Mock.Random.pick(['5A', '4A', '3A', '2A', '省级'])
    const trafficCount = Mock.Random.integer(1, 5)
    const trafficMethods: string[] = []
    const allTraffic = ['公交', '地铁', '出租车', '自驾', '旅游大巴', '火车', '飞机']
    
    for (let j = 0; j < trafficCount; j++) {
      const method = Mock.Random.pick(allTraffic.filter(m => !trafficMethods.includes(m)))
      if (method) trafficMethods.push(method)
    }
    
    // 随机特殊身份
    const identities = [
      'museumLevel', 'geologicalParkLevel', 'waterScenicSpot', 
      'forestParkLevel', 'wetlandLevel', 'culturalRelicLevel', 'natureReserveLevel'
    ]
    const selectedIdentities = Mock.Random.integer(0, 3)
    const identity: Record<string, string | boolean> = {}
    
    for (let k = 0; k < selectedIdentities; k++) {
      const idType = Mock.Random.pick(identities.filter(id => !(id in identity)))
      if (idType === 'waterScenicSpot') {
        identity[idType] = true
      } else if (idType) {
        identity[idType] = '国家级'
      }
    }
    
    // 生成评论
    const commentCount = Mock.Random.integer(3, 8)
    const comments = []
    
    for (let c = 0; c < commentCount; c++) {
      comments.push({
        id: c + 1,
        user: `用户${Mock.Random.word(3, 6)}`,
        avatar: `https://example.com/avatars/user${c + 1}.jpg`,
        content: Mock.Random.csentence(20, 100),
        score: Mock.Random.integer(1, 5),
        date: Mock.Random.date('yyyy-MM-dd')
      })
    }
    
    scenicSpots.push({
      id: Mock.Random.integer(1000, 9999),
      name: keyword ? 
        `${keyword}${Mock.Random.cword(2, 6)}景区` : 
        `${Mock.Random.cword(2, 4)}${Mock.Random.cword(2, 4)}景区`,
      location: {
        province: Mock.Random.province(),
        city: Mock.Random.city(),
        address: Mock.Random.county() + Mock.Random.cword(5, 10),
        latitude: parseFloat(Mock.Random.float(18, 40, 6, 6).toFixed(6)),
        longitude: parseFloat(Mock.Random.float(100, 130, 6, 6).toFixed(6))
      },
      level,
      price: Mock.Random.integer(20, 300),
      trafficMethods,
      description: Mock.Random.cparagraph(2, 4),
      mainImage: `https://example.com/images/scenic_${Mock.Random.integer(1, 100)}.jpg`,
      tags: [Mock.Random.pick(['自然风光', '人文历史', '亲子游', '情侣游'])],
      score: parseFloat(Mock.Random.float(3.5, 5, 1, 1).toFixed(1)),
      commentCount: Mock.Random.integer(100, 5000),
      collected: Mock.Random.boolean(),
      ...identity,
      comments
    } as ScenicSpot)
  }
  
  return {
    code: 200,
    data: scenicSpots
  }
})

// 景区详情API
Mock.mock(/\/api\/scenic\/\w+/, 'get', (options: MockRequest) => {
  const id = options.url.split('/').pop()
  
  // 生成单个景区详情
  const level = Mock.Random.pick(['5A', '4A', '3A', '2A', '省级'])
  const trafficCount = Mock.Random.integer(1, 5)
  const trafficMethods: string[] = []
  const allTraffic = ['公交', '地铁', '出租车', '自驾', '旅游大巴', '火车', '飞机']
  
  for (let j = 0; j < trafficCount; j++) {
    const method = Mock.Random.pick(allTraffic.filter(m => !trafficMethods.includes(m)))
    if (method) trafficMethods.push(method)
  }
  
  // 随机特殊身份
  const identities = [
    'museumLevel', 'geologicalParkLevel', 'waterScenicSpot', 
    'forestParkLevel', 'wetlandLevel', 'culturalRelicLevel', 'natureReserveLevel'
  ]
  const selectedIdentities = Mock.Random.integer(0, 3)
  const identity: Record<string, string | boolean> = {}
  
  for (let k = 0; k < selectedIdentities; k++) {
    const idType = Mock.Random.pick(identities.filter(id => !(id in identity)))
    if (idType === 'waterScenicSpot') {
      identity[idType] = true
    } else if (idType) {
      identity[idType] = '国家级'
    }
  }
  
  // 生成评论
  const commentCount = Mock.Random.integer(3, 8)
  const comments = []
  
  for (let c = 0; c < commentCount; c++) {
    comments.push({
      id: c + 1,
      user: `用户${Mock.Random.word(3, 6)}`,
      avatar: `https://example.com/avatars/user${c + 1}.jpg`,
      content: Mock.Random.csentence(20, 100),
      score: Mock.Random.integer(1, 5),
      date: Mock.Random.date('yyyy-MM-dd')
    })
  }
  
  const scenic: ScenicSpot = {
    id: parseInt(id || Mock.Random.integer(1000, 9999).toString()),
    name: `${Mock.Random.cword(2, 4)}${Mock.Random.cword(2, 4)}景区`,
    location: {
      province: Mock.Random.province(),
      city: Mock.Random.city(),
      address: Mock.Random.county() + Mock.Random.cword(5, 10),
      latitude: parseFloat(Mock.Random.float(18, 40, 6, 6).toFixed(6)),
      longitude: parseFloat(Mock.Random.float(100, 130, 6, 6).toFixed(6))
    },
    level,
    price: Mock.Random.integer(20, 300),
    trafficMethods,
    description: Mock.Random.cparagraph(2, 4),
    mainImage: `https://example.com/images/scenic_${Mock.Random.integer(1, 100)}.jpg`,
    tags: [Mock.Random.pick(['自然风光', '人文历史', '亲子游', '情侣游'])],
    score: parseFloat(Mock.Random.float(3.5, 5, 1, 1).toFixed(1)),
    commentCount: Mock.Random.integer(100, 5000),
    collected: Mock.Random.boolean(),
    ...identity,
    comments
  } as ScenicSpot
  
  return {
    code: 200,
    data: scenic
  }
})

// 用户收藏API
Mock.mock('/api/user/favorites', 'get', () => {
  const count = Mock.Random.integer(0, 5)
  const favorites = []
  
  for (let i = 0; i < count; i++) {
    favorites.push({
      scenicId: Mock.Random.guid(),
      name: `${Mock.Random.cword(2, 4)}${Mock.Random.cword(2, 4)}景区`,
      addTime: Mock.Random.datetime()
    })
  }
  
  return {
    code: 200,
    data: favorites
  }
})

// 收藏景区
Mock.mock('/api/user/favorite', 'post', () => {
  return {
    code: 200,
    data: null,
    message: '收藏成功'
  }
})

// 取消收藏
Mock.mock('/api/user/favorite', 'delete', () => {
  return {
    code: 200,
    data: null,
    message: '取消收藏成功'
  }
})

export default Mock 