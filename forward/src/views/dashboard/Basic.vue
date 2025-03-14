<template>
  <div class="basic-distribution-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <h2>景区基础分布分析</h2>
          <p>本模块提供全国范围内景区的基础分布情况分析，包括城市景区数量分布和景区级别分布等信息。</p>
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
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>城市景区数量分布</span>
              <div>
                <el-button v-if="selectedCity" size="small" @click="resetCityView">返回全国</el-button>
              </div>
            </div>
          </template>
          <div class="chart-container map-container" ref="cityMapChartRef"></div>
          <div class="chart-container" ref="cityBarChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区级别分布</span>
              <el-select v-model="selectedLevel" placeholder="全部级别" size="small" clearable>
                <el-option label="5A级景区" value="5A"></el-option>
                <el-option label="4A级景区" value="4A"></el-option>
                <el-option label="3A级景区" value="3A"></el-option>
                <el-option label="其他" value="other"></el-option>
              </el-select>
            </div>
          </template>
          <div class="chart-container" ref="levelChartRef"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>景区城市分布</span>
              <el-tag v-if="selectedLevelForCity" size="small" closable @close="clearLevelFilter">
                {{ selectedLevelForCity }}级景区
              </el-tag>
            </div>
          </template>
          <div class="chart-container" ref="cityDistributionChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import 'echarts/extension/bmap/bmap'
import { MapLocation, TrophyBase, Tickets, DataLine } from '@element-plus/icons-vue'

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
    icon: 'TrophyBase',
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

// 选中的景区级别
const selectedLevel = ref('')
// 选中的城市（用于地图下钻）
const selectedCity = ref('')
// 选中的城市数据（用于地图下钻）
const selectedCityData = ref<any>(null)
// 选择的级别过滤（用于联动城市分布图）
const selectedLevelForCity = ref('')

// 图表引用
const cityBarChartRef = ref<HTMLElement | null>(null)
const cityMapChartRef = ref<HTMLElement | null>(null)
const levelChartRef = ref<HTMLElement | null>(null)
const cityDistributionChartRef = ref<HTMLElement | null>(null)

// 图表实例
let cityBarChart: echarts.ECharts | null = null
let cityMapChart: echarts.ECharts | null = null
let levelChart: echarts.ECharts | null = null
let cityDistributionChart: echarts.ECharts | null = null

// 城市景区数量数据
interface CityDistrict {
  name: string;
  value: number;
}

interface CityDataItem {
  name: string;
  value: number;
  districts: CityDistrict[];
}

interface CityLevelDataItem {
  name: string;
  value: number;
  level5A: number;
  level4A: number;
  level3A: number;
  levelOther: number;
}

interface LevelDataItem {
  name: string;
  value: number;
}

// 城市景区数量数据
const cityData: CityDataItem[] = [
  { name: '北京', value: 186, districts: [
    { name: '东城区', value: 35 },
    { name: '西城区', value: 42 },
    { name: '朝阳区', value: 28 },
    { name: '海淀区', value: 45 },
    { name: '丰台区', value: 15 },
    { name: '石景山区', value: 8 },
    { name: '门头沟区', value: 13 }
  ]},
  { name: '上海', value: 152, districts: [
    { name: '黄浦区', value: 32 },
    { name: '徐汇区', value: 25 },
    { name: '长宁区', value: 18 },
    { name: '静安区', value: 30 },
    { name: '普陀区', value: 14 },
    { name: '虹口区', value: 10 },
    { name: '杨浦区', value: 23 }
  ]},
  { name: '广州', value: 138, districts: [
    { name: '越秀区', value: 28 },
    { name: '海珠区', value: 22 },
    { name: '荔湾区', value: 19 },
    { name: '天河区', value: 31 },
    { name: '白云区', value: 15 },
    { name: '黄埔区', value: 12 },
    { name: '番禺区', value: 11 }
  ]},
  { name: '深圳', value: 125, districts: [
    { name: '福田区', value: 32 },
    { name: '罗湖区', value: 24 },
    { name: '南山区', value: 35 },
    { name: '宝安区', value: 18 },
    { name: '龙岗区', value: 16 }
  ]},
  { name: '杭州', value: 174, districts: [
    { name: '上城区', value: 28 },
    { name: '下城区', value: 22 },
    { name: '江干区', value: 19 },
    { name: '拱墅区', value: 15 },
    { name: '西湖区', value: 45 },
    { name: '滨江区', value: 18 },
    { name: '萧山区', value: 27 }
  ]},
  { name: '南京', value: 142, districts: [] },
  { name: '成都', value: 165, districts: [] },
  { name: '重庆', value: 152, districts: [] },
  { name: '西安', value: 145, districts: [] },
  { name: '武汉', value: 132, districts: [] },
  { name: '厦门', value: 105, districts: [] },
  { name: '苏州', value: 128, districts: [] },
  { name: '天津', value: 118, districts: [] },
  { name: '青岛', value: 97, districts: [] }
]

