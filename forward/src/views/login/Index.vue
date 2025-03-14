<template>
  <div class="login-container">
    <div class="login-box">
      <h2 class="title">全国景区数据可视化系统</h2>
      
      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="login-form">
        <el-form-item prop="account">
          <el-input 
            v-model="loginForm.account" 
            placeholder="请输入用户名/邮箱"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            class="login-button" 
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
        
        <div class="options">
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
          <div>
            <router-link to="/forgot-password" class="forgot-link">忘记密码？</router-link>
            <router-link to="/register" class="register-link" style="margin-left: 15px;">用户注册</router-link>
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/store/user'
import { login } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const rememberMe = ref(false)
const loginFormRef = ref<FormInstance>()

// 登录表单数据
const loginForm = reactive({
  account: '',  // 可以是用户名或邮箱
  password: ''
})

// 表单验证规则
const loginRules = reactive<FormRules>({
  account: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ]
})

// 登录处理函数
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        const res = await login(loginForm.account, loginForm.password)
        
        // 登录成功，保存token和用户信息
        userStore.login(res.data.token, res.data.username, res.data.isAdmin)
        
        ElMessage.success('登录成功')
        
        // 如果是管理员，重定向到管理后台，否则进入普通用户仪表盘
        const nextRoute = res.data.isAdmin ? '/admin' : '/dashboard'
        router.push(nextRoute)
        
      } catch (error: any) {
        console.error('登录失败:', error)
        ElMessage.error(error.message || '登录失败，请检查账号和密码')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  width: 100%;
  background-color: #409EFF;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-box {
  width: 400px;
  padding: 30px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 22px;
}

.login-form {
  margin-top: 20px;
}

.login-button {
  width: 100%;
}

.options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.forgot-link {
  color: #909399;
  text-decoration: none;
}

.forgot-link:hover {
  color: #409EFF;
  text-decoration: underline;
}

.register-link {
  color: #409EFF;
  text-decoration: none;
}

.register-link:hover {
  text-decoration: underline;
}
</style> 