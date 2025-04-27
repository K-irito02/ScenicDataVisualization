<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted, watch } from 'vue'
import { useScenicStore } from '@/stores/scenic'
import * as echarts from 'echarts'
// 导入本地地图数据
import chinaJson from '@/assets/geojson/country/中国.json'
import { ElMessage } from 'element-plus'
// 引入图标组件
import { Loading, DataAnalysis } from '@element-plus/icons-vue'

// 直辖市列表
const MUNICIPALITIES = ['北京市', '上海市', '天津市', '重庆市']
// 直辖市默认的"城市"名称
const DEFAULT_MUNICIPALITY_CITY = '市辖区'

// 判断是否为直辖市
const isMunicipality = (provinceName: string) => {
  return MUNICIPALITIES.includes(provinceName)
}

// 确保中国地图数据被正确注册
try {
  echarts.registerMap('china', chinaJson as any)
  console.log('中国地图数据注册成功')
} catch(error) {
  console.error('中国地图数据注册失败:', error)
}

// 当前地图层级 0-全国 1-省级 2-市级
const currentMapLevel = ref(0)
// 地图加载中状态
const mapLoading = ref(false)

const scenicStore = useScenicStore()
const loading = ref(false)
const mapChart = ref<HTMLElement | null>(null)
const barChart = ref<HTMLElement | null>(null)
const provinceMapChart = ref<HTMLElement | null>(null)
const mapChartInstance = ref<echarts.ECharts | null>(null)
const barChartInstance = ref<echarts.ECharts | null>(null)
const provinceMapChartInstance = ref<echarts.ECharts | null>(null)
const showProvinceMap = ref(false)
const currentProvince = ref('')
const dataReady = ref(false)
const provinceMapError = ref(false)
// 新增变量，用于存储当前省份的市级数据
const cityData = ref<Array<{name: string, value: number}>>([])

// 新增市级地图相关的状态变量
const showCityMap = ref(false)
const currentCity = ref('')
const cityMapChartInstance = ref<echarts.ECharts | null>(null)
const cityMapChart = ref<HTMLElement | null>(null)
const cityMapError = ref(false)

// 初始化地图
const initMapChart = () => {
  if (!mapChart.value) {
    console.error('地图容器不存在')
    return
  }
  
  console.log('开始初始化地图', mapChart.value)
  
  // 如果已经初始化过，先销毁原实例
  if (mapChartInstance.value) {
    mapChartInstance.value.dispose()
  }
  
  try {
    // 创建新实例
    mapChartInstance.value = echarts.init(mapChart.value)
    console.log('地图实例已创建', mapChartInstance.value)
    
    const option = {
      title: {
        text: '全国景区分布热力图',
        left: 'center',
        textStyle: {
          fontSize: 18
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} 个景区'
      },
      // 添加visualMap组件以实现热力图效果
      visualMap: {
        min: 0,
        // 最大值会在updateCharts中根据实际数据动态设置
        max: 100,
        left: 'left',
        top: 'bottom',
        text: ['高', '低'],
        calculable: true,
        inRange: {
          color: ['#edf8fb', '#b2e2e2', '#66c2a4', '#2ca25f', '#006d2c']
        }
      },
      // 中国地图配置
      series: [
        {
          name: '中国',
          type: 'map',
          map: 'china',
          roam: true, // 允许缩放和平移
          zoom: 1.2, // 默认放大一点
          // 标签显示
          label: {
            show: true,
            fontSize: 8,
            color: '#333'
          },
          // 省份样式
          itemStyle: {
            areaColor: '#edf8fb',
            borderColor: '#999',
            borderWidth: 0.5
          },
          // 高亮效果
          emphasis: {
            label: {
              show: true,
              fontSize: 12,
              color: '#000'
            },
            itemStyle: {
              areaColor: '#b3daff'
            }
          },
          // 初始为空数据，后续可以更新
          data: []
        }
      ]
    }
    
    // 应用配置
    mapChartInstance.value.setOption(option)
    console.log('地图配置已设置')
    
    // 点击事件
    mapChartInstance.value.on('click', (params: any) => {
      if (params.componentType === 'series') {
        const provinceName = params.name
        console.log('点击了地图：', provinceName)
        showProvinceDetail(provinceName)
      }
    })
    
    // 监听图表渲染完成事件
    mapChartInstance.value.on('rendered', () => {
      console.log('地图渲染完成')
    })
    
    // 强制触发一次重绘
    setTimeout(() => {
      if (mapChartInstance.value) {
        console.log('强制重绘地图')
        mapChartInstance.value.resize()
      }
    }, 100)
  } catch (error) {
    console.error('初始化地图失败:', error)
    ElMessage.error('地图加载失败，请刷新页面重试')
  }
}

// 初始化柱状图
const initBarChart = () => {
  if (!barChart.value) return
  
  // 如果已经初始化过，先销毁原实例
  if (barChartInstance.value) {
    barChartInstance.value.dispose()
  }
  
  // 创建新实例
  barChartInstance.value = echarts.init(barChart.value)
  
  const option = {
    title: {
      text: '省份景区数量统计',
      left: 'center',
      textStyle: {
        fontSize: 18
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '{b}: {c} 个景区'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%', // 增加底部空间以便于显示标签
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [],
      axisLabel: {
        interval: 0,
        rotate: 45,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      name: '景区数量',
      min: 0,
      // 固定最大值以确保差距明显
      max: function(value: any) {
        return Math.ceil(value.max * 1.1); // 增加最大值的10%作为上限
      },
      splitNumber: 5
    },
    series: [
      {
        name: '景区数量',
        type: 'bar',
        data: [],
        barWidth: '50%', // 调整柱宽
        // 应用渐变色，使柱状图更醒目
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#0364bb' }
          ]),
          // 添加边框
          borderColor: '#0364bb',
          borderWidth: 0.5,
          borderRadius: [3, 3, 0, 0] // 柱状图圆角
        },
        // 在柱顶显示数值
        label: {
          show: true,
          position: 'top',
          formatter: '{c}',
          fontSize: 10,
          color: '#333'
        },
        // 鼠标悬停效果
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#ffb74d' },
              { offset: 0.7, color: '#ff9800' },
              { offset: 1, color: '#f57c00' }
            ]),
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.3)'
          }
        }
      }
    ]
  }
  
  // 应用配置
  barChartInstance.value.setOption(option)
  
  // 点击事件
  barChartInstance.value.on('click', (params: any) => {
    const provinceName = params.name
    console.log('点击了柱状图：', provinceName)
    showProvinceDetail(provinceName)
  })
}

