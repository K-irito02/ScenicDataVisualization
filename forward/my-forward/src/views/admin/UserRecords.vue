<template>
  <div class="user-records-container">
    <div class="records-header">
      <h2>用户记录查看</h2>
      <div class="filter-form">
        <el-form :inline="true" :model="filterForm" class="demo-form-inline">
          <el-form-item label="用户搜索">
            <el-input v-model="filterForm.userSearch" placeholder="输入用户ID或用户名" clearable />
          </el-form-item>
          <el-form-item label="记录类型">
            <el-select v-model="filterForm.recordType" placeholder="选择记录类型" clearable style="min-width: 180px;">
              <el-option label="搜索记录" value="search" />
              <el-option label="收藏记录" value="favorite" />
              <el-option label="登录记录" value="login" />
              <el-option label="注册记录" value="register" />
              <el-option label="管理员操作" value="admin" />
              <el-option label="修改个人信息" value="profile_update" />
              <el-option label="查看景区详情" value="view_scenic_detail" />
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
    </div>

    <card-container>
      <!-- 图表展示区域 -->
      <div class="charts-container">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-card">
              <div class="chart-title">记录类型分布</div>
              <div v-loading="chartLoading" class="chart-content">
                <div ref="pieChartRef" class="chart" v-if="pieChartData.length > 0"></div>
                <div v-else class="no-data">暂无数据</div>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-card">
              <div class="chart-title">记录趋势</div>
              <div v-loading="chartLoading" class="chart-content">
                <div ref="trendChartRef" class="chart" v-if="trendChartData.xAxisData.length > 0"></div>
                <div v-else class="no-data">暂无数据</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      
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
                  :color="COLOR_MAP.search"
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
                  :color="COLOR_MAP.favorite"
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
                  :color="COLOR_MAP.login"
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
                  :color="COLOR_MAP.register"
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
                  :color="COLOR_MAP.admin"
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
                  :color="COLOR_MAP.profile_update"
                />
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-card">
              <div class="summary-title">查看景区详情</div>
              <div class="summary-content">
                <div class="summary-value">{{ summary.viewScenicDetailRecords }}</div>
                <el-progress
                  :percentage="summary.viewScenicDetailPercentage"
                  :format="() => summary.viewScenicDetailPercentage + '%'"
                  :stroke-width="8"
                  :color="COLOR_MAP.view_scenic_detail"
                />
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
          <el-table-column prop="action" label="记录类型" width="120">
            <template #default="scope">
              <el-tag :type="getTagType(scope.row.action)" class="record-type-tag">
                {{ getActionText(scope.row.action) }}
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
          <el-tag :type="getTagType(currentRecord.action)" class="record-type-tag">
            {{ getActionText(currentRecord.action) }}
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
import { defineComponent, ref, reactive, onMounted, nextTick, watch, onUnmounted } from 'vue'
import CardContainer from '@/components/common/CardContainer.vue'
import { View, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ElMessageBox from 'element-plus/es/components/message-box/index'
import { getUserRecords, deleteUserRecord, getUserRecordsChartData } from '@/api/admin'
import * as echarts from 'echarts'

// 添加颜色映射常量
const COLOR_MAP = {
  'search': '#409EFF',
  'favorite': '#67C23A',
  'login': '#E6A23C',
  'register': '#F56C6C',
  'admin': '#909399',
  'profile_update': '#8E44AD',
  'view_scenic_detail': '#26A69A'
}

// 添加调试日志函数
const DEBUG = true
function logDebug(message: string, data: any = null) {
  if (DEBUG) {
    const logMessage = data ? `${message}: ${JSON.stringify(data)}` : message
    console.log(`[UserRecords] ${logMessage}`)
    
    // 如果数据过大，单独输出
    if (data && Object.keys(data).length > 0) {
      console.log('[UserRecords] 详细数据:', data)
    }
  }
}

export default defineComponent({
  name: 'UserRecords',
  components: {
    CardContainer,
    View,
    Delete
  },
  setup() {
    const loading = ref(false)
    const chartLoading = ref(false)
    const recordsData = ref<any[]>([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalRecords = ref(0)
    const recordDetailVisible = ref(false)
    const currentRecord = ref<any>({})
    
    // 图表DOM引用
    const pieChartRef = ref<HTMLElement | null>(null)
    const trendChartRef = ref<HTMLElement | null>(null)
    // 图表实例
    let pieChart: echarts.ECharts | null = null
    let trendChart: echarts.ECharts | null = null
    
    // 图表数据
    const pieChartData = ref<any[]>([])
    const trendChartData = ref<{
      xAxisData: string[],
      searchData: number[],
      favoriteData: number[],
      loginData: number[],
      registerData: number[],
      adminData: number[],
      profileUpdateData: number[],
      viewScenicDetailData: number[]
    }>({
      xAxisData: [],
      searchData: [],
      favoriteData: [],
      loginData: [],
      registerData: [],
      adminData: [],
      profileUpdateData: [],
      viewScenicDetailData: []
    })
    const trendChartDates = ref<string[]>([])
    const trendChartSeries = ref<any[]>([])
    
    // 筛选表单
    const filterForm = reactive({
      userSearch: '',
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
      viewScenicDetailRecords: 0,
      searchPercentage: 0,
      favoritePercentage: 0,
      loginPercentage: 0,
      registerPercentage: 0,
      adminPercentage: 0,
      profileUpdatePercentage: 0,
      viewScenicDetailPercentage: 0
    })
    
    // 初始化图表
    const initCharts = () => {
      nextTick(() => {
        try {
          // 初始化饼图
          if (pieChartRef.value && !pieChart) {
            pieChart = echarts.init(pieChartRef.value)
            // 设置默认空状态
            pieChart.setOption({
              title: {
                text: '暂无数据',
                left: 'center',
                top: 'center',
                textStyle: {
                  color: '#909399',
                  fontSize: 14
                }
              }
            })
          }
          
          // 初始化趋势图
          if (trendChartRef.value && !trendChart) {
            trendChart = echarts.init(trendChartRef.value)
            // 设置默认空状态
            trendChart.setOption({
              title: {
                text: '暂无数据',
                left: 'center',
                top: 'center',
                textStyle: {
                  color: '#909399',
                  fontSize: 14
                }
              }
            })
          }
          
          // 窗口大小变化时重新调整图表大小
          const resizeHandler = () => {
            try {
              pieChart?.resize()
              trendChart?.resize()
            } catch (error) {
              console.error('调整图表大小时出错:', error)
            }
          }
          
          window.addEventListener('resize', resizeHandler)
          
          // 组件卸载时移除事件监听
          onUnmounted(() => {
            window.removeEventListener('resize', resizeHandler)
            pieChart?.dispose()
            trendChart?.dispose()
          })
          
        } catch (error) {
          console.error('初始化图表时出错:', error)
          ElMessage.error('初始化图表时出错')
        }
      })
    }
    
    // 渲染饼图
    const renderPieChart = () => {
      if (!pieChartRef.value || !pieChartData.value || pieChartData.value.length === 0) return
      
      try {
        // 如果图表实例不存在，初始化它
        if (!pieChart) {
          pieChart = echarts.init(pieChartRef.value)
        }
        
        // 设置颜色映射表，确保饼图和卡片颜色一致
        const typeColorMap = {
          '搜索': COLOR_MAP.search,
          '收藏': COLOR_MAP.favorite,
          '登录': COLOR_MAP.login,
          '注册': COLOR_MAP.register,
          '管理员操作': COLOR_MAP.admin,
          '修改个人信息': COLOR_MAP.profile_update,
          '查看景区详情': COLOR_MAP.view_scenic_detail
        }
        
        const option = {
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 'left',
            data: pieChartData.value.map(item => item.name || '未知')
          },
          color: Object.values(typeColorMap),
          series: [
            {
              name: '记录类型',
              type: 'pie',
              radius: ['40%', '70%'],
              avoidLabelOverlap: false,
              itemStyle: {
                borderRadius: 8,
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
              data: pieChartData.value.map(item => ({
                value: item.count || 0,
                name: item.name || '未知'
              }))
            }
          ]
        }
        
        pieChart.setOption(option)
      } catch (error) {
        console.error('渲染饼图时出错:', error)
      }
    }
    
    // 渲染趋势图
    const renderTrendChart = () => {
      if (!trendChartRef.value) {
        console.warn('趋势图DOM引用不存在')
        return
      }
      
      try {
        // 如果图表实例不存在，初始化它
        if (!trendChart) {
          logDebug('初始化趋势图实例')
          trendChart = echarts.init(trendChartRef.value)
        }
        
        // 检查是否有真实数据
        if (!trendChartData.value?.xAxisData?.length) {
          // 显示无数据状态
          logDebug('趋势图没有真实数据，显示无数据状态')
          trendChart.setOption({
            title: {
              text: '暂无趋势数据',
              left: 'center',
              top: 'center',
              textStyle: {
                color: '#909399',
                fontSize: 14
              }
            }
          })
          return
        }
        
        // 过滤掉所有系列都为0的数据点
        const filteredData = filterEmptyPoints(trendChartData.value)
        
        // 构建趋势图配置
        const option = {
          tooltip: {
            trigger: 'axis',
            formatter: function(params: any) {
              let result = params[0].axisValue + '<br/>'
              params.forEach((item: any) => {
                result += `${item.marker} ${item.seriesName}: ${item.value}<br/>`
              })
              return result
            }
          },
          legend: {
            data: ['搜索', '收藏', '登录', '注册', '管理员操作', '修改个人信息', '查看景区详情'],
            top: 10
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          toolbox: {
            feature: {
              saveAsImage: {}
            }
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: filteredData.xAxisData,
            axisLabel: {
              interval: 0, // 强制显示所有标签
              formatter: function(value: string) {
                // 检查日期格式
                if (!value.match(/^\d{4}-\d{2}-\d{2}$/)) {
                  return value;
                }
                
                // 分解日期
                const parts = value.split('-');
                const year = parts[0];
                const month = parts[1];
                const day = parts[2];
                
                // 检查是否是第一个日期或月份的第一天
                const index = filteredData.xAxisData.indexOf(value);
                const isFirstDate = index === 0;
                const isPreviousMonthDifferent = index > 0 && 
                  !filteredData.xAxisData[index-1].startsWith(`${year}-${month}`);
                const isPreviousYearDifferent = index > 0 && 
                  !filteredData.xAxisData[index-1].startsWith(year);
                
                // 决定显示格式
                if (isFirstDate || isPreviousYearDifferent) {
                  // 第一个点或年份变化时显示完整年月日
                  return `{yearStyle|${year}}\n{monthStyle|${month}月}\n{dayStyle|${day}日}`;
                } else if (isPreviousMonthDifferent) {
                  // 月份变化时显示月日
                  return `{monthStyle|${month}月}\n{dayStyle|${day}日}`;
                } else {
                  // 其他情况只显示日
                  return `{dayStyle|${day}日}`;
                }
              },
              rich: {
                yearStyle: {
                  color: '#303133',
                  fontWeight: 'bold',
                  fontSize: 14,
                  height: 15,
                  lineHeight: 20
                },
                monthStyle: {
                  color: '#606266',
                  fontWeight: 'bold',
                  fontSize: 12,
                  height: 14,
                  lineHeight: 18
                },
                dayStyle: {
                  color: '#909399',
                  fontSize: 10,
                  height: 12,
                  lineHeight: 14
                }
              }
            }
          },
          yAxis: {
            type: 'value',
            minInterval: 1, // 确保y轴显示整数
            axisLabel: {
              formatter: '{value}'
            }
          },
          series: [
            {
              name: '搜索',
              type: 'line',
              data: filteredData.searchData,
              smooth: true, // 使用平滑曲线
              smoothMonotone: 'x', // 确保曲线平滑但不过度弯曲
              symbolSize: 6,
              lineStyle: { width: 2 },
              itemStyle: { color: COLOR_MAP.search }
            },
            {
              name: '收藏',
              type: 'line',
              data: filteredData.favoriteData,
              smooth: true,
              smoothMonotone: 'x',
              symbolSize: 6,
              lineStyle: { width: 2 },
              itemStyle: { color: COLOR_MAP.favorite }
            },
            {
              name: '登录',
              type: 'line',
              data: filteredData.loginData,
              smooth: true,
              smoothMonotone: 'x',
              symbolSize: 6,
              lineStyle: { width: 2 },
              itemStyle: { color: COLOR_MAP.login }
            },
            {
              name: '注册',
              type: 'line',
              data: filteredData.registerData,
              smooth: true,
              smoothMonotone: 'x',
              symbolSize: 6,
              lineStyle: { width: 2 },
              itemStyle: { color: COLOR_MAP.register }
            },
            {
              name: '管理员操作',
              type: 'line',
              data: filteredData.adminData,
              smooth: true,
              smoothMonotone: 'x',
              symbolSize: 6,
              lineStyle: { width: 2 },
              itemStyle: { color: COLOR_MAP.admin }
            },
            {
              name: '修改个人信息',
              type: 'line',
              data: filteredData.profileUpdateData,
              smooth: true,
              smoothMonotone: 'x',
              symbolSize: 6,
              lineStyle: { width: 2 },
              itemStyle: { color: COLOR_MAP.profile_update }
            },
            {
              name: '查看景区详情',
              type: 'line',
              data: filteredData.viewScenicDetailData,
              smooth: true,
              smoothMonotone: 'x',
              symbolSize: 6,
              lineStyle: { width: 2 },
              itemStyle: { color: COLOR_MAP.view_scenic_detail }
            }
          ]
        }
        
        logDebug('设置趋势图配置', {
          xAxisDataLength: option.xAxis.data.length,
          seriesCount: option.series.length
        })
        
        // 记录每个系列的详细信息
        option.series.forEach((series, index) => {
          logDebug(`系列 ${index+1} 详情`, {
            name: series.name,
            type: series.type,
            dataLength: series.data.length
          })
        })
        
        trendChart.setOption(option, true) // 使用true以完全覆盖之前的选项
        logDebug('趋势图渲染完成')
      } catch (error) {
        console.error('渲染趋势图时出错:', error)
        // 输出详细错误堆栈
        if (error instanceof Error) {
          console.error(error.stack)
        }
      }
    }
    
    // 过滤掉所有系列都为0的数据点
    const filterEmptyPoints = (data: any) => {
      const result = {
        xAxisData: [] as string[],
        searchData: [] as number[],
        favoriteData: [] as number[],
        loginData: [] as number[],
        registerData: [] as number[],
        adminData: [] as number[],
        profileUpdateData: [] as number[],
        viewScenicDetailData: [] as number[]
      }
      
      // 检查每个点，如果所有系列都为0则跳过
      for (let i = 0; i < data.xAxisData.length; i++) {
        const allZero = [
          data.searchData[i],
          data.favoriteData[i],
          data.loginData[i],
          data.registerData[i],
          data.adminData[i],
          data.profileUpdateData[i],
          data.viewScenicDetailData[i]
        ].every(val => val === 0 || val === null || val === undefined)
        
        if (!allZero) {
          result.xAxisData.push(data.xAxisData[i])
          result.searchData.push(data.searchData[i])
          result.favoriteData.push(data.favoriteData[i])
          result.loginData.push(data.loginData[i])
          result.registerData.push(data.registerData[i])
          result.adminData.push(data.adminData[i])
          result.profileUpdateData.push(data.profileUpdateData[i])
          result.viewScenicDetailData.push(data.viewScenicDetailData[i])
        }
      }
      
      return result
    }
    
    // 获取记录数据
    const fetchRecords = async () => {
      loading.value = true
      
      try {
        // 准备API请求参数
        const params: any = {
          page: currentPage.value,
          pageSize: pageSize.value
        }
        
        // 处理用户搜索（支持ID和用户名）
        if (filterForm.userSearch && filterForm.userSearch.trim() !== '') {
          // 判断是数字（ID）还是字符串（用户名）
          if (!isNaN(Number(filterForm.userSearch))) {
            params.user_id = parseInt(filterForm.userSearch)
          } else {
            // 用户名精确匹配
            params.username = filterForm.userSearch
          }
        }
        
        // 添加记录类型筛选
        if (filterForm.recordType) {
          params.record_type = filterForm.recordType
        }
        
        // 添加时间范围筛选
        if (filterForm.timeRange && filterForm.timeRange.length === 2 && filterForm.timeRange[0] && filterForm.timeRange[1]) {
          params.start_date = filterForm.timeRange[0].toISOString().split('T')[0]
          params.end_date = filterForm.timeRange[1].toISOString().split('T')[0]
        }

        // 从API获取数据
        const response = await getUserRecords(params)
        
        // 更新数据
        recordsData.value = response.data.data
        totalRecords.value = response.data.total
        
        // 更新统计数据
        if (response.data.summary) {
          updateSummary(response.data.summary)
        }
        
        // 获取图表数据
        fetchChartData()
      } catch (error) {
        console.error('获取记录数据失败:', error)
        ElMessage.error('获取记录数据失败')
      } finally {
        loading.value = false
      }
    }
    
    // 获取图表数据
    const fetchChartData = async () => {
      chartLoading.value = true
      
      try {
        // 准备图表数据请求参数
        const params: any = {}
        
        // 处理用户搜索（支持ID和用户名）
        if (filterForm.userSearch && filterForm.userSearch.trim() !== '') {
          // 判断是数字（ID）还是字符串（用户名）
          if (!isNaN(Number(filterForm.userSearch))) {
            params.user_id = parseInt(filterForm.userSearch)
          } else {
            // 用户名精确匹配
            params.username = filterForm.userSearch
          }
        }
        
        // 添加记录类型筛选
        if (filterForm.recordType) {
          params.record_type = filterForm.recordType
        }
        
        // 添加时间范围筛选
        if (filterForm.timeRange && filterForm.timeRange.length === 2 && filterForm.timeRange[0] && filterForm.timeRange[1]) {
          params.start_date = filterForm.timeRange[0].toISOString().split('T')[0]
          params.end_date = filterForm.timeRange[1].toISOString().split('T')[0]
        }
        
        logDebug('开始获取图表数据，参数', params)
        
        // 从API获取图表数据
        const response = await getUserRecordsChartData(params)
        
        logDebug('获取图表数据响应', response)
        
        // 确保响应是有效的对象且包含所需的数据
        if (response && response.data) {
          // 更新饼图数据 - 确保数据是数组
          if (response.data.pie_data && Array.isArray(response.data.pie_data)) {
            pieChartData.value = response.data.pie_data
            logDebug('饼图数据解析成功', pieChartData.value)
          } else {
            console.warn('收到的饼图数据格式不正确', response.data.pie_data)
            pieChartData.value = []
          }
          
          // 更新趋势图数据 - 使用新的数据结构
          if (response.data.trend_data) {
            const trendData = response.data.trend_data
            
            // 使用新的数据结构更新趋势图数据
            trendChartData.value = {
              xAxisData: Array.isArray(trendData.xAxisData) ? trendData.xAxisData : [],
              searchData: Array.isArray(trendData.searchData) ? trendData.searchData : [],
              favoriteData: Array.isArray(trendData.favoriteData) ? trendData.favoriteData : [],
              loginData: Array.isArray(trendData.loginData) ? trendData.loginData : [],
              registerData: Array.isArray(trendData.registerData) ? trendData.registerData : [],
              adminData: Array.isArray(trendData.adminData) ? trendData.adminData : [],
              profileUpdateData: Array.isArray(trendData.profileUpdateData) ? trendData.profileUpdateData : [],
              viewScenicDetailData: Array.isArray(trendData.viewScenicDetailData) ? trendData.viewScenicDetailData : []
            }
            
            // 为了兼容性，同时更新旧的数据结构
            trendChartDates.value = trendChartData.value.xAxisData
            
            logDebug('趋势图数据解析成功', trendChartData.value)
          } else {
            console.warn('收到的趋势图数据格式不正确', response.data.trend_data)
            trendChartData.value = {
              xAxisData: [],
              searchData: [],
              favoriteData: [],
              loginData: [],
              registerData: [],
              adminData: [],
              profileUpdateData: [],
              viewScenicDetailData: []
            }
            trendChartDates.value = []
            trendChartSeries.value = []
          }
        } else {
          console.warn('API响应格式不正确', response)
          pieChartData.value = []
          trendChartData.value = {
            xAxisData: [],
            searchData: [],
            favoriteData: [],
            loginData: [],
            registerData: [],
            adminData: [],
            profileUpdateData: [],
            viewScenicDetailData: []
          }
          trendChartDates.value = []
          trendChartSeries.value = []
        }
        
        // 更新图表
        nextTick(() => {
          try {
            logDebug('准备渲染图表', {
              hasPieChartData: pieChartData.value.length > 0,
              hasTrendChartData: trendChartData.value.xAxisData.length > 0
            })
            
            if (pieChartData.value.length > 0) {
              renderPieChart()
            }
            
            // 使用新的条件判断
            if (trendChartData.value.xAxisData.length > 0) {
              renderTrendChart()
            }
          } catch (chartError) {
            console.error('渲染图表时出错:', chartError)
            ElMessage.error('渲染图表时出错')
          }
        })
      } catch (error) {
        console.error('获取图表数据失败:', error)
        ElMessage.error('获取图表数据失败，请稍后再试')
        
        // 清空图表数据
        pieChartData.value = []
        trendChartData.value = {
          xAxisData: [],
          searchData: [],
          favoriteData: [],
          loginData: [],
          registerData: [],
          adminData: [],
          profileUpdateData: [],
          viewScenicDetailData: []
        }
        trendChartDates.value = []
        trendChartSeries.value = []
      } finally {
        chartLoading.value = false
      }
    }
    
    // 监听筛选条件变化，更新图表
    watch([() => filterForm.userSearch, () => filterForm.recordType, () => filterForm.timeRange], () => {
      // 当筛选条件改变时，只有在调用fetchRecords后才会触发图表更新
    })
    
    // 更新统计数据
    const updateSummary = (summaryData: any) => {
      summary.totalRecords = summaryData.totalRecords || 0
      summary.searchRecords = summaryData.searchRecords || 0
      summary.favoriteRecords = summaryData.favoriteRecords || 0
      summary.loginRecords = summaryData.loginRecords || 0
      summary.registerRecords = summaryData.registerRecords || 0
      summary.adminRecords = summaryData.adminRecords || 0
      summary.profileUpdateRecords = summaryData.profileUpdateRecords || 0
      summary.viewScenicDetailRecords = summaryData.viewScenicDetailRecords || 0
      
      summary.searchPercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.searchRecords / summary.totalRecords) * 100)
      
      summary.favoritePercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.favoriteRecords / summary.totalRecords) * 100)
      
      summary.loginPercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.loginRecords / summary.totalRecords) * 100)
      
      summary.registerPercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.registerRecords / summary.totalRecords) * 100)
      
      summary.adminPercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.adminRecords / summary.totalRecords) * 100)
      
      summary.profileUpdatePercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.profileUpdateRecords / summary.totalRecords) * 100)
      
      summary.viewScenicDetailPercentage = summary.totalRecords === 0 ? 0 : 
        Math.round((summary.viewScenicDetailRecords / summary.totalRecords) * 100)
    }
    
    // 处理筛选
    const handleFilter = () => {
      currentPage.value = 1
      fetchRecords()
    }
    
    // 重置筛选
    const resetFilter = () => {
      filterForm.userSearch = ''
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
          `确定要删除用户 "${record.username}" 的${getActionText(record.action)}记录吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        try {
          // 调用API删除记录
          await deleteUserRecord(record.id)
          
          // 从本地数据中移除
          const index = recordsData.value.findIndex(r => r.id === record.id)
          if (index !== -1) {
            recordsData.value.splice(index, 1)
          }
          
          // 重新获取数据以更新统计信息
          fetchRecords()
          
          ElMessage.success('删除记录成功')
          
          // 如果是从对话框删除，关闭对话框
          if (fromDialog) {
            recordDetailVisible.value = false
          }
        } catch (error) {
          console.error('删除记录失败:', error)
          ElMessage.error('删除记录失败')
        }
      } catch (error) {
        // 用户取消操作，不做处理
      }
    }
    
    // 导出数据
    const exportData = async () => {
      loading.value = true
      
      try {
        // 准备导出数据的API请求参数
        const params: any = {
          export: true
        }
        
        // 处理用户搜索（支持ID和用户名）
        if (filterForm.userSearch && filterForm.userSearch.trim() !== '') {
          // 判断是数字（ID）还是字符串（用户名）
          if (!isNaN(Number(filterForm.userSearch))) {
            params.user_id = parseInt(filterForm.userSearch)
          } else {
            // 用户名精确匹配
            params.username = filterForm.userSearch
          }
        }
        
        // 添加记录类型筛选
        if (filterForm.recordType) {
          params.record_type = filterForm.recordType
        }
        
        // 添加时间范围筛选
        if (filterForm.timeRange && filterForm.timeRange.length === 2 && filterForm.timeRange[0] && filterForm.timeRange[1]) {
          params.start_date = filterForm.timeRange[0].toISOString().split('T')[0]
          params.end_date = filterForm.timeRange[1].toISOString().split('T')[0]
        }
        
        // 调用导出API
        const response = await getUserRecords(params)
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'user_records.csv')
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        ElMessage.success('数据导出成功')
      } catch (error) {
        console.error('导出数据失败:', error)
        ElMessage.error('导出数据失败')
      } finally {
        loading.value = false
      }
    }
    
    // 获取操作类型显示文本
    const getActionText = (action: string) => {
      if (action === 'search') return '搜索';
      if (action === 'favorite') return '收藏';
      if (action === 'login') return '登录';
      if (action === 'register') return '注册';
      if (action === 'admin') return '管理员操作';
      if (action === 'profile_update') return '修改个人信息';
      if (action === 'view_scenic_detail') return '查看景区详情';
      return action;
    }
    
    // 获取标签类型
    const getTagType = (action: string) => {
      if (action === 'search') return 'primary';
      if (action === 'favorite') return 'success';
      if (action === 'login') return 'warning';
      if (action === 'register') return 'danger';
      if (action === 'admin') return 'info';
      if (action === 'profile_update') return 'purple';
      if (action === 'view_scenic_detail') return 'success';
      return 'info';
    }
    
    onMounted(() => {
      fetchRecords()
      initCharts()
    })
    
    return {
      loading,
      chartLoading,
      recordsData,
      currentPage,
      pageSize,
      totalRecords,
      filterForm,
      summary,
      recordDetailVisible,
      currentRecord,
      pieChartData,
      trendChartData,
      trendChartDates,
      trendChartSeries,
      pieChartRef,
      trendChartRef,
      getActionText,
      getTagType,
      handleFilter,
      resetFilter,
      handleCurrentChange,
      handleSizeChange,
      handleViewRecord,
      handleDeleteRecord,
      exportData,
      COLOR_MAP
    }
  }
})
</script>

<style scoped>
.user-records-container {
  padding: 20px;
}

/* 彻底禁止用户搜索框的放大效果 */
.filter-form :deep(.el-input),
.filter-form :deep(.el-input__wrapper),
.filter-form :deep(.el-input__inner) {
  transition: none !important;
  transform: none !important;
}

.filter-form :deep(.el-input:hover),
.filter-form :deep(.el-input__wrapper:hover),
.filter-form :deep(.el-input__inner:hover),
.filter-form :deep(.el-input:focus),
.filter-form :deep(.el-input__wrapper:focus),
.filter-form :deep(.el-input__inner:focus),
.filter-form :deep(.el-input__wrapper.is-focus) {
  transform: none !important;
  box-shadow: none !important;
}

.records-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 10px 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.records-header h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.filter-form {
  flex-grow: 1;
  display: flex;
  justify-content: flex-end;
}

.charts-container {
  margin-top: 30px;
}

.chart-card {
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 15px;
  height: 400px;
  margin-bottom: 20px;
}

.chart-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 15px;
}

.chart-content {
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart {
  width: 100%;
  height: 100%;
}

.no-data {
  color: #909399;
  font-size: 14px;
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.el-tag {
  text-transform: capitalize;
}

.record-type-tag {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 10px;
  margin: 0 auto;
  min-width: 80px;
  height: 28px;
}

/* 定义紫色标签样式 - 修改为淡紫色 */
:deep(.el-tag--purple) {
  color: #fff;
  background-color: #d1adda; /* 淡紫色 */
}
</style> 