<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useScenicStore } from '@/stores/scenic'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const scenicStore = useScenicStore()
const loading = ref(false)
const radarChart = ref<HTMLElement | null>(null)
const stackedBarChart = ref<HTMLElement | null>(null)
const radarChartInstance = ref<echarts.ECharts | null>(null)
const stackedBarChartInstance = ref<echarts.ECharts | null>(null)

// 保底数量阈值和保底值配置
const minValueThreshold = 50; // 低于此值将触发保底机制
const minDisplayValue = 100; // 保底值
const isPaddingEnabled = ref(true); // 是否启用保底机制

// 颜色主题
const colors = {
  radar: {
    background: 'rgba(84, 112, 198, 0.5)',
    border: 'rgba(84, 112, 198, 0.8)',
    main: '#5470c6'
  },
  bars: [
    '#5470c6', // 蓝色
    '#91cc75', // 绿色
    '#fac858', // 黄色
    '#ee6666', // 红色
    '#73c0de', // 浅蓝
    '#3ba272', // 深绿
    '#fc8452', // 橙色
    '#9a60b4', // 紫色
    '#ea7ccc', // 粉色
    '#6b778d', // 灰蓝
    '#a4c46c', // 橄榄绿
    '#d9735e', // 陶砖红
    '#96dee8', // 天蓝
    '#8c7bc4', // 紫罗兰
    '#c1c1c1', // 银灰
    '#abb2bf', // 石板灰
    '#d19a66', // 金棕
    '#57b698', // 绿松石
    '#e06c75', // 珊瑚红
    '#35a7d4'  // 钴蓝
  ]
}

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChart.value) return
  
  radarChartInstance.value = echarts.init(radarChart.value)
  
  // 检查数据是否存在
  if (!scenicStore.typeRadarData || !scenicStore.typeRadarData.length) {
    radarChartInstance.value.setOption({
      title: {
        text: '暂无景区类型数据',
        left: 'center',
        top: 'center',
        textStyle: {
          fontSize: 16,
          color: '#999'
        }
      }
    })
    return
  }
  
  // 不再过滤掉"未分类景区"，保留所有类型
  const radarData = scenicStore.typeRadarData.map(item => {
    // 将"景区"类型替换为"A级景区"
    if (item.name === '景区') {
      return {...item, name: 'A级景区'};
    }
    return item;
  });
  
  // 准备雷达图的指示器数据
  const indicator = radarData.map(item => ({
    name: item.name,
    max: Math.max(...radarData.map(d => d.value || 0)) * 1.2 || 100, // 防止所有值为0的情况
    axisLabel: {
      show: true,
      fontSize: 12
    }
  }))
  
  // 准备雷达图的数据
  const chartData = [
    {
      value: radarData.map(item => item.value || 0),
      name: '景区数量',
      areaStyle: {
        opacity: 0.7
      }
    }
  ]
  
  const option = {
    title: {
      text: '景区类型雷达图',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      },
      top: 15, // 增加顶部间距，把标题下移
      bottom: 10, // 确保标题与图表有足够间距
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params: any) {
        // 如果是点击的是轴线上的点
        if (params.componentType === 'radar' && params.seriesType === 'radar') {
          // 获取雷达图的具体指标点
          const pointIndex = params.encode?.tooltip?.[0];
          if (pointIndex !== undefined && indicator[pointIndex]) {
            return `${indicator[pointIndex].name}: ${params.value?.[pointIndex]}个景区`;
          }
        }
        
        // 默认情况，显示所有点的值
        return radarData.map(item => 
          `${item.name}: ${item.value || 0}个景区`
        ).join('<br>');
      }
    },
    legend: {
      show: false // 隐藏图例小方块
    },
    radar: {
      indicator: indicator,
      shape: 'circle',
      radius: '70%', // 增加雷达图半径，使其内容更大
      center: ['50%', '57%'], // 将雷达图中心向下移动，远离标题
      splitNumber: 4,
      axisName: {
        color: '#666',
        fontSize: 14,  // 增大字号
        fontWeight: 'normal',  // 调整文字粗细
        backgroundColor: 'rgba(248, 249, 250, 0.7)',  // 增加背景色的不透明度
        padding: [5, 8],  // 增加内边距使文字更突出
        borderRadius: 4,  // 增加圆角
        // 格式化文本，处理长文本
        formatter: function(value: string) {
          if (value.length > 4) {
            return value.substring(0, 3) + '\n' + value.substring(3);
          }
          return value;
        }
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(250, 250, 250, 0.3)', 'rgba(235, 238, 245, 0.3)'],
          shadowColor: 'rgba(0, 0, 0, 0.1)',
          shadowBlur: 10
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(211, 211, 211, 0.8)'
        }
      },
      splitLine: {
        lineStyle: {
          color: ['rgba(211, 211, 211, 0.8)']
        }
      },
      // 增加间距，减少点的重叠
      nameGap: 25,  // 增加间距，使名称更远离雷达图
      // 添加轴标签格式化，将数字取整
      axisLabel: {
        formatter: function(value: number) {
          return Math.round(value);
        }
      }
    },
    series: [
      {
        name: '景区类型分布',
        type: 'radar',
        data: chartData,
        symbol: 'circle',
        symbolSize: 8, // 增大点的大小，使其更容易选中
        emphasis: {
          focus: 'self', // 高亮自身
          scale: 1.2, // 放大效果
          lineStyle: {
            width: 4
          },
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.3)'
          }
        },
        itemStyle: {
          color: colors.radar.main,
          borderColor: colors.radar.border,
          borderWidth: 2,
          shadowBlur: 5,
          shadowColor: 'rgba(0, 0, 0, 0.3)'
        },
        areaStyle: {
          color: colors.radar.background,
          opacity: 0.7
        },
        lineStyle: {
          width: 2.5
        }
      }
    ],
    animation: true,
    animationDuration: 1000,
    animationEasing: 'cubicOut' as const
  }
  
  radarChartInstance.value.setOption(option)
  
  // 添加点击事件
  radarChartInstance.value.on('click', function(params: any) {
    if (params.componentType === 'radar' && params.seriesType === 'radar') {
      // 根据点击位置找到对应的类型
      const pointIndex = params.encode?.tooltip?.[0];
      if (pointIndex !== undefined && indicator[pointIndex]) {
        const typeName = indicator[pointIndex].name;
        const value = params.value?.[pointIndex];
        console.log(`点击了类型: ${typeName}, 景区数量: ${value}`);
        // 在这里可以添加更多的点击响应逻辑
      }
    }
  });
}

