<template>
  <div class="transportation-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <card-container title="交通方式分布">
          <template #actions>
            <el-select v-model="selectedProvince" placeholder="选择省份/地区" size="small" @change="handleProvinceChange" filterable>
              <el-option label="全国" value="全国" />
              <el-option v-for="province in availableProvinces.filter(p => p !== '全国')" :key="province" :label="province" :value="province" />
            </el-select>
          </template>
          
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="8" animated />
          </div>
          
          <div v-else-if="noDataError" class="no-data-container">
            <el-empty description="暂无该省份的交通数据" :image-size="200">
              <template #description>
                <p>{{ noDataError }}</p>
              </template>
              <el-button type="primary" @click="selectedProvince = '全国'">返回全国视图</el-button>
            </el-empty>
          </div>
          
          <div v-else>
            <!-- 对全国视图使用Highcharts依赖轮图 -->
            <div v-if="selectedProvince === '全国'" class="chart-wrapper">
              <div id="highcharts-container" style="width:100%; height:900px;"></div>
            </div>
            <!-- 对省级视图使用ECharts图表 -->
            <div v-else class="chart-wrapper">
              <base-chart 
                :options="circularChartOptions" 
                height="700px"
              />
            </div>
          </div>
        </card-container>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed, watch } from 'vue'
import CardContainer from '@/components/common/CardContainer.vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import type { 
  EChartsOption, 
} from 'echarts'
// 引入Highcharts及其依赖轮模块
import Highcharts from 'highcharts'
import 'highcharts/modules/sankey'
import 'highcharts/modules/dependency-wheel'
// 添加Highcharts导出模块
import 'highcharts/modules/exporting'
// 添加离线导出模块
import 'highcharts/modules/offline-exporting'
// 添加导出数据模块
import 'highcharts/modules/export-data'
// 删除不存在的库导入
import { ElMessage } from 'element-plus'
import { Location, Van, TrendCharts } from '@element-plus/icons-vue'
import { getTransportation } from '@/api/scenic'

// 链接和节点的接口定义
interface SankeyNode {
  name: string;
  itemStyle?: { color?: string };
  value?: number;
}

interface SankeyLink {
  source: string | SankeyNode | number;
  target: string | SankeyNode | number;
  value: number;
  lineStyle?: any;
}

