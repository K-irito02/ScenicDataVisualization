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
  <div class="login-container">
    <div class="login-box">
      <div class="logo-container">
        <img src="/logo.png" alt="景区数据分析及可视化系统" class="logo-image" />
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
            show-password
            :disabled="loading || lockoutTime > 0"
            @keyup.enter="debounceLogin(loginFormRef)"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <div class="form-actions">
          <el-button @click="goToForgotPassword" type="text" class="forgot-password" :disabled="loading">
            忘记密码？
          </el-button>
        </div>
        
        <el-button 
          type="primary" 
          :loading="loading" 
          :disabled="lockoutTime > 0"
          class="login-button" 
          @click="debounceLogin(loginFormRef)"
        >
          <span v-if="lockoutTime > 0">{{ lockoutTime }}秒后可重试</span>
          <span v-else>登录</span>
        </el-button>
        
        <div class="form-footer">
          <span>没有账号？</span>
          <el-button @click="goToRegister" type="text" class="register-link" :disabled="loading">
            立即注册
          </el-button>
        </div>
        
        <div class="admin-login-link">
          <el-button @click="goToAdminLogin" type="text" :disabled="loading">
            管理员入口
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(120deg, #191549 0%, #072e83 100%);
  position: relative;
  overflow: hidden;
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

.logo-image {
  width: 100px;
  height: 100px;
  margin-bottom: 10px;
}

.system-title {
  font-size: 20px;
  text-align: center;
  margin-top: 15px;
  color: #333;
  font-weight: 500;
}

.login-title {
  font-size: 22px;
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.login-form {
  margin-top: 20px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.forgot-password {
  font-size: 14px;
  color: #999;
  padding: 0;
}

.login-button {
  width: 100%;
  padding: 12px 20px;
  margin-bottom: 20px;
}

.form-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #666;
}

.register-link {
  margin-left: 5px;
  font-weight: 500;
  padding: 0;
}

.admin-login-link {
  text-align: center;
  margin-top: 15px;
}
</style> 