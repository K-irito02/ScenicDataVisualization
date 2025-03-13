<template>
  <div class="traffic-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区交通方式分布</span>
              <el-tooltip content="展示各种交通方式在景区中的分布比例">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="chart-container" ref="trafficPieRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>交通方式组合分析</span>
              <el-tooltip content="展示景区支持的交通方式组合情况">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="chart-container" ref="trafficComboRef"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getTrafficAnalysis } from '@/api/scenic'
import type { TrafficAnalysis } from '@/types/scenic'
import { InfoFilled } from '@element-plus/icons-vue'

// 图表实例
let trafficPieChart: echarts.ECharts | null = null
let trafficComboChart: echarts.ECharts | null = null

// DOM引用
const trafficPieRef = ref<HTMLElement | null>(null)
const trafficComboRef = ref<HTMLElement | null>(null)

// 初始化图表
onMounted(async () => {
  await initTrafficPieChart()
  await initTrafficComboChart()
  
  // 窗口大小变化时重新调整图表大小
  window.addEventListener('resize', handleResize)
})

// 处理窗口大小变化
const handleResize = () => {
  trafficPieChart?.resize()
  trafficComboChart?.resize()
}

// 初始化交通方式饼图
const initTrafficPieChart = async () => {
  if (!trafficPieRef.value) return
  
  // 初始化图表实例
  trafficPieChart = echarts.init(trafficPieRef.value)
  
  // 设置加载中
  trafficPieChart.showLoading()
  
  try {
    // 获取交通分析数据
    const trafficData = await getTrafficAnalysis()
    updateTrafficPieChart(trafficData)
  } catch (error) {
    console.error('加载交通分析数据失败:', error)
    
    // 使用模拟数据
    const mockData: TrafficAnalysis = {
      methodsCount: {
        '公交': 150,
        '地铁': 120,
        '出租车': 100,
        '自驾': 200,
        '旅游大巴': 80,
        '火车': 90,
        '飞机': 60
      },
      sentimentByTrafficCount: [
        { methodsCount: 1, positive: 30, neutral: 50, negative: 20, mainMethod: '自驾' },
        { methodsCount: 2, positive: 45, neutral: 40, negative: 15, mainMethod: '公交+出租车' },
        { methodsCount: 3, positive: 60, neutral: 30, negative: 10, mainMethod: '地铁+公交+出租车' },
        { methodsCount: 4, positive: 70, neutral: 25, negative: 5, mainMethod: '地铁+公交+出租车+自驾' },
        { methodsCount: 5, positive: 80, neutral: 15, negative: 5, mainMethod: '全部交通方式' }
      ]
    }
    
    updateTrafficPieChart(mockData)
  } finally {
    trafficPieChart.hideLoading()
  }
}

// 更新交通方式饼图
const updateTrafficPieChart = (data: TrafficAnalysis) => {
  if (!trafficPieChart) return
  
  const { methodsCount } = data
  
  // 准备数据
  const pieData = Object.entries(methodsCount).map(([name, value]) => ({
    name,
    value
  }))
  
  // 设置图表选项
  const option = {
    title: {
      text: '景区交通方式分布',
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
        name: '交通方式',
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
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: pieData
      }
    ]
  }
  
  trafficPieChart.setOption(option)
}

// 初始化交通方式组合图
const initTrafficComboChart = async () => {
  if (!trafficComboRef.value) return
  
  // 初始化图表实例
  trafficComboChart = echarts.init(trafficComboRef.value)
  
  // 设置加载中
  trafficComboChart.showLoading()
  
  try {
    // 获取交通分析数据
    const trafficData = await getTrafficAnalysis()
    updateTrafficComboChart(trafficData)
  } catch (error) {
    console.error('加载交通组合数据失败:', error)
    
    // 使用模拟数据
    const mockData: TrafficAnalysis = {
      methodsCount: {
        '公交': 150,
        '地铁': 120,
        '出租车': 100,
        '自驾': 200,
        '旅游大巴': 80,
        '火车': 90,
        '飞机': 60
      },
      sentimentByTrafficCount: [
        { methodsCount: 1, positive: 30, neutral: 50, negative: 20, mainMethod: '自驾' },
        { methodsCount: 2, positive: 45, neutral: 40, negative: 15, mainMethod: '公交+出租车' },
        { methodsCount: 3, positive: 60, neutral: 30, negative: 10, mainMethod: '地铁+公交+出租车' },
        { methodsCount: 4, positive: 70, neutral: 25, negative: 5, mainMethod: '地铁+公交+出租车+自驾' },
        { methodsCount: 5, positive: 80, neutral: 15, negative: 5, mainMethod: '全部交通方式' }
      ]
    }
    
    updateTrafficComboChart(mockData)
  } finally {
    trafficComboChart.hideLoading()
  }
}

// 更新交通方式组合图
const updateTrafficComboChart = (data: TrafficAnalysis) => {
  if (!trafficComboChart) return
  
  const { sentimentByTrafficCount } = data
  
  // 准备数据
  const xAxisData = sentimentByTrafficCount.map(item => `${item.methodsCount}种`)
  const barData = sentimentByTrafficCount.map(item => item.methodsCount * 20) // 模拟景区数量
  const mainMethods = sentimentByTrafficCount.map(item => item.mainMethod || '')
  
  // 设置图表选项
  const option = {
    title: {
      text: '景区交通方式组合分析',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function (params: any) {
        const index = params[0].dataIndex
        return `
          <div>交通方式数量: ${sentimentByTrafficCount[index].methodsCount}种</div>
          <div>主要组合: ${mainMethods[index]}</div>
          <div>景区数量: ${barData[index]}</div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLabel: {
        interval: 0,
        rotate: 0
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
        barWidth: '60%',
        data: barData.map((value, index) => ({
          value,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          },
          label: {
            show: true,
            position: 'top',
            formatter: mainMethods[index]
          }
        }))
      }
    ]
  }
  
  trafficComboChart.setOption(option)
}
</script>

<style scoped>
.traffic-container {
  padding: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-header .el-icon {
  margin-left: 8px;
  color: #909399;
  cursor: pointer;
}

.chart-container {
  height: 400px;
  width: 100%;
}
</style> 