// 显示省份详情
const showProvinceDetail = (provinceName: string) => {
  console.log('准备显示省份详情:', provinceName)
  if (!provinceName) {
    console.error('省份名称为空')
    ElMessage.warning('选择的省份无效')
    return
  }
  
  // 处理数据为空的情况
  if (!scenicStore.provinceData || scenicStore.provinceData.length === 0) {
    console.error('省份数据为空，无法查找省份:', provinceName)
    ElMessage.warning(`暂无${provinceName}数据`)
    return
  }
  
  const province = scenicStore.provinceData.find(item => item.name === provinceName)
  
  if (!province) {
    console.error(`未找到省份: ${provinceName}`)
    ElMessage.warning(`未找到${provinceName}数据`)
    return
  }
  
  if (!province.scenics || province.scenics.length === 0) {
    console.warn(`${provinceName}没有景区数据`)
    ElMessage.warning(`${provinceName}暂无景区数据`)
    return
  }
  
  console.log(`找到${provinceName}的景区数据:`, province.scenics.length)
  
  // 设置当前省份和显示状态
  currentProvince.value = provinceName
  currentMapLevel.value = 1
  
  // 高亮柱状图中的当前省份
  highlightProvinceInBarChart(provinceName);
  
  // 切换显示状态 - 提前切换以便DOM准备好
  showProvinceMap.value = true;
  
  // 获取API数据并初始化地图
  loadProvinceDataAndInitMap(provinceName);
}

// 高亮柱状图中的省份
const highlightProvinceInBarChart = (provinceName: string) => {
  if (!barChartInstance.value) return;
  
  try {
    const option = barChartInstance.value.getOption();
    const seriesData = (option as any).series[0].data;
    
    const newData = seriesData.map((item: any) => {
      if (item.name === provinceName) {
        return {
          ...item,
          itemStyle: {
            color: '#ff4500', // 高亮颜色
            borderColor: '#ff4500',
            borderWidth: 1
          }
        }
      }
      return {
        ...item,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#0364bb' }
          ]),
          borderColor: '#0364bb',
          borderWidth: 0.5
        }
      }
    });
    
    barChartInstance.value.setOption({
      series: [{
        data: newData
      }]
    });
  } catch (error) {
    console.error('更新柱状图高亮失败:', error);
  }
}

// 加载省份数据并初始化地图
const loadProvinceDataAndInitMap = async (provinceName: string) => {
  console.log(`加载${provinceName}数据并初始化地图`);
  mapLoading.value = true;
  
  try {
    // 1. 确保DOM已准备好
    await nextTick();
    if (!provinceMapChart.value) {
      console.error('省份地图容器不存在');
      ElMessage.error('地图容器加载失败，请重试');
      return;
    }
    
    // 2. 获取省份城市数据
    console.log(`开始加载${provinceName}的城市景区分布数据`);
    const cityDistData = await scenicStore.getProvinceCityDistribution(provinceName);
    
    // 特殊调试：输出重庆市的数据结构
    if (provinceName === '重庆市') {
      console.log('重庆市城市数据结构:', JSON.stringify(cityDistData));
    }
    
    if (!cityDistData || cityDistData.length === 0) {
      console.warn(`${provinceName}没有城市数据`);
      ElMessage.warning(`暂无${provinceName}的城市分布数据`);
      mapLoading.value = false;
      return;
    }
    
    // 3. 更新cityData
    cityData.value = cityDistData;
    console.log(`成功加载${provinceName}的${cityDistData.length}个城市数据:`, cityDistData);
    
    // 4. 检查是否为直辖市，如果是直辖市且只有"市辖区"
    if (isMunicipality(provinceName) && (cityDistData.length === 1 || cityDistData.some((item: any) => item.name === DEFAULT_MUNICIPALITY_CITY))) {
      console.log(`检测到直辖市${provinceName}，尝试直接获取区县数据`);
      
      try {
        // 直接获取区县数据
        const districtData = await scenicStore.getDistrictDistribution(provinceName, DEFAULT_MUNICIPALITY_CITY);
        
        // 特殊调试：输出重庆市的区县数据
        if (provinceName === '重庆市') {
          console.log('重庆市区县数据(原始):', JSON.stringify(districtData));
          // 检查是否有空的区县名称
          const emptyNames = districtData.filter((d: any) => !d.name || d.name.trim() === '');
          if (emptyNames.length > 0) {
            console.warn('存在空的区县名称:', emptyNames);
          }
        }
        
        if (districtData && districtData.length > 0) {
          console.log(`成功获取到${provinceName}的${districtData.length}个区县数据`);
          
          // 验证区县数据
          const validatedData = districtData.map((district: { name: string; value: any }) => {
            // 确保值是数字
            const numValue = Number(district.value);
            const value = isNaN(numValue) ? 0 : numValue;
            
            // 确保区县名称不为空
            const name = district.name && district.name.trim() !== '' ? district.name : '未知区县';
            
            if (isNaN(numValue)) {
              console.warn(`区县 ${name} 的景区数量值 ${district.value} 无效，已替换为0`);
            }
            
            return {
              name: name,
              value: value
            };
          });
          
          // 特殊调试：输出重庆市的验证后区县数据
          if (provinceName === '重庆市') {
            console.log('重庆市区县数据(验证后):', JSON.stringify(validatedData));
          }
          
          // 记录验证后的数据
          console.log(`验证后的区县数据:`, validatedData);
          
          // 将区县数据作为城市数据使用
          cityData.value = validatedData;
          
          // 更新柱状图
          updateBarChartWithCityData(true); // 传递参数表示这是直辖市的区县数据
        } else {
          console.warn(`未能获取到${provinceName}的区县数据，将使用原城市数据`);
          updateBarChartWithCityData();
        }
      } catch (error) {
        console.error(`获取${provinceName}区县数据失败:`, error);
        updateBarChartWithCityData();
      }
    } else {
      // 5. 更新柱状图
      updateBarChartWithCityData();
    }
    
    // 6. 初始化地图
    setTimeout(() => {
      initProvinceMapWithApiData(provinceName, cityData.value);
    }, 300);
  } catch (error) {
    console.error(`加载省份数据失败:`, error);
    ElMessage.error(`加载数据失败，请稍后重试`);
    provinceMapError.value = true;
  } finally {
    mapLoading.value = false;
  }
}

