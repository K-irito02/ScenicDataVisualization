<template>
  <div class="search-container">
    <el-card class="search-card">
      <template #header>
        <div class="card-header">
          <span>景区搜索</span>
        </div>
      </template>
      
      <div class="search-form">
        <el-input
          v-model="searchKeyword"
          placeholder="请输入景区名称或关键词"
          class="search-input"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
        
        <div class="filter-section">
          <el-collapse v-model="activeCollapse">
            <el-collapse-item title="高级筛选" name="filters">
              <div class="filter-form">
                <el-row :gutter="20">
                  <el-col :span="8">
                    <el-form-item label="地理范围">
                      <el-cascader
                        v-model="filters.location"
                        :options="locationOptions"
                        placeholder="选择省/市/县"
                        clearable
                      />
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="8">
                    <el-form-item label="景区级别">
                      <el-select v-model="filters.level" placeholder="选择景区级别" clearable>
                        <el-option label="5A" value="5A" />
                        <el-option label="4A" value="4A" />
                        <el-option label="3A" value="3A" />
                        <el-option label="2A" value="2A" />
                        <el-option label="省级" value="省级" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="8">
                    <el-form-item label="价格区间">
                      <el-slider
                        v-model="filters.priceRange"
                        range
                        :min="0"
                        :max="500"
                        :step="10"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="20">
                  <el-col :span="8">
                    <el-form-item label="特殊身份">
                      <el-select v-model="filters.identity" placeholder="选择景区特殊身份" clearable>
                        <el-option label="国家级自然保护区" value="natureReserveLevel" />
                        <el-option label="国家级森林公园" value="forestParkLevel" />
                        <el-option label="国家级地质公园" value="geologicalParkLevel" />
                        <el-option label="国家级水利风景区" value="waterScenicSpot" />
                        <el-option label="国家级文物保护单位" value="culturalRelicLevel" />
                        <el-option label="国家级湿地公园" value="wetlandLevel" />
                        <el-option label="国家级博物馆" value="museumLevel" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="8">
                    <el-form-item label="交通方式">
                      <el-select v-model="filters.trafficMethods" multiple placeholder="选择交通方式" clearable>
                        <el-option label="公交" value="公交" />
                        <el-option label="地铁" value="地铁" />
                        <el-option label="出租车" value="出租车" />
                        <el-option label="自驾" value="自驾" />
                        <el-option label="旅游大巴" value="旅游大巴" />
                        <el-option label="火车" value="火车" />
                        <el-option label="飞机" value="飞机" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="8" class="filter-buttons">
                    <el-button type="primary" @click="handleSearch">筛选</el-button>
                    <el-button @click="resetFilters">重置</el-button>
                  </el-col>
                </el-row>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
      
      <div class="search-results" v-loading="loading">
        <div v-if="searchResults.length === 0 && !loading" class="empty-result">
          <el-empty description="暂无搜索结果" v-if="hasSearched"></el-empty>
          <div class="search-tips" v-else>
            <p>搜索提示:</p>
            <ul>
              <li>输入景区名称，如"故宫"、"黄山"</li>
              <li>输入关键词，如"避暑"、"古镇"</li>
              <li>使用高级筛选进行精确查找</li>
            </ul>
          </div>
        </div>
        
        <div v-else class="result-list">
          <el-card v-for="item in searchResults" :key="item.id" class="result-item" shadow="hover">
            <div class="result-header">
              <h3 class="result-title">{{ item.name }}</h3>
              <el-tag v-if="item.level" :type="getLevelTagType(item.level)">{{ item.level }}</el-tag>
            </div>
            
            <div class="result-info">
              <p><el-icon><Location /></el-icon> {{ formatLocation(item.location) }}</p>
              <p><el-icon><Ticket /></el-icon> 门票: {{ item.price }}元</p>
              <p><el-icon><Van /></el-icon> 交通: {{ item.trafficMethods.join(', ') }}</p>
            </div>
            
            <div class="result-tags">
              <el-tag v-if="item.museumLevel" size="small" type="info">{{ item.museumLevel }}</el-tag>
              <el-tag v-if="item.geologicalParkLevel" size="small" type="success">{{ item.geologicalParkLevel }}</el-tag>
              <el-tag v-if="item.waterScenicSpot" size="small" type="info">国家级水利风景区</el-tag>
              <el-tag v-if="item.forestParkLevel" size="small" type="success">{{ item.forestParkLevel }}</el-tag>
              <el-tag v-if="item.wetlandLevel" size="small" type="info">{{ item.wetlandLevel }}</el-tag>
              <el-tag v-if="item.culturalRelicLevel" size="small" type="danger">{{ item.culturalRelicLevel }}</el-tag>
              <el-tag v-if="item.natureReserveLevel" size="small" type="success">{{ item.natureReserveLevel }}</el-tag>
            </div>
            
            <div class="result-actions">
              <el-button type="primary" size="small" @click="viewDetail(item)">查看详情</el-button>
              <el-button 
                :type="isFavorite(item.id) ? 'danger' : 'default'" 
                size="small" 
                @click="toggleFavorite(item)"
              >
                <el-icon><Star /></el-icon>
                {{ isFavorite(item.id) ? '取消收藏' : '收藏' }}
              </el-button>
            </div>
          </el-card>
          
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 30, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalResults"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 景区详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="景区详情"
      width="60%"
      destroy-on-close
    >
      <div v-if="selectedScenic" class="scenic-detail">
        <div class="detail-header">
          <h2>{{ selectedScenic.name }}</h2>
          <el-tag v-if="selectedScenic.level" :type="getLevelTagType(selectedScenic.level)">{{ selectedScenic.level }}</el-tag>
        </div>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="位置">{{ formatLocation(selectedScenic.location) }}</el-descriptions-item>
          <el-descriptions-item label="门票价格">{{ selectedScenic.price }}元</el-descriptions-item>
          <el-descriptions-item label="交通方式">{{ selectedScenic.trafficMethods.join(', ') }}</el-descriptions-item>
          <el-descriptions-item label="特殊身份">
            <div class="detail-tags">
              <el-tag v-if="selectedScenic.museumLevel" size="small" type="info">{{ selectedScenic.museumLevel }}</el-tag>
              <el-tag v-if="selectedScenic.geologicalParkLevel" size="small" type="success">{{ selectedScenic.geologicalParkLevel }}</el-tag>
              <el-tag v-if="selectedScenic.waterScenicSpot" size="small" type="info">国家级水利风景区</el-tag>
              <el-tag v-if="selectedScenic.forestParkLevel" size="small" type="success">{{ selectedScenic.forestParkLevel }}</el-tag>
              <el-tag v-if="selectedScenic.wetlandLevel" size="small" type="info">{{ selectedScenic.wetlandLevel }}</el-tag>
              <el-tag v-if="selectedScenic.culturalRelicLevel" size="small" type="danger">{{ selectedScenic.culturalRelicLevel }}</el-tag>
              <el-tag v-if="selectedScenic.natureReserveLevel" size="small" type="success">{{ selectedScenic.natureReserveLevel }}</el-tag>
            </div>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="detail-comments">
          <h3>游客评论</h3>
          <el-timeline>
            <el-timeline-item
              v-for="(comment, index) in selectedScenic.comments"
              :key="index"
              :type="getSentimentType(comment.sentiment)"
              :color="getSentimentColor(comment.sentiment)"
            >
              <p class="comment-content">{{ comment.content }}</p>
              <div class="comment-keywords">
                <el-tag v-for="keyword in comment.keywords" :key="keyword" size="small">{{ keyword }}</el-tag>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { searchScenic, getScenicDetail, favoriteScenicSpot, unfavoriteScenicSpot } from '@/api/scenic'
