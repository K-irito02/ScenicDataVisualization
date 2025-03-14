<template>
  <div class="ticket-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <h2>门票与开放时间分析</h2>
          <p>本模块提供全国景区门票价格及开放时间的分析，帮助您了解不同级别景区的价格分布及运营时间特征。</p>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>门票价格分布</span>
              <el-select v-model="priceFilter" placeholder="景区级别" size="small" clearable>
                <el-option label="5A级景区" value="5A"></el-option>
                <el-option label="4A级景区" value="4A"></el-option>
                <el-option label="3A级景区" value="3A"></el-option>
                <el-option label="所有景区" value="all"></el-option>
              </el-select>
            </div>
          </template>
          <div class="chart-container" ref="boxPlotChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>开放时间分布</span>
            </div>
          </template>
          <div class="chart-container" ref="openTimeChartRef"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>价格与级别关系</span>
            </div>
          </template>
          <div class="chart-container" ref="priceLevelChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>不同时段开放景区数量</span>
              <el-slider
                v-model="timeRange"
                range
                :min="0"
                :max="24"
                :format-tooltip="formatHour"
                style="width: 300px"
              ></el-slider>
            </div>
          </template>
          <div class="chart-container" ref="timeDistributionChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>异常定价景区列表</span>
            </div>
          </template>
          <el-table :data="abnormalPriceData" style="width: 100%">
            <el-table-column prop="name" label="景区名称" />
            <el-table-column prop="level" label="景区级别">
              <template #default="scope">
                <el-tag :type="getLevelTagType(scope.row.level)">{{ scope.row.level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="location" label="所在地" />
            <el-table-column prop="price" label="门票价格">
              <template #default="scope">
                <span>¥{{ scope.row.price }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="avgPrice" label="同级别平均价格">
              <template #default="scope">
                <span>¥{{ scope.row.avgPrice }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="deviation" label="偏离度">
              <template #default="scope">
                <el-tag :type="getDeviationTagType(scope.row.deviation)">
                  {{ scope.row.deviation > 0 ? '+' : '' }}{{ scope.row.deviation }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="可能原因" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

// 价格筛选
const priceFilter = ref('all')
// 时间范围
const timeRange = ref([8, 18])

// 图表引用
const boxPlotChartRef = ref<HTMLElement | null>(null)
const openTimeChartRef = ref<HTMLElement | null>(null)
const priceLevelChartRef = ref<HTMLElement | null>(null)
const timeDistributionChartRef = ref<HTMLElement | null>(null)

// 图表实例
let boxPlotChart: echarts.ECharts | null = null
let openTimeChart: echarts.ECharts | null = null
let priceLevelChart: echarts.ECharts | null = null
let timeDistributionChart: echarts.ECharts | null = null

// 异常定价景区数据
const abnormalPriceData = [
  {
    name: '九寨沟',
    level: '5A',
    location: '四川省阿坝州',
    price: 220,
    avgPrice: 163,
    deviation: 35,
    reason: '稀缺自然资源，旅游旺季，恢复性定价'
  },
  {
    name: '峨眉山景区',
    level: '5A',
    location: '四川省乐山市',
    price: 185,
    avgPrice: 163,
    deviation: 13,
    reason: '高海拔景区，运营成本高'
  },
  {
    name: '故宫博物院',
    level: '5A',
    location: '北京市东城区',
    price: 60,
    avgPrice: 163,
    deviation: -63,
    reason: '国家政策，普惠性文化景区'
  },
  {
    name: '西溪湿地',
    level: '4A',
    location: '浙江省杭州市',
    price: 150,
    avgPrice: 95,
    deviation: 58,
    reason: '生态保护成本高，限流需求'
  },
  {
    name: '鼓浪屿',
    level: '5A',
    location: '福建省厦门市',
    price: 35,
    avgPrice: 163,
    deviation: -79,
    reason: '门票与交通费分离，实际消费较高'
  },
  {
    name: '兵马俑博物馆',
    level: '5A',
    location: '陕西省西安市',
    price: 120,
    avgPrice: 163,
    deviation: -26,
    reason: '国家文物保护单位，价格管控'
  }
]

// 格式化小时
const formatHour = (val: number) => {
  return `${val}:00`
}

// 获取景区级别标签类型
const getLevelTagType = (level: string) => {
  const typeMap: Record<string, string> = {
    '5A': 'danger',
    '4A': 'warning',
    '3A': 'success',
    '2A': ''
  }
  return typeMap[level] || ''
}

// 获取偏离度标签类型
const getDeviationTagType = (deviation: number) => {
  if (deviation > 30) return 'danger'
  if (deviation > 0) return 'warning'
  if (deviation < -30) return 'success'
  return 'info'
}

// 监听价格筛选变化
watch(priceFilter, () => {
  nextTick(() => {
    updateBoxPlotChart()
  })
})

// 监听时间范围变化
watch(timeRange, () => {
  nextTick(() => {
    updateTimeDistributionChart()
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
  initBoxPlotChart()
  initOpenTimeChart()
  initPriceLevelChart()
  initTimeDistributionChart()
}

// 重置图表大小
const resizeCharts = () => {
  boxPlotChart?.resize()
  openTimeChart?.resize()
  priceLevelChart?.resize()
  timeDistributionChart?.resize()
}

// 初始化门票价格箱线图
const initBoxPlotChart = () => {
  if (!boxPlotChartRef.value) return
  
  boxPlotChart = echarts.init(boxPlotChartRef.value)
  updateBoxPlotChart()
}

// 更新门票价格箱线图
const updateBoxPlotChart = () => {
  if (!boxPlotChart) return
  
  let data: any[] = []
  
  // 按景区级别过滤数据
  if (priceFilter.value === 'all' || priceFilter.value === '5A') {
    data.push({
      name: '5A景区',
      value: [80, 120, 165, 210, 280],
      itemStyle: { color: '#ee6666' }
    })
  }
  
  if (priceFilter.value === 'all' || priceFilter.value === '4A') {
    data.push({
      name: '4A景区',
      value: [45, 75, 95, 138, 190],
      itemStyle: { color: '#fac858' }
    })
  }
  
  if (priceFilter.value === 'all' || priceFilter.value === '3A') {
    data.push({
      name: '3A景区',
      value: [25, 45, 65, 85, 120],
      itemStyle: { color: '#73c0de' }
    })
  }
  
  // 异常值数据
  const outliers = [
    [0, 280, '九寨沟'], // 5A级第一个箱线图，280元为异常值
    [0, 35, '鼓浪屿'],  // 5A级第一个箱线图，35元为异常值
    [1, 190, '西溪湿地'] // 4A级第二个箱线图，190元为异常值
  ]
  
  // 根据筛选调整异常值
  let filteredOutliers: any[] = []
  
  if (priceFilter.value === 'all') {
    filteredOutliers = outliers
  } else if (priceFilter.value === '5A') {
    filteredOutliers = outliers.filter(item => item[0] === 0)
  } else if (priceFilter.value === '4A') {
    // 需要调整索引，因为筛选后只有4A的箱线图，所以索引从0开始
    filteredOutliers = outliers.filter(item => item[0] === 1).map(item => [0, item[1], item[2]])
  } else if (priceFilter.value === '3A') {
    // 3A级没有显示异常值
    filteredOutliers = []
  }

  const option = {
    title: {
      text: '不同级别景区门票价格分布',
      left: 'center'
    },
    dataset: [
      {
        source: data.map(item => item.value)
      },
      {
        transform: {
          type: 'boxplot',
          config: { 
            itemNameFormatter: (params: any) => {
              return data[params.value].name
            }
          }
        }
      }
    ],
    tooltip: {
      trigger: 'item',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params: any) {
        if (params.seriesType === 'boxplot') {
          return `${params.name}<br/>
            最大值: ¥${params.data[5]}<br/>
            上四分位: ¥${params.data[4]}<br/>
            中位数: ¥${params.data[3]}<br/>
            下四分位: ¥${params.data[2]}<br/>
            最小值: ¥${params.data[1]}`
        } else {
          return `${params.name}: ¥${params.data[1]}`
        }
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      boundaryGap: true,
      nameGap: 30,
      splitLine: {
        show: false
      },
      axisLabel: {
        show: true
      },
      axisLine: {
        show: true
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
        name: '门票价格',
        type: 'boxplot',
        datasetIndex: 1,
        itemStyle: {
          color: function(params: any) {
            return data[params.dataIndex].itemStyle.color
          }
        }
      },
      {
        name: '异常值',
        type: 'scatter',
        data: filteredOutliers,
        tooltip: {
          formatter: function(params: any) {
            return `${params.data[2]}: ¥${params.data[1]}`
          }
        }
      }
    ]
  }
  
  boxPlotChart.setOption(option)
}

// 初始化开放时间环形图
const initOpenTimeChart = () => {
  if (!openTimeChartRef.value) return
  
  openTimeChart = echarts.init(openTimeChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: ['全天开放', '早8点-晚6点', '早9点-晚5点', '早8点-晚9点', '季节性调整', '其他时段']
    },
    series: [
      {
        name: '开放时间',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 58, name: '早8点-晚6点', itemStyle: { color: '#5470c6' } },
          { value: 21, name: '早9点-晚5点', itemStyle: { color: '#91cc75' } },
          { value: 10, name: '早8点-晚9点', itemStyle: { color: '#fac858' } },
          { value: 5, name: '全天开放', itemStyle: { color: '#ee6666' } },
          { value: 4, name: '季节性调整', itemStyle: { color: '#73c0de' } },
          { value: 2, name: '其他时段', itemStyle: { color: '#3ba272' } }
        ]
      }
    ]
  }
  
  openTimeChart.setOption(option)
}

// 初始化价格与级别散点图
const initPriceLevelChart = () => {
  if (!priceLevelChartRef.value) return
  
  priceLevelChart = echarts.init(priceLevelChartRef.value)
  
  const option = {
    title: {
      text: '价格与景区级别关系',
      left: 'center'
    },
    grid: {
      left: '10%',
      right: '5%',
      bottom: '12%'
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params: any) {
        return `${params.data[2]}<br/>级别: ${params.data[3]}<br/>价格: ¥${params.data[1]}`
      }
    },
    xAxis: {
      type: 'category',
      data: ['5A', '4A', '3A', '2A', '1A'],
      name: '景区级别',
      nameLocation: 'middle',
      nameGap: 30
    },
    yAxis: {
      type: 'value',
      name: '价格（元）'
    },
    series: [
      {
        type: 'scatter',
        symbolSize: function(val: any) {
          return val[1] / 3
        },
        data: [
          [0, 220, '九寨沟', '5A'],
          [0, 185, '峨眉山', '5A'],
          [0, 180, '黄山', '5A'],
          [0, 175, '张家界', '5A'],
          [0, 160, '泰山', '5A'],
          [0, 150, '华山', '5A'],
          [0, 120, '兵马俑', '5A'],
          [0, 60, '故宫', '5A'],
          [0, 35, '鼓浪屿', '5A'],
          [1, 190, '西溪湿地', '4A'],
          [1, 130, '千岛湖', '4A'],
          [1, 110, '武当山', '4A'],
          [1, 90, '普陀山', '4A'],
          [1, 85, '秦皇岛', '4A'],
          [1, 80, '三清山', '4A'],
          [1, 70, '天山天池', '4A'],
          [2, 80, '望江楼', '3A'],
          [2, 65, '南京总统府', '3A'],
          [2, 60, '龙门石窟', '3A'],
          [2, 55, '北戴河', '3A'],
          [2, 50, '嵩山少林寺', '3A'],
          [3, 40, '九华山', '2A'],
          [3, 35, '青城山', '2A'],
          [3, 30, '梵净山', '2A']
        ],
        markLine: {
          data: [
            {
              type: 'average',
              name: '平均价格',
              label: {
                formatter: '平均: {c}'
              }
            }
          ]
        }
      }
    ]
  }
  
  priceLevelChart.setOption(option)
}

// 初始化时间分布图
const initTimeDistributionChart = () => {
  if (!timeDistributionChartRef.value) return
  
  timeDistributionChart = echarts.init(timeDistributionChartRef.value)
  updateTimeDistributionChart()
}

// 更新时间分布图
const updateTimeDistributionChart = () => {
  if (!timeDistributionChart) return
  
  // 准备横坐标（每小时）
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  
  // 各时段景区数量
  const scenicCountsByHour = [
    0, 0, 0, 0, 0, 10, 25, 90, 220, 310, 340, 350,
    350, 345, 340, 335, 325, 280, 210, 160, 110, 65, 25, 5
  ]
  
  // 过滤数据，只保留选定时间范围内的数据
  const filteredHours = hours.slice(timeRange.value[0], timeRange.value[1] + 1)
  const filteredCounts = scenicCountsByHour.slice(timeRange.value[0], timeRange.value[1] + 1)
  
  const option = {
    title: {
      text: '景区开放时段分布',
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
      data: filteredHours,
      axisTick: {
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value',
      name: '开放景区数量'
    },
    series: [
      {
        name: '开放景区数量',
        type: 'bar',
        barWidth: '60%',
        data: filteredCounts.map((value, index) => {
          return {
            value: value,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#83bff6' },
                { offset: 0.5, color: '#188df0' },
                { offset: 1, color: '#188df0' }
              ])
            }
          }
        })
      }
    ]
  }
  
  timeDistributionChart.setOption(option)
}
</script>

<style scoped>
.ticket-container {
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