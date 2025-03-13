<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 用户信息卡片 -->
      <el-col :span="8">
        <el-card class="user-card">
          <div class="user-avatar">
            <el-avatar :size="100" src="https://example.com/avatar.jpg">用户</el-avatar>
          </div>
          <div class="user-info">
            <h2>张三</h2>
            <p class="user-level">旅行达人 Lv.5</p>
            <div class="user-stats">
              <div class="stat-item">
                <p class="stat-value">125</p>
                <p class="stat-label">足迹</p>
              </div>
              <div class="stat-item">
                <p class="stat-value">38</p>
                <p class="stat-label">收藏</p>
              </div>
              <div class="stat-item">
                <p class="stat-value">89</p>
                <p class="stat-label">评论</p>
              </div>
            </div>
          </div>
          <div class="user-actions">
            <el-button type="primary">编辑资料</el-button>
            <el-button>我的足迹</el-button>
          </div>
        </el-card>
        
        <!-- 个人信息详情 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>个人信息</span>
              <el-button class="button" text>编辑</el-button>
            </div>
          </template>
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">用户名</span>
              <span class="info-value">travel_zhang</span>
            </div>
            <div class="info-item">
              <span class="info-label">注册时间</span>
              <span class="info-value">2022-05-15</span>
            </div>
            <div class="info-item">
              <span class="info-label">邮箱</span>
              <span class="info-value">zhang@example.com</span>
            </div>
            <div class="info-item">
              <span class="info-label">所在地</span>
              <span class="info-value">北京市</span>
            </div>
            <div class="info-item">
              <span class="info-label">偏好景点</span>
              <span class="info-value">
                <el-tag size="small" class="preference-tag">自然风光</el-tag>
                <el-tag size="small" class="preference-tag">历史人文</el-tag>
                <el-tag size="small" class="preference-tag">博物馆</el-tag>
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 收藏景区列表 -->
      <el-col :span="16">
        <el-card class="favorites-card">
          <template #header>
            <div class="card-header">
              <span>我的收藏</span>
              <el-select v-model="filterValue" placeholder="筛选" style="width: 120px">
                <el-option label="全部景区" value="all"></el-option>
                <el-option label="5A景区" value="5A"></el-option>
                <el-option label="4A景区" value="4A"></el-option>
                <el-option label="3A景区" value="3A"></el-option>
              </el-select>
            </div>
          </template>
          
          <el-empty v-if="favoriteList.length === 0" description="暂无收藏景区"></el-empty>
          
          <div v-else class="scenic-list">
            <el-card v-for="(item, index) in favoriteList" :key="index" class="scenic-item" shadow="hover">
              <div class="scenic-content">
                <el-image 
                  :src="item.image" 
                  fit="cover"
                  class="scenic-image"
                  :preview-src-list="[item.image]">
                </el-image>
                <div class="scenic-info">
                  <div class="scenic-title">
                    <h3>{{ item.name }}</h3>
                    <el-tag size="small" :type="item.level === '5A' ? 'danger' : item.level === '4A' ? 'warning' : 'info'">
                      {{ item.level }}
                    </el-tag>
                  </div>
                  <div class="scenic-desc">{{ item.description }}</div>
                  <div class="scenic-meta">
                    <span>
                      <el-icon><Location /></el-icon> {{ item.location }}
                    </span>
                    <span>
                      <el-icon><Tickets /></el-icon> {{ item.price }}元
                    </span>
                    <el-rate 
                      v-model="item.score" 
                      disabled 
                      text-color="#ff9900"
                      show-score>
                    </el-rate>
                  </div>
                  <div class="scenic-actions">
                    <el-button type="primary" size="small">查看详情</el-button>
                    <el-button type="danger" size="small" @click="unfavorite(item.id)">
                      取消收藏
                    </el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
          
          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              layout="prev, pager, next, jumper"
              :total="total"
              @current-change="handlePageChange">
            </el-pagination>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Location, Tickets } from '@element-plus/icons-vue'
import { unfavoriteScenicSpot } from '@/api/scenic'
import { ElMessage } from 'element-plus'

// 筛选值
const filterValue = ref('all')

