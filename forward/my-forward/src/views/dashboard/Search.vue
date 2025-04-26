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
                  @change="handlePriceRangeChange"
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
            <span class="result-count">找到 {{ pageConfig.totalCount }} 个结果</span>
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
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="i in 8" :key="i">
              <div class="scenic-card-skeleton">
                <div class="image-skeleton"></div>
                <div class="content-skeleton">
                  <div class="title-skeleton"></div>
                  <div class="location-skeleton"></div>
                  <div class="info-skeleton">
                    <div class="price-skeleton"></div>
                    <div class="type-skeleton"></div>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
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
              v-if="pageConfig.totalCount > 0"
              :key="rerenderPagination"
              background
              layout="prev, pager, next, jumper"
              :total="pageConfig.totalCount"
              :page-size="pageConfig.pageSize"
              :current-page="pageConfig.currentPage"
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </card-container>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import CardContainer from '@/components/common/CardContainer.vue'
import ScenicCard from '@/components/common/ScenicCard.vue'
import { useScenicStore } from '@/stores/scenic'
import { ElMessage } from 'element-plus'
import typeAndLevelData from '@/assets/search/type_level_data.json'
import locationData from '@/assets/search/location_data.json'
import { request } from '@/api'
import { processImageUrl, DEFAULT_IMAGE } from '@/api/image-proxy'

// 设置API基础URL
const API_BASE_URL = 'http://localhost:8000/api'

