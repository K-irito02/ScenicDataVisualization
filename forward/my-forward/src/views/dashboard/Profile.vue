<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import axios from 'axios'
import { 
  Check, 
  Upload, 
  Picture, 
  Location, 
  Delete, 
  WarningFilled, 
  CircleCheckFilled, 
  Loading, 
  View,
  Key,
  CircleCheck
} from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { processImageUrl, DEFAULT_IMAGE } from '@/api/image-proxy' // 导入图片处理工具

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const activeTab = ref('info')
const uploading = ref(false)
const loading = ref(false)
const favoritesLoading = ref(false)
const favorites = ref<any[]>([])
const defaultImage = DEFAULT_IMAGE // 使用统一的默认图片路径

// 个人信息表单
const profileForm = reactive({
  username: userStore.username,
  email: userStore.email,
  email_code: '',
  location: userStore.location,
  avatar: userStore.avatar
})

const originalEmail = ref(userStore.email) // 保存原始邮箱用于比较
const showEmailCodeField = ref(false) // 控制验证码字段显示
const emailCodeSending = ref(false) // 验证码发送状态
const emailCodeCountdown = ref(0) // 验证码倒计时
const emailVerificationSuccess = ref(false) // 邮箱验证成功状态
const emailModificationInProgress = ref(false) // 邮箱修改进行中状态

const profileFormRef = ref<FormInstance>()

const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  email_code: [
    { validator: (_rule, value, callback) => {
        if (showEmailCodeField.value && !value) {
          callback(new Error('请输入验证码'));
        } else if (value && value.length !== 6) {
          callback(new Error('验证码为6位数字'));
        } else {
          callback();
        }
      }, 
      trigger: 'blur' 
    }
  ]
})

// 处理图片URL，确保正确显示默认图片
const getImageUrl = (imageUrl: string) => {
  return processImageUrl(imageUrl, defaultImage);
}

// 刷新头像变量
const avatarKey = ref(0)
const refreshAvatar = () => {
  avatarKey.value++
  console.log('Avatar key updated:', avatarKey.value)
  
  // 强制刷新已加载的头像
  const avatarImg = document.querySelector('.user-avatar img') as HTMLImageElement
  if (avatarImg) {
    // 添加随机参数强制浏览器重新加载
    const originalSrc = avatarImg.src.split('?')[0]
    avatarImg.src = `${originalSrc}?t=${new Date().getTime()}`
    console.log('强制刷新头像元素:', avatarImg.src)
  }
}

// 处理上传开始
const handleAvatarUploadStart = () => {
  uploading.value = true;
  console.log('开始上传头像...');
}

// 处理上传错误
const handleAvatarError = (error: any) => {
  console.error('头像上传失败:', error);
  ElMessage.error('头像上传失败，请稍后重试');
  uploading.value = false;
}

// 处理头像上传成功
const handleAvatarSuccess = (response: any) => {
  console.log('头像上传成功响应:', response);
  
  // 确保响应中包含头像URL
  if (!response.avatar_url) {
    ElMessage.error('服务器未返回头像URL');
    return;
  }
  
  // 使用服务器返回的头像URL更新头像
  let avatarUrl = response.avatar_url;
  
  // 确保URL格式正确（开头有/）
  if (avatarUrl && !avatarUrl.startsWith('/') && !avatarUrl.startsWith('http')) {
    avatarUrl = '/' + avatarUrl;
  }
  
  console.log('处理后的头像URL:', avatarUrl);
  
  // 保存到表单中用于更新资料
  profileForm.avatar = avatarUrl;
  
  // 更新用户存储中的头像
  userStore.setUserInfo({ avatar: avatarUrl });
  
  // 强制刷新头像显示
  refreshAvatar();
  
  // 设置上传状态为完成
  uploading.value = false;
  
  ElMessage.success('头像上传成功');
}

