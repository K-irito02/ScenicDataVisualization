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
import { errorLogger } from './api'
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

// 全局错误处理
window.addEventListener('error', (event) => {
  const errorMessage = event.message || '未知错误'
  errorLogger.error('全局捕获的错误', {
    message: errorMessage,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno
  })
})

// 捕获未处理的Promise错误
window.addEventListener('unhandledrejection', (event) => {
  const errorMessage = event.reason?.message || '未处理的Promise错误'
  errorLogger.error('未处理的Promise错误', {
    message: errorMessage,
    reason: event.reason
  })
})

// 导入完整的ECharts
import * as echarts from 'echarts'
// 确保词云图扩展被加载
import 'echarts-wordcloud'

const app = createApp(App)

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