// API服务
const apiService = {
  // 获取景区搜索结果
  searchScenic: async (keyword = '', params = {}, timeout = 10000) => {
    try {
      console.log('请求URL:', `${API_BASE_URL}/api/scenic/search/`);
      console.log('请求参数:', { keyword, ...params });
      
      // 使用request实例，确保在用户登录时能正确传递token
      const response = await request.get(`/api/scenic/search/`, {
        params: {
          keyword,
          ...params
        },
        timeout: timeout // 可配置超时
      })
      
      console.log('API响应状态码:', response.status);
      
      // 增强的数据结构验证和日志
      if (!response.data) {
        console.error('API响应为空或无效');
        return { results: [], total: 0, page: 1, page_size: 10, pages: 0 };
      }
      
      // 全面检查响应数据结构
      console.log('API响应数据类型:', typeof response.data);
      console.log('是否为数组:', Array.isArray(response.data));
      
      // 规范化响应数据结构
      let normalizedData;
      
      if (Array.isArray(response.data)) {
        // 数组情况 - 包装为标准分页格式
        console.log('处理API返回的数组数据，长度:', response.data.length);
        normalizedData = {
          results: response.data,
          total: response.data.length,
          page: 1,
          page_size: response.data.length,
          pages: 1
        };
      } else if (typeof response.data === 'object') {
        // 非null对象情况
        console.log('对象键:', Object.keys(response.data));
        
        if (response.data.results && Array.isArray(response.data.results)) {
          // 标准分页格式
          console.log('标准分页响应，结果数量:', response.data.results.length);
          normalizedData = response.data;
        } else if (!response.data.results) {
          // 单一对象，可能是单个景区结果
          console.log('单一对象响应，无results字段，可能是单个景区');
          // 确认是否有典型的景区对象字段
          if (response.data.name || response.data.scenic_id) {
            console.log('识别为单个景区对象，包装为标准格式');
            normalizedData = {
              results: [response.data],
              total: 1,
              page: 1,
              page_size: 1,
              pages: 1
            };
          } else {
            // 可能是其他格式的对象
            console.warn('无法识别的对象结构，尝试保持原样');
            normalizedData = response.data;
          }
        } else {
          // 其他情况，保持原样
          console.warn('未识别的对象结构，保持原样');
          normalizedData = response.data;
        }
      } else {
        // 其他情况：字符串、数字等，返回空结果
        console.error('API返回了无效数据类型:', response.data);
        normalizedData = { results: [], total: 0, page: 1, page_size: 10, pages: 0 };
      }
      
      console.log('规范化后的响应数据:', normalizedData);
      return normalizedData;
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
      // 返回标准化的空结果对象，而不是空数组
      return { results: [], total: 0, page: 1, page_size: 10, pages: 0 };
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
    const sortType = ref('popularity')
    const searchResult = ref<any[]>([])
    const hasInitialized = ref(false)
    const rerenderPagination = ref(0) // 用于强制重新渲染分页组件
    
    // 分页直接使用对象，避免响应式问题
    const pageConfig = reactive({
      currentPage: 1,
      totalCount: 0,
      pageSize: 12
    })
    
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
      
      // 调试可用级别
      console.log('获取可用级别 - 类型:', typeKey);
      
      // 从typeLevels中获取当前类型的级别列表
      const levels = (typeAndLevelData.typeLevels as TypeLevels)[typeKey] || [];
      console.log('级别列表:', levels);
      return levels;
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
    
    // 计算总页数
    const totalPages = computed(() => {
      return Math.ceil(pageConfig.totalCount / pageConfig.pageSize) || 1;
    })
    
    // 计算当前页面显示的数据
    const paginatedResults = computed(() => {
      // 直接返回搜索结果，因为后端已经实现了分页
      console.log(`[分页计算] 返回搜索结果, 长度: ${searchResult.value.length}, 当前页: ${pageConfig.currentPage}`);
      return searchResult.value;
    })
    
    // 恢复保存的搜索状态
    const restoreSavedState = () => {
      if (scenicStore.savedSearchState.hasSearched) {
        // 恢复搜索表单
        const savedForm = scenicStore.savedSearchState.searchForm
        searchForm.keyword = savedForm.keyword || ''
        searchForm.province = savedForm.province || ''
        searchForm.city = savedForm.city || ''
        searchForm.district = savedForm.district || ''
        searchForm.type = savedForm.type || ''
        searchForm.level = savedForm.level || ''
        
        // 安全处理priceRange，确保它是数组
        if (Array.isArray(savedForm.priceRange) && savedForm.priceRange.length >= 2) {
          searchForm.priceRange = [...savedForm.priceRange]
        } else {
          // 提供默认值
          searchForm.priceRange = [0, 500]
          console.warn('[恢复状态] priceRange格式不正确，使用默认值')
        }
        
        // 恢复排序和分页
        sortType.value = scenicStore.savedSearchState.sortType || 'popularity'
        
        // 设置当前页码，确保使用pageConfig
        pageConfig.currentPage = scenicStore.savedSearchState.currentPage || 1
        console.log(`[恢复状态] 已恢复页码: ${pageConfig.currentPage}`);
        
        console.log('已恢复搜索状态:', {
          searchForm,
          currentPage: pageConfig.currentPage,
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
        pageConfig.currentPage,
        sortType.value
      )
    }
    
    // 图片预加载函数
    const preloadImages = (results: any[]) => {
      if (!results || results.length === 0) return;
      
      console.log('[预加载] 开始预加载图片，数量:', results.length);
      
      // 创建一个单一的批处理，延迟100ms开始批量预加载
      setTimeout(() => {
        // 批量加载 - 同时最多加载5张图片
        let currentIndex = 0;
        const batchSize = 5;
        
        const loadNextBatch = () => {
          const batch = results.slice(currentIndex, currentIndex + batchSize);
          currentIndex += batchSize;
          
          if (batch.length === 0) {
            console.log('[预加载] 所有图片预加载完成');
            return;
          }
          
          console.log(`[预加载] 加载批次 ${Math.ceil(currentIndex / batchSize)}, 数量: ${batch.length}`);
          
          // 使用Promise.all并行加载一批图片
          const preloadPromises = batch.map(item => {
            return new Promise<void>((resolve) => {
              if (!item.image) {
                resolve();
                return;
              }
              
              // 使用预加载图片
              try {
                const imgUrl = processImageUrl(item.image, DEFAULT_IMAGE);
                
                console.log(`[预加载] 开始加载图片: ${imgUrl.substring(0, 100)}...`);
                
                // 创建图片对象并设置加载事件
                const img = new Image();
                
                // 设置超时，避免图片加载太久
                const timeout = setTimeout(() => {
                  console.warn(`[预加载] 图片加载超时: ${imgUrl.substring(0, 50)}...`);
                  resolve();
                }, 5000);
                
                img.onload = () => {
                  clearTimeout(timeout);
                  console.log(`[预加载] 图片加载成功: ${imgUrl.substring(0, 50)}...`);
                  resolve();
                };
                
                img.onerror = () => {
                  clearTimeout(timeout);
                  console.error(`[预加载] 图片加载失败: ${imgUrl.substring(0, 50)}...`);
                  resolve();
                };
                
                // 开始加载
                img.src = imgUrl;
              } catch (error) {
                console.error(`[预加载] 处理图片URL出错:`, error);
                resolve();
              }
            });
          });
          
          // 等待所有图片加载完成后，继续下一批
          Promise.all(preloadPromises).then(() => {
            if (currentIndex < results.length) {
              setTimeout(loadNextBatch, 200); // 每批次间隔200ms
            } else {
              console.log('[预加载] 所有批次加载完成');
            }
          });
        };
        
        // 开始加载第一批
        loadNextBatch();
      }, 100);
    };
    
    // 处理搜索
    const handleSearch = async (resetPage = false, skipSaveState = false) => {
      console.log('[搜索] 开始搜索，重置页码?', resetPage, '跳过记录?', skipSaveState);
      
      if (resetPage) {
        console.log(`[分页] 重置页码: 从 ${pageConfig.currentPage} 到 1`);
        pageConfig.currentPage = 1;
      }
      
      console.log('[搜索] 当前搜索条件:', {
        关键词: searchForm.keyword,
        省份: searchForm.province,
        城市: searchForm.city,
        区县: searchForm.district,
        类型: searchForm.type,
        等级: searchForm.level,
        价格范围: searchForm.priceRange.join('-'),
        排序方式: sortType.value,
        页码: pageConfig.currentPage,
        每页数量: pageConfig.pageSize
      });

      // 清空搜索结果防止闪烁
      searchResult.value = [];
      loading.value = true;
      
      try {
        // 构建API请求参数
        const params: Record<string, any> = {
          keyword: searchForm.keyword?.trim() || '',
          page: pageConfig.currentPage,
          page_size: pageConfig.pageSize,
          sort_by: sortType.value
        }
        
        // 添加可选参数
        if (searchForm.province) params.province = searchForm.province;
        if (searchForm.city) params.city = searchForm.city;
        if (searchForm.district) params.district = searchForm.district;
        if (searchForm.type) params.type = searchForm.type;
        if (searchForm.level) params.level = searchForm.level;
        
        // 始终发送价格范围参数，无论是否是默认值
        params.priceRange = `${searchForm.priceRange[0]},${searchForm.priceRange[1]}`;
        console.log(`[价格筛选] 设置价格范围: ${params.priceRange}`);
        
        console.log('[搜索] 发送API请求:', params);
        
        const response = await apiService.searchScenic(searchForm.keyword, params, 20000)
        const data = response;
        console.log('[搜索] 搜索结果:', data);
        
        // 标记已经初始化过搜索
        hasInitialized.value = true;
        
        // 只有当不是跳过记录状态时，才保存搜索状态
        if (!skipSaveState) {
          console.log('[搜索] 保存搜索状态:', {
            searchForm,
            currentPage: pageConfig.currentPage,
            sortType: sortType.value
          });
          
          // 保存搜索状态
          scenicStore.saveSearchState(
            { ...searchForm },
            pageConfig.currentPage,
            sortType.value
          );
        }
        
        // 处理搜索结果 - 使用新的规范化响应格式
        if (data && data.results) {
          console.log(`[搜索] 获取到${data.results.length}个结果，总共${data.total || data.results.length}个`);
          searchResult.value = data.results;
          pageConfig.totalCount = data.total || data.results.length;
          
          // 开始预加载图片 (在设置搜索结果后)
          preloadImages(data.results);
          
          // 更新分页信息
          if (data.page) {
            // 转换为数字
            const pageNum = Number(data.page);
            if (!isNaN(pageNum)) {
              pageConfig.currentPage = pageNum;
            }
          }
          
          if (data.page_size) {
            // 转换为数字
            const pageSizeNum = Number(data.page_size);
            if (!isNaN(pageSizeNum)) {
              pageConfig.pageSize = pageSizeNum;
            }
          }
        } else {
          console.error('[搜索] 未识别的结果格式或结果为空:', data);
          searchResult.value = [];
          pageConfig.totalCount = 0;
        }
        
        console.log(`[分页] 更新分页数据: 总数=${pageConfig.totalCount}, 每页=${pageConfig.pageSize}, 总页数=${Math.ceil(pageConfig.totalCount / pageConfig.pageSize)}`);
        
        // 如果搜索结果为空，显示提示
        if (searchResult.value.length === 0) {
          ElMessage.info('没有找到符合条件的景区');
        }
        
        // 搜索完成后强制刷新分页组件以确保高亮正确
        nextTick(() => {
          refreshPaginationComponent();
          console.log('[分页] 搜索完成后刷新分页组件，当前页码:', pageConfig.currentPage);
        });
        
      } catch (error: any) {
        console.error('[搜索] 搜索失败:', error);
        ElMessage.error(`搜索失败: ${error.message || '未知错误'}`);
        searchResult.value = [];
        pageConfig.totalCount = 0;
      } finally {
        loading.value = false;
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
      
      // 重置页码
      console.log('[分页] 重置条件，页码重置为1');
      pageConfig.currentPage = 1
      sortType.value = 'popularity'
      
      // 强制重新创建分页组件
      refreshPaginationComponent();
      
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
        console.log('[分页] 排序变更，页码重置为1');
        pageConfig.currentPage = 1
        
        // 强制重新创建分页组件
        refreshPaginationComponent();
        
        // 保存当前状态
        saveCurrentState()
      }
    }
    
    // 强制重新创建分页组件
    const refreshPaginationComponent = () => {
      console.log(`[分页] 强制重新创建分页组件，当前key=${rerenderPagination.value}, 当前页=${pageConfig.currentPage}`);
      
      // 增加key以强制重新渲染
      rerenderPagination.value += 1;
      
      // 使用nextTick确保DOM更新后再执行
      nextTick(() => {
        console.log(`[分页] 组件应该已重新创建，key=${rerenderPagination.value}, 页码=${pageConfig.currentPage}`);
        
        // 确保数据刷新正确
        if (pageConfig.currentPage > Math.ceil(pageConfig.totalCount / pageConfig.pageSize)) {
          console.warn(`[分页] 页码超出范围，重置为1, 当前页=${pageConfig.currentPage}, 总页数=${Math.ceil(pageConfig.totalCount / pageConfig.pageSize)}`);
          pageConfig.currentPage = 1;
        }
      });
    };

    // 处理分页变更
    const handlePageChange = (page: number) => {
      console.log(`[分页] 页码变更事件: 从 ${pageConfig.currentPage} 到 ${page}`);
      
      // 如果点击的是当前页，不需要处理
      if (page === pageConfig.currentPage) {
        console.log('[分页] 点击了当前页，不需要处理');
        return;
      }
      
      // 更新页码
      pageConfig.currentPage = page;
      
      // 强制重新创建分页组件，确保高亮正确
      refreshPaginationComponent();
      
      console.log(`[分页] 更新后的当前页码: ${pageConfig.currentPage}, 准备发送搜索请求...`);
      
      // 请求新页的数据
      handleSearch();
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
      
      console.log('类型已更改为:', searchForm.type)
      console.log('可用级别选项:', availableLevels.value)
    }
    
    // 添加价格范围变化的处理函数
    const handlePriceRangeChange = (value: [number, number]) => {
      console.log(`[价格筛选] 价格范围变更: ${value[0]}-${value[1]}`);
      // 当用户手动调整价格范围时，我们要确保这个变更被记录
      // 这里不需要额外处理，因为已经在watch中监听searchForm变化
    }
    
    // 修改watch监听，确保深度监听searchForm对象的所有属性
    watch([
      () => JSON.stringify(searchForm), // 使用JSON.stringify确保监听到深层变化 
      () => pageConfig.currentPage, 
      () => sortType.value
    ], () => {
      if (hasInitialized.value) {
        console.log('[状态变化] 检测到搜索参数变化，保存状态:', searchForm);
        saveCurrentState();
      }
    }, { deep: true })
    
    onMounted(() => {
      fetchFilterOptions().then(() => {
        // 检查是否有之前保存的状态需要恢复
        if (scenicStore.savedSearchState.hasSearched) {
          restoreSavedState()
        } else {
          // 确保页码为1
          pageConfig.currentPage = 1;
          console.log('[分页] 初始化页码为1');
          // 执行初始搜索，但不记录
          handleSearch(false, true) // 添加第二个参数表示不记录此次搜索
        }
        
        // 初始化完成后才开始监听状态变化
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
      pageConfig,
      sortType,
      availableLevels,
      handleSearch,
      handleReset,
      handleSort,
      handlePageChange,
      handleProvinceChange,
      handleCityChange,
      handleTypeChange,
      handlePriceRangeChange,
      isWaterScenic,
      levelPlaceholder,
      totalPages,
      rerenderPagination
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
  flex-direction: column;
  align-items: center;
}

.page-info {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
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

/* 添加骨架屏样式 */
.scenic-card-skeleton {
  height: 320px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 20px;
}

.image-skeleton {
  height: 180px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

.content-skeleton {
  padding: 15px;
}

.title-skeleton {
  height: 20px;
  width: 80%;
  margin-bottom: 15px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

.location-skeleton {
  height: 16px;
  width: 60%;
  margin-bottom: 15px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

.info-skeleton {
  display: flex;
  justify-content: space-between;
}

.price-skeleton {
  height: 18px;
  width: 40%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

.type-skeleton {
  height: 18px;
  width: 30%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style> 