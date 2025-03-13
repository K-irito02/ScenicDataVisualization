<template>
  <div class="attribute-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区等级与票价关联分析</span>
              <el-tooltip content="展示不同等级景区的票价分布情况">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="chart-container" ref="levelPriceRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区热度与属性关联</span>
              <el-tooltip content="展示景区热度与各种属性之间的关联性">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="chart-container" ref="attrHeatRef"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getAttributeAnalysis } from '@/api/scenic'
import type { AttributeAnalysis } from '@/types/scenic'
import { InfoFilled } from '@element-plus/icons-vue'

// 图表实例
let levelPriceChart: echarts.ECharts | null = null
let attrHeatChart: echarts.ECharts | null = null

// DOM引用
const levelPriceRef = ref<HTMLElement | null>(null)
const attrHeatRef = ref<HTMLElement | null>(null)

// 初始化图表
onMounted(async () => {
  await initLevelPriceChart()
  await initAttrHeatChart()
  
  // 窗口大小变化时重新调整图表大小
  window.addEventListener('resize', handleResize)
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  
  // 销毁图表实例
  levelPriceChart?.dispose()
  attrHeatChart?.dispose()
})

// 处理窗口大小变化
const handleResize = () => {
  levelPriceChart?.resize()
  attrHeatChart?.resize()
}

// 初始化等级-票价关联图表
const initLevelPriceChart = async () => {
  if (!levelPriceRef.value) return
  
  // 初始化图表实例
  levelPriceChart = echarts.init(levelPriceRef.value)
  
  // 设置加载中
  levelPriceChart.showLoading()
  
  try {
    // 获取属性分析数据
    const attrData = await getAttributeAnalysis()
    updateLevelPriceChart(attrData)
  } catch (error) {
    console.error('加载属性分析数据失败:', error)
    
    // 使用模拟数据
    const mockData: AttributeAnalysis = {
      levelPriceData: [
        { level: '5A', priceRange: '0-50', count: 5 },
        { level: '5A', priceRange: '51-100', count: 25 },
        { level: '5A', priceRange: '101-150', count: 40 },
        { level: '5A', priceRange: '151-200', count: 20 },
        { level: '5A', priceRange: '201+', count: 10 },
        
        { level: '4A', priceRange: '0-50', count: 30 },
        { level: '4A', priceRange: '51-100', count: 50 },
        { level: '4A', priceRange: '101-150', count: 30 },
        { level: '4A', priceRange: '151-200', count: 10 },
        { level: '4A', priceRange: '201+', count: 5 },
        
        { level: '3A', priceRange: '0-50', count: 60 },
        { level: '3A', priceRange: '51-100', count: 30 },
        { level: '3A', priceRange: '101-150', count: 15 },
        { level: '3A', priceRange: '151-200', count: 5 },
        { level: '3A', priceRange: '201+', count: 0 },
        
        { level: '其他', priceRange: '0-50', count: 80 },
        { level: '其他', priceRange: '51-100', count: 20 },
        { level: '其他', priceRange: '101-150', count: 5 },
        { level: '其他', priceRange: '151-200', count: 0 },
        { level: '其他', priceRange: '201+', count: 0 }
      ],
      attributeHeatData: [
        { name: '自然风光', value: [0, 0, 90] },
        { name: '人文历史', value: [0, 1, 80] },
        { name: '主题乐园', value: [0, 2, 75] },
        { name: '温泉度假', value: [0, 3, 45] },
        { name: '海滨沙滩', value: [0, 4, 65] },
        
        { name: '自然风光', value: [1, 0, 85] },
        { name: '人文历史', value: [1, 1, 70] },
        { name: '主题乐园', value: [1, 2, 60] },
        { name: '温泉度假', value: [1, 3, 55] },
        { name: '海滨沙滩', value: [1, 4, 50] },
        
        { name: '自然风光', value: [2, 0, 70] },
        { name: '人文历史', value: [2, 1, 80] },
        { name: '主题乐园', value: [2, 2, 90] },
        { name: '温泉度假', value: [2, 3, 65] },
        { name: '海滨沙滩', value: [2, 4, 40] },
        
        { name: '自然风光', value: [3, 0, 50] },
        { name: '人文历史', value: [3, 1, 60] },
        { name: '主题乐园', value: [3, 2, 75] },
        { name: '温泉度假', value: [3, 3, 85] },
        { name: '海滨沙滩', value: [3, 4, 60] }
      ]
    }
    
    updateLevelPriceChart(mockData)
  } finally {
    levelPriceChart.hideLoading()
  }
}

