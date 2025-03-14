<template>
  <div class="transportation-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <h2>交通与可达性分析</h2>
          <p>本模块提供全国景区的交通方式及可达性分析，帮助您了解不同景区的交通便捷程度及游客出行选择。</p>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>交通方式分布</span>
              <el-select v-model="transportCity" placeholder="选择城市" size="small">
                <el-option label="北京" value="北京"></el-option>
                <el-option label="上海" value="上海"></el-option>
                <el-option label="杭州" value="杭州"></el-option>
                <el-option label="西安" value="西安"></el-option>
                <el-option label="成都" value="成都"></el-option>
                <el-option label="全国" value="全国"></el-option>
              </el-select>
            </div>
          </template>
          <div class="chart-container sankey-container" ref="sankeyChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区可达性等级分布</span>
              <el-radio-group v-model="accessibilityLevel" size="small">
                <el-radio-button label="scenic">按景区级别</el-radio-button>
                <el-radio-button label="region">按区域</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="accessibilityChartRef"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>公共交通便捷度</span>
            </div>
          </template>
          <div class="chart-container" ref="publicTransportChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区交通满意度分析</span>
              <el-slider
                v-model="satisfactionYear"
                :min="2018"
                :max="2023"
                :marks="{2018: '2018', 2019: '2019', 2020: '2020', 2021: '2021', 2022: '2022', 2023: '2023'}"
                style="width: 300px"
              ></el-slider>
            </div>
          </template>
          <div class="chart-container" ref="satisfactionChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>典型景区交通方式对比</span>
            </div>
          </template>
          <el-table :data="scenicTransportData" style="width: 100%">
            <el-table-column prop="name" label="景区名称" width="150" />
            <el-table-column prop="level" label="景区级别" width="100">
              <template #default="scope">
                <el-tag :type="getLevelTagType(scope.row.level)">{{ scope.row.level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="location" label="所在地" width="150" />
            <el-table-column prop="publicTransport" label="公共交通">
              <template #default="scope">
                <el-progress :percentage="scope.row.publicTransport" :color="getProgressColor(scope.row.publicTransport)"></el-progress>
              </template>
            </el-table-column>
            <el-table-column prop="selfDriving" label="自驾">
              <template #default="scope">
                <el-progress :percentage="scope.row.selfDriving" :color="getProgressColor(scope.row.selfDriving)"></el-progress>
              </template>
            </el-table-column>
            <el-table-column prop="tourGroup" label="跟团">
              <template #default="scope">
                <el-progress :percentage="scope.row.tourGroup" :color="getProgressColor(scope.row.tourGroup)"></el-progress>
              </template>
            </el-table-column>
            <el-table-column prop="accessibility" label="可达性评分" width="120">
              <template #default="scope">
                <el-rate v-model="scope.row.accessibility" disabled text-color="#ff9900" :max="5" :show-score="true" score-template="{value}"></el-rate>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

// 筛选条件
const transportCity = ref('全国')
const accessibilityLevel = ref('scenic')
const satisfactionYear = ref(2023)

// 图表引用
const sankeyChartRef = ref<HTMLElement | null>(null)
const accessibilityChartRef = ref<HTMLElement | null>(null)
const publicTransportChartRef = ref<HTMLElement | null>(null)
const satisfactionChartRef = ref<HTMLElement | null>(null)

// 图表实例
let sankeyChart: echarts.ECharts | null = null
let accessibilityChart: echarts.ECharts | null = null
let publicTransportChart: echarts.ECharts | null = null
let satisfactionChart: echarts.ECharts | null = null

// 典型景区交通方式数据
const scenicTransportData = [
  {
    name: '故宫博物院',
    level: '5A',
    location: '北京市东城区',
    publicTransport: 80,
    selfDriving: 15,
    tourGroup: 5,
    accessibility: 4.5
  },
  {
    name: '黄山风景区',
    level: '5A',
    location: '安徽省黄山市',
    publicTransport: 30,
    selfDriving: 35,
    tourGroup: 35,
    accessibility: 3.5
  },
  {
    name: '九寨沟',
    level: '5A',
    location: '四川省阿坝州',
    publicTransport: 15,
    selfDriving: 25,
    tourGroup: 60,
    accessibility: 2.5
  },
  {
    name: '西湖',
    level: '5A',
    location: '浙江省杭州市',
    publicTransport: 65,
    selfDriving: 30,
    tourGroup: 5,
    accessibility: 5.0
  },
  {
    name: '泰山',
    level: '5A',
    location: '山东省泰安市',
    publicTransport: 45,
    selfDriving: 35,
    tourGroup: 20,
    accessibility: 4.0
  },
  {
    name: '峨眉山',
    level: '5A',
    location: '四川省乐山市',
    publicTransport: 35,
    selfDriving: 30,
    tourGroup: 35,
    accessibility: 3.5
  },
  {
    name: '周庄古镇',
    level: '4A',
    location: '江苏省苏州市',
    publicTransport: 55,
    selfDriving: 35,
    tourGroup: 10,
    accessibility: 4.0
  },
  {
    name: '张家界',
    level: '5A',
    location: '湖南省张家界市',
    publicTransport: 20,
    selfDriving: 30,
    tourGroup: 50,
    accessibility: 3.0
  }
]

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

// 获取进度条颜色
const getProgressColor = (percentage: number) => {
  if (percentage > 70) return '#67C23A'
  if (percentage > 30) return '#409EFF'
  return '#E6A23C'
}

// 监听城市选择变化
watch(transportCity, () => {
  nextTick(() => {
    updateSankeyChart()
  })
})

// 监听可达性分类方式变化
watch(accessibilityLevel, () => {
  nextTick(() => {
    updateAccessibilityChart()
  })
})

// 监听满意度年份变化
watch(satisfactionYear, () => {
  nextTick(() => {
    updateSatisfactionChart()
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
  initSankeyChart()
  initAccessibilityChart()
  initPublicTransportChart()
  initSatisfactionChart()
}

// 重置图表大小
const resizeCharts = () => {
  sankeyChart?.resize()
  accessibilityChart?.resize()
  publicTransportChart?.resize()
  satisfactionChart?.resize()
}

// 初始化桑基图
const initSankeyChart = () => {
  if (!sankeyChartRef.value) return
  
  sankeyChart = echarts.init(sankeyChartRef.value)
  updateSankeyChart()
}

// 更新桑基图
const updateSankeyChart = () => {
  if (!sankeyChart) return
  
  // 准备不同城市的数据
  let nodesData: any[] = []
  let linksData: any[] = []
  
  if (transportCity.value === '北京' || transportCity.value === '全国') {
    nodesData.push(
      { name: '北京' },
      { name: '地铁' },
      { name: '公交' },
      { name: '自驾' },
      { name: '旅游专线' },
      { name: '出租车' },
      { name: '自行车' }
    )
    
    linksData.push(
      { source: '北京', target: '地铁', value: 45 },
      { source: '北京', target: '公交', value: 20 },
      { source: '北京', target: '自驾', value: 15 },
      { source: '北京', target: '旅游专线', value: 10 },
      { source: '北京', target: '出租车', value: 8 },
      { source: '北京', target: '自行车', value: 2 }
    )
  }
  
  if (transportCity.value === '上海' || transportCity.value === '全国') {
    nodesData.push(
      { name: '上海' },
      { name: '地铁' },
      { name: '公交' },
      { name: '自驾' },
      { name: '旅游专线' },
      { name: '出租车' },
      { name: '自行车' }
    )
    
    linksData.push(
      { source: '上海', target: '地铁', value: 50 },
      { source: '上海', target: '公交', value: 18 },
      { source: '上海', target: '自驾', value: 12 },
      { source: '上海', target: '旅游专线', value: 8 },
      { source: '上海', target: '出租车', value: 10 },
      { source: '上海', target: '自行车', value: 2 }
    )
  }
  
  if (transportCity.value === '杭州' || transportCity.value === '全国') {
    nodesData.push(
      { name: '杭州' },
      { name: '地铁' },
      { name: '公交' },
      { name: '自驾' },
      { name: '旅游专线' },
      { name: '出租车' },
      { name: '自行车' }
    )
    
    linksData.push(
      { source: '杭州', target: '地铁', value: 35 },
      { source: '杭州', target: '公交', value: 25 },
      { source: '杭州', target: '自驾', value: 20 },
      { source: '杭州', target: '旅游专线', value: 8 },
      { source: '杭州', target: '出租车', value: 7 },
      { source: '杭州', target: '自行车', value: 5 }
    )
  }
  
  if (transportCity.value === '西安' || transportCity.value === '全国') {
    nodesData.push(
      { name: '西安' },
      { name: '地铁' },
      { name: '公交' },
      { name: '自驾' },
      { name: '旅游专线' },
      { name: '出租车' },
      { name: '自行车' }
    )
    
    linksData.push(
      { source: '西安', target: '地铁', value: 32 },
      { source: '西安', target: '公交', value: 22 },
      { source: '西安', target: '自驾', value: 25 },
      { source: '西安', target: '旅游专线', value: 12 },
      { source: '西安', target: '出租车', value: 8 },
      { source: '西安', target: '自行车', value: 1 }
    )
  }
  
  if (transportCity.value === '成都' || transportCity.value === '全国') {
    nodesData.push(
      { name: '成都' },
      { name: '地铁' },
      { name: '公交' },
      { name: '自驾' },
      { name: '旅游专线' },
      { name: '出租车' },
      { name: '自行车' }
    )
    
    linksData.push(
      { source: '成都', target: '地铁', value: 30 },
      { source: '成都', target: '公交', value: 20 },
      { source: '成都', target: '自驾', value: 28 },
      { source: '成都', target: '旅游专线', value: 15 },
      { source: '成都', target: '出租车', value: 6 },
      { source: '成都', target: '自行车', value: 1 }
    )
  }
  
  // 去重节点
  const uniqueNodes = Array.from(new Set(nodesData.map(node => node.name))).map(name => {
    return { name }
  })
  
  const option = {
    title: {
      text: '景区交通方式流向分析',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove'
    },
    series: [
      {
        type: 'sankey',
        emphasis: {
          focus: 'adjacency'
        },
        nodeAlign: 'left',
        data: uniqueNodes,
        links: linksData,
        lineStyle: {
          color: 'source',
          curveness: 0.5
        },
        label: {
          color: 'rgba(0,0,0,0.7)',
          fontFamily: 'Arial',
          fontSize: 14
        },
        itemStyle: {
          color: '#1f77b4',
          borderColor: '#fff'
        }
      }
    ]
  }
  
  sankeyChart.setOption(option)
}

// 初始化可达性图表
const initAccessibilityChart = () => {
  if (!accessibilityChartRef.value) return
  
  accessibilityChart = echarts.init(accessibilityChartRef.value)
  updateAccessibilityChart()
}

// 更新可达性图表
const updateAccessibilityChart = () => {
  if (!accessibilityChart) return
  
  let xAxisData: string[] = []
  let seriesData: any[] = []
  
  if (accessibilityLevel.value === 'scenic') {
    xAxisData = ['5A级景区', '4A级景区', '3A级景区', '2A级景区', '其他景区']
    seriesData = [
      {
        name: '高度便捷',
        stack: 'total',
        data: [70, 45, 30, 20, 10],
        itemStyle: { color: '#91cc75' }
      },
      {
        name: '较为便捷',
        stack: 'total',
        data: [15, 25, 30, 25, 15],
        itemStyle: { color: '#fac858' }
      },
      {
        name: '一般便捷',
        stack: 'total',
        data: [10, 20, 25, 30, 35],
        itemStyle: { color: '#ee6666' }
      },
      {
        name: '不便捷',
        stack: 'total',
        data: [5, 10, 15, 25, 40],
        itemStyle: { color: '#73c0de' }
      }
    ]
  } else {
    xAxisData = ['华东', '华南', '华北', '西南', '西北', '东北', '华中']
    seriesData = [
      {
        name: '高度便捷',
        stack: 'total',
        data: [65, 60, 55, 40, 30, 35, 50],
        itemStyle: { color: '#91cc75' }
      },
      {
        name: '较为便捷',
        stack: 'total',
        data: [20, 25, 25, 25, 20, 25, 25],
        itemStyle: { color: '#fac858' }
      },
      {
        name: '一般便捷',
        stack: 'total',
        data: [10, 10, 15, 20, 25, 25, 15],
        itemStyle: { color: '#ee6666' }
      },
      {
        name: '不便捷',
        stack: 'total',
        data: [5, 5, 5, 15, 25, 15, 10],
        itemStyle: { color: '#73c0de' }
      }
    ]
  }
  
  const option = {
    title: {
      text: '景区可达性等级分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['高度便捷', '较为便捷', '一般便捷', '不便捷'],
      bottom: '0%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: xAxisData
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '比例（%）'
      }
    ],
    series: seriesData
  }
  
  accessibilityChart.setOption(option)
}

// 初始化公共交通便捷度图表
const initPublicTransportChart = () => {
  if (!publicTransportChartRef.value) return
  
  publicTransportChart = echarts.init(publicTransportChartRef.value)
  
  const option = {
    title: {
      text: '主要景区公共交通便捷度',
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
    dataset: {
      source: [
        ['score', 'amount', 'product'],
        [89.3, 58, '西湖'],
        [86.5, 65, '故宫'],
        [83.8, 55, '天安门'],
        [78.4, 48, '颐和园'],
        [72.2, 46, '外滩'],
        [65.9, 42, '泰山'],
        [62.7, 38, '兵马俑'],
        [51.6, 35, '乐山大佛'],
        [48.3, 32, '黄山'],
        [43.5, 28, '九寨沟'],
        [38.2, 25, '张家界'],
        [35.1, 20, '峨眉山']
      ]
    },
    xAxis: {
      name: '便捷度评分',
      nameLocation: 'middle',
      nameGap: 30
    },
    yAxis: {
      type: 'category'
    },
    visualMap: {
      orient: 'horizontal',
      left: 'center',
      min: 30,
      max: 90,
      text: ['高便捷度', '低便捷度'],
      dimension: 0,
      inRange: {
        color: ['#ee6666', '#fac858', '#91cc75']
      }
    },
    series: [
      {
        type: 'bar',
        encode: {
          x: 'amount',
          y: 'product'
        }
      }
    ]
  }
  
  publicTransportChart.setOption(option)
}

// 初始化满意度图表
const initSatisfactionChart = () => {
  if (!satisfactionChartRef.value) return
  
  satisfactionChart = echarts.init(satisfactionChartRef.value)
  updateSatisfactionChart()
}

// 更新满意度图表
const updateSatisfactionChart = () => {
  if (!satisfactionChart) return
  
  const transportTypes = ['地铁/轻轨', '公交车', '旅游专线', '自驾车', '出租车', '网约车', '共享单车']
  
  // 不同年份的满意度数据（0-100分）
  const data2018 = [87, 76, 68, 83, 75, 85, 62]
  const data2019 = [88, 77, 70, 84, 76, 87, 65]
  const data2020 = [85, 75, 65, 86, 72, 84, 63]
  const data2021 = [87, 78, 73, 86, 75, 86, 68]
  const data2022 = [89, 80, 75, 87, 78, 88, 72]
  const data2023 = [90, 82, 78, 88, 80, 90, 75]
  
  // 根据年份选择数据
  let seriesData = data2023
  if (satisfactionYear.value === 2018) seriesData = data2018
  if (satisfactionYear.value === 2019) seriesData = data2019
  if (satisfactionYear.value === 2020) seriesData = data2020
  if (satisfactionYear.value === 2021) seriesData = data2021
  if (satisfactionYear.value === 2022) seriesData = data2022
  
  const option = {
    title: {
      text: `${satisfactionYear.value}年景区交通满意度分析`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params: any) {
        return `${params[0].name}<br/>${params[0].marker} 满意度: ${params[0].value}分`
      }
    },
    radar: {
      indicator: transportTypes.map(type => {
        return { name: type, max: 100 }
      }),
      center: ['50%', '50%'],
      radius: '65%'
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: seriesData,
            name: '满意度',
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.6)'
            },
            lineStyle: {
              width: 2,
              color: '#409EFF'
            },
            itemStyle: {
              color: '#409EFF'
            }
          }
        ]
      }
    ]
  }
  
  satisfactionChart.setOption(option)
}
</script>

<style scoped>
.transportation-container {
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

.sankey-container {
  height: 450px;
}
</style> 