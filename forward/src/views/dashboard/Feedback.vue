<template>
  <div class="feedback-container">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>评论关键词云</span>
              <el-tooltip content="展示游客评论中出现频率最高的关键词">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="chart-container" ref="keywordCloudRef"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>评论词频分析</span>
              <el-tooltip content="展示游客评论中词语使用频率分析">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="chart-container" ref="frequencyCloudRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>交通方式与评论情感关系</span>
              <el-tooltip content="分析不同交通方式下游客的评论情感倾向">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <div class="chart-container" ref="trafficSentimentRef"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import { getCommentAnalysis, getTrafficAnalysis } from '@/api/scenic'
import type { CommentAnalysis, TrafficAnalysis } from '@/types/scenic'
import { InfoFilled } from '@element-plus/icons-vue'

// 图表实例
let keywordCloudChart: echarts.ECharts | null = null
let frequencyCloudChart: echarts.ECharts | null = null
let trafficSentimentChart: echarts.ECharts | null = null

// DOM引用
const keywordCloudRef = ref<HTMLElement | null>(null)
const frequencyCloudRef = ref<HTMLElement | null>(null)
const trafficSentimentRef = ref<HTMLElement | null>(null)

// 初始化图表
onMounted(async () => {
  await initKeywordCloud()
  await initFrequencyCloud()
  await initTrafficSentiment()
  
  // 窗口大小变化时重新调整图表大小
  window.addEventListener('resize', handleResize)
})

// 处理窗口大小变化
const handleResize = () => {
  keywordCloudChart?.resize()
  frequencyCloudChart?.resize()
  trafficSentimentChart?.resize()
}

// 初始化关键词云图
const initKeywordCloud = async () => {
  if (!keywordCloudRef.value) return
  
  // 初始化图表实例
  keywordCloudChart = echarts.init(keywordCloudRef.value)
  
  // 设置加载中
  keywordCloudChart.showLoading()
  
  try {
    // 获取评论分析数据
    const commentData = await getCommentAnalysis()
    updateKeywordCloud(commentData)
  } catch (error) {
    console.error('加载评论分析数据失败:', error)
    
    // 使用模拟数据
    const mockData: CommentAnalysis = {
      keywordCloud: [
        { word: '景色', weight: 100 },
        { word: '服务', weight: 75 },
        { word: '环境', weight: 95 },
        { word: '价格', weight: 80 },
        { word: '交通', weight: 70 },
        { word: '人多', weight: 65 },
        { word: '排队', weight: 60 },
        { word: '美丽', weight: 85 },
        { word: '干净', weight: 75 },
        { word: '拥挤', weight: 60 },
        { word: '壮观', weight: 90 },
        { word: '推荐', weight: 80 },
        { word: '值得', weight: 85 },
        { word: '特色', weight: 70 },
        { word: '文化', weight: 75 },
        { word: '历史', weight: 80 },
        { word: '自然', weight: 85 },
        { word: '方便', weight: 65 },
        { word: '体验', weight: 75 },
        { word: '传统', weight: 70 }
      ],
      frequencyCloud: [
        { word: '推荐', weight: 250 },
        { word: '值得一去', weight: 220 },
        { word: '景色优美', weight: 180 },
        { word: '人山人海', weight: 160 },
        { word: '服务态度', weight: 140 },
        { word: '环境优美', weight: 135 },
        { word: '交通便利', weight: 130 },
        { word: '历史悠久', weight: 128 },
        { word: '文化底蕴', weight: 120 },
        { word: '价格合理', weight: 115 },
        { word: '游客众多', weight: 112 },
        { word: '风景如画', weight: 110 },
        { word: '特色小吃', weight: 105 },
        { word: '自然景观', weight: 100 },
        { word: '人文景观', weight: 98 },
        { word: '气候宜人', weight: 95 },
        { word: '环境整洁', weight: 90 },
        { word: '适合拍照', weight: 88 },
        { word: '门票贵', weight: 85 },
        { word: '性价比高', weight: 80 }
      ]
    }
    
    updateKeywordCloud(mockData)
  } finally {
    keywordCloudChart.hideLoading()
  }
}

