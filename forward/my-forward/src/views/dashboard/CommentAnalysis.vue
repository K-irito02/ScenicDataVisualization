<template>
  <div class="comment-analysis-container">
    <el-row :gutter="30">
      <!-- 左侧列 - 图表区域 -->
      <el-col :span="12">
        <!-- 条形图在上面 -->
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
              height="490px"
              style="width: 100%;"
              v-loading="typeLoading"
            />
          </div>
        </card-container>
        
        <!-- 饼图在下面 -->
        <card-container title="景区情感倾向分布" class="mt-20 bottom-card">
          <div class="chart-wrapper">
            <base-chart 
              :options="sentimentPieOptions" 
              height="490px"
              v-loading="sentimentLoading"
            />
          </div>
        </card-container>
      </el-col>
      
      <!-- 右侧列 - 分析区域 -->
      <el-col :span="12">
        <!-- 合并后的分析卡片 -->
        <card-container title="景区情感数据综合分析">
          <!-- 第一部分：景区类型情感数据表 -->
          <div v-if="typeData.length > 0" class="data-table-backup">
            <h4>景区类型情感数据表</h4>
            <el-table 
              :data="typeData.filter(item => item.level !== 'xxx' && item.level !== 'null' && item.level !== null)" 
              stripe 
              style="width: 100%"
              size="small"
              border
              :header-cell-style="{background:'#f5f7fa',color:'#606266'}"
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
          
          <div class="analysis-summary">
            <h4>景区类型情感分析</h4>
            <ul>
              <li>表中的情感得分和情感强度是该类型等级景区相关数据之和除以该类型等级景区数量得到的<strong>（即平均值）</strong></li>
              <li>随着景区等级的提高，情感得分总体呈上升趋势</li>
              <li>高等级景区通常能引起更强烈的情感反应</li>
              <li>同类型不同等级景区间的情感得分差异反映了等级评定的合理性</li>
              <li>情感强度高的景区往往具有更鲜明的特色或更好的服务</li>
            </ul>
          </div>
          
          <!-- 中间部分：情感分析计算方法 -->
          <div class="calculation-method">
            <h4>情感分析计算方法</h4>
            <div class="calculation-item">
              <div class="calculation-title">情感得分</div>
              <div class="calculation-desc">
                情感得分<strong>（考虑情感词正负）</strong>通过遍历评论中的每个词语，如果该词在情感词典中存在，则获取其情感值。计算过程中同时考虑了程度词（如"非常"、"很"等）的增强作用，以及否定词（如"不"、"没有"等）对情感极性的反转作用。最终将所有词语的情感值累加，得到总的情感得分。
              </div>
            </div>
            
            <div class="calculation-item">
              <div class="calculation-title">情感强度</div>
              <div class="calculation-desc">
                情感强度<strong>（不考虑情感词正负）</strong>反映情感表达的强弱程度。计算时，系统累加每个<strong>情感词得分的绝对值</strong>，然后除以分词后的总词数，得到平均情感强度。无论是积极情感还是消极情感，强度越高表示情感表达越强烈。
              </div>
            </div>
            
            <div class="calculation-item">
              <div class="calculation-title">情感倾向</div>
              <div class="calculation-desc">
                情感倾向将评价分为"优"、"中"、"良"三类，基于平均情感得分确定：<br>
                平均情感得分 = 情感得分 / 分词数<br>
                平均情感得分 > 0.09，判定为"优"<br>
                平均情感得分 < 0.03，判定为"良"<br>
                介于两者之间，判定为"中"
              </div>
            </div>
          </div>
          
          <!-- 第三部分：情感倾向分析 -->
          <div class="analysis-summary mt-20">
            <h4>情感倾向分析</h4>
            <ul>
              <li>情感倾向为"优"的景区占比最大，表明大部分景区评价良好</li>
              <li>不同情感倾向的分布反映游客对景区的整体满意度</li>
              <li>情感倾向为"良"的景区，说明改进空间较大</li>
              <li>情感倾向为"中"的景区，可进行针对性改进</li>
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
          radius: ['20%', '70%'],
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
    
    // 情感得分与景区类型等级条形图配置
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
        const response = await axios.get('/api/data/sentiment-distribution/')
        
        // 这里假设后端返回格式为 [{name: '优', value: 100}, {name: '良', value: 50}, {name: '中', value: 30}]
        sentimentData.value = response.data
        
        sentimentLoading.value = false
      } catch (error) {
        console.error('获取情感倾向分布数据失败:', error)
        ElMessage.error('获取情感倾向分布数据失败')
        
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
        const response = await axios.get('/api/data/sentiment-type/', { params })
        
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
        console.log('图表渲染检查 - 当前条形图配置:', sentimentBubbleOptions.value);
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
  margin-bottom: 0%;
}

.analysis-summary {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 4px;
  margin-top: 20px;
  border: 1px solid #e4e7ed;
}

.analysis-summary h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  position: relative;
  padding-left: 10px;
  font-size: 16px;
}

.analysis-summary h4:before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 14px;
  background-color: #67c23a;
  border-radius: 2px;
}

.analysis-summary ul {
  padding-left: 20px;
  margin: 0;
}

.analysis-summary li {
  margin-bottom: 8px;
  line-height: 1.6;
  color: #606266;
}

.data-table-backup {
  margin-top: 20px;
  margin-bottom: 0;
  border: 1px solid #e4e7ed;
  padding: 20px;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.data-table-backup h4 {
  margin-top: 0;
  margin-bottom: 15px;
  text-align: center;
  position: relative;
  color: #303133;
}

.mt-20 {
  margin-top: 20px;
}

.mt-10 {
  margin-top: 10px;
}

.title-with-select {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

/* 确保底部两张卡片高度一致 */
.el-row {
  display: flex;
  align-items: flex-start;
}

.el-col {
  display: flex;
  flex-direction: column;
}

.el-col .card-container {
  margin-bottom: 20px;
  height: 100%;
}

/* 确保左右两列的卡片从相同位置开始 */
.el-row {
  display: flex;
  align-items: flex-start;
}

/* 使左侧布局为纵向布局，以便饼图能对齐到底部 */
.el-col:first-child {
  display: flex;
  flex-direction: column;
}

/* 调整饼图卡片，使其占用剩余空间 */
.bottom-card {
  margin-top: 20px !important;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

/* 确保右侧卡片高度占满 */
.el-col:last-child .card-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.analysis-summary:last-child h4:before {
  background-color: #e6a23c;
}

.calculation-method {
  margin-top: 25px;
  margin-bottom: 25px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #f5f7fa;
}

.calculation-method h4 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  color: #303133;
  position: relative;
  padding-left: 10px;
}

.calculation-method h4:before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 14px;
  background-color: #409EFF;
  border-radius: 2px;
}

.calculation-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #e4e7ed;
}

.calculation-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.calculation-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #409EFF;
}

.calculation-desc {
  margin-left: 0;
  line-height: 1.6;
  color: #606266;
  text-align: justify;
}
</style>
