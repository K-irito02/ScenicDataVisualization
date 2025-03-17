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
import axios from 'axios'

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
    const scenic = ref<any>({
      sentimentScore: 0,
      sentimentIntensity: 0,
      commentCount: 0,
      positiveRate: 0,
      comments: [],
      trafficInfo: [],
      facilities: [],
      recommendations: [],
      images: []
    })
    
    const scenicId = computed(() => {
      const id = route.params.id as string
      if (!id || id === 'undefined') {
        // 如果ID为undefined，重定向到搜索页面
        ElMessage.warning('未指定景区ID，请先搜索选择景区')
        router.push('/dashboard/search')
        return ''
      }
      return id
    })
    
    const isFavorite = computed(() => userStore.favorites.some((item: any) => {
      // 检查item是字符串还是对象
      if (typeof item === 'string') {
        return item === scenicId.value
      }
      return item.id === scenicId.value
    }))
    const isLoggedIn = computed(() => !!userStore.token)
    
    // 获取景区详情
    const fetchScenicDetail = async () => {
      if (!scenicId.value) {
        return;
      }
      
      loading.value = true;
      
      try {
        const response = await axios.get(`/scenic/${scenicId.value}/`);
        scenic.value = response.data;
        loading.value = false;
      } catch (error) {
        console.error('获取景区详情失败:', error);
        ElMessage.error('获取景区详情失败');
        loading.value = false;
      }
    };
    
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
      if (!id) {
        ElMessage.warning('景区ID不存在')
        return
      }
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