// 城市坐标数据
const cityGeoCoords: Record<string, [number, number]> = {
  '北京': [116.46, 39.92],
  '上海': [121.48, 31.22],
  '广州': [113.23, 23.16],
  '深圳': [114.07, 22.62],
  '杭州': [120.21, 30.25],
  '南京': [118.78, 32.04],
  '成都': [104.06, 30.67],
  '重庆': [106.55, 29.56],
  '西安': [108.95, 34.26],
  '武汉': [114.31, 30.59],
  '厦门': [118.09, 24.48],
  '苏州': [120.62, 31.32],
  '天津': [117.20, 39.13],
  '青岛': [120.38, 36.06],
  '哈尔滨': [126.63, 45.75],
  '大连': [121.62, 38.92],
  '南宁': [108.33, 22.84],
  '昆明': [102.73, 25.04],
  '拉萨': [91.11, 29.97],
  '三亚': [109.50, 18.25]
}

// 更多城市数据（用于城市分布横向柱状图）
const allCitiesData: CityLevelDataItem[] = [
  { name: '北京', value: 186, level5A: 18, level4A: 42, level3A: 78, levelOther: 48 },
  { name: '上海', value: 152, level5A: 15, level4A: 35, level3A: 65, levelOther: 37 },
  { name: '广州', value: 138, level5A: 12, level4A: 32, level3A: 60, levelOther: 34 },
  { name: '深圳', value: 125, level5A: 10, level4A: 28, level3A: 55, levelOther: 32 },
  { name: '杭州', value: 174, level5A: 16, level4A: 40, level3A: 75, levelOther: 43 },
  { name: '南京', value: 142, level5A: 14, level4A: 32, level3A: 62, levelOther: 34 },
  { name: '成都', value: 165, level5A: 15, level4A: 38, level3A: 72, levelOther: 40 },
  { name: '重庆', value: 152, level5A: 14, level4A: 35, level3A: 66, levelOther: 37 },
  { name: '西安', value: 145, level5A: 13, level4A: 33, level3A: 63, levelOther: 36 },
  { name: '武汉', value: 132, level5A: 12, level4A: 30, level3A: 58, levelOther: 32 },
  { name: '厦门', value: 105, level5A: 10, level4A: 24, level3A: 46, levelOther: 25 },
  { name: '苏州', value: 128, level5A: 11, level4A: 29, level3A: 56, levelOther: 32 },
  { name: '天津', value: 118, level5A: 10, level4A: 27, level3A: 52, levelOther: 29 },
  { name: '青岛', value: 97, level5A: 9, level4A: 22, level3A: 42, levelOther: 24 },
  { name: '哈尔滨', value: 86, level5A: 8, level4A: 20, level3A: 37, levelOther: 21 },
  { name: '大连', value: 93, level5A: 9, level4A: 21, level3A: 41, levelOther: 22 },
  { name: '南宁', value: 112, level5A: 10, level4A: 26, level3A: 49, levelOther: 27 },
  { name: '昆明', value: 147, level5A: 13, level4A: 34, level3A: 64, levelOther: 36 },
  { name: '拉萨', value: 78, level5A: 7, level4A: 18, level3A: 34, levelOther: 19 },
  { name: '三亚', value: 134, level5A: 12, level4A: 31, level3A: 58, levelOther: 33 }
]

// 城市景区级别分布数据
const levelData: LevelDataItem[] = [
  { name: '5A级景区', value: 302 },
  { name: '4A级景区', value: 854 },
  { name: '3A级景区', value: 1256 },
  { name: '2A级景区', value: 782 },
  { name: '其他', value: 368 }
]