// 作为initProvinceMapWithApiData的包装函数，解决函数名不匹配问题
const initProvinceMap = (provinceName: string, scenics: any[]) => {
  console.log(`包装函数：初始化${provinceName}地图`);
  // 从省份景区数据中提取城市分布数据
  const cityDistributionData: Array<{name: string, value: number}> = [];
  if (scenics && scenics.length > 0) {
    // 统计每个城市的景区数量
    const cityCount: Record<string, number> = {};
    scenics.forEach(spot => {
      if (spot.city) {
        if (!cityCount[spot.city]) {
          cityCount[spot.city] = 0;
        }
        cityCount[spot.city]++;
      }
    });
    
    // 转换为数组格式
    Object.keys(cityCount).forEach(city => {
      cityDistributionData.push({
        name: city,
        value: cityCount[city]
      });
    });
  }
  
  // 调用实际的初始化函数
  initProvinceMapWithApiData(provinceName, cityDistributionData);
}

// 使用API数据初始化省份地图
const initProvinceMapWithApiData = (provinceName: string, cityData: any[]) => {
  if (!provinceMapChart.value) return;
  
  provinceMapError.value = false;
  
  // 销毁旧实例
  if (provinceMapChartInstance.value) {
    provinceMapChartInstance.value.dispose();
  }
  
  // 创建新实例
  provinceMapChartInstance.value = echarts.init(provinceMapChart.value);
  provinceMapChartInstance.value.showLoading();
  
  // 加载地图JSON
  try {
    import(/* webpackChunkName: "province-map" */ `@/assets/geojson/provinces/${provinceName}.json`)
      .then((provinceJson) => {
        if (!provinceMapChartInstance.value) return;
        provinceMapChartInstance.value.hideLoading();
        
        try {
          // 注册地图
          echarts.registerMap(provinceName, provinceJson.default);
          console.log(`${provinceName}地图数据注册成功`);
          
          // 获取地图中包含的区域名称
          const geoJSON = provinceJson.default;
          const mapRegions = geoJSON.features.map((feature: any) => feature.properties.name);
          console.log(`${provinceName}地图包含的区域名称:`, mapRegions);
          
          // 特殊调试：如果是重庆市，检查地图区域与数据名称的匹配情况
          if (provinceName === '重庆市') {
            console.log('重庆市地图区域名称:', mapRegions);
            console.log('重庆市数据区县名称:', cityData.map(item => item.name));
            
            // 检查名称匹配情况
            const matchedNames = cityData.filter(item => mapRegions.includes(item.name));
            const unmatchedNames = cityData.filter(item => !mapRegions.includes(item.name));
            
            console.log('匹配的区县名称数量:', matchedNames.length);
            console.log('未匹配的区县名称:', unmatchedNames.map(item => item.name));
            
            // 对于重庆市，尝试修正区县名称
            if (unmatchedNames.length > 0) {
              console.log('尝试修正重庆市区县名称');
              // 示例：添加"区"或"县"后缀
              cityData = cityData.map(item => {
                if (!mapRegions.includes(item.name)) {
                  // 尝试添加后缀
                  const withDistrict = item.name + '区';
                  const withCounty = item.name + '县';
                  
                  if (mapRegions.includes(withDistrict)) {
                    console.log(`修正区县名称: ${item.name} -> ${withDistrict}`);
                    return { ...item, name: withDistrict };
                  } else if (mapRegions.includes(withCounty)) {
                    console.log(`修正区县名称: ${item.name} -> ${withCounty}`);
                    return { ...item, name: withCounty };
                  }
                }
                return item;
              });
            }
          }
          
          // 准备热力图数据，确保数据值有效
          const data = cityData.map(city => {
            // 确保值是数字
            const numValue = Number(city.value);
            const value = isNaN(numValue) ? 0 : numValue;
            
            // 记录日志以便调试
            if (isNaN(numValue)) {
              console.warn(`${city.name} 的景区数量值 ${city.value} 无效，已替换为0`);
            }
            
            // 检查名称是否在地图中存在
            if (!mapRegions.includes(city.name)) {
              console.warn(`区域 ${city.name} 在${provinceName}地图中不存在`);
            }
            
            return {
              name: city.name,
              value: value
            };
          });
          
          console.log(`热力图数据准备完成:`, data);
          
          // 找出最大值
          const maxValue = Math.max(...data.map(item => item.value), 0);
          console.log(`最大值: ${maxValue}`);
          
          // 检查是否为直辖市
          const isCurrentProvinceMunicipality = MUNICIPALITIES.includes(provinceName);
          
          // 配置热力图
          const option = {
            title: {
              text: `${provinceName}景区分布热力图`,
              subtext: isCurrentProvinceMunicipality ? '(直辖市显示区县级数据)' : '',
              left: 'center',
              textStyle: {
                fontSize: 18
              },
              subtextStyle: {
                fontSize: 12,
                color: '#666'
              }
            },
            tooltip: {
              trigger: 'item',
              formatter: function(params: any) {
                // 确保值是有效数字
                const value = isNaN(params.value) ? 0 : params.value;
                return `${params.name}: ${value} 个景区`;
              }
            },
            visualMap: {
              min: 0,
              max: maxValue > 0 ? maxValue : 10,
              left: 'left',
              top: 'bottom',
              text: ['高', '低'],
              calculable: true,
              inRange: {
                color: ['#edf8fb', '#b2e2e2', '#66c2a4', '#2ca25f', '#006d2c']
              }
            },
            series: [
              {
                name: '景区数量',
                type: 'map',
                map: provinceName,
                roam: true,
                zoom: 1.2,
                label: {
                  show: true,
                  fontSize: 10,
                  color: '#333'
                },
                itemStyle: {
                  areaColor: '#edf8fb',
                  borderColor: '#1890ff',
                  borderWidth: 0.5
                },
                emphasis: {
                  label: {
                    show: true,
                    fontSize: 12,
                    color: '#000'
                  },
                  itemStyle: {
                    areaColor: '#b3daff'
                  }
                },
                data: data
              }
            ]
          };
          
          // 应用配置
          provinceMapChartInstance.value.setOption(option);
          console.log('省份热力图配置已应用');
          
          // 添加点击事件
          provinceMapChartInstance.value.on('click', (params: any) => {
            if (params.componentType === 'series') {
              const cityName = params.name;
              console.log('点击了城市：', cityName);
              
              // 如果是直辖市中的市辖区，不做处理
              if (isCurrentProvinceMunicipality && cityName === DEFAULT_MUNICIPALITY_CITY) {
                console.log(`直辖市中的"${DEFAULT_MUNICIPALITY_CITY}"被点击，不做处理`);
                ElMessage.info(`作为直辖市，${provinceName}已直接显示区县数据`);
                return;
              }
              
              // 非直辖市的第三层下钻已取消，显示提示信息
              if (!isMunicipality(currentProvince.value)) {
                console.log(`非直辖市${currentProvince.value}的${cityName}被点击，但第三层下钻已禁用`);
                ElMessage.info(`暂未实现市级行政区下钻功能`);
                return;
              }
              
              // 仅对直辖市执行下钻
              showCityDetail(cityName);
            }
          });
          
        } catch (error) {
          console.error(`设置${provinceName}地图失败:`, error);
          provinceMapError.value = true;
          ElMessage.error(`无法显示${provinceName}地图数据`);
        }
      })
      .catch(error => {
        if (!provinceMapChartInstance.value) return;
        provinceMapChartInstance.value.hideLoading();
        
        console.error(`加载${provinceName}地图数据失败:`, error);
        provinceMapError.value = true;
        ElMessage.error(`加载${provinceName}地图数据失败，该省份地图可能不存在`);
        
        // 失败提示
        if (provinceMapChartInstance.value) {
          provinceMapChartInstance.value.setOption({
            title: {
              text: `${provinceName}地图数据无法加载`,
              left: 'center',
              textStyle: {
                fontSize: 18,
                color: '#ff4d4f'
              }
            },
            graphic: [
              {
                type: 'text',
                left: 'center',
                top: 'middle',
                style: {
                  text: '无法加载该省份地图数据，请检查地图文件是否存在',
                  fill: '#999',
                  font: '14px Microsoft YaHei'
                }
              }
            ]
          });
        }
      });
  } catch (error) {
    console.error(`动态导入${provinceName}地图数据失败:`, error);
    provinceMapError.value = true;
    ElMessage.error(`加载${provinceName}地图数据失败，请检查地图文件是否存在`);
    if (provinceMapChartInstance.value) {
      provinceMapChartInstance.value.hideLoading();
    }
  }
}