// 更新关键词云图
const updateKeywordCloud = (data: CommentAnalysis) => {
  if (!keywordCloudChart) return
  
  // 设置图表选项
  const option = {
    title: {
      text: '景区评论关键词云',
      left: 'center'
    },
    tooltip: {
      show: true
    },
    series: [{
      type: 'wordCloud',
      shape: 'circle',
      left: 'center',
      top: 'center',
      width: '90%',
      height: '90%',
      right: null,
      bottom: null,
      sizeRange: [12, 60],
      rotationRange: [-90, 90],
      rotationStep: 45,
      gridSize: 8,
      drawOutOfBound: false,
      textStyle: {
        fontFamily: 'sans-serif',
        fontWeight: 'bold',
        color: function () {
          return 'rgb(' + [
            Math.round(Math.random() * 160),
            Math.round(Math.random() * 160),
            Math.round(Math.random() * 160)
          ].join(',') + ')'
        }
      },
      emphasis: {
        focus: 'self',
        textStyle: {
          shadowBlur: 10,
          shadowColor: '#333'
        }
      },
      data: data.keywordCloud.map(item => ({
        name: item.word,
        value: item.weight
      }))
    }]
  }
  
  keywordCloudChart.setOption(option)
}

// 初始化词频云图
const initFrequencyCloud = async () => {
  if (!frequencyCloudRef.value) return
  
  // 初始化图表实例
  frequencyCloudChart = echarts.init(frequencyCloudRef.value)
  
  // 设置加载中
  frequencyCloudChart.showLoading()
  
  try {
    // 获取评论分析数据
    const commentData = await getCommentAnalysis()
    updateFrequencyCloud(commentData)
  } catch (error) {
    console.error('加载词频分析数据失败:', error)
    
    // 使用模拟数据 (与上面相同)
    const mockData: CommentAnalysis = {
      keywordCloud: [
        { word: '景色', weight: 100 },
        { word: '服务', weight: 75 },
        { word: '环境', weight: 95 },
        { word: '价格', weight: 80 },
        { word: '交通', weight: 70 },
        { word: '人多', weight: 65 },
        { word: '排队', weight: 60 },
        { word: '美丽', weight: 85 },
        { word: '干净', weight: 75 },
        { word: '拥挤', weight: 60 },
        { word: '壮观', weight: 90 },
        { word: '推荐', weight: 80 },
        { word: '值得', weight: 85 },
        { word: '特色', weight: 70 },
        { word: '文化', weight: 75 },
        { word: '历史', weight: 80 },
        { word: '自然', weight: 85 },
        { word: '方便', weight: 65 },
        { word: '体验', weight: 75 },
        { word: '传统', weight: 70 }
      ],
      frequencyCloud: [
        { word: '推荐', weight: 250 },
        { word: '值得一去', weight: 220 },
        { word: '景色优美', weight: 180 },
        { word: '人山人海', weight: 160 },
        { word: '服务态度', weight: 140 },
        { word: '环境优美', weight: 135 },
        { word: '交通便利', weight: 130 },
        { word: '历史悠久', weight: 128 },
        { word: '文化底蕴', weight: 120 },
        { word: '价格合理', weight: 115 },
        { word: '游客众多', weight: 112 },
        { word: '风景如画', weight: 110 },
        { word: '特色小吃', weight: 105 },
        { word: '自然景观', weight: 100 },
        { word: '人文景观', weight: 98 },
        { word: '气候宜人', weight: 95 },
        { word: '环境整洁', weight: 90 },
        { word: '适合拍照', weight: 88 },
        { word: '门票贵', weight: 85 },
        { word: '性价比高', weight: 80 }
      ]
    }
    
    updateFrequencyCloud(mockData)
  } finally {
    frequencyCloudChart.hideLoading()
  }
}