// 初始化图表
onMounted(() => {
  // 使用nextTick确保DOM已经渲染完成
  nextTick(() => {
    // 初始化各图表实例
    if (cityBarChartRef.value) {
      cityBarChart = echarts.init(cityBarChartRef.value)
      initCityBarChart()
    }
    
    if (cityMapChartRef.value) {
      cityMapChart = echarts.init(cityMapChartRef.value)
      initCityMapChart()
    }
    
    if (levelChartRef.value) {
      levelChart = echarts.init(levelChartRef.value)
      initLevelChart()
    }
    
    if (cityDistributionChartRef.value) {
      cityDistributionChart = echarts.init(cityDistributionChartRef.value)
      initCityDistributionChart()
    }
  })
  
  // 监听窗口大小变化
  window.addEventListener('resize', resizeCharts)
})

// 监听城市选择变化
watch(selectedCity, () => {
  updateCityBarChart()
  updateCityMapChart()
})

// 监听级别选择变化
watch(selectedLevel, () => {
  updateLevelChart()
})

// 监听级别选择对城市分布图的影响
watch(selectedLevelForCity, () => {
  updateCityDistributionChart()
})

// 初始化所有图表
const initCharts = () => {
  // 由于在onMounted中已经初始化了图表，这里可以为空或移除
}

// 重置图表大小
const resizeCharts = () => {
  cityBarChart?.resize()
  cityMapChart?.resize()
  levelChart?.resize()
  cityDistributionChart?.resize()
}

// 初始化城市景区数量柱状图
const initCityBarChart = () => {
  if (!cityBarChartRef.value) return
  
  cityBarChart = echarts.init(cityBarChartRef.value)
  updateCityBarChart()
  
  // 添加点击事件，联动热力图
  cityBarChart.on('click', (params) => {
    if (selectedCity.value === params.name) {
      // 如果点击当前选中的城市，则重置
      resetCityView()
    } else {
      // 否则设置选中的城市
      selectedCity.value = params.name
      selectedCityData.value = cityData.find(item => item.name === params.name)
    }
  })
}

// 更新城市景区数量柱状图
const updateCityBarChart = () => {
  if (!cityBarChart) return
  
  // 根据是否有选中的城市决定显示的数据
  const data = selectedCity.value && selectedCityData.value?.districts?.length > 0
    ? selectedCityData.value.districts
    : cityData

  // 设置柱状图选项
  const option = {
    title: {
      text: selectedCity.value ? `${selectedCity.value}各区景区数量分布` : '城市景区数量分布',
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
      data: data.map((item: CityDataItem | CityDistrict) => item.name),
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
        barWidth: '60%',
        data: data.map((item: CityDataItem | CityDistrict) => ({
          value: item.value,
          itemStyle: {
            color: item.name === selectedCity.value 
              ? '#ff6b6b' 
              : new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#83bff6' },
                  { offset: 0.5, color: '#188df0' },
                  { offset: 1, color: '#188df0' }
                ])
          }
        })),
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#5470c6' },
              { offset: 0.7, color: '#3c5fe0' },
              { offset: 1, color: '#3c5fe0' }
            ])
          }
        }
      }
    ]
  }
  
  cityBarChart.setOption(option)
}

// 初始化城市景区热力图
const initCityMapChart = () => {
  if (!cityMapChartRef.value || !cityMapChart) return
  
  // 尝试加载中国地图
  fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    .then(response => response.json())
    .then(chinaJson => {
      // 注册地图
      echarts.registerMap('china', chinaJson);
      // 更新地图
      updateCityMapChart();
    })
    .catch(() => {
      console.error('无法加载中国地图数据，尝试使用内置地图');
      updateCityMapChart();
    });
  
  // 添加地图点击事件，返回全国视图
  cityMapChart.on('click', (params) => {
    if (params.componentType === 'geo') {
      resetCityView()
    }
  })
}

