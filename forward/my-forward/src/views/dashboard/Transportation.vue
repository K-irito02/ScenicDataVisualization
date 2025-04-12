<template>
  <div class="transportation-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <card-container title="交通方式分布">
          <template #actions>
            <el-select v-model="selectedProvince" placeholder="选择省份/地区" size="small" @change="handleProvinceChange" filterable>
              <el-option label="全国" value="all" />
              <el-option v-for="province in provinceList" :key="province" :label="province" :value="province" />
            </el-select>
          </template>
          
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="8" animated />
          </div>
          
          <div v-else class="chart-wrapper">
            <base-chart 
              :options="sankeyOptions" 
              height="900px"
            />
          </div>
          
          <div class="analysis-summary">
            <h4>交通分析结论</h4>
            <ul>
              <li>全国范围内，公交和地铁是前往城市景区的主要交通方式</li>
              <li>步行在近郊景点也占有相当大的比例，表明很多景区都有便捷的步行路线</li>
              <li>北京、上海、广州等一线城市的公共交通系统较为完善</li>
              <li>西部偏远景区主要依靠自驾和旅游大巴前往</li>
              <li>沿海城市景区有更多样化的交通选择</li>
            </ul>
          </div>
        </card-container>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import type { Ref } from 'vue'
import CardContainer from '@/components/common/CardContainer.vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import * as echarts from 'echarts'
import type { 
  EChartsOption, 
  SankeySeriesOption
} from 'echarts'
import { ElMessage } from 'element-plus'
import { Location, Van, TrendCharts } from '@element-plus/icons-vue'
import { getTransportation } from '@/api/scenic'
import { useScenicStore } from '@/stores/scenic'