// 检查邮箱是否有变更
const checkEmailChange = () => {
  if (profileForm.email !== originalEmail.value) {
    showEmailCodeField.value = true
    emailVerificationSuccess.value = false
    emailModificationInProgress.value = true
  } else {
    showEmailCodeField.value = false
    profileForm.email_code = '' // 清空验证码
    emailVerificationSuccess.value = false
    emailModificationInProgress.value = false
  }
}

// 发送邮箱验证码
const sendEmailCode = async () => {
  if (!profileForm.email) {
    ElMessage.warning('请先输入邮箱地址')
    return
  }

  if (!/^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/.test(profileForm.email)) {
    ElMessage.warning('请输入有效的邮箱地址')
    return
  }

  emailCodeSending.value = true
  emailVerificationSuccess.value = false
  
  try {
    await userStore.sendEmailCode(profileForm.email, true) // true表示是个人资料更新场景
    ElMessage.success('验证码已发送，请查收邮件')
    
    // 设置倒计时
    emailCodeCountdown.value = 60
    const timer = setInterval(() => {
      emailCodeCountdown.value--
      if (emailCodeCountdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error: any) {
    console.error('发送验证码失败:', error)
    ElMessage.error(error.response?.data?.message || '发送验证码失败，请稍后重试')
  } finally {
    emailCodeSending.value = false
  }
}

// 验证验证码是否正确（可选，添加单独验证步骤）
const verifyEmailCode = async () => {
  if (!profileForm.email_code || profileForm.email_code.length !== 6) {
    ElMessage.warning('请输入6位数字验证码')
    return
  }
  
  loading.value = true
  
  try {
    // 调用API验证验证码
    await userStore.verifyEmailCode(profileForm.email, profileForm.email_code)
    emailVerificationSuccess.value = true
    ElMessage.success('验证码验证成功')
  } catch (error: any) {
    console.error('验证码验证失败:', error)
    emailVerificationSuccess.value = false
    ElMessage.error(error.response?.data?.message || '验证码验证失败')
  } finally {
    loading.value = false
  }
}

// 取消修改邮箱
const cancelEmailModification = () => {
  profileForm.email = originalEmail.value
  profileForm.email_code = ''
  showEmailCodeField.value = false
  emailVerificationSuccess.value = false
  emailModificationInProgress.value = false
  
  // 重置表单验证状态
  if (profileFormRef.value) {
    profileFormRef.value.clearValidate('email')
  }
}

// 保存个人信息
const saveProfile = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  
  await formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 确保从表单获取最新的头像URL
        const currentAvatar = profileForm.avatar;
        console.log('当前头像URL:', currentAvatar);
        
        // 尝试从本地存储获取最新的头像URL
        console.log('用户存储中的头像URL:', userStore.avatar);
        
        // 获取最新头像URL (优先使用表单中的，再尝试用户存储中的)
        const avatarToSubmit = currentAvatar || userStore.avatar;
        console.log('即将提交的头像URL:', avatarToSubmit);
        
        // 检查头像URL是否为空
        if (!avatarToSubmit || avatarToSubmit === '') {
          console.log('头像URL为空，使用默认头像');
          // 不阻止表单提交，只是记录日志
        }
        
        // 确保资料表单中的avatar是最新的
        profileForm.avatar = avatarToSubmit;
        
        // 准备要提交的数据
        const updateData: any = {
          username: profileForm.username,
          email: profileForm.email,
          location: profileForm.location,
          avatar: profileForm.avatar
        }
        
        // 如果邮箱有变更，添加验证码
        if (profileForm.email !== originalEmail.value) {
          if (!profileForm.email_code) {
            ElMessage.warning('修改邮箱需要验证码')
            loading.value = false
            return
          }
          updateData.email_code = profileForm.email_code
        }
        
        console.log('提交更新的个人资料:', updateData);
        
        await userStore.updateProfile(updateData)
        
        // 更新原始邮箱
        originalEmail.value = profileForm.email
        // 隐藏验证码字段和清空验证码
        showEmailCodeField.value = false
        profileForm.email_code = ''
        emailVerificationSuccess.value = false
        emailModificationInProgress.value = false
        
        // 成功后强制刷新头像显示
        setTimeout(() => {
          refreshAvatar();
          console.log('保存成功后刷新头像');
        }, 100);
        
        ElMessage.success('个人资料更新成功')
      } catch (error: any) {
        console.error('个人资料更新错误:', error);
        
        // 显示更详细的错误信息
        if (error.response?.data?.errors?.email_code) {
          ElMessage.error(`验证码错误: ${error.response.data.errors.email_code.join(', ')}`);
        } else if (error.response?.data?.errors?.avatar) {
          ElMessage.error(`头像URL格式错误: ${error.response.data.errors.avatar.join(', ')}`);
        } else if (error.response?.data?.message) {
          ElMessage.error(error.response.data.message);
        } else {
          ElMessage.error(error.message || '更新失败，请稍后重试');
        }
      } finally {
        loading.value = false
      }
    }
  })
}

