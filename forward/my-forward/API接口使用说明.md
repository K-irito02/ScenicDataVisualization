# 景区数据可视化系统 API 接口使用说明

本项目已对后端API进行了完整封装，前端开发者可以直接通过以下方式使用API服务。

## 目录

1. [项目配置](#项目配置)
2. [API服务层](#API服务层)
3. [状态管理](#状态管理)
4. [使用示例](#使用示例)

## 项目配置

项目已配置好API服务，主要配置如下：

1. API基础URL在`.env`文件中配置：
   ```
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

2. 在`vite.config.ts`中配置了开发时的代理：
   ```typescript
   server: {
     port: 3000,
     open: true,
     proxy: {
       '/api': {
         target: 'http://localhost:8000',
         changeOrigin: true
       }
     }
   }
   ```

3. 在`main.ts`中配置了axios默认设置：
   ```typescript
   axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || '/'
   axios.defaults.timeout = 10000
   ```

## API服务层

所有API服务被封装在`src/api`目录下，包括：

1. **axios.ts**: 封装了axios实例，包含请求和响应拦截器
2. **user.ts**: 封装了用户相关API
3. **scenic.ts**: 封装了景区数据相关API
4. **admin.ts**: 封装了管理员相关API
5. **index.ts**: 统一导出所有API服务

## 状态管理

项目使用Pinia进行状态管理，所有store位于`src/stores`目录：

1. **user.ts**: 用户相关状态和操作
2. **scenic.ts**: 景区数据相关状态和操作
3. **admin.ts**: 管理员相关状态和操作

## 使用示例

### 1. 用户登录

```typescript
<script setup>
import { useUserStore } from '../stores'
import { ref } from 'vue'

const userStore = useUserStore()
const username = ref('')
const password = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    await userStore.login(username.value, password.value)
    // 登录成功，可以进行页面跳转
  } catch (error) {
    // 处理登录失败
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>
```

### 2. 获取省份景区分布数据

```typescript
<script setup>
import { useScenicStore } from '../stores'
import { onMounted, ref } from 'vue'

const scenicStore = useScenicStore()
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    await scenicStore.getProvinceData()
    // 数据已加载到 scenicStore.provinceData
  } catch (error) {
    console.error('获取省份数据失败:', error)
  } finally {
    loading.value = false
  }
})
</script>
```

### 3. 管理员获取所有用户

```typescript
<script setup>
import { useAdminStore, useUserStore } from '../stores'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const adminStore = useAdminStore()
const userStore = useUserStore()
const router = useRouter()
const loading = ref(false)

onMounted(async () => {
  // 检查是否为管理员
  if (!userStore.isAdmin) {
    router.push('/login')
    return
  }
  
  loading.value = true
  try {
    await adminStore.getAllUsers()
    // 用户数据已加载到 adminStore.users
  } catch (error) {
    console.error('获取用户数据失败:', error)
  } finally {
    loading.value = false
  }
})
</script>
```

## API接口列表

所有API请参考后端接口文档。以下是主要API及其在前端的使用方式：

### 用户API

- **login(username, password)**: 用户登录
- **register(username, email, password)**: 用户注册
- **updateProfile(profileData)**: 更新用户资料
- **toggleFavorite(scenicId)**: 添加/取消收藏
- **getFavorites()**: 获取用户收藏列表

### 景区数据API

- **getProvinceDistribution()**: 获取省份景区分布
- **getScenicLevels()**: 获取景区等级与分类
- **getTicketPrices()**: 获取门票价格数据
- **getOpenTimes()**: 获取开放时间数据
- **getCommentAnalysis()**: 获取评论情感分析
- **getWordCloud(scenicId)**: 获取词云数据
- **getTransportation()**: 获取交通方式数据
- **searchScenic(keyword, filters)**: 搜索景区
- **getFilterOptions()**: 获取筛选选项
- **getScenicDetail(scenicId)**: 获取景区详情

### 管理员API

- **getUsers()**: 获取所有用户信息
- **getUserRecords()**: 获取用户操作记录