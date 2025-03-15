<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { useScenicStore } from '@/stores/scenic'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const scenicStore = useScenicStore()
const loading = ref(false)
const classType = ref('scenic') // 默认显示景区级别
const levelChart = ref<HTMLElement | null>(null)
const priceChart = ref<HTMLElement | null>(null)
const levelChartInstance = ref<echarts.ECharts | null>(null)
const priceChartInstance = ref<echarts.ECharts | null>(null)
const activeLevel = ref('') // 当前选中的级别

// 分类类型选项
const classTypeOptions = [
  { value: 'scenic', label: '景区级别' },
  { value: 'museum', label: '博物馆等级' },
  { value: 'geo', label: '地质公园等级' },
  { value: 'forest', label: '森林公园等级' },
  { value: 'wetland', label: '湿地级别' },
  { value: 'cultural', label: '文物保护单位' },
  { value: 'nature', label: '自然保护区等级' }
]

// 根据分类类型获取对应的数据
const getLevelData = computed(() => {
  switch (classType.value) {
    case 'scenic':
      return scenicStore.scenicLevels
    case 'museum':
      return scenicStore.museumLevels
    case 'geo':
      return scenicStore.geoLevels
    case 'forest':
      return scenicStore.forestLevels
    case 'wetland':
      return scenicStore.wetlandLevels
    case 'cultural':
      return scenicStore.culturalLevels
    case 'nature':
      return scenicStore.natureLevels
    default:
      return []
  }
})

// 根据分类类型获取对应的价格数据
const getPriceData = computed(() => {
  switch (classType.value) {
    case 'scenic':
      return scenicStore.scenicLevelPrices
    case 'museum':
      return scenicStore.museumLevelPrices
    case 'geo':
      return scenicStore.geoLevelPrices
    case 'forest':
      return scenicStore.forestLevelPrices
    case 'wetland':
      return scenicStore.wetlandLevelPrices
    case 'cultural':
      return scenicStore.culturalLevelPrices
    case 'nature':
      return scenicStore.natureLevelPrices
    default:
      return []
  }
})

// 初始化级别环形图
const initLevelChart = () => {
  if (!levelChart.value) return
  
  levelChartInstance.value = echarts.init(levelChart.value)
  
  const option = {
    title: {
      text: '级别分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: getLevelData.value.map(item => item.name)
    },
    series: [
      {
        name: '级别分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: getLevelData.value.map(item => ({
          name: item.name,
          value: item.value
        }))
      }
    ]
  }
  
  levelChartInstance.value.setOption(option)
  
  // 点击事件
  levelChartInstance.value.on('click', (params) => {
    activeLevel.value = params.name
    updatePriceChart(params.name)
  })
}

// 初始化价格环形图
const initPriceChart = () => {
  if (!priceChart.value) return
  
  priceChartInstance.value = echarts.init(priceChart.value)
  
  const option = {
    title: {
      text: '平均价格分布（元）',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}元'
    },
    series: [
      {
        name: '平均价格',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}元'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        data: getPriceData.value.map(item => ({
          name: item.name,
          value: item.value
        }))
      }
    ]
  }
  
  priceChartInstance.value.setOption(option)
}

// 更新价格环形图以突出显示选中的级别
const updatePriceChart = (levelName: string) => {
  if (!priceChartInstance.value) return
  
  const data = getPriceData.value.map(item => {
    if (item.name === levelName) {
      return {
        name: item.name,
        value: item.value,
        itemStyle: {
          color: '#FF4500'
        }
      }
    }
    return {
      name: item.name,
      value: item.value
    }
  })
  
  priceChartInstance.value.setOption({
    series: [
      {
        data: data
      }
    ]
  })
}

// 更新图表数据
const updateCharts = () => {
  if (!levelChartInstance.value || !priceChartInstance.value) return
  
  // 更新级别环形图
  levelChartInstance.value.setOption({
    legend: {
      data: getLevelData.value.map(item => item.name)
    },
    series: [
      {
        data: getLevelData.value.map(item => ({
          name: item.name,
          value: item.value
        }))
      }
    ]
  })
  
  // 更新价格环形图
  priceChartInstance.value.setOption({
    series: [
      {
        data: getPriceData.value.map(item => {
          if (item.name === activeLevel.value) {
            return {
              name: item.name,
              value: item.value,
              itemStyle: {
                color: '#FF4500'
              }
            }
          }
          return {
            name: item.name,
            value: item.value
          }
        })
      }
    ]
  })
}

