<template>
  <div class="error-log-container">
    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="错误级别">
          <el-select v-model="filterForm.level" placeholder="选择错误级别" clearable>
            <el-option label="调试" value="DEBUG" />
            <el-option label="信息" value="INFO" />
            <el-option label="警告" value="WARNING" />
            <el-option label="错误" value="ERROR" />
            <el-option label="严重" value="CRITICAL" />
          </el-select>
        </el-form-item>
        <el-form-item label="错误类型">
          <el-select v-model="filterForm.error_type" placeholder="选择错误类型" clearable>
            <el-option label="前端" value="FRONTEND" />
            <el-option label="后端" value="BACKEND" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-select v-model="filterForm.days" placeholder="选择时间范围" clearable>
            <el-option label="今天" :value="1" />
            <el-option label="最近3天" :value="3" />
            <el-option label="最近7天" :value="7" />
            <el-option label="最近30天" :value="30" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchErrorLogs">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table
      v-loading="loading"
      :data="safeErrorLogs"
      style="width: 100%"
      border
      stripe
      :default-sort="{ prop: 'timestamp', order: 'descending' }"
    >
      <el-table-column prop="level_display" label="级别" width="100">
        <template #default="scope">
          <el-tag
            :type="getTagType(scope.row.level)"
            effect="dark"
          >
            {{ scope.row.level_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="error_type_display" label="类型" width="100">
        <template #default="scope">
          <el-tag
            :type="scope.row.error_type === 'FRONTEND' ? 'warning' : 'info'"
          >
            {{ scope.row.error_type_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="timestamp" label="时间" width="180" sortable />
      <el-table-column prop="message" label="错误信息" min-width="250" show-overflow-tooltip />
      <el-table-column prop="path" label="请求路径" min-width="180" show-overflow-tooltip />
      <el-table-column prop="method" label="请求方法" width="100" />
      <el-table-column prop="user_id" label="用户ID" width="100" />
      <el-table-column prop="ip_address" label="IP地址" width="150" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="scope">
          <el-button
            size="small"
            @click="showDetails(scope.row)"
          >
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加分页组件 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      title="错误详情"
      width="70%"
    >
      <div class="error-details">
        <h4>错误信息</h4>
        <p>{{ currentError.message }}</p>
        
        <h4>错误类型</h4>
        <p>{{ currentError.error_type_display || '未知' }}</p>
        
        <h4>请求信息</h4>
        <p><strong>路径:</strong> {{ currentError.path }}</p>
        <p><strong>方法:</strong> {{ currentError.method }}</p>
        <p><strong>用户ID:</strong> {{ currentError.user_id || '未登录' }}</p>
        <p><strong>IP地址:</strong> {{ currentError.ip_address }}</p>
        
        <h4>堆栈追踪</h4>
        <pre class="traceback">{{ currentError.traceback || '无堆栈追踪信息' }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { getSystemErrorLogs } from '@/api/admin'
import { ElMessage } from 'element-plus'
import { errorLogger } from '@/api'

// 加载状态
const loading = ref(false)

// 错误日志列表
const errorLogs = ref<any[]>([])

// 安全的错误日志列表（确保是数组）
const safeErrorLogs = computed(() => {
  // 确保errorLogs始终是一个数组
  if (!Array.isArray(errorLogs.value)) {
    errorLogger.warning('错误日志数据不是数组', errorLogs.value)
    return []
  }
  
  // 确保每个日志项都有所有必要的字段
  return errorLogs.value.map(log => ({
    id: log.id || 0,
    level: log.level || 'ERROR',
    level_display: log.level_display || '错误',
    error_type: log.error_type || 'BACKEND',
    error_type_display: log.error_type_display || '后端',
    message: log.message || '未知错误',
    traceback: log.traceback || '',
    path: log.path || '',
    method: log.method || '',
    user_id: log.user_id || null,
    ip_address: log.ip_address || '',
    timestamp: log.timestamp || new Date().toISOString()
  }))
})

// 过滤表单
const filterForm = reactive({
  level: '',
  error_type: '',
  days: undefined
})

// 分页参数
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 对话框控制
const dialogVisible = ref(false)
const currentError = ref({
  message: '',
  path: '',
  method: '',
  user_id: null,
  ip_address: '',
  traceback: '',
  error_type: '',
  error_type_display: ''
})

// 获取错误日志
const fetchErrorLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      pageSize: pagination.pageSize
    } as any
    if (filterForm.level) params.level = filterForm.level
    if (filterForm.error_type) params.error_type = filterForm.error_type
    if (filterForm.days) params.days = filterForm.days
    
    const res = await getSystemErrorLogs(params)
    
    // 安全地处理后端返回的数据
    try {
      if (res && res.data) {
        if (Array.isArray(res.data.data)) {
          // 正确的嵌套格式
          errorLogs.value = res.data.data
          pagination.total = res.data.total || 0
          pagination.currentPage = res.data.page || 1
          pagination.pageSize = res.data.pageSize || 10
        } else if (Array.isArray(res.data)) {
          // 直接返回的数组
          errorLogs.value = res.data
          pagination.total = res.data.length
        } else {
          // 未知格式，记录错误并使用空数组
          errorLogger.error('返回的数据格式不符合预期', res.data)
          errorLogs.value = []
          pagination.total = 0
        }
      } else {
        errorLogs.value = []
        pagination.total = 0
      }
    } catch (dataError) {
      errorLogger.error('处理返回数据时出错', dataError)
      errorLogs.value = []
      pagination.total = 0
    }
  } catch (error) {
    errorLogger.error('获取错误日志失败', error)
    ElMessage.error('获取错误日志失败')
    errorLogs.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 重置过滤条件
const resetFilter = () => {
  filterForm.level = ''
  filterForm.error_type = ''
  filterForm.days = undefined
  fetchErrorLogs()
}

// 根据错误级别获取标签类型
const getTagType = (level: string) => {
  const map: Record<string, string> = {
    'DEBUG': 'info',
    'INFO': 'success',
    'WARNING': 'warning',
    'ERROR': 'danger',
    'CRITICAL': 'danger'
  }
  return map[level] || 'info'
}

// 显示详情
const showDetails = (row: any) => {
  currentError.value = row
  dialogVisible.value = true
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
  fetchErrorLogs()
}

// 处理每页条数变化
const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1 // 重置到第一页
  fetchErrorLogs()
}

// 组件挂载时加载数据
onMounted(() => {
  fetchErrorLogs()
})
</script>

<style scoped>
.error-log-container {
  padding: 20px;
}

.filter-bar {
  margin-bottom: 20px;
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.traceback {
  background-color: #f8f8f8;
  padding: 10px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
}

.error-details h4 {
  margin-top: 20px;
  margin-bottom: 10px;
  font-weight: bold;
  color: #333;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style> 