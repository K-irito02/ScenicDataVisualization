<template>
  <div class="forgot-password-container">
    <div class="forgot-password-box">
      <h2 class="title">全国景区数据可视化系统</h2>
      <h3 class="subtitle">找回密码</h3>
      
      <el-steps :active="currentStep" finish-status="success" simple style="margin: 20px 0">
        <el-step title="验证邮箱" />
        <el-step title="重置密码" />
        <el-step title="完成" />
      </el-steps>
      
      <!-- 步骤1: 验证邮箱 -->
      <el-form 
        v-if="currentStep === 0" 
        ref="emailFormRef" 
        :model="emailForm" 
        :rules="emailRules" 
        class="forgot-password-form"
      >
        <el-form-item prop="email">
          <el-input 
            v-model="emailForm.email" 
            placeholder="请输入注册邮箱"
            prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item prop="verifyCode" class="verify-code-item">
          <el-input 
            v-model="emailForm.verifyCode" 
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
            class="next-button" 
            @click="verifyEmail"
          >
            下一步
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 步骤2: 重置密码 -->
      <el-form 
        v-if="currentStep === 1" 
        ref="passwordFormRef" 
        :model="passwordForm" 
        :rules="passwordRules" 
        class="forgot-password-form"
      >
        <el-form-item prop="newPassword">
          <el-input 
            v-model="passwordForm.newPassword" 
            type="password" 
            placeholder="请输入新密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="passwordForm.confirmPassword" 
            type="password" 
            placeholder="请确认新密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            class="next-button" 
            @click="resetPassword"
          >
            重置密码
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 步骤3: 完成 -->
      <div v-if="currentStep === 2" class="success-step">
        <el-result
          icon="success"
          title="密码重置成功"
          sub-title="您的密码已成功重置，请使用新密码登录"
        >
          <template #extra>
            <el-button type="primary" @click="goToLogin">
              返回登录
            </el-button>
          </template>
        </el-result>
      </div>
      
      <div class="options">
        <router-link to="/login" class="login-link">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getResetPasswordCode, resetPassword } from '@/api/user'

const router = useRouter()
const loading = ref(false)
const cooldown = ref(0)
const currentStep = ref(0)
const emailFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

// 邮箱验证表单数据
const emailForm = reactive({
  email: '',
  verifyCode: ''
})

// 密码重置表单数据
const passwordForm = reactive({
  newPassword: '',
  confirmPassword: ''
})

// 表单验证规则
const emailRules = reactive<FormRules>({
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  verifyCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码为4位数字', trigger: 'blur' }
  ]
})

// 密码验证
const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = reactive<FormRules>({
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
})

// 获取验证码
const getCode = async () => {
  // 首先验证邮箱
  emailFormRef.value?.validateField('email', async (valid) => {
    if (!valid) {
      try {
        const res = await getResetPasswordCode(emailForm.email)
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
          emailForm.verifyCode = res.data.verifyCode
        }
      } catch (error: any) {
        console.error('获取验证码失败:', error)
        ElMessage.error('获取验证码失败')
      }
    }
  })
}

// 验证邮箱
const verifyEmail = async () => {
  if (!emailFormRef.value) return
  
  await emailFormRef.value.validate(async (valid) => {
    if (valid) {
      // 邮箱验证成功，进入下一步
      currentStep.value = 1
    }
  })
}

// 重置密码
const resetPassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        const res = await resetPassword(
          emailForm.email,
          emailForm.verifyCode,
          passwordForm.newPassword
        )
        
        ElMessage.success('密码重置成功')
        currentStep.value = 2
      } catch (error: any) {
        console.error('密码重置失败:', error)
        ElMessage.error(error.message || '密码重置失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// 返回登录页
const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.forgot-password-container {
  height: 100vh;
  width: 100%;
  background-color: #409EFF;
  display: flex;
  justify-content: center;
  align-items: center;
}

.forgot-password-box {
  width: 450px;
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

.forgot-password-form {
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

.next-button {
  width: 100%;
}

.success-step {
  padding: 20px 0;
}

.options {
  display: flex;
  justify-content: center;
  margin-top: 15px;
  color: #666;
}

.login-link {
  color: #409EFF;
  text-decoration: none;
}

.login-link:hover {
  text-decoration: underline;
}
</style> 