<template>
  <div class="geographic-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区全国分布热力图</span>
              <el-tooltip content="展示全国各省景区数量分布情况">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="map-container" ref="mapChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>各省景区数量排名</span>
              <el-tooltip content="展示各省景区数量从多到少的排名">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="chart-container" ref="rankChartRef"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区级别分布</span>
              <div class="header-right">
                <el-select v-model="currentDistributionType" placeholder="选择分布类型" size="small">
                  <el-option
                    v-for="item in distributionTypes"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </div>
            </div>
          </template>
          <div class="chart-container" ref="distributionChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watchEffect, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getScenicDistribution, getScenicHeatmap } from '@/api/scenic'
import type { DistributionStatistics } from '@/types/scenic'
import { InfoFilled } from '@element-plus/icons-vue'

// 图表实例
let mapChart: echarts.ECharts | null = null
let rankChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null

// DOM引用
const mapChartRef = ref<HTMLElement | null>(null)
const rankChartRef = ref<HTMLElement | null>(null)
const distributionChartRef = ref<HTMLElement | null>(null)

// 分布类型选择
const distributionTypes = [
  { label: '景区级别分布', value: 'level' },
  { label: '自然保护区分布', value: 'natureReserve' },
  { label: '森林公园分布', value: 'forestPark' },
  { label: '地质公园分布', value: 'geologicalPark' },
  { label: '文物保护单位分布', value: 'culturalRelic' }
]
const currentDistributionType = ref('level')

// 初始化图表
onMounted(async () => {
  // 加载中国地图数据
  await loadChineseMap()
  
  // 初始化图表
  await initMapChart()
  await initRankChart()
  await initDistributionChart()
  
  // 窗口大小变化时重新调整图表大小
  window.addEventListener('resize', handleResize)
  
  // 监听分布类型变化
  watchEffect(async () => {
    await updateDistributionChart()
  })
})

// 加载中国地图数据
const loadChineseMap = async () => {
  try {
    // 通常需要从CDN或本地加载中国地图数据
    // 这里简化处理，实际使用时可能需要从public目录下加载
    await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
      .then(response => response.json())
      .then(data => {
        echarts.registerMap('china', { 
          geoJSON: data,
          specialAreas: {}
        })
      })
  } catch (error) {
    console.error('加载中国地图数据失败:', error)
  }
}

// 处理窗口大小变化
const handleResize = () => {
  mapChart?.resize()
  rankChart?.resize()
  distributionChart?.resize()
}

// 初始化地图图表
const initMapChart = async () => {
  if (!mapChartRef.value) return
  
  // 初始化图表实例
  mapChart = echarts.init(mapChartRef.value)
  
  // 设置加载中
  mapChart.showLoading()
  
  try {
    // 获取热力图数据
    const rawData = await getScenicHeatmap()
    const heatmapData = rawData.map(([province, count]) => ({ 
      name: String(province), 
      value: Number(count),
      a5Count: 0,
      a4Count: 0,
      a3Count: 0
    }))
    updateMapChart(heatmapData)
  } catch (error) {
    console.error('加载热力图数据失败:', error)
    
    // 使用模拟数据
    const mockData = [
      { name: '北京', value: 120, a5Count: 20, a4Count: 50, a3Count: 50 },
      { name: '天津', value: 80, a5Count: 15, a4Count: 35, a3Count: 30 },
      { name: '河北', value: 150, a5Count: 25, a4Count: 55, a3Count: 70 },
      { name: '山西', value: 110, a5Count: 18, a4Count: 42, a3Count: 50 },
      { name: '内蒙古', value: 90, a5Count: 12, a4Count: 38, a3Count: 40 },
      // 其他省份数据 ...
    ]
    
    updateMapChart(mockData)
  } finally {
    mapChart.hideLoading()
  }
}

