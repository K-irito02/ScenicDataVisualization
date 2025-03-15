<template>
  <div class="scenic-card" @click="navigateToDetail">
    <div class="scenic-card-image">
      <img :src="scenic.image || defaultImage" :alt="scenic.name" />
      <div class="scenic-card-level" v-if="scenic.level">{{ scenic.level }}</div>
    </div>
    <div class="scenic-card-content">
      <h3 class="scenic-card-title">{{ scenic.name }}</h3>
      <div class="scenic-card-location">
        <el-icon><Location /></el-icon>
        <span>{{ scenic.province }} {{ scenic.city }}</span>
      </div>
      <div class="scenic-card-info">
        <div class="scenic-card-price" v-if="scenic.price !== undefined">
          <span>¥</span>{{ scenic.price }}
        </div>
        <div class="scenic-card-type" v-if="scenic.type">{{ scenic.type }}</div>
      </div>
    </div>
    <div class="scenic-card-actions">
      <el-button 
        type="text" 
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
import { defineComponent, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Location, Star, StarFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

export default defineComponent({
  name: 'ScenicCard',
  components: {
    Location,
    Star,
    StarFilled
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
    const defaultImage = '/images/default-scenic.jpg'
    
    // 检查用户是否已登录
    const isLoggedIn = computed(() => !!userStore.token)
    
    // 检查是否已收藏
    const isFavorite = computed(() => {
      return userStore.favorites.some((id: string) => id === props.scenic.id)
    })
    
    // 跳转到景区详情页
    const navigateToDetail = () => {
      router.push(`/dashboard/scenic/${props.scenic.id}`)
    }
    
    // 切换收藏状态
    const toggleFavorite = async () => {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录')
        return
      }
      
      try {
        await userStore.toggleFavorite(props.scenic.id)
        ElMessage.success(isFavorite.value ? '已取消收藏' : '收藏成功')
      } catch (error) {
        ElMessage.error('操作失败，请重试')
      }
    }
    
    return {
      defaultImage,
      isFavorite,
      navigateToDetail,
      toggleFavorite
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
</style> 