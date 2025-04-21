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
  <div class="admin-login-container">
    <div class="login-box">
      <div class="logo-container">
        <img src="/logo.png" alt="景区数据可视化平台" class="logo-image" />
        <h2 class="system-title">全国景区的数据分析及可视化系统 - 管理后台</h2>
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
</template>

<style scoped>
.admin-login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #001529 0%, #003a70 100%);
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

.logo-image {
  width: 100px;
  height: 100px;
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
  font-size: 14px;
}
</style> 