// 获取收藏列表
const getFavorites = async (page = 1) => {
  favoritesLoading.value = true
  try {
    // 使用userStore提供的方法获取收藏列表
    await userStore.fetchFavorites()
    // 从API获取完整的收藏详情，添加页码参数
    const response = await axios.get('/api/favorites/', {
      headers: { Authorization: `Token ${userStore.token}` },
      params: { page }
    })
    
    console.log('收藏列表响应数据:', response.data);
    
    // 处理不同结构的响应数据
    if (Array.isArray(response.data)) {
      favorites.value = response.data;
      // 如果是数组，则没有分页信息
      totalItems.value = response.data.length;
      totalPages.value = 1;
    } else if (response.data && Array.isArray(response.data.results)) {
      favorites.value = response.data.results;
      // 设置分页信息
      totalItems.value = response.data.count || response.data.results.length;
      totalPages.value = Math.ceil(totalItems.value / pageSize.value);
      currentPage.value = page;
    } else {
      // 处理其他类型的响应格式
      favorites.value = [];
      totalItems.value = 0;
      totalPages.value = 0;
      console.warn('收藏列表数据格式不符合预期:', response.data);
    }
  } catch (error) {
    ElMessage.error('获取收藏列表失败，请稍后重试')
    console.error('获取收藏列表错误:', error)
  } finally {
    favoritesLoading.value = false
  }
}

// 分页相关变量
const currentPage = ref(1)
const pageSize = ref(10)
const totalItems = ref(0)
const totalPages = ref(0)

// 处理页码变化
const handlePageChange = (page: number) => {
  currentPage.value = page
  getFavorites(page)
  
  // 更新URL中的页码参数，保持其他参数不变
  const query = { ...route.query, page: page.toString() }
  // 如果是第一页，移除页码参数
  if (page === 1) {
    delete query.page
  }
  router.push({ query })
}

// 移除收藏
const removeFavorite = async (scenicId: string) => {
  try {
    // 使用简单的确认替代ElMessageBox
    if(!confirm('确定取消收藏该景区吗？')) {
      return;
    }
    
    await userStore.toggleFavorite(scenicId)
    ElMessage.success('已取消收藏')
    
    // 从当前列表中移除
    favorites.value = favorites.value.filter(item => item.id !== scenicId)
    
    // 如果当前页面的收藏全部被移除，并且不是第一页，则回到上一页
    if (favorites.value.length === 0 && currentPage.value > 1) {
      currentPage.value -= 1
      getFavorites(currentPage.value)
      
      // 更新URL
      const query = { ...route.query, page: currentPage.value.toString() }
      if (currentPage.value === 1) {
        delete query.page
      }
      router.push({ query })
    } else if (totalItems.value > 0) {
      // 更新总数量和总页数
      totalItems.value -= 1
      totalPages.value = Math.ceil(totalItems.value / pageSize.value)
      
      // 如果当前页已经没有数据，但还有其他页，刷新当前页
      if (favorites.value.length === 0 && totalPages.value > 0) {
        getFavorites(currentPage.value)
      }
    }
  } catch (error) {
    ElMessage.error('取消收藏失败，请稍后重试')
  }
}

