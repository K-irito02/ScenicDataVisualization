<template>
  <div class="classification-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <h2>景区等级与分类分析</h2>
          <p>本模块提供全国景区不同类型等级的分布与分析，包括森林公园、地质公园、博物馆等不同类型资源的等级分布。</p>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>多类型等级对比</span>
              <el-radio-group v-model="categoryType" size="small">
                <el-radio-button label="nature">自然保护</el-radio-button>
                <el-radio-button label="culture">文化遗产</el-radio-button>
                <el-radio-button label="all">全部分类</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="categoryChartRef"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>文物保护单位词云</span>
              <el-select v-model="wordcloudWeight" placeholder="权重类型" size="small">
                <el-option label="按年代" value="age"></el-option>
                <el-option label="按保护等级" value="level"></el-option>
                <el-option label="按访问量" value="visits"></el-option>
              </el-select>
            </div>
          </template>
          <div class="chart-container" ref="wordCloudChartRef"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>不同类型景区对比</span>
            </div>
          </template>
          <div class="chart-container" ref="radarChartRef"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区分类趋势</span>
              <el-select v-model="trendYear" placeholder="选择年份" size="small">
                <el-option label="2021年" value="2021"></el-option>
                <el-option label="2022年" value="2022"></el-option>
                <el-option label="2023年" value="2023"></el-option>
                <el-option label="全部" value="all"></el-option>
              </el-select>
            </div>
          </template>
          <div class="chart-container" ref="trendChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'

// 分类类型
const categoryType = ref('all')
// 词云权重类型
const wordcloudWeight = ref('level')
// 趋势年份
const trendYear = ref('all')

// 图表引用
const categoryChartRef = ref<HTMLElement | null>(null)
const wordCloudChartRef = ref<HTMLElement | null>(null)
const radarChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)

// 图表实例
let categoryChart: echarts.ECharts | null = null
let wordCloudChart: echarts.ECharts | null = null
let radarChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// 监听类型变化
watch(categoryType, () => {
  nextTick(() => {
    updateCategoryChart()
  })
})

// 监听词云权重变化
watch(wordcloudWeight, () => {
  nextTick(() => {
    updateWordCloudChart()
  })
})

// 监听趋势年份变化
watch(trendYear, () => {
  nextTick(() => {
    updateTrendChart()
  })
})

// 初始化图表
onMounted(() => {
  initCharts()
  
  // 监听窗口大小变化
  window.addEventListener('resize', resizeCharts)
})

// 初始化所有图表
const initCharts = () => {
  initCategoryChart()
  initWordCloudChart()
  initRadarChart()
  initTrendChart()
}

// 重置图表大小
const resizeCharts = () => {
  categoryChart?.resize()
  wordCloudChart?.resize()
  radarChart?.resize()
  trendChart?.resize()
}

// 初始化多类型等级对比图
const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  
  categoryChart = echarts.init(categoryChartRef.value)
  updateCategoryChart()
}

