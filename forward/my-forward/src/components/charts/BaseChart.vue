<template>
  <div ref="chartRef" :style="{ width: '100%', height: height }" />
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
// 导入完整的ECharts库，而不是按需导入
import * as echarts from 'echarts'
// 导入词云图扩展
import 'echarts-wordcloud'

export default defineComponent({
  name: 'BaseChart',
  props: {
    options: {
      type: Object,
      required: true
    },
    height: {
      type: String,
      default: '300px'
    }
  },
  emits: ['rendered'],
  setup(props, { emit }) {
    const chartRef = ref<HTMLElement | null>(null)
    let chart: echarts.ECharts | null = null
    
    const initChart = () => {
      if (!chartRef.value) return
      
      // 创建或重用图表实例
      if (!chart) {
        chart = echarts.init(chartRef.value)
        console.log('ECharts实例创建成功')
      }
      
      try {
        console.log('正在设置图表配置项:', props.options)
        // 设置图表配置项
        chart.setOption(props.options, true)
        console.log('图表渲染完成')
        
        // 发出渲染完成事件
        emit('rendered')
      } catch (error) {
        console.error('图表渲染出错:', error)
      }
    }
    
    // 监听配置项变化
    watch(() => props.options, () => {
      console.log('配置项变化，重新渲染图表')
      nextTick(() => {
        initChart()
      })
    }, { deep: true })
    
    // 监听窗口大小变化
    const handleResize = () => {
      if (chart) {
        chart.resize()
      }
    }
    
    onMounted(() => {
      // 初始化图表
      console.log('BaseChart组件挂载完成，准备初始化图表')
      nextTick(() => {
        initChart()
      })
      
      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
    })
    
    onUnmounted(() => {
      // 销毁图表实例
      if (chart) {
        chart.dispose()
        chart = null
      }
      
      // 移除事件监听
      window.removeEventListener('resize', handleResize)
    })
    
    return {
      chartRef
    }
  }
})
</script>

<style scoped>
.chart-container {
  position: relative;
}
</style> 