// 更新词频云图
const updateFrequencyCloud = (data: CommentAnalysis) => {
  if (!frequencyCloudChart) return
  
  // 设置图表选项
  const option = {
    title: {
      text: '景区评论词频分析',
      left: 'center'
    },
    tooltip: {
      show: true
    },
    series: [{
      type: 'wordCloud',
      shape: 'diamond',
      left: 'center',
      top: 'center',
      width: '90%',
      height: '90%',
      right: null,
      bottom: null,
      sizeRange: [12, 60],
      rotationRange: [0, 0],
      rotationStep: 45,
      gridSize: 8,
      drawOutOfBound: false,
      textStyle: {
        fontFamily: 'sans-serif',
        fontWeight: 'bold',
        color: function () {
          return 'rgb(' + [
            Math.round(Math.random() * 160),
            Math.round(Math.random() * 160),
            Math.round(Math.random() * 160)
          ].join(',') + ')'
        }
      },
      emphasis: {
        focus: 'self',
        textStyle: {
          shadowBlur: 10,
          shadowColor: '#333'
        }
      },
      data: data.frequencyCloud.map(item => ({
        name: item.word,
        value: item.weight
      }))
    }]
  }
  
  frequencyCloudChart.setOption(option)
}

// 初始化交通与情感关系图
const initTrafficSentiment = async () => {
  if (!trafficSentimentRef.value) return
  
  // 初始化图表实例
  trafficSentimentChart = echarts.init(trafficSentimentRef.value)
  
  // 设置加载中
  trafficSentimentChart.showLoading()
  
  try {
    // 获取交通分析数据
    const trafficData = await getTrafficAnalysis()
    updateTrafficSentiment(trafficData)
  } catch (error) {
    console.error('加载交通情感数据失败:', error)
    
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
    
    updateTrafficSentiment(mockData)
  } finally {
    trafficSentimentChart.hideLoading()
  }
}

// 更新交通与情感关系图
const updateTrafficSentiment = (data: TrafficAnalysis) => {
  if (!trafficSentimentChart) return
  
  const { sentimentByTrafficCount } = data
  
  // 准备数据
  const xAxisData = sentimentByTrafficCount.map(item => `${item.methodsCount}种`)
  const positiveData = sentimentByTrafficCount.map(item => item.positive)
  const neutralData = sentimentByTrafficCount.map(item => item.neutral)
  const negativeData = sentimentByTrafficCount.map(item => item.negative)
  
  // 设置图表选项
  const option = {
    title: {
      text: '交通方式数量与评论情感关系',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function (params: any) {
        const index = params[0].dataIndex
        let result = `<div>交通方式数量: ${sentimentByTrafficCount[index].methodsCount}种</div>`
        result += `<div>主要组合: ${sentimentByTrafficCount[index].mainMethod}</div>`
        
        for (let i = 0; i < params.length; i++) {
          const param = params[i]
          const colorSpan = `<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${param.color};"></span>`
          result += `<div>${colorSpan}${param.seriesName}: ${param.value}%</div>`
        }
        
        return result
      }
    },
    legend: {
      data: ['正面评价', '中性评价', '负面评价'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxisData
    },
    yAxis: {
      type: 'value',
      name: '评论比例 (%)'
    },
    series: [
      {
        name: '正面评价',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        itemStyle: {
          color: '#67C23A'
        },
        data: positiveData
      },
      {
        name: '中性评价',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        itemStyle: {
          color: '#E6A23C'
        },
        data: neutralData
      },
      {
        name: '负面评价',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        itemStyle: {
          color: '#F56C6C'
        },
        data: negativeData
      }
    ]
  }
  
  trafficSentimentChart.setOption(option)
}
</script>

<style scoped>
.feedback-container {
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