// 初始化重叠柱状图（替代原来的矩形树图）
const initStackedBarChart = () => {
  if (!stackedBarChart.value) return
  
  stackedBarChartInstance.value = echarts.init(stackedBarChart.value)
  
  // 检查数据是否存在
  if (!scenicStore.typeSunburstData || !scenicStore.typeSunburstData.children || !scenicStore.typeSunburstData.children.length) {
    stackedBarChartInstance.value.setOption({
      title: {
        text: '暂无景区等级分布数据',
        left: 'center',
        top: 'center',
        textStyle: {
          fontSize: 16,
          color: '#999'
        }
      }
    })
    return
  }
  
  // 过滤掉"未分类景区"
  const filteredTypes = scenicStore.typeSunburstData.children.filter((item: any) => item.name !== '未分类景区').map((item: any) => {
    // 将"景区"类型替换为"A级景区"
    if (item.name === '景区') {
      return {...item, name: 'A级景区'};
    }
    return item;
  });
  
  // 调试输出
  console.log('过滤后的数据:', filteredTypes);
  
  // 准备柱状图数据
  const prepareBarData = () => {
    // 收集所有的景区类型和等级
    const typeNames: string[] = [];
    const levelNames = new Set<string>();
    
    // 确定所有的类型名和等级名
    filteredTypes.forEach((type: any) => {
      typeNames.push(type.name);
      if (type.children && type.children.length > 0) {
        type.children.forEach((level: any) => {
          // 排除 xxx 和 null 等级
          if (level.name !== 'xxx' && level.name !== 'null') {
            levelNames.add(level.name);
          }
        });
      }
    });
    
    // 将等级转换为数组并按照优先级排序（5A、4A...）
    const sortedLevelNames = Array.from(levelNames).sort((a, b) => {
      // 自定义排序逻辑，将5A放在最前面，依次是4A, 3A, 2A, 1A，然后是其他等级
      const getWeight = (name: string) => {
        if (name.includes('5A')) return 1;
        if (name.includes('4A')) return 2;
        if (name.includes('3A')) return 3;
        if (name.includes('2A')) return 4;
        if (name.includes('1A')) return 5;
        if (name.includes('国家级')) return 6;
        if (name.includes('省级')) return 7;
        if (name.includes('市级')) return 8;
        return 10;
      };
      return getWeight(a) - getWeight(b);
    });
    
    // 准备系列数据（每个等级一个系列）和总量数据
    const series: any[] = [];
    const typeTotalValues: {[key: string]: number} = {};
    
    // 先计算每个类型的总量
    typeNames.forEach(typeName => {
      let total = 0;
      // 查找该类型的所有等级数据
      const typeData = filteredTypes.find((t: any) => t.name === typeName);
      if (typeData && typeData.children) {
        typeData.children.forEach((level: any) => {
          // 排除 xxx 和 null 等级
          if (level.name !== 'xxx' && level.name !== 'null') {
            total += level.value || 0;
          }
        });
      }
      typeTotalValues[typeName] = total;
    });
    
    // 创建自定义颜色映射，确保每个等级有独特的颜色
    const levelColorMap: {[key: string]: string} = {};
    sortedLevelNames.forEach((levelName, index) => {
      // 确保不会超出颜色数组范围
      const colorIndex = index % colors.bars.length;
      levelColorMap[levelName] = colors.bars[colorIndex];
    });
    
    // 为每个等级创建一个系列
    sortedLevelNames.forEach((levelName) => {
      const seriesData: any[] = [];
      
      // 为每个类型填充该等级的数据
      typeNames.forEach(typeName => {
        // 查找该类型
        const typeData = filteredTypes.find((t: any) => t.name === typeName);
        
        // 默认值
        let value = 0;
        let realValue = 0;
        let hasPadding = false;
        
        // 如果找到类型，则查找等级
        if (typeData && typeData.children) {
          const levelData = typeData.children.find((l: any) => l.name === levelName);
          
          if (levelData) {
            realValue = levelData.value;
            
            // 应用保底机制
            if (isPaddingEnabled.value && realValue < minValueThreshold) {
              value = minDisplayValue;
              hasPadding = true;
            } else {
              value = realValue;
            }
          }
        }
        
        // 添加到系列数据中
        seriesData.push({
          value: value,
          realValue: realValue,
          hasPadding: hasPadding,
          typeName: typeName,
          levelName: levelName
        });
      });
      
      // 创建系列，使用唯一颜色
      series.push({
        name: levelName,
        type: 'bar',
        stack: 'total',
        barWidth: '60%',
        label: {
          show: true,
          position: 'inside',
          formatter: (params: any) => {
            // 显示实际值，如果触发了保底机制，则添加标记
            if (params.data.hasPadding) {
              return `${params.data.realValue}*`;
            }
            return params.data.realValue > 0 ? params.data.realValue : '';
          },
          fontSize: 12,
          color: '#fff',
          textBorderColor: 'rgba(0, 0, 0, 0.3)',
          textBorderWidth: 2
        },
        emphasis: {
          focus: 'series', // 高亮同一系列的所有数据项
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0,0,0,0.3)'
          }
        },
        data: seriesData,
        itemStyle: {
          color: levelColorMap[levelName]
        }
      });
    });
    
    // 创建总数显示系列（顶部标签）
    const totalLabelSeries = {
      name: '总数',
      type: 'bar',
      stack: 'total',
      silent: true, // 禁止交互
      itemStyle: {
        opacity: 0, // 完全透明
        borderWidth: 0
      },
      label: {
        show: true,
        position: 'top',
        distance: 5, // 距离柱子顶部的距离
        formatter: (params: any) => {
          const typeName = params.name;
          return `总计: ${typeTotalValues[typeName]}`;
        },
        fontSize: 14,
        fontWeight: 'bold',
        color: '#303133'
      },
      data: typeNames.map(typeName => ({
        value: 0, // 值为0，只用于显示标签
        typeName: typeName,
        totalValue: typeTotalValues[typeName] // 存储总值用于提示框显示
      }))
    };
    
    series.push(totalLabelSeries as any);
    
    return {
      typeNames,
      series,
      levelColorMap,
      typeTotalValues
    };
  };
  
  const { typeNames, series, typeTotalValues } = prepareBarData();
  
  // 设置柱状图选项
  const option = {
    title: {
      text: '景区类型与等级分析柱状图',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      },
    },
    tooltip: {
      trigger: 'item', // 改为item，使提示框只针对当前悬停项
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        // 检查是否是透明的总数系列
        if (params.seriesName === '总数') {
          return `<strong>${params.name}</strong><br/><div style="margin-top: 5px;">
            <strong>总计: ${typeTotalValues[params.name]}个</strong>
          </div>`;
        }
        
        // 如果不是有效数据，返回空
        if (!params.data || params.data.realValue === undefined) return '';
        
        const typeName = params.name;
        const levelName = params.seriesName;
        const realValue = params.data.realValue;
        const displayValue = params.data.value;
        const hasPadding = params.data.hasPadding;
        const color = params.color;
        
        let result = `<div style="padding: 4px 0;">
          <strong>${typeName}</strong> - <span style="color:${color}; font-weight:bold;">${levelName}</span>
        </div>`;
        
        result += `<div style="display: flex; align-items: center; margin: 5px 0;">
          <span style="display: inline-block; width: 10px; height: 10px; background: ${color}; margin-right: 6px;"></span>
          <span>数量: <strong>${realValue}</strong>个`;
          
        if (hasPadding) {
          result += ` <span style="color: #ff4500;">(已保底至${displayValue})</span>`;
        }
        
        result += `</span></div>`;
        
        // 添加总计信息
        result += `<div style="margin-top: 5px; padding-top: 5px; border-top: 1px dashed #ccc;">
          <strong>该类型总计: ${typeTotalValues[typeName]}个</strong>
        </div>`;
        
        return result;
      }
    },
    legend: {
      data: series.slice(0, -1).map(item => item.name), // 排除总数系列
      top: 50,
      type: 'plain', // 普通模式，不使用滚动
      orient: 'horizontal',
      padding: [5, 5, 5, 5],
      textStyle: {
        fontSize: 12
      },
      // 自动计算每行的图例数量
      itemGap: 15,
      formatter: (name: string) => {
        // 如果名称太长，截断并加上省略号
        if (name.length > 20) {
          return name.slice(0, 18) + '...';
        }
        return name;
      }
    },
    grid: {
      left: '5%',
      right: '4%',
      bottom: '0%',
      top: '130px', // 增加顶部空间，留给图例
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: typeNames,
      axisLabel: {
        rotate: 45,
        interval: 0,
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      name: '景区数量',
      nameLocation: 'middle',
      nameGap: 50,
      nameTextStyle: {
        fontSize: 14,
        fontWeight: 'bold'
      }
    },
    series: series
    // 移除 dataZoom
  };
  
  stackedBarChartInstance.value.setOption(option);
  
  // 添加鼠标事件
  stackedBarChartInstance.value.on('click', function(params: any) {
    console.log('点击了图表:', params);
    if (params.data) {
      console.log('节点数据:', params.data);
    }
  });
}