// 更新城市景区热力图
const updateCityMapChart = () => {
  if (!cityMapChart) return
  
  let mapOption: any = {}
  
  if (selectedCity.value && selectedCityData.value?.districts?.length > 0) {
    // 如果选中了城市，显示城市内部景区分布热力图
    // 注意：这里简化处理，实际应加载具体城市地图数据
    mapOption = {
      title: {
        text: `${selectedCity.value}景区分布热力图`,
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c}个景区'
      },
      visualMap: {
        min: 0,
        max: Math.max(...selectedCityData.value.districts.map((d: any) => d.value)),
        calculable: true,
        inRange: {
          color: ['#50a3ba', '#eac736', '#d94e5d']
        },
        textStyle: {
          color: '#333'
        }
      },
      series: [
        {
          name: `${selectedCity.value}景区分布`,
          type: 'map',
          map: selectedCity.value, // 这里需要加载具体城市地图，简化处理
          roam: true,
          emphasis: {
            label: {
              show: true
            },
            itemStyle: {
              areaColor: '#e6e6e6'
            }
          },
          data: selectedCityData.value.districts.map((district: any) => ({
            name: district.name,
            value: district.value
          }))
        }
      ]
    }
  } else {
    // 全国景区分布热力图
    mapOption = {
      backgroundColor: '#fff',
      title: {
        text: '全国景区分布热力图',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: function(params: any) {
          if (params.componentType === 'series' && params.seriesType === 'scatter') {
            return `${params.name}: ${params.value[2]}个景区`
          }
          return ''
        }
      },
      visualMap: {
        min: 0,
        max: 200,
        calculable: true,
        inRange: {
          color: ['#50a3ba', '#eac736', '#d94e5d']
        },
        textStyle: {
          color: '#333'
        }
      },
      geo: {
        map: 'china',
        roam: false,
        zoom: 1.2,
        label: {
          show: true,
          fontSize: 8,
          color: '#333'
        },
        itemStyle: {
          areaColor: '#f3f3f3',
          borderColor: '#ccc',
          borderWidth: 1
        },
        emphasis: {
          itemStyle: {
            areaColor: '#e6e6e6'
          }
        }
      },
      series: [
        {
          name: '景区数量',
          type: 'scatter',
          coordinateSystem: 'geo',
          data: cityData.map(city => {
            const geoCoord = cityGeoCoords[city.name]
            if (geoCoord) {
              return {
                name: city.name,
                value: [...geoCoord, city.value]
              }
            }
            return null
          }).filter(item => item !== null),
          symbolSize: function(val: any) {
            return val[2] > 0 ? Math.sqrt(val[2]) * 3 : 0
          },
          label: {
            show: false
          },
          itemStyle: {
            color: '#f4e925',
            shadowBlur: 10,
            shadowColor: '#333'
          },
          emphasis: {
            label: {
              show: true,
              formatter: '{b}'
            }
          }
        }
      ]
    }
  }
  
  cityMapChart.setOption(mapOption, true)
}

// 重置城市视图
const resetCityView = () => {
  selectedCity.value = ''
  selectedCityData.value = null
  
  updateCityBarChart()
  updateCityMapChart()
}

// 初始化景区级别分布饼图
const initLevelChart = () => {
  if (!levelChartRef.value) return
  
  levelChart = echarts.init(levelChartRef.value)
  updateLevelChart()
  
  // 添加点击事件，联动城市分布图
  levelChart.on('click', (params) => {
    // 提取级别标识
    const level = params.name.includes('5A') ? '5A' : 
                  params.name.includes('4A') ? '4A' : 
                  params.name.includes('3A') ? '3A' : 'other'
                  
    // 如果点击当前选中的级别，则清除过滤
    if (selectedLevelForCity.value === level) {
      selectedLevelForCity.value = ''
    } else {
      selectedLevelForCity.value = level
    }
  })
}

// 更新景区级别分布饼图
const updateLevelChart = () => {
  if (!levelChart) return
  
  // 根据选择的级别过滤数据
  let seriesData = []
  if (selectedLevel.value === '') {
    // 显示所有级别
    seriesData = levelData
  } else {
    // 仅显示选中的级别
    seriesData = levelData.filter(item => 
      item.name.includes(selectedLevel.value === 'other' ? 'A级' : selectedLevel.value)
    )
  }
  
  // 设置图表选项
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: seriesData.map(item => item.name)
    },
    series: [
      {
        name: selectedLevel.value ? `${selectedLevel.value}级景区分布` : '景区级别分布',
        type: 'pie',
        radius: ['50%', '70%'],
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
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: seriesData.map(item => ({
          value: item.value,
          name: item.name,
          itemStyle: {
            color: item.name === '5A级景区' ? '#ee6666' : 
                  item.name === '4A级景区' ? '#fac858' : 
                  item.name === '3A级景区' ? '#91cc75' : 
                  item.name === '2A级景区' ? '#73c0de' : '#3ba272'
          }
        }))
      }
    ]
  }
  
  levelChart.setOption(option)
}