// 更新地图图表
const updateMapChart = (data: {name: string, value: number, a5Count: number, a4Count: number, a3Count: number}[]) => {
  if (!mapChart) return
  
  // 准备地图数据
  const mapData = data.map(item => ({
    name: item.name,
    value: item.value
  }))
  
  // 设置图表选项
  const option = {
    title: {
      text: '全国景区分布热力图',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 个景区'
    },
    visualMap: {
      min: 0,
      max: Math.max(...mapData.map(item => item.value)),
      left: 'left',
      top: 'bottom',
      text: ['高', '低'],
      calculable: true,
      inRange: {
        color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
      }
    },
    series: [
      {
        name: '景区数量',
        type: 'map',
        map: 'china',
        roam: true,
        zoom: 1.2, // 初始缩放级别
        scaleLimit: {
          min: 1,
          max: 5
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 12
          },
          itemStyle: {
            areaColor: '#ff9933',
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        data: mapData
      }
    ]
  }
  
  mapChart.setOption(option)
}

// 初始化排名图表
const initRankChart = async () => {
  if (!rankChartRef.value) return
  
  // 初始化图表实例
  rankChart = echarts.init(rankChartRef.value)
  
  // 设置加载中
  rankChart.showLoading()
  
  try {
    // 获取热力图数据(复用热力图数据)
    const rawRankData = await getScenicHeatmap()
    const rankData = rawRankData.map(([province, count]) => ({ 
      name: String(province), 
      value: Number(count),
      a5Count: 0,
      a4Count: 0,
      a3Count: 0
    }))
    updateRankChart(rankData)
  } catch (error) {
    console.error('加载排名数据失败:', error)
    
    // 使用模拟数据
    const mockData = [
      { name: '北京', value: 120, a5Count: 30, a4Count: 40, a3Count: 50 },
      { name: '天津', value: 80, a5Count: 10, a4Count: 30, a3Count: 40 },
      // ... 更多省份数据 ...
    ]
    
    updateRankChart(mockData)
  } finally {
    rankChart.hideLoading()
  }
}

// 更新排名图表
const updateRankChart = (data: {name: string, value: number, a5Count: number, a4Count: number, a3Count: number}[]) => {
  if (!rankChart) return
  
  // 准备排名数据
  const sortedData = [...data].sort((a, b) => b.value - a.value).slice(0, 15)
  const provinces = sortedData.map(item => item.name)
  const counts = sortedData.map(item => item.value)
  
  // 设置图表选项
  const option = {
    title: {
      text: '各省景区数量排名(前15)',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '景区数量'
    },
    yAxis: {
      type: 'category',
      data: provinces.reverse(),
      axisLabel: {
        interval: 0,
        rotate: 0
      }
    },
    series: [
      {
        name: '景区数量',
        type: 'bar',
        data: counts.reverse(),
        itemStyle: {
          color: function(params: any) {
            const colorList = [
              '#c23531', '#2f4554', '#61a0a8', '#d48265', '#91c7ae',
              '#749f83', '#ca8622', '#bda29a', '#6e7074', '#546570',
              '#c4ccd3', '#4ECDC4', '#FF6B6B', '#2E73B3', '#92BFCD'
            ]
            return colorList[params.dataIndex % colorList.length]
          }
        }
      }
    ]
  }
  
  rankChart.setOption(option)
}

// 初始化分布图表
const initDistributionChart = async () => {
  if (!distributionChartRef.value) return
  
  // 初始化图表实例
  distributionChart = echarts.init(distributionChartRef.value)
  
  // 设置加载中
  distributionChart.showLoading()
  
  await updateDistributionChart()
}

// 更新分布图表
const updateDistributionChart = async () => {
  if (!distributionChart) return
  
  distributionChart.showLoading()
  
  try {
    // 获取分布数据
    const distributionData = await getScenicDistribution()
    
    // 根据不同类型设置图表
    if (currentDistributionType.value === 'level') {
      updateLevelDistribution(distributionData.levelDistribution)
    } else {
      updateSpecialDistribution(distributionData.levelDistribution)
    }
  } catch (error) {
    console.error('加载分布数据失败:', error)
    
    // 使用模拟数据
    const mockData: DistributionStatistics = {
      provinceData: [
        { name: '北京', value: 120, a5Count: 20, a4Count: 50, a3Count: 50 },
        { name: '上海', value: 100, a5Count: 15, a4Count: 45, a3Count: 40 }
      ],
      levelDistribution: currentDistributionType.value === 'level' 
        ? [
            { name: '5A', value: 302 },
            { name: '4A', value: 688 },
            { name: '3A', value: 1245 },
            { name: '2A', value: 876 },
            { name: '其他', value: 451 }
          ]
        : [
            { name: '国家级', value: 240 },
            { name: '省级', value: 380 },
            { name: '市级', value: 560 },
            { name: '县级', value: 720 },
            { name: '其他', value: 170 }
          ]
    }
    
    if (currentDistributionType.value === 'level') {
      updateLevelDistribution(mockData.levelDistribution)
    } else {
      updateSpecialDistribution(mockData.levelDistribution)
    }
  } finally {
    distributionChart.hideLoading()
  }
}

// 更新级别分布
const updateLevelDistribution = (data: {name: string, value: number}[]) => {
  if (!distributionChart) return
  
  // 准备数据
  const pieData = data.map(item => ({
    name: item.name,
    value: item.value
  }))
  
  // 设置图表选项
  const option = {
    title: {
      text: '景区级别分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [
      {
        name: '景区级别',
        type: 'pie',
        radius: '60%',
        center: ['50%', '50%'],
        data: pieData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  distributionChart.setOption(option)
}

// 更新特殊身份分布
const updateSpecialDistribution = (data: {name: string, value: number}[]) => {
  if (!distributionChart) return
  
  // 准备数据
  const categories = data.map(item => item.name)
  const values = data.map(item => item.value)
  
  // 设置图表选项
  const option = {
    title: {
      text: getDistributionTitle(),
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '景区数量'
    },
    series: [
      {
        name: '景区数量',
        type: 'bar',
        data: values,
        itemStyle: {
          color: function(params: any) {
            const colorList = [
              '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'
            ]
            return colorList[params.dataIndex % colorList.length]
          }
        }
      }
    ]
  }
  
  distributionChart.setOption(option)
}

// 获取分布类型标题
const getDistributionTitle = () => {
  const titleMap: Record<string, string> = {
    'level': '景区级别分布',
    'natureReserve': '自然保护区级别分布',
    'forestPark': '森林公园级别分布',
    'geologicalPark': '地质公园级别分布',
    'culturalRelic': '文物保护单位级别分布'
  }
  
  return titleMap[currentDistributionType.value] || '景区特殊身份分布'
}

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.geographic-container {
  padding: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.card-header .el-icon {
  margin-left: 8px;
  color: #909399;
  cursor: pointer;
}

.map-container {
  height: 700px;
  width: 100%;
}

.chart-container {
  height: 400px;
  width: 100%;
}
</style> 