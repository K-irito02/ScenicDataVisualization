<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { request } from '@/api'
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

// 密码强度检查器
const passwordStrength = computed(() => {
  const password = registerForm.password;
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
const validateUsername = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请输入用户名'))
  } else if (value.length < 3) {
    callback(new Error('用户名长度不能少于3个字符'))
  } else if (value.length > 20) {
    callback(new Error('用户名长度不能超过20个字符'))
  } else if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(value)) {
    callback(new Error('用户名只能包含字母、数字、下划线和汉字'))
  } else {
    callback()
  }
}

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

const validatePass = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6个字符'))
  } else if (passwordStrength.value.score <= 2) {
    callback(new Error('密码强度较弱，建议包含大小写字母、数字和特殊字符'))
  } else {
    if (registerForm.confirmPassword !== '') {
      if (registerFormRef.value) {
        registerFormRef.value.validateField('confirmPassword')
      }
    }
    callback()
  }
}

const validatePass2 = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
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

const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { validator: validateUsername, trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { validator: validateEmail, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { validator: validateCode, trigger: 'blur' }
  ]
})

// 发送验证码
const sendCode = async () => {
  try {
    await registerFormRef.value?.validateField('email')
    sendingCode.value = true
    
    ElMessage.info('正在发送验证码，请稍候...')
    
    try {
      await request({
        url: '/api/email/send-code/',
        method: 'post',
        data: { email: registerForm.email }
      })
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
      console.error('发送验证码错误详情:', error)
      
      // 检查是否为超时错误
      if (error.message && error.message.includes('timeout')) {
        ElMessage.error('发送验证码请求超时，请检查网络连接或稍后重试')
      } else if (error.response?.status === 400 && error.response?.data?.message?.includes('该邮箱已被使用')) {
        ElMessage.error('该邮箱已被注册，请使用其他邮箱或找回密码')
      } else if (error.response?.data?.errors) {
        const errors = error.response.data.errors
        Object.keys(errors).forEach(key => {
          ElMessage.error(`${key}: ${errors[key].join(', ')}`)
        })
      } else if (error.response?.data?.message) {
        ElMessage.error(error.response.data.message)
      } else if (error.message && error.message.includes('Network Error')) {
        ElMessage.error('网络连接错误，请检查您的网络连接')
      } else {
        ElMessage.error('发送验证码失败，请稍后重试')
      }
      sendingCode.value = false
    }
  } catch (error) {
    // 邮箱验证失败
    sendingCode.value = false
  }
}

