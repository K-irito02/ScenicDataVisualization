<template>
  <div class="search-container">
    <div class="search-header">
      <card-container>
        <el-form :model="searchForm" label-width="80px" class="search-form">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="关键词">
                <el-input 
                  v-model="searchForm.keyword" 
                  placeholder="景区名称、特色等" 
                  clearable
                  @keyup.enter="handleSearch"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="省份">
                <el-select 
                  v-model="searchForm.province" 
                  placeholder="选择省份" 
                  clearable 
                  filterable
                  @change="handleProvinceChange"
                >
                  <el-option 
                    v-for="item in filterOptions.provinces" 
                    :key="item" 
                    :label="item" 
                    :value="item" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="城市">
                <el-select 
                  v-model="searchForm.city" 
                  placeholder="选择城市" 
                  clearable 
                  filterable
                  :disabled="!searchForm.province"
                  @change="handleCityChange"
                >
                  <el-option 
                    v-for="item in filteredCities" 
                    :key="item" 
                    :label="item" 
                    :value="item" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="区县">
                <el-select 
                  v-model="searchForm.district" 
                  placeholder="选择区县" 
                  clearable 
                  filterable
                  :disabled="!searchForm.province || !searchForm.city"
                >
                  <el-option 
                    v-for="item in filteredDistricts" 
                    :key="item" 
                    :label="item" 
                    :value="item" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="类型">
                <el-select 
                  v-model="searchForm.type" 
                  placeholder="景区类型" 
                  clearable
                  filterable
                  @change="handleTypeChange"
                >
                  <el-option 
                    v-for="item in filterOptions.types" 
                    :key="item" 
                    :label="item" 
                    :value="item" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="级别">
                <el-select 
                  v-model="searchForm.level" 
                  :placeholder="levelPlaceholder" 
                  clearable
                  filterable
                  :disabled="!searchForm.type || isWaterScenic"
                >
                  <el-option 
                    v-for="item in availableLevels" 
                    :key="item" 
                    :label="item" 
                    :value="item" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="价格">
                <el-slider 
                  v-model="searchForm.priceRange" 
                  range 
                  :min="0" 
                  :max="500" 
                  :step="10"
                  :marks="{0: '0', 100: '100', 200: '200', 300: '300', 400: '400', 500: '500'}"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </card-container>
    </div>
    
    <div class="search-result">
      <card-container>
        <template #actions>
          <div class="result-actions">
            <span class="result-count">找到 {{ totalCount }} 个结果</span>
            <div class="sort-options">
              <span>排序：</span>
              <el-radio-group v-model="sortType" size="small" @change="handleSort">
                <el-radio-button label="popularity">热度</el-radio-button>
                <el-radio-button label="price_asc">价格低到高</el-radio-button>
                <el-radio-button label="price_desc">价格高到低</el-radio-button>
                <el-radio-button label="rating">评分</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>
        
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="3" animated />
          <el-skeleton :rows="3" animated />
          <el-skeleton :rows="3" animated />
        </div>
        
        <div v-else-if="searchResult.length === 0" class="empty-result">
          <el-empty description="暂无符合条件的景区" />
          <div class="empty-suggestions">
            <p>您可以尝试：</p>
            <ul>
              <li>检查搜索关键字是否有误</li>
              <li>放宽筛选条件（类型、级别、价格范围等）</li>
              <li>选择不同的省份或城市</li>
              <li v-if="searchForm.type && searchForm.level">取消"{{ searchForm.level }}"级别筛选</li>
              <li v-if="searchForm.priceRange[0] > 0 || searchForm.priceRange[1] < 500">调整价格范围</li>
            </ul>
            <el-button type="primary" @click="handleReset" size="small" style="margin-top:10px">
              重置所有筛选条件
            </el-button>
          </div>
        </div>
        
        <div v-else class="result-grid">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="(item, index) in paginatedResults" :key="index">
              <scenic-card :scenic="item" />
            </el-col>
          </el-row>
          
          <div class="pagination-container">
            <el-pagination
              background
              layout="prev, pager, next"
              :total="totalCount"
              :page-size="pageSize"
              :current-page="currentPage"
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </card-container>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed, onMounted, watch } from 'vue'
import CardContainer from '@/components/common/CardContainer.vue'
import ScenicCard from '@/components/common/ScenicCard.vue'
import { useScenicStore } from '@/stores/scenic'
import { ElMessage } from 'element-plus'
import typeAndLevelData from '@/assets/search/type_level_data.json'
import locationData from '@/assets/search/location_data.json'
import axios from 'axios'

// 设置API基础URL
const API_BASE_URL = 'http://localhost:8000/api'

