<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

interface LoginResponse {
  token?: string
  user_id?: string
  username?: string
  is_admin?: boolean
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
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' }
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
        // 开发环境下的模拟登录（临时方案）
        if (loginForm.username === 'user' && loginForm.password === 'user123') {
          // 模拟普通用户登录
          const mockResponse = {
            data: {
              token: 'mock-user-token-' + new Date().getTime(), // 添加时间戳避免使用旧token
              user_id: 'user-001',
              username: 'user',
              email: 'user@example.com',
              avatar: '',
              location: '北京',
              is_admin: false
            }
          }
          
          // 直接设置localStorage，避免依赖Store
          localStorage.setItem('token', mockResponse.data.token)
          localStorage.setItem('userId', mockResponse.data.user_id)
          localStorage.setItem('username', mockResponse.data.username)
          localStorage.setItem('email', mockResponse.data.email)
          localStorage.setItem('avatar', mockResponse.data.avatar || '')
          localStorage.setItem('location', mockResponse.data.location || '')
          localStorage.setItem('isAdmin', mockResponse.data.is_admin.toString())
          localStorage.setItem('favorites', JSON.stringify([]))
          
          // 同时也更新Store
          await userStore.setUserInfo({
            token: mockResponse.data.token,
            userId: mockResponse.data.user_id,
            username: mockResponse.data.username,
            email: mockResponse.data.email,
            avatar: mockResponse.data.avatar,
            location: mockResponse.data.location,
            isAdmin: mockResponse.data.is_admin,
            favorites: []
          })
          
          ElMessage.success('登录成功，正在跳转...')
          
          // 确保状态已更新
          console.log('登录成功，localStorage状态:', {
            token: localStorage.getItem('token') ? '已设置' : '未设置',
            userId: localStorage.getItem('userId'),
            username: localStorage.getItem('username')
          })
          console.log('登录成功，Store状态:', userStore.getUserInfo())
          
          // 使用延时确保状态更新
          setTimeout(() => {
            console.log('准备跳转到dashboard页面...')
            router.push('/dashboard')
          }, 500)
          return
        }
        
        // 原有的API调用登录逻辑
        console.log('开始调用登录API...')
        const loginResult = await userStore.login(loginForm.username, loginForm.password)
        console.log('登录API调用成功:', loginResult)
        
        // 确保token直接保存到localStorage
        const responseData = loginResult as LoginResponse
        if (responseData.token) {
          console.log('API返回了token，确保保存到localStorage')
          localStorage.setItem('token', responseData.token)
          localStorage.setItem('userId', responseData.user_id || '')
          localStorage.setItem('username', responseData.username || '')
          localStorage.setItem('isAdmin', (responseData.is_admin || false).toString())
        } else {
          console.error('API返回中没有找到token:', loginResult)
        }
        
        // 检查登录状态
        const userInfo = userStore.getUserInfo()
        console.log('登录后用户状态:', {
          isLoggedIn: !!userInfo.token,
          token: userInfo.token ? `${userInfo.token.substring(0, 10)}...` : 'null',
          username: userInfo.username
        })
        
        // 检查localStorage
        console.log('localStorage状态:', {
          token: localStorage.getItem('token') ? '已设置' : '未设置',
          userId: localStorage.getItem('userId'),
          username: localStorage.getItem('username')
        })
        
        // 使用延时确保状态已完全更新
        setTimeout(() => {
          console.log('准备跳转到dashboard页面...')
          router.push('/dashboard')
        }, 500)
      } catch (error: any) {
        console.error('登录失败:', error)
        ElMessage.error(error.response?.data?.message || '登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
  })
}

const goToRegister = () => {
  router.push('/register')
}

const goToForgotPassword = () => {
  // 暂时未实现忘记密码功能
  ElMessage.info('忘记密码功能暂未实现，请联系管理员')
}

const goToAdminLogin = () => {
  router.push('/admin')
}
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo-container">
        <el-icon size="60"><Picture /></el-icon>
        <h2 class="system-title">全国景区的数据分析及可视化系统</h2>
      </div>
      
      <h3 class="login-title">用户登录</h3>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        label-position="top"
        class="login-form"
      >
        <el-form-item label="用户名/邮箱" prop="username">
          <el-input 
            v-model="loginForm.username"
            placeholder="请输入用户名或邮箱"
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
        
        <div class="form-actions">
          <el-button @click="goToForgotPassword" type="text" class="forgot-password">
            忘记密码？
          </el-button>
        </div>
        
        <el-button 
          type="primary" 
          :loading="loading" 
          class="login-button" 
          @click="handleLogin(loginFormRef)"
        >
          登录
        </el-button>
        
        <div class="form-footer">
          <span>没有账号？</span>
          <el-button @click="goToRegister" type="text" class="register-link">
            立即注册
          </el-button>
        </div>
        
        <div class="admin-login-link">
          <el-button @click="goToAdminLogin" type="text">
            管理员登录
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.logo {
  height: 60px;
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.forgot-password {
  font-size: 14px;
}

.login-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  margin-bottom: 20px;
}

.form-footer {
  text-align: center;
  margin-bottom: 20px;
  color: #606266;
}

.register-link {
  margin-left: 5px;
  font-weight: bold;
}

.admin-login-link {
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
}
</style> 