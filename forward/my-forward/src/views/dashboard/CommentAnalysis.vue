<template>
  <div class="comment-analysis-container">
    <el-row :gutter="20">
      <el-col :span="12">
        <card-container title="景区情感倾向分布">
          <div class="chart-wrapper">
            <base-chart 
              :options="sentimentPieOptions" 
              height="400px"
              v-loading="sentimentLoading"
            />
          </div>
          
          <div class="analysis-summary">
            <h4>数据分析结论</h4>
            <ul>
              <li>情感倾向为"优"的景区占比最大，表明大部分景区评价良好</li>
              <li>不同情感倾向的分布反映游客对景区的整体满意度</li>
              <li>情感倾向为"良"的景区比例适中，说明有一定改进空间</li>
              <li>情感倾向为"中"的景区需要重点关注，进行针对性改进</li>
            </ul>
          </div>
        </card-container>
      </el-col>
      
      <el-col :span="12">
        <card-container title="景区类型情感分析">
          <template #actions>
            <el-select v-model="selectedType" placeholder="选择景区类型" size="small" @change="handleTypeChange">
              <el-option 
                v-for="type in scenicTypes" 
                :key="type" 
                :label="type" 
                :value="type" 
              />
            </el-select>
          </template>
          
          <div class="chart-wrapper">
            <base-chart 
              :options="sentimentBubbleOptions" 
              height="500px"
              style="width: 100%;"
              v-loading="typeLoading"
            />
            
            <!-- 添加备用数据表格，确保数据可见 -->
            <div v-if="typeData.length > 0" class="data-table-backup">
              <h4>景区类型情感数据表</h4>
              <el-table 
                :data="typeData.filter(item => item.level !== 'xxx' && item.level !== 'null' && item.level !== null)" 
                stripe 
                style="width: 100%"
              >
                <el-table-column prop="level" label="景区级别" />
                <el-table-column prop="avg_sentiment_score" label="情感得分">
                  <template #default="scope">
                    {{ Math.floor(Number(scope.row.avg_sentiment_score)) }}.00
                  </template>
                </el-table-column>
                <el-table-column prop="avg_sentiment_magnitude" label="情感强度">
                  <template #default="scope">
                    {{ Number(scope.row.avg_sentiment_magnitude).toFixed(2) }}
                  </template>
                </el-table-column>
                <el-table-column prop="count" label="景区数量" />
              </el-table>
            </div>
          </div>
          
          <div class="analysis-summary">
            <h4>数据分析结论</h4>
            <ul>
              <li>随着景区等级的提高，情感得分总体呈上升趋势</li>
              <li>高等级景区通常能引起更强烈的情感反应</li>
              <li>同类型不同等级景区间的情感得分差异反映了等级评定的合理性</li>
              <li>情感强度高的景区往往具有更鲜明的特色和更好的服务</li>
            </ul>
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
import type { EChartsOption } from 'echarts'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 导入景区类型数据
import typeLevelData from '@/assets/search/type_level_data.json'

interface SentimentDistData {
  name: string;
  value: number;
}

interface TypeLevelData {
  level: string;
  avg_sentiment_score: number;
  avg_sentiment_magnitude: number;
  count: number;
}

interface TypeLevelDataMap {
  [key: string]: string[];
}