// 窗口大小改变时重新调整图表大小
const handleResize = () => {
  radarChartInstance.value?.resize()
  stackedBarChartInstance.value?.resize()
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const result = await scenicStore.getScenicTypeDistribution()
    
    // 检查返回的数据是否符合预期
    if (!result || !result.radar_data || !result.sunburst_data) {
      ElMessage.error('获取景区类型分布数据格式异常，请稍后重试')
      loading.value = false
      return
    }
    
    // 调试输出数据，检查结构
    console.log('获取到的数据:', result)
    console.log('雷达图数据:', result.radar_data)
    console.log('旭日图数据:', result.sunburst_data)
    
    nextTick(() => {
      initRadarChart()
      initStackedBarChart()
    })
  } catch (error) {
    console.error('获取景区类型分布数据失败:', error)
    ElMessage.error('获取景区类型分布数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  window.addEventListener('resize', handleResize)
  
  const adjustHeight = () => {
    nextTick(() => {
      const leftColumnEl = document.querySelector('.left-column') as HTMLElement;
      const rightColumnEl = document.querySelector('.right-column') as HTMLElement;
      
      if (leftColumnEl && rightColumnEl && window.innerWidth >= 992) {
        const leftHeight = leftColumnEl.offsetHeight;
        rightColumnEl.style.height = `${leftHeight}px`;
        
        if (stackedBarChartInstance.value) {
          stackedBarChartInstance.value.resize();
        }
      }
    });
  };
  
  adjustHeight();
  window.addEventListener('resize', adjustHeight);

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
    window.removeEventListener('resize', adjustHeight);
    
    radarChartInstance.value?.dispose()
    stackedBarChartInstance.value?.dispose()
  })
})
</script>

