<template>
  <div class="users-container">
    <card-container title="用户管理">
      <template #actions>
        <div class="action-buttons">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户名/邮箱"
            clearable
            prefix-icon="Search"
            style="width: 220px"
            @input="handleSearch"
          />
        </div>
      </template>
      
      <div class="statistics-cards">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="statistics-card">
              <div class="statistics-card-content">
                <div class="statistics-value">{{ statistics.totalUsers }}</div>
                <div class="statistics-label">总用户数</div>
              </div>
              <div class="statistics-icon">
                <el-icon><User /></el-icon>
              </div>
            </div>
          </el-col>
          
          <el-col :span="6">
            <div class="statistics-card">
              <div class="statistics-card-content">
                <div class="statistics-value">{{ statistics.activeUsers }}</div>
                <div class="statistics-label">今日活跃</div>
              </div>
              <div class="statistics-icon green">
                <el-icon><UserFilled /></el-icon>
              </div>
            </div>
          </el-col>
          
          <el-col :span="6">
            <div class="statistics-card">
              <div class="statistics-card-content">
                <div class="statistics-value">{{ statistics.newUsers }}</div>
                <div class="statistics-label">今日新增</div>
              </div>
              <div class="statistics-icon blue">
                <el-icon><Plus /></el-icon>
              </div>
            </div>
          </el-col>
          
          <el-col :span="6">
            <div class="statistics-card">
              <div class="statistics-card-content">
                <div class="statistics-value">{{ statistics.disabledUsers }}</div>
                <div class="statistics-label">禁用用户</div>
              </div>
              <div class="statistics-icon red">
                <el-icon><CircleClose /></el-icon>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <div class="users-table">
        <el-table
          v-loading="loading"
          :data="filteredUsers"
          border
          style="width: 100%"
          row-key="id"
        >
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" width="150" />
          <el-table-column prop="email" label="邮箱" width="200" />
          <el-table-column label="头像" width="80">
            <template #default="scope">
              <el-avatar :src="scope.row.avatar || defaultAvatar" :size="40"></el-avatar>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="所在地" width="120" />
          <el-table-column prop="registerTime" label="注册时间" width="180" />
          <el-table-column prop="lastLoginTime" label="最后登录时间" width="180" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
                {{ scope.row.status === 'active' ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" fixed="right" width="150">
            <template #default="scope">
              <el-button
                type="primary"
                circle
                size="small"
                @click="handleViewUser(scope.row)"
              >
                <el-icon><View /></el-icon>
              </el-button>
              <el-button
                :type="scope.row.status === 'active' ? 'danger' : 'success'"
                circle
                size="small"
                @click="handleToggleStatus(scope.row)"
              >
                <el-icon>
                  <component :is="scope.row.status === 'active' ? CircleClose : CircleCheck" />
                </el-icon>
              </el-button>
              <el-button
                type="info"
                circle
                size="small"
                @click="handleEditUser(scope.row)"
              >
                <el-icon><Edit /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            background
            layout="total, sizes, prev, pager, next, jumper"
            :current-page="currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pageSize"
            :total="totalUsers"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </card-container>
    
    <!-- 查看用户详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="用户详情"
      width="500px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="用户ID">{{ currentUser.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ currentUser.email }}</el-descriptions-item>
        <el-descriptions-item label="所在地">{{ currentUser.location }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ currentUser.registerTime }}</el-descriptions-item>
        <el-descriptions-item label="最后登录">{{ currentUser.lastLoginTime }}</el-descriptions-item>
        <el-descriptions-item label="收藏数量">{{ currentUser.favorites || 0 }}</el-descriptions-item>
        <el-descriptions-item label="搜索次数">{{ currentUser.searches || 0 }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentUser.status === 'active' ? 'success' : 'danger'">
            {{ currentUser.status === 'active' ? '正常' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
          <el-button 
            :type="currentUser.status === 'active' ? 'danger' : 'success'"
            @click="handleToggleStatus(currentUser, true)"
          >
            {{ currentUser.status === 'active' ? '禁用用户' : '启用用户' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑用户"
      width="500px"
    >
      <el-form :model="editForm" label-width="100px" :rules="editRules" ref="editFormRef">
        <el-form-item label="用户ID" prop="id">
          <el-input v-model="editForm.id" disabled />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="所在地" prop="location">
          <el-input v-model="editForm.location" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="editForm.status" placeholder="请选择状态">
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEdit">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed, onMounted } from 'vue'
import CardContainer from '@/components/common/CardContainer.vue'
import { User, UserFilled, Edit, View, Plus, CircleClose, CircleCheck } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ElMessageBox from 'element-plus/es/components/message-box/index'
import type { FormInstance } from 'element-plus'
import { getUsers, toggleUserStatus, updateUser, getUserStats } from '@/api/admin'

export default defineComponent({
  name: 'Users',
  components: {
    CardContainer,
    User,
    UserFilled,
    Edit,
    View,
    Plus,
    CircleClose,
    CircleCheck
  },
  setup() {
    const loading = ref(false)
    const users = ref<any[]>([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalUsers = ref(0)
    const searchQuery = ref('')
    const dialogVisible = ref(false)
    const editDialogVisible = ref(false)
    const currentUser = ref<any>({})
    const editFormRef = ref<FormInstance>()
    const defaultAvatar = '/images/default-avatar.jpg'
    
    // 统计数据
    const statistics = reactive({
      totalUsers: 0,
      activeUsers: 0,
      newUsers: 0,
      disabledUsers: 0
    })
    
    // 编辑表单
    const editForm = reactive({
      id: '',
      username: '',
      email: '',
      location: '',
      status: 'active'
    })
    
    // 编辑表单校验规则
    const editRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '长度在3到20个字符', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ]
    }
    
    // 根据搜索过滤用户
    const filteredUsers = computed(() => {
      if (!searchQuery.value) return users.value
      
      const query = searchQuery.value.toLowerCase()
      return users.value.filter(user => 
        user.username.toLowerCase().includes(query) || 
        user.email.toLowerCase().includes(query)
      )
    })
    
    // 获取用户数据
    const fetchUsers = async () => {
      loading.value = true;
      
      try {
        // 从API获取用户数据
        const response = await getUsers({
          page: currentPage.value,
          pageSize: pageSize.value
        });
        
        // 更新用户数据和总数
        users.value = response.data.data;
        totalUsers.value = response.data.total;
        
        // 更新统计数据
        statistics.totalUsers = totalUsers.value;
        // 如果API返回了活跃用户数和新增用户数，则直接使用
        if ('active_users_today' in response.data) {
          statistics.activeUsers = response.data.active_users_today;
        } else {
          // 否则使用前端计算的逻辑（作为备选）
          statistics.activeUsers = users.value.filter(user => {
            if (!user.lastLoginTime) return false;
            const loginDate = new Date(user.lastLoginTime);
            const today = new Date();
            return loginDate.getDate() === today.getDate() &&
                   loginDate.getMonth() === today.getMonth() &&
                   loginDate.getFullYear() === today.getFullYear();
          }).length;
        }
        
        statistics.disabledUsers = users.value.filter(user => user.status === 'disabled').length;
        
        if ('new_users_today' in response.data) {
          statistics.newUsers = response.data.new_users_today;
        } else {
          // 备选的前端计算逻辑
          statistics.newUsers = users.value.filter(user => {
            if (!user.registerTime) return false;
            const registerDate = new Date(user.registerTime);
            const today = new Date();
            return registerDate.getDate() === today.getDate() &&
                   registerDate.getMonth() === today.getMonth() &&
                   registerDate.getFullYear() === today.getFullYear();
          }).length;
        }
      } catch (error) {
        console.error('获取用户数据失败:', error);
        ElMessage.error('获取用户数据失败');
      } finally {
        loading.value = false;
      }
    };
    
    // 处理搜索
    const handleSearch = () => {
      // 在实际应用中，可能需要重新请求API进行搜索
      // 在这个模拟中，我们直接使用计算属性进行客户端筛选
    }
    
    // 处理页码变化
    const handleCurrentChange = (page: number) => {
      currentPage.value = page
      fetchUsers()
    }
    
    // 处理每页条数变化
    const handleSizeChange = (size: number) => {
      pageSize.value = size
      currentPage.value = 1
      fetchUsers()
    }
    
    // 查看用户详情
    const handleViewUser = async (user: any) => {
      currentUser.value = { ...user }
      dialogVisible.value = true
      
      try {
        // 获取用户统计信息
        const response = await getUserStats(user.id)
        if (response && response.data) {
          // 更新用户详情中的统计数据
          currentUser.value.favorites = response.data.favorites || 0
          currentUser.value.searches = response.data.searches || 0
        }
      } catch (error) {
        console.error('获取用户统计信息失败:', error)
        ElMessage.warning('获取用户统计信息失败')
      }
    }
    
    // 切换用户状态
    const handleToggleStatus = async (user: any, fromDialog = false) => {
      try {
        const action = user.status === 'active' ? '禁用' : '启用'
        
        await ElMessageBox.confirm(
          `确定要${action}用户 "${user.username}" 吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        try {
          // 调用API切换用户状态
          const response = await toggleUserStatus(user.id)
          
          // 更新本地数据
          const updatedUser = response.data.user
          const targetUser = users.value.find(u => u.id === user.id)
          if (targetUser) {
            targetUser.status = updatedUser.status
            
            // 如果是从对话框操作，也更新当前查看的用户
            if (fromDialog) {
              currentUser.value.status = updatedUser.status
            }
            
            // 更新统计数据
            statistics.activeUsers = users.value.filter(u => u.status === 'active').length
            statistics.disabledUsers = users.value.filter(u => u.status === 'disabled').length
          }
          
          ElMessage.success(response.data.message || `${action}用户成功`)
        } catch (error: any) {
          // 处理API错误
          console.error('切换用户状态失败:', error)
          ElMessage.error(error.response?.data?.error || `${action}用户失败`)
        }
      } catch (error) {
        // 用户取消操作，不做处理
      }
    }
    
    // 编辑用户
    const handleEditUser = (user: any) => {
      editForm.id = user.id
      editForm.username = user.username
      editForm.email = user.email
      editForm.location = user.location
      editForm.status = user.status
      
      editDialogVisible.value = true
    }
    
    // 提交编辑
    const submitEdit = async () => {
      if (!editFormRef.value) return
      
      await editFormRef.value.validate(async (valid) => {
        if (valid) {
          try {
            // 调用API更新用户信息
            const response = await updateUser(Number(editForm.id), {
              username: editForm.username,
              email: editForm.email,
              location: editForm.location,
              status: editForm.status as 'active' | 'disabled'
            })
            
            // 更新本地数据
            const updatedUser = response.data.user
            const targetUser = users.value.find(u => u.id === editForm.id)
            if (targetUser) {
              targetUser.username = updatedUser.username
              targetUser.email = updatedUser.email
              targetUser.location = updatedUser.location
              targetUser.status = updatedUser.status
              
              // 如果当前正在查看这个用户，也更新查看视图
              if (currentUser.value.id === editForm.id) {
                currentUser.value = { ...targetUser }
              }
              
              // 更新统计数据
              statistics.activeUsers = users.value.filter(u => u.status === 'active').length
              statistics.disabledUsers = users.value.filter(u => u.status === 'disabled').length
            }
            
            editDialogVisible.value = false
            ElMessage.success(response.data.message || '更新用户信息成功')
          } catch (error: any) {
            console.error('更新用户信息失败:', error)
            ElMessage.error(error.response?.data?.error || '更新用户信息失败')
            return false
          }
        } else {
          ElMessage.error('表单验证失败，请检查输入')
          return false
        }
      })
    }
    
    onMounted(() => {
      fetchUsers()
    })
    
    return {
      loading,
      users,
      filteredUsers,
      currentPage,
      pageSize,
      totalUsers,
      searchQuery,
      statistics,
      dialogVisible,
      editDialogVisible,
      currentUser,
      editForm,
      editRules,
      editFormRef,
      defaultAvatar,
      handleSearch,
      handleCurrentChange,
      handleSizeChange,
      handleViewUser,
      handleToggleStatus,
      handleEditUser,
      submitEdit,
      CircleClose,
      CircleCheck
    }
  }
})
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
}

.statistics-cards {
  margin-bottom: 20px;
}

.statistics-card {
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  height: 100px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.statistics-card-content {
  display: flex;
  flex-direction: column;
}

.statistics-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.statistics-label {
  font-size: 14px;
  color: #909399;
}

.statistics-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #f2f6fc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.statistics-icon .el-icon {
  font-size: 24px;
  color: #909399;
}

.statistics-icon.green {
  background-color: #f0f9eb;
}

.statistics-icon.green .el-icon {
  color: #67c23a;
}

.statistics-icon.blue {
  background-color: #ecf5ff;
}

.statistics-icon.blue .el-icon {
  color: #409eff;
}

.statistics-icon.red {
  background-color: #fef0f0;
}

.statistics-icon.red .el-icon {
  color: #f56c6c;
}

.users-table {
  margin-top: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style> 