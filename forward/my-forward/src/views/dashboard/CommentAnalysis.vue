<template>
  <div class="comment-analysis-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <card-container title="景区评论与情感分析">
          <template #actions>
            <el-select v-model="sortType" placeholder="排序方式" size="small" @change="handleSortChange">
              <el-option label="评论数量" value="commentCount" />
              <el-option label="情感得分" value="sentimentScore" />
              <el-option label="情感强度" value="sentimentIntensity" />
            </el-select>
          </template>
          
          <div class="chart-wrapper">
            <base-chart 
              :options="scatterOptions" 
              height="450px"
              @chartClick="handleChartClick"
            />
          </div>
          
          <div class="analysis-summary">
            <h4>数据分析结论</h4>
            <ul>
              <li>情感得分较高的景区集中在国家5A级景区和知名自然风景区</li>
              <li>评论数量和情感得分呈现一定的正相关性，受欢迎的景区往往评价更高</li>
              <li>部分小众景区尽管评论数量少，但情感得分较高，表明有特色的小众景区也有良好口碑</li>
              <li>情感强度高的景区通常是那些能引起强烈情感共鸣的景区，如壮观的自然景观或独特的文化体验</li>
            </ul>
          </div>
        </card-container>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" v-if="selectedScenic">
      <el-col :span="24">
        <card-container :title="`${selectedScenic.scenicName} - 评论词云分析`">
          <template #actions>
            <el-button type="text" @click="clearSelectedScenic">返回总览</el-button>
          </template>
          
          <div class="chart-wrapper">
            <base-chart 
              :options="wordCloudOptions" 
              height="350px"
            />
          </div>
          
          <div class="analysis-detail">
            <h4>游客关注点分析</h4>
            <p>基于词云分析，游客对该景区评论中最关注的几个方面是：</p>
            <el-row :gutter="20">
              <el-col :span="8" v-for="(aspect, index) in topAspects" :key="index">
                <div class="aspect-card">
                  <h5>{{ aspect.name }}</h5>
                  <p>{{ aspect.description }}</p>
                  <div class="sentiment-indicator" :class="getSentimentClass(aspect.sentiment)">
                    {{ getSentimentLabel(aspect.sentiment) }}
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </card-container>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import CardContainer from '@/components/common/CardContainer.vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import { useScenicStore } from '@/stores/scenic'
import type { EChartsOption } from 'echarts'
import { ElMessage } from 'element-plus'
import 'echarts-wordcloud'

