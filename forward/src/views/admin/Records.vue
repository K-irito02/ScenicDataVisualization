<template>
  <div class="records-container">
    <el-card class="header-card">
      <div class="header">
        <h2>系统记录</h2>
        <div class="actions">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 350px; margin-right: 10px"
          />
          <el-select
            v-model="typeFilter"
            placeholder="记录类型"
            clearable
            style="width: 150px; margin-right: 10px">
            <el-option label="所有类型" value="" />
            <el-option label="登录" value="login" />
            <el-option label="操作" value="operation" />
            <el-option label="系统" value="system" />
            <el-option label="错误" value="error" />
          </el-select>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button type="danger" @click="handleClearLogs">清空记录</el-button>
          <el-button type="success" @click="handleExport">导出记录</el-button>
        </div>
      </div>
    </el-card>
    
    <el-card class="table-card">
      <el-table
        :data="recordList"
        stripe
        style="width: 100%"
        border
        v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="scope">
            <el-tag
              :type="scope.row.type === 'login' ? 'primary' : 
                     scope.row.type === 'operation' ? 'success' : 
                     scope.row.type === 'system' ? 'warning' : 'danger'">
              {{ 
                scope.row.type === 'login' ? '登录' : 
                scope.row.type === 'operation' ? '操作' : 
                scope.row.type === 'system' ? '系统' : '错误' 
              }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="ipAddress" label="IP地址" width="150" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="createdAt" label="时间" width="180" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" @click="handleViewDetail(scope.row)">详情</el-button>
            <el-button size="small" type="danger" @click="handleDeleteRecord(scope.row)">删除</el-button>
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
    
    <!-- 记录详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="记录详情"
      width="700px">
      <div v-if="currentRecord" class="record-detail">
        <div class="detail-item">
          <span class="label">ID:</span>
          <span class="value">{{ currentRecord.id }}</span>
        </div>
        <div class="detail-item">
          <span class="label">类型:</span>
          <span class="value">
            <el-tag
              :type="currentRecord.type === 'login' ? 'primary' : 
                    currentRecord.type === 'operation' ? 'success' : 
                    currentRecord.type === 'system' ? 'warning' : 'danger'">
              {{ 
                currentRecord.type === 'login' ? '登录' : 
                currentRecord.type === 'operation' ? '操作' : 
                currentRecord.type === 'system' ? '系统' : '错误' 
              }}
            </el-tag>
          </span>
        </div>
        <div class="detail-item">
          <span class="label">时间:</span>
          <span class="value">{{ currentRecord.createdAt }}</span>
        </div>
        <div class="detail-item">
          <span class="label">用户:</span>
          <span class="value">{{ currentRecord.username }}</span>
        </div>
        <div class="detail-item">
          <span class="label">IP地址:</span>
          <span class="value">{{ currentRecord.ipAddress }}</span>
        </div>
        <div class="detail-item">
          <span class="label">用户代理:</span>
          <span class="value">{{ currentRecord.userAgent || '-' }}</span>
        </div>
        <div class="detail-item full">
          <span class="label">操作内容:</span>
          <span class="value content">{{ currentRecord.content }}</span>
        </div>
        <div v-if="currentRecord.details" class="detail-item full">
          <span class="label">详细信息:</span>
          <pre class="value details">{{ JSON.stringify(currentRecord.details, null, 2) }}</pre>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface SystemRecord {
  id: number
  type: 'login' | 'operation' | 'system' | 'error'
  content: string
  ipAddress: string
  username: string
  createdAt: string
  userAgent?: string
  details?: any
}

// 搜索过滤条件
const dateRange = ref([])
const typeFilter = ref('')

// 记录加载状态
const loading = ref(false)

// 分页参数
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 记录列表
const recordList = ref([
  {
    id: 10001,
    type: 'login',
    content: '用户登录系统',
    ipAddress: '192.168.1.100',
    username: 'admin',
    createdAt: '2023-03-15 08:30:45',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    details: {
      loginType: '密码登录',
      status: '成功'
    }
  },
  {
    id: 10002,
    type: 'operation',
    content: '更新景区信息: 故宫博物院',
    ipAddress: '192.168.1.100',
    username: 'admin',
    createdAt: '2023-03-15 09:15:22',
    details: {
      scenicId: 1001,
      fields: ['name', 'description', 'price'],
      oldValues: {
        price: 55
      },
      newValues: {
        price: 60
      }
    }
  },
  {
    id: 10003,
    type: 'system',
    content: '系统备份完成',
    ipAddress: '192.168.1.1',
    username: 'system',
    createdAt: '2023-03-15 01:00:00',
    details: {
      backupSize: '123.5MB',
      backupPath: '/backups/2023-03-15.zip',
      duration: '45s'
    }
  },
  {
    id: 10004,
    type: 'error',
    content: '数据库连接失败',
    ipAddress: '192.168.1.1',
    username: 'system',
    createdAt: '2023-03-14 23:45:12',
    details: {
      errorCode: 'ERR_DB_CONN',
      message: '无法连接到数据库服务器',
      retries: 3,
      resolved: true,
      resolution: '自动恢复'
    }
  },
  {
    id: 10005,
    type: 'operation',
    content: '删除评论ID: 5002',
    ipAddress: '192.168.1.100',
    username: 'admin',
    createdAt: '2023-03-14 16:22:05',
    details: {
      commentId: 5002,
      scenicId: 1003,
      userId: 42,
      reason: '违规内容'
    }
  }
])

// 当前选中的记录
const currentRecord = ref<SystemRecord | null>(null)
const detailVisible = ref(false)

// 加载记录列表
const loadRecords = async () => {
  loading.value = true
  try {
    // 实际项目中应从API获取数据
    // const response = await getSystemRecords({
    //   page: currentPage.value,
    //   pageSize: pageSize.value,
    //   startDate: dateRange.value[0],
    //   endDate: dateRange.value[1],
    //   type: typeFilter.value
    // })
    // recordList.value = response.data.list
    // total.value = response.data.total
    
    // 模拟加载延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 使用模拟数据
    total.value = recordList.value.length
    
    console.log('加载记录', {
      page: currentPage.value,
      pageSize: pageSize.value,
      dateRange: dateRange.value,
      type: typeFilter.value
    })
  } catch (error) {
    console.error('加载记录失败', error)
    ElMessage.error('获取系统记录失败')
  } finally {
    loading.value = false
  }
}

// 搜索记录
const handleSearch = () => {
  currentPage.value = 1
  loadRecords()
}

// 清空记录
const handleClearLogs = () => {
  ElMessageBox.confirm(
    '确定要清空所有记录吗？此操作不可恢复！',
    '警告',
    {
      confirmButtonText: '确定清空',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        // 实际项目中应调用API
        // await clearSystemLogs()
        
        // 模拟操作延迟
        await new Promise(resolve => setTimeout(resolve, 800))
        
        ElMessage.success('记录已清空')
        recordList.value = []
        total.value = 0
      } catch (error) {
        console.error('清空记录失败', error)
        ElMessage.error('清空记录失败')
      }
    })
    .catch(() => {
      ElMessage.info('已取消操作')
    })
}

