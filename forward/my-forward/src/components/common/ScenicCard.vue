<template>
  <div class="scenic-card" @click="navigateToDetail">
    <div class="scenic-card-image">
      <img 
        :src="processedImageUrl || defaultImage"
        :alt="scenic.name || '景区'" 
        @error="handleImageError"
        class="lazy-image"
        v-loading="imageLoading"
        loading="lazy"
      />
      <div class="scenic-card-level" v-if="scenic.level">{{ scenic.level }}</div>
    </div>
    <div class="scenic-card-content">
      <h3 class="scenic-card-title">{{ scenic.name || '未命名景区' }}</h3>
      <div class="scenic-card-location">
        <el-icon><Location /></el-icon>
        <span>{{ (scenic.province || '') + ' ' + (scenic.city || '') }}</span>
      </div>
      <div class="scenic-card-info">
        <div class="scenic-card-price" v-if="scenic.min_price || scenic.price !== undefined">
          <span>¥</span>{{ displayPrice }}
        </div>
        <div class="scenic-card-type" v-if="getDisplayType">{{ getDisplayType }}</div>
      </div>
    </div>
    <div class="scenic-card-actions">
      <el-button 
        type="primary"
        link
        :icon="isFavorite ? 'StarFilled' : 'Star'" 
        @click.stop="toggleFavorite"
        :class="{ 'is-favorite': isFavorite }"
      >
        {{ isFavorite ? '已收藏' : '收藏' }}
      </el-button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Location, Star, StarFilled, Picture } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { processImageUrl, DEFAULT_IMAGE } from '@/api/image-proxy'

export default defineComponent({
  name: 'ScenicCard',
  components: {
    Location,
    Star,
    StarFilled,
    Picture
  },
  props: {
    scenic: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const router = useRouter()
    const userStore = useUserStore()
    const defaultImage = DEFAULT_IMAGE
    const imageError = ref(false)
    const imageLoading = ref(true)
    
    // 处理图片URL，避免跨域和403错误，使用缩略图模式
    const processedImageUrl = computed(() => {
      try {
        // 先检查图片是否存在
        if (!props.scenic.image) {
          console.log('[ScenicCard] 景区没有图片，使用默认图片');
          return defaultImage;
        }
        
        // 简化为直接处理图片URL
        console.log('[ScenicCard] 处理图片URL:', props.scenic.image);
        return processImageUrl(props.scenic.image, defaultImage);
      } catch (error) {
        console.error('[ScenicCard] 处理图片URL出错:', error);
        return defaultImage;
      }
    });
    
    // 预加载图片
    const preloadImage = () => {
      if (!processedImageUrl.value) return;
      
      const img = new Image();
      img.onload = () => {
        imageLoading.value = false;
        console.log('[ScenicCard] 图片加载成功:', processedImageUrl.value);
      };
      img.onerror = () => {
        imageLoading.value = false;
        imageError.value = true;
        console.error('[ScenicCard] 图片加载失败:', processedImageUrl.value);
      };
      img.src = processedImageUrl.value;
    };
    
    onMounted(() => {
      // 开始预加载
      preloadImage();
    });
    
    // 计算属性：获取适合显示的价格
    const displayPrice = computed(() => {
      // 尝试获取价格值
      const priceValue = props.scenic.price !== undefined ? props.scenic.price : 
                          props.scenic.min_price !== undefined ? props.scenic.min_price : null;
      
      // 如果价格为空、0或undefined，显示免费
      if (priceValue === null || priceValue === undefined || 
          priceValue === 0 || priceValue === '0' || 
          priceValue === '' || priceValue === 'free' || 
          priceValue === '免费') {
        return '免费';
      }
      
      return priceValue;
    });
    
    // 计算属性：获取适合显示的类型
    const getDisplayType = computed(() => {
      try {
        // 优先使用frontend_type
        if (props.scenic.frontend_type) {
          console.log(`[ScenicCard] 使用frontend_type: ${props.scenic.frontend_type}`);
          return props.scenic.frontend_type;
        }
        
        // 备选使用type
        if (props.scenic.type) {
          console.log(`[ScenicCard] 使用type: ${props.scenic.type}`);
          return props.scenic.type;
        }
        
        // 都没有时显示未分类
        return '未分类';
      } catch (error) {
        console.error('[ScenicCard] 获取景区类型出错:', error);
        return '未分类';
      }
    });
    
    // 检查用户是否已登录
    const isLoggedIn = computed(() => !!userStore.token)
    
    // 检查是否已收藏
    const isFavorite = computed(() => {
      try {
        const scenicId = props.scenic.scenic_id || props.scenic.id
        return scenicId && userStore.favorites.some((id: string) => id === scenicId)
      } catch (error) {
        console.error('[ScenicCard] 检查收藏状态出错:', error);
        return false;
      }
    })
    
    // 跳转到景区详情页
    const navigateToDetail = () => {
      try {
        const scenicId = props.scenic.scenic_id || props.scenic.id
        if (!scenicId) {
          ElMessage.warning('景区ID不存在')
          return
        }
        router.push(`/dashboard/scenic/${scenicId}`)
      } catch (error) {
        console.error('[ScenicCard] 导航到详情页出错:', error);
        ElMessage.error('导航到详情页失败');
      }
    }
    
    // 切换收藏状态
    const toggleFavorite = async () => {
      try {
        if (!isLoggedIn.value) {
          ElMessage.warning('请先登录')
          return
        }
        
        const scenicId = props.scenic.scenic_id || props.scenic.id
        if (!scenicId) {
          ElMessage.warning('景区ID不存在')
          return
        }
        
        const response = await userStore.toggleFavorite(scenicId)
        // 使用类型断言避免TypeScript错误
        const responseData = (response as any).data
        // 根据API响应的is_favorite字段决定提示内容，而不是基于旧的isFavorite值
        ElMessage.success(responseData?.is_favorite ? '已收藏' : '已取消收藏')
      } catch (error) {
        console.error('[ScenicCard] 切换收藏状态出错:', error);
        ElMessage.error('操作失败，请重试')
      }
    }
    
    // 处理图片加载错误
    const handleImageError = (event: Event) => {
      console.log('[ScenicCard] 图片加载失败，使用默认图片');
      // 替换为默认图片，而不仅仅是设置错误标志
      if (event.target) {
        (event.target as HTMLImageElement).src = defaultImage;
      }
      imageLoading.value = false;
    }
    
    return {
      defaultImage,
      imageLoading,
      handleImageError,
      isFavorite,
      navigateToDetail,
      toggleFavorite,
      getDisplayType,
      displayPrice,
      processedImageUrl
    }
  }
})
</script>

