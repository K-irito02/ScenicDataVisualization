<template>
  <div class="identity-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区多重身份交叉分析</span>
              <el-tooltip content="展示景区多重身份的交叉关系，如既是5A景区又是国家级自然保护区的景区数量">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="chart-container" ref="identityChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区身份关系网络图</span>
              <el-tooltip content="展示不同景区身份之间的关联强度，连线越粗表示关联越强">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="chart-container" ref="relationChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getIdentityAnalysis } from '@/api/scenic'
import { InfoFilled } from '@element-plus/icons-vue'

// 图表实例
let identityChart: echarts.ECharts | null = null
let relationChart: echarts.ECharts | null = null

// DOM引用
const identityChartRef = ref<HTMLElement | null>(null)
const relationChartRef = ref<HTMLElement | null>(null)

// 初始化图表
onMounted(async () => {
  await initIdentityChart()
  await initRelationChart()
  
  // 窗口大小变化时重新调整图表大小
  window.addEventListener('resize', handleResize)
})

// 当组件销毁时移除事件监听器
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  // 销毁图表实例以释放内存
  identityChart?.dispose()
  relationChart?.dispose()
})

// 处理窗口大小变化
const handleResize = () => {
  if (identityChart) {
    identityChart.resize()
  }
  if (relationChart) {
    relationChart.resize()
  }
}

// 初始化身份交叉图
const initIdentityChart = async () => {
  if (!identityChartRef.value) return
  
  // 初始化图表实例
  identityChart = echarts.init(identityChartRef.value)
  
  // 设置加载中
  identityChart.showLoading()
  
  try {
    // 获取身份分析数据
    const identityData = await getIdentityAnalysis()
    updateIdentityChart(identityData.sets)
  } catch (error) {
    console.error('加载身份分析数据失败:', error)
    
    // 使用模拟数据
    const mockData = [
      { name: '5A景区', value: 588 },
      { name: '国家级自然保护区', value: 224 },
      { name: '国家级森林公园', value: 441 },
      { name: '国家级地质公园', value: 193 },
      { name: '国家级水利风景区', value: 219 },
      { name: '国家级文物保护单位', value: 831 },
      { name: '国家级湿地公园', value: 87 },
      { name: '国家级博物馆', value: 306 },
      { name: '5A景区 ∩ 国家级自然保护区', value: 45 },
      { name: '5A景区 ∩ 国家级森林公园', value: 78 },
      { name: '5A景区 ∩ 国家级地质公园', value: 52 },
      { name: '国家级自然保护区 ∩ 国家级森林公园', value: 65 },
      { name: '国家级自然保护区 ∩ 国家级地质公园', value: 38 },
      { name: '国家级森林公园 ∩ 国家级地质公园', value: 42 },
      { name: '5A景区 ∩ 国家级自然保护区 ∩ 国家级森林公园', value: 25 },
      { name: '5A景区 ∩ 国家级自然保护区 ∩ 国家级地质公园', value: 18 },
      { name: '5A景区 ∩ 国家级森林公园 ∩ 国家级地质公园', value: 22 },
      { name: '国家级自然保护区 ∩ 国家级森林公园 ∩ 国家级地质公园', value: 15 },
      { name: '5A景区 ∩ 国家级自然保护区 ∩ 国家级森林公园 ∩ 国家级地质公园', value: 10 }
    ]
    
    updateIdentityChart(mockData)
  } finally {
    identityChart.hideLoading()
  }
}

// 更新身份交叉图
const updateIdentityChart = (data: { name: string, value: number }[]) => {
  if (!identityChart) return
  
  // 准备数据
  const seriesData = data.map(item => ({
    name: item.name,
    value: item.value
  }))
  
  // 设置图表选项
  const option = {
    title: {
      text: '景区多重身份交叉分析',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 个景区'
    },
    series: [
      {
        name: '景区身份',
        type: 'treemap',
        visibleMin: 1,
        data: seriesData,
        leafDepth: 1,
        levels: [
          {
            itemStyle: {
              borderColor: '#fff',
              borderWidth: 2,
              gapWidth: 2
            }
          },
          {
            colorSaturation: [0.3, 0.6],
            itemStyle: {
              borderColorSaturation: 0.7,
              gapWidth: 2,
              borderWidth: 2
            }
          }
        ]
      }
    ]
  }
  
  identityChart.setOption(option)
}

// 初始化关系网络图
const initRelationChart = async () => {
  if (!relationChartRef.value) return
  
  // 初始化图表实例
  relationChart = echarts.init(relationChartRef.value)
  
  // 设置加载中
  relationChart.showLoading()
  
  try {
    // 获取身份分析数据
    const identityData = await getIdentityAnalysis()
    updateRelationChart(identityData.relations)
  } catch (error) {
    console.error('加载身份关系数据失败:', error)
    
    // 使用模拟数据
    const mockData = [
      { source: '5A景区', target: '国家级自然保护区', value: 45 },
      { source: '5A景区', target: '国家级森林公园', value: 78 },
      { source: '5A景区', target: '国家级地质公园', value: 52 },
      { source: '5A景区', target: '国家级水利风景区', value: 35 },
      { source: '5A景区', target: '国家级文物保护单位', value: 120 },
      { source: '国家级自然保护区', target: '国家级森林公园', value: 65 },
      { source: '国家级自然保护区', target: '国家级地质公园', value: 38 },
      { source: '国家级自然保护区', target: '国家级水利风景区', value: 28 },
      { source: '国家级森林公园', target: '国家级地质公园', value: 42 },
      { source: '国家级森林公园', target: '国家级水利风景区', value: 32 },
      { source: '国家级地质公园', target: '国家级水利风景区', value: 25 },
      { source: '国家级文物保护单位', target: '国家级博物馆', value: 45 }
    ]
    
    updateRelationChart(mockData)
  } finally {
    relationChart.hideLoading()
  }
}

// 更新关系网络图
const updateRelationChart = (data: { source: string, target: string, value: number }[]) => {
  if (!relationChart) return
  
  // 提取所有唯一的节点
  const nodes = Array.from(
    new Set(
      data.reduce((acc: string[], curr) => {
        acc.push(curr.source, curr.target)
        return acc
      }, [])
    )
  ).map(name => ({ name }))
  
  // 准备连接数据
  const links = data.map(item => ({
    source: item.source,
    target: item.target,
    value: item.value
  }))
  
  // 设置图表选项
  const option = {
    title: {
      text: '景区身份关系网络',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: function (params: any) {
        if (params.dataType === 'edge') {
          return `${params.data.source} 与 ${params.data.target} 之间有 ${params.data.value} 个景区同时具备这两种身份`
        } else {
          return params.name
        }
      }
    },
    legend: {
      data: nodes.map(node => node.name),
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        name: '景区身份关系',
        type: 'graph',
        layout: 'force',
        data: nodes,
        links: links,
        roam: true,
        label: {
          show: true,
          position: 'right'
        },
        force: {
          repulsion: 100,
          edgeLength: [50, 200]
        },
        lineStyle: {
          width: function (params: any) {
            return Math.sqrt(params.data.value) / 2
          },
          curveness: 0.3,
          opacity: 0.7
        }
      }
    ]
  }
  
  relationChart.setOption(option)
}
</script>

<style scoped>
.identity-container {
  padding: 20px;
  width: 100%;
}

.chart-card {
  margin-bottom: 20px;
  width: 100%;
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
  height: 600px;
  width: 100%;
}
</style> 