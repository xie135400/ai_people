<template>
  <div class="records-container">
    <!-- 顶部导航 -->
    <van-nav-bar 
      title="分析记录" 
      left-arrow 
      @click-left="$router.back()"
      class="records-navbar"
    >
      <template #right>
        <van-icon 
          name="refresh" 
          @click="refreshRecords"
          :class="{ 'rotating': loading }"
        />
      </template>
    </van-nav-bar>

    <!-- 主要内容 -->
    <div class="records-content">
      <!-- 统计概览 -->
      <div class="overview-section" v-if="records.length > 0">
        <div class="overview-card">
          <div class="overview-item">
            <div class="overview-icon">
              <van-icon name="notes-o" />
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ records.length }}</div>
              <div class="overview-label">总记录数</div>
            </div>
          </div>
          <div class="overview-divider"></div>
          <div class="overview-item">
            <div class="overview-icon">
              <van-icon name="friends-o" />
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ totalPeople }}</div>
              <div class="overview-label">总人数</div>
            </div>
          </div>
          <div class="overview-divider"></div>
          <div class="overview-item">
            <div class="overview-icon">
              <van-icon name="user-o" />
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ avgAge }}</div>
              <div class="overview-label">平均年龄</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 筛选器 -->
      <div class="filter-section">
        <div class="filter-card">
          <div class="filter-header">
            <van-icon name="filter-o" class="filter-icon" />
            <span>筛选记录</span>
          </div>
          <div class="filter-input">
            <van-field
              v-model="searchQuery"
              placeholder="输入记录名称搜索..."
              clearable
              @input="onSearchInput"
            >
              <template #left-icon>
                <van-icon name="search" class="search-icon" />
              </template>
            </van-field>
          </div>
        </div>
      </div>

      <!-- 记录列表 -->
      <div class="records-list">
        <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
          <van-list
            :loading="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="onLoad"
          >
            <div class="record-card" v-for="record in filteredRecords" :key="record.id" @click="viewRecordDetail(record)">
              <div class="record-header">
                <div class="record-title-area">
                  <van-icon name="clock-o" class="record-time-icon" />
                  <span class="record-time">{{ formatTime(record.timestamp) }}</span>
                </div>
                <van-icon name="arrow" class="record-arrow" />
              </div>
              
              <div class="record-name">{{ record.record_name || '无名记录' }}</div>
              
              <div class="record-metrics">
                <div class="metric-item">
                  <van-icon name="friends-o" class="metric-icon people" />
                  <span class="metric-value">{{ record.total_people }} 人</span>
                </div>
                <div class="metric-item" v-if="record.avg_age">
                  <van-icon name="user-o" class="metric-icon age" />
                  <span class="metric-value">{{ Math.round(record.avg_age) }} 岁</span>
                </div>
                <div class="metric-item">
                  <div class="gender-icons">
                    <van-icon name="contact" class="metric-icon male" />
                    <van-icon name="like" class="metric-icon female" />
                  </div>
                  <span class="metric-value">{{ record.male_count }}/{{ record.female_count }}</span>
                </div>
              </div>
              
              <div class="record-footer">
                <div class="engagement-bar">
                  <div class="engagement-progress" 
                       :style="{width: (record.engagement_score ? Math.round(record.engagement_score * 100) : 0) + '%'}">
                  </div>
                </div>
                <span class="engagement-label">参与度: {{ record.engagement_score ? Math.round(record.engagement_score * 100) : 0 }}%</span>
              </div>
            </div>
          </van-list>
        </van-pull-refresh>
      </div>

      <!-- 空状态 -->
      <div class="empty-state" v-if="!loading && records.value?.length === 0">
        <div class="empty-image">
          <van-icon name="records" />
        </div>
        <div class="empty-text">暂无分析记录</div>
        <div class="empty-description">开始您的第一次分析，记录将显示在这里</div>
        <div class="empty-actions">
          <van-button round type="primary" @click="refreshRecords" icon="refresh">刷新记录</van-button>
          <van-button round type="info" @click="testDetailPopup" icon="play-circle-o">测试弹窗</van-button>
        </div>
      </div>
    </div>

    <!-- 自定义详情弹窗 -->
    <div class="custom-popup" v-if="showDetail" @click.self="closePopup">
      <div class="custom-popup-content" v-if="selectedRecord">
        <div class="custom-popup-header">
          <h3>{{ selectedRecord.record_name || '无名记录' }}</h3>
          <span class="custom-popup-close" @click="closePopup">&times;</span>
        </div>
        
        <div class="custom-popup-body">
          <!-- 基本信息卡片 -->
          <div class="detail-card">
            <div class="detail-card-header">
              <van-icon name="clock" class="card-icon" />
              <span>记录时间: {{ formatTime(selectedRecord.timestamp) }}</span>
            </div>
            
            <!-- 核心数据概览 -->
            <div class="stats-overview">
              <div class="stat-item">
                <div class="stat-value">{{ selectedRecord.total_people }}</div>
                <div class="stat-label">总人数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ selectedRecord.active_tracks }}</div>
                <div class="stat-label">活跃人数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ selectedRecord.avg_age ? Math.round(selectedRecord.avg_age) : '-' }}</div>
                <div class="stat-label">平均年龄</div>
              </div>
            </div>
          </div>
          
          <!-- 性别分布卡片 -->
          <div class="detail-card">
            <div class="detail-card-header">
              <van-icon name="friends-o" class="card-icon" />
              <span>性别分布</span>
            </div>
            
            <div class="gender-distribution">
              <div class="gender-bar">
                <div class="gender-male" :style="{width: getMalePercentage(selectedRecord) + '%'}">
                  <van-icon name="contact" /> {{ selectedRecord.male_count }}
                </div>
                <div class="gender-female" :style="{width: getFemalePercentage(selectedRecord) + '%'}">
                  {{ selectedRecord.female_count }} <van-icon name="like" />
                </div>
              </div>
              <div class="gender-labels">
                <span class="male-label">男性 {{ getMalePercentage(selectedRecord) }}%</span>
                <span class="female-label">{{ getFemalePercentage(selectedRecord) }}% 女性</span>
              </div>
            </div>
          </div>
          
          <!-- 行为分析卡片 -->
          <div class="detail-card" v-if="selectedRecord.shopper_count > 0 || selectedRecord.browser_count > 0">
            <div class="detail-card-header">
              <van-icon name="eye-o" class="card-icon" />
              <span>行为分析</span>
            </div>
            
            <div class="behavior-stats">
              <div class="behavior-item">
                <van-icon name="cart-o" class="behavior-icon shopper" />
                <div class="behavior-info">
                  <div class="behavior-value">{{ selectedRecord.shopper_count }}</div>
                  <div class="behavior-label">购物者</div>
                </div>
              </div>
              <div class="behavior-item">
                <van-icon name="browsing-history-o" class="behavior-icon browser" />
                <div class="behavior-info">
                  <div class="behavior-value">{{ selectedRecord.browser_count }}</div>
                  <div class="behavior-label">浏览者</div>
                </div>
              </div>
              <div class="behavior-item">
                <van-icon name="underway-o" class="behavior-icon dwell" />
                <div class="behavior-info">
                  <div class="behavior-value">{{ formatDuration(selectedRecord.avg_dwell_time) }}</div>
                  <div class="behavior-label">平均停留</div>
                </div>
              </div>
              <div class="behavior-item">
                <van-icon name="chart-trending-o" class="behavior-icon engagement" />
                <div class="behavior-info">
                  <div class="behavior-value">{{ Math.round(selectedRecord.engagement_score * 100) }}%</div>
                  <div class="behavior-label">参与度</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 年龄分布卡片 -->
          <div class="detail-card" v-if="selectedRecord.additional_data?.age_distribution">
            <div class="detail-card-header">
              <van-icon name="bar-chart-o" class="card-icon" />
              <span>年龄分布</span>
            </div>
            
            <div class="age-distribution">
              <div 
                v-for="(count, ageGroup) in selectedRecord.additional_data.age_distribution" 
                :key="ageGroup"
                class="age-bar"
              >
                <div class="age-label">{{ ageGroup }}</div>
                <div class="age-progress">
                  <div 
                    class="age-progress-bar" 
                    :style="{
                      width: getTotalAgeAnalyzed(selectedRecord) > 0 ? 
                        (count / getTotalAgeAnalyzed(selectedRecord) * 100) + '%' : '0%',
                      backgroundColor: getAgeColor(ageGroup)
                    }"
                  ></div>
                </div>
                <div class="age-count">{{ count }}</div>
              </div>
            </div>
          </div>
          
          <!-- 附加信息卡片 -->
          <div class="detail-card" v-if="selectedRecord.additional_data">
            <div class="detail-card-header">
              <van-icon name="info-o" class="card-icon" />
              <span>处理信息</span>
            </div>
            
            <div class="processing-info">
              <div class="processing-item">
                <div class="processing-label">处理帧数</div>
                <div class="processing-value">{{ selectedRecord.additional_data.frame_count?.toLocaleString() || '0' }}</div>
              </div>
              <div class="processing-item">
                <div class="processing-label">检测人脸</div>
                <div class="processing-value">{{ selectedRecord.additional_data.faces_detected || '0' }}</div>
              </div>
              <div class="processing-item">
                <div class="processing-label">处理时间</div>
                <div class="processing-value">{{ selectedRecord.additional_data.processing_time ? selectedRecord.additional_data.processing_time.toFixed(2) + 'ms' : '0ms' }}</div>
              </div>
            </div>
          </div>
          
          <!-- 备注信息卡片 -->
          <div class="detail-card" v-if="selectedRecord.notes">
            <div class="detail-card-header">
              <van-icon name="comment-o" class="card-icon" />
              <span>备注信息</span>
            </div>
            
            <div class="notes-content">
              {{ selectedRecord.notes || '暂无备注' }}
            </div>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="custom-popup-footer">
          <van-button type="primary" round block @click="shareRecord(selectedRecord)" icon="share-o">分享记录</van-button>
          <van-button type="info" round block @click="exportRecord(selectedRecord)" icon="down" style="margin-top: 10px;">导出数据</van-button>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <van-tabbar v-model="activeTab" @change="onTabChange">
      <van-tabbar-item icon="home-o" to="/">主页</van-tabbar-item>
      <van-tabbar-item icon="chart-trending-o" to="/analysis">分析</van-tabbar-item>
      <van-tabbar-item icon="records" to="/records">记录</van-tabbar-item>
      <van-tabbar-item icon="setting-o" to="/settings">设置</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalyticsStore } from '../stores/analytics'
