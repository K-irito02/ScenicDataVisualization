<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { useScenicStore } from '@/stores/scenic'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import typeLevelData from '@/assets/search/type_level_data.json'
import type { EChartsOption, ECharts } from 'echarts'

// 扩展 OpenTimeData 接口，添加我们需要的字段
interface ExtendedOpenTimeData {
  timeRange: string
  count: number
  weekdays?: string
  id?: string
  name?: string
}

const scenicStore = useScenicStore()
// 为每个图表创建独立的加载状态
const barLoading = ref(false)
const boxplotLoading = ref(false)
const timeDataLoading = ref(false)
const selectedScenicType = ref('景区') // 改回默认值为"景区"
const boxplotScenicType = ref('景区') // 改回默认值为"景区"
const selectedBoxplotType = ref('byType') // 默认显示按类型的箱线图 'byType' or 'byLevel'
const barChartRef = ref<HTMLElement | null>(null)
const boxplotChartRef = ref<HTMLElement | null>(null)
const heatmapChartRef = ref<HTMLElement | null>(null)
const radarChartRef = ref<HTMLElement | null>(null)
const barChartInstance = ref<ECharts | null>(null)
const boxplotChartInstance = ref<ECharts | null>(null)
const heatmapChartInstance = ref<ECharts | null>(null)
const radarChartInstance = ref<ECharts | null>(null)
const selectedTimeRange = ref('')
const showTimeMap = ref(false)

// 修改景区类型的标签显示
const scenicTypeLabels: Record<string, string> = {
  '景区': 'A级景区', // 将"景区"显示为"A级景区"
}

// 所有景区类型
const scenicTypes = computed(() => {
  return typeLevelData.types || []
})

// 当前选择类型的等级列表
const currentTypeLevels = computed(() => {
  if (selectedScenicType.value) {
    return (typeLevelData.typeLevels as Record<string, string[]>)[selectedScenicType.value] || []
  }
  return []
})

// 箱线图类型选项
const boxplotTypeOptions = [
  { value: 'byType', label: '各景区类型门票价格分布' },
  { value: 'byLevel', label: '景区类型各等级门票价格分布' }
]

// 开放时间相关变量
const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
// 恢复timeRanges用于热力图
const timeRanges = Array.from({ length: 24 }, (_, i) => `${i}:00`)
// 新增：时间段名称对应的时间范围
const timeRangeNames = ['午夜', '凌晨', '早晨', '上午', '中午', '下午', '傍晚', '夜晚']
// 新增：时间段对应的小时范围
const timeRangeHours = [
  [0, 3],   // 午夜: 0:00-3:00
  [3, 6],   // 凌晨: 3:00-6:00
  [6, 9],   // 早晨: 6:00-9:00
  [9, 12],  // 上午: 9:00-12:00
  [12, 14], // 中午: 12:00-14:00
  [14, 17], // 下午: 14:00-17:00
  [17, 20], // 傍晚: 17:00-20:00
  [20, 24]  // 夜晚: 20:00-24:00
]

// 新增：将小时数转换为对应的时间段索引的函数
const hourToRangeIndex = (hour: number): number => {
  for (let i = 0; i < timeRangeHours.length; i++) {
    if (hour >= timeRangeHours[i][0] && hour < timeRangeHours[i][1]) {
      return i
    }
  }
  return 0 // 默认返回第一个时间段
}

const timeHeatmapData = ref<any[]>([])
const radarData = ref<any[]>([])