// 更新多类型等级对比图
const updateCategoryChart = () => {
  if (!categoryChart) return
  
  let categories: string[] = []
  let series: any[] = []
  
  if (categoryType.value === 'nature' || categoryType.value === 'all') {
    categories = [...categories, '森林公园', '地质公园', '自然保护区', '湿地公园']
    
    series.push({
      name: '国家级',
      type: 'bar',
      stack: 'total',
      emphasis: { focus: 'series' },
      data: [128, 92, 104, 83],
      itemStyle: { color: '#5470c6' }
    })
    
    series.push({
      name: '省级',
      type: 'bar',
      stack: 'total',
      emphasis: { focus: 'series' },
      data: [234, 187, 163, 141],
      itemStyle: { color: '#91cc75' }
    })
    
    series.push({
      name: '市县级',
      type: 'bar',
      stack: 'total',
      emphasis: { focus: 'series' },
      data: [342, 253, 215, 187],
      itemStyle: { color: '#fac858' }
    })
  }
  
  if (categoryType.value === 'culture' || categoryType.value === 'all') {
    // 假设 nature 和 culture 类型都选择时，categories 包含所有类型
    if (categoryType.value === 'culture') {
      categories = ['博物馆', '文化遗产', '名胜古迹', '历史街区']
    } else {
      categories = [...categories, '博物馆', '文化遗产', '名胜古迹', '历史街区']
    }
    
    // 假设我们已经有三个 series 条目，需要更新它们的数据
    if (categoryType.value === 'all' && series.length === 3) {
      series[0].data = [...series[0].data, 112, 78, 92, 65]
      series[1].data = [...series[1].data, 187, 142, 165, 132]
      series[2].data = [...series[2].data, 274, 187, 213, 186]
    } else {
      series.push({
        name: '国家级',
        type: 'bar',
        stack: 'total',
        emphasis: { focus: 'series' },
        data: [112, 78, 92, 65],
        itemStyle: { color: '#5470c6' }
      })
      
      series.push({
        name: '省级',
        type: 'bar',
        stack: 'total',
        emphasis: { focus: 'series' },
        data: [187, 142, 165, 132],
        itemStyle: { color: '#91cc75' }
      })
      
      series.push({
        name: '市县级',
        type: 'bar',
        stack: 'total',
        emphasis: { focus: 'series' },
        data: [274, 187, 213, 186],
        itemStyle: { color: '#fac858' }
      })
    }
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['国家级', '省级', '市县级']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: categories
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '数量'
      }
    ],
    series: series
  }
  
  categoryChart.setOption(option)
}

// 初始化文物保护单位词云
const initWordCloudChart = () => {
  if (!wordCloudChartRef.value) return
  
  wordCloudChart = echarts.init(wordCloudChartRef.value)
  updateWordCloudChart()
}

