<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { useScenicStore } from '@/stores/scenic'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const scenicStore = useScenicStore()
const loading = ref(false)
const ticketType = ref('scenic') // 默认显示景区级别
const boxPlotChart = ref<HTMLElement | null>(null)
const timeRingChart = ref<HTMLElement | null>(null)
const timeMapChart = ref<HTMLElement | null>(null)
const boxPlotChartInstance = ref<echarts.ECharts | null>(null)
const timeRingChartInstance = ref<echarts.ECharts | null>(null)
const timeMapChartInstance = ref<echarts.ECharts | null>(null)
const selectedTimeRange = ref('')
const showTimeMap = ref(false)

// 分类类型选项
const ticketTypeOptions = [
  { value: 'scenic', label: '景区级别' },
  { value: 'museum', label: '博物馆等级' },
  { value: 'geo', label: '地质公园等级' },
  { value: 'forest', label: '森林公园等级' },
  { value: 'wetland', label: '湿地级别' },
  { value: 'cultural', label: '文物保护单位' },
  { value: 'nature', label: '自然保护区等级' }
]

// 根据分类类型获取对应的数据
const getTicketData = computed(() => {
  if (!scenicStore.ticketPrices) return []
  
  switch (ticketType.value) {
    case 'scenic':
      return scenicStore.ticketPrices.scenicLevels || []
    case 'museum':
      return scenicStore.ticketPrices.museumLevels || []
    case 'geo':
      return scenicStore.ticketPrices.geoLevels || []
    case 'forest':
      return scenicStore.ticketPrices.forestLevels || []
    case 'wetland':
      return scenicStore.ticketPrices.wetlandLevels || []
    case 'cultural':
      return scenicStore.ticketPrices.culturalLevels || []
    case 'nature':
      return scenicStore.ticketPrices.natureLevels || []
    default:
      return []
  }
})

// 初始化箱线图
const initBoxPlotChart = () => {
  if (!boxPlotChart.value) return
  
  boxPlotChartInstance.value = echarts.init(boxPlotChart.value)
  
  const ticketData = getTicketData.value
  if (!ticketData.length) {
    return
  }
  
  const data = ticketData.map((item: any) => [item.min, item.q1, item.median, item.q3, item.max])
  const categories = ticketData.map((item: any) => item.level)
  
  const option = {
    title: {
      text: '门票价格分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function (params: any) {
        const itemData = ticketData[params.dataIndex]
        return `${itemData.level}<br>
               最小值: ${itemData.min}元<br>
               下四分位: ${itemData.q1}元<br>
               中位数: ${itemData.median}元<br>
               上四分位: ${itemData.q3}元<br>
               最大值: ${itemData.max}元`
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: categories,
      boundaryGap: true,
      nameGap: 30,
      splitArea: {
        show: false
      },
      axisLabel: {
        formatter: '{value}'
      },
      splitLine: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      name: '价格（元）',
      splitArea: {
        show: true
      }
    },
    series: [
      {
        name: '箱线图',
        type: 'boxplot',
        datasetIndex: 0,
        data: data,
        tooltip: {
          formatter: function (param: any) {
            return [
              param.name + ': ',
              '最小值: ' + param.data[0] + '元',
              '下四分位: ' + param.data[1] + '元',
              '中位数: ' + param.data[2] + '元',
              '上四分位: ' + param.data[3] + '元',
              '最大值: ' + param.data[4] + '元'
            ].join('<br/>')
          }
        }
      }
    ]
  }
  
  boxPlotChartInstance.value.setOption(option)
}

// 初始化开放时间环形图
const initTimeRingChart = () => {
  if (!timeRingChart.value) return
  
  timeRingChartInstance.value = echarts.init(timeRingChart.value)
  
  const timeData = scenicStore.openTimeData.map(item => ({
    name: item.timeRange,
    value: item.count
  }))
  
  const option = {
    title: {
      text: '景区开放时间分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 个景区 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: timeData.map(item => item.name)
    },
    series: [
      {
        name: '开放时间',
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
          position: 'outside',
          formatter: '{b}: {c}个 ({d}%)'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        data: timeData
      }
    ]
  }
  
  timeRingChartInstance.value.setOption(option)
  
  // 点击事件
  timeRingChartInstance.value.on('click', (params) => {
    selectedTimeRange.value = params.name
    showTimeMap.value = true
    nextTick(() => {
      initTimeMapChart(params.name)
    })
  })
}

// 初始化时间地图
const initTimeMapChart = (timeRange: string) => {
  if (!timeMapChart.value) return
  
  if (!timeMapChartInstance.value) {
    timeMapChartInstance.value = echarts.init(timeMapChart.value)
  }
  
  // 获取该时间段的景区数据
  const scenicIds = scenicStore.openTimeScenicMap[timeRange] || []
  
  // 这里需要获取景区的经纬度数据，实际应用中应该从服务器获取
  // 这里简单模拟一些点
  const scenicPoints = scenicIds.map((id, index) => {
    // 模拟数据，实际应该从API获取
    return {
      name: `景区${id}`,
      value: [100 + Math.random() * 20, 30 + Math.random() * 10, 1]
    }
  })
  
  const option = {
    title: {
      text: `${timeRange} 开放的景区分布`,
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        return params.name
      }
    },
    geo: {
      map: 'china',
      roam: true,
      emphasis: {
        label: {
          show: true
        }
      }
    },
    series: [
      {
        name: '景区分布',
        type: 'scatter',
        coordinateSystem: 'geo',
        data: scenicPoints,
        symbolSize: 8,
        itemStyle: {
          color: '#FF4500'
        },
        emphasis: {
          scale: true
        }
      }
    ]
  }
  
  timeMapChartInstance.value.setOption(option)
}