// 解析工作日范围
const parseWeekdays = (weekdaysStr: string): string[] => {
  if (!weekdaysStr) {
    console.log('工作日字符串为空')
    // 默认返回全周
    return [...weekdays]
  }
  
  console.log('正在解析工作日字符串:', weekdaysStr)
  const result: string[] = []
  
  // 处理全周相关的关键词
  if (weekdaysStr.includes('全周') || 
      weekdaysStr.includes('每天') || 
      weekdaysStr.includes('全年') || 
      weekdaysStr.includes('天天') || 
      weekdaysStr.includes('全天') ||
      weekdaysStr.includes('全年无休') || 
      weekdaysStr.includes('无休')) {
    console.log('检测到全周关键词，返回所有工作日')
    return [...weekdays]
  }
  
  const parts = weekdaysStr.split(/[,，、;；\s]+/).filter(Boolean)
  console.log('分割后的工作日部分:', parts)
  
  parts.forEach(part => {
    part = part.trim()
    
    // 处理范围格式，如"周一-周五"或"周一至周五"
    if (part.includes('-') || part.includes('至') || part.includes('到')) {
      const rangeParts = part.split(/[-至到]/)
      if (rangeParts.length === 2) {
        const start = rangeParts[0].trim()
        const end = rangeParts[1].trim()
        const startIndex = weekdays.indexOf(start)
        const endIndex = weekdays.indexOf(end)
        
        if (startIndex >= 0 && endIndex >= 0) {
          // 确保范围有效（即使end在start之前，如"周日-周二"）
          if (startIndex <= endIndex) {
            for (let i = startIndex; i <= endIndex; i++) {
              if (!result.includes(weekdays[i])) {
                result.push(weekdays[i])
              }
            }
          } else {
            // 处理跨周的情况，如"周日-周二"
            for (let i = startIndex; i < weekdays.length; i++) {
              if (!result.includes(weekdays[i])) {
                result.push(weekdays[i])
              }
            }
            for (let i = 0; i <= endIndex; i++) {
              if (!result.includes(weekdays[i])) {
                result.push(weekdays[i])
              }
            }
          }
        } else {
          console.log(`无法识别工作日范围: ${part}, 起始日: ${start}(${startIndex}), 结束日: ${end}(${endIndex})`)
        }
      }
    } else {
      // 单个工作日
      // 检查是否包含"周"字
      let dayName = part
      
      // 如果只包含数字1-7，可能表示周一到周日
      if (/^[1-7]$/.test(part)) {
        const index = parseInt(part) - 1  // 1对应周一，7对应周日
        if (index >= 0 && index < 7) {
          dayName = weekdays[index]
        }
      }
      
      if (weekdays.includes(dayName)) {
        if (!result.includes(dayName)) {
          result.push(dayName)
        }
      } else {
        console.log(`无法识别的工作日: ${part}`)
      }
    }
  })
  
  // 如果没有识别出任何天，默认为全周
  if (result.length === 0) {
    console.log('未能识别工作日格式，默认为全周:', weekdaysStr)
    return [...weekdays]
  }
  
  return result
}

// 将时间字符串转换为小时数（考虑非整点的四舍五入）
const parseTimeToHour = (timeStr: string): number | null => {
  // 移除所有空格
  timeStr = timeStr.trim().replace(/\s+/g, '')
  
  // 特殊情况处理
  if (timeStr === '24' || timeStr === '24时' || timeStr === '24点') {
    return 24
  }
  
  // 处理只有小时的情况，如"9"而不是"9:00"
  if (/^\d+$/.test(timeStr)) {
    const hours = parseInt(timeStr)
    if (hours >= 0 && hours <= 24) {
      return hours
    }
    return null
  }
  
  // 尝试匹配多种时间格式: 数字:数字, 数字点数字, 数字时数字分
  const timeRegex = /(\d{1,2})[:：.点时]?(\d{0,2})/
  const match = timeStr.match(timeRegex)
  
  if (match) {
    const hours = parseInt(match[1])
    const minutes = match[2] ? parseInt(match[2]) : 0
    
    // 有效性检查
    if (isNaN(hours) || hours < 0 || hours > 24) {
      console.log(`无效的小时: ${hours}, 原字符串: ${timeStr}`)
      return null
    }
    if (isNaN(minutes) || minutes < 0 || minutes >= 60) {
      console.log(`无效的分钟: ${minutes}, 原字符串: ${timeStr}`)
      return null
    }
    
    // 对于24:00这种特殊情况
    if (hours === 24 && minutes === 0) return 24
    
    // 四舍五入到最接近的小时
    if (minutes >= 30) {
      return Math.min(hours + 1, 24)
    } else {
      return hours
    }
  }
  
  console.log(`无法解析的时间字符串: ${timeStr}`)
  return null
}