// 更新文物保护单位词云
const updateWordCloudChart = () => {
  if (!wordCloudChart) return
  
  // 根据权重类型生成不同的数据
  let data = []
  
  if (wordcloudWeight.value === 'level') {
    data = [
      { name: '故宫博物院', value: 98, textStyle: { color: '#e63946' } },
      { name: '秦始皇陵兵马俑', value: 96, textStyle: { color: '#e63946' } },
      { name: '莫高窟', value: 94, textStyle: { color: '#e63946' } },
      { name: '颐和园', value: 91, textStyle: { color: '#e63946' } },
      { name: '长城', value: 90, textStyle: { color: '#e63946' } },
      { name: '平遥古城', value: 88, textStyle: { color: '#f1a208' } },
      { name: '周口店遗址', value: 86, textStyle: { color: '#f1a208' } },
      { name: '曲阜孔庙', value: 85, textStyle: { color: '#f1a208' } },
      { name: '乐山大佛', value: 84, textStyle: { color: '#f1a208' } },
      { name: '明十三陵', value: 83, textStyle: { color: '#f1a208' } },
      { name: '苏州园林', value: 82, textStyle: { color: '#1d3557' } },
      { name: '泰山', value: 81, textStyle: { color: '#1d3557' } },
      { name: '布达拉宫', value: 80, textStyle: { color: '#1d3557' } },
      { name: '龙门石窟', value: 78, textStyle: { color: '#1d3557' } },
      { name: '黄山', value: 76, textStyle: { color: '#1d3557' } },
      { name: '三星堆', value: 75, textStyle: { color: '#457b9d' } },
      { name: '武当山', value: 74, textStyle: { color: '#457b9d' } },
      { name: '清东陵', value: 72, textStyle: { color: '#457b9d' } },
      { name: '承德避暑山庄', value: 71, textStyle: { color: '#457b9d' } },
      { name: '云冈石窟', value: 70, textStyle: { color: '#457b9d' } },
      { name: '殷墟', value: 68, textStyle: { color: '#457b9d' } },
      { name: '大足石刻', value: 67, textStyle: { color: '#457b9d' } },
      { name: '峨眉山', value: 66, textStyle: { color: '#457b9d' } },
      { name: '皖南古村落', value: 65, textStyle: { color: '#a8dadc' } },
      { name: '丽江古城', value: 64, textStyle: { color: '#a8dadc' } },
      { name: '安阳古城', value: 63, textStyle: { color: '#a8dadc' } },
      { name: '嵩山少林寺', value: 62, textStyle: { color: '#a8dadc' } },
      { name: '张家界', value: 61, textStyle: { color: '#a8dadc' } },
      { name: '九寨沟', value: 60, textStyle: { color: '#a8dadc' } },
      { name: '鼓浪屿', value: 59, textStyle: { color: '#a8dadc' } }
    ]
  } else if (wordcloudWeight.value === 'age') {
    data = [
      { name: '周口店遗址', value: 98, textStyle: { color: '#e63946' } },
      { name: '殷墟', value: 97, textStyle: { color: '#e63946' } },
      { name: '三星堆', value: 95, textStyle: { color: '#e63946' } },
      { name: '莫高窟', value: 92, textStyle: { color: '#f1a208' } },
      { name: '云冈石窟', value: 90, textStyle: { color: '#f1a208' } },
      { name: '龙门石窟', value: 89, textStyle: { color: '#f1a208' } },
      { name: '大足石刻', value: 88, textStyle: { color: '#f1a208' } },
      { name: '长城', value: 86, textStyle: { color: '#1d3557' } },
      { name: '秦始皇陵兵马俑', value: 85, textStyle: { color: '#1d3557' } },
      { name: '泰山', value: 84, textStyle: { color: '#1d3557' } },
      { name: '曲阜孔庙', value: 83, textStyle: { color: '#1d3557' } },
      { name: '武当山', value: 82, textStyle: { color: '#1d3557' } },
      { name: '嵩山少林寺', value: 81, textStyle: { color: '#1d3557' } },
      { name: '峨眉山', value: 80, textStyle: { color: '#1d3557' } },
      { name: '黄山', value: 78, textStyle: { color: '#457b9d' } },
      { name: '乐山大佛', value: 76, textStyle: { color: '#457b9d' } },
      { name: '平遥古城', value: 75, textStyle: { color: '#457b9d' } },
      { name: '苏州园林', value: 74, textStyle: { color: '#457b9d' } },
      { name: '明十三陵', value: 72, textStyle: { color: '#457b9d' } },
      { name: '清东陵', value: 71, textStyle: { color: '#457b9d' } },
      { name: '故宫博物院', value: 70, textStyle: { color: '#457b9d' } },
      { name: '承德避暑山庄', value: 68, textStyle: { color: '#a8dadc' } },
      { name: '颐和园', value: 66, textStyle: { color: '#a8dadc' } },
      { name: '皖南古村落', value: 65, textStyle: { color: '#a8dadc' } },
      { name: '丽江古城', value: 64, textStyle: { color: '#a8dadc' } },
      { name: '安阳古城', value: 63, textStyle: { color: '#a8dadc' } },
      { name: '布达拉宫', value: 62, textStyle: { color: '#a8dadc' } },
      { name: '张家界', value: 61, textStyle: { color: '#a8dadc' } },
      { name: '九寨沟', value: 60, textStyle: { color: '#a8dadc' } },
      { name: '鼓浪屿', value: 58, textStyle: { color: '#a8dadc' } }
    ]
  } else {
    data = [
      { name: '故宫博物院', value: 98, textStyle: { color: '#e63946' } },
      { name: '长城', value: 96, textStyle: { color: '#e63946' } },
      { name: '秦始皇陵兵马俑', value: 95, textStyle: { color: '#e63946' } },
      { name: '黄山', value: 92, textStyle: { color: '#e63946' } },
      { name: '张家界', value: 90, textStyle: { color: '#e63946' } },
      { name: '九寨沟', value: 89, textStyle: { color: '#f1a208' } },
      { name: '颐和园', value: 87, textStyle: { color: '#f1a208' } },
      { name: '乐山大佛', value: 86, textStyle: { color: '#f1a208' } },
      { name: '苏州园林', value: 85, textStyle: { color: '#f1a208' } },
      { name: '莫高窟', value: 84, textStyle: { color: '#f1a208' } },
      { name: '布达拉宫', value: 83, textStyle: { color: '#1d3557' } },
      { name: '丽江古城', value: 81, textStyle: { color: '#1d3557' } },
      { name: '泰山', value: 80, textStyle: { color: '#1d3557' } },
      { name: '三星堆', value: 78, textStyle: { color: '#1d3557' } },
      { name: '鼓浪屿', value: 76, textStyle: { color: '#1d3557' } },
      { name: '平遥古城', value: 75, textStyle: { color: '#457b9d' } },
      { name: '龙门石窟', value: 74, textStyle: { color: '#457b9d' } },
      { name: '峨眉山', value: 72, textStyle: { color: '#457b9d' } },
      { name: '武当山', value: 71, textStyle: { color: '#457b9d' } },
      { name: '明十三陵', value: 70, textStyle: { color: '#457b9d' } },
      { name: '嵩山少林寺', value: 68, textStyle: { color: '#457b9d' } },
      { name: '周口店遗址', value: 66, textStyle: { color: '#457b9d' } },
      { name: '云冈石窟', value: 65, textStyle: { color: '#457b9d' } },
      { name: '皖南古村落', value: 64, textStyle: { color: '#a8dadc' } },
      { name: '承德避暑山庄', value: 63, textStyle: { color: '#a8dadc' } },
      { name: '殷墟', value: 62, textStyle: { color: '#a8dadc' } },
      { name: '安阳古城', value: 61, textStyle: { color: '#a8dadc' } },
      { name: '大足石刻', value: 60, textStyle: { color: '#a8dadc' } },
      { name: '清东陵', value: 59, textStyle: { color: '#a8dadc' } },
      { name: '曲阜孔庙', value: 58, textStyle: { color: '#a8dadc' } }
    ]
  }
  
  const option = {
    tooltip: {
      show: true,
      formatter: function(params: any) {
        return `${params.name}: ${params.value}`
      }
    },
    series: [
      {
        type: 'wordCloud',
        shape: 'circle',
        left: 'center',
        top: 'center',
        width: '80%',
        height: '80%',
        right: null,
        bottom: null,
        sizeRange: [12, 50],
        rotationRange: [-90, 90],
        rotationStep: 45,
        gridSize: 8,
        drawOutOfBound: false,
        textStyle: {
          fontFamily: 'sans-serif',
          fontWeight: 'bold'
        },
        emphasis: {
          focus: 'self',
          textStyle: {
            shadowBlur: 10,
            shadowColor: '#333'
          }
        },
        data: data
      }
    ]
  }
  
  wordCloudChart.setOption(option)
}

