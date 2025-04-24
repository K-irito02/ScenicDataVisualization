import { defineStore } from 'pinia'
import { 
  getProvinceDistribution, 
  getScenicLevels, 
  getTicketPrices, 
  getOpenTimes, 
  getCommentAnalysis, 
  getWordCloud, 
  getTransportation, 
  searchScenic as apiSearchScenic, 
  getFilterOptions as apiGetFilterOptions,
  getScenicDetail,
  getProvinceCityDistribution,
  getDistrictDistribution,
  getTicketAvgPrice as apiGetTicketAvgPrice,
  getTicketBoxplotByType as apiGetTicketBoxplotByType,
  getTicketBoxplotByLevel as apiGetTicketBoxplotByLevel,
  getScenicTypeDistribution
} from '../api'

interface ProvinceData {
  name: string
  value: number
  scenics?: Array<{
    id: string
    name: string
    city?: string
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

// 雷达图数据接口
interface RadarDataItem {
  name: string
  value: number
}

// 柱状图数据接口
interface SunburstDataItem {
  name: string
  value: number
  children?: SunburstDataItem[]
}

// 定义搜索表单状态接口
interface SearchFormState {
  keyword: string
  province: string
  city: string
  district: string
  type: string
  level: string
  priceRange: [number, number]
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
    
    // 景区类型分布数据
    typeRadarData: [] as RadarDataItem[],
    typeSunburstData: {} as SunburstDataItem,
    
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
      cities: {} as Record<string, string[]>,
      types: [] as string[],
      levels: [] as string[],
      priceRange: [0, 1000] as [number, number]
    },
    
    // 保存的搜索状态
    savedSearchState: {
      searchForm: {
        keyword: '',
        province: '',
        city: '',
        district: '',
        type: '',
        level: '',
        priceRange: [0, 500] as [number, number]
      } as SearchFormState,
      currentPage: 1,
      sortType: 'popularity',
      hasSearched: false
    },
    
    // 景区详情
    scenicDetail: null as any
  }),
  
  actions: {
    // 保存搜索状态
    saveSearchState(searchForm: SearchFormState, currentPage: number, sortType: string) {
      this.savedSearchState.searchForm = { ...searchForm }
      this.savedSearchState.currentPage = currentPage
      this.savedSearchState.sortType = sortType
      this.savedSearchState.hasSearched = true
    },
    
    // 重置搜索状态
    resetSearchState() {
      this.savedSearchState = {
        searchForm: {
          keyword: '',
          province: '',
          city: '',
          district: '',
          type: '',
          level: '',
          priceRange: [0, 500]
        },
        currentPage: 1,
        sortType: 'popularity',
        hasSearched: false
      }
    },
    
    // 获取省份景区分布数据
    async getProvinceData() {
      try {
        const response = await getProvinceDistribution()
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
        const response = await getScenicLevels()
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
        const response = await getTicketPrices()
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
        const response = await getOpenTimes()
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
        const response = await getCommentAnalysis()
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
        const response = await getWordCloud(scenicId)
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
        const response = await getTransportation()
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
        const response = await apiSearchScenic(keyword, filters)
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
        const response = await apiGetFilterOptions()
        this.filterOptions = response.data
        return response.data
      } catch (error) {
        console.error('获取筛选选项失败:', error)
        return {}
      }
    },
    
    // 获取景区详情
    async getScenicDetail(scenicId: string | number) {
      try {
        // 如果ID以'S'开头，去掉前缀只使用数字部分
        let requestId = scenicId;
        if (typeof scenicId === 'string' && scenicId.startsWith('S') && !isNaN(parseInt(scenicId.substring(1)))) {
          requestId = scenicId.substring(1);
          console.log('Store中调整请求ID:', requestId);
        }
        
        const response = await getScenicDetail(requestId)
        this.scenicDetail = response.data
        return response.data
      } catch (error) {
        console.error('获取景区详情失败:', error)
        this.scenicDetail = null
        return null
      }
    },

    // 获取省份城市景区分布数据
    async getProvinceCityDistribution(provinceName: string) {
      try {
        const response = await getProvinceCityDistribution(provinceName)
        return response.data
      } catch (error) {
        console.error('获取省份城市景区分布数据失败:', error)
        return []
      }
    },
    
    // 获取区县景区分布数据
    async getDistrictDistribution(provinceName: string, cityName: string) {
      try {
        const response = await getDistrictDistribution(provinceName, cityName)
        return response.data
      } catch (error) {
        console.error('获取区县景区分布数据失败:', error)
        return []
      }
    },
    
    // 获取门票平均价格数据
    async getTicketAvgPrice(scenicType: string) {
      try {
        const response = await apiGetTicketAvgPrice(scenicType)
        return response.data
      } catch (error) {
        console.error('获取门票平均价格数据失败:', error)
        return []
      }
    },
    
    // 获取各景区类型的箱线图数据
    async getTicketBoxplotByType() {
      try {
        const response = await apiGetTicketBoxplotByType()
        return response.data
      } catch (error) {
        console.error('获取景区类型箱线图数据失败:', error)
        return []
      }
    },
    
    // 获取指定景区类型各等级的箱线图数据
    async getTicketBoxplotByLevel(scenicType: string) {
      try {
        const response = await apiGetTicketBoxplotByLevel(scenicType)
        return response.data
      } catch (error) {
        console.error('获取景区等级箱线图数据失败:', error)
        return []
      }
    },
    
    // 获取景区类型分布数据（用于雷达图和旭日图）
    async getScenicTypeDistribution() {
      try {
        const response = await getScenicTypeDistribution()
        // 检查响应数据结构是否符合预期
        if (response && response.data && response.data.radar_data && response.data.sunburst_data) {
          this.typeRadarData = response.data.radar_data
          this.typeSunburstData = response.data.sunburst_data
          return response.data
        } else {
          console.error('景区类型分布数据结构异常:', response)
          // 保持数据不变
          return null
        }
      } catch (error) {
        console.error('获取景区类型分布数据失败:', error)
        // 保持数据不变
        return null
      }
    }
  }
}) 