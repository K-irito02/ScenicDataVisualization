<template>
  <div class="transportation-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <card-container title="交通方式分布">
          <template #actions>
            <el-select v-model="selectedRegion" placeholder="选择地区" size="small" @change="handleRegionChange">
              <el-option label="全国" value="all" />
              <el-option v-for="region in regions" :key="region" :label="region" :value="region" />
            </el-select>
          </template>
          
          <div class="chart-wrapper">
            <base-chart 
              :options="sankeyOptions" 
              height="500px"
            />
          </div>
          
          <div class="analysis-summary">
            <h4>交通分析结论</h4>
            <ul>
              <li>全国范围内，自驾是前往景区的主要交通方式，占比约45%</li>
              <li>高铁网络覆盖的东部地区，高铁出行比例明显高于西部地区</li>
              <li>北京、上海、广州等一线城市的地铁直达景区比例较高</li>
              <li>西部偏远景区主要依靠自驾和旅游大巴前往</li>
              <li>沿海城市景区水路交通占比高于内陆景区</li>
            </ul>
          </div>
        </card-container>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :span="24">
        <card-container title="景区可达性评分">
          <template #actions>
            <el-radio-group v-model="transportType" size="small" @change="handleTransportTypeChange">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="car">自驾</el-radio-button>
              <el-radio-button label="train">高铁/火车</el-radio-button>
              <el-radio-button label="bus">公交/大巴</el-radio-button>
              <el-radio-button label="subway">地铁</el-radio-button>
            </el-radio-group>
          </template>
          
          <div class="chart-wrapper">
            <base-chart 
              :options="mapOptions" 
              height="450px"
            />
          </div>
          
          <div class="facility-summary">
            <h4>交通设施分布</h4>
            <el-row :gutter="20">
              <el-col :xs="12" :sm="6" v-for="item in facilityStats" :key="item.type">
                <div class="facility-card">
                  <div class="facility-icon">
                    <el-icon><component :is="item.icon"></component></el-icon>
                  </div>
                  <div class="facility-info">
                    <div class="facility-name">{{ item.name }}</div>
                    <div class="facility-count">{{ item.count }}</div>
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
import { 
  Location, 
  Van, 
  TrendCharts, 
  OfficeBuilding, 
  Clock 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

export default defineComponent({
  name: 'Transportation',
  components: {
    CardContainer,
    BaseChart,
    Location,
    Van,
    TrendCharts,
    OfficeBuilding,
    Clock
  },
  setup() {
    const scenicStore = useScenicStore()
    const selectedRegion = ref('all')
    const transportType = ref('all')
    const regions = ref(['华北', '华东', '华南', '西南', '西北', '东北', '华中'])
    
    // 模拟桑基图数据
    const sankeyData = ref({
      nodes: [
        { name: '北京' },
        { name: '上海' },
        { name: '广州' },
        { name: '成都' },
        { name: '西安' },
        { name: '武汉' },
        { name: '哈尔滨' },
        { name: '自驾' },
        { name: '高铁' },
        { name: '地铁' },
        { name: '公交/大巴' },
        { name: '旅游专线' },
        { name: '水路' },
        { name: '飞机' }
      ],
      links: [
        { source: '北京', target: '自驾', value: 3000 },
        { source: '北京', target: '高铁', value: 2500 },
        { source: '北京', target: '地铁', value: 3500 },
        { source: '北京', target: '公交/大巴', value: 1500 },
        { source: '北京', target: '旅游专线', value: 800 },
        { source: '上海', target: '自驾', value: 2800 },
        { source: '上海', target: '高铁', value: 3000 },
        { source: '上海', target: '地铁', value: 4000 },
        { source: '上海', target: '公交/大巴', value: 1200 },
        { source: '上海', target: '水路', value: 1000 },
        { source: '广州', target: '自驾', value: 2600 },
        { source: '广州', target: '高铁', value: 2200 },
        { source: '广州', target: '地铁', value: 2800 },
        { source: '广州', target: '公交/大巴', value: 1100 },
        { source: '广州', target: '水路', value: 800 },
        { source: '成都', target: '自驾', value: 3200 },
        { source: '成都', target: '高铁', value: 1800 },
        { source: '成都', target: '公交/大巴', value: 1600 },
        { source: '成都', target: '旅游专线', value: 1200 },
        { source: '成都', target: '飞机', value: 1000 },
        { source: '西安', target: '自驾', value: 2400 },
        { source: '西安', target: '高铁', value: 2000 },
        { source: '西安', target: '公交/大巴', value: 1400 },
        { source: '西安', target: '旅游专线', value: 1000 },
        { source: '武汉', target: '自驾', value: 2200 },
        { source: '武汉', target: '高铁', value: 2500 },
        { source: '武汉', target: '公交/大巴', value: 1300 },
        { source: '武汉', target: '水路', value: 1200 },
        { source: '哈尔滨', target: '自驾', value: 1800 },
        { source: '哈尔滨', target: '高铁', value: 1600 },
        { source: '哈尔滨', target: '公交/大巴', value: 1100 },
        { source: '哈尔滨', target: '飞机', value: 900 }
      ]
    })
    
    // 模拟交通设施统计
    const facilityStats = ref([
      { type: 'station', name: '火车站/高铁站', count: 264, icon: 'TrendCharts' },
      { type: 'bus_stop', name: '公交站/大巴站', count: 1852, icon: 'Van' },
      { type: 'subway', name: '地铁站', count: 138, icon: 'OfficeBuilding' },
      { type: 'airport', name: '机场', count: 47, icon: 'Location' }
    ])
    
    // 根据地区筛选桑基图数据
    const filterSankeyData = () => {
      if (selectedRegion.value === 'all') {
        return sankeyData.value
      }
      
      // 这里应该根据选中的地区过滤数据
      // 简化起见，这里只是模拟不同地区有不同数据
      const regionNodesMap: Record<string, string[]> = {
        '华北': ['北京', '自驾', '高铁', '地铁', '公交/大巴', '旅游专线'],
        '华东': ['上海', '自驾', '高铁', '地铁', '公交/大巴', '水路'],
        '华南': ['广州', '自驾', '高铁', '地铁', '公交/大巴', '水路'],
        '西南': ['成都', '自驾', '高铁', '公交/大巴', '旅游专线', '飞机'],
        '西北': ['西安', '自驾', '高铁', '公交/大巴', '旅游专线'],
        '华中': ['武汉', '自驾', '高铁', '公交/大巴', '水路'],
        '东北': ['哈尔滨', '自驾', '高铁', '公交/大巴', '飞机']
      }
      
      const targetNodes = regionNodesMap[selectedRegion.value] || []
      
      return {
        nodes: sankeyData.value.nodes.filter(node => targetNodes.includes(node.name)),
        links: sankeyData.value.links.filter(link => 
          targetNodes.includes(link.source as string) && 
          targetNodes.includes(link.target as string)
        )
      }
    }
    
    // 桑基图配置
    const sankeyOptions = computed<EChartsOption>(() => {
      const filteredData = filterSankeyData()
      
      return {
        title: {
          text: `${selectedRegion.value === 'all' ? '全国' : selectedRegion.value}景区交通方式分布`,
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          triggerOn: 'mousemove'
        },
        series: [
          {
            type: 'sankey',
            data: filteredData.nodes,
            links: filteredData.links,
            emphasis: {
              focus: 'adjacency'
            },
            levels: [
              {
                depth: 0,
                itemStyle: {
                  color: '#fbb4ae'
                },
                lineStyle: {
                  color: 'source',
                  opacity: 0.6
                }
              },
              {
                depth: 1,
                itemStyle: {
                  color: '#b3cde3'
                },
                lineStyle: {
                  color: 'target',
                  opacity: 0.6
                }
              }
            ],
            lineStyle: {
              curveness: 0.5
            }
          }
        ]
      }
    })
    
    // 获取中国地图数据
    const getMapOption = () => ({
      title: {
        text: '景区可达性评分分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item' as const,
        formatter: '{b}<br/>可达性评分: {c}'
      },
      visualMap: {
        min: 0,
        max: 100,
        text: ['高', '低'],
        realtime: false,
        calculable: true,
        inRange: {
          color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
        }
      },
      series: [
        {
          name: '可达性评分',
          type: 'map',
          map: 'china',
          emphasis: {
            label: {
              show: true
            }
          },
          data: generateProvinceScores()
        }
      ]
    }) as EChartsOption
    
    // 生成省份得分数据
    const generateProvinceScores = () => {
      const provinces = [
        '北京', '天津', '河北', '山西', '内蒙古', 
        '辽宁', '吉林', '黑龙江', '上海', '江苏',
        '浙江', '安徽', '福建', '江西', '山东',
        '河南', '湖北', '湖南', '广东', '广西',
        '海南', '重庆', '四川', '贵州', '云南',
        '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆'
      ]
      
      // 根据交通类型调整得分
      let scoreAdjustment = 0
      if (transportType.value === 'car') {
        scoreAdjustment = 10
      } else if (transportType.value === 'train') {
        scoreAdjustment = -5
      } else if (transportType.value === 'subway') {
        scoreAdjustment = -15
      } else if (transportType.value === 'bus') {
        scoreAdjustment = 5
      }
      
      return provinces.map(province => {
        // 简单模拟不同省份的基础得分
        let baseScore
        if (['北京', '上海', '江苏', '浙江', '广东'].includes(province)) {
          baseScore = 85 // 东部发达省份
        } else if (['西藏', '青海', '新疆', '甘肃', '内蒙古'].includes(province)) {
          baseScore = 50 // 西部偏远省份
        } else {
          baseScore = 70 // 其他省份
        }
        
        // 添加随机性和交通类型调整
        const finalScore = Math.min(100, Math.max(0, baseScore + scoreAdjustment + Math.floor(Math.random() * 10 - 5)))
        
        return {
          name: province,
          value: finalScore
        }
      })
    }
    
    // 地图配置
    const mapOptions = computed<EChartsOption>(() => getMapOption())
    
    // 处理地区变更
    const handleRegionChange = () => {
      // 这里如果需要从API获取数据，可以添加相应逻辑
    }
    
    // 处理交通类型变更
    const handleTransportTypeChange = () => {
      // 更新地图数据
    }
    
    // 获取交通数据
    const fetchTransportationData = async () => {
      try {
        // 实际项目中应该从API获取数据
        // 这里使用的是预设的模拟数据
      } catch (error) {
        console.error('获取交通数据失败:', error)
        ElMessage.error('获取交通数据失败')
      }
    }
    
    onMounted(async () => {
      try {
        // 注册中国地图
        await echarts.registerMap('china', await fetch('/china.json').then(response => response.json()))
        
        fetchTransportationData()
      } catch (error) {
        console.error('地图数据加载失败:', error)
        ElMessage.error('地图数据加载失败')
      }
    })
    
    return {
      selectedRegion,
      transportType,
      regions,
      facilityStats,
      sankeyOptions,
      mapOptions,
      handleRegionChange,
      handleTransportTypeChange
    }
  }
})
</script>

<style scoped>
.transportation-container {
  padding: 20px;
}

.chart-wrapper {
  width: 100%;
  margin-bottom: 20px;
}

.analysis-summary, .facility-summary {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
}

.analysis-summary h4, .facility-summary h4 {
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

.facility-card {
  display: flex;
  align-items: center;
  background-color: white;
  border-radius: 4px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 15px;
}

.facility-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #ecf5ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.facility-icon .el-icon {
  font-size: 20px;
  color: #409eff;
}

.facility-info {
  flex: 1;
}

.facility-name {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.facility-count {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
</style> 