<script setup lang="ts">
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { useScenicStore } from '@/stores/scenic'
import * as echarts from 'echarts'
import 'echarts/extension/bmap/bmap'
import chinaJson from '@/assets/geo/china.json'
import { ElMessage } from 'element-plus'

// 使用类型断言解决类型不匹配问题
echarts.registerMap('china', chinaJson as any)

const scenicStore = useScenicStore()
const loading = ref(false)
const mapChart = ref<HTMLElement | null>(null)
const barChart = ref<HTMLElement | null>(null)
const provinceMapChart = ref<HTMLElement | null>(null)
const mapChartInstance = ref<echarts.ECharts | null>(null)
const barChartInstance = ref<echarts.ECharts | null>(null)
const provinceMapChartInstance = ref<echarts.ECharts | null>(null)
const showProvinceMap = ref(false)
const currentProvince = ref('')

// 初始化地图
const initMapChart = () => {
  if (!mapChart.value) return
  
  mapChartInstance.value = echarts.init(mapChart.value)
  
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
      max: 300,
      left: 'left',
      top: 'bottom',
      text: ['高','低'],
      calculable: true,
      inRange: {
        color: ['#e0f3f8', '#iceef6', '#abd9e9', '#74add1', '#4575b4', '#313695']
      }
    },
    series: [
      {
        name: '景区数量',
        type: 'map',
        map: 'china',
        roam: true,
        emphasis: {
          label: {
            show: true
          }
        },
        data: []
      }
    ]
  }
  
  mapChartInstance.value.setOption(option)
  
  // 点击事件
  mapChartInstance.value.on('click', (params) => {
    if (params.componentType === 'series') {
      const provinceName = params.name
      showProvinceDetail(provinceName)
    }
  })
}

// 初始化柱状图
const initBarChart = () => {
  if (!barChart.value) return
  
  barChartInstance.value = echarts.init(barChart.value)
  
  const option = {
    title: {
      text: '省份景区数量统计',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '{b}: {c} 个景区'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [],
      axisLabel: {
        interval: 0,
        rotate: 45
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
        data: []
      }
    ]
  }
  
  barChartInstance.value.setOption(option)
  
  // 点击事件
  barChartInstance.value.on('click', (params) => {
    const provinceName = params.name
    showProvinceDetail(provinceName)
  })
}

// 初始化省份地图
const initProvinceMap = (provinceName: string, scenics: any[]) => {
  if (!provinceMapChart.value) return
  
  if (!provinceMapChartInstance.value) {
    provinceMapChartInstance.value = echarts.init(provinceMapChart.value)
  }
  
  // 获取省份地图JSON数据（这里假设已经在静态资源中准备好了省份地图数据）
  // 实际情况可能需要动态加载或者从服务器获取
  import(`@/assets/province/${provinceName}.json`).then(provinceJson => {
    echarts.registerMap(provinceName, provinceJson.default)
    
    const data = scenics.map(item => ({
      name: item.name,
      value: [item.longitude, item.latitude, 1],
      scenicId: item.id
    }))
    
    const option = {
      title: {
        text: `${provinceName}景区分布`,
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          return params.data.name
        }
      },
      geo: {
        map: provinceName,
        roam: true,
        emphasis: {
          label: {
            show: true
          }
        }
      },
      series: [
        {
          name: '景区',
          type: 'scatter',
          coordinateSystem: 'geo',
          data: data,
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
    
    provinceMapChartInstance.value?.setOption(option)
  }).catch(error => {
    console.error(`加载${provinceName}地图数据失败:`, error)
    ElMessage.error(`加载${provinceName}地图数据失败`)
  })
}

// 显示省份详情
const showProvinceDetail = (provinceName: string) => {
  const province = scenicStore.provinceData.find(item => item.name === provinceName)
  
  if (province && province.scenics) {
    currentProvince.value = provinceName
    showProvinceMap.value = true
    
    // 更新柱状图高亮
    if (barChartInstance.value) {
      const option = barChartInstance.value.getOption()
      // 使用类型断言解决类型未知问题
      const seriesData = (option as any).series[0].data
      
      const newData = seriesData.map((item: any) => {
        if (item.name === provinceName) {
          return {
            ...item,
            itemStyle: {
              color: '#FF4500'
            }
          }
        }
        return item
      })
      
      barChartInstance.value.setOption({
        series: [
          {
            data: newData
          }
        ]
      })
    }
    
    nextTick(() => {
      initProvinceMap(provinceName, province.scenics || [])
    })
  }
}

// 返回全国地图
const backToChina = () => {
  showProvinceMap.value = false
  currentProvince.value = ''
  
  // 重置柱状图高亮
  if (barChartInstance.value) {
    updateCharts()
  }
}

// 更新图表数据
const updateCharts = () => {
  if (!mapChartInstance.value || !barChartInstance.value) return
  
  const provinces = scenicStore.provinceData
  
  // 更新地图数据
  mapChartInstance.value.setOption({
    series: [
      {
        data: provinces.map(item => ({
          name: item.name,
          value: item.value
        }))
      }
    ]
  })
  
  // 更新柱状图数据
  barChartInstance.value.setOption({
    xAxis: {
      data: provinces.map(item => item.name)
    },
    series: [
      {
        data: provinces.map(item => ({
          name: item.name,
          value: item.value
        }))
      }
    ]
  })
}

// 窗口大小改变时重新调整图表大小
const handleResize = () => {
  mapChartInstance.value?.resize()
  barChartInstance.value?.resize()
  provinceMapChartInstance.value?.resize()
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    await scenicStore.getProvinceData()
    nextTick(() => {
      initMapChart()
      initBarChart()
      updateCharts()
    })
  } catch (error) {
    console.error('获取景区分布数据失败:', error)
    ElMessage.error('获取景区分布数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  mapChartInstance.value?.dispose()
  barChartInstance.value?.dispose()
  provinceMapChartInstance.value?.dispose()
})
</script>

<template>
  <div class="scenic-distribution-container">
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>景区基础分布分析</span>
          <el-button v-if="showProvinceMap" @click="backToChina" type="primary" size="small">
            返回全国地图
          </el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="24">
          <div class="map-container" ref="mapChart" v-show="!showProvinceMap"></div>
          <div class="province-map-container" ref="provinceMapChart" v-show="showProvinceMap"></div>
        </el-col>
        <el-col :span="24" class="mt-20">
          <div class="bar-container" ref="barChart"></div>
        </el-col>
      </el-row>
      
      <el-empty v-if="loading" description="加载中...">
        <template #image>
          <el-icon class="loading-icon"><loading /></el-icon>
        </template>
      </el-empty>
    </el-card>
  </div>
</template>

<style scoped>
.scenic-distribution-container {
  height: 100%;
}

.chart-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.map-container, .province-map-container {
  height: 500px;
  width: 100%;
}

.bar-container {
  height: 400px;
  width: 100%;
}

.mt-20 {
  margin-top: 20px;
}

.loading-icon {
  font-size: 32px;
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style> 