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
const resending = ref(false)
const resendCountdown = ref(0)
const resendTimer = ref<number | null>(null)

// 从路由参数中获取邮箱
onMounted(() => {
  if (route.query.email) {
    form.email = route.query.email as string
  }
  
  // 重置计时器，以防组件重新加载
  clearInterval(resendTimer.value as number)
})

// 密码强度检查器
const passwordStrength = computed(() => {
  const password = form.password;
  if (!password) return { score: 0, level: '空', color: '#e6e6e6' };
  
  let score = 0;
  
  // 长度检查
  if (password.length >= 8) score += 1;
  if (password.length >= 10) score += 1;
  
  // 包含数字
  if (/\d/.test(password)) score += 1;
  
  // 包含小写字母
  if (/[a-z]/.test(password)) score += 1;
  
  // 包含大写字母
  if (/[A-Z]/.test(password)) score += 1;
  
  // 包含特殊字符
  if (/[^A-Za-z0-9]/.test(password)) score += 1;
  
  // 根据分数确定强度级别
  let level, color;
  if (score <= 2) {
    level = '弱';
    color = '#F56C6C';
  } else if (score <= 4) {
    level = '中';
    color = '#E6A23C';
  } else {
    level = '强';
    color = '#67C23A';
  }
  
  return { score, level, color };
});

// 表单验证规则
const validateEmail = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请输入邮箱地址'))
  } else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value)) {
    callback(new Error('请输入有效的邮箱地址'))
  } else {
    callback()
  }
}

const validateCode = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请输入验证码'))
  } else if (!/^\d{6}$/.test(value)) {
    callback(new Error('验证码为6位数字'))
  } else {
    callback()
  }
}

const validatePass = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6个字符'))
  } else if (passwordStrength.value.score <= 1) {
    callback(new Error('密码强度过弱，请使用更安全的密码'))
  } else {
    if (form.confirmPassword !== '') {
      if (formRef.value) {
        formRef.value.validateField('confirmPassword')
      }
    }
    callback()
  }
}

const validatePass2 = (_rule: any, value: string, callback: any) => {
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
    { validator: validateEmail, trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { validator: validateCode, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
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
      
      ElMessage.info('正在处理密码重置请求，请稍候...')
      
      try {
        await userStore.resetPassword(form.email, form.code, form.password)
        ElMessage.success('密码重置成功，请使用新密码登录')
        
        // 延迟跳转，让用户有时间看到成功消息
        setTimeout(() => {
          router.push({
            path: '/login',
            query: { reset: 'true' }
          })
        }, 1500)
      } catch (error: any) {
        console.error('密码重置失败:', error)
        
        // 根据不同错误类型给出友好提示
        if (error.response?.status === 400 && error.response?.data?.message?.includes('验证码错误')) {
          ElMessage.error('验证码错误或已过期，请重新获取')
        } else if (error.response?.status === 400 && error.response?.data?.message?.includes('邮箱不存在')) {
          ElMessage.error('该邮箱未注册，请检查输入是否正确')
        } else if (error.message && error.message.includes('Network Error')) {
          ElMessage.error('网络连接错误，请检查您的网络连接')
        } else if (error.message && error.message.includes('timeout')) {
          ElMessage.error('服务器响应超时，请稍后重试')
        } else {
          const errorMessage = error.response?.data?.message || '密码重置失败，请稍后重试'
          ElMessage.error(errorMessage)
        }
      } finally {
        loading.value = false
      }
    } else {
      // 表单验证失败
      ElMessage.warning('请正确填写所有字段')
    }
  })
}

const resendCode = async () => {
  if (!form.email) {
    ElMessage.warning('请先输入邮箱地址')
    return
  }
  
  if (resending.value) {
    return // 防止重复点击
  }
  
  resending.value = true
  ElMessage.info('正在重新发送验证码，请稍候...')
  
  try {
    await userStore.forgotPassword(form.email)
    ElMessage.success('验证码已重新发送，请查收您的邮箱')
    
    // 开始倒计时，60秒内不允许重复发送
    resendCountdown.value = 60
    resendTimer.value = window.setInterval(() => {
      resendCountdown.value--
      if (resendCountdown.value <= 0) {
        clearInterval(resendTimer.value as number)
        resending.value = false
      }
    }, 1000)
  } catch (error: any) {
    console.error('重新发送验证码失败:', error)
    
    if (error.response?.status === 429) {
      ElMessage.error('发送请求过于频繁，请稍后再试')
    } else if (error.message && error.message.includes('Network Error')) {
      ElMessage.error('网络连接错误，请检查您的网络连接')
    } else {
      const errorMessage = error.response?.data?.message || '重新发送验证码失败，请稍后重试'
      ElMessage.error(errorMessage)
    }
    
    resending.value = false
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
        status-icon
      >
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="form.email"
            placeholder="请输入邮箱"
            :disabled="!!route.query.email || loading"
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
              placeholder="请输入6位数字验证码"
              :disabled="loading"
              @keyup.enter="handleSubmit(formRef)"
            >
              <template #prefix>
                <el-icon><Key /></el-icon>
              </template>
            </el-input>
            <el-button 
              @click="resendCode" 
              class="resend-button" 
              :disabled="resending || resendCountdown > 0 || loading"
              :loading="resending && resendCountdown === 0"
            >
              <span v-if="resendCountdown > 0">{{ resendCountdown }}秒后重发</span>
              <span v-else>重新发送</span>
            </el-button>
          </div>
          <div class="form-tip">验证码将发送到您的邮箱，有效期5分钟</div>
        </el-form-item>
        
        <el-form-item label="新密码" prop="password">
          <el-input 
            v-model="form.password"
            type="password"
            placeholder="请输入新密码（至少6个字符）"
            show-password
            :disabled="loading"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
          <div class="password-strength" v-if="form.password">
            <span>密码强度：</span>
            <span :style="{ color: passwordStrength.color }">{{ passwordStrength.level }}</span>
            <div class="strength-bar">
              <div 
                class="strength-level" 
                :style="{ 
                  width: `${Math.min(passwordStrength.score * 16, 100)}%`,
                  backgroundColor: passwordStrength.color 
                }"
              ></div>
            </div>
            <div class="form-tip">建议使用字母、数字和特殊字符组合</div>
          </div>
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
            :disabled="loading"
            @keyup.enter="handleSubmit(formRef)"
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
          <el-button @click="goToForgotPassword" type="text" class="back-link" :disabled="loading">
            返回上一步
          </el-button>
          <el-divider direction="vertical" />
          <el-button @click="goToLogin" type="text" class="login-link" :disabled="loading">
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
  background: linear-gradient(120deg, #29205e 0%, #4e3abb 100%);
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
  width: 450px;
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

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.code-input-group {
  display: flex;
  gap: 10px;
}

.code-input-group .el-input {
  flex: 1;
}

.code-input-group .el-button {
  width: 130px;
  white-space: nowrap;
  font-size: 13px;
  padding: 0 10px;
}

.password-strength {
  display: flex;
  align-items: center;
  font-size: 12px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.strength-bar {
  width: 100px;
  height: 4px;
  background-color: #e6e6e6;
  border-radius: 2px;
  overflow: hidden;
  margin-left: 8px;
}

.strength-level {
  height: 100%;
  transition: width 0.3s, background-color 0.3s;
}

.submit-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  margin-top: 20px;
}

.form-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
}

.back-link,
.login-link {
  font-weight: bold;
}

.el-divider {
  margin: 0 10px;
}
</style> 