// 更新柱状图为城市数据（新增函数）
const updateBarChartWithCityData = (isDistrictData = false) => {
  if (!barChartInstance.value || cityData.value.length === 0) {
    console.error('柱状图实例不存在或城市数据为空')
    return
  }
  
  try {
    // 按景区数量排序
    const sortedData = [...cityData.value].sort((a, b) => b.value - a.value)
    
    // 设置标题，如果是直辖市的区县数据，则显示为区县统计
    const titleText = isDistrictData || isMunicipality(currentProvince.value) 
      ? `${currentProvince.value}各区县景区数量统计`
      : `${currentProvince.value}各市景区数量统计`
    
    barChartInstance.value.setOption({
      title: {
        text: titleText,
      },
      xAxis: {
        data: sortedData.map(item => item.name)
      },
      series: [{
        data: sortedData.map(item => ({
          value: item.value,
          name: item.name,
          // 添加渐变色，使柱状图更生动
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#0364bb' }
            ]),
            borderColor: '#0364bb',
            borderWidth: 0.5,
            borderRadius: [3, 3, 0, 0] // 柱状图圆角
          },
          // 在柱顶显示数值
          label: {
            show: true,
            position: 'top',
            formatter: '{c}',
            fontSize: 10,
            color: '#333'
          }
        }))
      }]
    })
    
    // 强制重绘
    barChartInstance.value.resize()
    
    console.log(`${isDistrictData ? '区县' : '城市'}柱状图更新完成`)
  } catch (error) {
    console.error('更新城市/区县柱状图失败:', error)
  }
}

