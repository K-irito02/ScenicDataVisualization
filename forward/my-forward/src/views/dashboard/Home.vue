<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ElLoading } from 'element-plus/es'
import axios from 'axios'

// 统计数据
const totalScenicSpots = ref(0)
const totalProvinces = ref(0)
const totalCities = ref(0)
const dataSourceInfo = ref({
  mafengwo: {
    name: '马蜂窝',
    description: '中国领先的自由行旅游平台',
    dataCount: 0,
    logo: '/mafw.png',
    url: 'https://www.mafengwo.cn/'
  },
  deepseek: {
    name: 'DeepSeek AI',
    description: '深度学习与自然语言处理技术支持',
    dataCount: 0,
    logo: '/deepseek.png',
    url: 'https://www.deepseek.com/'
  }
})

// 数据加载函数
const fetchStatistics = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '加载数据统计信息...',
    background: 'rgba(255, 255, 255, 0.7)'
  })
  
  try {
    // 恢复API调用
    const response = await axios.get('/api/statistics/summary')
    const data = response.data
    
    // 使用API返回的数据
    totalScenicSpots.value = data.totalScenicSpots || 12506
    totalProvinces.value = data.totalProvinces || 34
    totalCities.value = data.totalCities || 370
    
    // 数据来源统计
    dataSourceInfo.value.mafengwo.dataCount = data.mafengwoCount || 10250
    dataSourceInfo.value.deepseek.dataCount = data.deepseekCount || 2256
    
    console.log('成功加载统计数据:', data)
    
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败，显示默认数据')
    
    // 设置默认数据，保证界面正常显示
    totalScenicSpots.value = 12506
    totalProvinces.value = 34
    totalCities.value = 370
    dataSourceInfo.value.mafengwo.dataCount = 10250
    dataSourceInfo.value.deepseek.dataCount = 2256
  } finally {
    loading.close()
  }
}

// 模块信息
const moduleInfo = [
  {
    title: '景区基础分布分析',
    icon: 'Location',
    description: '展示全国各省市景区的地理分布情况，帮助您了解各地区景区密度与分布规律。'
  },
  {
    title: '景区等级与分类分析',
    icon: 'Medal', 
    description: '根据景区等级（如5A、4A）和分类（如自然景观、文化遗址）进行统计分析。'
  },
  {
    title: '门票与开放时间分析',
    icon: 'Ticket',
    description: '分析景区门票价格区间分布和开放时间特点，为游客提供参考。'
  },
  {
    title: '评论与情感分析',
    icon: 'ChatDotRound',
    description: '基于游客评论进行情感分析，展示景区口碑和游客满意度。'
  },
  {
    title: '交通与可达性分析',
    icon: 'Van',
    description: '分析景区交通可达性和方式，为游客出行规划提供建议。'
  },
  {
    title: '搜索与筛选',
    icon: 'Search',
    description: '支持多维度搜索和筛选，快速找到您感兴趣的景区信息。'
  }
]

// 技术栈信息
const techStacks = [
  {
    title: '爬虫技术',
    items: ['Scrapy', 'Scrapy-Redis', 'Selenium', 'Python', '分布式爬虫架构']
  },
  {
    title: '后端技术',
    items: ['Django', 'Django REST Framework', 'MySQL', 'Redis', 'Python']
  },
  {
    title: '前端技术',
    items: ['Vue 3', 'TypeScript', 'Element Plus', 'ECharts', 'Highcharts']
  },
  {
    title: '数据处理技术',
    items: ['Pandas', 'NumPy', '情感分析', '自然语言处理', '地理信息处理']
  }
]

// 组件挂载后获取数据
onMounted(() => {
  fetchStatistics()
})
</script>

