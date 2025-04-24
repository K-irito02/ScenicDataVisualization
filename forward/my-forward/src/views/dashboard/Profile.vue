<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import axios from 'axios'
import { Check, Upload, Picture, Location, Delete } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const activeTab = ref('info')
const uploading = ref(false)
const loading = ref(false)
const favoritesLoading = ref(false)
const favorites = ref<any[]>([])
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 个人信息表单
const profileForm = reactive({
  username: userStore.username,
  email: userStore.email,
  location: userStore.location,
  avatar: userStore.avatar
})

const profileFormRef = ref<FormInstance>()

const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
})

// 获取完整的头像URL
const getFullAvatarUrl = (avatar: string) => {
  if (!avatar) return ''
  
  // 添加时间戳防止浏览器缓存头像
  const timestamp = new Date().getTime()
  
  // 已经是完整URL的情况
  if (avatar.startsWith('http')) {
    return avatar.includes('?') ? `${avatar}&_t=${timestamp}` : `${avatar}?_t=${timestamp}`
  }
  
  // 处理媒体文件路径
  // 确保在开发环境中使用后端服务器URL
  let baseUrl = apiBaseUrl
  
  // 针对媒体文件路径，确保使用apiBaseUrl
  let url = ''
  if (avatar.startsWith('/media/')) {
    // 如果是媒体文件路径，直接使用apiBaseUrl
    url = `${baseUrl}${avatar}`
  } else if (avatar.startsWith('media/')) {
    // 如果是不带前导斜杠的媒体路径
    url = `${baseUrl}/${avatar}`
  } else {
    // 其他路径
    url = baseUrl + (avatar.startsWith('/') ? avatar : `/${avatar}`)
  }
  
  // 添加时间戳
  return url.includes('?') ? `${url}&_t=${timestamp}` : `${url}?_t=${timestamp}`
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
        
        console.log('提交更新的个人资料:', {
          username: profileForm.username,
          email: profileForm.email,
          location: profileForm.location,
          avatar: profileForm.avatar
        });
        
        await userStore.updateProfile({
          username: profileForm.username,
          email: profileForm.email,
          location: profileForm.location,
          avatar: profileForm.avatar
        })
        
        // 成功后强制刷新头像显示
        setTimeout(() => {
          refreshAvatar();
          console.log('保存成功后刷新头像');
        }, 100);
        
        ElMessage.success('个人资料更新成功')
      } catch (error: any) {
        console.error('个人资料更新错误:', error);
        
        // 显示更详细的错误信息
        if (error.response?.data?.errors?.avatar) {
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
  const fullUrl = getFullAvatarUrl(profileForm.avatar)
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
</script>

<template>
  <div class="profile-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="header-title">个人中心</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <!-- 个人信息标签页 -->
        <el-tab-pane label="个人信息" name="info">
          <div class="user-info-container">
            <div class="avatar-section">
              <el-avatar 
                :key="avatarKey"
                :src="profileForm.avatar ? getFullAvatarUrl(profileForm.avatar) : 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" 
                :size="120" 
                class="user-avatar"
              >
                <template #error>
                  <el-icon style="font-size: 30px; color: #909399;"><Picture /></el-icon>
                </template>
              </el-avatar>
              
              <!-- 头像操作按钮区域 -->
              <div class="avatar-buttons">
                <el-button type="primary" size="small" @click="testDirectAccess" class="avatar-btn">
                  查看头像
                </el-button>
                
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
              >
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="profileForm.username" placeholder="请输入用户名" />
                </el-form-item>
                
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="profileForm.email" placeholder="请输入邮箱地址" />
                </el-form-item>
                
                <el-form-item label="所在地" prop="location">
                  <el-input v-model="profileForm.location" placeholder="如：北京市海淀区" />
                </el-form-item>
                
                <el-form-item>
                  <el-button 
                    type="primary" 
                    @click="saveProfile(profileFormRef)" 
                    :loading="loading"
                    class="save-btn"
                  >
                    <el-icon class="el-icon--left"><Check /></el-icon>保存修改
                  </el-button>
                </el-form-item>
                
                <!-- 账户安全区域 -->
                <div style="margin-top: 30px; border-top: 1px solid #ebeef5; padding-top: 20px;">
                  <h3 style="font-size: 16px; color: #303133; margin-bottom: 16px;">账户安全</h3>
                  <el-button 
                    type="danger" 
                    @click="showDeleteAccountConfirm"
                    plain
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
                  :src="item.image || '/static/images/default-scenic.jpg'" 
                  fit="cover"
                  class="scenic-image"
                >
                  <template #error>
                    <div class="image-placeholder">
                      <el-icon><picture /></el-icon>
                    </div>
                  </template>
                </el-image>
                
                <div class="scenic-info">
                  <h3 class="scenic-name">{{ item.name }}</h3>
                  <div class="scenic-location">
                    <el-icon><location /></el-icon>
                    <span>{{ item.province }} {{ item.city }}</span>
                  </div>
                  <div class="scenic-level" v-if="item.level">
                    <el-tag size="small">{{ item.level }}</el-tag>
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
    >
      <div>
        <p>请输入您的密码以确认删除账户：</p>
        <el-input
          v-model="deleteAccountPassword"
          type="password"
          placeholder="请输入密码"
          show-password
          class="delete-account-input"
        />
        <p class="dialog-warning">
          提示：账户删除后将无法恢复，所有数据将被永久删除。
        </p>
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
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.user-info-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.user-avatar {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border: 4px solid #fff;
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
}

.avatar-btn:hover {
  transform: translateY(-2px);
}

.el-upload__tip {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
  text-align: center;
  width: 100%;
}

.info-form-section {
  margin-top: 20px;
}

.profile-form .el-form-item {
  margin-bottom: 22px;
}

.save-btn {
  width: 100%;
  margin-top: 10px;
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
}

.favorite-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
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

.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}

.delete-account-input {
  margin: 20px 0;
  width: 100%;
}

.dialog-warning {
  color: #e6a23c;
  font-size: 14px;
  margin-top: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 15px 0;
  grid-column: 1 / -1; /* 确保在网格布局中占据所有列 */
}

@media (min-width: 768px) {
  .user-info-container {
    flex-direction: row;
    align-items: flex-start;
  }
  
  .avatar-section {
    width: 250px;
  }
  
  .info-form-section {
    flex: 1;
    margin-top: 0;
    margin-left: 30px;
  }
}
</style> 