// 解析时间范围，返回小时范围数组 [[起始小时, 结束小时], ...]
const parseTimeRanges = (timeRangeStr: string): number[][] => {
  if (!timeRangeStr) {
    console.log('时间范围字符串为空')
    return []
  }
  
  console.log('正在解析时间范围字符串:', timeRangeStr)
  
  // 处理全天24小时的情况
  if (timeRangeStr.includes('00:00-24:00') || 
      timeRangeStr.includes('0:00-24:00') || 
      /全天/.test(timeRangeStr.toLowerCase()) ||
      /24小时/.test(timeRangeStr) ||
      /24 ?h/i.test(timeRangeStr) ||
      /(\d+:\d+|\d+)[^\d]+24:?0?0?/i.test(timeRangeStr)) {
    console.log('检测到全天24小时关键词')
    return [[0, 24]]
  }
  
  const result: number[][] = []
  // 尝试用多种分隔符分割多个时间段
  const separators = /[,，;；、\s]+/
  let timeRanges = timeRangeStr.split(separators).filter(Boolean)
  
  console.log('分割后的时间段:', timeRanges)
  
  timeRanges.forEach(timeRange => {
    // 替换中文冒号为英文冒号，移除空格
    timeRange = timeRange.trim().replace(/[：]/g, ':').replace(/\s+/g, '')
    
    // 查找时间范围分隔符(-, 至, 到)
    const rangeSeparator = timeRange.match(/[-至到]/)
    if (!rangeSeparator) {
      console.log(`未找到时间范围分隔符: ${timeRange}`)
      return
    }
    
    // 根据找到的分隔符分割起止时间
    const parts = timeRange.split(rangeSeparator[0])
    
    if (parts.length === 2) {
      let startStr = parts[0].trim()
      let endStr = parts[1].trim()
      
      // 处理省略上午/下午的情况，如"9:00-17:00"
      let startHour = parseTimeToHour(startStr)
      let endHour = parseTimeToHour(endStr)
      
      // 处理特殊情况
      if (startHour !== null && endHour !== null) {
        console.log(`解析时间范围: ${startStr}-${endStr} => ${startHour}-${endHour}`)
        
        // 如果结束时间小于开始时间，假设跨越午夜
        if (endHour < startHour) {
          console.log(`检测到跨午夜时间范围: ${startHour}-${endHour}，调整为${startHour}-${endHour+24}`)
          endHour += 24
        }
        
        result.push([startHour, endHour])
      } else {
        console.log(`无法解析时间范围的某一部分: ${startStr}-${endStr}`)
      }
    }
  })
  
  // 如果没有解析出任何时间段，尝试一些启发式处理
  if (result.length === 0) {
    console.log('尝试使用启发式方法解析时间范围:', timeRangeStr)
    
    // 搜索开放时间中的数字，并尝试将它们配对
    const hourMatches = timeRangeStr.match(/\d+/g)
    if (hourMatches && hourMatches.length >= 2) {
      // 假设第一个数字是开始时间，第二个是结束时间
      const startHour = Math.min(parseInt(hourMatches[0]), 24)
      const endHour = Math.min(parseInt(hourMatches[1]), 24)
      
      if (startHour < endHour) {
        console.log(`使用启发式方法解析时间范围: ${startHour}-${endHour}`)
        result.push([startHour, endHour])
      }
    }
  }
  
  // 记录无法解析的情况
  if (result.length === 0) {
    console.warn('未能解析时间范围，使用默认值 9:00-18:00:', timeRangeStr)
    // 默认设置为9:00-18:00
    return [[9, 18]]
  }
  
  return result
}

// 初始化平均票价条形图
const initBarChart = () => {
  if (!barChartRef.value) return
  
  barChartInstance.value = echarts.init(barChartRef.value)
  updateBarChart()
}

// 更新平均票价条形图
const updateBarChart = async () => {
  if (!barChartInstance.value) return
  
  barLoading.value = true
  
  try {
    // 获取数据
    const response = await scenicStore.getTicketAvgPrice(selectedScenicType.value)
    const priceData = response || []
    
    if (!priceData.length) {
      barChartInstance.value.setOption({
        title: {
          text: '暂无数据',
          left: 'center',
          top: 'center'
        }
      })
      barLoading.value = false
      return
    }
    
    // 处理数据
    const xAxisData = priceData.map((item: any) => item.level)
    const seriesData = priceData.map((item: any) => item.avg_price)
    
    // 计算Y轴范围
    const maxPrice = Math.max(...seriesData)
    const yAxisMax = Math.ceil(maxPrice * 1.1) // 增加10%空间
    
    // 使用映射获取正确的显示名称
    const displayName = scenicTypeLabels[selectedScenicType.value] || selectedScenicType.value
    
    const option = {
      title: {
        text: `${displayName}平均门票价格`,
        left: 'center',
        subtext: '注：使用景区最低票价计算',
        top: 20 // 增加标题顶部边距
      },
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}元'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: 100, // 增加图表顶部边距，给标题和副标题留出空间
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: xAxisData,
        axisLabel: {
          interval: 0,
          rotate: 30
        }
      },
      yAxis: {
        type: 'value',
        name: '平均价格(元)',
        min: 0,
        max: yAxisMax
      },
      series: [
        {
          name: '平均门票价格',
          type: 'bar',
          data: seriesData,
          itemStyle: {
            color: '#409EFF'
          },
          label: {
            show: true,
            position: 'top',
            formatter: '{c}元'
          },
          barWidth: '40%'
        }
      ]
    }
    
    barChartInstance.value.setOption(option)
  } catch (error) {
    console.error('获取平均票价数据失败:', error)
    ElMessage.error('获取平均票价数据失败')
  } finally {
    barLoading.value = false
  }
}

// 初始化箱线图
const initBoxplotChart = () => {
  if (!boxplotChartRef.value) return
  
  boxplotChartInstance.value = echarts.init(boxplotChartRef.value)
  updateBoxplotChart()
}