<template>
  <div class="home-container">
    <!-- 头部欢迎区 -->
    <el-card class="welcome-section">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>全国景区数据分析及可视化系统</h1>
          <p class="welcome-description">
            本系统汇集全国各地景区数据，提供多维度分析和可视化展示，帮助您深入了解中国旅游资源分布和特点。
            基于大规模数据采集和先进的数据处理技术，为旅游研究、行业分析和旅行规划提供数据支持。
          </p>
          <div class="stats-container">
            <div class="stat-item">
              <div class="stat-value">{{ totalScenicSpots.toLocaleString() }}</div>
              <div class="stat-label">景区总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ totalProvinces }}</div>
              <div class="stat-label">覆盖省份</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ totalCities }}</div>
              <div class="stat-label">覆盖城市</div>
            </div>
          </div>
        </div>
        <div class="welcome-image">
          <img src="/logo.png" alt="系统Logo" class="system-logo" />
        </div>
      </div>
    </el-card>

    <!-- 数据来源部分 -->
    <h2 class="section-title">数据来源</h2>
    <div class="data-sources-container">
      <el-card v-for="(source, key) in dataSourceInfo" :key="key" class="data-source-card">
        <div class="data-source-content">
          <div class="data-source-logo">
            <a :href="source.url" target="_blank" rel="noopener noreferrer">
              <img :src="source.logo" :alt="source.name" class="source-logo-img">
            </a>
          </div>
          <div class="data-source-info">
            <h3>{{ source.name }}</h3>
            <p>{{ source.description }}</p>
            <div class="data-count">
              <span class="count-label">数据贡献：</span>
              <span class="count-value">{{ source.dataCount.toLocaleString() }} 条</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 数据采集流程 -->
    <h2 class="section-title">数据采集与处理流程</h2>
    <el-card class="process-section">
      <el-steps :active="5" finish-status="success" align-center>
        <el-step title="数据爬取" description="使用Scrapy-Redis分布式架构从马蜂窝网站爬取景区信息" />
        <el-step title="数据预处理" description="数据清洗、标准化和结构化处理" />
        <el-step title="情感分析" description="对游客评论进行情感分析，提取关键词和情感倾向" />
        <el-step title="数据存储" description="将处理后的数据存入MySQL和Redis数据库" />
        <el-step title="数据可视化" description="通过前端界面展示多维度数据分析结果" />
      </el-steps>
    </el-card>

    <!-- 功能模块 -->
    <h2 class="section-title">功能模块</h2>
    <div class="modules-container">
      <el-card v-for="(module, index) in moduleInfo" :key="index" class="module-card">
        <div class="module-icon">
          <el-icon :size="30">
            <component :is="module.icon" />
          </el-icon>
        </div>
        <h3>{{ module.title }}</h3>
        <p>{{ module.description }}</p>
      </el-card>
    </div>

    <!-- 技术栈 -->
    <h2 class="section-title">技术栈</h2>
    <el-card class="tech-stack-section">
      <div class="tech-stacks-container">
        <div v-for="(stack, index) in techStacks" :key="index" class="tech-stack">
          <h3>{{ stack.title }}</h3>
          <ul class="tech-list">
            <li v-for="(item, i) in stack.items" :key="i">{{ item }}</li>
          </ul>
        </div>
      </div>
    </el-card>

    <!-- 项目特点 -->
    <h2 class="section-title">项目特点</h2>
    <el-card class="features-section">
      <div class="features-container">
        <div class="feature">
          <h3><el-icon><data-line /></el-icon> 大规模数据集</h3>
          <p>覆盖全国32个省级行政区，超过7,000个景区的详细信息</p>
        </div>
        <div class="feature">
          <h3><el-icon><data-analysis /></el-icon> 多维度分析</h3>
          <p>提供地理分布、等级分类、票价、评论情感等多角度分析</p>
        </div>
        <div class="feature">
          <h3><el-icon><picture /></el-icon> 直观可视化</h3>
          <p>采用地图、图表、词云等多种可视化方式展示数据</p>
        </div>
        <div class="feature">
          <h3><el-icon><connection /></el-icon> 分布式架构</h3>
          <p>基于Scrapy-Redis的分布式爬虫，支持大规模数据采集</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.welcome-section {
  margin-bottom: 30px;
  border-radius: 8px;
}

.welcome-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.welcome-text {
  flex: 1;
  padding-right: 40px;
}

.welcome-text h1 {
  font-size: 28px;
  margin-bottom: 16px;
  color: #303133;
}

.welcome-description {
  font-size: 16px;
  line-height: 1.6;
  color: #606266;
  margin-bottom: 30px;
}

.welcome-image {
  flex: 0 0 200px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.system-logo {
  width: 180px;
  height: 180px;
  object-fit: contain;
}

.stats-container {
  display: flex;
  margin-top: 20px;
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 6px;
  margin-right: 10px;
}

.stat-item:last-child {
  margin-right: 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.section-title {
  font-size: 22px;
  margin: 30px 0 20px;
  color: #303133;
  position: relative;
  padding-left: 15px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 5px;
  height: 20px;
  background-color: #409EFF;
  border-radius: 2px;
}

.data-sources-container {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.data-source-card {
  flex: 1;
  border-radius: 8px;
}

.data-source-content {
  display: flex;
  align-items: center;
}

.data-source-logo {
  margin-right: 20px;
}

.source-logo-img {
  width: 80px;
  height: 80px;
  object-fit: contain;
  border-radius: 8px;
  transition: transform 0.3s ease;
}

.source-logo-img:hover {
  transform: scale(1.05);
  cursor: pointer;
}

.data-source-info {
  flex: 1;
}

.data-source-info h3 {
  margin: 0 0 10px;
  font-size: 18px;
  color: #303133;
}

.data-source-info p {
  margin: 0 0 15px;
  color: #606266;
}

.data-count {
  font-size: 14px;
}

.count-label {
  color: #909399;
}

.count-value {
  font-weight: 600;
  color: #409EFF;
}

.process-section {
  margin-bottom: 30px;
  padding: 30px;
  border-radius: 8px;
}

.modules-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.module-card {
  border-radius: 8px;
  height: 100%;
}

.module-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
  color: #409EFF;
}

.module-card h3 {
  text-align: center;
  margin: 0 0 10px;
  font-size: 18px;
  color: #303133;
}

.module-card p {
  text-align: center;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.tech-stack-section {
  margin-bottom: 30px;
  border-radius: 8px;
}

.tech-stacks-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.tech-stack h3 {
  font-size: 18px;
  margin: 0 0 15px;
  color: #303133;
}

.tech-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.tech-list li {
  padding: 5px 0;
  color: #606266;
  position: relative;
  padding-left: 15px;
}

.tech-list li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #409EFF;
}

.features-section {
  margin-bottom: 30px;
  border-radius: 8px;
}

.features-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
}

.feature h3 {
  display: flex;
  align-items: center;
  font-size: 18px;
  margin: 0 0 10px;
  color: #303133;
}

.feature h3 .el-icon {
  margin-right: 8px;
  color: #409EFF;
}

.feature p {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

@media (max-width: 992px) {
  .welcome-content {
    flex-direction: column;
  }
  
  .welcome-text {
    padding-right: 0;
    margin-bottom: 20px;
  }
  
  .data-sources-container,
  .tech-stacks-container {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .modules-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .data-sources-container,
  .tech-stacks-container,
  .modules-container,
  .features-container {
    grid-template-columns: 1fr;
  }
}
</style> 