export default defineComponent({
  name: 'CommentAnalysis',
  components: {
    CardContainer,
    BaseChart
  },
  setup() {
    const scenicStore = useScenicStore()
    const commentData = ref<any[]>([])
    const wordCloudData = ref<any[]>([])
    const sortType = ref('commentCount')
    const selectedScenic = ref<any>(null)
    
    // 模拟顶级关注点数据
    const topAspects = ref([
      {
        name: '风景美丽',
        description: '游客普遍对景区自然风光给予高度评价',
        sentiment: 0.8
      },
      {
        name: '服务质量',
        description: '对景区工作人员的服务态度褒贬不一',
        sentiment: 0.5
      },
      {
        name: '价格合理',
        description: '大部分游客认为票价与体验匹配',
        sentiment: 0.7
      }
    ])
    
    // 情感分数转换为标签
    const getSentimentLabel = (score: number) => {
      if (score >= 0.7) return '非常正面'
      if (score >= 0.5) return '较为正面'
      if (score >= 0.3) return '中性偏正面'
      if (score >= 0.0) return '中性'
      return '偏负面'
    }
    
    // 情感分数转换为样式类
    const getSentimentClass = (score: number) => {
      if (score >= 0.7) return 'very-positive'
      if (score >= 0.5) return 'positive'
      if (score >= 0.3) return 'neutral-positive'
      if (score >= 0.0) return 'neutral'
      return 'negative'
    }
    
    // 散点图配置
    const scatterOptions = computed<EChartsOption>(() => ({
      title: {
        text: '景区评论数量与情感得分关系',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: function(params: any) {
          const data = params.data
          return `${data[3]}<br/>评论数量: ${data[0]}<br/>情感得分: ${data[1]}<br/>情感强度: ${data[2]}`
        }
      },
      xAxis: {
        name: '评论数量',
        nameLocation: 'middle',
        nameGap: 30,
        scale: true
      },
      yAxis: {
        name: '情感得分',
        nameLocation: 'middle',
        nameGap: 30,
        scale: true
      },
      visualMap: {
        min: 0,
        max: 1,
        dimension: 2,  // 情感强度维度
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 10,
        text: ['情感强烈', '情感平淡'],
        inRange: {
          color: ['#50a3ba', '#eac736', '#d94e5d']
        }
      },
      grid: {
        top: 60,
        bottom: 90
      },
      series: [
        {
          type: 'scatter',
          symbolSize: function(data: any) {
            // 基于评论数量调整点的大小
            return Math.sqrt(data[0]) / 5 + 10
          },
          data: commentData.value.map(item => [
            item.commentCount,
            item.sentimentScore,
            item.sentimentIntensity,
            item.scenicName
          ]),
          emphasis: {
            focus: 'series',
            label: {
              show: true,
              formatter: function(param: any) {
                return param.data[3]
              },
              position: 'top'
            }
          }
        }
      ]
    }))
    
    // 词云图配置
    const wordCloudOptions = computed(() => ({
      title: {
        text: selectedScenic.value ? `${selectedScenic.value.scenicName} 热门评论词` : '热门评论词',
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
        width: '80%',
        height: '80%',
        right: undefined,
        bottom: undefined,
        sizeRange: [12, 60],
        rotationRange: [-45, 45],
        rotationStep: 10,
        gridSize: 8,
        drawOutOfBound: false,
        textStyle: {
          fontFamily: 'sans-serif',
          fontWeight: 'bold',
          color: function() {
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
        data: wordCloudData.value.length ? wordCloudData.value : [
          { name: '数据加载中', value: 10 }
        ]
      }]
    } as any))
    
    // 获取评论分析数据
    const fetchCommentData = async () => {
      try {
        // 应该从API获取数据，这里使用模拟数据
        const mockData = generateMockCommentData()
        commentData.value = mockData
        
        // 加载完成后排序
        sortCommentData()
      } catch (error) {
        console.error('获取评论数据失败:', error)
        ElMessage.error('获取评论数据失败')
      }
    }
    
    // 获取词云数据
    const fetchWordCloudData = async (scenicId: string) => {
      try {
        // 应该从API获取数据，这里使用模拟数据
        const mockData = generateMockWordCloudData()
        wordCloudData.value = mockData
      } catch (error) {
        console.error('获取词云数据失败:', error)
        ElMessage.error('获取词云数据失败')
      }
    }
    
    // 生成模拟评论数据
    const generateMockCommentData = () => {
      const scenicNames = [
        '故宫博物院', '颐和园', '八达岭长城', '西湖风景区', '黄山风景区',
        '泰山风景区', '峨眉山', '九寨沟', '桂林山水', '张家界', '敦煌莫高窟',
        '布达拉宫', '三亚湾', '鼓浪屿', '秦始皇兵马俑', '乐山大佛', '承德避暑山庄'
      ]
      
      return scenicNames.map((name, index) => {
        const commentCount = Math.floor(Math.random() * 3000) + 500
        const sentimentScore = Math.random() * 0.5 + 0.5  // 0.5-1.0
        const sentimentIntensity = Math.random() * 0.8 + 0.2  // 0.2-1.0
        
        return {
          scenicId: 'scenic_' + (index + 1),
          scenicName: name,
          commentCount,
          sentimentScore,
          sentimentIntensity
        }
      })
    }
    
    // 生成模拟词云数据
    const generateMockWordCloudData = () => {
      const words = [
        '美丽', '壮观', '震撼', '人多', '值得', '壮丽', '惊艳', '历史', '文化',
        '自然', '景色', '服务', '环境', '交通', '方便', '价格', '实惠', '拥挤',
        '清净', '古老', '独特', '奇特', '舒适', '气势', '磅礴', '宏伟', '辉煌'
      ]
      
      return words.map(word => ({
        name: word,
        value: Math.floor(Math.random() * 500) + 100
      }))
    }
    
    // 排序评论数据
    const sortCommentData = () => {
      if (sortType.value === 'commentCount') {
        commentData.value.sort((a, b) => b.commentCount - a.commentCount)
      } else if (sortType.value === 'sentimentScore') {
        commentData.value.sort((a, b) => b.sentimentScore - a.sentimentScore)
      } else if (sortType.value === 'sentimentIntensity') {
        commentData.value.sort((a, b) => b.sentimentIntensity - a.sentimentIntensity)
      }
    }
    
    // 处理排序变更
    const handleSortChange = () => {
      sortCommentData()
    }
    
    // 处理图表点击事件
    const handleChartClick = (params: any) => {
      const index = params.dataIndex
      if (index >= 0 && index < commentData.value.length) {
        selectedScenic.value = commentData.value[index]
        fetchWordCloudData(selectedScenic.value.scenicId)
      }
    }
    
    // 清除选中的景区
    const clearSelectedScenic = () => {
      selectedScenic.value = null
    }
    
    onMounted(() => {
      fetchCommentData()
    })
    
    return {
      commentData,
      wordCloudData,
      sortType,
      selectedScenic,
      topAspects,
      scatterOptions,
      wordCloudOptions,
      handleSortChange,
      handleChartClick,
      clearSelectedScenic,
      getSentimentLabel,
      getSentimentClass
    }
  }
})
</script>

<style scoped>
.comment-analysis-container {
  padding: 20px;
}

.chart-wrapper {
  width: 100%;
  margin-bottom: 20px;
}

.analysis-summary, .analysis-detail {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
}

.analysis-summary h4, .analysis-detail h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #303133;
}

.analysis-summary ul {
  padding-left: 20px;
  margin: 0;
}

.analysis-summary li {
  margin-bottom: 8px;
}

.aspect-card {
  background-color: white;
  border-radius: 4px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  height: 100%;
  margin-bottom: 15px;
}

.aspect-card h5 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
}

.aspect-card p {
  color: #606266;
  font-size: 14px;
}

.sentiment-indicator {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-top: 10px;
}

.very-positive {
  background-color: #67c23a;
  color: white;
}

.positive {
  background-color: #85ce61;
  color: white;
}

.neutral-positive {
  background-color: #e6a23c;
  color: white;
}

.neutral {
  background-color: #909399;
  color: white;
}

.negative {
  background-color: #f56c6c;
  color: white;
}
</style> 