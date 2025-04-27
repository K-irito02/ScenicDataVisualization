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
  
  // 先强制验证所有字段，确保状态显示正确
  Object.keys(form).forEach(field => {
    formEl.validateField(field)
  })
  
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

</script>

<template>
  <div class="auth-container">
    <!-- 左侧学校信息区域 -->
    <div class="school-info">
      <div class="school-header">
        <div class="school-logo">
          <img src="/logo-zijin.png" alt="南京理工大学紫金学院" class="logo-image">
        </div>
        <div class="school-name">
          <h1>南京理工大学紫金学院</h1>
          <h2>NANJING UNIVERSITY OF SCIENCE AND TECHNOLOGY ZIJIN COLLEGE</h2>
        </div>
      </div>
      <div class="department-info">
        <p>计算机与人工智能学院</p>
        <p>2025届本科毕业设计</p>
      </div>
    </div>
    
    <!-- 右侧重置密码区域 -->
    <div class="reset-password-container">
      <div class="reset-password-box">
        <div class="logo-container">
          <img src="/logo.png" alt="Logo" class="logo">
          <h2 class="system-title">全国景区数据分析及可视化系统</h2>
        </div>
        
        <h3 class="reset-password-title">重置密码</h3>
        
        <p class="instructions">
          请输入您收到的验证码，以及您希望设置的新密码。
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
              placeholder="请确认您的邮箱地址"
              :disabled="true"
            >
              <template #prefix>
                <el-icon><Message /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="验证码" prop="code" class="verification-code-item">
            <div class="verification-code-container">
              <el-input 
                v-model="form.code"
                placeholder="请输入6位验证码"
                :disabled="loading"
              >
                <template #prefix>
                  <el-icon><Key /></el-icon>
                </template>
              </el-input>
              <el-button 
                type="primary" 
                :disabled="resending" 
                @click="resendCode"
                class="send-code-button"
              >
                {{ resendCountdown > 0 ? `${resendCountdown}秒后重试` : '重新获取验证码' }}
              </el-button>
            </div>
          </el-form-item>
          
          <el-form-item label="新密码" prop="password">
            <el-input 
              v-model="form.password"
              type="password"
              placeholder="请设置新密码"
              :disabled="loading"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
            <div class="password-strength">
              <span>密码强度：</span>
              <div class="strength-indicator">
                <div 
                  class="strength-bar" 
                  :style="{ width: (passwordStrength.score / 6) * 100 + '%', background: passwordStrength.color }"
                ></div>
              </div>
              <span :style="{ color: passwordStrength.color }">{{ passwordStrength.level }}</span>
            </div>
          </el-form-item>
          
          <el-form-item label="确认新密码" prop="confirmPassword">
            <el-input 
              v-model="form.confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
              :disabled="loading"
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
            确认重置密码
          </el-button>
          
          <div class="form-footer">
            <el-button type="text" @click="$router.push('/login')" class="login-link" :disabled="loading">
              返回登录
            </el-button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
  background: linear-gradient(135deg, #4a0060 0%, #1a0d3b 100%);
}

/* 左侧学校信息区域样式 */
.school-info {
  flex: 1;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  text-align: center;
  max-width: 42%;
  margin-left: 5%;
}

.school-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.school-logo {
  margin-right: 20px;
}

.school-logo img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-top: 20px;
}

.school-name {
  text-align: left;
}

.school-name h1 {
  font-size: 65px;
  margin-bottom: 10px;
  font-weight: 500;
  font-family: "华文行楷", "STXingkai", serif;
  width: 100%;
}

.school-name h2 {
  font-size: 16px;
  font-weight: 400;
  margin-bottom: 20px;
  letter-spacing: 1px;
  font-family: "Noto Serif SC", serif;
  font-weight: 900;
}

.department-info {
  font-size: 18px;
  line-height: 1.6;
}

/* 右侧重置密码区域样式 */
.reset-password-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  max-width: 58%;
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
  max-height: 90vh;
  overflow-y: auto;
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
  width: 60px;
  border-radius: 50%;
  object-fit: cover;
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

.password-strength {
  display: flex;
  align-items: center;
  font-size: 12px;
  margin-top: 5px;
  color: #606266;
}

.strength-indicator {
  flex: 1;
  height: 6px;
  background-color: #eee;
  border-radius: 3px;
  margin: 0 8px;
  overflow: hidden;
}

.strength-bar {
  height: 100%;
  border-radius: 3px;
  transition: all 0.3s ease;
}

.verification-code-container {
  display: flex;
  gap: 10px;
}

.send-code-button {
  width: 140px;
  font-size: 14px;
}

.submit-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  margin-top: 20px;
  margin-bottom: 20px;
}

.form-footer {
  text-align: center;
  color: #606266;
}

.login-link {
  font-weight: bold;
}

/* 响应式调整 */
@media (max-width: 1024px) {
  .auth-container {
    flex-direction: column;
  }
  
  .school-info,
  .reset-password-container {
    flex: none;
    width: 100%;
    max-width: 100%;
    margin-left: 0;
  }
  
  .school-info {
    padding: 20px 0;
  }
  
  .school-header {
    justify-content: center;
  }
  
  .school-logo img {
    width: 80px;
    height: 80px;
  }
  
  .school-name h1 {
    font-size: 32px;
  }
  
  .school-name h2 {
    font-size: 14px;
  }
  
  .department-info {
    font-size: 16px;
  }
  
  .reset-password-box {
    width: 90%;
    padding: 30px;
  }
  
  .verification-code-container {
    flex-direction: column;
  }
  
  .send-code-button {
    width: 100%;
  }
}
</style> 