<style scoped>
.scenic-card {
  border-radius: 8px;
  overflow: hidden;
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.scenic-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.scenic-card-image {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.scenic-card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.scenic-card:hover .scenic-card-image img {
  transform: scale(1.05);
}

.scenic-card-level {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(245, 108, 108, 0.9);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.scenic-card-content {
  padding: 15px;
  flex: 1;
}

.scenic-card-title {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.scenic-card-location {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #606266;
  margin-bottom: 10px;
}

.scenic-card-location .el-icon {
  margin-right: 5px;
  color: #909399;
}

.scenic-card-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.scenic-card-price {
  color: #ff6b81;
  font-weight: bold;
  font-size: 16px;
}

.scenic-card-price span {
  font-size: 12px;
  margin-right: 2px;
}

.scenic-card-type {
  background-color: #f0f2f5;
  color: #606266;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.scenic-card-actions {
  border-top: 1px solid #f0f0f0;
  padding: 10px 15px;
  display: flex;
  justify-content: flex-end;
}

.is-favorite {
  color: #ff9900;
}

.image-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  color: #909399;
  font-size: 36px;
}

/* 修改懒加载相关样式 */
.lazy-image {
  opacity: 1;
  transition: opacity 0.5s ease, filter 0.5s ease;
}

.el-loading-mask {
  background-color: #f5f7fa !important;
  opacity: 0.8 !important;
}

/* 使用CSS变量使动画更流畅 */
:root {
  --loading-gradient: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  --loading-animation-duration: 1.5s;
}

/* 骨架屏背景 */
.scenic-card-image {
  background: var(--loading-gradient);
  background-size: 200% 100%;
  animation: loading var(--loading-animation-duration) infinite;
}

/* 修改图片加载时的背景动画 */
@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 当图片加载完成后移除背景动画 */
.lazy-image:not([v-loading]) ~ .scenic-card-image {
  background: none;
  animation: none;
}
</style> 