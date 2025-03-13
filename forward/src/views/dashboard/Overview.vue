<template>
  <div class="overview-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <h2>欢迎使用全国景区数据可视化系统</h2>
          <p>本系统提供了全国范围内的景区数据分析和可视化功能，帮助您全面了解景区分布和特征。</p>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6" v-for="(card, index) in dataCards" :key="index">
        <el-card class="data-card" shadow="hover">
          <div class="card-icon" :style="{ backgroundColor: card.color }">
            <el-icon><component :is="card.icon" /></el-icon>
          </div>
          <div class="card-content">
            <div class="card-title">{{ card.title }}</div>
            <div class="card-value">{{ card.value }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区级别分布</span>
            </div>
          </template>
          <div class="chart-container" ref="levelChartRef"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区门票价格分布</span>
            </div>
          </template>
          <div class="chart-container" ref="priceChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>近期热门景区</span>
            </div>
          </template>
          <el-table :data="hotSpots" style="width: 100%">
            <el-table-column prop="rank" label="排名" width="80" />
            <el-table-column prop="name" label="景区名称" />
            <el-table-column prop="level" label="级别">
              <template #default="scope">
                <el-tag :type="getLevelType(scope.row.level)">{{ scope.row.level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="location" label="位置" />
            <el-table-column prop="popularity" label="热度">
              <template #default="scope">
                <el-progress 
                  :percentage="scope.row.popularity" 
                  :color="getPopularityColor(scope.row.popularity)"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

// 数据卡片信息
const dataCards = [
  {
    title: '景区总数',
    value: '3,562',
    icon: 'MapLocation',
    color: '#409EFF'
  },
  {
    title: '5A景区',
    value: '302',
    icon: 'Trophy',
    color: '#67C23A'
  },
  {
    title: '平均票价',
    value: '¥126',
    icon: 'Tickets',
    color: '#E6A23C'
  },
  {
    title: '本月访问量',
    value: '12,658',
    icon: 'DataLine',
    color: '#F56C6C'
  }
]

// 图表引用
const levelChartRef = ref<HTMLElement | null>(null)
const priceChartRef = ref<HTMLElement | null>(null)

// 热门景区数据
const hotSpots = [
  { rank: 1, name: '故宫博物院', level: '5A', location: '北京市东城区', popularity: 98 },
  { rank: 2, name: '黄山风景区', level: '5A', location: '安徽省黄山市', popularity: 95 },
  { rank: 3, name: '长城', level: '5A', location: '北京市延庆区', popularity: 92 },
  { rank: 4, name: '桂林山水', level: '5A', location: '广西桂林市', popularity: 89 },
  { rank: 5, name: '西湖风景区', level: '5A', location: '浙江省杭州市', popularity: 86 },
  { rank: 6, name: '九寨沟风景区', level: '5A', location: '四川省阿坝州', popularity: 82 },
  { rank: 7, name: '乐山大佛', level: '5A', location: '四川省乐山市', popularity: 79 },
  { rank: 8, name: '张家界国家森林公园', level: '5A', location: '湖南省张家界市', popularity: 76 }
]

// 初始化图表
onMounted(() => {
  initLevelChart()
  initPriceChart()
})

// 初始化景区级别分布图表
const initLevelChart = () => {
  if (!levelChartRef.value) return
  
  const levelChart = echarts.init(levelChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '景区级别',
        type: 'pie',
        radius: '75%',
        data: [
          { value: 302, name: '5A级' },
          { value: 688, name: '4A级' },
          { value: 1245, name: '3A级' },
          { value: 876, name: '2A级' },
          { value: 451, name: '其他' }
        ],
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
  
  levelChart.setOption(option)
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    levelChart.resize()
  })
}

// 初始化景区门票价格分布图表
const initPriceChart = () => {
  if (!priceChartRef.value) return
  
  const priceChart = echarts.init(priceChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: ['0-50', '51-100', '101-150', '151-200', '201-300', '301+'],
      axisTick: {
        alignWithLabel: true
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
        data: [
          { value: 742, itemStyle: { color: '#91cc75' } },
          { value: 968, itemStyle: { color: '#5470c6' } },
          { value: 853, itemStyle: { color: '#fac858' } },
          { value: 521, itemStyle: { color: '#ee6666' } },
          { value: 324, itemStyle: { color: '#73c0de' } },
          { value: 154, itemStyle: { color: '#3ba272' } }
        ]
      }
    ]
  }
  
  priceChart.setOption(option)
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    priceChart.resize()
  })
}

// 获取景区级别标签类型
const getLevelType = (level: string) => {
  const typeMap: Record<string, string> = {
    '5A': 'danger',
    '4A': 'warning',
    '3A': 'success',
    '2A': 'info',
    '1A': 'info'
  }
  
  return typeMap[level] || ''
}

// 获取热度颜色
const getPopularityColor = (popularity: number) => {
  if (popularity >= 90) return '#F56C6C'
  if (popularity >= 80) return '#E6A23C'
  if (popularity >= 70) return '#67C23A'
  return '#909399'
}
</script>

<style scoped>
.overview-container {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
  text-align: center;
  padding: 20px;
}

.welcome-card h2 {
  margin-top: 0;
  color: #303133;
}

.welcome-card p {
  color: #606266;
  margin-bottom: 0;
}

.data-card {
  height: 100px;
  display: flex;
  align-items: center;
  padding: 20px;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 15px;
}

.card-icon .el-icon {
  font-size: 30px;
  color: white;
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
  width: 100%;
}
</style> 