// 返回全国地图
const backToChina = () => {
  console.log('返回全国地图')
  showProvinceMap.value = false
  currentProvince.value = ''
  currentMapLevel.value = 0
  
  // 重置柱状图高亮，并还原为显示省份数据
  if (barChartInstance.value) {
    updateCharts()
  }
  
  // 如果全国地图已初始化，重绘一次
  nextTick(() => {
    if (mapChartInstance.value) {
      setTimeout(() => {
        console.log('重新绘制全国地图')
        mapChartInstance.value?.resize()
      }, 200)
    }
  })
}

// 更新图表数据
const updateCharts = (displayEmpty = false) => {
  console.log('开始更新图表数据')
  
  if (!mapChartInstance.value || !barChartInstance.value) {
    console.error('图表实例不存在，无法更新数据', {
      mapChartInstance: !!mapChartInstance.value,
      barChartInstance: !!barChartInstance.value
    })
    return
  }
  
  if (!scenicStore.provinceData || scenicStore.provinceData.length === 0) {
    console.log('省份数据为空，显示空图表')
    
    if (displayEmpty) {
      // 显示空地图
      if (mapChartInstance.value) {
        mapChartInstance.value.setOption({
          series: [{
            // 确保地图显示，但数据为空
            data: []
          }]
        })
      }
      
      // 显示空柱状图
      if (barChartInstance.value) {
        barChartInstance.value.setOption({
          xAxis: {
            data: []
          },
          series: [{
            data: []
          }]
        })
      }
      
      // 强制重绘
      mapChartInstance.value.resize()
      barChartInstance.value.resize()
    }
    
    return
  }
  
  try {
    // 更新地图数据
    const mapData = scenicStore.provinceData.map(province => {
      return {
        name: province.name,
        value: province.value || 0
      }
    })
    
    console.log('准备更新地图数据:', JSON.stringify(mapData))
    
    // 计算最大值用于设置visualMap
    const maxValue = Math.max(...mapData.map(item => item.value), 0)
    
    // 更新地图数据
    mapChartInstance.value.setOption({
      visualMap: {
        min: 0,
        max: maxValue > 0 ? maxValue : 100, // 根据实际数据设置最大值
      },
      series: [{
        data: mapData
      }]
    })
    console.log('地图数据已更新')
    
    // 更新柱状图标题和数据（根据当前是全国还是省级决定）
    if (showProvinceMap.value && currentProvince.value && cityData.value.length > 0) {
      // 如果显示的是省份地图，则柱状图显示城市数据
      updateBarChartWithCityData()
    } else {
      // 如果显示的是全国地图，则柱状图显示省份数据
      const barData = scenicStore.provinceData
        .map(province => ({
          name: province.name,
          value: province.value || 0
        }))
        .sort((a, b) => b.value - a.value) // 按景区数量降序排列
      
      console.log('准备更新柱状图数据:', barData)
      
      barChartInstance.value.setOption({
        title: {
          text: '省份景区数量统计'
        },
        xAxis: {
          data: barData.map(item => item.name)
        },
        series: [{
          data: barData.map(item => ({
            value: item.value,
            name: item.name,
            // 高亮当前选中的省份
            itemStyle: item.name === currentProvince.value ? {
              color: '#ffc107'
            } : null
          }))
        }]
      })
    }
    
    // 强制重绘
    mapChartInstance.value.resize()
    barChartInstance.value.resize()
    
    dataReady.value = true
    console.log('图表数据更新完成')
  } catch (error) {
    console.error('更新图表数据失败:', error)
    ElMessage.error('更新图表数据失败')
  }
}

// 窗口大小改变时重新调整图表大小
const handleResize = () => {
  if (mapChartInstance.value) {
    console.log('调整地图大小')
    mapChartInstance.value.resize()
  }
  
  if (barChartInstance.value) {
    console.log('调整柱状图大小')
    barChartInstance.value.resize()
  }
  
  if (provinceMapChartInstance.value) {
    console.log('调整省份地图大小')
    provinceMapChartInstance.value.resize()
  }
  
  if (cityMapChartInstance.value) {
    console.log('调整城市地图大小')
    cityMapChartInstance.value.resize()
  }
}

// 等待DOM渲染并初始化图表
const waitForDomAndInitCharts = () => {
  console.log('尝试初始化图表...')
  // 使用requestAnimationFrame确保在下一个渲染周期尝试初始化
  window.requestAnimationFrame(() => {
    let mapContainerExists = mapChart.value && mapChart.value.clientWidth > 0
    let barContainerExists = barChart.value && barChart.value.clientWidth > 0
    
    console.log('图表容器状态:', {
      mapContainerExists,
      barContainerExists
    })
    
    if (mapContainerExists && barContainerExists) {
      console.log('DOM已准备就绪，开始初始化图表')
      initMapChart()
      initBarChart()
      
      // 无论是否有数据，都更新图表，displayEmpty参数控制是否显示空地图
      updateCharts(true)
    } else {
      console.log('图表容器尚未就绪，等待50ms后重试')
      setTimeout(waitForDomAndInitCharts, 50)
    }
  })
}

// 初始化和更新图表数据
const initCharts = () => {
  console.log('准备初始化图表')
  
  // 延迟执行以确保DOM已更新
  nextTick(() => {
    // 即使在没有数据的情况下也设置dataReady为true
    dataReady.value = true
    console.log('数据准备状态:', dataReady.value, '省份数据数量:', scenicStore.provinceData.length)
    
    waitForDomAndInitCharts()
  })
}

