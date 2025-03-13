<template>
  <div class="not-found-container">
    <div class="content">
      <div class="error-code">404</div>
      <h1>页面未找到</h1>
      <p>抱歉，您访问的页面不存在或已被移除</p>
      <div class="actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上一页</el-button>
      </div>
    </div>
    <div class="illustration">
      <img src="/404.svg" alt="页面未找到" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// 返回首页
const goHome = () => {
  router.push('/')
}

// 返回上一页
const goBack = () => {
  router.back()
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background-color: #f5f7fa;
}

.content {
  max-width: 500px;
  text-align: center;
  padding: 40px;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #409eff;
  line-height: 1;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 20px;
}

p {
  font-size: 16px;
  color: #606266;
  margin-bottom: 30px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.illustration {
  max-width: 400px;
}

.illustration img {
  width: 100%;
  height: auto;
}

@media (max-width: 768px) {
  .not-found-container {
    flex-direction: column;
  }
  
  .content {
    padding: 20px;
  }
  
  .error-code {
    font-size: 80px;
  }
  
  .illustration {
    max-width: 250px;
    margin-top: 20px;
  }
}
</style> 