import { showToast, showFailToast, showDialog } from 'vant'

const router = useRouter()
const analyticsStore = useAnalyticsStore()

// 响应式数据
const activeTab = ref(2)
const loading = ref(false)
const refreshing = ref(false)
const finished = ref(false)
const searchQuery = ref('')
const selectedRecord = ref(null)
const showDetail = ref(false) // 控制自定义弹窗的显示

// 从store获取数据
const records = ref([])

// 初始化数据
const initRecords = () => {
  if (analyticsStore.records && analyticsStore.records.value) {
    records.value = analyticsStore.records.value
  }
}

// 计算属性
const filteredRecords = computed(() => {
  if (!records.value?.length) return []
  if (!searchQuery.value) {
    return records.value
  }
  return records.value.filter(record => 
    record.record_name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const totalPeople = computed(() => {
  return records.value?.length ? records.value.reduce((sum, record) => sum + (record.total_people || 0), 0) : 0
})

const avgAge = computed(() => {
  if (!records.value?.length) return '-'
  const validAges = records.value.filter(record => record.avg_age).map(record => record.avg_age)
  if (validAges.length === 0) return '-'
  const sum = validAges.reduce((sum, age) => sum + age, 0)
  return Math.round(sum / validAges.length) + '岁'
})

// 页面加载
onMounted(async () => {
  console.log('Records页面加载')
  console.log('初始records状态:', records.value)
  
  // 初始化数据
  initRecords()
  
  // 加载记录
  await loadRecords()
  
  console.log('加载后records状态:', records.value)
  console.log('过滤后的记录:', filteredRecords.value)
  
  // 添加键盘事件监听器
  window.addEventListener('keydown', handleKeyDown)
})

// 页面卸载
onUnmounted(() => {
  // 移除键盘事件监听器
  window.removeEventListener('keydown', handleKeyDown)
})

// 处理键盘事件
const handleKeyDown = (event) => {
  // 按 ESC 键关闭弹窗
  if (event.key === 'Escape' && showDetail.value) {
    closePopup()
  }
}

// 加载记录
const loadRecords = async () => {
  try {
    loading.value = true
    
    // 获取当前用户ID
    const savedUser = localStorage.getItem('user')
    let userId = null
    
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser)
        userId = userData.id
      } catch (e) {
        console.error('解析用户数据失败:', e)
      }
    }
    
    // 构建URL，通过查询参数传递用户ID
    let url = '/api/records/all'
    if (userId) {
      url += `?user_id=${encodeURIComponent(userId)}`
    }
    console.log('加载记录URL:', url, '用户ID:', userId)
    
    // 直接调用API获取记录，不依赖store
    const response = await fetch(url)
    const data = await response.json()
    
    console.log('直接从API加载记录成功:', data)
    console.log('API返回的记录类型:', typeof data.records)
    console.log('API返回的记录是否为数组:', Array.isArray(data.records))
    
    if (data.records && data.records.length > 0) {
      console.log('第一条记录示例:', data.records[0])
    }
    
    // 更新本地数据
    if (data && data.records) {
      records.value = data.records
      console.log('更新本地records数据:', records.value)
      console.log('records.value类型:', typeof records.value)
      console.log('records.value是否为数组:', Array.isArray(records.value))
      console.log('records.value长度:', records.value.length)
      
      // 确保记录有正确的ID和其他必要字段
      if (records.value.length > 0) {
        const firstRecord = records.value[0]
        console.log('第一条记录ID:', firstRecord.id)
        console.log('第一条记录名称:', firstRecord.record_name)
        console.log('第一条记录时间戳:', firstRecord.timestamp)
      }
    } else {
      console.warn('API返回数据格式不正确:', data)
    }
    
    finished.value = true // 暂时设置为完成，实际项目中可以实现分页
  } catch (error) {
    console.error('加载记录失败:', error)
    showFailToast('加载记录失败')
  } finally {
    loading.value = false
  }
}

