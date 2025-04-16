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
            size="small"
            @click="toggleFavorite"
            class="favorite-btn"
          />
        </div>
        <div class="scenic-location">
          <el-icon><Location /></el-icon>
          <span>{{ scenic.address }}</span>
        </div>
        <div class="back-button">
          <el-button type="primary" size="small" @click="goBackToSearch" style="margin-right: 10px;">
            <el-icon><Back /></el-icon>
            返回筛选页面
          </el-button>
          <el-button type="success" size="small" @click="goBackToFavorites">
            <el-icon><Back /></el-icon>
            返回我的收藏
          </el-button>
        </div>
      </div>
      
      <el-row>
        <el-col :span="24">
          <card-container class="scenic-card">
            <el-carousel trigger="click" height="400px" indicator-position="outside">
              <el-carousel-item v-for="(img, index) in scenic.images" :key="index">
                <img :src="img" :alt="scenic.name" class="carousel-image">
              </el-carousel-item>
            </el-carousel>
            
            <div class="scenic-info">
              <el-descriptions :column="3" border>
                <el-descriptions-item label="门票价格">
                  <span class="price">{{ scenic.price ? `¥${scenic.price}` : '暂无数据' }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="景区类型">
                  {{ scenic.type || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="推荐游玩时长">
                  {{ scenic.suggestedDuration || '暂无数据' }}
                </el-descriptions-item>
                <el-descriptions-item label="开放时间" :span="3">
                  {{ scenic.openingHours || '暂无数据' }}
                </el-descriptions-item>
              </el-descriptions>
              
              <div class="scenic-description">
                <h3>景点简介</h3>
                <p>{{ scenic.description || '暂无数据' }}</p>
              </div>
              
              <!-- 交通信息部分 -->
              <div class="traffic-section">
                <h3>交通信息</h3>
                <div class="traffic-info">
                  <div v-if="trafficContent" class="traffic-item">
                    <div class="traffic-detail">
                      <pre>{{ trafficContent }}</pre>
                    </div>
                  </div>
                  <div v-else class="no-data-tip">
                    暂无交通信息
                  </div>
                </div>
              </div>
              
              <!-- 推荐景点部分 -->
              <div class="recommendation-section">
                <h3>推荐景点</h3>
                <div class="recommended-list">
                  <div v-if="scenic.recommendations && scenic.recommendations.length > 0">
                    <el-row :gutter="20">
                      <el-col :xs="24" :sm="12" :md="8" v-for="(item, index) in scenic.recommendations" :key="index">
                        <div class="recommended-item" @click="navigateToScenic(item.id)">
                          <div class="recommended-image">
                            <img :src="item.image" :alt="item.name">
                          </div>
                          <div class="recommended-info">
                            <div class="recommended-name">{{ item.name }}</div>
                            <div class="recommended-price">¥{{ item.price }}</div>
                          </div>
                        </div>
                      </el-col>
                    </el-row>
                  </div>
                  <div v-else class="no-data-tip">
                    暂无数据
                  </div>
                </div>
              </div>
            </div>
          </card-container>
          
          <card-container title="评论与情感分析" class="scenic-card">
            <div class="sentiment-overview">
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="sentiment-score">
                    <div class="score-circle">
                      <div class="score-value">{{ scenic.sentimentScore ? scenic.sentimentScore.toFixed(1) : '0.0' }}</div>
                    </div>
                    <div class="score-label">情感评分</div>
                  </div>
                </el-col>
                <el-col :span="16">
                  <div class="sentiment-details">
                    <div class="sentiment-item">
                      <span class="item-label">评论总数:</span>
                      <span class="item-value">{{ scenic.commentCount || '0' }}</span>
                    </div>
                    <div class="sentiment-item">
                      <span class="item-label">正面评论占比:</span>
                      <span class="item-value">{{ scenic.positiveRate ? (scenic.positiveRate * 100).toFixed(1) + '%' : '暂无数据' }}</span>
                    </div>
                    <div class="sentiment-item">
                      <span class="item-label">情感强度:</span>
                      <span class="item-value">{{ scenic.sentimentIntensity ? getSentimentIntensity(scenic.sentimentIntensity) : '暂无数据' }}</span>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
            
            <div class="comment-cloud">
              <h3>热门评论词</h3>
              <div v-if="wordCloudLoading" class="loading-tip">
                <el-skeleton animated :rows="3" />
              </div>
              <div class="cloud-wrapper" v-else-if="hasWordCloudData">
                <base-chart :options="wordCloudOptions" height="300px" />
              </div>
              <div v-else class="no-data-tip">
                暂无数据
              </div>
            </div>
            
            <div class="comment-list">
              <h3>最新评论</h3>
              <el-timeline v-if="scenic.comments && scenic.comments.length > 0">
                <el-timeline-item
                  v-for="(comment, index) in paginatedComments"
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
              <div v-else class="no-data-tip">
                暂无数据
              </div>
              
              <!-- 评论分页控制 -->
              <div class="pagination-container" v-if="scenic.comments && scenic.comments.length > pageSize">
                <el-pagination
                  v-model:current-page="currentPage"
                  v-model:page-size="pageSize"
                  :page-sizes="[5, 10, 15, 20]"
                  layout="total, sizes, prev, pager, next, jumper"
                  :total="scenic.comments.length"
                  @size-change="handleSizeChange"
                  @current-change="handleCurrentChange"
                />
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
import * as echarts from 'echarts'
import 'echarts-wordcloud'
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
  OfficeBuilding,
  Back
} from '@element-plus/icons-vue'
import { getScenicDetail, getWordCloud } from '@/api/scenic'

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
    OfficeBuilding,
    Back
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const scenicStore = useScenicStore()
    const userStore = useUserStore()
    const loading = ref(true)
    const wordCloudLoading = ref(false)
    const wordCloudData = ref<any[]>([])
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
    
    // 分页相关
    const currentPage = ref(1)
    const pageSize = ref(5)
    
    // 返回搜索筛选页面
    const goBackToSearch = () => {
      // 使用路由器导航到搜索页面，但我们确保不会导致状态丢失
      // 不再使用router.go(-1)，因为它在某些情况下不可靠
      router.push('/dashboard/search')
    }
    
    // 计算属性：交通信息内容
    const trafficContent = computed(() => {
      if (!scenic.value) {
        return '';
      }
      
      console.log('处理交通信息:', {
        transportation: scenic.value.transportation,
        traffic_info: scenic.value.traffic_info,
        trafficInfo: scenic.value.trafficInfo
      });
      
      // 检查顺序：trafficInfo数组 > transportation > traffic_info
      
      // 首先检查trafficInfo数组（因为这是序列化器特别处理过的数据）
      if (scenic.value.trafficInfo && Array.isArray(scenic.value.trafficInfo) && scenic.value.trafficInfo.length > 0) {
        const descriptions = scenic.value.trafficInfo
          .filter((item: any) => item && item.description && typeof item.description === 'string' && item.description.trim() !== '')
          .map((item: any) => item.description);
        
        if (descriptions.length > 0) {
          return descriptions.join('\n\n');
        }
      }
      
      // 然后检查transportation字段
      if (scenic.value.transportation && typeof scenic.value.transportation === 'string' && scenic.value.transportation.trim() !== '') {
        return scenic.value.transportation;
      }
      
      // 最后检查traffic_info字段
      if (scenic.value.traffic_info && typeof scenic.value.traffic_info === 'string' && scenic.value.traffic_info.trim() !== '') {
        return scenic.value.traffic_info;
      }
      
      return '';
    });
    
    // 获取景区详情
    const fetchScenicDetail = async () => {
      if (!scenicId.value) {
        return;
      }
      
      loading.value = true;
      
      try {
        // 确保使用正确的ID进行请求
        let requestId = scenicId.value;
        if (typeof requestId === 'string' && requestId.startsWith('S') && !isNaN(parseInt(requestId.substring(1)))) {
          // 获取S后面的数字部分作为ID
          requestId = requestId.substring(1);
          console.log('调整请求ID:', requestId);
        }
        
        // 验证ID是否为有效ID
        if (!requestId || requestId === '0') {
          throw new Error('无效的景区ID');
        }
        
        console.log('准备请求景区详情，ID:', requestId);
        const response = await getScenicDetail(requestId);
        
        if (!response || !response.data) {
          throw new Error('接收到空响应');
        }
        
        // 处理后端返回的数据以匹配前端需要的格式
        const data = response.data;
        
        // 提取交通相关信息并打印详细的日志
        console.log('景区交通数据详情:', {
          id: requestId,
          transportation: data.transportation,
          transportation_type: typeof data.transportation,
          transportation_empty: data.transportation === null || data.transportation === undefined || data.transportation === '',
          traffic_info: data.traffic_info,
          traffic_info_type: typeof data.traffic_info,
          traffic_info_empty: data.traffic_info === null || data.traffic_info === undefined || data.traffic_info === '',
          trafficInfo: data.trafficInfo,
        });
        
        scenic.value = {
          // 基本信息
          scenic_id: data.scenic_id,
          name: data.name,
          description: data.description || '暂无简介',
          province: data.province || '',
          city: data.city || '',
          district: data.district || '',
          address: [data.province, data.city, data.district, data.street].filter(Boolean).join(' '),
          
          // 价格信息
          price: data.min_price || '免费',
          
          // 类型和等级
          type: data.type || '未分类',
          level: data.level || '无等级',
          
          // 开放时间
          openingHours: data.opening_hours || '暂无开放时间信息',
          
          // 不再使用模拟数据
          suggestedDuration: '建议游玩时间暂无',
          
          // 图片
          image: data.image_url || '/images/default-scenic.jpg',
          images: data.image_url ? [data.image_url] : ['/images/default-scenic.jpg'],
          
          // 评论相关
          comments: data.comments || [],
          commentCount: data.comment_count || 0,
          sentimentScore: data.sentiment_score || 0,
          sentimentIntensity: data.sentiment_magnitude || 0,
          positiveRate: data.sentiment_score ? (data.sentiment_score > 0 ? data.sentiment_score/300 : 0) : 0,
          
          // 交通信息 - 保存所有可能的交通数据字段
          transportation: data.transportation || '',
          traffic_info: data.traffic_info || '',
          trafficInfo: Array.isArray(data.trafficInfo) ? data.trafficInfo : 
                      (data.trafficInfo ? [{ description: data.trafficInfo }] : []),

          // 设施和推荐景点不再使用模拟数据
          recommendations: []
        };
        
        // 获取词云数据
        fetchWordCloudData(data.scenic_id);
        
        // 打印处理后的交通数据
        console.log('前端处理后的交通数据:', {
          transportation: scenic.value.transportation,
          traffic_info: scenic.value.traffic_info,
          trafficInfo: scenic.value.trafficInfo,
          trafficContent: trafficContent.value
        });
        
        loading.value = false;
      } catch (error: any) {
        console.error('获取景区详情失败:', error)
        
        // 提供更详细的错误信息
        let errorMessage = '获取景区详情失败'
        
        if (error.response) {
          // 服务器响应了，但状态码不在 2xx 范围内
          console.error('服务器响应错误:', {
            status: error.response.status,
            data: error.response.data
          })
          
          if (error.response.status === 404) {
            errorMessage = '景区不存在，请检查ID是否正确'
          } else if (error.response.status === 500) {
            errorMessage = '服务器内部错误，请联系管理员'
          }
        } else if (error.request) {
          // 请求已发送，但没有收到响应
          console.error('未收到服务器响应')
          errorMessage = '无法连接到服务器，请检查网络连接'
        } else {
          // 设置请求时发生了错误
          console.error('请求错误:', error.message)
          errorMessage = `请求错误: ${error.message}`
        }
        
        ElMessage.error(errorMessage)
        loading.value = false
        
        // 如果是404错误，可以重定向回搜索页面
        if (error.response && error.response.status === 404) {
          setTimeout(() => {
            router.push('/dashboard/search')
          }, 2000)
        }
      }
    }
    
    // 获取词云数据
    const fetchWordCloudData = async (scenicId: string) => {
      if (!scenicId) return;
      
      wordCloudLoading.value = true;
      try {
        const response = await getWordCloud(scenicId);
        wordCloudData.value = response.data;
        console.log('词云数据:', wordCloudData.value);
      } catch (error) {
        console.error('获取词云数据失败:', error);
        wordCloudData.value = [];
      } finally {
        wordCloudLoading.value = false;
      }
    };
    
    // 分页方法
    const handleSizeChange = (size: number) => {
      pageSize.value = size;
      currentPage.value = 1; // 重置到第一页
    };
    
    const handleCurrentChange = (page: number) => {
      currentPage.value = page;
    };
    
    // 计算分页后的评论数据
    const paginatedComments = computed(() => {
      if (!scenic.value?.comments) return [];
      
      const startIndex = (currentPage.value - 1) * pageSize.value;
      const endIndex = startIndex + pageSize.value;
      return scenic.value.comments.slice(startIndex, endIndex);
    });
    
    // 词云图配置
    const wordCloudOptions = computed(() => ({
      tooltip: {
        show: true,
        formatter: function(params: any) {
          return params.name + ': ' + params.value;
        }
      },
      series: [{
        type: 'wordCloud',
        shape: 'circle',
        left: 'center',
        top: 'center',
        width: '90%',
        height: '90%',
        right: null,
        bottom: null,
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
          textStyle: {
            shadowBlur: 10,
            shadowColor: '#333'
          }
        },
        data: wordCloudData.value
      }]
    }) as EChartsOption)
    
    // 计算是否有词云数据
    const hasWordCloudData = computed(() => {
      return wordCloudData.value && wordCloudData.value.length > 0;
    });
    
    // 切换收藏状态
    const toggleFavorite = async () => {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录')
        return
      }
      
      try {
        await userStore.toggleFavorite(scenicId.value)
        ElMessage.success(isFavorite.value ? '收藏成功' : '已取消收藏')
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
    
    // 返回我的收藏页面
    const goBackToFavorites = () => {
      router.push({ 
        path: '/dashboard/profile',
        query: { tab: 'favorites' }
      })
    }
    
    onMounted(() => {
      fetchScenicDetail();
    })
    
    return {
      loading,
      wordCloudLoading,
      scenic,
      scenicId,
      isFavorite,
      isLoggedIn,
      wordCloudOptions,
      hasWordCloudData,
      currentPage,
      pageSize,
      paginatedComments,
      handleSizeChange,
      handleCurrentChange,
      toggleFavorite,
      navigateToScenic,
      getCommentType,
      getSentimentIntensity,
      getTrafficIcon,
      getFacilityIcon,
      goBackToSearch,
      goBackToFavorites,
      trafficContent
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
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.scenic-title {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  flex: 2;
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
  margin-left: 15px;
}

.scenic-location {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #606266;
  flex: 3;
  margin-bottom: 10px;
  padding-left: 10px;
}

.scenic-location .el-icon {
  margin-right: 8px;
  color: #409EFF;
  font-size: 16px;
}

.back-button {
  margin-left: auto;
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

.scenic-description,
.traffic-section,
.recommendation-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.scenic-description h3,
.traffic-section h3,
.recommendation-section h3 {
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

.traffic-info {
  margin-bottom: 20px;
}

.traffic-item {
  margin-bottom: 15px;
}

.traffic-detail {
  color: #606266;
  line-height: 1.5;
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

.recommended-list {
  display: flex;
  flex-direction: column;
  margin-top: 10px;
}

.recommended-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
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

.no-data-tip {
  text-align: center;
  color: #909399;
  padding: 10px;
  border: 1px dashed #f0f0f0;
  border-radius: 4px;
}

.comment-list {
  margin-top: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.loading-tip {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}
</style> 