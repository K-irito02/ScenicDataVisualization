<template>
  <div class="user-management">
    <el-card class="header-card">
      <div class="header">
        <h2>用户管理</h2>
        <div class="actions">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索用户名/邮箱"
            prefix-icon="Search"
            clearable
            style="width: 250px; margin-right: 10px"
            @keyup.enter="handleSearch"
          />
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button type="success" @click="dialogVisible = true">添加用户</el-button>
        </div>
      </div>
    </el-card>
    
    <el-card class="table-card">
      <el-table
        :data="userList"
        stripe
        style="width: 100%"
        border
        v-loading="loading">
        <el-table-column type="index" width="50" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="avatar" label="头像" width="100">
          <template #default="scope">
            <el-avatar :size="40" :src="scope.row.avatar">{{ scope.row.username.slice(0, 1) }}</el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'danger' : scope.row.role === 'vip' ? 'warning' : 'info'">
              {{ scope.row.role === 'admin' ? '管理员' : scope.row.role === 'vip' ? 'VIP用户' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-switch
              v-model="scope.row.status"
              :active-value="1"
              :inactive-value="0"
              @change="handleStatusChange(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="registerTime" label="注册时间" width="180" />
        <el-table-column prop="lastLoginTime" label="最后登录时间" width="180" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="primary" @click="handleViewDetail(scope.row)">详情</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingUser.id ? '编辑用户' : '添加用户'"
      width="500px">
      <el-form
        ref="userFormRef"
        :model="editingUser"
        :rules="rules"
        label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editingUser.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editingUser.email" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="editingUser.password" type="password" placeholder="留空则不修改" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="editingUser.role" placeholder="请选择角色">
            <el-option label="普通用户" value="user" />
            <el-option label="VIP用户" value="vip" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="editingUser.status"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveUser">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// 用户列表加载状态
const loading = ref(false)

// 搜索关键词
const searchKeyword = ref('')

// 分页参数
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 用户列表
const userList = ref([
  {
    id: 1,
    username: 'admin',
    avatar: 'https://example.com/avatars/admin.jpg',
    email: 'admin@example.com',
    role: 'admin',
    status: 1,
    registerTime: '2022-01-01 10:00:00',
    lastLoginTime: '2023-03-15 08:30:45'
  },
  {
    id: 2,
    username: 'zhangsan',
    avatar: 'https://example.com/avatars/zhangsan.jpg',
    email: 'zhangsan@example.com',
    role: 'user',
    status: 1,
    registerTime: '2022-02-15 14:22:30',
    lastLoginTime: '2023-03-14 16:42:12'
  },
  {
    id: 3,
    username: 'lisi',
    avatar: 'https://example.com/avatars/lisi.jpg',
    email: 'lisi@example.com',
    role: 'vip',
    status: 1,
    registerTime: '2022-03-20 09:15:40',
    lastLoginTime: '2023-03-13 10:18:25'
  },
  {
    id: 4,
    username: 'wangwu',
    avatar: 'https://example.com/avatars/wangwu.jpg',
    email: 'wangwu@example.com',
    role: 'user',
    status: 0,
    registerTime: '2022-04-10 11:33:20',
    lastLoginTime: '2023-02-28 14:50:10'
  },
  {
    id: 5,
    username: 'zhaoliu',
    avatar: 'https://example.com/avatars/zhaoliu.jpg',
    email: 'zhaoliu@example.com',
    role: 'user',
    status: 1,
    registerTime: '2022-05-05 16:45:00',
    lastLoginTime: '2023-03-10 09:22:30'
  }
])

// 对话框可见性
const dialogVisible = ref(false)

// 表单规则
const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ]
})

// 表单引用
const userFormRef = ref<FormInstance>()

// 当前编辑的用户数据
const editingUser = ref({
  id: 0,
  username: '',
  email: '',
  password: '',
  role: 'user',
  status: 1
})

