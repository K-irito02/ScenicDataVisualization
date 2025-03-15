<template>
  <div class="scenic-detail-container">
    <div v-if="loading" class="loading-wrapper">
      <el-skeleton animated :rows="10" />
    </div>
    
    <template v-else>
      <div class="scenic-header">
        <div class="scenic-title">
          <h1>{{ scenic.name }}</h1>
          <div class="scenic-level" v-if="scenic.level">{{ scenic.level }}</div>
          <el-button 
            :type="isFavorite ? 'warning' : 'default'" 
            :icon="isFavorite ? 'Star' : 'StarFilled'" 
            circle
            @click="toggleFavorite"
            class="favorite-btn"
          />
        </div>
        <div class="scenic-location">
          <el-icon><Location /></el-icon>
          <span>{{ scenic.province }} {{ scenic.city }} {{ scenic.address }}</span>
        </div>
      </div>
      
      <el-row :gutter="20">
        <el-col :span="16">
          <card-container class="scenic-card">
            <el-carousel trigger="click" height="400px" indicator-position="outside">
              <el-carousel-item v-for="(img, index) in scenic.images" :key="index">
                <img :src="img" :alt="scenic.name" class="carousel-image">
              </el-carousel-item>
            </el-carousel>
            
            <div class="scenic-info">
              <el-descriptions :column="3" border>
                <el-descriptions-item label="门票价格">
                  <span class="price">¥{{ scenic.price }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="景区类型">
                  {{ scenic.type }}
                </el-descriptions-item>
                <el-descriptions-item label="推荐游玩时长">
                  {{ scenic.suggestedDuration }}
                </el-descriptions-item>
                <el-descriptions-item label="开放时间" :span="3">
                  {{ scenic.openingHours }}
                </el-descriptions-item>
              </el-descriptions>
              
              <div class="scenic-description">
                <h3>景点简介</h3>
                <p>{{ scenic.description }}</p>
              </div>
            </div>
          </card-container>
          
          <card-container title="评论与情感分析" class="scenic-card">
            <div class="sentiment-overview">
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="sentiment-score">
                    <div class="score-circle">
                      <div class="score-value">{{ scenic.sentimentScore.toFixed(1) }}</div>
                    </div>
                    <div class="score-label">情感评分</div>
                  </div>
                </el-col>
                <el-col :span="16">
                  <div class="sentiment-details">
                    <div class="sentiment-item">
                      <span class="item-label">评论总数:</span>
                      <span class="item-value">{{ scenic.commentCount }}</span>
                    </div>
                    <div class="sentiment-item">
                      <span class="item-label">正面评论占比:</span>
                      <span class="item-value">{{ (scenic.positiveRate * 100).toFixed(1) }}%</span>
                    </div>
                    <div class="sentiment-item">
                      <span class="item-label">情感强度:</span>
                      <span class="item-value">{{ getSentimentIntensity(scenic.sentimentIntensity) }}</span>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
            
            <div class="comment-cloud">
              <h3>热门评论词</h3>
              <div class="cloud-wrapper">
                <base-chart :options="wordCloudOptions" height="300px" />
              </div>
            </div>
            
            <div class="comment-list">
              <h3>最新评论</h3>
              <el-timeline>
                <el-timeline-item
                  v-for="(comment, index) in scenic.comments"
                  :key="index"
                  :type="getCommentType(comment.sentiment)"
                  :timestamp="comment.date"
                >
                  <div class="comment-content">
                    <div class="comment-user">{{ comment.user }}</div>
                    <div class="comment-text">{{ comment.content }}</div>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </card-container>
        </el-col>
        
        <el-col :span="8">
          <card-container title="交通信息" class="scenic-card">
            <div class="traffic-info">
              <div v-for="(info, index) in scenic.trafficInfo" :key="index" class="traffic-item">
                <div class="traffic-type">
                  <el-icon>
                    <component :is="getTrafficIcon(info.type)"></component>
                  </el-icon>
                  <span>{{ info.typeName }}</span>
                </div>
                <div class="traffic-detail">{{ info.description }}</div>
              </div>
            </div>
          </card-container>
          
          <card-container title="周边设施" class="scenic-card">
            <el-row :gutter="10">
              <el-col :span="12" v-for="(facility, index) in scenic.facilities" :key="index">
                <div class="facility-item">
                  <el-icon>
                    <component :is="getFacilityIcon(facility.type)"></component>
                  </el-icon>
                  <span>{{ facility.name }}</span>
                </div>
              </el-col>
            </el-row>
          </card-container>
          
          <card-container title="推荐景点" class="scenic-card">
            <div class="recommended-list">
              <div v-for="(item, index) in scenic.recommendations" :key="index" class="recommended-item" @click="navigateToScenic(item.id)">
                <div class="recommended-image">
                  <img :src="item.image" :alt="item.name">
                </div>
                <div class="recommended-info">
                  <div class="recommended-name">{{ item.name }}</div>
                  <div class="recommended-price">¥{{ item.price }}</div>
                </div>
              </div>
            </div>
          </card-container>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CardContainer from '@/components/common/CardContainer.vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import { useScenicStore } from '@/stores/scenic'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import type { EChartsOption } from 'echarts'
import { 
  Location, 
  Star, 
  StarFilled, 
  Van, 
  Ship, 
  Bicycle,
  Dessert,
  House,
  School,
  ShoppingCart,
  OfficeBuilding
} from '@element-plus/icons-vue'

export default defineComponent({
  name: 'ScenicDetail',
  components: {
    CardContainer,
    BaseChart,
    Location,
    Star,
    StarFilled,
    Van,
    Ship,
    Bicycle,
    Dessert,
    House,
    School,
    ShoppingCart,
    OfficeBuilding
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const scenicStore = useScenicStore()
    const userStore = useUserStore()
    const loading = ref(true)
    const scenic = ref<any>({})
    
    const scenicId = computed(() => route.params.id as string)
    const isFavorite = computed(() => userStore.favorites.some((item: any) => item.id === scenicId.value))
    const isLoggedIn = computed(() => !!userStore.token)
    
    // 获取景区详情
    const fetchScenicDetail = async () => {
      loading.value = true
      
      try {
        // 实际项目中应该从API获取数据
        // 这里使用模拟数据
        await new Promise(resolve => setTimeout(resolve, 800)) // 模拟请求延迟
        
        scenic.value = generateMockScenicDetail(scenicId.value)
      } catch (error) {
        console.error('获取景区详情失败:', error)
        ElMessage.error('获取景区详情失败')
      } finally {
        loading.value = false
      }
    }
    
    // 生成模拟景区数据
    const generateMockScenicDetail = (id: string) => {
      // 生成一个模拟的景区详情数据
      return {
        id,
        name: '故宫博物院',
        province: '北京',
        city: '北京',
        address: '东城区景山前街4号',
        level: '5A',
        type: '历史文化',
        price: 80,
        openingHours: '4月1日-10月31日 8:30-17:00，11月1日-次年3月31日 8:30-16:30，周一闭馆（国家法定节假日除外）',
        suggestedDuration: '3-4小时',
        description: '故宫博物院是中国最大的古代宫殿建筑群，位于北京市中心，是明清两代24位皇帝的皇家宫殿，是中国古代宫廷文化收藏和展示的场所。故宫始建于明朝永乐四年（1406年），是中国现存最完整、规模最大的木质结构古建筑群，占地面积72万平方米，建筑面积约15万平方米，有大小宫殿七十多座，房屋九千余间。故宫于1987年被联合国教科文组织列为"世界文化遗产"。',
        images: [
          '/images/forbidden-city-1.jpg',
          '/images/forbidden-city-2.jpg',
          '/images/forbidden-city-3.jpg',
          '/images/forbidden-city-4.jpg',
        ],
        commentCount: 10862,
        sentimentScore: 4.7,
        sentimentIntensity: 0.82,
        positiveRate: 0.93,
        comments: [
          {
            user: '旅行者12345',
            content: '故宫真的太壮观了，建筑气势恢宏，历史感很强，值得一去。门票价格合理，讲解器很有用，建议租一个。',
            sentiment: 0.9,
            date: '2023-05-15'
          },
          {
            user: '文化爱好者',
            content: '作为中国传统文化的爱好者，故宫是必去的地方。建议早上去，人少一些。文物展示很精彩，但是人真的很多，特别是黄金周期间。',
            sentiment: 0.7,
            date: '2023-04-28'
          },
          {
            user: '历史研究者',
            content: '故宫是了解中国明清历史的窗口，建筑群保存完好，文物丰富。但是游客太多，有些区域拍照很困难，建议避开节假日。',
            sentiment: 0.5,
            date: '2023-04-10'
          },
          {
            user: '摄影爱好者',
            content: '故宫的建筑非常适合摄影，尤其是在阳光明媚的天气。不过人流量大，需要耐心等待拍摄时机。票价合理，整体体验满意。',
            sentiment: 0.8,
            date: '2023-03-22'
          }
        ],
        trafficInfo: [
          {
            type: 'subway',
            typeName: '地铁',
            description: '1号线天安门东站下车，步行约10分钟；1号线天安门西站下车，步行约15分钟。'
          },
          {
            type: 'bus',
            typeName: '公交',
            description: '乘坐1、2、4、10、20、52、59、82、120路到天安门东站下车。'
          },
          {
            type: 'car',
            typeName: '自驾',
            description: '自驾游客可将车辆停放在王府井停车场或天安门地下停车场，步行前往故宫。'
          }
        ],
        facilities: [
          { type: 'toilet', name: '公共厕所' },
          { type: 'rest', name: '休息区' },
          { type: 'store', name: '纪念品商店' },
          { type: 'food', name: '餐饮服务' },
          { type: 'museum', name: '展览馆' },
          { type: 'guide', name: '导游服务' }
        ],
        recommendations: [
          {
            id: 'scenic_2',
            name: '天坛公园',
            image: '/images/temple-of-heaven.jpg',
            price: 30
          },
          {
            id: 'scenic_3',
            name: '颐和园',
            image: '/images/summer-palace.jpg',
            price: 40
          },
          {
            id: 'scenic_4',
            name: '北海公园',
            image: '/images/beihai-park.jpg',
            price: 20
          }
        ]
      }
    }
    
    // 切换收藏状态
    const toggleFavorite = async () => {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录')
        return
      }
      
      try {
        await userStore.toggleFavorite(scenicId.value)
        ElMessage.success(isFavorite.value ? '已取消收藏' : '收藏成功')
      } catch (error) {
        console.error('收藏操作失败:', error)
        ElMessage.error('收藏操作失败，请重试')
      }
    }
    
    // 导航到其他景区
    const navigateToScenic = (id: string) => {
      router.push(`/dashboard/scenic/${id}`)
    }
    
    // 获取评论类型（用于timeline组件的图标颜色）
    const getCommentType = (sentiment: number) => {
      if (sentiment >= 0.7) return 'success'
      if (sentiment >= 0.4) return 'warning'
      return 'info'
    }
    
    // 获取情感强度描述
    const getSentimentIntensity = (intensity: number) => {
      if (intensity >= 0.8) return '非常强烈'
      if (intensity >= 0.6) return '强烈'
      if (intensity >= 0.4) return '中等'
      return '一般'
    }
    
    // 获取交通图标
    const getTrafficIcon = (type: string) => {
      const iconMap: Record<string, string> = {
        'subway': 'OfficeBuilding',
        'bus': 'Van',
        'car': 'Van',
        'ship': 'Ship',
        'bicycle': 'Bicycle'
      }
      return iconMap[type] || 'Location'
    }
    
    // 获取设施图标
    const getFacilityIcon = (type: string) => {
      const iconMap: Record<string, string> = {
        'toilet': 'House',
        'rest': 'House',
        'store': 'ShoppingCart',
        'food': 'Dessert',
        'museum': 'School',
        'guide': 'Location'
      }
      return iconMap[type] || 'Location'
    }
    
    // 词云图配置
    const wordCloudOptions = computed(() => ({
      series: [{
        type: 'wordCloud',
        shape: 'circle',
        left: 'center',
        top: 'center',
        width: '90%',
        height: '90%',
        right: undefined,
        bottom: undefined,
        sizeRange: [12, 50],
        rotationRange: [-45, 45],
        rotationStep: 10,
        gridSize: 8,
        drawOutOfBound: false,
        textStyle: {
          fontFamily: 'sans-serif',
          fontWeight: 'bold',
          color: function() {
            return 'rgb(' + [
              Math.round(Math.random() * 160),
              Math.round(Math.random() * 160),
              Math.round(Math.random() * 160)
            ].join(',') + ')'
          }
        },
        emphasis: {
          focus: 'self',
          textStyle: {
            shadowBlur: 10,
            shadowColor: '#333'
          }
        },
        data: [
          { name: '壮观', value: 300 },
          { name: '历史', value: 280 },
          { name: '文化', value: 250 },
          { name: '建筑', value: 220 },
          { name: '宏伟', value: 200 },
          { name: '皇宫', value: 180 },
          { name: '文物', value: 170 },
          { name: '古代', value: 150 },
          { name: '精美', value: 140 },
          { name: '故事', value: 130 },
          { name: '讲解', value: 120 },
          { name: '门票', value: 110 },
          { name: '拥挤', value: 100 },
          { name: '排队', value: 90 },
          { name: '值得', value: 80 },
          { name: '推荐', value: 70 },
          { name: '摄影', value: 60 },
          { name: '游客', value: 50 },
          { name: '保存', value: 40 },
          { name: '震撼', value: 30 }
        ]
      }]
    }) as EChartsOption)
    
    onMounted(() => {
      fetchScenicDetail()
    })
    
    return {
      loading,
      scenic,
      scenicId,
      isFavorite,
      isLoggedIn,
      wordCloudOptions,
      toggleFavorite,
      navigateToScenic,
      getCommentType,
      getSentimentIntensity,
      getTrafficIcon,
      getFacilityIcon
    }
  }
})
</script>

