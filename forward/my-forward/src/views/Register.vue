<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  code: ''
})

const loading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
const registerFormRef = ref<FormInstance>()

// 表单验证规则
const validatePass = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else {
    if (registerForm.confirmPassword !== '') {
      if (registerFormRef.value) {
        registerFormRef.value.validateField('confirmPassword')
      }
    }
    callback()
  }
}

const validatePass2 = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码长度为6位', trigger: 'blur' }
  ]
})

// 发送验证码
const sendCode = async () => {
  try {
    await registerFormRef.value?.validateField('email')
    sendingCode.value = true
    
    try {
      await axios.post('/api/email/send-code/', { email: registerForm.email })
      ElMessage.success('验证码已发送，请查收邮件')
      
      // 开始倒计时
      countdown.value = 60
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
          sendingCode.value = false
        }
      }, 1000)
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || '发送验证码失败，请稍后重试')
      sendingCode.value = false
    }
  } catch (error) {
    // 邮箱验证失败
  }
}

// 注册
const handleRegister = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  
  await formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.register(
          registerForm.username,
          registerForm.email,
          registerForm.password,
          registerForm.code
        )
        ElMessage.success('注册成功，请登录')
        router.push('/')
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '注册失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
  })
}

// 返回登录页
const goToLogin = () => {
  router.push('/')
}
</script>

<template>
  <div class="register-container">
    <div class="register-box">
      <div class="logo-container">
        <img src="/logo.png" alt="Logo" class="logo">
        <h2 class="system-title">全国景区的数据分析及可视化系统</h2>
      </div>
      
      <h3 class="register-title">用户注册</h3>
      
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        label-position="top"
        class="register-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="registerForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="验证码" prop="code">
          <div class="code-input-group">
            <el-input 
              v-model="registerForm.code"
              placeholder="请输入验证码"
              prefix-icon="Key"
            />
            <el-button 
              type="primary" 
              :disabled="sendingCode || countdown > 0" 
              @click="sendCode"
            >
              {{ countdown > 0 ? `${countdown}秒后重新发送` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>
        
        <el-button 
          type="primary" 
          :loading="loading" 
          class="register-button" 
          @click="handleRegister(registerFormRef)"
        >
          注册
        </el-button>
        
        <div class="form-footer">
          <span>已有账号？</span>
          <el-button @click="goToLogin" type="text" class="login-link">
            立即登录
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
  padding: 20px 0;
}

.register-box {
  width: 450px;
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

.register-title {
  font-size: 24px;
  color: #333;
  text-align: center;
  margin-bottom: 30px;
}

.register-form {
  width: 100%;
}

.register-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  margin-bottom: 20px;
}

.form-footer {
  text-align: center;
  color: #606266;
}

.login-link {
  margin-left: 5px;
  font-weight: bold;
}

.code-input-group {
  display: flex;
  gap: 10px;
}

.code-input-group .el-input {
  flex: 1;
}

.code-input-group .el-button {
  width: 140px;
}
</style> 