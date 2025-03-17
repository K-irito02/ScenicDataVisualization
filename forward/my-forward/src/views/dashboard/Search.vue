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
              <el-form-item label="类型">
                <el-select 
                  v-model="searchForm.type" 
                  placeholder="景区类型" 
                  clearable
                  filterable
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
                  placeholder="景区级别" 
                  clearable
                  filterable
                >
                  <el-option 
                    v-for="item in filterOptions.levels" 
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
        </div>
        
        <div v-else class="result-grid">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="(item, index) in searchResult" :key="index">
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
import { defineComponent, ref, reactive, computed, onMounted } from 'vue'
import CardContainer from '@/components/common/CardContainer.vue'
import ScenicCard from '@/components/common/ScenicCard.vue'
import { useScenicStore } from '@/stores/scenic'
import { ElMessage } from 'element-plus'
import axios from 'axios'

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
    
    // 筛选表单
    const searchForm = reactive({
      keyword: '',
      province: '',
      city: '',
      type: '',
      level: '',
      priceRange: [0, 500]
    })
    
    // 添加城市映射的类型声明
    type CitiesRecord = Record<string, string[]>
    
    // 筛选选项
    const filterOptions = reactive({
      provinces: ['北京', '上海', '广东', '江苏', '浙江', '四川', '陕西', '云南', '湖北', '湖南'],
      cities: {
        '北京': ['北京'],
        '上海': ['上海'],
        '广东': ['广州', '深圳', '珠海', '佛山', '东莞'],
        '江苏': ['南京', '苏州', '无锡', '常州', '扬州'],
        '浙江': ['杭州', '宁波', '温州', '绍兴', '湖州'],
        '四川': ['成都', '乐山', '峨眉山', '绵阳', '宜宾'],
        '陕西': ['西安', '延安', '宝鸡', '汉中', '榆林'],
        '云南': ['昆明', '大理', '丽江', '西双版纳', '香格里拉'],
        '湖北': ['武汉', '宜昌', '襄阳', '荆州', '恩施'],
        '湖南': ['长沙', '张家界', '岳阳', '常德', '湘西']
      },
      types: ['自然风景', '历史文化', '人文景观', '主题公园', '山岳景区', '水域风光', '古镇古村'],
      levels: ['5A', '4A', '3A', '国家级博物馆', '国家级风景名胜区', '国家级地质公园', '世界文化遗产']
    })
    
    // 使用类型断言修复索引访问
    const filteredCities = computed(() => {
      if (!searchForm.province) return []
      return (filterOptions.cities as CitiesRecord)[searchForm.province] || []
    })
    
    // 搜索景区
    const handleSearch = async () => {
      if (!searchForm.keyword.trim() && !searchForm.province && !searchForm.city && !searchForm.type && !searchForm.level && !searchForm.priceRange[0] && !searchForm.priceRange[1]) {
        return;
      }
      
      loading.value = true;
      
      try {
        // 构建筛选参数
        const params: any = {
          keyword: searchForm.keyword.trim() || undefined,
          province: searchForm.province || undefined,
          city: searchForm.city || undefined,
          type: searchForm.type || undefined,
          level: searchForm.level || undefined,
          priceRange: searchForm.priceRange.join(',') || undefined
        };
        
        const response = await axios.get('/api/scenic/search/', { params });
        searchResult.value = response.data;
        totalCount.value = response.data.length;
      } catch (error) {
        console.error('搜索失败:', error);
        ElMessage.error('搜索失败，请重试');
      } finally {
        loading.value = false;
      }
    };
    
    // 获取筛选选项
    const fetchFilterOptions = async () => {
      try {
        const response = await axios.get('/data/filter-options/');
        // 更新filterOptions中的各项数据
        filterOptions.provinces = response.data.provinces || [];
        filterOptions.cities = response.data.cities || {};
        filterOptions.types = response.data.types || [];
        filterOptions.levels = response.data.levels || [];
      } catch (error) {
        console.error('获取筛选选项失败:', error);
      }
    };
    
    // 重置筛选条件
    const handleReset = () => {
      searchForm.keyword = ''
      searchForm.province = ''
      searchForm.city = ''
      searchForm.type = ''
      searchForm.level = ''
      searchForm.priceRange = [0, 500]
      handleSearch()
    }
    
    // 处理排序变更
    const handleSort = () => {
      if (searchResult.value.length > 0) {
        handleSearch()
      }
    }
    
    // 处理分页变更
    const handlePageChange = (page: number) => {
      currentPage.value = page
      handleSearch()
    }
    
    // 处理省份变更
    const handleProvinceChange = () => {
      searchForm.city = ''
    }
    
    onMounted(() => {
      fetchFilterOptions()
      handleSearch()
    })
    
    return {
      loading,
      searchForm,
      filterOptions,
      filteredCities,
      searchResult,
      totalCount,
      currentPage,
      pageSize,
      sortType,
      handleSearch,
      handleReset,
      handleSort,
      handlePageChange,
      handleProvinceChange
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
</style> 