import { getUserFavorites } from '@/api/user'
import { ElMessage } from 'element-plus'
import { Search, Location, Ticket, Van, Star } from '@element-plus/icons-vue'

// 定义评论类型
interface Comment {
  id: number
  user: string
  avatar: string
  content: string
  score: number
  date: string
  sentiment: 'positive' | 'neutral' | 'negative'
  keywords: string[]
}

// 扩展ScenicSpot类型
interface ScenicSpot {
  id: number
  name: string
  level: string
  price: number
  location: {
    province: string
    city: string
    address: string
    latitude: number
    longitude: number
  }
  description: string
  trafficMethods: string[]
  comments?: Comment[]
  museumLevel?: string
  geologicalParkLevel?: string
  waterScenicSpot?: string
  forestParkLevel?: string
  wetlandLevel?: string
  culturalRelicLevel?: string
  natureReserveLevel?: string
}

// 搜索关键词
const searchKeyword = ref('')

// 筛选条件
const filters = reactive({
  location: [],
  level: '',
  priceRange: [0, 500],
  identity: '',
  trafficMethods: []
})

// 搜索结果
const searchResults = ref<ScenicSpot[]>([])
const loading = ref(false)
const hasSearched = ref(false)
const totalResults = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const activeCollapse = ref([''])

