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
                <el-option label="登录记录" value="login" />
                <el-option label="注册记录" value="register" />
                <el-option label="管理员操作" value="admin" />
                <el-option label="修改个人信息" value="profile_update" />
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
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="8">
            <div class="summary-card">
              <div class="summary-title">登录记录</div>
              <div class="summary-content">
                <div class="summary-value">{{ summary.loginRecords }}</div>
                <el-progress
                  :percentage="summary.loginPercentage"
                  :format="() => summary.loginPercentage + '%'"
                  :stroke-width="8"
                  color="#e6a23c"
                />
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-card">
              <div class="summary-title">注册记录</div>
              <div class="summary-content">
                <div class="summary-value">{{ summary.registerRecords }}</div>
                <el-progress
                  :percentage="summary.registerPercentage"
                  :format="() => summary.registerPercentage + '%'"
                  :stroke-width="8"
                  color="#f56c6c"
                />
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-card">
              <div class="summary-title">管理员操作</div>
              <div class="summary-content">
                <div class="summary-value">{{ summary.adminRecords }}</div>
                <el-progress
                  :percentage="summary.adminPercentage"
                  :format="() => summary.adminPercentage + '%'"
                  :stroke-width="8"
                  color="#909399"
                />
              </div>
            </div>
          </el-col>
        </el-row>
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="8">
            <div class="summary-card">
              <div class="summary-title">修改个人信息</div>
              <div class="summary-content">
                <div class="summary-value">{{ summary.profileUpdateRecords }}</div>
                <el-progress
                  :percentage="summary.profileUpdatePercentage"
                  :format="() => summary.profileUpdatePercentage + '%'"
                  :stroke-width="8"
                  color="#8e44ad"
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
              <div v-if="loading" style="height: 300px" v-loading="loading"></div>
              <base-chart v-else :options="lineChartOptions" height="300px" />
              <div v-if="!loading && !hasTimeData" class="no-data-tip">
                <el-empty description="暂无时间趋势数据" :image-size="80"></el-empty>
              </div>
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
          <el-table-column prop="action" label="记录类型" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.action === 'search' ? 'primary' : scope.row.action === 'favorite' ? 'success' : 'info'">
                {{ scope.row.action === 'search' ? '搜索' : scope.row.action === 'favorite' ? '收藏' : scope.row.action }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="details" label="内容" min-width="200" show-overflow-tooltip />
          <el-table-column prop="timestamp" label="时间" width="180" />
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
          <el-tag :type="currentRecord.action === 'search' ? 'primary' : currentRecord.action === 'favorite' ? 'success' : 'info'">
            {{ currentRecord.action === 'search' ? '搜索' : currentRecord.action === 'favorite' ? '收藏' : currentRecord.action }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="时间">{{ currentRecord.timestamp }}</el-descriptions-item>
        <el-descriptions-item label="内容">{{ currentRecord.details }}</el-descriptions-item>
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
import { getUserRecords, deleteUserRecord } from '@/api/admin'

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
      loginRecords: 0,
      registerRecords: 0,
      adminRecords: 0,
      profileUpdateRecords: 0,
      searchPercentage: 0,
      favoritePercentage: 0,
      loginPercentage: 0,
      registerPercentage: 0,
      adminPercentage: 0,
      profileUpdatePercentage: 0
    })
    
    // 获取记录数据
    const fetchRecords = async () => {
      loading.value = true;
      
      try {
        // 准备API请求参数
        const params: any = {
          page: currentPage.value,
          pageSize: pageSize.value
        };
        
        // 添加用户ID筛选
        if (filterForm.userId) {
          params.user_id = parseInt(filterForm.userId);
        }
        
        // 添加记录类型筛选
        if (filterForm.recordType) {
          params.record_type = filterForm.recordType;
        }
        
        // 添加时间范围筛选
        if (filterForm.timeRange && filterForm.timeRange.length === 2 && filterForm.timeRange[0] && filterForm.timeRange[1]) {
          params.start_date = filterForm.timeRange[0].toISOString().split('T')[0];
          params.end_date = filterForm.timeRange[1].toISOString().split('T')[0];
        }

        // 调试：记录请求参数
        console.log('【调试】请求参数:', params);
        
        // 从API获取数据
        const response = await getUserRecords(params);
        
        // 调试：记录原始响应数据
        console.log('【调试】API响应:', response.data);
        
        // 更新数据
        recordsData.value = response.data.data;
        totalRecords.value = response.data.total;
        
        // 更新统计数据
        if (response.data.summary) {
          console.log('【调试】处理统计数据:', response.data.summary);
          updateSummary(response.data.summary);
          
          // 更新图表数据
          if (response.data.summary.timeTrend) {
            console.log('【调试】时间趋势数据:', response.data.summary.timeTrend);
            timeTrendData.value = response.data.summary.timeTrend;
            // 检查时间趋势数据是否有效
            console.log('【调试】更新后的时间趋势数据状态:', {
              'x轴数据长度': timeTrendData.value.xAxisData?.length || 0,
              '搜索数据长度': timeTrendData.value.searchData?.length || 0,
              '收藏数据长度': timeTrendData.value.favoriteData?.length || 0,
              '登录数据长度': timeTrendData.value.loginData?.length || 0,
              '有数据示例': timeTrendData.value.xAxisData?.slice(0, 3),
              '完整xAxisData': timeTrendData.value.xAxisData
            });
          } else {
            console.log('【调试】后端返回的数据中没有timeTrend字段');
          }
        } else {
          console.log('【调试】后端返回的数据中没有summary字段');
        }
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
      summary.loginRecords = summaryData.loginRecords || 0;
      summary.registerRecords = summaryData.registerRecords || 0;
      summary.adminRecords = summaryData.adminRecords || 0;
      summary.profileUpdateRecords = summaryData.profileUpdateRecords || 0;
      
      summary.searchPercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.searchRecords / summary.totalRecords) * 100);
      
      summary.favoritePercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.favoriteRecords / summary.totalRecords) * 100);
      
      summary.loginPercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.loginRecords / summary.totalRecords) * 100);
      
      summary.registerPercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.registerRecords / summary.totalRecords) * 100);
      
      summary.adminPercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.adminRecords / summary.totalRecords) * 100);
      
      summary.profileUpdatePercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.profileUpdateRecords / summary.totalRecords) * 100);
    };
    
    // 获取记录类型分布图表数据
    const getRecordTypePieData = () => {
      return [
        { value: summary.searchRecords, name: '搜索记录' },
        { value: summary.favoriteRecords, name: '收藏记录' },
        { value: summary.loginRecords, name: '登录记录' },
        { value: summary.registerRecords, name: '注册记录' },
        { value: summary.adminRecords, name: '管理员操作' },
        { value: summary.profileUpdateRecords, name: '修改个人信息' }
      ];
    };
    
    // 获取时间趋势数据
    const timeTrendData = ref({
      xAxisData: [] as string[],
      searchData: [] as number[],
      favoriteData: [] as number[],
      loginData: [] as number[],
      registerData: [] as number[],
      adminData: [] as number[],
      profileUpdateData: [] as number[]
    });
    
    // 获取时间趋势数据
    const getTimeLineData = () => {
      return timeTrendData.value;
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
      const { xAxisData, searchData, favoriteData, loginData, registerData, adminData, profileUpdateData } = getTimeLineData()
      
      return {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['搜索记录', '收藏记录', '登录记录', '注册记录', '管理员操作', '修改个人信息'],
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
          },
          {
            name: '登录记录',
            type: 'line',
            stack: 'Total',
            data: loginData,
            smooth: true,
            lineStyle: {
              width: 3,
              color: '#e6a23c'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(230, 162, 60, 0.3)' },
                  { offset: 1, color: 'rgba(230, 162, 60, 0.1)' }
                ]
              }
            }
          },
          {
            name: '注册记录',
            type: 'line',
            stack: 'Total',
            data: registerData,
            smooth: true,
            lineStyle: {
              width: 3,
              color: '#f56c6c'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
                  { offset: 1, color: 'rgba(245, 108, 108, 0.1)' }
                ]
              }
            }
          },
          {
            name: '管理员操作',
            type: 'line',
            stack: 'Total',
            data: adminData,
            smooth: true,
            lineStyle: {
              width: 3,
              color: '#909399'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(144, 147, 153, 0.3)' },
                  { offset: 1, color: 'rgba(144, 147, 153, 0.1)' }
                ]
              }
            }
          },
          {
            name: '修改个人信息',
            type: 'line',
            stack: 'Total',
            data: profileUpdateData,
            smooth: true,
            lineStyle: {
              width: 3,
              color: '#8e44ad'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(142, 68, 173, 0.3)' },
                  { offset: 1, color: 'rgba(142, 68, 173, 0.1)' }
                ]
              }
            }
          }
        ]
      }
    })
    
    // 检查是否有时间趋势数据
    const hasTimeData = computed(() => {
      const { xAxisData } = timeTrendData.value;
      // 检查是否存在x轴数据且长度大于0
      return Array.isArray(xAxisData) && xAxisData.length > 0;
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
          `确定要删除用户 "${record.username}" 的${record.action === 'search' ? '搜索' : record.action === 'favorite' ? '收藏' : record.action}记录吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        try {
          // 调用API删除记录
          await deleteUserRecord(record.id);
          
          // 从本地数据中移除
          const index = recordsData.value.findIndex(r => r.id === record.id);
          if (index !== -1) {
            recordsData.value.splice(index, 1);
          }
          
          // 重新获取数据以更新统计信息
          fetchRecords();
          
          ElMessage.success('删除记录成功');
          
          // 如果是从对话框删除，关闭对话框
          if (fromDialog) {
            recordDetailVisible.value = false;
          }
        } catch (error) {
          console.error('删除记录失败:', error);
          ElMessage.error('删除记录失败');
        }
      } catch (error) {
        // 用户取消操作，不做处理
      }
    }
    
    // 导出数据
    const exportData = async () => {
      try {
        loading.value = true;
        
        // 准备API请求参数
        const params: any = {
          export: true
        };
        
        // 添加用户ID筛选
        if (filterForm.userId) {
          params.user_id = parseInt(filterForm.userId);
        }
        
        // 添加记录类型筛选
        if (filterForm.recordType) {
          params.record_type = filterForm.recordType;
        }
        
        // 添加时间范围筛选
        if (filterForm.timeRange && filterForm.timeRange.length === 2 && filterForm.timeRange[0] && filterForm.timeRange[1]) {
          params.start_date = filterForm.timeRange[0].toISOString().split('T')[0];
          params.end_date = filterForm.timeRange[1].toISOString().split('T')[0];
        }
        
        // 调用导出API
        const response = await getUserRecords(params);
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'user_records.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        ElMessage.success('数据导出成功');
      } catch (error) {
        console.error('导出数据失败:', error);
        ElMessage.error('导出数据失败');
      } finally {
        loading.value = false;
      }
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
      hasTimeData,
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

.no-data-tip {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}
</style> 