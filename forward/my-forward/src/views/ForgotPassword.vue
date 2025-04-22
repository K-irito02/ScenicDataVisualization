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

const rules = reactive<FormRules>({
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
})

const handleSubmit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  
  await formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        const response = await userStore.forgotPassword(email.value)
        ElMessage.success('验证码已发送，请检查您的邮箱')
        
        // 转到重置密码页面，并传递邮箱
        router.push({
          path: '/reset-password',
          query: { email: email.value }
        })
      } catch (error: any) {
        console.error('发送验证码失败:', error)
        // 显示后端返回的错误消息，特别关注邮箱重复的提示
        const errorMessage = error.response?.data?.message || '发送验证码失败，请稍后重试'
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
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
      >
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="email"
            placeholder="请输入邮箱"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
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
          <el-button @click="goToLogin" type="text" class="login-link">
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
</style> 