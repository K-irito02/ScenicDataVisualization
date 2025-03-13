<template>
  <div class="login-container">
    <div class="login-box">
      <div class="title">
        <h1>全国景区数据可视化系统</h1>
        <h3>{{ isAdminLogin ? '管理员登录' : '用户登录' }}</h3>
      </div>
      
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码">
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" class="login-btn" @click="handleLogin" :loading="loading">登录</el-button>
        </el-form-item>
      </el-form>
      
      <div class="actions">
        <span class="switch-login-type" @click="switchLoginType">
          {{ isAdminLogin ? '普通用户登录' : '管理员登录' }}
        </span>
        <span v-if="!isAdminLogin" class="register" @click="$router.push('/register')">注册账号</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login, adminLogin } from '@/api/user'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref<FormInstance>()
const loading = ref(false)
const isAdminLogin = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const { username, password } = loginForm
        let res
        
        if (isAdminLogin.value) {
          res = await adminLogin(username, password)
        } else {
          res = await login(username, password)
        }
        
        if (res && res.data && res.data.token) {
          userStore.login(res.data.token, username, isAdminLogin.value)
          ElMessage.success('登录成功')
          
          if (isAdminLogin.value) {
            router.push('/admin')
          } else {
            router.push('/dashboard')
          }
        } else {
          ElMessage.error('登录失败：无效的响应数据')
        }
      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error('登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
  })
}

const switchLoginType = () => {
  isAdminLogin.value = !isAdminLogin.value
  loginForm.username = ''
  loginForm.password = ''
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #1976d2, #64b5f6);
}

.login-box {
  width: 400px;
  padding: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.title {
  text-align: center;
  margin-bottom: 30px;
}

.title h1 {
  color: #333;
  font-size: 24px;
  margin-bottom: 10px;
}

.title h3 {
  color: #666;
  font-size: 16px;
}

.login-btn {
  width: 100%;
}

.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.switch-login-type, .register {
  color: #1976d2;
  cursor: pointer;
}

.switch-login-type:hover, .register:hover {
  text-decoration: underline;
}
</style> 