// 导出记录
const handleExport = () => {
  ElMessage.success('记录导出功能开发中...')
  console.log('导出记录', {
    dateRange: dateRange.value,
    type: typeFilter.value
  })
}

// 查看记录详情
const handleViewDetail = (record: SystemRecord) => {
  currentRecord.value = record
  detailVisible.value = true
}

// 删除单条记录
const handleDeleteRecord = (record: SystemRecord) => {
  ElMessageBox.confirm(
    `确定要删除ID为 ${record.id} 的记录吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        // 实际项目中应调用API
        // await deleteSystemRecord(record.id)
        
        // 模拟操作延迟
        await new Promise(resolve => setTimeout(resolve, 300))
        
        ElMessage.success('删除成功')
        // 更新列表
        recordList.value = recordList.value.filter(item => item.id !== record.id)
        total.value--
      } catch (error) {
        console.error('删除记录失败', error)
        ElMessage.error('删除记录失败')
      }
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  loadRecords()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadRecords()
}

// 初始化
onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.records-container {
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

.record-detail {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.detail-item {
  width: calc(50% - 6px);
  display: flex;
}

.detail-item.full {
  width: 100%;
  flex-direction: column;
}

.detail-item .label {
  font-weight: bold;
  color: #606266;
  width: 80px;
  flex-shrink: 0;
}

.detail-item .value {
  flex: 1;
}

.detail-item .content {
  white-space: pre-wrap;
  margin-top: 10px;
}

.detail-item .details {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  overflow: auto;
  margin-top: 10px;
  max-height: 300px;
}
</style> 