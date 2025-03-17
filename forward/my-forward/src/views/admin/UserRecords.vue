<template>
  <div class="user-records-container">
    <card-container title="用户记录管理">
      <template #actions>
        <div class="filter-form">
          <el-form :inline="true" :model="filterForm" class="demo-form-inline">
            <el-form-item label="用户ID">
              <el-input v-model="filterForm.userId" placeholder="输入用户ID" clearable />
            </el-form-item>
            <el-form-item label="记录类型">
              <el-select v-model="filterForm.recordType" placeholder="选择记录类型" clearable>
                <el-option label="搜索记录" value="search" />
                <el-option label="收藏记录" value="favorite" />
              </el-select>
            </el-form-item>
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="filterForm.timeRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleFilter">筛选</el-button>
              <el-button @click="resetFilter">重置</el-button>
              <el-button type="success" @click="exportData">导出数据</el-button>
            </el-form-item>
          </el-form>
        </div>
      </template>
      
      <div class="records-summary">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="summary-card">
              <div class="summary-title">记录总数</div>
              <div class="summary-content">
                <div class="summary-value">{{ summary.totalRecords }}</div>
                <el-progress
                  :percentage="100"
                  :format="() => ''"
                  :stroke-width="8"
                  status="success"
                />
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-card">
              <div class="summary-title">搜索记录</div>
              <div class="summary-content">
                <div class="summary-value">{{ summary.searchRecords }}</div>
                <el-progress
                  :percentage="summary.searchPercentage"
                  :format="() => summary.searchPercentage + '%'"
                  :stroke-width="8"
                  color="#409eff"
                />
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-card">
              <div class="summary-title">收藏记录</div>
              <div class="summary-content">
                <div class="summary-value">{{ summary.favoriteRecords }}</div>
                <el-progress
                  :percentage="summary.favoritePercentage"
                  :format="() => summary.favoritePercentage + '%'"
                  :stroke-width="8"
                  color="#67c23a"
                />
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <div class="records-chart">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h3>记录类型分布</h3>
              <base-chart :options="pieChartOptions" height="300px" />
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h3>记录时间趋势</h3>
              <base-chart :options="lineChartOptions" height="300px" />
            </div>
          </el-col>
        </el-row>
      </div>
      
      <div class="records-table">
        <el-table
          v-loading="loading"
          :data="recordsData"
          border
          style="width: 100%"
          row-key="id"
        >
          <el-table-column prop="id" label="记录ID" width="80" />
          <el-table-column prop="userId" label="用户ID" width="80" />
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="recordType" label="记录类型" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.recordType === 'search' ? 'primary' : 'success'">
                {{ scope.row.recordType === 'search' ? '搜索' : '收藏' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
          <el-table-column prop="time" label="时间" width="180" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button
                type="primary"
                circle
                size="small"
                @click="handleViewRecord(scope.row)"
              >
                <el-icon><View /></el-icon>
              </el-button>
              <el-button
                type="danger"
                circle
                size="small"
                @click="handleDeleteRecord(scope.row)"
              >
                <el-icon><Delete /></el-icon>
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
            :total="totalRecords"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </card-container>
    
    <!-- 查看记录详情对话框 -->
    <el-dialog
      v-model="recordDetailVisible"
      title="记录详情"
      width="500px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="记录ID">{{ currentRecord.id }}</el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ currentRecord.userId }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ currentRecord.username }}</el-descriptions-item>
        <el-descriptions-item label="记录类型">
          <el-tag :type="currentRecord.recordType === 'search' ? 'primary' : 'success'">
            {{ currentRecord.recordType === 'search' ? '搜索' : '收藏' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="时间">{{ currentRecord.time }}</el-descriptions-item>
        <el-descriptions-item label="内容">{{ currentRecord.content }}</el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="recordDetailVisible = false">关闭</el-button>
          <el-button type="danger" @click="handleDeleteRecord(currentRecord, true)">删除记录</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed, onMounted } from 'vue'
import CardContainer from '@/components/common/CardContainer.vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import { View, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ElMessageBox from 'element-plus/es/components/message-box/index'
import type { EChartsOption } from 'echarts'
import axios from 'axios'

export default defineComponent({
  name: 'UserRecords',
  components: {
    CardContainer,
    BaseChart,
    View,
    Delete
  },
  setup() {
    const loading = ref(false)
    const recordsData = ref<any[]>([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalRecords = ref(0)
    const recordDetailVisible = ref(false)
    const currentRecord = ref<any>({})
    
    // 筛选表单
    const filterForm = reactive({
      userId: '',
      recordType: '',
      timeRange: [] as [Date?, Date?]
    })
    
    // 统计数据
    const summary = reactive({
      totalRecords: 0,
      searchRecords: 0,
      favoriteRecords: 0,
      searchPercentage: 0,
      favoritePercentage: 0
    })
    
    // 获取记录数据
    const fetchRecords = async () => {
      loading.value = true;
      
      try {
        // 从API获取数据
        const response = await axios.get('/api/admin/user-records', {
          params: {
            page: currentPage.value,
            pageSize: pageSize.value,
            userId: filterForm.userId || undefined,
            recordType: filterForm.recordType || undefined,
            startDate: filterForm.timeRange && filterForm.timeRange[0] ? filterForm.timeRange[0].toISOString() : undefined,
            endDate: filterForm.timeRange && filterForm.timeRange[1] ? filterForm.timeRange[1].toISOString() : undefined
          }
        });
        
        // 更新数据
        recordsData.value = response.data.records;
        totalRecords.value = response.data.total;
        
        // 更新统计数据
        updateSummary(response.data.summary);
      } catch (error) {
        console.error('获取记录数据失败:', error);
        ElMessage.error('获取记录数据失败');
      } finally {
        loading.value = false;
      }
    };
    
    // 更新统计数据
    const updateSummary = (summaryData: any) => {
      summary.totalRecords = summaryData.totalRecords || 0;
      summary.searchRecords = summaryData.searchRecords || 0;
      summary.favoriteRecords = summaryData.favoriteRecords || 0;
      
      summary.searchPercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.searchRecords / summary.totalRecords) * 100);
      
      summary.favoritePercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.favoriteRecords / summary.totalRecords) * 100);
    };
    
    // 获取记录类型分布图表数据
    const getRecordTypePieData = () => {
      return [
        { value: summary.searchRecords, name: '搜索记录' },
        { value: summary.favoriteRecords, name: '收藏记录' }
      ];
    };
    
    // 获取时间趋势数据
    const getTimeLineData = () => {
      // 从API获取时间趋势数据
      return {
        xAxisData: [],
        searchData: [],
        favoriteData: []
      };
    };
    
    // 饼图配置
    const pieChartOptions = computed<EChartsOption>(() => {
      return {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 'bottom'
        },
        series: [
          {
            name: '记录类型',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: getRecordTypePieData()
          }
        ]
      }
    })
    
    // 折线图配置
    const lineChartOptions = computed<EChartsOption>(() => {
      const { xAxisData, searchData, favoriteData } = getTimeLineData()
      
      return {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['搜索记录', '收藏记录'],
          bottom: 'bottom'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: xAxisData
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '搜索记录',
            type: 'line',
            stack: 'Total',
            data: searchData,
            smooth: true,
            lineStyle: {
              width: 3,
              color: '#409eff'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
                  { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
                ]
              }
            }
          },
          {
            name: '收藏记录',
            type: 'line',
            stack: 'Total',
            data: favoriteData,
            smooth: true,
            lineStyle: {
              width: 3,
              color: '#67c23a'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
                  { offset: 1, color: 'rgba(103, 194, 58, 0.1)' }
                ]
              }
            }
          }
        ]
      }
    })
    
    // 处理筛选
    const handleFilter = () => {
      currentPage.value = 1
      fetchRecords()
    }
    
    // 重置筛选
    const resetFilter = () => {
      filterForm.userId = ''
      filterForm.recordType = ''
      filterForm.timeRange = []
      handleFilter()
    }
    
    // 处理页码变化
    const handleCurrentChange = (page: number) => {
      currentPage.value = page
      fetchRecords()
    }
    
    // 处理每页条数变化
    const handleSizeChange = (size: number) => {
      pageSize.value = size
      currentPage.value = 1
      fetchRecords()
    }
    
    // 查看记录详情
    const handleViewRecord = (record: any) => {
      currentRecord.value = { ...record }
      recordDetailVisible.value = true
    }
    
    // 删除记录
    const handleDeleteRecord = async (record: any, fromDialog = false) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除用户 "${record.username}" 的${record.recordType === 'search' ? '搜索' : '收藏'}记录吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 实际项目中应该调用API
        // 这里直接修改前端数据
        const index = recordsData.value.findIndex(r => r.id === record.id)
        if (index !== -1) {
          recordsData.value.splice(index, 1)
          
          // 更新统计数据 (简化处理，实际应该重新获取)
          if (record.recordType === 'search') {
            summary.searchRecords--
          } else {
            summary.favoriteRecords--
          }
          summary.totalRecords--
          
          // 更新百分比
          summary.searchPercentage = summary.totalRecords === 0 ? 0 : 
            Math.round((summary.searchRecords / summary.totalRecords) * 100)
          
          summary.favoritePercentage = summary.totalRecords === 0 ? 0 : 
            Math.round((summary.favoriteRecords / summary.totalRecords) * 100)
        }
        
        ElMessage.success('删除记录成功')
        
        // 如果是从对话框删除，关闭对话框
        if (fromDialog) {
          recordDetailVisible.value = false
        }
      } catch (error) {
        // 用户取消操作，不做处理
      }
    }
    
    // 导出数据
    const exportData = () => {
      ElMessage.success('数据导出功能将在实际项目中实现')
    }
    
    onMounted(() => {
      fetchRecords()
    })
    
    return {
      loading,
      recordsData,
      currentPage,
      pageSize,
      totalRecords,
      filterForm,
      summary,
      pieChartOptions,
      lineChartOptions,
      recordDetailVisible,
      currentRecord,
      handleFilter,
      resetFilter,
      handleCurrentChange,
      handleSizeChange,
      handleViewRecord,
      handleDeleteRecord,
      exportData
    }
  }
})
</script>

<style scoped>
.user-records-container {
  padding: 20px;
}

.filter-form {
  margin-bottom: 20px;
}

.records-summary {
  margin-bottom: 20px;
}

.summary-card {
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 15px;
  height: 100px;
}

.summary-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 15px;
}

.summary-content {
  display: flex;
  flex-direction: column;
}

.summary-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.records-chart {
  margin-bottom: 20px;
}

.chart-container {
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 15px;
  margin-bottom: 20px;
}

.chart-container h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 500;
  color: #606266;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.el-tag {
  text-transform: capitalize;
}
</style> 