// 注册
const handleRegister = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  
  // 先强制验证所有字段，确保状态显示正确
  Object.keys(registerForm).forEach(field => {
    formEl.validateField(field as any)
  })
  
  await formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      ElMessage.info('正在提交注册信息，请稍候...')
      
      try {
        console.log('发送注册请求，数据:', {
          username: registerForm.username,
          email: registerForm.email,
          code: registerForm.code
        })
        
        await userStore.register(
          registerForm.username,
          registerForm.email,
          registerForm.password,
          registerForm.code
        )
        
        ElMessage.success('注册成功，即将前往登录页面')
        
        // 跳转到登录页并传递参数
        setTimeout(() => {
          router.push({
            path: '/login',
            query: { registered: 'true' }
          })
        }, 1500)
      } catch (error: any) {
        console.error('注册错误详情:', error.response?.data)
        
        if (error.response?.status === 400 && error.response?.data?.errors?.username?.includes('用户名已存在')) {
          ElMessage.error('该用户名已被使用，请选择其他用户名')
        } else if (error.response?.status === 400 && error.response?.data?.errors?.email?.includes('邮箱已被注册')) {
          ElMessage.error('该邮箱已被注册，请使用其他邮箱')
        } else if (error.response?.status === 400 && error.response?.data?.errors?.code?.includes('验证码错误')) {
          ElMessage.error('验证码错误或已过期，请重新获取')
        } else if (error.response?.data?.errors) {
          const errors = error.response.data.errors
          Object.entries(errors).forEach(([key, value]) => {
            if (Array.isArray(value)) {
              ElMessage.error(`${key}: ${value.join(', ')}`)
            } else if (typeof value === 'string') {
              ElMessage.error(`${key}: ${value}`)
            } else {
              ElMessage.error(`${key}: 验证失败`)
            }
          })
        } else if (error.response?.data?.message) {
          ElMessage.error(error.response.data.message)
        } else if (error.message && error.message.includes('Network Error')) {
          ElMessage.error('网络连接错误，请检查您的网络连接')
        } else if (error.message && error.message.includes('timeout')) {
          ElMessage.error('服务器响应超时，请稍后重试')
        } else {
          ElMessage.error('注册失败，请稍后重试')
        }
      } finally {
        loading.value = false
      }
    } else {
      // 表单验证失败
      ElMessage.warning('请正确填写所有必填项')
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
        <h2 class="system-title">全国景区数据分析及可视化系统</h2>
      </div>
      
      <h3 class="register-title">用户注册</h3>
      
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        label-position="top"
        class="register-form"
        status-icon
        :validate-on-rule-change="false"
        validate-on-input
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="registerForm.username"
            placeholder="请输入用户名（3-20个字符）"
            prefix-icon="User"
            :disabled="loading"
            @input="() => registerFormRef?.validateField('username')"
            clearable
          />
          <div class="form-item-tip">仅支持字母、数字、下划线和汉字</div>
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            prefix-icon="Message"
            :disabled="loading"
            @input="() => registerFormRef?.validateField('email')"
            clearable
          />
          <div class="form-item-tip">用于接收验证码和找回密码</div>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（至少6个字符）"
            prefix-icon="Lock"
            show-password
            :disabled="loading"
            @input="() => registerFormRef?.validateField('password')"
            clearable
          />
          <div class="password-strength" v-if="registerForm.password">
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
          </div>
          <div class="form-item-tip">建议使用字母、数字和特殊字符组合</div>
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            show-password
            :disabled="loading"
            @input="() => registerFormRef?.validateField('confirmPassword')"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="验证码" prop="code">
          <div class="code-input-group">
            <el-input 
              v-model="registerForm.code"
              placeholder="请输入6位验证码"
              prefix-icon="Key"
              :disabled="loading"
              @input="() => registerFormRef?.validateField('code')"
              clearable
            />
            <el-button 
              type="primary" 
              :disabled="sendingCode || countdown > 0 || loading" 
              @click="sendCode"
            >
              {{ countdown > 0 ? `${countdown}秒后重新发送` : '获取验证码' }}
            </el-button>
          </div>
          <div class="form-item-tip">验证码将发送到您的邮箱</div>
        </el-form-item>
        
        <el-button 
          type="primary" 
          class="register-button" 
          :loading="loading"
          @click="handleRegister(registerFormRef)"
        >
          注册
        </el-button>
        
        <div class="form-footer">
          <span>已有账号？</span>
          <el-button @click="goToLogin" type="text" class="login-link" :disabled="loading">
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
  background: linear-gradient(120deg, #29205e 0%, #4e3abb 100%);
  padding: 20px 0;
  position: relative;
  overflow: hidden;
}

.register-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 40%);
  z-index: 1;
}

.register-box {
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

.register-box:hover {
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

.register-title {
  font-size: 24px;
  color: #333;
  text-align: center;
  margin-bottom: 20px;
}

.register-form {
  width: 100%;
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
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

.code-input-group {
  display: flex;
  gap: 10px;
}

.code-input-group .el-input {
  flex: 1;
}

.code-input-group .el-button {
  width: 130px;
  font-size: 13px;
  padding: 0 10px;
  white-space: nowrap;
}

.register-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  margin-top: 20px;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  color: #606266;
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