// API服务
const apiService = {
  // 获取景区搜索结果
  searchScenic: async (keyword = '', params = {}) => {
    try {
      console.log('请求URL:', `${API_BASE_URL}/scenic/search/`);
      console.log('请求参数:', { keyword, ...params });
      
      // 添加超时和错误处理
      const response = await axios.get(`${API_BASE_URL}/scenic/search/`, {
        params: {
          keyword,
          ...params
        },
        timeout: 10000 // 10秒超时
      })
      
      console.log('API响应数据:', response.data);
      return response.data
    } catch (error: any) {
      if (error.code === 'ECONNABORTED') {
        console.error('请求超时:', error);
        ElMessage.error('搜索请求超时，请检查后端服务是否正常运行');
      } else if (error.response) {
        console.error('服务器错误:', error.response.status, error.response.data);
        ElMessage.error(`服务器错误: ${error.response.status}`);
      } else if (error.request) {
        console.error('无响应错误:', error.request);
        ElMessage.error('无法连接到后端服务，请检查后端是否正在运行');
      } else {
        console.error('请求错误:', error.message);
        ElMessage.error(`请求错误: ${error.message}`);
      }
      // 返回空数组，以便前端能够正常处理
      return [];
    }
  },
  
  // 获取筛选选项数据
  getFilterOptions: async () => {
    try {
      // 这里优先使用本地JSON数据，若后端有专门的接口获取筛选选项，可以替换为API调用
      return {
        provinces: locationData.provinces,
        cities: locationData.cities,
        districts: locationData.districts,
        types: typeAndLevelData.types,
        typeLevels: typeAndLevelData.typeLevels
      }
    } catch (error) {
      console.error('获取筛选选项失败:', error)
      throw error
    }
  }
}

// 添加城市映射的类型声明
type CitiesRecord = Record<string, string[]>

// 添加TypeLevels类型定义
interface TypeLevels {
  [key: string]: string[];
}

// 筛选选项类型定义
interface FilterOptions {
  provinces: string[];
  cities: Record<string, string[]>;
  types: string[];
  levels: string[];
  districts: Record<string, string[]>;
}