// 获取数据
const fetchData = async () => {
  console.log('开始获取景区分布数据')
  loading.value = true
  
  try {
    await scenicStore.getProvinceData()
    console.log('景区分布数据获取成功', JSON.stringify(scenicStore.provinceData))
    loading.value = false
    
    // 无论是否有数据，都初始化图表
    initCharts()
  } catch (error) {
    console.error('景区分布数据获取失败:', error)
    loading.value = false
    ElMessage.error('数据加载失败，请稍后重试')
    
    // 即使获取数据失败，也尝试初始化空地图
    initCharts()
  }
}

// 添加显示状态监听器
watch(showProvinceMap, (newVal, oldVal) => {
  console.log('显示省份地图状态变化:', oldVal, '->', newVal)
  
  if (!newVal) {
    // 回到全国地图，重置相关状态
    currentProvince.value = ''
    
    // 如果全国地图已初始化，重绘一次
    nextTick(() => {
      if (mapChartInstance.value) {
        setTimeout(() => {
          console.log('重新绘制全国地图')
          mapChartInstance.value?.resize()
          updateCharts()
        }, 200)
      }
    })
  } else if (newVal && currentProvince.value) {
    // 切换到省份地图，确保省份地图正确初始化
    console.log('切换到省份地图:', currentProvince.value)
    
    // 确保省份地图容器已显示
    nextTick(() => {
      if (provinceMapChart.value) {
        const province = scenicStore.provinceData.find(item => item.name === currentProvince.value)
        if (province && province.scenics) {
          setTimeout(() => {
            console.log('(watch)准备初始化省份地图')
            initProvinceMap(currentProvince.value, province.scenics || [])
          }, 300)
        }
      }
    })
  }
})

// 清空地图缓存，强制重新加载地图
const clearMapCache = () => {
  // 根据当前地图级别决定刷新哪个地图
  if (currentMapLevel.value === 0) {
    // 全国地图级别
    if (mapChartInstance.value) {
      mapChartInstance.value.dispose()
      mapChartInstance.value = null
    }
    
    // 重新初始化全国地图
    nextTick(() => {
      initMapChart()
      updateCharts(true)
    })
    
    ElMessage.success('全国地图数据已重新加载')
  } else if (currentMapLevel.value === 1) {
    // 省级地图
    if (provinceMapChartInstance.value) {
      provinceMapChartInstance.value.dispose()
      provinceMapChartInstance.value = null
    }
    
    // 重新初始化省级地图，保持当前省份
    nextTick(() => {
      const province = scenicStore.provinceData.find(item => item.name === currentProvince.value)
      if (province && province.scenics) {
        initProvinceMapWithApiData(currentProvince.value, cityData.value)
      }
    })
    
    ElMessage.success(`${currentProvince.value}地图数据已重新加载`)
  } else if (currentMapLevel.value === 2) {
    // 市级地图
    if (cityMapChartInstance.value) {
      cityMapChartInstance.value.dispose()
      cityMapChartInstance.value = null
    }
    
    // 重新初始化市级地图，保持当前城市
    nextTick(() => {
      const province = scenicStore.provinceData.find(item => item.name === currentProvince.value)
      if (province && province.scenics) {
        initCityMap(currentProvince.value, currentCity.value, province.scenics)
      }
    })
    
    ElMessage.success(`${currentCity.value}地图数据已重新加载`)
  }
}

// 确保整个页面初始化
const initPage = () => {
  if (document.readyState === 'complete') {
    console.log('文档已完全加载，立即开始获取数据')
    fetchData()
  } else {
    console.log('文档尚未完全加载，等待完成后再获取数据')
    // 等待页面完全加载
    window.addEventListener('load', () => {
      console.log('文档加载完成，开始获取数据')
      fetchData()
    }, { once: true })
  }
}

// 页面加载时初始化
onMounted(() => {
  console.log('组件挂载')
  // 确保DOM已渲染
  nextTick(() => {
    console.log('DOM渲染完成，开始初始化')
    initPage()
  })
  window.addEventListener('resize', handleResize)
})

// 页面卸载时清理资源
onUnmounted(() => {
  console.log('组件卸载，清理资源')
  window.removeEventListener('resize', handleResize)
  
  if (mapChartInstance.value) {
    mapChartInstance.value.dispose()
    mapChartInstance.value = null
  }
  
  if (barChartInstance.value) {
    barChartInstance.value.dispose()
    barChartInstance.value = null
  }
  
  if (provinceMapChartInstance.value) {
    provinceMapChartInstance.value.dispose()
    provinceMapChartInstance.value = null
  }
  
  if (cityMapChartInstance.value) {
    cityMapChartInstance.value.dispose()
    cityMapChartInstance.value = null
  }
})

// 初始化市级地图
const initCityMap = (provinceName: string, cityName: string, scenics: any[]) => {
  if (!cityMapChart.value) return
  
  cityMapError.value = false
  
  // 如果已经初始化过，先销毁原实例
  if (cityMapChartInstance.value) {
    cityMapChartInstance.value.dispose()
  }
  
  // 创建新实例
  cityMapChartInstance.value = echarts.init(cityMapChart.value)
  
  // 显示加载中状态
  cityMapChartInstance.value.showLoading()
  
  try {
    // 使用动态导入 - 尝试加载市级地图数据
    import(/* webpackChunkName: "city-map" */ `@/assets/geojson/city/${provinceName}/${cityName}.json`)
      .then(() => {
        // 初始化城市地图
        initCityMap(provinceName, cityName, scenics || [])
      })
      .catch(error => {
        console.error(`城市地图文件不存在: ${provinceName}/${cityName}.json`, error)
        cityMapError.value = true
        
        // 显示失败提示但仍然更新柱状图
        if (cityMapChartInstance.value) {
          cityMapChartInstance.value.setOption({
            title: {
              text: `${cityName}地图数据无法加载`,
              left: 'center',
              textStyle: {
                fontSize: 18,
                color: '#ff4d4f'
              }
            },
            graphic: [
              {
                type: 'text',
                left: 'center',
                top: 'middle',
                style: {
                  text: '缺少城市地图文件，请联系管理员添加相应地图文件',
                  fill: '#999',
                  font: '14px Microsoft YaHei'
                }
              }
            ]
          })
        }
      });
  } catch (error) {
    console.error(`动态导入${cityName}地图数据失败:`, error)
    cityMapError.value = true
    ElMessage.error(`加载${cityName}地图数据失败，请检查地图文件是否存在`)
    cityMapChartInstance.value?.hideLoading()
  }
}