// 初始化
onMounted(() => {
  // 检查URL参数，如果有tab参数并且是'favorites'，则切换到收藏标签页
  if (route.query.tab === 'favorites') {
    activeTab.value = 'favorites'
    
    // 如果URL中包含页码，使用URL中的页码
    if (route.query.page) {
      currentPage.value = parseInt(route.query.page as string) || 1
    }
  }

  // 如果选择了收藏标签页，加载收藏列表
  if (activeTab.value === 'favorites') {
    getFavorites(currentPage.value)
  }
  
  // 确保头像URL正确格式化并加载
  if (profileForm.avatar) {
    console.log('初始化头像:', profileForm.avatar)
    // 延迟100ms刷新头像，确保DOM已经加载
    setTimeout(() => {
      refreshAvatar()
    }, 100)
  }
})

// 监听路由参数变化，处理从景区详情页返回的情况
watch(() => route.query.tab, (newVal) => {
  if (newVal === 'favorites') {
    activeTab.value = 'favorites'
    
    // 如果URL中包含页码，使用URL中的页码
    if (route.query.page) {
      currentPage.value = parseInt(route.query.page as string) || 1
    }
    
    // 如果收藏列表为空，重新加载
    if (favorites.value.length === 0) {
      getFavorites(currentPage.value)
    }
  }
}, { immediate: true })

// 切换标签页时加载数据
const handleTabClick = (tab: any) => {
  if (tab.props.name === 'favorites' && favorites.value.length === 0) {
    getFavorites(currentPage.value)
  }
  
  // 更新URL，便于刷新页面时保持在同一个标签页
  const query = { tab: tab.props.name }
  
  // 如果是收藏页且不是第一页，添加页码参数
  if (tab.props.name === 'favorites' && currentPage.value > 1) {
    Object.assign(query, { page: currentPage.value })
  }
  
  router.push({ query })
}

// 测试直接访问头像
const testDirectAccess = () => {
  if (!profileForm.avatar) {
    ElMessage.warning('没有头像路径可以测试')
    return
  }
  
  // 构建完整URL
  const fullUrl = getImageUrl(profileForm.avatar)
  console.log('测试直接访问头像URL:', fullUrl)
  
  // 在新窗口中打开图片URL
  window.open(fullUrl, '_blank')
  
  // 尝试预加载图片
  const img = new Image()
  img.onload = () => {
    console.log('头像图片加载成功!')
    ElMessage.success('头像图片加载成功!')
  }
  img.onerror = (e) => {
    console.error('头像图片加载失败:', e)
    ElMessage.error('头像图片加载失败，请检查网络控制台获取详细错误')
  }
  img.src = fullUrl
}

// 删除账户
const deleteAccountVisible = ref(false)
const deleteAccountPassword = ref('')
const deleteAccountLoading = ref(false)

const showDeleteAccountConfirm = () => {
  const result = confirm('删除账户将永久移除您的所有数据，包括个人信息和收藏记录，此操作不可撤销。是否确认继续？')
  if (result) {
    deleteAccountVisible.value = true
  }
}

const handleDeleteAccount = async () => {
  if (!deleteAccountPassword.value) {
    ElMessage.error('请输入密码以确认删除')
    return
  }
  
  deleteAccountLoading.value = true
  try {
    await userStore.deleteAccount(deleteAccountPassword.value)
    ElMessage.success('账户已成功删除')
    deleteAccountVisible.value = false
    // 重定向到登录页面
    router.push('/login')
  } catch (error: any) {
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('删除账户失败，请稍后重试')
    }
    console.error('删除账户失败:', error)
  } finally {
    deleteAccountLoading.value = false
  }
}