export default defineComponent({
  name: 'Search',
  components: {
    CardContainer,
    ScenicCard
  },
  setup() {
    const scenicStore = useScenicStore()
    const loading = ref(false)
    const totalCount = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(12)
    const sortType = ref('popularity')
    const searchResult = ref<any[]>([])
    const hasInitialized = ref(false)
    
    // 筛选表单
    const searchForm = reactive({
      keyword: '',
      province: '',
      city: '',
      district: '',
      type: '',
      level: '',
      priceRange: [0, 500] as [number, number]
    })
    
    // 筛选选项
    const filterOptions = reactive<FilterOptions>({
      provinces: [],
      cities: {},
      types: [],
      levels: [],
      districts: {}
    })
    
    // 计算属性：判断是否为水利风景区类型
    const isWaterScenic = computed(() => {
      return searchForm.type === '水利风景区'
    })
    
    // 级别选择框的占位文本
    const levelPlaceholder = computed(() => {
      return isWaterScenic.value ? '无级别选择' : '景区级别'
    })
    
    // 根据当前选择的类型返回可用的级别
    const availableLevels = computed(() => {
      if (!searchForm.type || isWaterScenic.value) return []
      
      // 处理"A级景区"类型，使其能够映射到原来的"景区"类型的级别
      const typeKey = searchForm.type === 'A级景区' ? '景区' : searchForm.type;
      
      // 从typeLevels中获取当前类型的级别列表
      return (typeAndLevelData.typeLevels as TypeLevels)[typeKey] || []
    })
    
    // 使用本地JSON文件中的筛选选项
    const fetchFilterOptions = async () => {
      try {
        // 获取筛选选项数据
        const optionsData = await apiService.getFilterOptions()
        
        // 省份数据
        if (optionsData.provinces) {
          filterOptions.provinces = optionsData.provinces
        }
        
        // 城市数据
        if (optionsData.cities) {
          filterOptions.cities = optionsData.cities
        }
        
        // 区县数据
        if (optionsData.districts) {
          filterOptions.districts = optionsData.districts
        }
        
        // 类型数据 - 将"景区"改为"A级景区"
        if (optionsData.types) {
          filterOptions.types = optionsData.types.map(type => 
            type === '景区' ? 'A级景区' : type
          )
        }
        
        // 从typeLevels获取所有级别的展平数组（用于其他地方可能需要所有级别）
        if (optionsData.typeLevels) {
          const allLevels = new Set<string>()
          
          // 将"景区"对应的级别映射到"A级景区"
          const modifiedTypeLevels = { ...optionsData.typeLevels } as TypeLevels;
          if (modifiedTypeLevels['景区']) {
            modifiedTypeLevels['A级景区'] = modifiedTypeLevels['景区'];
            delete modifiedTypeLevels['景区'];
          }
          
          Object.values(modifiedTypeLevels).forEach(levels => {
            levels.forEach(level => allLevels.add(level))
          })
          filterOptions.levels = Array.from(allLevels)
        }
        
        console.log('获取到的筛选选项：', filterOptions)
      } catch (error) {
        console.error('获取筛选选项失败:', error)
        ElMessage.error('获取筛选选项失败，请刷新页面重试')
      }
    }
    
    // 使用类型断言修复索引访问
    const filteredCities = computed(() => {
      if (!searchForm.province) return []
      return (filterOptions.cities as CitiesRecord)[searchForm.province] || []
    })
    
    // 计算属性：根据选择的省份和城市筛选区县列表
    const filteredDistricts = computed(() => {
      if (!searchForm.province || !searchForm.city) return []
      
      const cityKey = `${searchForm.province}_${searchForm.city}`
      return filterOptions.districts[cityKey] || []
    })
    
    // 计算当前页面显示的数据
    const paginatedResults = computed(() => {
      // 直接返回搜索结果，因为后端已经实现了分页
      return searchResult.value;
    })
    
    // 恢复保存的搜索状态
    const restoreSavedState = () => {
      if (scenicStore.savedSearchState.hasSearched) {
        // 恢复搜索表单
        const savedForm = scenicStore.savedSearchState.searchForm
        searchForm.keyword = savedForm.keyword
        searchForm.province = savedForm.province
        searchForm.city = savedForm.city
        searchForm.district = savedForm.district || ''
        searchForm.type = savedForm.type
        searchForm.level = savedForm.level
        searchForm.priceRange = [...savedForm.priceRange]
        
        // 恢复排序和分页
        sortType.value = scenicStore.savedSearchState.sortType
        currentPage.value = scenicStore.savedSearchState.currentPage
        
        console.log('已恢复搜索状态:', {
          searchForm,
          currentPage: currentPage.value,
          sortType: sortType.value
        })
        
        // 立即执行搜索
        handleSearch()
      }
    }
    
    // 保存当前搜索状态
    const saveCurrentState = () => {
      scenicStore.saveSearchState(
        { ...searchForm },
        currentPage.value,
        sortType.value
      )
    }
    
    // 使用后端API进行景区搜索
    const handleSearch = async () => {
      loading.value = true
      
      try {
        // 构建API参数
        const params: any = {
          province: searchForm.province || undefined,
          city: searchForm.city || undefined,
          district: searchForm.district || undefined,
          type: searchForm.type === 'A级景区' ? '景区' : searchForm.type,
          level: searchForm.level || undefined,
          priceRange: searchForm.priceRange.join(',') || undefined,
          page: currentPage.value,
          page_size: pageSize.value
        }
        
        // 特殊处理：对于A级景区类型，根据级别调整发送的参数
        if (searchForm.type === 'A级景区') {
          if (searchForm.level) {
            // 如果选择了具体级别，如"5A景区"，直接发送完整级别名
            params.level = searchForm.level;
          }
        }
        
        console.log('发送API请求参数:', params);
        
        // 调用后端API
        const data = await apiService.searchScenic(searchForm.keyword, params)
        
        console.log('接收到的搜索结果:', data);
        
        // 处理响应数据
        if (Array.isArray(data)) {
          // 数组格式，直接使用
          searchResult.value = data;
          totalCount.value = data.length;
        } else if (data.results && Array.isArray(data.results)) {
          // 分页格式，包含results和total字段
          searchResult.value = data.results;
          // 使用后端返回的总数，而不是当前页结果的长度
          totalCount.value = data.total || data.results.length;
          
          // 如果后端返回了页码信息，更新对应的值
          if (data.page) {
            currentPage.value = data.page;
          }
          
          // 更新页大小（如果有必要）
          if (data.page_size && data.page_size !== pageSize.value) {
            pageSize.value = data.page_size;
          }
        } else {
          // 未知格式，尝试处理
          console.warn('未识别的API响应格式:', data)
          searchResult.value = data && typeof data === 'object' ? [data] : []
          totalCount.value = searchResult.value.length
        }
        
        // 根据排序类型排序
        handleSort()
        
        // 保存当前搜索状态到store
        saveCurrentState()
      } catch (error: any) {
        console.error('搜索失败:', error)
        
        // 增强错误处理
        if (error.response && error.response.status === 500) {
          ElMessage.error('后端服务器错误，请联系管理员检查服务器日志')
        } else {
          ElMessage.error('搜索失败，请重试')
        }
        
        searchResult.value = []
        totalCount.value = 0
      } finally {
        loading.value = false
      }
    }
    
    // 重置筛选条件
    const handleReset = () => {
      searchForm.keyword = ''
      searchForm.province = ''
      searchForm.city = ''
      searchForm.district = ''
      searchForm.type = ''
      searchForm.level = ''
      searchForm.priceRange = [0, 500]
      currentPage.value = 1
      sortType.value = 'popularity'
      
      // 重置store中的保存状态
      scenicStore.resetSearchState()
      
      handleSearch()
    }
    
    // 处理排序变更
    const handleSort = () => {
      if (searchResult.value.length > 0) {
        // 只需要重新排序，不需要重新请求
        const sortedResults = searchResult.value.slice()
        sortedResults.sort((a: any, b: any) => {
          // 其次按照选定的排序方式排序
          if (sortType.value === 'price_asc') {
            return (parseFloat(a.price) || 0) - (parseFloat(b.price) || 0)
          } else if (sortType.value === 'price_desc') {
            return (parseFloat(b.price) || 0) - (parseFloat(a.price) || 0)
          } else if (sortType.value === 'rating') {
            return (parseFloat(b.sentiment_score || b.rating) || 0) - 
                   (parseFloat(a.sentiment_score || a.rating) || 0)
          }
          
          // 默认按热度/人气排序
          return (parseInt(b.comment_count || b.popularity) || 0) - 
                 (parseInt(a.comment_count || a.popularity) || 0)
        })
        
        searchResult.value = sortedResults
        // 重置当前页码
        currentPage.value = 1
        
        // 保存当前状态
        saveCurrentState()
      }
    }
    
    // 处理分页变更
    const handlePageChange = (page: number) => {
      currentPage.value = page
      // 请求新页的数据
      handleSearch()
      // 保存当前状态 (已在handleSearch中进行)
    }
    
    // 处理省份变更
    const handleProvinceChange = () => {
      searchForm.city = ''
      searchForm.district = ''
    }
    
    // 处理城市变更
    const handleCityChange = () => {
      searchForm.district = ''
    }
    
    // 处理类型变更
    const handleTypeChange = () => {
      // 当类型变化时，清空级别选择
      searchForm.level = ''
      
      // 如果选择的是水利风景区，确保级别清空
      if (searchForm.type === '水利风景区') {
        searchForm.level = ''
      }
      
      // 如果类型从"A级景区"变为其他，或从其他变为"A级景区"，需要调整表单
      if (searchForm.type === 'A级景区') {
        // 可以在这里添加特定的处理逻辑
        console.log('选择了A级景区类型')
      }
    }
    
    // 监听状态变化，避免路由导航后状态丢失
    watch([searchForm, currentPage, sortType], () => {
      if (hasInitialized.value) {
        saveCurrentState()
      }
    }, { deep: true })
    
    onMounted(() => {
      fetchFilterOptions().then(() => {
        // 检查是否有之前保存的状态需要恢复
        if (scenicStore.savedSearchState.hasSearched) {
          restoreSavedState()
        } else {
          // 否则执行初始搜索
          handleSearch()
        }
        
        hasInitialized.value = true
      })
    })
    
    return {
      loading,
      searchForm,
      filterOptions,
      filteredCities,
      filteredDistricts,
      searchResult,
      paginatedResults,
      totalCount,
      currentPage,
      pageSize,
      sortType,
      availableLevels,
      handleSearch,
      handleReset,
      handleSort,
      handlePageChange,
      handleProvinceChange,
      handleCityChange,
      handleTypeChange,
      isWaterScenic,
      levelPlaceholder
    }
  }
})
</script>

<style scoped>
.search-container {
  padding: 20px;
}

.search-header {
  margin-bottom: 20px;
}

.search-form {
  padding: 10px 0;
}

.result-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-count {
  font-size: 14px;
  color: #606266;
}

.sort-options {
  display: flex;
  align-items: center;
}

.sort-options span {
  margin-right: 10px;
  font-size: 14px;
  color: #606266;
}

.loading-container,
.empty-result {
  padding: 40px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.result-grid {
  margin-top: 10px;
}

.pagination-container {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.empty-suggestions {
  margin-top: 20px;
  padding: 20px;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.empty-suggestions p {
  margin-bottom: 10px;
  font-size: 14px;
  color: #606266;
}

.empty-suggestions ul {
  margin-bottom: 10px;
  padding-left: 20px;
}

.empty-suggestions li {
  margin-bottom: 5px;
  font-size: 14px;
  color: #606266;
}
</style> 