interface SankeyData {
  nodes: SankeyNode[];
  links: SankeyLink[];
}

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
    const selectedProvince = ref('全国')
    const provinceList = ref<string[]>([])
    const loading = ref(false) 
    const apiData = ref<any[]>([]) 
    const transportTypes = ref<string[]>([])
    const noDataError = ref('')
    const provincesWithData = ref<Set<string>>(new Set())
    
    // 定义所有省级行政区
    const allProvinces = [
      '北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
      '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北',
      '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州', '云南', '西藏',
      '陕西', '甘肃', '青海', '宁夏', '新疆', '香港', '澳门', '台湾',
      '东北', '西北' // 添加东北和西北作为省级行政区
    ]
    
    // 计算属性：只返回有数据的省份
    const availableProvinces = computed(() => {
      return Array.from(provincesWithData.value).sort();
    });
    
    // 使用空初始值，将从API获取真实数据
    const sankeyData = ref<SankeyData>({ nodes: [], links: [] });
    
    // 监听省份变化，检查是否有数据
    watch(selectedProvince, (newValue) => {
      if (newValue !== '全国') {
        checkProvinceData(newValue);
      } else {
        noDataError.value = '';
      }
    });
    
    // 检查省份是否有数据
    const checkProvinceData = (province: string) => {
      // 重置错误信息
      noDataError.value = '';
      
      // 检查省份节点是否存在
      const provinceNode = sankeyData.value.nodes.find(node => node.name === province);
      if (!provinceNode) {
        noDataError.value = `未找到${province}省份节点数据`;
        return false;
      }
      
      // 检查是否存在与该省份相关的链接
      const relatedLinks = sankeyData.value.links.filter(link => {
        const source = typeof link.source === 'string' 
          ? link.source 
          : typeof link.source === 'object' && link.source !== null 
            ? (link.source as SankeyNode).name 
            : '';
        const target = typeof link.target === 'string' 
          ? link.target 
          : typeof link.target === 'object' && link.target !== null 
            ? (link.target as SankeyNode).name 
            : '';
        return source === province || target === province;
      });
      
      if (relatedLinks.length === 0) {
        noDataError.value = `${province}没有相关的交通数据`;
        return false;
      }
      
      return true;
    };
    
    // 根据省份筛选桑基图数据
    const filterSankeyData = () => {
      console.log(`筛选桑基图数据，选中省份: ${selectedProvince.value}`);
      
      if (selectedProvince.value === '全国') {
        console.log('显示全国数据');
        return sankeyData.value;
      }
      
      // 根据选中的省份过滤数据
      const targetProvince = selectedProvince.value;
      console.log(`目标省份: ${targetProvince}`);
      
      // 如果没有数据，返回空数据结构
      if (noDataError.value) {
        return { nodes: [], links: [] };
      }
      
      // 获取交通方式节点列表
      const transportNodes = sankeyData.value.nodes.filter(node => {
        // 判断是否为交通方式节点（排除省份节点）
        return !allProvinces.includes(node.name);
      });
      console.log(`交通方式节点数量: ${transportNodes.length}`);
      
      // 获取选中的省份节点
      const provinceNode = sankeyData.value.nodes.find(node => node.name === targetProvince);
      
      // 如果找不到省份节点，返回空数据
      if (!provinceNode) {
        console.warn(`未找到省份节点: ${targetProvince}`);
        return { nodes: [], links: [] };
      }
      
      // 过滤链接，只保留与选中省份相关的链接
      const filteredLinks = sankeyData.value.links.filter(link => {
        const source = typeof link.source === 'string' 
          ? link.source 
          : typeof link.source === 'object' && link.source !== null 
            ? (link.source as SankeyNode).name 
            : '';
        const target = typeof link.target === 'string' 
          ? link.target 
          : typeof link.target === 'object' && link.target !== null 
            ? (link.target as SankeyNode).name 
            : '';
        return source === targetProvince || target === targetProvince;
      });
      console.log(`筛选后的链接数量: ${filteredLinks.length}`);
      
      // 链接数量为0，说明没有与该省份相关的数据
      if (filteredLinks.length === 0) {
        console.warn(`${targetProvince}没有相关链接数据`);
        return { nodes: [], links: [] };
      }
      
      // 获取相关节点的名称列表
      const relatedNodeNames = new Set<string>();
      
      // 收集与省份相关的所有交通方式节点
      filteredLinks.forEach(link => {
        const sourceName = typeof link.source === 'string' 
          ? link.source 
          : typeof link.source === 'object' && link.source !== null 
            ? (link.source as SankeyNode).name 
            : '';
        const targetName = typeof link.target === 'string' 
          ? link.target 
          : typeof link.target === 'object' && link.target !== null 
            ? (link.target as SankeyNode).name 
            : '';
        
        if (sourceName !== targetProvince) relatedNodeNames.add(sourceName);
        if (targetName !== targetProvince) relatedNodeNames.add(targetName);
      });
      console.log(`相关节点数量: ${relatedNodeNames.size}`);
      
      // 过滤节点，只保留相关节点和选中的省份节点
      const filteredNodes = [
        ...sankeyData.value.nodes.filter(node => 
          relatedNodeNames.has(node.name)
        ),
        provinceNode // 确保包含省份节点
      ];
      console.log(`筛选后的节点数量: ${filteredNodes.length}`);
      
      // 确保链接中的省份节点始终在左侧（作为source）
      const reorientedLinks = filteredLinks.map(link => {
        const newLink = { ...link };
        const sourceName = typeof newLink.source === 'string' 
          ? newLink.source 
          : typeof newLink.source === 'object' && newLink.source !== null 
            ? (newLink.source as SankeyNode).name 
            : '';
        const targetName = typeof newLink.target === 'string' 
          ? newLink.target 
          : typeof newLink.target === 'object' && newLink.target !== null 
            ? (newLink.target as SankeyNode).name 
            : '';
        
        // 如果省份不是source，就交换source和target
        if (sourceName !== targetProvince && targetName === targetProvince) {
          return {
            ...newLink,
            source: newLink.target,
            target: newLink.source
          };
        }
        
        return newLink;
      });
      
      return {
        nodes: filteredNodes,
        links: reorientedLinks
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
      
      // 省份节点使用梯度蓝色系
      const provinceIndex = allProvinces.indexOf(name);
      if (provinceIndex >= 0) {
        // 使用更丰富的颜色渐变
        const colors = [
          '#1A237E', '#283593', '#303F9F', '#3949AB', '#3F51B5', 
          '#5C6BC0', '#7986CB', '#9FA8DA', '#C5CAE9', '#E8EAF6', 
          '#8C9EFF', '#536DFE', '#3D5AFE', '#304FFE', '#1976D2'
        ];
        return colors[provinceIndex % colors.length];
      }
      
      // 默认颜色
      return '#CFD8DC';
    };
    
    // 环形图配置
    const circularChartOptions = computed(() => {
      const filteredData = filterSankeyData();
      console.log('过滤后的数据:', filteredData);
      
      // 如果没有数据，返回空配置
      if (filteredData.nodes.length === 0 || filteredData.links.length === 0) {
        return {
          title: {
            text: '暂无数据',
            left: 'center',
            top: 'center',
            textStyle: {
              fontSize: 24,
              fontWeight: 'bold',
              color: '#909399'
            }
          }
        } as EChartsOption;
      }
      
      // 只为省份视图提供ECharts配置，全国视图由Highcharts处理
      if (selectedProvince.value === '全国') {
        return {
          title: {
            text: ' ', // 空标题，由Highcharts处理
          }
        } as EChartsOption;
      } else {
        // 单个省份视图使用力导向图形式的桑基图
        // 为节点添加颜色
        const nodesWithColor = filteredData.nodes.map(node => ({
          name: node.name,
          itemStyle: {
            color: getNodeColor(node.name)
          },
          value: node.value,
          // 控制节点固定位置
          fixed: node.name === selectedProvince.value ? true : false,
          x: node.name === selectedProvince.value ? 300 : undefined,
          y: node.name === selectedProvince.value ? 300 : undefined
        }));
        
        // 为链接添加样式
        const linksWithColor = filteredData.links.map(link => {
          const source = typeof link.source === 'string' 
            ? link.source 
            : typeof link.source === 'object' && link.source !== null 
              ? (link.source as SankeyNode).name 
              : '';
          
          const target = typeof link.target === 'string' 
            ? link.target 
            : typeof link.target === 'object' && link.target !== null 
              ? (link.target as SankeyNode).name 
              : '';
          
          const sourceColor = getNodeColor(source);
          
          return {
            source: source,
            target: target,
            value: typeof link.value === 'number' ? link.value : 0,
            lineStyle: {
              color: sourceColor,
              opacity: 0.7,
              width: Math.max(1, (typeof link.value === 'number' ? link.value : 0) / 5000)
            }
          };
        });
        
        return {
          backgroundColor: '#FFFFFF',
          title: {
            text: `${selectedProvince.value}交通方式分布图`,
            left: 'center',
            top: 40,  // 标题距离顶部距离
            textStyle: {
              fontSize: 18,
              fontWeight: 'bold'
            },
            subtext: '显示省份相关交通方式',
            subtextStyle: {
              fontSize: 12,
              color: '#666'
            }
          },
          tooltip: {
            trigger: 'item',
            triggerOn: 'mousemove',
            formatter: function(params: any) {
              if (params.dataType === 'edge') {
                return `${params.data.source} → ${params.data.target}: ${params.data.value}`;
              } else {
                return `${params.name}`;
              }
            }
          },
          grid: {
            top: 80, 
            containLabel: true
          },
          legend: {
            show: true,
            type: 'scroll',
            orient: 'vertical',  // 垂直方向排列
            left: '25%',         // 距离左侧25%位置
            top: 'middle',      // 垂直居中
            itemGap: 10,         // 图例项之间的间距
            pageButtonPosition: 'end', // 分页按钮位置
            data: transportTypes.value,
            textStyle: {
              fontSize: 12
            },
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
              type: 'graph',
              name: '交通方式分布',
              layout: 'circular',
              circular: {
                rotateLabel: true
              },
              data: nodesWithColor,
              links: linksWithColor,
              roam: true,
              focusNodeAdjacency: true,
              edgeSymbol: ['none', 'arrow'],
              edgeSymbolSize: [0, 10],
              symbolSize: 40,
              label: {
                show: true,
                position: 'right',
                formatter: '{b}',
                distance: 15  // 增加标签距离，避免文字与节点重叠
              },
              lineStyle: {
                curveness: 0.3
              },
              emphasis: {
                lineStyle: {
                  width: 5
                },
                focus: 'adjacency'
              },
              categories: transportTypes.value.map(type => ({
                name: type
              })),
              force: {
                edgeLength: 150,  // 增加边的长度
                repulsion: 1000,  // 增加斥力
                gravity: 0.1      // 减小引力
              },
              edgeLabel: {
                show: true,
                formatter: '{c}',
                fontSize: 12,
                distance: 10
              },
              // 调整图表位置
              center: ['25%', '50%'],  // 将图表中心点向右移动到25%位置
              radius: '60%',           // 适当调整图表半径
              animationDuration: 1500,
              animationEasingUpdate: 'quinticInOut'
            }
          ]
        } as EChartsOption;
      }
    })
    
    // 处理省份变更
    const handleProvinceChange = () => {
      console.log('省份变更为:', selectedProvince.value);
      // 当省份变更时，检查是否有相关数据
      if (selectedProvince.value !== '全国') {
        checkProvinceData(selectedProvince.value);
      } else {
        noDataError.value = '';
        // 当切换到全国视图时，在下一个tick渲染Highcharts
        setTimeout(() => {
          renderDependencyWheel();
        }, 0);
      }
    }
    
    // 渲染Highcharts依赖轮图
    const renderDependencyWheel = () => {
      const filteredData = filterSankeyData();
      if (filteredData.nodes.length === 0 || filteredData.links.length === 0) {
        return;
      }
      
      // 定义统计数据的接口
      interface NodeStat {
        totalOutgoing: number;
        outgoingLinks: Array<{ target: string; value: number }>;
        uniqueTargets: Set<string>;
        totalIncoming: number;
        incomingLinks: Array<{ source: string; value: number }>;
        uniqueSources: Set<string>;
        isProvince: boolean;
      }
      
      const nodeStats: Record<string, NodeStat> = {};
      
      // 遍历所有链接，收集各节点的统计信息
      filteredData.links.forEach(link => {
        const source = typeof link.source === 'string' 
          ? link.source 
          : typeof link.source === 'object' && link.source !== null 
            ? (link.source as SankeyNode).name 
            : '';
        const target = typeof link.target === 'string' 
          ? link.target 
          : typeof link.target === 'object' && link.target !== null 
            ? (link.target as SankeyNode).name 
            : '';
        const value = typeof link.value === 'number' ? link.value : 0;
        
        // 初始化省份节点统计数据结构
        if (!nodeStats[source]) {
          nodeStats[source] = {
            totalOutgoing: 0,
            outgoingLinks: [],
            uniqueTargets: new Set<string>(),
            totalIncoming: 0,
            incomingLinks: [],
            uniqueSources: new Set<string>(),
            isProvince: allProvinces.includes(source)
          };
        }
        
        // 初始化交通方式节点统计数据结构
        if (!nodeStats[target]) {
          nodeStats[target] = {
            totalOutgoing: 0,
            outgoingLinks: [],
            uniqueTargets: new Set<string>(),
            totalIncoming: 0,
            incomingLinks: [],
            uniqueSources: new Set<string>(),
            isProvince: allProvinces.includes(target)
          };
        }
        
        // 累加数据
        nodeStats[source].totalOutgoing += value;
        nodeStats[source].outgoingLinks.push({ target, value });
        nodeStats[source].uniqueTargets.add(target);
        
        nodeStats[target].totalIncoming += value;
        nodeStats[target].incomingLinks.push({ source, value });
        nodeStats[target].uniqueSources.add(source);
      });
      
      // 准备Highcharts依赖轮格式的数据
      const dependencyWheelData = filteredData.links.map(link => {
        const source = typeof link.source === 'string' 
          ? link.source 
          : typeof link.source === 'object' && link.source !== null 
            ? (link.source as SankeyNode).name 
            : '';
        
        const target = typeof link.target === 'string' 
          ? link.target 
          : typeof link.target === 'object' && link.target !== null 
            ? (link.target as SankeyNode).name 
            : '';
        
        const value = typeof link.value === 'number' ? link.value : 0;
        
        return {
          from: source,
          to: target,
          weight: value,
          // 为节点设置颜色
          color: getNodeColor(source),
          // 设置环形桑基图的透明度
          opacity: 0.7
        };
      });
      
      // 使用正确的Highcharts API调用
      const container = document.getElementById('highcharts-container');
      if (container) {
        // 创建图表配置对象
        const chartOptions = {
          chart: {
            height: 850,  // 增加图表高度
            backgroundColor: '#FFFFFF'
          },
          title: {
            text: '全国交通方式分布图',
            style: {
              fontSize: '20px',  // 增大标题字体
              fontWeight: 'bold'
            }
          },
          subtitle: {
            text: '环形桑葚图展示省份与交通方式关系',
            style: {
              fontSize: '14px',  // 增大副标题字体
              color: '#666'
            }
          },
          tooltip: {
            useHTML: true,
            formatter: function(): string {
              // @ts-ignore
              const point = this.point;
              
              // 如果是链接（两点之间的连线）
              if (point.from && point.to) {
                return `<b>${point.from} → ${point.to}</b><br/>数量: <b>${point.weight}</b>`;
              }
              
              // 如果是节点
              const nodeName = point.name || point.id;
              if (nodeName && nodeStats[nodeName]) {
                const stats = nodeStats[nodeName];
                
                // 省份节点显示
                if (stats.isProvince) {
                  const transportTypesCount = stats.uniqueTargets.size;
                  const totalTransport = stats.totalOutgoing;
                  
                  let html = `<div style="min-width: 150px;">`;
                  html += `<div style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">${nodeName}</div>`;
                  html += `<div>交通方式种类: <b>${transportTypesCount}</b> 种</div>`;
                  html += `<div>交通总数量: <b>${totalTransport}</b></div>`;
                  
                  // 添加交通方式详情（最多显示前5种）
                  if (stats.outgoingLinks && stats.outgoingLinks.length > 0) {
                    html += `<div style="margin-top: 8px; border-top: 1px solid #ddd; padding-top: 5px;">`;
                    html += `<div style="font-weight: bold; margin-bottom: 3px;">主要交通方式:</div>`;
                    
                    // 按数量排序并取前5个
                    const sortedLinks = [...stats.outgoingLinks].sort((a, b) => b.value - a.value).slice(0, 5);
                    sortedLinks.forEach(link => {
                      html += `<div>${link.target}: <b>${link.value}</b></div>`;
                    });
                    
                    if (stats.outgoingLinks.length > 5) {
                      html += `<div>... 等${stats.outgoingLinks.length - 5}种</div>`;
                    }
                    
                    html += `</div>`;
                  }
                  
                  html += `</div>`;
                  return html;
                } 
                // 交通工具节点显示
                else {
                  const provincesCount = stats.uniqueSources.size;
                  const totalUsage = stats.totalIncoming;
                  
                  let html = `<div style="min-width: 150px;">`;
                  html += `<div style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">${nodeName}</div>`;
                  html += `<div>使用省份数: <b>${provincesCount}</b> 个</div>`;
                  html += `<div>总使用量: <b>${totalUsage}</b></div>`;
                  
                  // 添加省份使用详情（最多显示前5个）
                  if (stats.incomingLinks && stats.incomingLinks.length > 0) {
                    html += `<div style="margin-top: 8px; border-top: 1px solid #ddd; padding-top: 5px;">`;
                    html += `<div style="font-weight: bold; margin-bottom: 3px;">主要使用省份:</div>`;
                    
                    // 按数量排序并取前5个
                    const sortedLinks = [...stats.incomingLinks].sort((a, b) => b.value - a.value).slice(0, 5);
                    sortedLinks.forEach(link => {
                      html += `<div>${link.source}: <b>${link.value}</b></div>`;
                    });
                    
                    if (stats.incomingLinks.length > 5) {
                      html += `<div>... 等${stats.incomingLinks.length - 5}个省份</div>`;
                    }
                    
                    html += `</div>`;
                  }
                  
                  html += `</div>`;
                  return html;
                }
              }
              
              // 默认显示
              return `<b>${nodeName || 'Unknown'}</b>`;
            },
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#ccc',
            borderWidth: 1,
            borderRadius: 8,
            shadow: true,
            padding: 10,
            style: {
              fontSize: '12px',
              fontFamily: 'Arial, sans-serif'
            }
          },
          series: [{
            type: 'dependencywheel' as const,
            name: '交通方式分布',
            data: dependencyWheelData,
            size: '98%',  // 增大环形图尺寸
            // 数据标签设置
            dataLabels: {
              color: '#333',
              // 文本路径设置
              textPath: {
                enabled: true,
                attributes: {
                  dy: 5
                }
              },
              distance: 15,  // 增加标签距离
              // 标签格式化
              formatter: function(): string {
                // @ts-ignore
                return this.point.name;
              }
            },
            // 节点宽度
            nodeWidth: 25  // 增加节点宽度
          }],
          // 信用标签
          credits: {
            enabled: false
          },
          // 导出按钮
          exporting: {
            enabled: true,
            filename: '全国交通方式分布图',
            allowHTML: true,
            buttons: {
              contextButton: {
                menuItems: [
                  'viewFullscreen',
                  'printChart',
                  'separator',
                  'downloadPNG',
                  'downloadJPEG',
                  'downloadPDF',
                  'downloadSVG',
                  'separator',
                  'downloadCSV',
                  'downloadXLS'
                ],
                symbolStroke: '#666',
                theme: {
                  fill: '#ffffff',
                  states: {
                    hover: {
                      fill: '#f8f8f8'
                    },
                    select: {
                      fill: '#f8f8f8'
                    }
                  }
                }
              }
            }
          },
          // 添加导出数据配置
          navigation: {
            buttonOptions: {
              theme: {
                fill: '#ffffff',
                stroke: '#e6e6e6',
                states: {
                  hover: {
                    fill: '#f2f2f2'
                  },
                  select: {
                    fill: '#f2f2f2'
                  }
                }
              }
            },
            menuItemStyle: {
              padding: '6px 16px',
              fontSize: '14px'
            },
            menuItemHoverStyle: {
              background: '#f8f8f8',
              color: '#333333'
            }
          }
        };
        
        // 创建图表
        // @ts-ignore - 忽略类型错误，Highcharts的类型定义与实际使用有差异
        Highcharts.chart(container, chartOptions);
      }
    }
    
    // 获取交通数据
    const fetchTransportationData = async () => {
      loading.value = true
      noDataError.value = '';
      
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
            
            // 不再过滤东北和西北
            console.log('API返回的所有节点:', [...transportSet, ...provinceSet]);
            
            // 从各种交通工具中提取交通工具类型
            // 判断哪些是交通方式，哪些是省份
            const transportList = Array.from(transportSet);
            const provinceListFromAPI = Array.from(provinceSet);
            
            // 修复：确保provinceList是Ref对象
            // 我们假设交通方式的名称不会出现在省份列表中
            const realTransportTypes = transportList.filter(t => !allProvinces.includes(t));
            transportTypes.value = realTransportTypes.sort();
            
            // 更新省份列表供筛选使用
            provinceList.value = provinceListFromAPI.sort();
            console.log('API返回的省份列表:', provinceList.value);
            
            // 创建新的节点数组 - 不再过滤东北和西北
            const nodes = [
              ...Array.from(transportSet).map(name => ({ name })),
              ...Array.from(provinceSet).map(name => ({ name }))
            ]
            
            // 创建新的链接数组 - 不再过滤东北和西北相关的链接
            const links = responseData
              .map((item: any) => {
                const isProvinceSource = allProvinces.includes(item.source);
                const isProvinceTarget = allProvinces.includes(item.target);
                
                // 如果source是省份且target不是省份，保持原样
                if (isProvinceSource && !isProvinceTarget) {
                  return {
                    source: item.source,
                    target: item.target,
                    value: item.value || 1
                  };
                }
                
                // 如果source不是省份但target是省份，交换位置
                if (!isProvinceSource && isProvinceTarget) {
                  return {
                    source: item.target,  // 省份作为source
                    target: item.source,  // 交通方式作为target
                    value: item.value || 1
                  };
                }
                
                // 其他情况保持原样
                return {
                  source: item.source,
                  target: item.target,
                  value: item.value || 1
                };
              });
            
            // 更新桑基图数据
            sankeyData.value = {
              nodes,
              links
            }
            
            console.log('已更新桑基图数据:', sankeyData.value)
            console.log('交通工具类型:', transportTypes.value)
            
            // 识别哪些省份有数据
            identifyProvincesWithData();
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
    
    // 识别哪些省份有相关数据
    const identifyProvincesWithData = () => {
      const provincesWithLinks = new Set<string>();
      
      // 将"全国"添加到集合中
      provincesWithLinks.add('全国');
      
      // 遍历所有链接，收集有相关链接的省份
      sankeyData.value.links.forEach(link => {
        const source = typeof link.source === 'string' 
          ? link.source 
          : typeof link.source === 'object' && link.source !== null 
            ? (link.source as SankeyNode).name 
            : '';
        const target = typeof link.target === 'string' 
          ? link.target 
          : typeof link.target === 'object' && link.target !== null 
            ? (link.target as SankeyNode).name 
            : '';
        
        // 检查是否为省份
        if (allProvinces.includes(source)) {
          provincesWithLinks.add(source);
        }
        if (allProvinces.includes(target)) {
          provincesWithLinks.add(target);
        }
      });
      
      // 更新有数据的省份集合
      provincesWithData.value = provincesWithLinks;
      console.log('有交通数据的省份:', Array.from(provincesWithLinks));
    }
    
    onMounted(async () => {
      loading.value = true
      try {
        // 获取交通数据
        await fetchTransportationData()
        // 如果初始视图是全国，渲染依赖轮图
        if (selectedProvince.value === '全国') {
          setTimeout(() => {
            renderDependencyWheel();
          }, 100);
        }
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
      availableProvinces, // 使用可用省份替代所有省份
      circularChartOptions,
      handleProvinceChange,
      loading,
      noDataError
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
  padding: 0;
}

/* Highcharts容器样式 */
#highcharts-container {
  width: 100%;
  height: 800px;  /* 调整全国图表高度 */
  margin: 0 auto;
}

/* 移动设备适配 */
@media screen and (max-width: 768px) {
  .transportation-container {
    padding: 10px;
  }
  
  #highcharts-container {
    height: 600px;  /* 调整移动设备上的高度 */
  }
  
  .chart-wrapper {
    box-shadow: none;
  }
}

.no-data-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 500px;
  width: 100%;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 20px;
}

.loading-container {
  min-height: 700px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
}

/* 移动设备适配加载容器 */
@media screen and (max-width: 768px) {
  .loading-container {
    min-height: 500px;
  }
}
</style> 