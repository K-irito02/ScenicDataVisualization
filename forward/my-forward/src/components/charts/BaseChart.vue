<template>
  <div ref="chartContainer" :style="{ width: width, height: height }" class="chart-container"></div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted, watch } from 'vue'
import type { PropType } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

export default defineComponent({
  name: 'BaseChart',
  props: {
    options: {
      type: Object as PropType<EChartsOption>,
      required: true
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '400px'
    },
    theme: {
      type: String,
      default: ''
    }
  },
  emits: ['chartClick', 'chartInit'],
  setup(props, { emit }) {
    const chartContainer = ref<HTMLElement | null>(null)
    let chartInstance: echarts.ECharts | null = null

    const initChart = () => {
      if (!chartContainer.value) return
      
      // 销毁之前的实例
      if (chartInstance) {
        chartInstance.dispose()
      }
      
      // 初始化图表
      chartInstance = props.theme
        ? echarts.init(chartContainer.value, props.theme)
        : echarts.init(chartContainer.value)
        
      // 设置配置项
      chartInstance.setOption(props.options)
      
      // 绑定点击事件
      chartInstance.on('click', (params) => {
        emit('chartClick', params)
      })
      
      // 发送初始化完成事件
      emit('chartInit', chartInstance)
      
      // 监听窗口大小变化，自动调整图表大小
      window.addEventListener('resize', handleResize)
    }
    
    const handleResize = () => {
      if (chartInstance) {
        chartInstance.resize()
      }
    }
    
    // 组件挂载后初始化图表
    onMounted(() => {
      initChart()
    })
    
    // 组件卸载前清理资源
    onUnmounted(() => {
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
      window.removeEventListener('resize', handleResize)
    })
    
    // 监听配置项变化，更新图表
    watch(
      () => props.options,
      (newOptions) => {
        if (chartInstance) {
          chartInstance.setOption(newOptions, { notMerge: true })
        }
      },
      { deep: true }
    )
    
    return {
      chartContainer
    }
  }
})
</script>

<style scoped>
.chart-container {
  position: relative;
}
</style> 