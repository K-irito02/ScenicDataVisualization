<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Message, Key, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const form = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: ''
})

const loading = ref(false)
const formRef = ref<FormInstance>()

// 从路由参数中获取邮箱
onMounted(() => {
  if (route.query.email) {
    form.email = route.query.email as string
  }
})

// 表单验证规则
const validatePass = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else {
    if (form.confirmPassword !== '') {
      if (formRef.value) {
        formRef.value.validateField('confirmPassword')
      }
    }
    callback()
  }
}

const validatePass2 = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = reactive<FormRules>({
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码长度为6位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ]
})

const handleSubmit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  
  await formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        const response = await userStore.resetPassword(
          form.email,
          form.code,
          form.password
        )
        
        ElMessage.success('密码重置成功，请使用新密码登录')
        router.push('/login')
      } catch (error: any) {
        console.error('密码重置失败:', error)
        const errorMessage = error.response?.data?.message || '密码重置失败，请稍后重试'
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
    }
  })
}

const resendCode = async () => {
  if (!form.email) {
    ElMessage.warning('请先输入邮箱地址')
    return
  }
  
  try {
    const response = await userStore.forgotPassword(form.email)
    ElMessage.success('验证码已重新发送，请检查您的邮箱')
  } catch (error: any) {
    console.error('重新发送验证码失败:', error)
    const errorMessage = error.response?.data?.message || '重新发送验证码失败，请稍后重试'
    ElMessage.error(errorMessage)
  }
}

const goToForgotPassword = () => {
  router.push('/forgot-password')
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="reset-password-container">
    <div class="reset-password-box">
      <div class="logo-container">
        <img src="/logo.png" alt="Logo" class="logo">
        <h2 class="system-title">全国景区数据分析及可视化系统</h2>
      </div>
      
      <h3 class="reset-password-title">重置密码</h3>
      
      <p class="instructions">
        请输入您收到的验证码和新密码，完成密码重置。
      </p>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="reset-password-form"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="form.email"
            placeholder="请输入邮箱"
            :disabled="!!route.query.email"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="验证码" prop="code">
          <div class="code-input-group">
            <el-input 
              v-model="form.code"
              placeholder="请输入验证码"
            >
              <template #prefix>
                <el-icon><Key /></el-icon>
              </template>
            </el-input>
            <el-button @click="resendCode" class="resend-button">
              重新发送
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="新密码" prop="password">
          <el-input 
            v-model="form.password"
            type="password"
            placeholder="请输入新密码"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-button 
          type="primary" 
          :loading="loading" 
          class="submit-button" 
          @click="handleSubmit(formRef)"
        >
          重置密码
        </el-button>
        
        <div class="form-footer">
          <el-button @click="goToForgotPassword" type="text" class="back-link">
            返回上一步
          </el-button>
          <el-divider direction="vertical" />
          <el-button @click="goToLogin" type="text" class="login-link">
            返回登录
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.reset-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(120deg, #010357 0%, #20228a 100%);
  padding: 20px 0;
  position: relative;
  overflow: hidden;
}

.reset-password-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 40%);
  z-index: 1;
}

.reset-password-box {
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

.reset-password-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
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

.reset-password-title {
  font-size: 24px;
  color: #333;
  text-align: center;
  margin-bottom: 20px;
}

.instructions {
  text-align: center;
  margin-bottom: 20px;
  color: #606266;
  line-height: 1.5;
}

.reset-password-form {
  width: 100%;
}

.submit-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  margin-bottom: 20px;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.back-link, .login-link {
  font-weight: bold;
}

.code-input-group {
  display: flex;
  gap: 10px;
}

.code-input-group .el-input {
  flex: 1;
}

.resend-button {
  width: 100px;
}
</style> 