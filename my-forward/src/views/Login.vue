<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'


const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginForm = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const loginFormRef = ref<FormInstance>()

// 增强的验证规则
const validateEmail = (_rule: any, value: string, callback: any) => {
  // 检查是否为空
  if (!value) {
    return callback(new Error('请输入用户名或邮箱'))
  }
  
  // 如果输入的是邮箱，检查邮箱格式
  if (value.includes('@')) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    if (!emailRegex.test(value)) {
      return callback(new Error('邮箱格式不正确'))
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
  }
  
  callback() // 验证通过
}

const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { validator: validateEmail, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
})

// 添加登录尝试次数限制和防抖功能
const loginAttempts = ref(0);
const maxLoginAttempts = 3; // 登录尝试最大次数
const debounceTimeout = ref<number | null>(null);
const lockoutTime = ref(0); // 锁定时间（秒）
const lockoutTimer = ref<number | null>(null);

// 处理防抖登录提交
const debounceLogin = (formEl: FormInstance | undefined) => {
  // 如果在锁定期内，显示提示并返回
  if (lockoutTime.value > 0) {
    ElMessage.warning(`请等待 ${lockoutTime.value} 秒后再试`);
    return;
  }
  
  // 清除之前的计时器
  if (debounceTimeout.value) {
    clearTimeout(debounceTimeout.value);
  }
  
  // 设置新的防抖计时器
  debounceTimeout.value = window.setTimeout(() => {
    handleLogin(formEl);
  }, 300);  // 300毫秒的防抖时间
};

// 在组件加载时检查URL参数
onMounted(() => {
  // 检查URL中的参数，显示相应的消息
  if (route.query.disabled === 'true') {
    ElMessage.error({
      message: '您的账号已被管理员禁用，请联系管理员',
      duration: 5000
    })
  } else if (route.query.unauthorized === 'true') {
    ElMessage.warning({
      message: '您的登录已过期，请重新登录',
      duration: 5000
    })
  } else if (route.query.expired === 'true') {
    ElMessage.warning({
      message: '登录信息已过期，请重新登录',
      duration: 5000
    })
  } else if (route.query.logout === 'true') {
    ElMessage.success({
      message: '您已成功退出登录',
      duration: 3000
    })
  } else if (route.query.reset === 'true') {
    ElMessage.success({
      message: '密码已重置成功，请使用新密码登录',
      duration: 3000
    })
  } else if (route.query.registered === 'true') {
    ElMessage.success({
      message: '注册成功！请登录您的账号',
      duration: 3000
    })
  }
  
  // 清除可能存在的token和用户数据
  userStore.logout({ redirectToLogin: false, reason: '' })
})

const handleLogin = async (formEl: FormInstance | undefined) => {
  // 已经在加载状态，不重复提交
  if (loading.value) return;
  
  // 登录尝试次数限制，防止无限循环
  if (loginAttempts.value >= maxLoginAttempts) {
    // 设置锁定时间（递增）
    lockoutTime.value = 30 * Math.pow(2, loginAttempts.value - maxLoginAttempts);
    
    ElMessage.error(`尝试登录次数过多，请等待 ${lockoutTime.value} 秒后再试`);
    
    // 开始锁定倒计时
    if (lockoutTimer.value) clearInterval(lockoutTimer.value);
    
    lockoutTimer.value = window.setInterval(() => {
      lockoutTime.value--;
      if (lockoutTime.value <= 0) {
        clearInterval(lockoutTimer.value!);
        loginAttempts.value = 0; // 重置尝试次数
        ElMessage.info('现在可以重新尝试登录');
      }
    }, 1000);
    
    return;
  }
  
  if (!formEl) return;
  
  // 先强制验证所有字段，确保状态显示正确
  Object.keys(loginForm).forEach(field => {
    formEl.validateField(field)
  })
  
  await formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      loginAttempts.value++;  // 增加登录尝试次数
      
      try {
        // 正常API调用登录逻辑
        console.log('开始调用登录API...')
        const loginResult = await userStore.login(loginForm.username, loginForm.password)
        console.log('登录API调用成功:', loginResult)
        
        // 检查登录状态
        const userInfo = userStore.getUserInfo()
        console.log('登录后用户状态:', {
          isLoggedIn: !!userInfo.token,
          token: userInfo.token ? `${userInfo.token.substring(0, 10)}...` : 'null',
          username: userInfo.username,
          tokenExpiry: new Date(userInfo.tokenExpiry).toLocaleString()
        })
        
        // 登录成功，重置尝试次数
        loginAttempts.value = 0;
        
        // 显示欢迎消息
        ElMessage.success(`欢迎回来，${userInfo.username}！`);
        
        // 使用延时确保状态已完全更新
        setTimeout(() => {
          console.log('准备跳转到dashboard页面...')
          router.push('/dashboard')
        }, 500)
      } catch (error: any) {
        console.error('登录失败:', error);
        
        // 改进错误处理逻辑，特别处理禁用用户情况
        if (error.response) {
          // 禁用用户可能返回403或400状态码，需要分别处理
          if (error.response.status === 403 && error.response.data && error.response.data.detail === '用户已被禁用') {
            // 403 Forbidden - 禁用用户情况
            ElMessage.error({
              message: '您的账号已被管理员禁用，请联系管理员',
              duration: 5000
            });
            
            // 确保清理会话存储，但不进行重定向
            userStore.logout({ redirectToLogin: false, reason: '' });
            
            // 登录尝试次数加倍，快速达到限制
            loginAttempts.value = maxLoginAttempts;
          } else if (error.response.status === 400 && 
                    error.response.data && 
                    ((error.response.data.detail && error.response.data.detail.includes('已被禁用')) || 
                     (error.response.data.non_field_errors && error.response.data.non_field_errors.some((e: string) => e.includes('已被禁用'))) ||
                     (error.response.data.errors && error.response.data.errors.non_field_errors && 
                      error.response.data.errors.non_field_errors.some((e: string) => e.includes('已被禁用'))))) {
            // 400 Bad Request，但包含禁用用户信息 - 旧错误格式兼容
            ElMessage.error({
              message: '您的账号已被管理员禁用，请联系管理员',
              duration: 5000
            });
            
            // 确保清理会话存储，但不进行重定向
            userStore.logout({ redirectToLogin: false, reason: '' });
          } else if (error.response.status === 400) {
            // 其他400错误通常是验证错误
            ElMessage.error(error.response.data.detail || error.response.data.message || '用户名或密码错误');
          } else if (error.response.status === 401) {
            // 未授权错误
            ElMessage.error('用户名或密码错误，请重新输入');
          } else if (error.response.status === 429) {
            // 请求过多
            ElMessage.error('登录请求过于频繁，请稍后再试');
            // 增加锁定时间
            loginAttempts.value = maxLoginAttempts;
          } else {
            // 其他HTTP错误
            ElMessage.error(error.response.data.detail || error.response.data.message || '登录失败，请稍后再试');
          }
        } else if (error.message && error.message.includes('Network Error')) {
          // 网络错误
          ElMessage.error('网络连接错误，请检查您的网络连接');
        } else if (error.message && error.message.includes('timeout')) {
          // 请求超时
          ElMessage.error('服务器响应超时，请稍后重试');
        } else {
          // 非HTTP错误(如网络问题)
          ElMessage.error('登录失败，无法连接到服务器');
        }
      } finally {
        loading.value = false;
      }
    } else {
      // 表单验证失败时的友好提示
      ElMessage.warning('请正确填写登录信息');
    }
  })
}