// 初始化不同类型景区雷达图
const initRadarChart = () => {
  if (!radarChartRef.value) return
  
  radarChart = echarts.init(radarChartRef.value)
  
  const option = {
    title: {
      text: '不同类型景区特性对比'
    },
    tooltip: {},
    legend: {
      data: ['自然景区', '文化景区', '主题公园']
    },
    radar: {
      indicator: [
        { name: '票价', max: 100 },
        { name: '访问量', max: 100 },
        { name: '知名度', max: 100 },
        { name: '景区面积', max: 100 },
        { name: '季节性影响', max: 100 },
        { name: '国际影响力', max: 100 }
      ]
    },
    series: [
      {
        name: '景区类型',
        type: 'radar',
        data: [
          {
            value: [60, 85, 90, 95, 70, 80],
            name: '自然景区',
            areaStyle: {
              color: 'rgba(0, 128, 0, 0.2)'
            },
            lineStyle: {
              color: 'green'
            }
          },
          {
            value: [75, 90, 95, 70, 60, 90],
            name: '文化景区',
            areaStyle: {
              color: 'rgba(128, 0, 0, 0.2)'
            },
            lineStyle: {
              color: 'brown'
            }
          },
          {
            value: [90, 85, 85, 65, 50, 75],
            name: '主题公园',
            areaStyle: {
              color: 'rgba(0, 0, 128, 0.2)'
            },
            lineStyle: {
              color: 'blue'
            }
          }
        ]
      }
    ]
  }
  
  radarChart.setOption(option)
}