<template>
  <div class="scenic-classification-container">
    <el-row :gutter="20">
      <!-- 左侧列：雷达图和分析结论 -->
      <el-col :xs="24" :sm="24" :md="10" :lg="8" :xl="8" class="left-column">
        <el-card class="chart-card" :body-style="{ padding: '15px' }">
      <template #header>
        <div class="card-header">
              <span class="card-title">景区类型雷达图</span>
        </div>
      </template>
      
          <div v-loading="loading">
            <div class="chart-container radar-container" ref="radarChart"></div>
          </div>
          
          <el-empty v-if="scenicStore.typeRadarData.length === 0 && !loading" description="暂无数据" />
    </el-card>
    
        <el-card class="analysis-card" :body-style="{ padding: '15px' }">
      <template #header>
        <div class="card-header">
              <span class="card-title">分析结论</span>
        </div>
      </template>
      
      <div class="analysis-content">
        <el-alert
              title="景区类型与等级分布分析结论"
          type="info"
          :closable="false"
              :show-icon="true"
            >
              <p>1. 景区类型中"未分类景区"数量最多，覆盖范围最广；</p>
              <p>2. "A级景区"和"文物保护单位"是第二、三大类型；</p>
              <p>3. 国家级在各类型景区中占比比例均匀；</p>
              <p>4. 4A景区数量在各等级景区中占比最高；</p>
              <p>5. 湿地风景区中世界级占比较高，具有较高国际影响力。</p>
        </el-alert>
          </div>
          
          <!-- 添加保底机制开关 -->
          <div class="padding-control">
            <el-switch
              v-model="isPaddingEnabled"
              active-text="启用小数据保底"
              inactive-text="显示原始数据"
              @change="initStackedBarChart"
            />
            <div class="padding-info" v-if="isPaddingEnabled">
              <el-tag size="small" type="warning">数据量小于 {{ minValueThreshold }} 时，在图中保底显示为 100 ，实际值为 * 号数据</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧列：重叠柱状图 -->
      <el-col :xs="24" :sm="24" :md="14" :lg="16" :xl="16" class="right-column">
        <el-card class="chart-card stacked-bar-card" :body-style="{ padding: '15px' }">
          <template #header>
            <div class="card-header">
              <span class="card-title">景区类型与等级分析</span>
              <!-- 添加调试按钮 -->
              <el-button 
                v-if="scenicStore.typeSunburstData" 
                size="small" 
                type="primary" 
                @click="initStackedBarChart"
              >刷新图表</el-button>
            </div>
          </template>
          
          <div v-loading="loading">
            <div class="chart-container stacked-bar-container" ref="stackedBarChart"></div>
            <!-- 添加图表加载状态信息 -->
            <div v-if="!loading && (!scenicStore.typeSunburstData || !scenicStore.typeSunburstData.children || !scenicStore.typeSunburstData.children.length)" class="no-data-info">
              <p>当前没有可用的景区等级数据</p>
              <el-button size="small" @click="fetchData">重新加载数据</el-button>
            </div>
            <!-- 添加保底机制说明 -->
            <div v-if="isPaddingEnabled && !loading" class="padding-legend">
              <span class="padding-marker">*</span> 表示已触发保底机制，实际数值小于 {{ minValueThreshold }}
            </div>
      </div>
    </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.scenic-classification-container {
  display: flex;
  flex-direction: column;
  padding: 0 0 10px 0;
}