<style scoped>
.scenic-detail-container {
  padding: 20px;
}

.loading-wrapper {
  padding: 40px;
}

.scenic-header {
  margin-bottom: 20px;
}

.scenic-title {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.scenic-title h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-right: 15px;
}

.scenic-level {
  background-color: #f56c6c;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
  margin-right: 15px;
}

.favorite-btn {
  margin-left: auto;
}

.scenic-location {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #606266;
}

.scenic-location .el-icon {
  margin-right: 5px;
  color: #909399;
}

.scenic-card {
  margin-bottom: 20px;
}

.carousel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.scenic-info {
  margin-top: 20px;
}

.price {
  color: #f56c6c;
  font-weight: bold;
  font-size: 18px;
}

.scenic-description {
  margin-top: 20px;
}

.scenic-description h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.scenic-description p {
  margin: 0;
  line-height: 1.6;
  color: #606266;
  text-align: justify;
}

.sentiment-overview {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.sentiment-score {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #67c23a;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.score-value {
  color: white;
  font-size: 24px;
  font-weight: bold;
}

.score-label {
  font-size: 14px;
  color: #606266;
}

.sentiment-details {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.sentiment-item {
  margin-bottom: 12px;
}

.item-label {
  color: #909399;
  margin-right: 10px;
}

.item-value {
  font-weight: 500;
  color: #303133;
}

.comment-cloud h3,
.comment-list h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.cloud-wrapper {
  height: 300px;
  margin-bottom: 20px;
}

.comment-content {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
}

.comment-user {
  font-weight: 500;
  color: #303133;
  margin-bottom: 5px;
}

.comment-text {
  color: #606266;
  line-height: 1.5;
}

.traffic-info {
  margin-bottom: 20px;
}

.traffic-item {
  margin-bottom: 15px;
}

.traffic-type {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
  font-weight: 500;
  color: #303133;
}

.traffic-type .el-icon {
  margin-right: 5px;
  color: #409eff;
}

.traffic-detail {
  padding-left: 25px;
  color: #606266;
  line-height: 1.5;
}

.facility-item {
  display: flex;
  align-items: center;
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
}

.facility-item .el-icon {
  margin-right: 5px;
  color: #409eff;
}

.recommended-list {
  display: flex;
  flex-direction: column;
}

.recommended-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.recommended-item:last-child {
  border-bottom: none;
}

.recommended-item:hover {
  background-color: #f5f7fa;
}

.recommended-image {
  width: 60px;
  height: 60px;
  margin-right: 10px;
  border-radius: 4px;
  overflow: hidden;
}

.recommended-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recommended-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 5px;
}

.recommended-price {
  color: #f56c6c;
  font-size: 14px;
}
</style> 