// 监听邮箱变更
watch(() => profileForm.email, (newEmail) => {
  if (newEmail !== originalEmail.value) {
    showEmailCodeField.value = true
    emailVerificationSuccess.value = false
    emailModificationInProgress.value = true
  } else {
    showEmailCodeField.value = false
    emailVerificationSuccess.value = false
    emailModificationInProgress.value = false
  }
}, { immediate: true })
</script>

<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span class="header-title">个人中心</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="profile-tabs">
        <!-- 个人信息标签页 -->
        <el-tab-pane label="个人信息" name="info">
          <div class="user-info-container">
            <div class="avatar-section">
              <div class="avatar-wrapper">
                <el-avatar 
                  :key="avatarKey"
                  :src="profileForm.avatar ? getImageUrl(profileForm.avatar) : 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" 
                  :size="120" 
                  class="user-avatar"
                >
                  <template #error>
                    <el-icon style="font-size: 30px; color: #909399;"><Picture /></el-icon>
                  </template>
                </el-avatar>
                <div class="avatar-overlay" v-if="uploading">
                  <el-icon class="loading-icon"><Loading /></el-icon>
                </div>
              </div>
              
              <!-- 头像操作按钮区域 -->
              <div class="avatar-buttons">
                <el-upload
                  class="avatar-uploader"
                  action="/api/users/upload-avatar/"
                  :headers="{ 'Authorization': `Token ${userStore.token}` }"
                  :show-file-list="false"
                  :auto-upload="true"
                  :on-success="handleAvatarSuccess"
                  :on-error="handleAvatarError"
                  :on-progress="handleAvatarUploadStart"
                  name="avatar"
                  accept="image/jpeg,image/png,image/gif"
                  :before-upload="(file: File) => { 
                    const isLt5M = file.size / 1024 / 1024 < 5;
                    if (!isLt5M) {
                      ElMessage.error('上传头像不能超过5MB!');
                      return false;
                    }
                    const isImage = ['image/jpeg', 'image/png', 'image/gif'].includes(file.type);
                    if (!isImage) {
                      ElMessage.error('只能上传JPG、PNG或GIF格式的图片!');
                      return false;
                    }
                    return true;
                  }"
                >
                  <el-button type="primary" size="small" :loading="uploading" class="avatar-btn upload-btn">
                    <el-icon class="el-icon--left"><Upload /></el-icon>更换头像
                  </el-button>
                </el-upload>
                
                <el-button type="info" size="small" @click="testDirectAccess" class="avatar-btn view-btn">
                  <el-icon class="el-icon--left"><View /></el-icon>查看头像
                </el-button>
              </div>
              
              <!-- 提示信息 -->
              <div class="el-upload__tip">
                支持JPG、PNG、GIF格式，不超过5MB
              </div>
            </div>
            
            <div class="info-form-section">
              <el-form
                ref="profileFormRef"
                :model="profileForm"
                :rules="rules"
                label-position="top"
                class="profile-form"
                status-icon
              >
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="profileForm.username" placeholder="请输入用户名" prefix-icon="User" />
                </el-form-item>
                
                <!-- 邮箱修改部分 - 优化版 -->
                <el-form-item label="邮箱" prop="email" class="email-form-item">
                  <!-- 邮箱输入框 -->
                  <div class="email-input-container">
                    <el-input 
                      v-model="profileForm.email" 
                      placeholder="请输入邮箱地址" 
                      @input="checkEmailChange" 
                      :disabled="emailVerificationSuccess"
                      prefix-icon="Message"
                    />
                    
                    <!-- 取消修改按钮 - 修改为按钮形式并调整样式 -->
                    <el-button
                      v-if="emailModificationInProgress"
                      @click="cancelEmailModification"
                      size="small"
                      class="cancel-btn"
                      type="danger"
                      plain
                    >
                      取消修改
                    </el-button>
                  </div>
                  
                  <!-- 修改状态提示 -->
                  <div v-if="emailModificationInProgress && !emailVerificationSuccess" class="email-change-tip warning">
                    <el-icon><WarningFilled /></el-icon>
                    <span>您正在修改邮箱，需要验证新邮箱才能保存</span>
                  </div>
                  
                  <!-- 验证成功提示 -->
                  <div v-if="emailVerificationSuccess" class="email-change-tip success">
                    <el-icon><CircleCheckFilled /></el-icon>
                    <span>新邮箱验证成功，请点击保存修改按钮完成修改</span>
                  </div>
                </el-form-item>
                
                <!-- 验证码部分 -->
                <el-form-item 
                  v-if="showEmailCodeField" 
                  label="验证码" 
                  prop="email_code" 
                  class="verification-form-item"
                  :class="{'is-success': emailVerificationSuccess}"
                >
                  <div class="verify-code-input">
                    <el-input 
                      v-model="profileForm.email_code" 
                      placeholder="请输入验证码" 
                      :disabled="emailVerificationSuccess"
                      maxlength="6"
                      show-word-limit
                      class="code-input"
                    >
                      <template #prefix>
                        <el-icon><Key /></el-icon>
                      </template>
                      <template #suffix>
                        <el-icon v-if="emailVerificationSuccess" color="#67c23a"><CircleCheck /></el-icon>
                      </template>
                    </el-input>
                    <el-button 
                      type="primary" 
                      :disabled="emailCodeSending || emailCodeCountdown > 0 || emailVerificationSuccess" 
                      @click="sendEmailCode"
                      class="send-code-btn"
                    >
                      {{ emailCodeCountdown > 0 ? `${emailCodeCountdown}秒后重试` : '获取验证码' }}
                    </el-button>
                  </div>
                  
                  <!-- 验证码验证按钮 - 调整样式使其与获取验证码按钮一致 -->
                  <div class="verify-code-actions">
                    <el-button 
                      type="success" 
                      :disabled="!profileForm.email_code || profileForm.email_code.length !== 6 || emailVerificationSuccess"
                      :class="{'is-verified': emailVerificationSuccess}"
                      @click="verifyEmailCode"
                      class="verify-btn"
                    >
                      <el-icon v-if="emailVerificationSuccess"><Check /></el-icon>
                      {{ emailVerificationSuccess ? '已验证' : '验证' }}
                    </el-button>
                  </div>
                  
                  <div class="verify-code-tip">
                    <el-alert
                      type="info"
                      :closable="false"
                      show-icon
                    >
                      <template #title>修改邮箱说明</template>
                      <ol class="verification-steps">
                        <li>验证码已发送到新邮箱，有效期10分钟</li>
                        <li>请检查新邮箱的收件箱和垃圾邮件文件夹</li>
                        <li>验证成功后点击下方保存按钮完成修改</li>
                      </ol>
                    </el-alert>
                  </div>
                </el-form-item>
                
                <el-form-item label="所在地" prop="location">
                  <el-input 
                    v-model="profileForm.location" 
                    placeholder="如：北京市海淀区" 
                    prefix-icon="Location"
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button 
                    type="primary" 
                    @click="saveProfile(profileFormRef)" 
                    :loading="loading"
                    class="save-btn"
                    :disabled="emailModificationInProgress && !emailVerificationSuccess"
                  >
                    <el-icon class="el-icon--left"><Check /></el-icon>保存修改
                  </el-button>
                </el-form-item>
                
                <!-- 账户安全区域 -->
                <div class="account-security-section">
                  <h3 class="section-title">账户安全</h3>
                  <el-button 
                    type="danger" 
                    @click="showDeleteAccountConfirm"
                    plain
                    class="delete-btn"
                  >
                    <el-icon class="el-icon--left"><Delete /></el-icon>删除账户
                  </el-button>
                </div>
              </el-form>
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 收藏列表标签页 -->
        <el-tab-pane label="我的收藏" name="favorites">
          <el-empty v-if="favorites.length === 0 && !favoritesLoading" description="暂无收藏内容">
            <template #description>
              <p>您还没有收藏任何景区</p>
              <el-button type="primary" @click="$router.push('/dashboard/search')">
                去浏览景区
              </el-button>
            </template>
          </el-empty>
          
          <div v-loading="favoritesLoading" class="favorites-container">
            <el-card 
              v-for="item in favorites" 
              :key="item.id" 
              class="favorite-item"
              shadow="hover"
            >
              <div class="favorite-content">
                <el-image 
                  :src="getImageUrl(item.image)"
                  fit="cover"
                  class="scenic-image"
                  loading="lazy"
                >
                  <template #error>
                    <img :src="defaultImage" class="scenic-image" alt="默认景区图片" />
                  </template>
                </el-image>
                
                <div class="scenic-info">
                  <h3 class="scenic-name">{{ item.name }}</h3>
                  <div class="scenic-location">
                    <el-icon><Location /></el-icon>
                    <span>{{ item.province }} {{ item.city }}</span>
                  </div>
                  <div class="scenic-level" v-if="item.level">
                    <el-tag size="small" type="info" effect="plain" class="disabled-tag">{{ item.level }}</el-tag>
                  </div>
                </div>
                
                <div class="actions">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="$router.push(`/dashboard/scenic/${item.id}?from=favorites`)"
                  >
                    查看详情
                  </el-button>
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="removeFavorite(item.id)"
                  >
                    取消收藏
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 分页组件 -->
          <div class="pagination-container" v-if="totalPages > 1">
            <el-pagination
              background
              layout="prev, pager, next"
              :total="totalItems"
              :page-size="pageSize"
              :current-page="currentPage"
              @current-change="handlePageChange"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 删除账户确认对话框 -->
    <el-dialog
      v-model="deleteAccountVisible"
      title="确认删除账户"
      width="400px"
      :close-on-click-modal="false"
      :close-on-press-escape="!deleteAccountLoading"
      center
      align-center
      class="delete-account-dialog"
    >
      <div class="delete-account-content">
        <el-icon class="warning-icon"><WarningFilled /></el-icon>
        <p class="delete-warning">删除账户后将无法恢复，所有数据将被永久删除。</p>
        <p>请输入您的密码以确认删除账户：</p>
        <el-input
          v-model="deleteAccountPassword"
          type="password"
          placeholder="请输入密码"
          show-password
          class="delete-account-input"
        />
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="deleteAccountVisible = false" :disabled="deleteAccountLoading">取消</el-button>
          <el-button
            type="danger"
            @click="handleDeleteAccount"
            :loading="deleteAccountLoading"
          >
            确认删除
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.profile-container {
  min-height: 100%;
  padding: 20px 0;
}

