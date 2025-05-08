<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// 定义登录响应类型
interface LoginResponse {
  data: {
    is_admin: boolean;
    [key: string]: any;
  }
}

const router = useRouter()
const userStore = useUserStore()

const loginForm = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const loginFormRef = ref<FormInstance>()

const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入管理员账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
})

const handleLogin = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  
  await formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {        
        // API调用登录逻辑
        const response = await userStore.login(loginForm.username, loginForm.password) as LoginResponse
        if (response.data.is_admin) {
          router.push('/admin-dashboard')
        } else {
          ElMessage.error('非管理员账号，无法登录')
          await userStore.logout()
        }
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '登录失败，请检查账号和密码')
      } finally {
        loading.value = false
      }
    }
  })
}

const goToUserLogin = () => {
  router.push('/')
}
</script>

<template>
  <div class="auth-container">
    <!-- 左侧学校信息区域 -->
    <div class="school-info">
      <div class="school-header">
        <div class="school-logo">
          <img src="/logo-zijin.png" alt="南京理工大学紫金学院" class="logo-image">
        </div>
        <div class="school-name">
          <h1>南京理工大学紫金学院</h1>
          <h2>NANJING UNIVERSITY OF SCIENCE AND TECHNOLOGY ZIJIN COLLEGE</h2>
        </div>
      </div>
      <div class="department-info">
        <p>计算机与人工智能学院</p>
        <p>2025届本科毕业设计</p>
      </div>
    </div>
    
    <!-- 右侧管理员登录区域 -->
    <div class="admin-login-container">
      <div class="login-box">
        <div class="logo-container">
          <img src="/logo.png" alt="景区数据可视化平台" class="logo-image" />
          <h2 class="system-title">全国景区数据分析及可视化系统 - 管理后台</h2>
        </div>
        
        <h3 class="login-title">管理员登录</h3>
        
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="rules"
          label-position="top"
          class="login-form"
        >
          <el-form-item label="管理员账号" prop="username">
            <el-input 
              v-model="loginForm.username"
              placeholder="请输入管理员账号"
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <el-button 
            type="primary" 
            :loading="loading" 
            class="login-button" 
            @click="handleLogin(loginFormRef)"
          >
            登录
          </el-button>
          
          <div class="form-footer">
            <el-button @click="goToUserLogin" type="text" class="user-login-link">
              用户登录
            </el-button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
  background: linear-gradient(135deg, #4a0060 0%, #1a0d3b 100%);
}

/* 左侧学校信息区域样式 */
.school-info {
  flex: 1;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  text-align: center;
  max-width: 42%;
  margin-left: 5%;
}

.school-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.school-logo {
  margin-right: 20px;
}

.school-logo img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-top: 20px;
}

.school-name {
  text-align: left;
}

.school-name h1 {
  font-size: 65px;
  margin-bottom: 10px;
  font-weight: 500;
  font-family: "华文行楷", "STXingkai", serif;
  width: 100%;
}

.school-name h2 {
  font-size: 16px;
  font-weight: 400;
  margin-bottom: 20px;
  letter-spacing: 1px;
  font-family: "Noto Serif SC", serif;
  font-weight: 900;
}

.department-info {
  font-size: 18px;
  line-height: 1.6;
}

/* 右侧管理员登录区域样式 */
.admin-login-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  max-width: 58%;
}

.admin-login-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 40%);
  z-index: 1;
}

.login-box {
  width: 400px;
  padding: 40px;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 2;
  transition: all 0.3s ease;
}

.login-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.logo-container .logo-image {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 10px;
}

.system-title {
  font-size: 20px;
  color: #333;
  text-align: center;
  margin: 0;
}

.login-title {
  font-size: 24px;
  color: #333;
  text-align: center;
  margin-bottom: 30px;
}

.login-form {
  width: 100%;
}

.login-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  margin-bottom: 20px;
  background-color: #001529;
  border-color: #001529;
}

.login-button:hover {
  background-color: #003a70;
  border-color: #003a70;
}

.form-footer {
  text-align: center;
}

.user-login-link {
  font-weight: bold;
  color: #001529;
}

/* 响应式调整 */
@media (max-width: 1024px) {
  .auth-container {
    flex-direction: column;
  }
  
  .school-info,
  .admin-login-container {
    flex: none;
    width: 100%;
    max-width: 100%;
    margin-left: 0;
  }
  
  .school-info {
    padding: 20px 0;
  }
  
  .school-header {
    justify-content: center;
  }
  
  .school-logo img {
    width: 80px;
    height: 80px;
  }
  
  .school-name h1 {
    font-size: 32px;
  }
  
  .school-name h2 {
    font-size: 14px;
  }
  
  .department-info {
    font-size: 16px;
  }
}
</style> 