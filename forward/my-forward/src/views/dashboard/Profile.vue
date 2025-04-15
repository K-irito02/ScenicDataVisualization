<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import axios from 'axios'
import { Check, Upload, Picture, Location } from '@element-plus/icons-vue'

const userStore = useUserStore()
const activeTab = ref('info')
const uploading = ref(false)
const loading = ref(false)
const favoritesLoading = ref(false)
const favorites = ref<any[]>([])

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

// 上传头像
const handleAvatarUpload = (options: any) => {
  uploading.value = true
  
  // 从el-upload的http-request选项获取文件
  const file = options.file
  
  // 检查文件是否有效
  if (!file) {
    ElMessage.error('文件无效，请重新选择');
    uploading.value = false;
    return false;
  }
  
  console.log('准备上传文件:', file.name, file.type, file.size);
  
  // 创建FormData对象上传文件
  const formData = new FormData();
  formData.append('avatar', file);
  
  // 上传到服务器
  axios({
    method: 'post',
    url: '/api/users/upload-avatar/',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
      'Authorization': `Token ${userStore.token}`
    }
  }).then(response => {
    console.log('头像上传成功响应:', response.data);
    
    // 确保响应中包含头像URL
    if (!response.data.avatar_url) {
      throw new Error('服务器未返回头像URL');
    }
    
    // 获取头像相对路径 - 使用服务器返回的原始路径
    let avatarPath = response.data.avatar_url;
    console.log('服务器返回的头像路径:', avatarPath);
    
    // 确保路径以斜杠开头
    if (!avatarPath.startsWith('/')) {
      avatarPath = '/' + avatarPath;
    }
    
    // 保存相对路径用于资料更新
    profileForm.avatar = avatarPath;
    
    // 为了前端显示，构建完整URL
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    let displayUrl = avatarPath;
    
    // 构建完整URL进行显示
    if (!displayUrl.startsWith('http')) {
      // 去除URL中可能的双斜杠
      if (displayUrl.startsWith('/') && baseUrl.endsWith('/')) {
        displayUrl = `${baseUrl}${displayUrl.substring(1)}`;
      } else if (!displayUrl.startsWith('/') && !baseUrl.endsWith('/')) {
        displayUrl = `${baseUrl}/${displayUrl}`;
      } else {
        displayUrl = `${baseUrl}${displayUrl}`;
      }
    }
    
    console.log('显示用的完整头像URL:', displayUrl);
    
    // 更新用户存储中的头像 - 使用相对路径
    userStore.setUserInfo({ avatar: avatarPath });
    ElMessage.success('头像上传成功');
    
    // 调用上传成功回调
    if (options.onSuccess) {
      options.onSuccess(response.data);
    }
  }).catch(error => {
    console.error('头像上传完整错误:', error);
    if (error.response) {
      console.error('服务器响应:', error.response.data);
    }
    ElMessage.error(`头像上传失败: ${error.message || '未知错误'}`);
    
    // 调用上传失败回调
    if (options.onError) {
      options.onError(error);
    }
  }).finally(() => {
    uploading.value = false;
  });
}

// 保存个人信息
const saveProfile = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  
  await formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
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
const getFavorites = async () => {
  favoritesLoading.value = true
  try {
    // 使用userStore提供的方法获取收藏列表
    await userStore.fetchFavorites()
    // 从API获取完整的收藏详情
    const response = await axios.get('/api/favorites/', {
      headers: { Authorization: `Token ${userStore.token}` }
    })
    
    console.log('收藏列表响应数据:', response.data);
    
    // 处理不同结构的响应数据
    if (Array.isArray(response.data)) {
      favorites.value = response.data;
    } else if (response.data && Array.isArray(response.data.results)) {
      favorites.value = response.data.results;
    } else {
      // 处理其他类型的响应格式
      favorites.value = [];
      console.warn('收藏列表数据格式不符合预期:', response.data);
    }
  } catch (error) {
    ElMessage.error('获取收藏列表失败，请稍后重试')
    console.error('获取收藏列表错误:', error)
  } finally {
    favoritesLoading.value = false
  }
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
    
    // 刷新收藏列表
    favorites.value = favorites.value.filter(item => item.id !== scenicId)
  } catch (error) {
    ElMessage.error('取消收藏失败，请稍后重试')
  }
}

// 初始化
onMounted(() => {
  // 如果选择了收藏标签页，加载收藏列表
  if (activeTab.value === 'favorites') {
    getFavorites()
  }
})

// 切换标签页时加载数据
const handleTabClick = (tab: any) => {
  if (tab.props.name === 'favorites' && favorites.value.length === 0) {
    getFavorites()
  }
}

// 用户信息
const userInfo = computed(() => {
  return userStore.getUserInfo()
})
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
                :src="profileForm.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" 
                :size="120" 
                class="user-avatar"
              >
                <template #error>
                  <el-icon style="font-size: 30px; color: #909399;"><Picture /></el-icon>
                </template>
              </el-avatar>
              <div class="avatar-upload-container">
                <el-upload
                  class="avatar-uploader"
                  action=""
                  :show-file-list="false"
                  :auto-upload="false"
                  :http-request="handleAvatarUpload"
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
                  <el-button type="primary" size="small" :loading="uploading" class="upload-btn">
                    <el-icon class="el-icon--left"><Upload /></el-icon>更换头像
                  </el-button>
                  <div class="el-upload__tip">
                    支持 JPG、PNG、GIF 格式，不超过 5MB
                  </div>
                </el-upload>
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
                  :src="item.image" 
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
                    @click="$router.push(`/dashboard/scenic/${item.id}`)"
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
        </el-tab-pane>
      </el-tabs>
    </el-card>
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

.avatar-upload-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 10px;
}

.avatar-uploader {
  margin-top: 5px;
}

.upload-btn {
  transition: all 0.3s;
}

.upload-btn:hover {
  transform: translateY(-2px);
}

.el-upload__tip {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
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