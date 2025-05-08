<template>
  <div class="scenic-detail-container">
    <div v-if="loading" class="loading-container">
      <el-skeleton style="width: 100%" animated>
        <template #template>
          <el-skeleton-item variant="image" style="width: 100%; height: 400px" />
          <div style="padding: 20px;">
            <el-skeleton-item variant="h3" style="width: 50%" />
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px">
              <el-skeleton-item variant="text" style="width: 30%" />
              <el-skeleton-item variant="text" style="width: 30%" />
            </div>
            <el-skeleton-item variant="text" style="width: 100%; margin-top: 20px" />
            <el-skeleton-item variant="text" style="width: 100%; margin-top: 10px" />
            <el-skeleton-item variant="text" style="width: 100%; margin-top: 10px" />
          </div>
        </template>
      </el-skeleton>
    </div>
    
    <div v-else class="scenic-detail-content">
      <div class="header-actions">
        <div class="left-buttons">
          <el-button type="primary" size="large" @click="handleBackToSearch">
            <el-icon><Back /></el-icon>
            <span>返回搜索</span>
          </el-button>
          <el-button type="primary" size="large" @click="handleBackToFavorites">
            <el-icon><Back /></el-icon>
            <span>返回我的收藏</span>
          </el-button>
          <el-button 
            v-if="fromTransportation" 
            type="primary" 
            size="large" 
            @click="handleBackToTransportation"
          >
            <el-icon><Back /></el-icon>
            <span>{{ transportationBackButtonText }}</span>
          </el-button>
        </div>
        
        <div class="right-buttons">
          <el-button 
            type="primary"
            size="large"
            :icon="isFavorite ? 'StarFilled' : 'Star'" 
            @click="toggleFavorite"
            :class="{ 'is-favorite': isFavorite }"
          >
            {{ isFavorite ? '已收藏' : '收藏' }}
          </el-button>
        </div>
      </div>
      
      <h2 class="scenic-title">
        {{ scenic.name }}
      </h2>
      
      <el-row>
        <el-col :span="24">
          <card-container class="scenic-card">
            <el-carousel trigger="click" height="400px" indicator-position="outside">
              <el-carousel-item v-for="(img, index) in processedScenicImages" :key="index">
                <img :src="img" :alt="scenic.name" class="carousel-image" @error="handleCarouselImageError($event, index)">
              </el-carousel-item>
            </el-carousel>
            
            <div class="scenic-info">
              <el-descriptions :column="3" border>
                <el-descriptions-item label="门票价格">
                  <span class="price">{{ scenic.price ? `¥${scenic.price}` : '暂无数据' }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="景区类型">
                  <el-tag effect="plain" type="danger">{{ scenic.type ? (scenic.type.includes('景区') ? scenic.type.replace(/景区/g, 'A级景区') : scenic.type) : '暂无数据' }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="位置信息">
                  {{ formatAddress(scenic) || '暂无数据' }}
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
                      <pre class="traffic-content">{{ trafficContent }}</pre>
                    </div>
                  </div>
                  <div v-else class="no-data-tip">
                    暂无交通信息
                  </div>
                </div>
              </div>
              
              <!-- 推荐景点部分 -->
              <div class="recommendation-section">
                <h3>附近景区</h3>
                <div class="recommended-list">
                  <div v-if="nearbyScenics.length > 0">
                    <el-row :gutter="20">
                      <el-col :xs="24" :sm="12" :md="8" v-for="(item, index) in nearbyScenics" :key="index">
                        <div class="recommended-item" @click="navigateToScenic(item.id)">
                          <div class="recommended-image">
                            <img 
                              :src="handleImageUrl(item.image)" 
                              :alt="item.name" 
                              @error="handleNearbyImageError($event)"
                            >
                          </div>
                          <div class="recommended-info">
                            <div class="recommended-name">{{ item.name }}</div>
                            <div class="recommended-meta">
                              <span class="recommended-price">¥{{ item.price }}</span>
                              <span class="recommended-distance">{{ formatDistance(item.distance) }}</span>
                            </div>
                          </div>
                        </div>
                      </el-col>
                    </el-row>
                  </div>
                  <div v-else-if="nearbyLoading" class="loading-tip">
                    <el-skeleton animated :rows="3" />
                  </div>
                  <div v-else class="no-data-tip">
                    暂无景区
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
                    <div class="score-label">情感得分</div>
                  </div>
                </el-col>
                <el-col :span="16">
                  <div class="sentiment-details">
                    <div class="sentiment-item">
                      <span class="item-label">评论总数:</span>
                      <span class="item-value">{{ scenic.commentCount || '0' }}</span>
                    </div>
                    <div class="sentiment-item">
                      <span class="item-label">情感倾向:</span>
                      <span class="item-value">{{ scenic.sentiment || '暂无数据' }}</span>
                    </div>
                    <div class="sentiment-item">
                      <span class="item-label">情感强度:</span>
                      <span class="item-value">{{ scenic.sentimentMagnitude ? scenic.sentimentMagnitude.toFixed(2) : '暂无数据' }}</span>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
            
            <div class="sentiment-calculation">
              <h3>情感分析计算方法</h3>
              <div class="calculation-item">
                <div class="calculation-title">情感得分</div>
                <div class="calculation-desc">
                  情感得分<strong>（考虑情感词正负）</strong>通过遍历评论中的每个词语，如果该词在情感词典中存在，则获取其情感值。计算过程中同时考虑了程度词（如"非常"、"很"等）的增强作用，以及否定词（如"不"、"没有"等）对情感极性的反转作用。最终将所有词语的情感值累加，得到总的情感得分。
                </div>
              </div>
              
              <div class="calculation-item">
                <div class="calculation-title">情感强度</div>
                <div class="calculation-desc">
                  情感强度<strong>（不考虑情感词正负）</strong>反映情感表达的强弱程度。计算时，系统累加每个<strong>情感词得分的绝对值</strong>，然后除以分词后的总词数，得到平均情感强度。无论是积极情感还是消极情感，强度越高表示情感表达越强烈。
                </div>
              </div>
              
              <div class="calculation-item">
                <div class="calculation-title">情感倾向</div>
                <div class="calculation-desc">
                  情感倾向将评价分为"优"、"中"、"良"三类，基于平均情感得分确定：
                  <ul>
                    <li>平均情感得分 > 0.09，判定为"优"</li>
                    <li>平均情感得分 < 0.03，判定为"良"</li>
                    <li>介于两者之间，判定为"中"</li>
                  </ul>
                  平均情感得分 = 情感得分 / 分词数
                </div>
              </div>
            </div>
            
            <div class="comment-cloud">
              <h3>热门评论词</h3>
              <div v-if="wordCloudLoading" class="loading-tip">
                <el-skeleton animated :rows="3" />
              </div>
              <div class="cloud-wrapper" v-else-if="hasWordCloudData" ref="wordCloudContainer">
                <base-chart 
                  :options="wordCloudOptions" 
                  height="300px" 
                  :key="'wc-' + scenicId + '-' + wordCloudRefreshKey"
                  @rendered="onWordCloudRendered" 
                />
              </div>
              <div v-else class="no-data-tip">
                暂无数据
              </div>
            </div>
            
            <div class="comment-list">
              <h3>评论数据</h3>
              <el-timeline v-if="scenic.comments && scenic.comments.length > 0">
                <el-timeline-item
                  v-for="(comment, index) in paginatedComments"
                  :key="index"
                  :type="getCommentType(scenic.sentiment || '').type"
                  :timestamp="comment.date"
                >
                  <div class="comment-content">
                    <div class="comment-user">{{ comment.user || '游客' }}</div>
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
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed, nextTick, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CardContainer from '@/components/common/CardContainer.vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import type { EChartsOption } from 'echarts'
import { processImageUrl, DEFAULT_IMAGE } from '@/api/image-proxy'
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
import { getScenicDetail, getWordCloud, getNearbyScenics } from '@/api/scenic'

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
    const userStore = useUserStore()
    const loading = ref(true)
    const wordCloudLoading = ref(false)
    const wordCloudData = ref<any[]>([])
    const defaultImage = DEFAULT_IMAGE
    const imageErrors = ref<Record<number, boolean>>({})
    
    const scenic = ref<any>({
      sentimentScore: 0,
      sentimentMagnitude: 0,
      sentiment: '',
      commentCount: 0,
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
    
    // 判断用户来源是否为收藏页面
    const fromFavorites = computed(() => {
      // 从route.query中获取来源信息
      return route.query.from === 'favorites'
    })
    
    // 判断用户来源是否为交通分析页面
    const fromTransportation = computed(() => {
      // 从route.query中获取来源信息
      return route.query.from === 'transportation'
    })
    
    // 添加计算属性：返回按钮文本
    const transportationBackButtonText = computed(() => {
      const province = route.query.province as string
      return province && province !== '全国' ? `返回${province}力导向图` : '返回交通方式分布图'
    })
    
    // 返回搜索筛选页面
    const handleBackToSearch = () => {
      // 使用路由器导航到搜索页面，但我们确保不会导致状态丢失
      // 不再使用router.go(-1)，因为它在某些情况下不可靠
      router.push('/dashboard/search')
    }
    
    // 返回收藏页面
    const handleBackToFavorites = () => {
      // 导航到个人中心的收藏标签页
      router.push('/dashboard/profile?tab=favorites')
    }
    
    // 返回交通分析页面
    const handleBackToTransportation = () => {
      // 获取来源参数
      const province = route.query.province as string
      const transport = route.query.transport as string
      
      // 导航到交通分析页面，并保留原来的筛选条件
      router.push({
        path: '/dashboard/transportation',
        query: { 
          province: province || '全国',
          transport: transport || ''
        }
      })
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
    
    // 计算处理后的景区图片数组
    const processedScenicImages = computed(() => {
      if (!scenic.value.images || !Array.isArray(scenic.value.images) || scenic.value.images.length === 0) {
        return [defaultImage];
      }
      
      return scenic.value.images.map((img: string) => {
        return processImageUrl(img, defaultImage);
      });
    });
    
    // 处理轮播图图片加载错误
    const handleCarouselImageError = (event: Event, index: number) => {
      console.log(`[ScenicDetail] 轮播图第${index+1}张图片加载失败`);
      imageErrors.value[index] = true;
      
      // 替换为默认图片
      if (event.target) {
        (event.target as HTMLImageElement).src = defaultImage;
      }
    };
    
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
          street: data.street || '',
          
          // 价格信息
          price: data.min_price || '免费',
          
          // 类型和等级
          type: data.type || '未分类',
          level: data.level || '无等级',
          
          // 开放时间
          openingHours: data.opening_hours || '暂无开放时间信息',
          
          // 图片
          image: data.image_url ? processImageUrl(data.image_url, defaultImage) : defaultImage,
          images: data.image_url ? [processImageUrl(data.image_url, defaultImage)] : [defaultImage],
          
          // 评论相关
          comments: data.comments || [],
          commentCount: data.comment_count || 0,
          sentimentScore: data.sentiment_score || 0,
          sentiment: data.sentiment || '暂无',
          sentimentMagnitude: data.sentiment_magnitude || 0,
          
          // 交通信息 - 保存所有可能的交通数据字段
          transportation: data.transportation || '',
          traffic_info: data.traffic_info || '',
          trafficInfo: Array.isArray(data.trafficInfo) ? data.trafficInfo : 
                      (data.trafficInfo ? [{ description: data.trafficInfo }] : []),

          // 设施和推荐景点不再使用模拟数据
          recommendations: []
        };
        
        loading.value = false;
        
        // 获取词云数据 - 确保在景区详情加载完成后获取
        // 使用data.scenic_id或requestId作为参数
        fetchWordCloudData(data.scenic_id || requestId);
        
        // 获取附近景区数据
        fetchNearbyScenics(data.scenic_id || requestId);
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
    
    // 添加刷新键，确保词云图在数据变化时重新渲染
    const wordCloudRefreshKey = ref(0)
    const wordCloudContainer = ref<HTMLElement | null>(null)
    let wordCloudChart: echarts.ECharts | null = null

    // 处理词云图渲染完成事件
    const onWordCloudRendered = (chart: echarts.ECharts) => {
      wordCloudChart = chart
      console.log('词云图渲染完成')
    }
    
    // 获取词云数据
    const fetchWordCloudData = async (scenicId: string) => {
      if (!scenicId) return;
      
      wordCloudLoading.value = true;
      try {
        console.log('开始获取词云数据，景区ID:', scenicId);
        
        // 每次获取新数据前，增加刷新键
        wordCloudRefreshKey.value++
        
        // 如果存在词云图实例，先销毁
        if (wordCloudChart) {
          wordCloudChart.dispose()
          wordCloudChart = null
          console.log('已销毁旧的词云图实例')
        }
        
        const response = await getWordCloud(scenicId);
        console.log('词云数据API响应:', response);
        
        // 检查响应数据结构
        if (!response || !response.data) {
          console.error('词云数据响应格式错误:', response);
          wordCloudData.value = [];
          return;
        }
        
        // 检查返回的数据是否为空
        if (Array.isArray(response.data) && response.data.length > 0) {
          console.log('成功获取词云数据，数据项数:', response.data.length);
          wordCloudData.value = response.data;
        } else {
          console.warn('词云数据为空数组，不使用模拟数据');
          wordCloudData.value = [];
        }
        
        console.log('处理后的词云数据:', wordCloudData.value);
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
    
    // 判断是否有词云数据
    const hasWordCloudData = computed(() => {
      return wordCloudData.value && wordCloudData.value.length > 0;
    });
    
    // 词云图配置
    const wordCloudOptions = computed(() => {
      console.log('构建词云图配置，数据项数:', wordCloudData.value.length);
      
      return {
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
          sizeRange: [12, 60],
          rotationRange: [-45, 45],
          rotationStep: 10,
          gridSize: 8,
          drawOutOfBound: false,
          layoutAnimation: true,
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
      } as EChartsOption;
    });
    
    // 获取评论类型样式和文本
    const getCommentType = (sentiment: string) => {
      if (sentiment === '优') return { type: 'success', text: '评价优' };
      if (sentiment === '中') return { type: 'warning', text: '评价中' };
      if (sentiment === '良') return { type: 'danger', text: '评价良' };
      // 默认返回
      return { type: 'info', text: '暂无评价' };
    };
    
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
    
    // 导航到推荐景区
    const navigateToScenic = (scenicId: any) => {
      if (!scenicId) {
        ElMessage.warning('景区ID不存在');
        return;
      }
      
      console.log('准备导航到景区，ID类型:', typeof scenicId, '值:', scenicId);
      
      // 保存当前滚动位置
      const scrollPosition = window.scrollY;
      localStorage.setItem('scenic_scroll_position', scrollPosition.toString());
      
      // 确保ID是字符串类型，并检查是否需要添加前缀'S'
      let formattedId = String(scenicId); // 强制转换为字符串
      if (!formattedId.startsWith('S') && !isNaN(Number(formattedId))) {
        formattedId = `S${formattedId}`;
      }
      
      console.log(`导航到景区详情页，原始ID: ${scenicId}, 格式化后ID: ${formattedId}`);
      
      // 在同一页面导航到新景区时，添加reload参数以确保页面刷新数据
      router.push({
        path: `/dashboard/scenic/${formattedId}`,
        query: { 
          reload: Date.now().toString() // 添加时间戳确保路由变化
        }
      });
    }
    
    // 格式化地址，避免重复
    const formatAddress = (scenic: any) => {
      if (!scenic) return '';
      
      // 检查数据完整性
      const parts = [];
      
      if (scenic.province) parts.push(scenic.province);
      
      // 仅当城市名称与省份不同时才添加
      if (scenic.city && scenic.city !== scenic.province) parts.push(scenic.city);
      
      // 仅当区县名称与城市名不同时才添加
      if (scenic.district && scenic.district !== scenic.city) parts.push(scenic.district);
      
      // 添加街道
      if (scenic.street) parts.push(scenic.street);
      
      return parts.join(' ');
    };
    
    // 获取附近景区数据
    const nearbyScenics = ref<any[]>([])
    const nearbyLoading = ref(false)
    
    const fetchNearbyScenics = async (scenicId: string) => {
      if (!scenicId) return
      
      nearbyLoading.value = true
      try {
        console.log('开始获取附近景区数据，景区ID:', scenicId)
        const response = await getNearbyScenics(scenicId)
        console.log('附近景区API响应:', response)
        
        if (!response || !response.data) {
          console.error('附近景区响应格式错误:', response)
          nearbyScenics.value = []
          return
        }
        
        if (Array.isArray(response.data) && response.data.length > 0) {
          console.log('成功获取附近景区数据，数量:', response.data.length)
          nearbyScenics.value = response.data
        } else {
          console.warn('附近景区数据为空数组')
          nearbyScenics.value = []
        }
      } catch (error) {
        console.error('获取附近景区失败:', error)
        nearbyScenics.value = []
      } finally {
        nearbyLoading.value = false
      }
    }
    
    // 格式化距离的函数
    const formatDistance = (distance: number) => {
      if (distance === undefined || distance === null) return ''
      
      if (distance < 1) {
        return `${(distance * 1000).toFixed(0)}米`
      } else {
        return `${distance.toFixed(1)}公里`
      }
    }
    
    // 处理图片URL
    const handleImageUrl = (url: string) => {
      if (!url) return defaultImage
      return processImageUrl(url, defaultImage)
    }
    
    // 处理附近景区图片加载错误
    const handleNearbyImageError = (event: Event) => {
      console.log('[ScenicDetail] 附近景区图片加载失败');
      // 替换为默认图片
      if (event.target) {
        (event.target as HTMLImageElement).src = defaultImage;
      }
    };
    
    onMounted(() => {
      fetchScenicDetail();
      
      // 恢复滚动位置
      nextTick(() => {
        const savedPosition = localStorage.getItem('scenic_scroll_position');
        if (savedPosition) {
          window.scrollTo(0, parseInt(savedPosition));
          localStorage.removeItem('scenic_scroll_position'); // 清除保存的位置
        }
      });
    });
    
    // 监听路由变化，当URL中的景区ID变化时重新获取数据
    watch(() => route.params.id, (newId, oldId) => {
      if (newId && newId !== oldId) {
        console.log(`景区ID变化：${oldId} -> ${newId}, reload参数: ${route.query.reload}`);
        fetchScenicDetail();
      }
    });
    
    // 监听reload查询参数变化
    watch(() => route.query.reload, (newVal) => {
      if (newVal) {
        console.log(`检测到reload参数: ${newVal}, 重新获取景区数据`);
        fetchScenicDetail();
      }
    });
    
    // 在组件销毁时清理词云图实例
    onBeforeUnmount(() => {
      if (wordCloudChart) {
        wordCloudChart.dispose()
        wordCloudChart = null
        console.log('组件卸载时销毁词云图实例')
      }
    })
    
    return {
      scenic,
      loading,
      handleBackToSearch,
      handleBackToFavorites,
      handleBackToTransportation,
      fromFavorites,
      fromTransportation,
      isFavorite,
      toggleFavorite,
      wordCloudOptions,
      wordCloudLoading,
      trafficContent,
      currentPage,
      pageSize,
      paginatedComments,
      handleSizeChange,
      handleCurrentChange,
      processedScenicImages,
      handleCarouselImageError,
      defaultImage,
      scenicId,
      isLoggedIn,
      hasWordCloudData,
      getCommentType,
      navigateToScenic,
      formatAddress,
      nearbyScenics,
      nearbyLoading,
      formatDistance,
      handleImageUrl,
      wordCloudContainer,
      wordCloudRefreshKey,
      onWordCloudRendered,
      transportationBackButtonText,
      handleNearbyImageError
    }
  }
})
</script>

<style scoped>
.scenic-detail-container {
  padding: 20px;
}

.loading-container {
  padding: 40px;
}

.scenic-detail-content {
  margin-top: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.left-buttons {
  display: flex;
  gap: 10px;
}

.right-buttons {
  display: flex;
  gap: 10px;
}

.header-actions .el-button {
  margin-right: 0;
  font-size: 16px;
}

.scenic-title {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 10px;
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

.traffic-detail pre.traffic-content {
  font-family: 'PingFang SC', 'Helvetica Neue', Helvetica, 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  white-space: pre-wrap;
  font-size: 15px;
  line-height: 1.8;
  color: #333;
  background-color: #f9f9f9;
  padding: 12px;
  border-radius: 4px;
  border-left: 3px solid #409EFF;
}

.sentiment-overview {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.sentiment-calculation {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.sentiment-calculation h3 {
  font-size: 16px;
  color: #303133;
  margin-top: 0;
  margin-bottom: 15px;
  font-weight: 500;
}

.calculation-item {
  margin-bottom: 15px;
}

.calculation-item:last-child {
  margin-bottom: 0;
}

.calculation-title {
  font-weight: 500;
  color: #409EFF;
  margin-bottom: 8px;
}

.calculation-desc {
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
}

.calculation-desc ul {
  padding-left: 20px;
  margin: 8px 0;
}

.calculation-desc li {
  margin-bottom: 5px;
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
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  padding: 10px;
  background-color: #f9f9f9;
  overflow: hidden;
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
  position: relative;
  overflow: hidden;
}

.recommended-item:before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #409EFF;
  transform: scaleX(0);
  transition: transform 0.3s ease;
  transform-origin: left;
}

.recommended-item:hover {
  background-color: #f5f7fa;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.recommended-item:hover:before {
  transform: scaleX(1);
}

.recommended-item:active {
  transform: translateY(0);
  box-shadow: 0 1px 4px 0 rgba(0, 0, 0, 0.1);
}

.recommended-image {
  width: 60px;
  height: 60px;
  margin-right: 10px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.recommended-info {
  flex: 1;
}

.recommended-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 5px;
  display: -webkit-box;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recommended-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recommended-price {
  color: #f56c6c;
  font-size: 14px;
}

.recommended-distance {
  color: #909399;
  font-size: 13px;
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

/* 响应式布局调整 */
@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    gap: 15px;
  }
  
  .left-buttons {
    width: 100%;
    justify-content: space-between;
  }
  
  .right-buttons {
    width: 100%;
  }
  
  .right-buttons .el-button {
    width: 100%;
  }
}

.recommended-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.recommended-item:hover .recommended-image img {
  transform: scale(1.1);
}
</style> 