export default defineComponent({
  name: 'CommentAnalysis',
  components: {
    CardContainer,
    BaseChart
  },
  setup() {
    const sentimentData = ref<SentimentDistData[]>([])
    const typeData = ref<TypeLevelData[]>([])
    const selectedType = ref('景区')
    const sentimentLoading = ref(false)
    const typeLoading = ref(false)
    
    // 从导入的JSON中获取景区类型列表
    const scenicTypes = computed(() => {
      // 获取所有类型
      const types = typeLevelData.types || [];
      // 将"景区"替换为"A级景区"
      return types.map(type => type === '景区' ? 'A级景区' : type);
    })
    
    // 获取当前选择类型的等级列表
    const currentTypeLevels = computed(() => {
      if (selectedType.value) {
        // 根据景区类型获取对应的等级列表
        const levels = (typeLevelData.typeLevels as TypeLevelDataMap)[selectedType.value]
        return levels || []
      }
      return []
    })
    
    // 情感倾向饼图配置
    const sentimentPieOptions = computed<EChartsOption>(() => ({
      title: {
        text: '景区情感倾向分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'horizontal',
        bottom: 0,
        data: sentimentData.value.map(item => item.name)
      },
      series: [
        {
          name: '情感倾向',
          type: 'pie',
          radius: ['40%', '70%'],
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
              fontSize: 20,
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: sentimentData.value.map(item => ({
            name: item.name,
            value: item.value
          })),
          color: ['#67c23a', '#e6a23c', '#f56c6c']
        }
      ]
    }))
    
    // 情感得分与景区类型等级气泡图配置
    const sentimentBubbleOptions = computed<EChartsOption>(() => {
      // 获取当前选择类型的等级列表
      const validLevels = currentTypeLevels.value
      
      // 添加调试信息
      console.log('当前选择类型:', selectedType.value)
      console.log('后端返回数据:', typeData.value)
      console.log('有效级别列表:', validLevels)
      
      // 过滤掉xxx和null
      const filteredData = typeData.value.filter(item => {
        // 排除level为xxx或null的数据
        return item.level !== 'xxx' && 
               item.level !== 'null' && 
               item.level !== null &&
               item.level !== undefined;
      });
      
      // 极简处理，直接从过滤后的数据中提取数据
      const simplifiedData = filteredData.map(item => {
        const score = Number(item.avg_sentiment_score);
        // 使用向下取整，与表格保持一致
        return Math.floor(score); // 改为向下取整，与表格保持一致
      });
      
      // 打印额外的响应信息，确认数据正常
      console.log('原始数据中项目数量:', typeData.value.length);
      console.log('过滤后数据项目数量:', filteredData.length);
      console.log('处理后的数据项目数量:', simplifiedData.length);
      if (filteredData.length > 0) {
        console.log('第一个数据样本:', filteredData[0]);
      }
      
      // 获取X轴标签
      const xAxisLabels = filteredData.map(item => item.level);
      
      console.log('简化后的数据:', simplifiedData);
      console.log('X轴标签:', xAxisLabels);
      
      // 计算最大值，用于Y轴范围
      let maxScore = 300;
      if (simplifiedData.length > 0) {
        // 计算最大值并向上取整，去除小数部分
        const rawMax = Math.max(...simplifiedData);
        maxScore = Math.ceil(rawMax * 1.1); // 增加10%空间并向上取整
        console.log('计算的最大得分:', maxScore);
      }
      
      // 使用符合ECharts类型定义的配置
      return {
        title: {
          text: `${selectedType.value === 'A级景区' ? 'A级景区' : selectedType.value}情感得分与等级关系`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params: any) {
            const param = params[0];
            // 保持与Y轴格式一致，显示为整数.00
            return `${param.name}: ${Math.floor(param.value)}.00`;
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: xAxisLabels,
          axisLabel: {
            interval: 0, // 强制显示所有标签
            rotate: 30, // 旋转标签以防重叠
            fontSize: 12,
            margin: 8
          }
        },
        yAxis: {
          type: 'value',
          name: '情感得分',
          min: 0,
          max: maxScore,
          axisLabel: {
            formatter: function(value: number) {
              // 保留整数部分加 .00 后缀
              return Math.floor(value) + '.00';
            }
          }
        },
        series: [
          {
            name: '情感得分',
            type: 'bar',
            data: simplifiedData,
            itemStyle: {
              color: '#409EFF'
            },
            label: {
              show: true,
              position: 'top',
              formatter: function(params: any) {
                // 保持与Y轴格式一致，显示为整数.00
                return Math.floor(params.value) + '.00';
              }
            },
            barWidth: '50%' // 调整柱子宽度，使图表更美观
          }
        ]
      } as EChartsOption;
    })
    
    // 获取情感倾向分布数据
    const fetchSentimentData = async () => {
      sentimentLoading.value = true
      
      try {
        // 请求情感倾向分布数据
        const response = await axios.get('/data/sentiment-distribution/')
        
        // 这里假设后端返回格式为 [{name: '优', value: 100}, {name: '良', value: 50}, {name: '中', value: 30}]
        sentimentData.value = response.data
        
        sentimentLoading.value = false
      } catch (error) {
        console.error('获取情感倾向分布数据失败:', error)
        ElMessage.error('获取情感倾向分布数据失败')
        
        // 使用模拟数据（仅供开发测试）
        sentimentData.value = [
          { name: '优', value: 65 },
          { name: '良', value: 25 },
          { name: '中', value: 10 }
        ]
        
        sentimentLoading.value = false
      }
    }
    
    // 获取情感得分与景区类型等级关系数据
    const fetchTypeData = async (scenicType: string) => {
      typeLoading.value = true
      
      try {
        // 根据景区类型构建请求参数
        let params: Record<string, string> = { type: scenicType }
        
        // 处理不同类型的查询方式
        // 对于"A级景区"(原"景区")和"水利风景区"，我们使用特殊处理
        if (scenicType === 'A级景区') {
          // A级景区查询使用"景区"类型，级别将是5A、4A等
          params = { type: '景区' }
        } else if (scenicType === '水利风景区') {
          // 水利风景区查询"是"
          params = { type: '水利风景区', level: '是' }
        } else {
          // 其他类型使用组合查询
          params = { type: scenicType }
        }
        
        // 请求情感得分与景区类型等级关系数据
        const response = await axios.get('/data/sentiment-type/', { params })
        
        console.log('API响应数据:', response.data)
        console.log('API响应数据类型:', typeof response.data)
        console.log('是否为数组:', Array.isArray(response.data))
        
        if (Array.isArray(response.data) && response.data.length > 0) {
          console.log('第一项数据类型:', typeof response.data[0])
          console.log('第一项情感得分类型:', typeof response.data[0].avg_sentiment_score)
          console.log('第一项情感得分值:', response.data[0].avg_sentiment_score)
        }
        
        // 这里假设后端返回格式为 [{level: '国家级', avg_sentiment_score: 254.38, avg_sentiment_magnitude: 0.18, count: 42}, ...]
        typeData.value = response.data
        
        typeLoading.value = false
      } catch (error) {
        console.error('获取情感得分与景区类型等级关系数据失败:', error)
        ElMessage.error('获取情感得分与景区类型等级关系数据失败')
        
        // 使用模拟数据（仅供开发测试）
        if (scenicType === '森林公园') {
          typeData.value = [
            { level: '国家级', avg_sentiment_score: 254.38, avg_sentiment_magnitude: 0.18, count: 42 },
            { level: '省级', avg_sentiment_score: 178.95, avg_sentiment_magnitude: 0.15, count: 36 },
            { level: '市级', avg_sentiment_score: 125.64, avg_sentiment_magnitude: 0.12, count: 28 }
          ]
        } else if (scenicType === '景区') {
          typeData.value = [
            { level: '5A景区', avg_sentiment_score: 290.52, avg_sentiment_magnitude: 0.22, count: 25 },
            { level: '4A景区', avg_sentiment_score: 240.18, avg_sentiment_magnitude: 0.19, count: 68 },
            { level: '3A景区', avg_sentiment_score: 185.73, avg_sentiment_magnitude: 0.15, count: 97 },
            { level: '2A景区', avg_sentiment_score: 150.34, avg_sentiment_magnitude: 0.12, count: 45 },
            { level: '省级景区', avg_sentiment_score: 130.87, avg_sentiment_magnitude: 0.10, count: 32 }
          ]
        } else {
          // 默认模拟数据
          typeData.value = [
            { level: '国家级', avg_sentiment_score: 230.45, avg_sentiment_magnitude: 0.20, count: 38 },
            { level: '省级', avg_sentiment_score: 180.12, avg_sentiment_magnitude: 0.16, count: 42 }
          ]
        }
        
        typeLoading.value = false
      }
    }
    
    // 处理景区类型变更
    const handleTypeChange = () => {
      fetchTypeData(selectedType.value)
    }
    
    // 在组件挂载后，初始化获取数据
    onMounted(() => {
      fetchSentimentData()
      // 初始化时如果选择的是"景区"，需要修改为"A级景区"
      if (selectedType.value === '景区') {
        selectedType.value = 'A级景区'
      }
      fetchTypeData(selectedType.value)
      
      // 添加延迟检查，确保图表渲染
      setTimeout(() => {
        console.log('图表渲染检查 - 当前气泡图配置:', sentimentBubbleOptions.value);
      }, 2000);
    })
    
    return {
      sentimentData,
      typeData,
      selectedType,
      scenicTypes,
      sentimentPieOptions,
      sentimentBubbleOptions,
      sentimentLoading,
      typeLoading,
      handleTypeChange
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

.analysis-summary {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
}

.analysis-summary h4 {
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

.data-table-backup {
  margin-top: 20px;
  border: 1px solid #ebeef5;
  padding: 15px;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.data-table-backup h4 {
  margin-top: 0;
  margin-bottom: 15px;
  text-align: center;
}
</style>
