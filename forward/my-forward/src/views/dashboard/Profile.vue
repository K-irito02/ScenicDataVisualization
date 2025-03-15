<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import axios from 'axios'

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
const handleAvatarUpload = (file: File) => {
  uploading.value = true
  
  // 这里应该是上传到服务器的逻辑
  // 模拟上传过程
  const reader = new FileReader()
  reader.readAsDataURL(file)
  reader.onload = () => {
    profileForm.avatar = reader.result as string
    uploading.value = false
    ElMessage.success('头像上传成功')
  }
  
  return false // 阻止 el-upload 自动上传
}

// 保存个人信息
const saveProfile = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  
  await formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.updateProfile({
          username: profileForm.username,
          email: profileForm.email,
          location: profileForm.location,
          avatar: profileForm.avatar
        })
        ElMessage.success('个人资料更新成功')
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '更新失败，请稍后重试')
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
    const response = await axios.get('/api/favorites/list/', {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    favorites.value = response.data
  } catch (error) {
    ElMessage.error('获取收藏列表失败，请稍后重试')
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
          <span>个人中心</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <!-- 个人信息标签页 -->
        <el-tab-pane label="个人信息" name="info">
          <div class="user-info-container">
            <div class="avatar-section">
              <el-avatar 
                :src="profileForm.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" 
                :size="100" 
              />
              <el-upload
                class="avatar-uploader"
                action=""
                :show-file-list="false"
                :auto-upload="false"
                :on-change="handleAvatarUpload"
              >
                <el-button type="primary" size="small" :loading="uploading">
                  更换头像
                </el-button>
              </el-upload>
            </div>
            
            <div class="info-form-section">
              <el-form
                ref="profileFormRef"
                :model="profileForm"
                :rules="rules"
                label-position="top"
              >
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="profileForm.username" />
                </el-form-item>
                
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="profileForm.email" />
                </el-form-item>
                
                <el-form-item label="所在地" prop="location">
                  <el-input v-model="profileForm.location" placeholder="如：北京市海淀区" />
                </el-form-item>
                
                <el-form-item>
                  <el-button 
                    type="primary" 
                    @click="saveProfile(profileFormRef)" 
                    :loading="loading"
                  >
                    保存修改
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 收藏列表标签页 -->
        <el-tab-pane label="我的收藏" name="favorites">
          <el-empty v-if="favorites.length === 0 && !favoritesLoading" description="暂无收藏内容" />
          
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
}

.avatar-uploader {
  margin-top: 5px;
}

.info-form-section {
  margin-top: 20px;
}

.favorites-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.favorite-item {
  height: 100%;
}

.favorite-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.scenic-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
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
}

.scenic-location {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #606266;
  font-size: 14px;
  margin-bottom: 5px;
}

.scenic-level {
  margin-top: 5px;
}

.actions {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

@media (min-width: 768px) {
  .user-info-container {
    flex-direction: row;
    align-items: flex-start;
  }
  
  .avatar-section {
    width: 200px;
  }
  
  .info-form-section {
    flex: 1;
    margin-top: 0;
    margin-left: 40px;
  }
}
</style> 