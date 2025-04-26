<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Message } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const email = ref('')
const loading = ref(false)
const formRef = ref<FormInstance>()

// 增强的邮箱验证逻辑
const validateEmail = (_rule: any, value: string, callback: any) => {
  if (!value) {
    return callback(new Error('请输入邮箱地址'))
  }
  
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (!emailRegex.test(value)) {
    return callback(new Error('请输入有效的邮箱地址'))
  }
  
  // 添加邮箱长度限制
  const localPart = value.split('@')[0]
  const domainPart = value.split('@')[1]
  
  if (localPart.length > 64) {
    return callback(new Error('邮箱用户名部分不能超过64个字符'))
  }
  
  if (domainPart.length > 255) {
    return callback(new Error('邮箱域名部分不能超过255个字符'))
  }
  
  if (value.length > 320) {
    return callback(new Error('邮箱总长度不能超过320个字符'))
  }
  
  callback() // 验证通过
}

const rules = reactive<FormRules>({
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { validator: validateEmail, trigger: 'blur' }
  ]
})

const handleSubmit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  
  // 先强制验证所有字段，确保状态显示正确
  formEl.validateField('email')
  
  await formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      // 显示正在处理的提示
      ElMessage.info('正在发送验证码，请稍候...')
      
      try {
        await userStore.forgotPassword(email.value)
        ElMessage.success('验证码已发送，请检查您的邮箱')
        
        // 转到重置密码页面，并传递邮箱
        router.push({
          path: '/reset-password',
          query: { email: email.value }
        })
      } catch (error: any) {
        console.error('发送验证码失败:', error)
        
        // 改进错误提示，针对不同情况给出不同反馈
        if (error.response?.status === 404) {
          // 邮箱不存在但后端为了安全考虑可能不会明确告知
          ElMessage.warning({
            message: '如果该邮箱已注册，验证码将发送到您的邮箱',
            duration: 4000
          })
          
          // 用延迟模拟邮件发送过程，提升用户体验
          setTimeout(() => {
            ElMessage.error('没有找到与该邮箱关联的账号')
          }, 2000)
        } else if (error.response?.status === 429) {
          // 请求过于频繁
          ElMessage.error('请求过于频繁，请稍后再试')
        } else if (error.message && error.message.includes('Network Error')) {
          // 网络错误
          ElMessage.error('网络连接错误，请检查您的网络连接')
        } else if (error.message && error.message.includes('timeout')) {
          // 请求超时
          ElMessage.error('服务器响应超时，请稍后重试')
        } else {
          // 其他错误
          const errorMessage = error.response?.data?.message || '发送验证码失败，请稍后重试'
          ElMessage.error(errorMessage)
        }
      } finally {
        loading.value = false
      }
    } else {
      // 表单验证未通过
      ElMessage.warning('请输入有效的邮箱地址')
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="forgot-password-container">
    <div class="forgot-password-box">
      <div class="logo-container">
        <img src="/logo.png" alt="Logo" class="logo">
        <h2 class="system-title">全国景区数据分析及可视化系统</h2>
      </div>
      
      <h3 class="forgot-password-title">忘记密码</h3>
      
      <p class="instructions">
        请输入您的注册邮箱，我们会向该邮箱发送验证码，用于重置密码。
      </p>
      
      <el-form
        ref="formRef"
        :model="{ email }"
        :rules="rules"
        label-position="top"
        class="forgot-password-form"
        status-icon
        :validate-on-rule-change="false"
        validate-on-input
      >
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="email"
            placeholder="请输入注册时使用的邮箱"
            :disabled="loading"
            @keyup.enter="handleSubmit(formRef)"
            @input="() => formRef?.validateField('email')"
            clearable
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">请确保输入的邮箱能够正常接收邮件</div>
        </el-form-item>
        
        <el-button 
          type="primary" 
          :loading="loading" 
          class="submit-button" 
          @click="handleSubmit(formRef)"
        >
          发送验证码
        </el-button>
        
        <div class="form-footer">
          <el-button @click="goToLogin" type="text" class="login-link" :disabled="loading">
            返回登录
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.forgot-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(120deg, #29205e 0%, #4e3abb 100%);
  position: relative;
  overflow: hidden;
}

.forgot-password-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 40%);
  z-index: 1;
}

.forgot-password-box {
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

.forgot-password-box:hover {
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

.forgot-password-title {
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

.forgot-password-form {
  width: 100%;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
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
}

.login-link {
  font-weight: bold;
}

/* 添加自定义样式确保验证状态图标正确显示 */
:deep(.el-form-item.is-success .el-input__wrapper) {
  border-color: #67c23a !important;
  box-shadow: 0 0 0 1px #67c23a inset !important;
}

:deep(.el-form-item.is-error .el-input__wrapper) {
  border-color: #f56c6c !important;
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.el-form-item__error) {
  color: #f56c6c;
}

:deep(.el-form-item.is-success .el-input__validateIcon) {
  color: #67c23a;
  display: inline-flex !important;
}

:deep(.el-form-item.is-error .el-input__validateIcon) {
  color: #f56c6c;
  display: inline-flex !important;
}
</style> 