.profile-card {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.profile-tabs :deep(.el-tabs__nav) {
  border-radius: 4px;
}

.profile-tabs :deep(.el-tabs__item) {
  transition: all 0.3s ease;
}

.profile-tabs :deep(.el-tabs__item.is-active) {
  font-weight: 600;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 8px;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  position: relative;
  padding-left: 10px;
}

.header-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background-color: #409eff;
  border-radius: 2px;
}

.user-info-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  padding: 25px;
  background-color: #f8f9fb;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.avatar-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
}

.user-avatar {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border: 4px solid #fff;
  transition: all 0.3s ease;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
}

.loading-icon {
  font-size: 24px;
  color: #fff;
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.avatar-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
  width: 100%;
}

.avatar-uploader {
  display: inline-block;
}

.avatar-btn {
  transition: all 0.3s;
  border-radius: 4px;
}

.avatar-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.view-btn {
  background-color: #f4f4f5;
  color: #606266;
}

.view-btn:hover {
  background-color: #e9e9eb;
}

.el-upload__tip {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
  text-align: center;
  width: 100%;
}

.info-form-section {
  margin-top: 10px;
}

.profile-form .el-form-item {
  margin-bottom: 22px;
  max-width: 100%;
}

.profile-form .el-input,
.profile-form .el-select,
.save-btn {
  width: 100%;
}