// 收藏列表
const favorites = ref<(string | number)[]>([])

// 详情对话框
const detailDialogVisible = ref(false)
const selectedScenic = ref<ScenicSpot | null>(null)

// 模拟地理位置数据
const locationOptions = [
  {
    value: '北京',
    label: '北京',
    children: [
      {
        value: '北京市',
        label: '北京市',
        children: [
          { value: '东城区', label: '东城区' },
          { value: '西城区', label: '西城区' },
          { value: '朝阳区', label: '朝阳区' },
          { value: '海淀区', label: '海淀区' }
        ]
      }
    ]
  },
  {
    value: '江苏',
    label: '江苏',
    children: [
      {
        value: '南京市',
        label: '南京市',
        children: [
          { value: '玄武区', label: '玄武区' },
          { value: '秦淮区', label: '秦淮区' },
          { value: '建邺区', label: '建邺区' }
        ]
      },
      {
        value: '苏州市',
        label: '苏州市',
        children: [
          { value: '姑苏区', label: '姑苏区' },
          { value: '吴中区', label: '吴中区' },
          { value: '相城区', label: '相城区' }
        ]
      }
    ]
  }
]

// 初始化
onMounted(async () => {
  await loadFavorites()
})

// 加载收藏列表
const loadFavorites = async () => {
  try {
    const { data } = await getUserFavorites()
    favorites.value = data.map((item: any) => item.scenicId)
  } catch (error) {
    console.error('加载收藏列表失败:', error)
  }
}

// 判断是否已收藏
const isFavorite = (id: string | number) => {
  return favorites.value.includes(id)
}

