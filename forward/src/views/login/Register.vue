<template>
  <div class="register-container">
    <div class="register-box">
      <h2 class="title">全国景区数据可视化系统</h2>
      <h3 class="subtitle">用户注册</h3>
      
      <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" class="register-form">
        <el-form-item prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="请输入用户名"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="email">
          <el-input 
            v-model="registerForm.email" 
            placeholder="请输入邮箱"
            prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="请确认密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item prop="verifyCode" class="verify-code-item">
          <el-input 
            v-model="registerForm.verifyCode" 
            placeholder="请输入验证码"
            prefix-icon="Key"
            maxlength="4"
          />
          <el-button 
            :disabled="cooldown > 0" 
            @click="getCode" 
            class="get-code-btn"
          >
            {{ cooldown > 0 ? `${cooldown}秒后重新获取` : '获取验证码' }}
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            class="register-button" 
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>
        
        <div class="options">
          <span>已有账号？</span>
          <router-link to="/login" class="login-link">返回登录</router-link>
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
import { register, getVerifyCode } from '@/api/user'

const router = useRouter()
const loading = ref(false)
const cooldown = ref(0)
const registerFormRef = ref<FormInstance>()

// 注册表单数据
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  verifyCode: ''
})

// 表单验证规则
const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  verifyCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码为4位数字', trigger: 'blur' }
  ]
})

// 获取验证码
const getCode = async () => {
  // 首先验证邮箱
  registerFormRef.value?.validateField('email', async (valid) => {
    if (!valid) {
      try {
        const res = await getVerifyCode(registerForm.email)
        ElMessage.success('验证码已发送')
        
        // 开始倒计时
        cooldown.value = 60
        const timer = setInterval(() => {
          cooldown.value--
          if (cooldown.value <= 0) {
            clearInterval(timer)
          }
        }, 1000)
        
        // 如果在开发环境下，自动填充验证码（便于测试）
        if (import.meta.env.MODE === 'development' && res.data?.verifyCode) {
          registerForm.verifyCode = res.data.verifyCode
        }
      } catch (error: any) {
        console.error('获取验证码失败:', error)
        ElMessage.error('获取验证码失败')
      }
    }
  })
}

// 注册处理函数
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        const res = await register(
          registerForm.username,
          registerForm.password,
          registerForm.email,
          registerForm.verifyCode
        )
        
        ElMessage.success(res.data?.message || '注册成功')
        router.push('/login')
      } catch (error: any) {
        console.error('注册失败:', error)
        ElMessage.error(error.message || '注册失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.register-container {
  height: 100vh;
  width: 100%;
  background-color: #409EFF;
  display: flex;
  justify-content: center;
  align-items: center;
}

.register-box {
  width: 400px;
  padding: 30px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.title {
  text-align: center;
  margin-bottom: 10px;
  color: #333;
  font-size: 22px;
}

.subtitle {
  text-align: center;
  margin-bottom: 20px;
  color: #666;
  font-size: 16px;
}

.register-form {
  margin-top: 20px;
}

.verify-code-item :deep(.el-form-item__content) {
  display: flex;
  gap: 10px;
}

.get-code-btn {
  width: 120px;
  flex-shrink: 0;
}

.register-button {
  width: 100%;
}

.options {
  display: flex;
  justify-content: center;
  margin-top: 15px;
  color: #666;
}

.login-link {
  margin-left: 5px;
  color: #409EFF;
  text-decoration: none;
}

.login-link:hover {
  text-decoration: underline;
}
</style> 