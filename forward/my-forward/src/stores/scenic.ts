import { defineStore } from 'pinia'
import axios from 'axios'

interface ProvinceData {
  name: string
  value: number
  scenics?: Array<{
    id: string
    name: string
    longitude: number
    latitude: number
  }>
}

interface ScenicLevel {
  name: string
  value: number
}

interface OpenTimeData {
  timeRange: string
  count: number
}

interface CommentData {
  scenicId: string
  scenicName: string
  sentimentScore: number
  sentimentIntensity: number
  commentCount: number
}

interface WordCloudItem {
  name: string
  value: number
}

interface TransportationFlow {
  source: string
  target: string
  value: number
}

export const useScenicStore = defineStore('scenic', {
  state: () => ({
    // 模块一：景区基础分布
    provinceData: [] as ProvinceData[],
    currentProvince: {} as ProvinceData,
    
    // 模块二：景区等级与分类
    scenicLevels: [] as ScenicLevel[],
    museumLevels: [] as ScenicLevel[],
    geoLevels: [] as ScenicLevel[],
    forestLevels: [] as ScenicLevel[],
    wetlandLevels: [] as ScenicLevel[],
    culturalLevels: [] as ScenicLevel[],
    natureLevels: [] as ScenicLevel[],
    
    scenicLevelPrices: [] as ScenicLevel[],
    museumLevelPrices: [] as ScenicLevel[],
    geoLevelPrices: [] as ScenicLevel[],
    forestLevelPrices: [] as ScenicLevel[],
    wetlandLevelPrices: [] as ScenicLevel[],
    culturalLevelPrices: [] as ScenicLevel[],
    natureLevelPrices: [] as ScenicLevel[],
    
    // 模块三：门票与开放时间
    ticketPrices: {
      scenicLevels: [] as any[],
      museumLevels: [] as any[],
      geoLevels: [] as any[],
      forestLevels: [] as any[],
      wetlandLevels: [] as any[],
      culturalLevels: [] as any[],
      natureLevels: [] as any[]
    },
    openTimeData: [] as OpenTimeData[],
    openTimeScenicMap: {} as Record<string, string[]>,
    
    // 模块四：评论与情感分析
    commentData: [] as CommentData[],
    wordCloudData: [] as WordCloudItem[],
    currentScenicId: '',
    
    // 模块五：交通与可达性
    transportationFlows: [] as TransportationFlow[],
    
    // 搜索相关
    searchResults: [] as any[],
    searchLoading: false,
    filterOptions: {
      provinces: [] as string[],
      cities: [] as string[],
      types: [] as string[],
      levels: [] as string[],
      priceRange: [0, 1000]
    }
  }),
  
  actions: {
    // 获取省份景区分布数据
    async getProvinceData() {
      try {
        const response = await axios.get('/api/data/province-distribution/')
        this.provinceData = response.data
        return response.data
      } catch (error) {
        console.error('获取省份数据失败:', error)
        return []
      }
    },
    
    // 获取景区等级数据
    async getScenicLevels() {
      try {
        const response = await axios.get('/api/data/scenic-levels/')
        const data = response.data
        
        this.scenicLevels = data.scenic_levels
        this.museumLevels = data.museum_levels
        this.geoLevels = data.geo_levels
        this.forestLevels = data.forest_levels
        this.wetlandLevels = data.wetland_levels
        this.culturalLevels = data.cultural_levels
        this.natureLevels = data.nature_levels
        
        this.scenicLevelPrices = data.scenic_level_prices
        this.museumLevelPrices = data.museum_level_prices
        this.geoLevelPrices = data.geo_level_prices
        this.forestLevelPrices = data.forest_level_prices
        this.wetlandLevelPrices = data.wetland_level_prices
        this.culturalLevelPrices = data.cultural_level_prices
        this.natureLevelPrices = data.nature_level_prices
        
        return data
      } catch (error) {
        console.error('获取景区等级数据失败:', error)
        return {}
      }
    },
    
    // 获取门票价格数据
    async getTicketData() {
      try {
        const response = await axios.get('/api/data/ticket-prices/')
        this.ticketPrices = response.data
        return response.data
      } catch (error) {
        console.error('获取门票价格数据失败:', error)
        return {}
      }
    },
    
    // 获取开放时间数据
    async getOpenTimeData() {
      try {
        const response = await axios.get('/api/data/open-times/')
        this.openTimeData = response.data.time_ranges
        this.openTimeScenicMap = response.data.scenic_map
        return response.data
      } catch (error) {
        console.error('获取开放时间数据失败:', error)
        return {}
      }
    },
    
    // 获取评论情感数据
    async getCommentData() {
      try {
        const response = await axios.get('/api/data/comment-analysis/')
        this.commentData = response.data
        return response.data
      } catch (error) {
        console.error('获取评论情感数据失败:', error)
        return []
      }
    },
    
    // 获取词云数据
    async getWordCloudData(scenicId: string) {
      try {
        const response = await axios.get(`/api/data/word-cloud/${scenicId}/`)
        this.wordCloudData = response.data
        this.currentScenicId = scenicId
        return response.data
      } catch (error) {
        console.error('获取词云数据失败:', error)
        return []
      }
    },
    
    // 获取交通方式数据
    async getTransportationData() {
      try {
        const response = await axios.get('/api/data/transportation/')
        this.transportationFlows = response.data
        return response.data
      } catch (error) {
        console.error('获取交通方式数据失败:', error)
        return []
      }
    },
    
    // 搜索景区
    async searchScenic(keyword: string, filters?: any) {
      this.searchLoading = true
      try {
        const response = await axios.get('/api/scenic/search/', { 
          params: { 
            keyword,
            ...filters
          } 
        })
        this.searchResults = response.data
        this.searchLoading = false
        return response.data
      } catch (error) {
        console.error('搜索景区失败:', error)
        this.searchLoading = false
        return []
      }
    },
    
    // 获取筛选选项
    async getFilterOptions() {
      try {
        const response = await axios.get('/api/data/filter-options/')
        this.filterOptions = response.data
        return response.data
      } catch (error) {
        console.error('获取筛选选项失败:', error)
        return {}
      }
    }
  }
}) 