// 更新等级-票价关联图表
const updateLevelPriceChart = (data: AttributeAnalysis) => {
  if (!levelPriceChart) return
  
  const { levelPriceData } = data
  
  // 准备数据
  const levels = Array.from(new Set(levelPriceData.map(item => item.level)))
  const priceRanges = Array.from(new Set(levelPriceData.map(item => item.priceRange)))
  
  // 生成系列数据
  const series = levels.map(level => {
    const data = priceRanges.map(price => {
      const item = levelPriceData.find(d => d.level === level && d.priceRange === price)
      return item ? item.count : 0
    })
    
    return {
      name: level,
      type: 'bar',
      stack: 'total',
      emphasis: {
        focus: 'series'
      },
      data: data
    }
  })
  
  // 设置图表选项
  const option = {
    title: {
      text: '景区等级与票价分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: levels,
      top: 'bottom'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: priceRanges,
      name: '票价范围(元)'
    },
    yAxis: {
      type: 'value',
      name: '景区数量'
    },
    series: series
  }
  
  levelPriceChart.setOption(option)
}

// 初始化属性-热度关联图表
const initAttrHeatChart = async () => {
  if (!attrHeatRef.value) return
  
  // 初始化图表实例
  attrHeatChart = echarts.init(attrHeatRef.value)
  
  // 设置加载中
  attrHeatChart.showLoading()
  
  try {
    // 获取属性分析数据
    const attrData = await getAttributeAnalysis()
    updateAttrHeatChart(attrData)
  } catch (error) {
    console.error('加载属性热度数据失败:', error)
    
    // 使用模拟数据(与之前相同)
    const mockData: AttributeAnalysis = {
      levelPriceData: [
        { level: '5A', priceRange: '0-50', count: 5 },
        { level: '5A', priceRange: '51-100', count: 25 },
        { level: '5A', priceRange: '101-150', count: 40 },
        { level: '5A', priceRange: '151-200', count: 20 },
        { level: '5A', priceRange: '201+', count: 10 },
        
        { level: '4A', priceRange: '0-50', count: 30 },
        { level: '4A', priceRange: '51-100', count: 50 },
        { level: '4A', priceRange: '101-150', count: 30 },
        { level: '4A', priceRange: '151-200', count: 10 },
        { level: '4A', priceRange: '201+', count: 5 },
        
        { level: '3A', priceRange: '0-50', count: 60 },
        { level: '3A', priceRange: '51-100', count: 30 },
        { level: '3A', priceRange: '101-150', count: 15 },
        { level: '3A', priceRange: '151-200', count: 5 },
        { level: '3A', priceRange: '201+', count: 0 },
        
        { level: '其他', priceRange: '0-50', count: 80 },
        { level: '其他', priceRange: '51-100', count: 20 },
        { level: '其他', priceRange: '101-150', count: 5 },
        { level: '其他', priceRange: '151-200', count: 0 },
        { level: '其他', priceRange: '201+', count: 0 }
      ],
      attributeHeatData: [
        { name: '自然风光', value: [0, 0, 90] },
        { name: '人文历史', value: [0, 1, 80] },
        { name: '主题乐园', value: [0, 2, 75] },
        { name: '温泉度假', value: [0, 3, 45] },
        { name: '海滨沙滩', value: [0, 4, 65] },
        
        { name: '自然风光', value: [1, 0, 85] },
        { name: '人文历史', value: [1, 1, 70] },
        { name: '主题乐园', value: [1, 2, 60] },
        { name: '温泉度假', value: [1, 3, 55] },
        { name: '海滨沙滩', value: [1, 4, 50] },
        
        { name: '自然风光', value: [2, 0, 70] },
        { name: '人文历史', value: [2, 1, 80] },
        { name: '主题乐园', value: [2, 2, 90] },
        { name: '温泉度假', value: [2, 3, 65] },
        { name: '海滨沙滩', value: [2, 4, 40] },
        
        { name: '自然风光', value: [3, 0, 50] },
        { name: '人文历史', value: [3, 1, 60] },
        { name: '主题乐园', value: [3, 2, 75] },
        { name: '温泉度假', value: [3, 3, 85] },
        { name: '海滨沙滩', value: [3, 4, 60] }
      ]
    }
    
    updateAttrHeatChart(mockData)
  } finally {
    attrHeatChart.hideLoading()
  }
}

// 更新属性-热度关联图表
const updateAttrHeatChart = (data: AttributeAnalysis) => {
  if (!attrHeatChart) return
  
  const { attributeHeatData } = data
  
  // 提取热度指标和属性类型
  const heatFactors = ['访问量', '停留时间', '社交分享', '评分']
  const attrTypes = ['自然风光', '人文历史', '主题乐园', '温泉度假', '海滨沙滩']
  
  // 设置图表选项
  const option = {
    title: {
      text: '景区属性与热度关联分析',
      left: 'center'
    },
    tooltip: {
      position: 'top',
      formatter: function (params: any) {
        return `${heatFactors[params.value[0]]} - ${attrTypes[params.value[1]]}: ${params.value[2]}`
      }
    },
    grid: {
      left: 35,
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: attrTypes,
      splitArea: {
        show: true
      },
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'category',
      data: heatFactors,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: 0,
      max: 100,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      text: ['高', '低'],
      inRange: {
        color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
      }
    },
    series: [
      {
        name: '热度关联',
        type: 'heatmap',
        data: attributeHeatData.map(item => item.value),
        label: {
          show: true
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  attrHeatChart.setOption(option)
}
</script>

<style scoped>
.attribute-container {
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