// 切换收藏状态
const toggleFavorite = async (scenic: ScenicSpot) => {
  try {
    if (isFavorite(scenic.id)) {
      await unfavoriteScenicSpot(scenic.id)
      favorites.value = favorites.value.filter(id => id !== scenic.id)
      ElMessage.success('已取消收藏')
    } else {
      await favoriteScenicSpot(scenic.id)
      favorites.value.push(scenic.id)
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    ElMessage.error('操作失败，请重试')
    console.error('收藏操作失败:', error)
  }
}

// 搜索处理
const handleSearch = async () => {
  loading.value = true
  hasSearched.value = true
  currentPage.value = 1
  
  try {
    // 构建筛选参数
    const filterParams: Record<string, any> = {}
    
    if (filters.location.length > 0) {
      filterParams.province = filters.location[0]
      if (filters.location.length > 1) {
        filterParams.city = filters.location[1]
      }
      if (filters.location.length > 2) {
        filterParams.district = filters.location[2]
      }
    }
    
    if (filters.level) {
      filterParams.level = filters.level
    }
    
    if (filters.priceRange[0] > 0 || filters.priceRange[1] < 500) {
      filterParams.minPrice = filters.priceRange[0]
      filterParams.maxPrice = filters.priceRange[1]
    }
    
    if (filters.identity) {
      filterParams.identity = filters.identity
    }
    
    if (filters.trafficMethods.length > 0) {
      filterParams.trafficMethods = filters.trafficMethods
    }
    
    // 添加分页参数
    filterParams.page = currentPage.value
    filterParams.pageSize = pageSize.value
    
    const res = await searchScenic({
      keyword: searchKeyword.value,
      ...filterParams
    })
    
    // 模拟总数据量
    totalResults.value = 100
    
    // 使用返回的数据
    searchResults.value = res as unknown as ScenicSpot[]
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请重试')
    
    // 使用模拟数据
    searchResults.value = [
      {
        id: 1,
        name: '故宫博物院',
        description: '故宫博物院，中国明清两代的皇家宫殿，世界上现存规模最大、保存最完整的木质结构古建筑群。',
        location: {
          province: '北京',
          city: '北京市',
          address: '东城区景山前街4号',
          latitude: 39.916345,
          longitude: 116.397155
        },
        level: '5A',
        price: 60,
        trafficMethods: ['地铁', '公交', '出租车'],
        museumLevel: '国家级博物馆',
        culturalRelicLevel: '国家级文物保护单位',
        comments: [
          {
            id: 1,
            user: '游客1',
            avatar: '/avatar1.png',
            content: '故宫真的很壮观，历史感很强，值得一去！',
            score: 5,
            date: '2024-03-20',
            sentiment: 'positive',
            keywords: ['壮观', '历史感', '值得']
          },
          {
            id: 2,
            user: '游客2',
            avatar: '/avatar2.png',
            content: '人太多了，建议避开节假日前往。',
            score: 3,
            date: '2024-03-19',
            sentiment: 'neutral',
            keywords: ['人多', '节假日']
          }
        ]
      },
      {
        id: 2,
        name: '黄山风景区',
        description: '黄山，中国著名风景区之一，世界文化和自然遗产，国家5A级旅游景区。',
        location: {
          province: '安徽',
          city: '黄山市',
          address: '黄山区汤口镇',
          latitude: 30.131904,
          longitude: 118.175464
        },
        level: '5A',
        price: 230,
        trafficMethods: ['火车', '汽车', '自驾'],
        geologicalParkLevel: '世界级',
        forestParkLevel: '国家级',
        natureReserveLevel: '国家级',
        comments: [
          {
            id: 3,
            user: '游客3',
            avatar: '/avatar3.png',
            content: '黄山的风景太美了，云海、奇松、怪石，美不胜收！',
            score: 5,
            date: '2024-03-18',
            sentiment: 'positive',
            keywords: ['风景', '云海', '奇松', '怪石']
          },
          {
            id: 4,
            user: '游客4',
            avatar: '/avatar4.png',
            content: '爬山很累，但是风景确实值得。',
            score: 4,
            date: '2024-03-17',
            sentiment: 'positive',
            keywords: ['爬山', '累', '风景', '值得']
          }
        ]
      }
    ]
  } finally {
    loading.value = false
  }
}

// 重置筛选条件
const resetFilters = () => {
  filters.location = []
  filters.level = ''
  filters.priceRange = [0, 500]
  filters.identity = ''
  filters.trafficMethods = []
}

// 查看详情
const viewDetail = async (scenic: ScenicSpot) => {
  try {
    const detail = await getScenicDetail(scenic.id)
    selectedScenic.value = detail as unknown as ScenicSpot
  } catch (error) {
    console.error('获取景区详情失败:', error)
    // 使用当前数据
    selectedScenic.value = scenic
  }
  
  detailDialogVisible.value = true
}

// 格式化地理位置
const formatLocation = (location: { province: string, city: string, address: string }) => {
  return `${location.province} ${location.city} ${location.address}`
}

// 获取景区级别对应的标签类型
const getLevelTagType = (level: string) => {
  const typeMap: Record<string, string> = {
    '5A': 'danger',
    '4A': 'warning',
    '3A': 'success',
    '2A': 'info',
    '省级': ''
  }
  
  return typeMap[level] || ''
}

// 获取评论情感对应的类型
const getSentimentType = (sentiment: string) => {
  const typeMap: Record<string, string> = {
    'positive': 'success',
    'neutral': 'info',
    'negative': 'danger'
  }
  
  return typeMap[sentiment] || 'info'
}

// 获取评论情感对应的颜色
const getSentimentColor = (sentiment: string) => {
  const colorMap: Record<string, string> = {
    'positive': '#67C23A',
    'neutral': '#909399',
    'negative': '#F56C6C'
  }
  
  return colorMap[sentiment] || '#909399'
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  handleSearch()
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  handleSearch()
}
</script>

<style scoped>
.search-container {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  margin-bottom: 20px;
}

.search-input {
  margin-bottom: 15px;
}

.filter-section {
  margin-top: 15px;
}

.filter-form {
  padding: 15px 0;
}

.filter-buttons {
  display: flex;
  justify-content: flex-end;
  align-items: flex-end;
}

.empty-result {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.search-tips {
  text-align: center;
  color: #606266;
}

.search-tips ul {
  text-align: left;
  display: inline-block;
}

.result-list {
  margin-top: 20px;
}

.result-item {
  margin-bottom: 15px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.result-title {
  margin: 0;
  font-size: 18px;
}

.result-info {
  margin-bottom: 10px;
}

.result-info p {
  margin: 5px 0;
  display: flex;
  align-items: center;
}

.result-info .el-icon {
  margin-right: 5px;
}

.result-tags {
  margin-bottom: 15px;
}

.result-tags .el-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.result-actions {
  display: flex;
  justify-content: flex-end;
}

.result-actions .el-button {
  margin-left: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.scenic-detail {
  padding: 10px;
}

.detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.detail-header h2 {
  margin: 0;
  margin-right: 10px;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.detail-comments {
  margin-top: 20px;
}

.comment-content {
  margin-bottom: 5px;
}

.comment-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
</style> 