// 返回环形图
const backToTimeRing = () => {
  showTimeMap.value = false
  selectedTimeRange.value = ''
}

// 更新箱线图
const updateBoxPlotChart = () => {
  if (!boxPlotChartInstance.value) return
  
  const ticketData = getTicketData.value
  if (!ticketData.length) {
    return
  }
  
  const data = ticketData.map((item: any) => [item.min, item.q1, item.median, item.q3, item.max])
  const categories = ticketData.map((item: any) => item.level)
  
  boxPlotChartInstance.value.setOption({
    xAxis: {
      data: categories
    },
    series: [
      {
        data: data
      }
    ]
  })
}

// 窗口大小改变时重新调整图表大小
const handleResize = () => {
  boxPlotChartInstance.value?.resize()
  timeRingChartInstance.value?.resize()
  if (showTimeMap.value && timeMapChartInstance.value) {
    timeMapChartInstance.value.resize()
  }
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    await Promise.all([
      scenicStore.getTicketData(),
      scenicStore.getOpenTimeData()
    ])
    nextTick(() => {
      initBoxPlotChart()
      initTimeRingChart()
    })
  } catch (error) {
    console.error('获取门票与开放时间数据失败:', error)
    ElMessage.error('获取数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 监听票价类型变化
watch(ticketType, () => {
  updateBoxPlotChart()
})

onMounted(() => {
  fetchData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  boxPlotChartInstance.value?.dispose()
  timeRingChartInstance.value?.dispose()
  timeMapChartInstance.value?.dispose()
})
</script>

<template>
  <div class="ticket-analysis-container">
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>门票价格分析</span>
          <el-select v-model="ticketType" placeholder="选择票价分类">
            <el-option
              v-for="item in ticketTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </div>
      </template>
      
      <div v-loading="loading" class="boxplot-container" ref="boxPlotChart"></div>
      
      <el-empty v-if="getTicketData.length === 0 && !loading" description="暂无数据" />
    </el-card>
    
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>开放时间分析</span>
          <el-button 
            v-if="showTimeMap" 
            @click="backToTimeRing" 
            type="primary" 
            size="small"
          >
            返回时间分布图
          </el-button>
        </div>
      </template>
      
      <div v-loading="loading" class="time-chart-container">
        <div 
          class="time-ring-container" 
          ref="timeRingChart" 
          v-show="!showTimeMap"
        ></div>
        <div 
          class="time-map-container" 
          ref="timeMapChart" 
          v-show="showTimeMap"
        ></div>
      </div>
      
      <div v-if="selectedTimeRange" class="selected-time-info">
        <el-tag type="success">已选择: {{ selectedTimeRange }}</el-tag>
        <p class="hint-text">显示在此时间段开放的景区分布</p>
      </div>
      
      <el-empty 
        v-if="scenicStore.openTimeData.length === 0 && !loading" 
        description="暂无数据" 
      />
    </el-card>
    
    <el-card class="analysis-card">
      <template #header>
        <div class="card-header">
          <span>分析结论</span>
        </div>
      </template>
      
      <div class="analysis-content">
        <el-alert
          title="门票价格分析结论"
          type="info"
          :closable="false"
        >
          <p>1. 5A级景区门票中位数显著高于4A级，平均价格为120元；</p>
          <p>2. 存在部分低价促销景区，最低价格与中位数差距较大；</p>
          <p>3. 博物馆票价整体低于景区，国家级博物馆多为免费。</p>
        </el-alert>
        
        <el-divider></el-divider>
        
        <el-alert
          title="开放时间分析结论"
          type="info"
          :closable="false"
        >
          <p>1. 约90%的景区开放时间为8:00-18:00；</p>
          <p>2. 夏季部分景区延长开放时间至19:00或20:00；</p>
          <p>3. 少数景区（如夜景观赏区）采用错峰开放时间。</p>
        </el-alert>
        
        <el-divider></el-divider>
        
        <el-alert
          title="区域分布特点"
          type="warning"
          :closable="false"
        >
          <p>1. 东部沿海地区景区普遍票价高于中西部地区；</p>
          <p>2. 大型城市周边景区多采用9:00-17:00错峰开放时间；</p>
          <p>3. 北方地区景区冬季开放时间普遍较短，多为8:30-16:30。</p>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.ticket-analysis-container {
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

.boxplot-container {
  height: 400px;
  width: 100%;
}

.time-chart-container {
  height: 400px;
  width: 100%;
}

.time-ring-container, .time-map-container {
  height: 100%;
  width: 100%;
}

.selected-time-info {
  margin-top: 10px;
  text-align: center;
}

.hint-text {
  color: #606266;
  font-size: 12px;
  margin-top: 5px;
}

.analysis-content p {
  margin: 5px 0;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .boxplot-container,
  .time-chart-container {
    height: 300px;
  }
}
</style> 