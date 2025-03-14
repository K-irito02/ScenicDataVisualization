<template>
  <div class="comment-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <h2>评论与情感分析</h2>
          <p>本模块提供全国景区游客评论的情感分析，帮助您了解游客对不同景区的情感倾向和评价强度。</p>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>情感倾向分布</span>
              <div>
                <el-select v-model="sentimentFilter" placeholder="筛选条件" size="small" style="margin-right: 10px">
                  <el-option label="按城市" value="city"></el-option>
                  <el-option label="按景区级别" value="level"></el-option>
                  <el-option label="按季节" value="season"></el-option>
                  <el-option label="全部数据" value="all"></el-option>
                </el-select>
                <el-select 
                  v-if="sentimentFilter !== 'all'" 
                  v-model="filterValue" 
                  :placeholder="getFilterPlaceholder()" 
                  size="small"
                >
                  <el-option 
                    v-for="option in getFilterOptions()" 
                    :key="option.value" 
                    :label="option.label" 
                    :value="option.value"
                  ></el-option>
                </el-select>
              </div>
            </div>
          </template>
          <div class="chart-container" ref="sentimentPieChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>情感得分-强度分析</span>
            </div>
          </template>
          <div class="chart-container" ref="sentimentBubbleChartRef"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>热门评论关键词</span>
              <el-radio-group v-model="keywordType" size="small">
                <el-radio-button label="positive">正面</el-radio-button>
                <el-radio-button label="negative">负面</el-radio-button>
                <el-radio-button label="all">全部</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="keywordCloudRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>情感评分趋势</span>
              <el-select v-model="trendScenicSpot" placeholder="选择景区" size="small">
                <el-option label="故宫博物院" value="故宫博物院"></el-option>
                <el-option label="黄山风景区" value="黄山风景区"></el-option>
                <el-option label="长城" value="长城"></el-option>
                <el-option label="张家界" value="张家界"></el-option>
                <el-option label="西湖" value="西湖"></el-option>
                <el-option label="平均水平" value="average"></el-option>
              </el-select>
            </div>
          </template>
          <div class="chart-container" ref="trendChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>典型评论摘要</span>
              <el-radio-group v-model="commentFilter" size="small">
                <el-radio-button label="excellent">优评</el-radio-button>
                <el-radio-button label="good">良评</el-radio-button>
                <el-radio-button label="negative">差评</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <el-table :data="getFilteredComments()" style="width: 100%">
            <el-table-column prop="scenicName" label="景区名称" width="150" />
            <el-table-column prop="username" label="用户" width="120">
              <template #default="scope">
                <el-avatar :size="24" class="user-avatar">{{ scope.row.username.substring(0, 1) }}</el-avatar>
                <span style="margin-left: 8px">{{ scope.row.username }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="评论内容" show-overflow-tooltip />
            <el-table-column prop="date" label="评论时间" width="120" />
            <el-table-column prop="sentiment" label="情感倾向" width="100">
              <template #default="scope">
                <el-tag :type="getSentimentTagType(scope.row.sentiment)">
                  {{ getSentimentLabel(scope.row.sentiment) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="评分" width="100">
              <template #default="scope">
                <el-rate v-model="scope.row.score" disabled text-color="#ff9900"></el-rate>
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
import 'echarts-wordcloud'

// 筛选条件
const sentimentFilter = ref('all')
const filterValue = ref('')
const keywordType = ref('all')
const trendScenicSpot = ref('average')
const commentFilter = ref('excellent')

// 图表引用
const sentimentPieChartRef = ref<HTMLElement | null>(null)
const sentimentBubbleChartRef = ref<HTMLElement | null>(null)
const keywordCloudRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)

// 图表实例
let sentimentPieChart: echarts.ECharts | null = null
let sentimentBubbleChart: echarts.ECharts | null = null
let keywordCloudChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// 评论数据
const commentsData = [
  {
    scenicName: '故宫博物院',
    username: '旅行者123',
    content: '故宫真是太壮观了！建筑宏伟，历史文化底蕴深厚。就是人太多了，建议避开节假日前往。讲解员很专业，了解了很多历史知识。',
    date: '2023-05-15',
    sentiment: 'excellent',
    score: 5
  },
  {
    scenicName: '黄山风景区',
    username: '山水客',
    content: '黄山云海绝美，日出壮观！住山上比较贵，但值得体验。山路有点陡，老人小孩需要注意安全。索道设施很好，服务也不错。',
    date: '2023-06-20',
    sentiment: 'excellent',
    score: 5
  },
  {
    scenicName: '张家界',
    username: '自由行者',
    content: '景色确实不错，但商业化太严重了。各种额外消费项目，感觉被宰。门票加上各种小交通费用下来一天至少500+，性价比不高。',
    date: '2023-07-12',
    sentiment: 'negative',
    score: 2
  },
  {
    scenicName: '西湖',
    username: '城市漫步',
    content: '西湖景色宜人，环境优美，免费开放很良心。断桥残雪人太多，拍照困难。其他景点如雷峰塔、三潭印月等都很值得一去。',
    date: '2023-08-05',
    sentiment: 'good',
    score: 4
  },
  {
    scenicName: '长城',
    username: '历史爱好者',
    content: '八达岭长城修缮得很好，但游客太多影响体验。建议去人少的司马台或慕田峪段。爬上去很累但风景绝佳，值得一去。',
    date: '2023-09-10',
    sentiment: 'good',
    score: 4
  },
  {
    scenicName: '九寨沟',
    username: '自然控',
    content: '九寨沟的水色简直太惊艳了！蓝色、绿色、碧色变幻，美不胜收。交通不便，但绝对值得远途跋涉。景区管理很好，环保做得不错。',
    date: '2023-10-15',
    sentiment: 'excellent',
    score: 5
  },
  {
    scenicName: '鼓浪屿',
    username: '岛屿梦想',
    content: '岛上建筑风格独特，历史感强。但商业化严重，到处都是游客和商店，失去了原有的宁静氛围。住宿偏贵，性价比一般。',
    date: '2023-07-28',
    sentiment: 'good',
    score: 3
  },
  {
    scenicName: '兵马俑',
    username: '考古迷',
    content: '震撼！中国古代工艺的巅峰之作。展馆设计合理，就是人太多，建议请导游讲解，不然看不出门道。周边餐饮和纪念品很贵。',
    date: '2023-08-30',
    sentiment: 'excellent',
    score: 5
  },
  {
    scenicName: '峨眉山',
    username: '登山者',
    content: '山路陡峭难行，索道排队时间长。猴子有些凶，游客需要注意。金顶云海很美，但住宿条件一般，价格偏高，性价比不高。',
    date: '2023-09-18',
    sentiment: 'negative',
    score: 2
  }
]

// 获取筛选占位符
const getFilterPlaceholder = () => {
  if (sentimentFilter.value === 'city') return '选择城市'
  if (sentimentFilter.value === 'level') return '选择景区级别'
  if (sentimentFilter.value === 'season') return '选择季节'
  return '选择筛选条件'
}

// 获取筛选选项
const getFilterOptions = () => {
  if (sentimentFilter.value === 'city') {
    return [
      { label: '北京', value: 'beijing' },
      { label: '上海', value: 'shanghai' },
      { label: '杭州', value: 'hangzhou' },
      { label: '西安', value: 'xian' },
      { label: '成都', value: 'chengdu' }
    ]
  } else if (sentimentFilter.value === 'level') {
    return [
      { label: '5A级景区', value: '5A' },
      { label: '4A级景区', value: '4A' },
      { label: '3A级景区', value: '3A' }
    ]
  } else if (sentimentFilter.value === 'season') {
    return [
      { label: '春季', value: 'spring' },
      { label: '夏季', value: 'summer' },
      { label: '秋季', value: 'autumn' },
      { label: '冬季', value: 'winter' }
    ]
  }
  return []
}

// 获取情感标签类型
const getSentimentTagType = (sentiment: string) => {
  if (sentiment === 'excellent') return 'success'
  if (sentiment === 'good') return 'warning'
  if (sentiment === 'negative') return 'danger'
  return 'info'
}

// 获取情感标签文本
const getSentimentLabel = (sentiment: string) => {
  if (sentiment === 'excellent') return '优评'
  if (sentiment === 'good') return '良评'
  if (sentiment === 'negative') return '差评'
  return '未知'
}

// 获取筛选评论
const getFilteredComments = () => {
  return commentsData.filter(comment => comment.sentiment === commentFilter.value)
}

// 监听情感筛选变化
watch([sentimentFilter, filterValue], () => {
  nextTick(() => {
    updateSentimentPieChart()
  })
})

// 监听关键词类型变化
watch(keywordType, () => {
  nextTick(() => {
    updateKeywordCloud()
  })
})

// 监听景区趋势变化
watch(trendScenicSpot, () => {
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
  initSentimentPieChart()
  initSentimentBubbleChart()
  initKeywordCloud()
  initTrendChart()
}

// 重置图表大小
const resizeCharts = () => {
  sentimentPieChart?.resize()
  sentimentBubbleChart?.resize()
  keywordCloudChart?.resize()
  trendChart?.resize()
}

// 初始化情感饼图
const initSentimentPieChart = () => {
  if (!sentimentPieChartRef.value) return
  
  sentimentPieChart = echarts.init(sentimentPieChartRef.value)
  updateSentimentPieChart()
}

// 更新情感饼图
const updateSentimentPieChart = () => {
  if (!sentimentPieChart) return
  
  // 根据筛选条件准备数据
  let sentimentData = [
    { value: 65, name: '优评', itemStyle: { color: '#91cc75' } },
    { value: 25, name: '良评', itemStyle: { color: '#fac858' } },
    { value: 10, name: '差评', itemStyle: { color: '#ee6666' } }
  ]
  
  if (sentimentFilter.value === 'city' && filterValue.value === 'beijing') {
    sentimentData = [
      { value: 70, name: '优评', itemStyle: { color: '#91cc75' } },
      { value: 22, name: '良评', itemStyle: { color: '#fac858' } },
      { value: 8, name: '差评', itemStyle: { color: '#ee6666' } }
    ]
  } else if (sentimentFilter.value === 'level' && filterValue.value === '5A') {
    sentimentData = [
      { value: 75, name: '优评', itemStyle: { color: '#91cc75' } },
      { value: 20, name: '良评', itemStyle: { color: '#fac858' } },
      { value: 5, name: '差评', itemStyle: { color: '#ee6666' } }
    ]
  } else if (sentimentFilter.value === 'season' && filterValue.value === 'summer') {
    sentimentData = [
      { value: 55, name: '优评', itemStyle: { color: '#91cc75' } },
      { value: 30, name: '良评', itemStyle: { color: '#fac858' } },
      { value: 15, name: '差评', itemStyle: { color: '#ee6666' } }
    ]
  }
  
  const option = {
    title: {
      text: '游客情感倾向分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: '15%',
      top: 'center',
      data: sentimentData.map(item => item.name)
    },
    series: [
      {
        name: '情感倾向',
        type: 'pie',
        radius: '50%',
        center: ['60%', '50%'],
        label: {
          formatter: '{b}: {c} ({d}%)'
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        data: sentimentData
      }
    ]
  }
  
  sentimentPieChart.setOption(option)
}

// 初始化情感气泡图
const initSentimentBubbleChart = () => {
  if (!sentimentBubbleChartRef.value) return
  
  sentimentBubbleChart = echarts.init(sentimentBubbleChartRef.value)
  
  const data = [
    // [情感得分(0-400), 情感强度(0-0.5), 评论数量, 景区名称]
    [350, 0.45, 168, '故宫博物院'],
    [320, 0.4, 152, '长城'],
    [310, 0.38, 142, '黄山'],
    [290, 0.35, 130, '西湖'],
    [280, 0.42, 125, '兵马俑'],
    [275, 0.3, 118, '张家界'],
    [260, 0.25, 110, '九寨沟'],
    [240, 0.38, 105, '峨眉山'],
    [230, 0.42, 100, '泰山'],
    [220, 0.32, 95, '鼓浪屿'],
    [210, 0.28, 90, '千岛湖'],
    [200, 0.35, 85, '武当山'],
    [190, 0.22, 82, '三亚'],
    [180, 0.18, 78, '丽江'],
    [170, 0.15, 75, '苏州园林'],
    [160, 0.25, 70, '布达拉宫'],
    [150, 0.3, 68, '五台山'],
    [140, 0.35, 65, '颐和园'],
    [130, 0.15, 62, '秦皇岛'],
    [120, 0.1, 58, '漓江'],
    [110, 0.08, 54, '三清山'],
    [100, 0.05, 50, '天山天池']
  ]
  
  const option = {
    title: {
      text: '景区情感得分与强度分析',
      left: 'center'
    },
    legend: {
      right: '10%',
      top: '3%',
      data: ['情感分析']
    },
    grid: {
      left: '8%',
      right: '8%',
      bottom: '10%'
    },
    xAxis: {
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      },
      name: '情感得分',
      nameLocation: 'middle',
      nameGap: 30,
      min: 50,
      max: 400
    },
    yAxis: {
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      },
      scale: true,
      name: '情感强度',
      nameLocation: 'middle',
      nameGap: 35,
      min: 0,
      max: 0.5
    },
    tooltip: {
      formatter: function(params: any) {
        return `${params.data[3]}<br/>
                情感得分: ${params.data[0]}<br/>
                情感强度: ${params.data[1]}<br/>
                评论量: ${params.data[2]}`
      }
    },
    series: [
      {
        name: '情感分析',
        type: 'scatter',
        symbolSize: function(data: any) {
          return Math.sqrt(data[2]) * 2
        },
        itemStyle: {
          color: function(params: any) {
            const value = params.data[0]
            if (value >= 300) return '#91cc75'  // 高分
            if (value >= 200) return '#fac858'  // 中高分
            if (value >= 100) return '#ee6666'  // 中低分
            return '#73c0de'                    // 低分
          }
        },
        data: data
      }
    ]
  }
  
  sentimentBubbleChart.setOption(option)
}

// 初始化关键词云
const initKeywordCloud = () => {
  if (!keywordCloudRef.value) return
  
  keywordCloudChart = echarts.init(keywordCloudRef.value)
  updateKeywordCloud()
}

// 更新关键词云
const updateKeywordCloud = () => {
  if (!keywordCloudChart) return
  
  // 准备不同类型的关键词数据
  const positiveKeywords = [
    { name: '壮观', value: 85, textStyle: { color: '#1a8f00' } },
    { name: '美丽', value: 78, textStyle: { color: '#1a8f00' } },
    { name: '震撼', value: 72, textStyle: { color: '#1a8f00' } },
    { name: '值得', value: 68, textStyle: { color: '#1a8f00' } },
    { name: '服务好', value: 65, textStyle: { color: '#1a8f00' } },
    { name: '历史', value: 62, textStyle: { color: '#1a8f00' } },
    { name: '风景', value: 60, textStyle: { color: '#1a8f00' } },
    { name: '干净', value: 58, textStyle: { color: '#1a8f00' } },
    { name: '便利', value: 56, textStyle: { color: '#1a8f00' } },
    { name: '文化', value: 55, textStyle: { color: '#1a8f00' } },
    { name: '推荐', value: 52, textStyle: { color: '#1a8f00' } },
    { name: '专业', value: 50, textStyle: { color: '#1a8f00' } },
    { name: '精彩', value: 48, textStyle: { color: '#1a8f00' } },
    { name: '舒适', value: 45, textStyle: { color: '#1a8f00' } },
    { name: '宏伟', value: 42, textStyle: { color: '#1a8f00' } }
  ]
  
  const negativeKeywords = [
    { name: '拥挤', value: 70, textStyle: { color: '#c92a2a' } },
    { name: '贵', value: 65, textStyle: { color: '#c92a2a' } },
    { name: '商业化', value: 60, textStyle: { color: '#c92a2a' } },
    { name: '排队', value: 55, textStyle: { color: '#c92a2a' } },
    { name: '宰客', value: 50, textStyle: { color: '#c92a2a' } },
    { name: '一般', value: 45, textStyle: { color: '#c92a2a' } },
    { name: '不值', value: 42, textStyle: { color: '#c92a2a' } },
    { name: '脏乱', value: 40, textStyle: { color: '#c92a2a' } },
    { name: '交通不便', value: 38, textStyle: { color: '#c92a2a' } },
    { name: '坑', value: 35, textStyle: { color: '#c92a2a' } },
    { name: '无聊', value: 32, textStyle: { color: '#c92a2a' } },
    { name: '失望', value: 30, textStyle: { color: '#c92a2a' } },
    { name: '服务差', value: 28, textStyle: { color: '#c92a2a' } },
    { name: '噪音大', value: 25, textStyle: { color: '#c92a2a' } },
    { name: '不推荐', value: 22, textStyle: { color: '#c92a2a' } }
  ]
  
  // 根据筛选类型选择数据
  let data = []
  
  if (keywordType.value === 'positive') {
    data = positiveKeywords
  } else if (keywordType.value === 'negative') {
    data = negativeKeywords
  } else {
    data = [...positiveKeywords, ...negativeKeywords]
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
        width: '90%',
        height: '90%',
        right: null,
        bottom: null,
        sizeRange: [12, 45],
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
  
  keywordCloudChart.setOption(option)
}

// 初始化趋势图
const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  trendChart = echarts.init(trendChartRef.value)
  updateTrendChart()
}

// 更新趋势图
const updateTrendChart = () => {
  if (!trendChart) return
  
  // 准备各景区月度情感评分数据
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  
  // 各景区情感评分数据（0-100）
  const averageData = [72, 75, 78, 82, 85, 83, 80, 78, 76, 79, 80, 78]
  const gugongData = [85, 86, 88, 90, 92, 90, 88, 85, 83, 87, 88, 86]
  const huangshanData = [80, 79, 82, 86, 90, 92, 94, 92, 88, 85, 82, 80]
  const changchengData = [82, 83, 85, 88, 90, 86, 82, 80, 84, 85, 86, 84]
  const zhangjiajiData = [75, 76, 78, 82, 85, 84, 78, 75, 73, 76, 78, 77]
  const xihuData = [78, 80, 83, 86, 88, 89, 85, 82, 80, 82, 84, 82]
  
  // 根据所选景区准备数据
  let selectedData = []
  let seriesName = '平均水平'
  
  if (trendScenicSpot.value === '故宫博物院') {
    selectedData = gugongData
    seriesName = '故宫博物院'
  } else if (trendScenicSpot.value === '黄山风景区') {
    selectedData = huangshanData
    seriesName = '黄山风景区'
  } else if (trendScenicSpot.value === '长城') {
    selectedData = changchengData
    seriesName = '长城'
  } else if (trendScenicSpot.value === '张家界') {
    selectedData = zhangjiajiData
    seriesName = '张家界'
  } else if (trendScenicSpot.value === '西湖') {
    selectedData = xihuData
    seriesName = '西湖'
  } else {
    selectedData = averageData
    seriesName = '平均水平'
  }
  
  const option = {
    title: {
      text: '月度情感评分趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params: any) {
        return `${params[0].name}<br/>${params[0].seriesName}: ${params[0].value}分`
      }
    },
    grid: {
      left: '5%',
      right: '5%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: months
    },
    yAxis: {
      type: 'value',
      name: '情感评分',
      min: 60,
      max: 100
    },
    series: [
      {
        name: seriesName,
        type: 'line',
        data: selectedData,
        smooth: true,
        lineStyle: {
          width: 3,
          color: '#5470c6'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(84, 112, 198, 0.5)' },
            { offset: 1, color: 'rgba(84, 112, 198, 0.1)' }
          ])
        },
        markPoint: {
          data: [
            { type: 'max', name: '最高分' },
            { type: 'min', name: '最低分' }
          ]
        }
      }
    ]
  }
  
  trendChart.setOption(option)
}
</script>

<style scoped>
.comment-container {
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

.user-avatar {
  background-color: #409EFF;
  color: #fff;
  vertical-align: middle;
}
</style> 