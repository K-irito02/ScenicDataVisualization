<template>
  <div class="register-container">
    <div class="register-box">
      <div class="title">
        <h1>全国景区数据可视化系统</h1>
        <h3>用户注册</h3>
      </div>
      
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef">
        <el-form-item prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="请输入用户名" 
            @blur="validateField('username')"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
            <template #suffix v-if="validStatus.username === 'valid'">
              <el-icon class="valid-icon"><Check /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="email">
          <el-input 
            v-model="registerForm.email" 
            placeholder="请输入邮箱" 
            @blur="validateField('email')"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
            <template #suffix v-if="validStatus.email === 'valid'">
              <el-icon class="valid-icon"><Check /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="请输入密码" 
            @blur="validateField('password')"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
            <template #suffix v-if="validStatus.password === 'valid'">
              <el-icon class="valid-icon"><Check /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="请确认密码"
            @blur="validateField('confirmPassword')"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
            <template #suffix v-if="validStatus.confirmPassword === 'valid'">
              <el-icon class="valid-icon"><Check /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" class="register-btn" @click="handleRegister" :loading="loading">注册</el-button>
        </el-form-item>
      </el-form>
      
      <div class="actions">
        <span class="back-to-login" @click="$router.push('/login')">返回登录</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Check } from '@element-plus/icons-vue'
import { register } from '@/api/user'

const router = useRouter()
const registerFormRef = ref<FormInstance>()
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 验证状态对象：未验证|验证中|验证通过
const validStatus = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 验证确认密码
const validateConfirmPassword = (_: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 验证单个字段
const validateField = async (field: string) => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validateField(field)
    validStatus[field as keyof typeof validStatus] = 'valid'
  } catch (error) {
    validStatus[field as keyof typeof validStatus] = 'invalid'
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const { username, email, password } = registerForm
        await register(username, password, email)
        
        ElMessage.success('注册成功，请登录')
        router.push('/login')
      } catch (error) {
        console.error('注册失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #1976d2, #64b5f6);
}

.register-box {
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

.register-btn {
  width: 100%;
}

.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.back-to-login {
  color: #1976d2;
  cursor: pointer;
}

.back-to-login:hover {
  text-decoration: underline;
}

.valid-icon {
  color: #67c23a;
}
</style> 