.chart-card, .analysis-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
}

.stacked-bar-card {
  height: calc(100% - 20px);
  display: flex;
  flex-direction: column;
}

.left-column, .right-column {
  display: flex;
  flex-direction: column;
}

.right-column {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.chart-container {
  width: 100%;
  border-radius: 6px;
  padding: 10px;
  transition: all 0.3s;
}

.radar-container {
  height: 450px; /* 增加雷达图容器高度 */
}

.stacked-bar-container {
  height: 800px; /* 增加高度 */
  flex: 1;
}

.chart-container:hover {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.analysis-content p {
  margin: 8px 0;
  line-height: 1.6;
  font-size: 14px;
  color: #333;
}

.padding-control {
  margin-top: 16px;
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
}

.padding-info {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
}

.padding-legend {
  text-align: center;
  margin: 10px 0;
  font-size: 13px;
  color: #666;
}

.padding-marker {
  color: #ff4500;
  font-weight: bold;
  margin-right: 4px;
}

/* 媒体查询设置 */
@media (max-width: 768px) {
  .radar-container {
    height: 350px;
  }
  
  .stacked-bar-container {
    height: 500px;
  }
  
  .scenic-classification-container {
    padding: 0;
  }
}

:deep(.el-alert__content) {
  width: 100%;
  padding: 5px 0;
}

:deep(.el-alert__title) {
  font-size: 15px;
  font-weight: bold;
  margin-bottom: 8px;
}

@media (min-width: 992px) {
  .el-row {
    display: flex;
    align-items: stretch;
  }
  
  .left-column, .right-column {
    height: 100%;
  }
}

.no-data-info {
  padding: 20px;
  text-align: center;
  color: #909399;
}
</style> 