// 显示城市详情
const showCityDetail = (cityName: string) => {
  console.log('准备显示城市详情:', cityName)
  if (!cityName || !currentProvince.value) {
    console.error('城市名称或当前省份为空')
    ElMessage.warning('选择的城市无效')
    return
  }
  
  // 检查是否是直辖市且点击的是"市辖区"
  if (isMunicipality(currentProvince.value) && cityName === DEFAULT_MUNICIPALITY_CITY) {
    console.log(`检测到点击直辖市的"${DEFAULT_MUNICIPALITY_CITY}"，不做处理`)
    ElMessage.info(`${currentProvince.value}作为直辖市，已直接显示区县数据`)
    return
  }
  
  const province = scenicStore.provinceData.find(item => item.name === currentProvince.value)
  
  if (!province || !province.scenics) {
    console.error(`未找到省份: ${currentProvince.value}的数据`)
    ElMessage.warning(`未找到${currentProvince.value}数据`)
    return
  }
  
  const cityScenicSpots = province.scenics.filter(item => item.city === cityName)
  
  if (!cityScenicSpots.length) {
    console.warn(`${cityName}没有景区数据`)
    ElMessage.warning(`${cityName}暂无景区数据`)
    return
  }
  
  console.log(`找到${cityName}的景区数据:`, cityScenicSpots.length)
  
  // 设置当前城市和显示状态
  currentCity.value = cityName
  currentMapLevel.value = 2
  
  // 切换显示状态
  showCityMap.value = true
  showProvinceMap.value = false
  
  // 确保DOM更新后才初始化城市地图
  nextTick(() => {
    setTimeout(async () => {
      if (cityMapChart.value) {
        console.log('初始化城市地图:', cityName)
        
        // 确保地图容器已完全显示
        cityMapChart.value.style.display = 'block'
        
        try {
          // 尝试加载区县数据
          console.log(`尝试加载${currentProvince.value}${cityName}的区县数据`)
          const districtData = await scenicStore.getDistrictDistribution(currentProvince.value, cityName)
          
          if (districtData && districtData.length > 0) {
            console.log(`成功获取到${districtData.length}个区县数据`)
            
            // 初始化柱状图以显示区县数据
            updateBarChartWithDistrictData(districtData)
          } else {
            console.warn(`没有找到区县数据，将使用默认分组`)
          }
          
          // 检查城市地图文件是否存在
          import(/* webpackChunkName: "city-map" */ `@/assets/geojson/city/${currentProvince.value}/${cityName}.json`)
            .then(() => {
              // 初始化城市地图
              initCityMap(currentProvince.value, cityName, province.scenics || [])
            })
            .catch(error => {
              console.error(`城市地图文件不存在: ${currentProvince.value}/${cityName}.json`, error)
              cityMapError.value = true
              
              // 显示失败提示但仍然更新柱状图
              if (cityMapChartInstance.value) {
                cityMapChartInstance.value.setOption({
                  title: {
                    text: `${cityName}地图数据无法加载`,
                    left: 'center',
                    textStyle: {
                      fontSize: 18,
                      color: '#ff4d4f'
                    }
                  },
                  graphic: [
                    {
                      type: 'text',
                      left: 'center',
                      top: 'middle',
                      style: {
                        text: '缺少城市地图文件，请联系管理员添加相应地图文件',
                        fill: '#999',
                        font: '14px Microsoft YaHei'
                      }
                    }
                  ]
                })
              }
            })
        } catch (error) {
          console.error('无法加载城市地图:', error)
          cityMapError.value = true
          ElMessage.error(`加载城市地图失败，请确认地图文件是否存在`)
        }
      } else {
        console.error('城市地图容器不存在')
        
        // 重置状态
        showCityMap.value = false
        currentCity.value = ''
        
        ElMessage.error('地图容器加载失败，请重试')
      }
    }, 500) // 延长延迟时间确保DOM完全更新
  })
}

// 返回省级地图
const backToProvince = () => {
  console.log('返回省级地图')
  showCityMap.value = false
  currentCity.value = ''
  currentMapLevel.value = 1
  showProvinceMap.value = true
  
  // 重新显示省级地图
  nextTick(() => {
    const province = scenicStore.provinceData.find(item => item.name === currentProvince.value)
    if (province && province.scenics && provinceMapChart.value) {
      setTimeout(() => {
        console.log('重新绘制省级地图')
        
        // 如果省级地图实例存在，重绘
        if (provinceMapChartInstance.value) {
          provinceMapChartInstance.value.resize()
        } else {
          // 否则重新初始化
          initProvinceMap(currentProvince.value, province.scenics || [])
        }
      }, 200)
    }
  })
}