// 获取用户列表数据
const loadUserList = async () => {
  loading.value = true
  try {
    // 在真实项目中应从API获取数据
    // const response = await getUserList({
    //   page: currentPage.value,
    //   pageSize: pageSize.value,
    //   keyword: searchKeyword.value
    // })
    // userList.value = response.data.list
    // total.value = response.data.total
    
    // 模拟加载延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 使用模拟数据
    total.value = userList.value.length
    
    console.log('加载用户列表', {
      page: currentPage.value,
      pageSize: pageSize.value,
      keyword: searchKeyword.value
    })
  } catch (error) {
    console.error('加载用户列表失败', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  loadUserList()
}

// 页码变化处理
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadUserList()
}

// 每页数量变化处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  loadUserList()
}

// 状态变化处理
const handleStatusChange = async (row: any) => {
  try {
    // 在真实项目中应调用API
    // await updateUserStatus(row.id, row.status)
    
    ElMessage.success(`用户 ${row.username} 状态已${row.status === 1 ? '启用' : '禁用'}`)
    console.log('更新用户状态', row.id, row.status)
  } catch (error) {
    console.error('更新用户状态失败', error)
    ElMessage.error('更新用户状态失败')
    // 恢复之前的状态
    row.status = row.status === 1 ? 0 : 1
  }
}

// 编辑用户
const handleEdit = (row: any) => {
  editingUser.value = {
    id: row.id,
    username: row.username,
    email: row.email,
    password: '', // 密码不回显
    role: row.role,
    status: row.status
  }
  dialogVisible.value = true
}

// 查看用户详情
const handleViewDetail = (row: any) => {
  console.log('查看用户详情', row.id)
  ElMessage.info(`功能开发中: 查看用户 ${row.username} 的详细信息`)
}

// 删除用户
const handleDelete = (row: any) => {
  ElMessageBox.confirm(
    `确定要删除用户 ${row.username} 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        // 在真实项目中应调用API
        // await deleteUser(row.id)
        
        // 模拟操作成功
        await new Promise(resolve => setTimeout(resolve, 300))
        
        ElMessage.success('删除成功')
        // 更新列表
        userList.value = userList.value.filter(item => item.id !== row.id)
        total.value--
      } catch (error) {
        console.error('删除用户失败', error)
        ElMessage.error('删除用户失败')
      }
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 保存用户数据
const handleSaveUser = async () => {
  if (!userFormRef.value) return
  
  try {
    const valid = await userFormRef.value.validate()
    if (valid) {
      const isEdit = Boolean(editingUser.value.id)
      
      // 在真实项目中应调用API
      // if (isEdit) {
      //   await updateUser(editingUser.value)
      // } else {
      //   await createUser(editingUser.value)
      // }
      
      // 模拟操作延迟
      await new Promise(resolve => setTimeout(resolve, 500))
      
      if (isEdit) {
        // 更新列表中的数据
        const index = userList.value.findIndex(item => item.id === editingUser.value.id)
        if (index !== -1) {
          userList.value[index] = {
            ...userList.value[index],
            username: editingUser.value.username,
            email: editingUser.value.email,
            role: editingUser.value.role,
            status: editingUser.value.status
          }
        }
      } else {
        // 添加到列表
        userList.value.unshift({
          id: Date.now(), // 模拟生成ID
          username: editingUser.value.username,
          email: editingUser.value.email,
          role: editingUser.value.role,
          status: editingUser.value.status,
          avatar: 'https://example.com/avatars/default.jpg',
          registerTime: new Date().toLocaleString(),
          lastLoginTime: '-'
        })
        total.value++
      }
      
      ElMessage.success(isEdit ? '更新成功' : '添加成功')
      dialogVisible.value = false
    }
  } catch (error) {
    return
  }
}

// 初始化
onMounted(() => {
  loadUserList()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.actions {
  display: flex;
  align-items: center;
}

.table-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 