.save-btn {
  width: 100%;
  margin-top: 10px;
  height: 42px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 1px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.favorites-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.favorite-item {
  height: 100%;
  transition: all 0.3s;
  border-radius: 8px;
  overflow: hidden;
}

.favorite-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.favorite-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.scenic-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 12px;
  transition: all 0.5s ease;
}

.scenic-image:hover {
  transform: scale(1.03);
}

.image-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  color: #909399;
  font-size: 24px;
}

.scenic-info {
  margin: 10px 0;
  flex: 1;
}

.scenic-name {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.scenic-location {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #606266;
  font-size: 14px;
  margin-bottom: 10px;
}

.scenic-level {
  margin-top: 8px;
}

.disabled-tag {
  color: #909399;
  background-color: #f4f4f5;
  border-color: #e9e9eb;
  cursor: default;
}

.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}

.delete-account-dialog :deep(.el-dialog__header) {
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.delete-account-content {
  text-align: center;
  padding: 10px 0;
}

.warning-icon {
  font-size: 48px;
  color: #e6a23c;
  margin-bottom: 15px;
}

.delete-warning {
  color: #e6a23c;
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 20px;
}

.delete-account-input {
  margin: 20px 0;
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding-top: 10px;
}

.pagination-container {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 15px 0;
  grid-column: 1 / -1; /* 确保在网格布局中占据所有列 */
}

.verify-code-input {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.verify-code-input .code-input {
  flex: 1;
}

.send-code-btn {
  white-space: nowrap;
  margin-left: 10px;
  height: 40px;
  min-width: 100px;
}

.verify-code-actions {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 15px;
}

.verify-btn {
  height: 40px;
  min-width: 100px;
}

.verification-form-item {
  margin-bottom: 25px;
  padding: 15px;
  background-color: #f8f9fd;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.verification-form-item.is-success {
  background-color: #f0f9eb;
  border: 1px solid rgba(103, 194, 58, 0.2);
}

.verify-code-tip {
  margin-top: 5px;
}

.verification-steps {
  padding-left: 20px;
  margin: 10px 0 5px;
}

.verification-steps li {
  margin-bottom: 6px;
  font-size: 13px;
}

.email-form-item {
  margin-bottom: 22px;
}

.email-input-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.email-input-container .el-input {
  flex: 1;
}

.cancel-btn {
  border-radius: 4px;
  transition: all 0.3s ease;
  min-width: 90px;
  margin-left: 10px;
  height: 32px;
}

.cancel-btn:hover {
  background-color: rgba(245, 108, 108, 0.1);
}

.email-change-tip {
  margin-top: 8px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.warning {
  color: #e6a23c;
}

.success {
  color: #67c23a;
}

.account-security-section {
  margin-top: 30px; 
  border-top: 1px solid #ebeef5; 
  padding-top: 20px;
}

.section-title {
  font-size: 16px; 
  color: #303133; 
  margin-bottom: 16px;
  position: relative;
  padding-left: 10px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 14px;
  background-color: #f56c6c;
  border-radius: 2px;
}

.delete-btn {
  transition: all 0.3s ease;
}

.delete-btn:hover {
  background-color: rgba(245, 108, 108, 0.1);
  transform: translateY(-2px);
}

.is-verified {
  pointer-events: none;
}

@media (min-width: 768px) {
  .user-info-container {
    flex-direction: row;
    align-items: flex-start;
  }
  
  .avatar-section {
    width: 280px;
  }
  
  .info-form-section {
    flex: 1;
    margin-top: 0;
    margin-left: 30px;
  }
}

@media (max-width: 767px) {
  .avatar-section {
    margin-bottom: 20px;
  }
  
  .email-input-container {
    align-items: flex-start;
  }
  
  .cancel-btn {
    margin-top: 5px;
  }
  
  .verify-code-input {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .send-code-btn {
    margin-left: 0;
    margin-top: 10px;
    width: 100%;
  }
  
  .verify-btn {
    width: 100%;
  }
}
</style> 