// 刷新记录
const refreshRecords = async () => {
  try {
    refreshing.value = true
    await loadRecords()
    showToast('刷新成功')
  } catch (error) {
    showFailToast('刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 下拉刷新
const onRefresh = async () => {
  await refreshRecords()
}

// 加载更多
const onLoad = async () => {
  // 暂时不实现分页加载
  finished.value = true
}

// 搜索输入
const onSearchInput = () => {
  // 实时搜索，无需额外处理
}

// 查看记录详情
const viewRecordDetail = (record) => {
  console.log('查看记录详情:', record)
  console.log('记录ID:', record.id)
  console.log('记录名称:', record.record_name)
  
  // 使用选中的记录
  selectedRecord.value = record
  showDetail.value = true // 显示弹窗
}

// 关闭弹窗
const closePopup = () => {
  showDetail.value = false
  selectedRecord.value = null
}

// 获取年龄分布总数
const getTotalAgeAnalyzed = (record) => {
  if (!record.additional_data?.age_distribution) return 0
  return Object.values(record.additional_data.age_distribution).reduce((sum, count) => sum + count, 0)
}

// 获取年龄组颜色
const getAgeColor = (ageGroup) => {
  const colors = {
    '0-17': '#ff976a',
    '18-25': '#07c160',
    '26-35': '#1989fa',
    '36-45': '#ee0a24',
    '46-55': '#ff976a',
    '56-65': '#646566',
    '65+': '#969799'
  }
  return colors[ageGroup] || '#1989fa'
}

// 获取男性百分比
const getMalePercentage = (record) => {
  if (!record || !record.total_people) return 0;
  return (record.male_count / record.total_people) * 100;
};

// 获取女性百分比
const getFemalePercentage = (record) => {
  if (!record || !record.total_people) return 0;
  return (record.female_count / record.total_people) * 100;
};

// 底部导航切换
const onTabChange = (index) => {
  const routes = ['/', '/analysis', '/records', '/settings']
  if (routes[index]) {
    router.push(routes[index])
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化持续时间
const formatDuration = (seconds) => {
  if (!seconds || seconds === 0) return '0秒'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}时${minutes}分`
  } else if (minutes > 0) {
    return `${minutes}分${secs}秒`
  } else {
    return `${secs}秒`
  }
}

// 导出记录数据
const exportRecord = (record) => {
  if (!record) return
  
  try {
    // 准备导出数据
    const exportData = {
      ...record,
      export_time: new Date().toISOString(),
      export_version: '1.0'
    }
    
    // 转换为JSON字符串
    const jsonStr = JSON.stringify(exportData, null, 2)
    
    // 创建Blob对象
    const blob = new Blob([jsonStr], { type: 'application/json' })
    
    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `记录_${record.id || new Date().getTime()}.json`
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    // 释放URL对象
    URL.revokeObjectURL(url)
    
    showToast('导出成功')
  } catch (error) {
    console.error('导出记录失败:', error)
    showFailToast('导出失败')
  }
}

// 分享记录
const shareRecord = async (record) => {
  if (!record) return
  
  try {
    // 检查是否支持网页分享API
    if (navigator.share) {
      await navigator.share({
        title: `分析记录: ${record.record_name || '无名记录'}`,
        text: `总人数: ${record.total_people}人, 平均年龄: ${record.avg_age ? Math.round(record.avg_age) : '未知'}岁`,
        url: window.location.href
      })
      showToast('分享成功')
    } else {
      // 不支持分享API，使用复制链接方式
      const shareText = `分析记录: ${record.record_name || '无名记录'}\n总人数: ${record.total_people}人\n平均年龄: ${record.avg_age ? Math.round(record.avg_age) : '未知'}岁`
      await navigator.clipboard.writeText(shareText)
      showToast('已复制分享内容到剪贴板')
    }
  } catch (error) {
    console.error('分享记录失败:', error)
    showFailToast('分享失败')
  }
}

// 编辑记录
const editRecord = (record) => {
  if (!record) return
  
  showDialog({
    title: '编辑记录',
    message: '此功能尚未实现，敬请期待！',
    confirmButtonText: '确定'
  })
  
  // TODO: 实现编辑功能
  console.log('编辑记录:', record)
}

// 确认删除
const confirmDelete = (record) => {
  if (!record) return
  
  showDialog({
    title: '删除确认',
    message: `确定要删除记录"${record.record_name || '无名记录'}"吗？此操作不可撤销。`,
    showCancelButton: true,
    confirmButtonText: '删除',
    confirmButtonColor: '#ee0a24',
    cancelButtonText: '取消',
  }).then(action => {
    if (action === 'confirm') {
      deleteRecord(record)
    }
  })
}

// 删除记录
const deleteRecord = async (record) => {
  if (!record) return
  
  try {
    // 显示加载提示
    showToast({
      type: 'loading',
      message: '删除中...',
      forbidClick: true,
    })
    
    // 调用API删除记录
    const response = await fetch(`/api/records/${record.id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      // 从本地数据中移除
      records.value = records.value.filter(r => r.id !== record.id)
      
      // 显示成功提示
      showToast({
        type: 'success',
        message: '删除成功'
      })
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    console.error('删除记录失败:', error)
    showFailToast('删除失败')
  }
}

// 测试弹窗
const testDetailPopup = () => {
  // 创建一个测试记录对象
  const testRecord = {
    id: 'test-id',
    record_name: '测试记录',
    timestamp: new Date().toISOString(),
    total_people: 10,
    active_tracks: 5,
    avg_age: 30,
    male_count: 6,
    female_count: 4,
    shopper_count: 3,
    browser_count: 7,
    avg_dwell_time: 120,
    engagement_score: 0.75,
    notes: '这是一条测试记录，用于验证弹窗功能是否正常。',
    additional_data: {
      frame_count: 1000,
      faces_detected: 50,
      processing_time: 250.5,
      age_distribution: {
        '0-17': 1,
        '18-25': 2,
        '26-35': 3,
        '36-45': 2,
        '46-55': 1,
        '56-65': 1,
        '65+': 0
      }
    }
  }
  
  // 显示弹窗
  selectedRecord.value = testRecord
  showDetail.value = true
  
  console.log('测试弹窗触发')
  console.log('弹窗状态:', showDetail.value)
  console.log('选中记录:', selectedRecord.value)
}

// 显示调试信息
const showDebugInfo = () => {
  console.log('记录数据:', records.value)
  console.log('过滤后记录:', filteredRecords.value)
  
  showDialog({
    title: '调试信息',
    message: `
      <div style="text-align: left;">
        <p>记录总数: ${records.value?.length || 0}</p>
        <p>过滤后记录数: ${filteredRecords.value?.length || 0}</p>
        <p>记录数据类型: ${typeof records.value}</p>
      </div>
    `,
    confirmButtonText: '确定',
    dangerouslyUseHTMLString: true
  })
}
</script>

<style scoped>
.records-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f7f8fa;
}

.records-navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.records-navbar :deep(.van-nav-bar__title) {
  color: white;
  font-weight: 600;
}

.records-navbar :deep(.van-icon) {
  color: white;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.records-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 60px;
}

.overview-section {
  padding: 16px;
}

.overview-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-around;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.overview-item {
  display: flex;
  align-items: center;
  flex: 1;
  padding: 0 10px;
}

.overview-divider {
  width: 1px;
  height: 40px;
  background-color: #ebedf0;
}

.overview-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.overview-icon .van-icon {
  font-size: 20px;
  color: white;
}

.overview-info {
  display: flex;
  flex-direction: column;
}

.overview-value {
  font-size: 20px;
  font-weight: 700;
  color: #323233;
  margin-bottom: 4px;
}

.overview-label {
  font-size: 12px;
  color: #646566;
}

.filter-section {
  padding: 0 16px 16px;
}

.filter-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filter-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.filter-icon {
  font-size: 20px;
  color: #1989fa;
  margin-right: 8px;
}

.filter-header span {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.filter-input :deep(.van-field__left-icon) {
  margin-right: 8px;
}

.search-icon {
  color: #1989fa;
}

.records-list {
  flex: 1;
  padding: 0 16px;
}

.record-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  transform: translateY(20px);
}

.record-card:nth-child(1) { animation-delay: 0.1s; }
.record-card:nth-child(2) { animation-delay: 0.2s; }
.record-card:nth-child(3) { animation-delay: 0.3s; }
.record-card:nth-child(4) { animation-delay: 0.4s; }
.record-card:nth-child(5) { animation-delay: 0.5s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebedf0;
}

.record-title-area {
  display: flex;
  align-items: center;
  gap: 4px;
}

.record-time-icon {
  font-size: 18px;
  color: #1989fa;
}

.record-time {
  font-size: 14px;
  color: #323233;
  font-weight: 500;
}

.record-arrow {
  font-size: 20px;
  color: #969799;
  transition: transform 0.3s ease;
}

.record-card:hover .record-arrow {
  transform: translateX(5px);
}

.record-name {
  font-size: 18px;
  font-weight: 600;
  color: #323233;
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.record-metrics {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebedf0;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #646566;
}

.metric-icon {
  font-size: 20px;
  color: #1989fa;
}

.people .metric-icon {
  color: #07c160;
}

.age .metric-icon {
  color: #1989fa;
}

.gender-icons {
  display: flex;
  gap: 4px;
}

.male .metric-icon {
  color: #07c160;
}

.female .metric-icon {
  color: #ee0a24;
}

.metric-value {
  font-size: 16px;
  font-weight: 700;
  color: #323233;
}

.record-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebedf0;
}

.engagement-bar {
  flex: 1;
  height: 8px;
  background-color: #ebedf0;
  border-radius: 4px;
  overflow: hidden;
}

.engagement-progress {
  height: 100%;
  border-radius: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.engagement-label {
  font-size: 12px;
  color: #646566;
  font-weight: 500;
}

.custom-popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.custom-popup-content {
  background-color: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.custom-popup-header {
  padding: 16px;
  border-bottom: 1px solid #ebedf0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.custom-popup-header h3 {
  margin: 0;
  font-size: 18px;
  color: white;
  font-weight: 600;
}

.custom-popup-close {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: color 0.3s ease;
}

.custom-popup-close:hover {
  color: white;
}

.custom-popup-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #f7f8fa;
}

.detail-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  transform: translateY(20px);
}

.detail-card:nth-child(1) { animation-delay: 0.1s; }
.detail-card:nth-child(2) { animation-delay: 0.2s; }
.detail-card:nth-child(3) { animation-delay: 0.3s; }
.detail-card:nth-child(4) { animation-delay: 0.4s; }
.detail-card:nth-child(5) { animation-delay: 0.5s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.detail-card-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebedf0;
}

.detail-card-header .card-icon {
  font-size: 20px;
  margin-right: 8px;
  color: #1989fa;
}

.detail-card-header span {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1989fa;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #646566;
}

.gender-distribution {
  margin-top: 16px;
}

.gender-bar {
  position: relative;
  height: 10px;
  background-color: #ebedf0;
  border-radius: 5px;
  margin-bottom: 8px;
  overflow: hidden;
}

.gender-male {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background-color: #07c160;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 4px;
  color: white;
  font-size: 12px;
}

.gender-female {
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  background-color: #ee0a24;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-left: 4px;
  color: white;
  font-size: 12px;
}

.gender-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #646566;
}

.male-label {
  color: #07c160;
}

.female-label {
  color: #ee0a24;
}

.behavior-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.behavior-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #323233;
}

.behavior-icon {
  font-size: 20px;
  color: #1989fa;
}

.shopper .behavior-icon {
  color: #07c160;
}

.browser .behavior-icon {
  color: #ee0a24;
}

.dwell .behavior-icon {
  color: #1989fa;
}

.engagement .behavior-icon {
  color: #ff976a;
}

.behavior-info {
  flex: 1;
}

.behavior-value {
  font-size: 18px;
  font-weight: 700;
  color: #323233;
  margin-bottom: 4px;
}

.behavior-label {
  font-size: 12px;
  color: #646566;
}

.age-distribution {
  margin-top: 16px;
}

.age-bar {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  gap: 10px;
}

.age-label {
  font-size: 14px;
  color: #646566;
  font-weight: 500;
  min-width: 60px;
}

.age-progress {
  flex: 1;
  height: 10px;
  background-color: #ebedf0;
  border-radius: 5px;
  overflow: hidden;
}

.age-progress-bar {
  height: 100%;
  border-radius: 5px;
  transition: width 0.3s ease;
}

.age-count {
  font-size: 12px;
  color: #969799;
  min-width: 30px;
  text-align: right;
}

.processing-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.processing-item {
  text-align: center;
}

.processing-label {
  font-size: 12px;
  color: #646566;
  margin-bottom: 4px;
}

.processing-value {
  font-size: 16px;
  font-weight: 700;
  color: #323233;
}

.notes-content {
  background: #f7f8fa;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  color: #323233;
  line-height: 1.6;
  white-space: pre-wrap; /* 保留换行符 */
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

.custom-popup-footer {
  padding: 16px;
  border-top: 1px solid #ebedf0;
  background-color: white;
}

.custom-popup-footer .van-button {
  height: 44px;
  font-size: 16px;
  font-weight: 500;
}

.custom-popup-footer .van-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.custom-popup-footer .van-button--info {
  background: #f7f8fa;
  color: #323233;
  border: 1px solid #ebedf0;
}

.action-row {
  display: flex;
  justify-content: space-around;
  margin-top: 12px;
  gap: 8px;
}

.action-row .van-button {
  flex: 1;
}

/* 移动端适配 */
@media (max-width: 480px) {
  .overview-card {
    padding: 12px;
  }
  
  .overview-icon {
    width: 32px;
    height: 32px;
    margin-right: 8px;
  }
  
  .overview-icon .van-icon {
    font-size: 16px;
  }
  
  .overview-value {
    font-size: 16px;
  }
  
  .overview-label {
    font-size: 10px;
  }
  
  .filter-card {
    padding: 12px;
  }
  
  .filter-header {
    margin-bottom: 8px;
  }
  
  .filter-icon {
    font-size: 18px;
  }
  
  .filter-header span {
    font-size: 14px;
  }
  
  .records-list {
    padding: 0 12px;
  }
  
  .record-card {
    padding: 12px;
    margin-bottom: 12px;
  }
  
  .record-header {
    margin-bottom: 8px;
    padding-bottom: 8px;
  }
  
  .record-time-icon {
    font-size: 16px;
  }
  
  .record-time {
    font-size: 12px;
  }
  
  .record-arrow {
    font-size: 18px;
  }
  
  .record-name {
    font-size: 16px;
    margin-bottom: 8px;
  }
  
  .record-metrics {
    margin-bottom: 8px;
    padding-bottom: 8px;
  }
  
  .metric-item {
    gap: 4px;
    font-size: 12px;
  }
  
  .metric-icon {
    font-size: 16px;
  }
  
  .metric-value {
    font-size: 14px;
  }
  
  .record-footer {
    gap: 8px;
    margin-top: 8px;
    padding-top: 8px;
  }
  
  .engagement-bar {
    height: 6px;
  }
  
  .engagement-label {
    font-size: 10px;
  }
  
  .empty-state {
    padding: 40px 20px;
  }
  
  .empty-image {
    font-size: 60px;
  }
  
  .empty-text {
    font-size: 18px;
  }
  
  .empty-description {
    font-size: 14px;
  }
  
  .empty-actions {
    flex-direction: column;
    gap: 12px;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-image {
  font-size: 80px;
  color: #dcdee0;
  margin-bottom: 20px;
}

.empty-text {
  font-size: 20px;
  font-weight: 600;
  color: #323233;
  margin-bottom: 8px;
}

.empty-description {
  font-size: 16px;
  color: #969799;
  margin-bottom: 24px;
}

.empty-actions {
  display: flex;
  gap: 16px;
}
</style> 