// 初始化景区分类趋势图
const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  trendChart = echarts.init(trendChartRef.value)
  updateTrendChart()
}

// 更新景区分类趋势图
const updateTrendChart = () => {
  if (!trendChart) return
  
  // 准备数据
  let xAxisData = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  let series = []
  
  const naturalData2021 = [120, 132, 145, 160, 175, 188, 196, 210, 182, 165, 152, 143]
  const culturalData2021 = [130, 142, 156, 172, 185, 192, 204, 215, 195, 178, 163, 152]
  const themeParkData2021 = [110, 125, 138, 155, 170, 185, 198, 208, 185, 162, 145, 132]
  
  const naturalData2022 = [135, 148, 162, 178, 190, 205, 215, 228, 196, 182, 168, 155]
  const culturalData2022 = [146, 158, 173, 189, 205, 215, 225, 232, 214, 195, 176, 165]
  const themeParkData2022 = [125, 138, 152, 172, 188, 204, 218, 226, 198, 178, 162, 148]
  
  const naturalData2023 = [152, 165, 180, 198, 215, 228, 235, 248, 225, 198, 184, 172]
  const culturalData2023 = [165, 178, 195, 212, 225, 238, 248, 255, 235, 212, 193, 180]
  const themeParkData2023 = [142, 155, 170, 190, 205, 220, 232, 242, 218, 190, 176, 162]
  
  if (trendYear.value === '2021' || trendYear.value === 'all') {
    series.push(
      {
        name: trendYear.value === 'all' ? '2021自然景区' : '自然景区',
        type: 'line',
        smooth: true,
        data: naturalData2021,
        lineStyle: { width: 2 }
      },
      {
        name: trendYear.value === 'all' ? '2021文化景区' : '文化景区',
        type: 'line',
        smooth: true,
        data: culturalData2021,
        lineStyle: { width: 2 }
      },
      {
        name: trendYear.value === 'all' ? '2021主题公园' : '主题公园',
        type: 'line',
        smooth: true,
        data: themeParkData2021,
        lineStyle: { width: 2 }
      }
    )
  }
  
  if (trendYear.value === '2022' || trendYear.value === 'all') {
    series.push(
      {
        name: trendYear.value === 'all' ? '2022自然景区' : '自然景区',
        type: 'line',
        smooth: true,
        data: naturalData2022,
        lineStyle: { width: 2 }
      },
      {
        name: trendYear.value === 'all' ? '2022文化景区' : '文化景区',
        type: 'line',
        smooth: true,
        data: culturalData2022,
        lineStyle: { width: 2 }
      },
      {
        name: trendYear.value === 'all' ? '2022主题公园' : '主题公园',
        type: 'line',
        smooth: true,
        data: themeParkData2022,
        lineStyle: { width: 2 }
      }
    )
  }
  
  if (trendYear.value === '2023' || trendYear.value === 'all') {
    series.push(
      {
        name: trendYear.value === 'all' ? '2023自然景区' : '自然景区',
        type: 'line',
        smooth: true,
        data: naturalData2023,
        lineStyle: { width: 2 }
      },
      {
        name: trendYear.value === 'all' ? '2023文化景区' : '文化景区',
        type: 'line',
        smooth: true,
        data: culturalData2023,
        lineStyle: { width: 2 }
      },
      {
        name: trendYear.value === 'all' ? '2023主题公园' : '主题公园',
        type: 'line',
        smooth: true,
        data: themeParkData2023,
        lineStyle: { width: 2 }
      }
    )
  }
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: series.map(item => item.name)
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xAxisData
    },
    yAxis: {
      type: 'value',
      name: '景区数量'
    },
    series: series
  }
  
  trendChart.setOption(option)
}
</script>

<style scoped>
.classification-container {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
  text-align: center;
}

.welcome-card h2 {
  margin-top: 0;
  color: #303133;
}

.welcome-card p {
  color: #606266;
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
  height: 350px;
}
</style> 