// 分页数据
const currentPage = ref(1)
const pageSize = ref(5)
const total = ref(38)

// 收藏景区列表（模拟数据）
const favoriteList = ref([
  {
    id: 1001,
    name: '故宫博物院',
    level: '5A',
    price: 60,
    location: '北京市东城区景山前街4号',
    description: '中国明清两代的皇家宫殿，是中国古代宫廷建筑之精华。',
    score: 4.8,
    image: 'https://example.com/images/gugong.jpg'
  },
  {
    id: 1002,
    name: '颐和园',
    level: '5A',
    price: 30,
    location: '北京市海淀区新建宫门路19号',
    description: '中国现存规模最大、保存最完整的皇家园林，是中国园林艺术巅峰之作。',
    score: 4.7,
    image: 'https://example.com/images/yiheyuan.jpg'
  },
  {
    id: 1003,
    name: '八达岭长城',
    level: '5A',
    price: 40,
    location: '北京市延庆区八达岭长城景区',
    description: '中国古代伟大的防御工程，是中国古代文明的象征。',
    score: 4.6,
    image: 'https://example.com/images/badaling.jpg'
  },
  {
    id: 1004,
    name: '天坛公园',
    level: '5A',
    price: 15,
    location: '北京市东城区天坛路甲1号',
    description: '明清两代帝王祭祀皇天、祈求五谷丰登的场所，是中国现存规模最大的祭天建筑群。',
    score: 4.5,
    image: 'https://example.com/images/tiantan.jpg'
  },
  {
    id: 1005,
    name: '圆明园',
    level: '4A',
    price: 10,
    location: '北京市海淀区清华西路28号',
    description: '清代著名的皇家园林，被誉为"万园之园"。',
    score: 4.4,
    image: 'https://example.com/images/yuanmingyuan.jpg'
  }
])

// 获取用户收藏的景区列表
const loadFavoriteScenics = async () => {
  // 实际项目中应该从API获取数据
  // const { data } = await getUserFavorites({
  //   page: currentPage.value,
  //   pageSize: pageSize.value,
  //   level: filterValue.value === 'all' ? undefined : filterValue.value
  // })
  // favoriteList.value = data.list
  // total.value = data.total
  
  // 此处使用模拟数据
  console.log('加载收藏景区数据，页码:', currentPage.value, '筛选:', filterValue.value)
}

// 分页变化处理
const handlePageChange = (page: number) => {
  currentPage.value = page
  loadFavoriteScenics()
}

// 取消收藏
const unfavorite = async (id: number) => {
  try {
    const success = await unfavoriteScenicSpot(id)
    if (success) {
      ElMessage.success('取消收藏成功')
      // 从列表中移除
      favoriteList.value = favoriteList.value.filter(item => item.id !== id)
      // 更新总数
      total.value--
    }
  } catch (error) {
    ElMessage.error('操作失败，请重试')
    console.error('取消收藏失败:', error)
  }
}

onMounted(() => {
  loadFavoriteScenics()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.user-card {
  margin-bottom: 20px;
  text-align: center;
}

.user-avatar {
  margin: 10px 0 20px;
}

.user-info h2 {
  margin: 0;
  font-size: 22px;
}

.user-level {
  color: #909399;
  margin: 5px 0 15px;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  margin: 0;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin: 5px 0 0;
}

.user-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-list {
  margin-top: 10px;
}

.info-item {
  display: flex;
  padding: 10px 0;
  border-bottom: 1px solid #EBEEF5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  width: 80px;
  color: #909399;
}

.info-value {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.preference-tag {
  margin-right: 5px;
}

.favorites-card {
  height: 100%;
}

.scenic-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.scenic-item {
  margin-bottom: 0;
}

.scenic-content {
  display: flex;
  gap: 15px;
}

.scenic-image {
  width: 200px;
  height: 120px;
  border-radius: 4px;
  overflow: hidden;
}

.scenic-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.scenic-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.scenic-title h3 {
  margin: 0;
  font-size: 18px;
}

.scenic-desc {
  color: #606266;
  font-size: 14px;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.scenic-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}

.scenic-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.scenic-actions {
  margin-top: auto;
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style> 