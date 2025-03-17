import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './style.css'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import axios from 'axios'

// 配置 axios
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || '/'
axios.defaults.timeout = 10000

const app = createApp(App)

app.use(ElementPlus as any)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)

app.mount('#app')