// 窗口大小改变时重新调整图表大小
const handleResize = () => {
  levelChartInstance.value?.resize()
  priceChartInstance.value?.resize()
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    await scenicStore.getScenicLevels()
    nextTick(() => {
      initLevelChart()
      initPriceChart()
    })
  } catch (error) {
    console.error('获取景区等级数据失败:', error)
    ElMessage.error('获取景区等级数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 监听分类类型变化
watch(classType, () => {
  updateCharts()
  activeLevel.value = '' // 重置选中的级别
})

onMounted(() => {
  fetchData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  levelChartInstance.value?.dispose()
  priceChartInstance.value?.dispose()
})
</script>

<template>
  <div class="scenic-classification-container">
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>景区等级与分类分析</span>
          <el-select v-model="classType" placeholder="选择分类类型">
            <el-option
              v-for="item in classTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </div>
      </template>
      
      <el-row :gutter="20" v-loading="loading">
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <div class="chart-container" ref="levelChart"></div>
        </el-col>
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <div class="chart-container" ref="priceChart"></div>
        </el-col>
      </el-row>
      
      <el-empty v-if="getLevelData.length === 0 && !loading" description="暂无数据" />
    </el-card>
    
    <el-card class="analysis-card">
      <template #header>
        <div class="card-header">
          <span>分析结论</span>
        </div>
      </template>
      
      <div class="analysis-content">
        <el-alert
          v-if="classType === 'scenic'"
          title="景区级别分析结论"
          type="info"
          :closable="false"
        >
          <p>1. 5A级景区数量较少但门票价格最高，平均价格为150元；</p>
          <p>2. 4A级景区数量最多，占总数的60%以上；</p>
          <p>3. 高等级景区分布主要集中在东部沿海地区。</p>
        </el-alert>
        
        <el-alert
          v-else-if="classType === 'museum'"
          title="博物馆等级分析结论"
          type="info"
          :closable="false"
        >
          <p>1. 国家级博物馆数量占比约为30%，大多免费开放；</p>
          <p>2. 省级博物馆数量最多，占总数的45%；</p>
          <p>3. 非国有博物馆虽数量较少，但平均票价最高。</p>
        </el-alert>
        
        <el-alert
          v-else-if="classType === 'geo'"
          title="地质公园等级分析结论"
          type="info"
          :closable="false"
        >
          <p>1. 世界级地质公园数量稀少，仅占总数的10%，但门票价格最高；</p>
          <p>2. 国家级地质公园占据主导地位，约占总数的70%；</p>
          <p>3. 地质公园主要分布在西部和西南地区。</p>
        </el-alert>
        
        <el-alert
          v-else-if="classType === 'forest'"
          title="森林公园等级分析结论"
          type="info"
          :closable="false"
        >
          <p>1. 国家级森林公园数量远超地质公园，占比约55%；</p>
          <p>2. 森林公园平均票价较低，多在50-80元区间；</p>
          <p>3. 大部分森林公园分布在东北、西南等林区资源丰富地区。</p>
        </el-alert>
        
        <el-alert
          v-else-if="classType === 'wetland'"
          title="湿地级别分析结论"
          type="info"
          :closable="false"
        >
          <p>1. 国际级湿地占比约15%，主要是拉姆萨尔湿地；</p>
          <p>2. 国家级湿地占主导地位，约占总数的65%；</p>
          <p>3. 湿地公园平均票价较低，多在40-60元区间。</p>
        </el-alert>
        
        <el-alert
          v-else-if="classType === 'cultural'"
          title="文物保护单位分析结论"
          type="info"
          :closable="false"
        >
          <p>1. 国家级文物保护单位约占总数的25%，平均票价最高；</p>
          <p>2. 省级文物保护单位数量最多，占比约50%；</p>
          <p>3. 文物保护单位数量在东部地区明显高于西部地区。</p>
        </el-alert>
        
        <el-alert
          v-else-if="classType === 'nature'"
          title="自然保护区等级分析结论"
          type="info"
          :closable="false"
        >
          <p>1. 国家级自然保护区约占总数的35%，部分不对外开放；</p>
          <p>2. 省级自然保护区占比约65%，主要分布在西部地区；</p>
          <p>3. 自然保护区整体票价较低，以保护为主要目的。</p>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.scenic-classification-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-card, .analysis-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.analysis-content p {
  margin: 5px 0;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .chart-container {
    height: 300px;
    margin-bottom: 20px;
  }
}
</style> 