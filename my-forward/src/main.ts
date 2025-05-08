import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import axios from 'axios'
import type { RouteLocationNormalized } from 'vue-router'
// 移除懒加载插件，使用浏览器原生懒加载和Element Plus的loading指令

// 创建标题更新函数
const updateWindowTitle = (title: string) => {
  document.title = title || '景区数据分析与可视化系统';
};

// 将favicon的标题与当前路由同步
router.afterEach((to: RouteLocationNormalized) => {
  const pageTitle = to.meta.title as string || '景区数据分析与可视化系统';
  updateWindowTitle(pageTitle);
});

// 配置 axios
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || '/'
axios.defaults.timeout = 10000

// 创建Vue应用实例
const app = createApp(App)

// 全局错误处理，将前端错误记录到后端
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue应用错误:', err)
  console.error('错误组件:', instance)
  console.error('错误信息:', info)
  
  // 将错误上报到后端
  try {
    // 获取错误的堆栈跟踪
    const stackTrace = err instanceof Error ? err.stack || '' : ''
    
    // 获取错误的详细信息
    const errorDetails = {
      message: err instanceof Error ? err.message : String(err),
      stack: stackTrace,
      componentInfo: instance ? {
        componentName: instance.$options?.name || '未命名组件',
        props: instance.$props || {}
      } : null,
      vueInfo: info,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString()
    }
    
    // 发送错误信息到后端API
    fetch('/api/admin/frontend-error-log/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Anonymous-Error-Log': '1'
      },
      body: JSON.stringify({
        level: 'ERROR',
        message: errorDetails.message,
        traceback: JSON.stringify(errorDetails, null, 2),
        location: window.location.href
      }),
      // 不需要凭证，允许匿名错误报告
      credentials: 'same-origin'
    }).catch(e => {
      // 如果错误上报失败，只记录在控制台
      console.error('无法上报错误:', e)
    })
  } catch (reportError) {
    console.error('错误上报失败:', reportError)
  }
}

// 捕获未处理的Promise拒绝
window.addEventListener('unhandledrejection', (event) => {
  console.error('未处理的Promise拒绝:', event.reason)
  
  // 将Promise错误上报到后端
  try {
    const errorDetails = {
      message: event.reason instanceof Error ? 
        event.reason.message : 
        String(event.reason),
      stack: event.reason instanceof Error ? 
        event.reason.stack || '' : 
        '未提供堆栈信息',
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString()
    }
    
    // 发送错误信息到后端API
    fetch('/api/admin/frontend-error-log/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Anonymous-Error-Log': '1'
      },
      body: JSON.stringify({
        level: 'ERROR',
        message: `未处理的Promise拒绝: ${errorDetails.message}`,
        traceback: JSON.stringify(errorDetails, null, 2),
        location: window.location.href
      }),
      credentials: 'same-origin'
    }).catch(e => {
      console.error('无法上报Promise错误:', e)
    })
  } catch (reportError) {
    console.error('Promise错误上报失败:', reportError)
  }
})

// 捕获全局错误
window.addEventListener('error', (event) => {
  // 忽略网络资源加载错误
  if (event.error === null && event.message.includes('Script error.')) {
    return
  }
  
  console.error('全局错误:', event.error || event.message)
  
  // 将全局错误上报到后端
  try {
    const errorDetails = {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      stack: event.error?.stack || '未提供堆栈信息',
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString()
    }
    
    // 发送错误信息到后端API
    fetch('/api/admin/frontend-error-log/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Anonymous-Error-Log': '1'
      },
      body: JSON.stringify({
        level: 'ERROR',
        message: `全局错误: ${errorDetails.message}`,
        traceback: JSON.stringify(errorDetails, null, 2),
        location: `${errorDetails.filename}:${errorDetails.lineno}:${errorDetails.colno}`
      }),
      credentials: 'same-origin'
    }).catch(e => {
      console.error('无法上报全局错误:', e)
    })
  } catch (reportError) {
    console.error('全局错误上报失败:', reportError)
  }
})

// 导入完整的ECharts
import * as echarts from 'echarts'
// 确保词云图扩展被加载
import 'echarts-wordcloud'

// 不再使用 vue-echarts 组件，改为直接全局注册ECharts实例

// 注册ElementPlus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 添加到全局属性中，方便在组件中使用
app.config.globalProperties.$echarts = echarts

// 移除全局懒加载配置，使用更现代的方法

app.use(createPinia())
app.use(router)
app.use(ElementPlus as any, {
  locale: zhCn,
})

app.mount('#app')