// 更新柱状图为区县数据
const updateBarChartWithDistrictData = (districtData: Array<{name: string, value: number | any}>) => {
  if (!barChartInstance.value || districtData.length === 0) {
    console.error('柱状图实例不存在或区县数据为空')
    return
  }
  
  try {
    // 确保数据值有效
    const validatedData = districtData.map(item => {
      // 确保值是数字
      const numValue = Number(item.value);
      const value = isNaN(numValue) ? 0 : numValue;
      
      if (isNaN(numValue)) {
        console.warn(`区县/城市 ${item.name} 的景区数量值 ${item.value} 无效，已替换为0`);
      }
      
      return {
        name: item.name,
        value: value
      };
    });
    
    // 按景区数量排序
    const sortedData = [...validatedData].sort((a, b) => b.value - a.value)
    
    barChartInstance.value.setOption({
      title: {
        text: `${currentCity.value}各区县景区数量统计`,
      },
      xAxis: {
        data: sortedData.map(item => item.name)
      },
      series: [{
        data: sortedData.map(item => ({
          value: item.value,
          name: item.name,
          // 添加渐变色，使柱状图更生动
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#91cc75' },
              { offset: 0.5, color: '#67c23a' },
              { offset: 1, color: '#4e8c30' }
            ]),
            borderColor: '#4e8c30',
            borderWidth: 0.5,
            borderRadius: [3, 3, 0, 0] // 柱状图圆角
          },
          // 在柱顶显示数值
          label: {
            show: true,
            position: 'top',
            formatter: '{c}',
            fontSize: 10,
            color: '#333'
          }
        }))
      }]
    })
    
    // 强制重绘
    barChartInstance.value.resize()
    
    console.log('区县柱状图更新完成')
  } catch (error) {
    console.error('更新区县柱状图失败:', error)
  }
}
</script>

<template>
  <div class="scenic-distribution-container">
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>景区基础分布分析</span>
          <div class="header-buttons">
            <el-button @click="clearMapCache" type="primary" size="small">
              刷新地图
            </el-button>
            <el-button v-if="showCityMap" @click="backToProvince" type="primary" size="small">
              返回省级地图
            </el-button>
            <el-button v-if="showProvinceMap && !showCityMap" @click="backToChina" type="primary" size="small">
              返回全国地图
            </el-button>
          </div>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-icon class="loading-icon">
          <loading />
        </el-icon>
        <div class="loading-text">数据加载中...</div>
      </div>
      
      <div v-else>
        <!-- 地图和图表区域 -->
        <el-row :gutter="20">
          <el-col :span="24">
            <!-- 全国地图 -->
            <div class="map-container" ref="mapChart" :style="{ display: !showProvinceMap && !showCityMap ? 'block' : 'none' }">
            </div>
            
            <!-- 省份地图 -->
            <div :style="{ display: showProvinceMap && !showCityMap ? 'block' : 'none' }" class="province-map-container">
              <div ref="provinceMapChart" class="province-map"></div>
              <div v-if="provinceMapError" class="map-error">
                <el-alert
                  title="无法加载省份地图数据"
                  type="error"
                  description="该省份的地图文件可能不存在，请检查assets/province目录"
                  show-icon
                  :closable="false"
                />
              </div>
              <div class="province-info" v-if="currentProvince">
                <h3>{{ currentProvince }}景区信息</h3>
                <p v-if="isMunicipality(currentProvince)">景区热力分布（点击区县查看详情）</p>
                <p v-else>景区热力分布（仅显示城市级数据）</p>
              </div>
            </div>
            
            <!-- 城市地图 -->
            <div :style="{ display: showCityMap ? 'block' : 'none' }" class="city-map-container">
              <div ref="cityMapChart" class="city-map"></div>
              <div v-if="cityMapError" class="map-error">
                <el-alert
                  title="无法加载城市地图数据"
                  type="error"
                  description="该城市的地图文件可能不存在，请检查assets/city目录"
                  show-icon
                  :closable="false"
                />
              </div>
              <div class="city-info" v-if="currentCity">
                <h3>{{ currentCity }}景区信息</h3>
                <p>景区热力分布</p>
              </div>
            </div>
          </el-col>
          
          <el-col :span="24" class="mt-20">
            <!-- 柱状图 -->
            <div class="bar-container" ref="barChart">
            </div>
          </el-col>
        </el-row>
        
        <div v-if="!scenicStore.provinceData.length" class="no-data">
          <el-empty description="暂无景区分布数据">
            <template #image>
              <el-icon style="font-size: 48px; color: #909399;">
                <data-analysis />
              </el-icon>
            </template>
            <el-button type="primary" @click="fetchData">重新加载</el-button>
          </el-empty>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.scenic-distribution-container {
  height: 100%;
  position: relative;
  min-height: 900px; /* 确保容器有最小高度 */
}

.chart-card {
  height: 100%;
  overflow: hidden;
  min-height: 900px; /* 确保卡片有最小高度 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.map-container, .province-map-container, .city-map-container {
  height: 500px;
  width: 100%;
  position: relative;
  border: 1px solid #f0f0f0; /* 添加边框以便于调试 */
}

.province-map, .city-map {
  height: 100%;
  width: 100%;
}

.map-error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  z-index: 10;
}

.province-info, .city-info {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.9);
  padding: 10px 15px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.province-info h3, .city-info h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #303133;
}

.province-info p, .city-info p {
  margin: 0;
  font-size: 12px;
  color: #606266;
}

.bar-container {
  height: 400px;
  width: 100%;
  margin-bottom: 20px;
  border: 1px solid #f0f0f0; /* 添加边框以便于调试 */
}

.mt-20 {
  margin-top: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 600px;
}

.loading-icon {
  font-size: 48px;
  color: #409EFF;
  animation: rotating 2s linear infinite;
}

.loading-text {
  margin-top: 15px;
  color: #409EFF;
  font-size: 14px;
}

.no-data {
  height: 600px;
  display: flex;
  justify-content: center;
  align-items: center;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style> 