const goToRegister = () => {
  router.push('/register')
}

const goToForgotPassword = () => {
  router.push('/forgot-password')
}

const goToAdminLogin = () => {
  router.push('/admin')
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
    
    <!-- 右侧登录区域 -->
    <div class="login-container">
      <div class="login-box">
        <div class="logo-container">
          <img src="/logo.png" alt="Logo" class="logo">
          <h2 class="system-title">全国景区数据分析及可视化系统</h2>
        </div>
        
        <h3 class="login-title">用户登录</h3>
        
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="rules"
          label-position="top"
          class="login-form"
          status-icon
        >
          <el-form-item label="用户名/邮箱" prop="username">
            <el-input 
              v-model="loginForm.username"
              placeholder="请输入用户名或邮箱"
              :disabled="loading || lockoutTime > 0"
              @keyup.enter="debounceLogin(loginFormRef)"
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              :disabled="loading || lockoutTime > 0"
              @keyup.enter="debounceLogin(loginFormRef)"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <div class="form-actions">
            <el-checkbox>记住我</el-checkbox>
            <el-button @click="goToForgotPassword" type="text">忘记密码?</el-button>
          </div>
          
          <el-button 
            type="primary" 
            :loading="loading" 
            class="login-button" 
            @click="debounceLogin(loginFormRef)"
            :disabled="lockoutTime > 0"
          >
            {{ lockoutTime > 0 ? `请等待 ${lockoutTime} 秒` : '登录' }}
          </el-button>
          
          <div class="form-footer">
            <span>还没有账号? </span>
            <el-button @click="goToRegister" type="text" class="register-link">
              注册
            </el-button>
          </div>
          
          <div class="admin-login-link">
            <el-button @click="goToAdminLogin" type="text">
              管理员登录
            </el-button>
          </div>
        </el-form>
      </div>
    </div>

    <!-- MOVED DISCLAIMER HERE -->
    <div class="page-disclaimer">
      <p><strong>声明：</strong></p>
      <p>1. 本网站所有景区数据均采集自马蜂窝旅游网，仅用于本科毕业设计（学术研究），非商业用途。数据版权归马蜂窝所有。</p>
      <p>2. 若马蜂窝或其他权利方认为本网站内容侵犯合法权益，可通过 [邮箱：Kirito3143285505@outlook.com / 联系方式：19985469461] 联系，我将立即处理。</p>
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
  position: relative; /* Added for positioning disclaimer */
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
  margin-left: 7%;
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

/* 右侧登录区域样式 */
.login-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  max-width: 58%;
}

.login-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 40%);
  z-index: 1;
}

.login-box {
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

.login-box:hover {
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

.login-title {
  font-size: 24px;
  color: #333;
  text-align: center;
  margin-bottom: 30px;
}

.login-form {
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  margin-bottom: 20px;
}

.form-footer {
  text-align: center;
  margin-bottom: 10px;
}

.register-link {
  font-weight: bold;
}

.admin-login-link {
  text-align: center;
  margin-top: 10px;
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

/* 响应式调整 */
@media (max-width: 1024px) {
  .auth-container {
    flex-direction: column;
  }
  
  .school-info,
  .login-container {
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
}

/* New styles for page-level disclaimer */
.page-disclaimer {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 15px;
  background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent background */
  font-size: 12px;
  color: #f0f0f0; /* Light text color for dark background */
  line-height: 1.6;
  text-align: center;
  z-index: 10; /* Ensure it's above other content if necessary */
}

.page-disclaimer p {
  margin-bottom: 5px;
}

.page-disclaimer p:last-child {
  margin-bottom: 0;
}
</style> 