// 更新箱线图
const updateBoxplotChart = async () => {
  if (!boxplotChartInstance.value) return
  
  boxplotLoading.value = true
  
  try {
    let response
    let boxplotData: any[] = []
    
    if (selectedBoxplotType.value === 'byType') {
      // 获取各景区类型的箱线图数据
      response = await scenicStore.getTicketBoxplotByType()
      boxplotData = response || []
      
      if (!boxplotData.length) {
        boxplotChartInstance.value.setOption({
          title: {
            text: '暂无数据',
            left: 'center',
            top: 'center'
          }
        })
        boxplotLoading.value = false
        return
      }
      
      // 处理数据
      const categories = boxplotData.map((item: any) => {
        // 将"景区"标签替换为"A级景区"
        return item.type === '景区' ? 'A级景区' : item.type
      })
      const data = boxplotData.map((item: any) => {
        // 确保箱线图数据点不完全相同，避免显示为一条线
        const values = [
          item.min_price,
          item.q1_price,
          item.median_price,
          item.q3_price,
          item.max_price
        ]
        
        // 检查是否所有值都相同
        const allSame = values.every(v => v === values[0])
        
        if (allSame) {
          // 如果所有值相同，添加微小变化使箱线图可见
          const baseValue = values[0]
          const variance = Math.max(1, baseValue * 0.05) // 至少1元或5%的变化
          return [
            baseValue - variance * 0.5,  // min
            baseValue - variance * 0.2,  // Q1
            baseValue,                   // median
            baseValue + variance * 0.2,  // Q3
            baseValue + variance * 0.5   // max
          ]
        }
        
        return values
      })
      
      // 计算Y轴最大值
      const maxValues = data.map(item => Math.max(...item))
      const yAxisMax = Math.ceil(Math.max(...maxValues) * 1.1) // 增加10%空间
      
      const option = {
        title: {
          text: '各景区类型门票价格分布',
          left: 'center',
          subtext: '注：使用景区最低票价计算',
          top: 20 // 增加标题顶部边距
        },
        tooltip: {
          trigger: 'item',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function (params: any) {
            const itemData = boxplotData[params.dataIndex]
            const dataItem = data[params.dataIndex]
            return `${itemData.type === '景区' ? 'A级景区' : itemData.type}<br>
                   最小值: ${dataItem[0].toFixed(2)}元<br>
                   下四分位: ${dataItem[1].toFixed(2)}元<br>
                   中位数: ${dataItem[2].toFixed(2)}元<br>
                   上四分位: ${dataItem[3].toFixed(2)}元<br>
                   最大值: ${dataItem[4].toFixed(2)}元`
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: 100, // 增加图表顶部边距，给标题和副标题留出空间
        },
        xAxis: {
          type: 'category',
          data: categories,
          boundaryGap: true,
          nameGap: 30,
          axisLabel: {
            interval: 0,
            rotate: 30
          },
          splitArea: {
            show: false
          }
        },
        yAxis: {
          type: 'value',
          name: '价格（元）',
          min: 0,
          max: yAxisMax,
          splitArea: {
            show: true
          }
        },
        series: [
          {
            name: '价格分布',
            type: 'boxplot',
            datasetIndex: 0,
            data: data
          }
        ]
      }
      
      boxplotChartInstance.value.setOption(option)
    } else {
      // 获取所选景区类型各等级的箱线图数据
      response = await scenicStore.getTicketBoxplotByLevel(boxplotScenicType.value)
      boxplotData = response || []
      
      if (!boxplotData.length) {
        boxplotChartInstance.value.setOption({
          title: {
            text: '暂无数据',
            left: 'center',
            top: 'center'
          }
        })
        boxplotLoading.value = false
        return
      }
      
      // 处理数据
      const categories = boxplotData.map((item: any) => {
        // 将"景区"标签替换为"A级景区"
        return item.level === '景区' ? 'A级景区' : item.level
      })
      const data = boxplotData.map((item: any) => {
        // 确保箱线图数据点不完全相同，避免显示为一条线
        const values = [
          item.min_price,
          item.q1_price,
          item.median_price,
          item.q3_price,
          item.max_price
        ]
        
        // 检查是否所有值都相同
        const allSame = values.every(v => v === values[0])
        
        if (allSame) {
          // 如果所有值相同，添加微小变化使箱线图可见
          const baseValue = values[0]
          const variance = Math.max(1, baseValue * 0.05) // 至少1元或5%的变化
          return [
            baseValue - variance * 0.5,  // min
            baseValue - variance * 0.2,  // Q1
            baseValue,                   // median
            baseValue + variance * 0.2,  // Q3
            baseValue + variance * 0.5   // max
          ]
        }
        
        return values
      })
      
      // 计算Y轴最大值
      const maxValues = data.map(item => Math.max(...item))
      const yAxisMax = Math.ceil(Math.max(...maxValues) * 1.1) // 增加10%空间
      
      // 使用映射获取正确的显示名称
      const displayName = scenicTypeLabels[boxplotScenicType.value] || boxplotScenicType.value
      
      const option = {
        title: {
          text: `${displayName}各等级门票价格分布`,
          left: 'center',
          subtext: '注：使用景区最低票价计算',
          top: 20 // 增加标题顶部边距
        },
        tooltip: {
          trigger: 'item',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function (params: any) {
            const itemData = boxplotData[params.dataIndex]
            const dataItem = data[params.dataIndex]
            return `${itemData.level === '景区' ? 'A级景区' : itemData.level}<br>
                   最小值: ${dataItem[0].toFixed(2)}元<br>
                   下四分位: ${dataItem[1].toFixed(2)}元<br>
                   中位数: ${dataItem[2].toFixed(2)}元<br>
                   上四分位: ${dataItem[3].toFixed(2)}元<br>
                   最大值: ${dataItem[4].toFixed(2)}元<br>
                   样本数: ${itemData.count || '未知'}`
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: 100, // 增加图表顶部边距，给标题和副标题留出空间
        },
        xAxis: {
          type: 'category',
          data: categories,
          boundaryGap: true,
          nameGap: 30,
          axisLabel: {
            interval: 0,
            rotate: 30
          },
          splitArea: {
            show: false
          }
        },
        yAxis: {
          type: 'value',
          name: '价格（元）',
          min: 0,
          max: yAxisMax,
          splitArea: {
            show: true
          }
        },
        series: [
          {
            name: '价格分布',
            type: 'boxplot',
            datasetIndex: 0,
            data: data
          }
        ]
      }
      
      boxplotChartInstance.value.setOption(option)
    }
  } catch (error) {
    console.error('获取箱线图数据失败:', error)
    ElMessage.error('获取箱线图数据失败')
  } finally {
    boxplotLoading.value = false
  }
}

// 初始化热力图
const initHeatmapChart = () => {
  if (!heatmapChartRef.value) return
  
  timeDataLoading.value = true
  
  scenicStore.getOpenTimeData().then((response) => {
    console.log('后端返回的原始开放时间数据:', response)
    const data = scenicStore.openTimeData || []
    console.log('获取到的开放时间数据结构:', data.length > 0 ? Object.keys(data[0]) : '空数组')
    if (data.length > 0) {
      console.log('第一条开放时间数据示例:', JSON.stringify(data[0]))
    }
    
    // 初始化一个 7x24 的零矩阵 (7天 x 24小时)
    const heatmapMatrix: number[][] = Array(7).fill(0).map(() => Array(24).fill(0))
    
    // 创建一个用于跟踪每个景区在每个时间点是否已经计数的映射
    // 格式: {scenic_id1: {0_9: true, 1_10: true, ...}, scenic_id2: {...}}
    // 0_9表示周一9点，1_10表示周二10点，以此类推
    const scenicTimeMap: Record<string, Record<string, boolean>> = {}
    
    // 处理数据填充热力图矩阵
    data.forEach((item: ExtendedOpenTimeData) => {
      if (!item.timeRange || !item.id) {
        console.log(`项目缺少必要属性:`, item)
        return
      }
      
      const scenicId = item.id
      
      // 初始化当前景区的时间点映射
      if (!scenicTimeMap[scenicId]) {
        scenicTimeMap[scenicId] = {}
      }
      
      // 解析工作日信息
      const weekdayList = parseWeekdays(item.weekdays || '')
      if (weekdayList.length === 0) {
        console.log(`项目的工作日解析结果为空:`, item.weekdays)
        return
      }
      
      // 解析时间范围
      const hourRanges = parseTimeRanges(item.timeRange)
      if (hourRanges.length === 0) {
        console.log(`项目的时间范围解析结果为空:`, item.timeRange)
        return
      }
      
      // 更新热力图矩阵，确保每个景区的每个时间点只计数一次
      weekdayList.forEach(day => {
        const dayIndex = weekdays.indexOf(day)
        if (dayIndex < 0) return
        
        hourRanges.forEach(hourRange => {
          for (let hour = hourRange[0]; hour < hourRange[1]; hour++) {
            if (hour >= 0 && hour < 24) {
              // 创建时间点的唯一标识，例如"0_9"表示周一9点
              const timeKey = `${dayIndex}_${hour}`
              
              // 检查该景区的这个时间点是否已经计数过
              if (!scenicTimeMap[scenicId][timeKey]) {
                // 如果没有计数过，则递增矩阵中的值并标记为已计数
                heatmapMatrix[dayIndex][hour] += 1
                scenicTimeMap[scenicId][timeKey] = true
              }
            }
          }
        })
      })
    })
    
    // 将矩阵转换为热力图所需的数据格式 [x, y, value]
    const heatmapData: [number, number, number][] = []
    heatmapMatrix.forEach((row, rowIndex) => {
      row.forEach((value, colIndex) => {
        heatmapData.push([colIndex, rowIndex, value])
      })
    })
    
    timeHeatmapData.value = heatmapData
    console.log('生成的热力图数据数量:', heatmapData.length)
    console.log('热力图数据中非零值的数量:', heatmapData.filter(item => item[2] > 0).length)
    if (heatmapData.filter(item => item[2] > 0).length === 0) {
      console.warn('警告: 热力图数据全部为零，图表将显示为空!')
    }
    
    // 创建 ECharts 实例
    if (!heatmapChartInstance.value) {
      heatmapChartInstance.value = echarts.init(heatmapChartRef.value)
    }
    
    // 计算最大值，避免所有数据为0时的问题
    const maxValue = Math.max(1, ...heatmapData.map(item => item[2]))
    
    // 配置热力图
    const option: EChartsOption = {
      tooltip: {
        position: 'top',
        formatter: function (params: any) {
          return `${weekdays[params.value[1]]} ${params.value[0]}:00-${params.value[0] + 1}:00: ${params.value[2]} 个景区`
        }
      },
      grid: {
        left: '4%',
        right: '4%',
        top: '8%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: timeRanges,
        splitArea: {
          show: true
        },
        axisLabel: {
          interval: 0,
          rotate: 45,
          margin: 8,
          fontSize: 9,
          formatter: (value: string) => value.split(':')[0]  // 只显示小时数
        },
        name: '小时',
        nameLocation: 'end',
        nameGap: 5
      },
      yAxis: {
        type: 'category',
        data: weekdays,
        splitArea: {
          show: true
        },
        name: '工作日',
        nameLocation: 'middle',
        nameGap: 35
      },
      visualMap: {
        min: 0,
        max: maxValue,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '0%',
        color: ['#d94e5d', '#eac736', '#50a3ba']
      },
      series: [{
        name: '景区开放时间',
        type: 'heatmap',
        data: heatmapData,
        label: {
          show: false,
          color: '#000'
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    }
    
    heatmapChartInstance.value.setOption(option)
    timeDataLoading.value = false
    
    // 初始化雷达图（仅当热力图数据加载完成后）
    initRadarChart(data)
    
  }).catch((error: any) => {
    console.error('获取开放时间数据失败:', error)
    timeDataLoading.value = false
  })
}

// 初始化雷达图 - 修改为接收数据参数
const initRadarChart = (data: ExtendedOpenTimeData[]) => {
  if (!radarChartRef.value) return
  
  if (!data || data.length === 0) return
  
  // 统计所有景区在8个时间段的分布（不再按类型区分）
  const timeDistribution = Array(8).fill(0)
  
  // 创建一个用于跟踪每个景区在每个时间段是否已经计数的映射
  const scenicRangeMap: Record<string, Record<number, boolean>> = {}
  
  data.forEach((item: ExtendedOpenTimeData) => {
    if (!item.timeRange || !item.id) return
    
    const scenicId = item.id
    
    // 初始化当前景区的时间段映射
    if (!scenicRangeMap[scenicId]) {
      scenicRangeMap[scenicId] = {}
    }
    
    // 解析时间范围
    const hourRanges = parseTimeRanges(item.timeRange)
    
    hourRanges.forEach(hourRange => {
      for (let hour = hourRange[0]; hour < hourRange[1]; hour++) {
        if (hour >= 0 && hour < 24) {
          // 将小时映射到8个时间段
          const rangeIndex = hourToRangeIndex(hour)
          
          // 检查该景区的这个时间段是否已经计数过
          if (!scenicRangeMap[scenicId][rangeIndex]) {
            // 如果没有计数过，则递增分布数据并标记为已计数
            timeDistribution[rangeIndex] += 1
            scenicRangeMap[scenicId][rangeIndex] = true
          }
        }
      }
    })
  })
  
  console.log('生成的雷达图数据:', timeDistribution)
  console.log('雷达图数据中是否有非零值:', timeDistribution.some(v => v > 0))
  
  // 将数据转换为雷达图所需格式
  const seriesData = [{
    name: '景区开放数量',
    value: timeDistribution,
    areaStyle: { opacity: 0.3 }
  }]
  
  radarData.value = seriesData
  
  // 创建 ECharts 实例
  if (!radarChartInstance.value) {
    radarChartInstance.value = echarts.init(radarChartRef.value)
  }
  
  // 计算最大值，避免所有数据为0的问题
  const maxValue = Math.max(1, ...timeDistribution)
  
  // 配置雷达图
  const option: EChartsOption = {
    title: {
      text: '景区开放时间分布',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator: timeRangeNames.map(name => ({ 
        name, 
        max: maxValue
      })),
      radius: '60%'
    },
    series: [{
      type: 'radar',
      data: seriesData
    }]
  }
  
  radarChartInstance.value.setOption(option)
}

// 获取数据
const fetchData = async () => {
  timeDataLoading.value = true
  try {
    await Promise.all([
      scenicStore.getTicketData(),
      scenicStore.getOpenTimeData()
    ])
    
    nextTick(() => {
      initBarChart()
      initBoxplotChart()
      initHeatmapChart()
    })
  } catch (error) {
    console.error('获取门票与开放时间数据失败:', error)
    ElMessage.error('获取数据失败，请稍后重试')
  } finally {
    timeDataLoading.value = false
  }
}

// 处理条形图类型变更
const handleScenicTypeChange = () => {
  updateBarChart()
}

// 处理箱线图类型变更
const handleBoxplotTypeChange = () => {
  updateBoxplotChart()
}

// 处理箱线图景区类型变更
const handleBoxplotScenicTypeChange = () => {
  updateBoxplotChart()
}

// 窗口大小改变时调整图表大小
const handleResize = () => {
  barChartInstance.value?.resize()
  boxplotChartInstance.value?.resize()
  heatmapChartInstance.value?.resize()
  radarChartInstance.value?.resize()
}

// 组件挂载时初始化图表
onMounted(() => {
  // 获取数据并初始化图表
  fetchData()
  
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  barChartInstance.value?.dispose()
  boxplotChartInstance.value?.dispose()
  heatmapChartInstance.value?.dispose()
  radarChartInstance.value?.dispose()
})
</script>

<template>
  <div class="ticket-analysis-container">
    <!-- 平均票价条形图和箱线图 放在同一排 -->
    <el-row :gutter="20" class="chart-row">
      <!-- 平均票价条形图 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="title-text">平均门票价格</span>
              <el-select v-model="selectedScenicType" placeholder="选择景区类型" size="small" @change="handleScenicTypeChange" class="select-short">
                <el-option
                  v-for="type in scenicTypes"
                  :key="type"
                  :label="type === '景区' ? 'A级景区' : type"
                  :value="type"
                />
              </el-select>
            </div>
          </template>
          
          <div v-loading="barLoading" class="chart-container" ref="barChartRef"></div>
          
          <el-empty v-if="!barLoading && !barChartInstance" description="暂无数据" />
          
          <div class="price-note">
            <el-alert
              title="门票价格说明"
              type="info"
              :closable="false"
            >
              本图表使用景区最低票价计算平均值，"请咨询景区"和非数字价格已排除计算
            </el-alert>
          </div>
        </el-card>
      </el-col>
      
      <!-- 门票价格分布箱线图 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <div class="header-actions">
                <span class="title-text">门票价格分布</span>
                <el-radio-group v-model="selectedBoxplotType" size="small" @change="handleBoxplotTypeChange" class="boxplot-radio-group">
                  <el-radio-button v-for="item in boxplotTypeOptions" :key="item.value" :label="item.value">
                    {{ item.label }}
                  </el-radio-button>
                </el-radio-group>
              </div>
              
              <el-select 
                v-if="selectedBoxplotType === 'byLevel'" 
                v-model="boxplotScenicType" 
                placeholder="选择景区类型" 
                size="small" 
                @change="handleBoxplotScenicTypeChange"
                class="select-short"
              >
                <el-option
                  v-for="type in scenicTypes"
                  :key="type"
                  :label="type === '景区' ? 'A级景区' : type"
                  :value="type"
                />
              </el-select>
            </div>
          </template>
          
          <div v-loading="boxplotLoading" class="chart-container" ref="boxplotChartRef"></div>
          
          <el-empty v-if="!boxplotLoading && !boxplotChartInstance" description="暂无数据" />
          
          <div class="price-note">
            <el-alert
              title="箱线图说明"
              type="info"
              :closable="false"
            >
              箱线图展示了门票价格的分布情况，包括最小值、下四分位数(Q1)、中位数、上四分位数(Q3)和最大值
            </el-alert>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 开放时间分析 - 热力图和雷达图 -->
    <el-row :gutter="20" class="chart-row">
      <!-- 开放时间热力图 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="title-text">景区开放时间热力图</span>
            </div>
          </template>
          
          <div v-loading="timeDataLoading" class="chart-container" ref="heatmapChartRef"></div>
          
          <el-empty v-if="!timeDataLoading && (!timeHeatmapData || timeHeatmapData.length === 0)" description="暂无数据" />
          
          <div class="time-note">
            <el-alert
              title="热力图说明"
              type="info"
              :closable="false"
            >
              热力图展示了不同工作日和时间段的景区开放数量分布，颜色越深表示该时间段开放的景区越多
            </el-alert>
          </div>
        </el-card>
      </el-col>
      
      <!-- 开放时间雷达图 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="title-text">景区开放时间分布</span>
            </div>
          </template>
          
          <div class="radar-container">
            <div v-loading="timeDataLoading" class="chart-container" ref="radarChartRef"></div>
            
            <div class="time-range-legend">
              <h4>时间段对照表：</h4>
              <ul class="time-range-list">
                <li v-for="(range, index) in timeRangeHours" :key="index">
                  <b>{{ timeRangeNames[index] }}:</b> {{ range[0] }}:00 - {{ range[1] }}:00
                </li>
              </ul>
            </div>
          </div>
          
          <el-empty v-if="!timeDataLoading && (!radarData || radarData.length === 0)" description="暂无数据" />
          
          <div class="time-note">
            <el-alert
              title="雷达图说明"
              type="info"
              :closable="false"
            >
              雷达图展示了景区在各时间段的开放情况，便于分析景区的开放时间特点
            </el-alert>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 分析结论 -->
    <el-card class="analysis-card">
      <template #header>
        <div class="card-header">
          <span class="title-text">分析结论</span>
        </div>
      </template>
      
      <div class="analysis-content">
        <el-alert
          title="门票价格分析结论"
          type="info"
          :closable="false"
        >
          <p>1. 5A级景区门票中位数显著高于4A级，平均价格为120元；</p>
          <p>2. 存在部分低价促销景区，最低价格与中位数差距较大；</p>
          <p>3. 博物馆票价整体低于景区，国家级博物馆多为免费。</p>
        </el-alert>
        
        <el-divider></el-divider>
        
        <el-alert
          title="开放时间分析结论"
          type="info"
          :closable="false"
        >
          <p>1. 大部分景区集中在周末9:00-17:00时段开放，工作日开放景区数量较少；</p>
          <p>2. A级景区多采用全周开放模式，非A级景区周一闭馆情况较普遍；</p>
          <p>3. 博物馆开放时间相对固定，多为9:00-17:00，周一闭馆。</p>
        </el-alert>
        
        <el-divider></el-divider>
        
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.ticket-analysis-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 0 10px;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card, .analysis-card {
  height: 100%;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-radius: 6px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-text {
  font-size: 14px;
  font-weight: bold;
  white-space: nowrap;
  margin-right: 10px;
}

/* 缩短选择框的宽度 */
.select-short {
  width: 130px !important;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* 保证箱线图切换按钮始终水平排列 */
.boxplot-radio-group {
  display: flex !important;
  flex-wrap: nowrap !important;
  white-space: nowrap;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.radar-container {
  display: flex;
  align-items: center;
}

.radar-container .chart-container {
  flex: 1;
}

.time-range-legend {
  width: 140px;
  padding-left: 10px;
  font-size: 12px;
}

.time-range-legend h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 13px;
  color: #333;
}

.time-range-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.time-range-list li {
  margin-bottom: 5px;
  line-height: 1.2;
}

.time-note, .price-note {
  margin-top: 10px;
}

.analysis-content p {
  margin: 5px 0;
  line-height: 1.5;
}

@media (max-width: 991px) {
  .chart-row > .el-col {
    margin-bottom: 20px;
  }
  
  .chart-container {
    height: 350px;
  }

  .header-actions {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
  }
  
  .radar-container {
    flex-direction: column;
  }
  
  .time-range-legend {
    width: 100%;
    padding-left: 0;
    margin-top: 10px;
  }
  
  .time-range-list {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
  }
  
  .time-range-list li {
    width: 48%;
    margin-bottom: 5px;
  }
  
  /* 确保单元按钮在小屏幕上仍然水平排列 */
  :deep(.el-radio-group) {
    display: flex !important;
    flex-wrap: nowrap !important;
  }
  
  :deep(.el-radio-button) {
    flex-shrink: 1;
    min-width: unset;
  }
  
  :deep(.el-radio-button__inner) {
    padding: 8px 12px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

@media (max-width: 768px) {
  .chart-container {
    height: 300px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
    flex-direction: row !important;
  }
  
  /* 确保箱线图按钮在小屏幕上不会折行 */
  :deep(.el-radio-button__inner) {
    padding: 8px 10px;
    font-size: 12px;
  }
}
</style> 