export default defineComponent({
  name: 'Transportation',
  components: {
    CardContainer,
    BaseChart,
    Location,
    Van,
    TrendCharts
  },
  setup() {
    const scenicStore = useScenicStore()
    const selectedProvince = ref('all')
    const provinceList = ref<string[]>([])
    const loading = ref(false) 
    const apiData = ref<any[]>([]) 
    const transportTypes = ref<string[]>([])
    
    // 使用空初始值，将从API获取真实数据
    const sankeyData = ref<{
      nodes: Array<{ name: string, [key: string]: any }>,
      links: Array<{ source: string, target: string, value: number, [key: string]: any }>
    }>({
      nodes: [],
      links: []
    })
    
    // 根据省份筛选桑基图数据
    const filterSankeyData = () => {
      if (selectedProvince.value === 'all') {
        return sankeyData.value
      }
      
      // 根据选中的省份过滤数据
      const targetProvince = selectedProvince.value
      
      // 获取交通方式节点列表
      const transportNodes = sankeyData.value.nodes.filter(node => {
        // 判断是否为交通方式节点（排除省份节点）
        return !provinceList.value.includes(node.name);
      });
      
      // 获取选中的省份节点
      const provinceNode = sankeyData.value.nodes.find(node => node.name === targetProvince);
      
      // 如果找不到省份节点，返回空数据
      if (!provinceNode) {
        return { nodes: [], links: [] };
      }
      
      // 过滤链接，只保留与选中省份相关的链接
      const filteredLinks = sankeyData.value.links.filter(link => 
        link.source === targetProvince || link.target === targetProvince
      );
      
      // 获取相关节点的名称列表
      const relatedNodeNames = new Set<string>();
      relatedNodeNames.add(targetProvince);
      
      filteredLinks.forEach(link => {
        relatedNodeNames.add(link.source as string);
        relatedNodeNames.add(link.target as string);
      });
      
      // 过滤节点，只保留相关节点
      const filteredNodes = sankeyData.value.nodes.filter(node => 
        relatedNodeNames.has(node.name)
      );
      
      return {
        nodes: filteredNodes,
        links: filteredLinks
      };
    }
    
    // 根据交通工具种类生成丰富的颜色系列
    const generateTransportColors = (transportTypes: string[]) => {
      // 预定义的鲜明颜色系列，确保每种交通工具有独特颜色
      const colorPalette = [
        '#FF3D00', '#D50000', '#C51162', '#AA00FF', '#6200EA',  
        '#304FFE', '#2962FF', '#0091EA', '#00B8D4', '#00BFA5',
        '#00C853', '#64DD17', '#AEEA00', '#FFD600', '#FFAB00',
        '#FF6D00', '#8D6E63', '#546E7A', '#78909C', '#26A69A',
        '#7CB342', '#FB8C00', '#F4511E', '#6D4C41', '#5D4037'
      ];
      
      const transportColorMap: Record<string, string> = {};
      
      transportTypes.forEach((type, index) => {
        transportColorMap[type] = colorPalette[index % colorPalette.length];
      });
      
      return transportColorMap;
    };
    
    // 为节点分配颜色
    const getNodeColor = (name: string) => {
      // 生成交通工具颜色映射
      const transportColors = generateTransportColors(transportTypes.value);
      
      // 检查是否为交通方式
      if (transportColors[name]) {
        return transportColors[name];
      }
      
      // 省份节点使用蓝色色系渐变
      const provinceIndex = provinceList.value.indexOf(name);
      if (provinceIndex >= 0) {
        // 使用更丰富的颜色渐变
        const colors = [
          '#E3F2FD', '#BBDEFB', '#90CAF9', '#64B5F6', '#42A5F5', '#2196F3', 
          '#1E88E5', '#1976D2', '#1565C0', '#0D47A1', '#82B1FF', '#448AFF'
        ];
        return colors[provinceIndex % colors.length];
      }
      
      // 默认颜色
      return '#CFD8DC';
    };
    
    // 桑基图配置
    const sankeyOptions = computed(() => {
      const filteredData = filterSankeyData()
      
      // 为节点添加颜色
      const nodesWithColor = filteredData.nodes.map(node => ({
        ...node,
        itemStyle: {
          color: getNodeColor(node.name)
        }
      }));
      
      // 链接的颜色基于源节点
      const linksWithColor = filteredData.links.map(link => {
        const sourceNode = nodesWithColor.find(node => node.name === link.source);
        return {
          ...link,
          lineStyle: {
            color: sourceNode?.itemStyle?.color || '#CFD8DC',
            opacity: 0.7 // 增加不透明度使颜色更鲜明
          }
        };
      });
      
      // 计算数据总量用于设置节点宽度 - 增加宽度
      const totalValue = linksWithColor.reduce((sum, link) => sum + (link.value || 0), 0);
      // 为圆形布局调整节点宽度
      const nodeWidth = Math.max(15, Math.min(30, totalValue / 8000));
      
      // 创建图例数据，包含所有交通方式类型
      const legendData = [...transportTypes.value, '省份/地区'];
      
      return {
        backgroundColor: '#FFFFFF', // 添加白色背景
        title: {
          text: `${selectedProvince.value === 'all' ? '全国' : selectedProvince.value}景区交通方式分布`,
          left: 'center',
          top: 20,
          textStyle: {
            fontSize: 20,
            fontWeight: 'bold',
            color: '#333333'
          }
        },
        tooltip: {
          trigger: 'item',
          triggerOn: 'mousemove',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderColor: '#ccc',
          borderWidth: 1,
          textStyle: {
            color: '#333',
            fontSize: 14
          },
          formatter: function(params: any) {
            if (params.dataType === 'node') {
              return `<div style="font-weight:bold;">${params.name}</div>总连接量: ${params.value || 0}`;
            } else if (params.data) {
              const data = params.data as {
                source: string;
                target: string;
                value: number;
              };
              return `<div style="font-weight:bold;">${data.source} → ${data.target}</div>数量: ${data.value}`;
            }
            return '';
          }
        },
        legend: {
          show: true,
          type: 'scroll',
          orient: 'horizontal',
          bottom: 10,
          padding: [15, 5, 5, 5],
          itemGap: 15,
          textStyle: {
            fontSize: 14
          },
          data: legendData,
          formatter: function(name: string) {
            // 截断过长的名称
            if (name.length > 15) {
              return name.substr(0, 12) + '...';
            }
            return name;
          }
        },
        series: [
          {
            type: 'sankey',
            layout: 'circular', // 使用圆形布局
            emphasis: {
              focus: 'adjacency'
            },
            data: nodesWithColor,
            links: linksWithColor,
            nodeWidth: nodeWidth,
            nodeGap: 8, // 为圆形布局调整节点间距
            radius: ['20%', '70%'], // 设置圆形布局的内外半径
            layoutIterations: 64, // 圆形布局迭代次数
            draggable: false, // 禁止拖拽节点，避免布局混乱
            label: {
              formatter: '{b}', // 只显示节点名称
              position: 'right',
              fontSize: 12,
              fontWeight: 'bold',
              color: '#000',
              distance: 5, // 标签与节点的距离
              show: true
            },
            lineStyle: {
              color: 'source',
              opacity: 0.6,
              curveness: 0.5
            },
            itemStyle: {
              borderWidth: 1,
              borderColor: 'rgba(255, 255, 255, 0.5)'
            },
            animation: true,
            animationDuration: 1500, // 增加动画时间
            animationEasing: 'cubicOut'
          }
        ]
      } as EChartsOption
    })
    
    // 处理省份变更
    const handleProvinceChange = () => {
      console.log('省份变更为:', selectedProvince.value);
    }
    
    // 获取交通数据
    const fetchTransportationData = async () => {
      loading.value = true
      try {
        // 调用API获取交通方式数据
        const response = await getTransportation()
        console.log('交通数据API响应:', response)
        
        // 处理API响应，判断是否有data属性或者本身是数组
        const responseData = response?.data || response
        
        if (responseData && Array.isArray(responseData)) {
          apiData.value = responseData
          
          // 处理API返回的数据更新桑基图
          if (responseData.length > 0) {
            // 从API数据提取唯一的交通方式和目标省份
            const transportSet = new Set<string>()
            const provinceSet = new Set<string>()
            
            responseData.forEach((item: any) => {
              if (item.source) transportSet.add(item.source)
              if (item.target) provinceSet.add(item.target)
            })
            
            // 从各种交通工具中提取交通工具类型
            // 判断哪些是交通方式，哪些是省份
            const transportList = Array.from(transportSet);
            const provinceList = Array.from(provinceSet);
            
            // 我们假设交通方式的名称不会出现在省份列表中
            const realTransportTypes = transportList.filter(t => !provinceList.includes(t));
            transportTypes.value = realTransportTypes.sort();
            
            // 更新省份列表供筛选使用
            provinceList.value = Array.from(provinceSet).sort()
            
            // 创建新的节点数组
            const nodes = [
              ...Array.from(transportSet).map(name => ({ name })),
              ...Array.from(provinceSet).map(name => ({ name }))
            ]
            
            // 创建新的链接数组
            const links = responseData.map((item: any) => ({
              source: item.source,
              target: item.target,
              value: item.value || 1
            }))
            
            // 更新桑基图数据
            sankeyData.value = {
              nodes,
              links
            }
            
            console.log('已更新桑基图数据:', sankeyData.value)
            console.log('交通工具类型:', transportTypes.value)
          }
        } else {
          console.warn('API返回的交通数据格式不正确')
          ElMessage.warning('无法获取交通数据，请稍后再试')
        }
      } catch (error) {
        console.error('获取交通数据失败:', error)
        ElMessage.error('获取交通数据失败，请检查网络连接')
      } finally {
        loading.value = false
      }
    }
    
    onMounted(async () => {
      loading.value = true
      try {
        // 获取交通数据
        await fetchTransportationData()
      } catch (error) {
        console.error('初始化失败:', error)
        ElMessage.error('页面初始化失败')
      } finally {
        loading.value = false
      }
    })
    
    return {
      selectedProvince,
      provinceList,
      sankeyOptions,
      handleProvinceChange,
      loading
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
  height: 100%;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  border-radius: 4px;
  padding: 10px;
}

.analysis-summary {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.05);
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

.loading-container {
  min-height: 900px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
}
</style> 