// 初始化景区城市分布横向柱状图
const initCityDistributionChart = () => {
  if (!cityDistributionChartRef.value) return
  
  cityDistributionChart = echarts.init(cityDistributionChartRef.value)
  updateCityDistributionChart()
}

// 更新景区城市分布横向柱状图
const updateCityDistributionChart = () => {
  if (!cityDistributionChart) return
  
  // 根据选择的级别过滤数据
  let filteredData = [...allCitiesData]
  
  // 排序城市数据（按总量降序）
  filteredData.sort((a, b) => {
    // 如果有级别过滤，按照对应级别的数量排序
    if (selectedLevelForCity.value === '5A') {
      return b.level5A - a.level5A
    } else if (selectedLevelForCity.value === '4A') {
      return b.level4A - a.level4A
    } else if (selectedLevelForCity.value === '3A') {
      return b.level3A - a.level3A
    } else if (selectedLevelForCity.value === 'other') {
      return b.levelOther - a.levelOther
    }
    // 默认按总量排序
    return b.value - a.value
  })
  
  // 限制显示前15个城市，避免图表过于拥挤
  filteredData = filteredData.slice(0, 15)
  
  // 选择要显示的数据系列
  let seriesData: number[] = []
  if (selectedLevelForCity.value === '5A') {
    seriesData = filteredData.map(item => item.level5A)
  } else if (selectedLevelForCity.value === '4A') {
    seriesData = filteredData.map(item => item.level4A)
  } else if (selectedLevelForCity.value === '3A') {
    seriesData = filteredData.map(item => item.level3A)
  } else if (selectedLevelForCity.value === 'other') {
    seriesData = filteredData.map(item => item.levelOther)
  } else {
    seriesData = filteredData.map(item => item.value)
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params: any) {
        const data = params[0]
        const cityData = filteredData[data.dataIndex]
        let content = `${cityData.name}<br/>`
        
        if (selectedLevelForCity.value) {
          const levelValue = selectedLevelForCity.value === '5A' ? cityData.level5A :
                            selectedLevelForCity.value === '4A' ? cityData.level4A :
                            selectedLevelForCity.value === '3A' ? cityData.level3A :
                            cityData.levelOther
          content += `${selectedLevelForCity.value}级景区: ${levelValue}个`
        } else {
          content += `景区总数: ${cityData.value}个<br/>`
          content += `5A级: ${cityData.level5A}个<br/>`
          content += `4A级: ${cityData.level4A}个<br/>`
          content += `3A级: ${cityData.level3A}个<br/>`
          content += `其他: ${cityData.levelOther}个`
        }
        
        return content
      }
    },
    title: {
      text: selectedLevelForCity.value ? `${selectedLevelForCity.value}级景区城市分布` : '景区城市分布',
      left: 'center'
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
      data: filteredData.map(item => item.name),
      axisLabel: {
        interval: 0
      }
    },
    series: [
      {
        name: selectedLevelForCity.value ? `${selectedLevelForCity.value}级景区` : '景区数量',
        type: 'bar',
        barWidth: '60%',
        data: seriesData.map((value) => ({
          value: value,
          itemStyle: {
            color: selectedLevelForCity.value === '5A' ? '#ee6666' :
                  selectedLevelForCity.value === '4A' ? '#fac858' :
                  selectedLevelForCity.value === '3A' ? '#91cc75' :
                  selectedLevelForCity.value === 'other' ? '#73c0de' :
                  new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                    { offset: 0, color: '#83bff6' },
                    { offset: 0.5, color: '#188df0' },
                    { offset: 1, color: '#188df0' }
                  ])
          }
        }))
      }
    ]
  }
  
  cityDistributionChart.setOption(option)
}

// 清除级别过滤
const clearLevelFilter = () => {
  selectedLevelForCity.value = ''
}
</script>

<style scoped>
.basic-distribution-container {
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

.data-card {
  display: flex;
  align-items: center;
  padding: 15px;
  margin-bottom: 20px;
}

.card-icon {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.card-icon .el-icon {
  font-size: 32px;
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
  height: 350px;
}

.map-container {
  height: 400px;
  margin-bottom: 20px;
}
</style> 