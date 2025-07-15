<template>
  <div class="home-container">
    <!-- 顶部导航 -->
    <van-nav-bar 
      :title="user.username || 'AI人流分析'"
      class="home-navbar"
    >
      <template #left>
        <van-tag 
          :type="analysisStatus.isRunning ? 'success' : 'default'"
          size="medium"
        >
          {{ analysisStatus.isRunning ? '运行中' : '已停止' }}
        </van-tag>
      </template>
      
      <template #right>
        <van-icon 
          :name="analysisStatus.isConnected ? 'success' : 'cross'"
          :color="analysisStatus.isConnected ? '#07c160' : '#ee0a24'"
          size="16"
        />
      </template>
    </van-nav-bar>

    <!-- 主要内容区域 -->
    <div class="home-content">
      <!-- 会话加载中 -->
      <div v-if="sessionLoading" class="loading-prompt">
        <div class="prompt-card">
          <van-loading size="30" color="#1989fa" />
          <p style="margin-top: 16px;">正在恢复会话...</p>
        </div>
      </div>

      <!-- 用户已登录时显示完整功能 -->
      <div v-else class="main-content">
        <!-- 摄像头和控制面板 -->
        <div class="camera-section">
          <CameraCapture 
            :user-id="user.id"
            @frame-analyzed="onFrameAnalyzed"
            @faces-detected="onFacesDetected"
            @error="onCameraError"
            ref="cameraRef"
          />
        </div>

        <!-- 实时统计卡片 -->
        <div class="stats-section">
          <div class="section-title">
            <van-icon name="chart-trending-o" />
            <span>实时统计</span>
            <van-tag v-if="analysisStatus.lastUpdate" type="primary" size="mini">
              {{ formatTime(analysisStatus.lastUpdate) }}
            </van-tag>
          </div>
          
          <div class="stats-grid">
            <!-- 人流统计 -->
            <div class="stats-card">
              <div class="stats-card-header">
                <span class="stats-card-title">当前人数</span>
                <van-icon name="friends-o" color="#1989fa" />
              </div>
              <div class="stats-card-value">{{ realtimeStats.activePeople }}</div>
              <div class="stats-card-footer">
                <span class="stats-card-label">总计: {{ realtimeStats.totalPeople }}</span>
              </div>
            </div>
            
            <!-- 平均年龄 -->
            <div class="stats-card">
              <div class="stats-card-header">
                <span class="stats-card-title">平均年龄</span>
                <van-icon name="user-o" color="#07c160" />
              </div>
              <div class="stats-card-value">
                {{ realtimeStats.avgAge ? Math.round(realtimeStats.avgAge) : '-' }}
                <span v-if="realtimeStats.avgAge" class="stats-card-unit">岁</span>
              </div>
              <div class="stats-card-footer">
                <span class="stats-card-label">实时计算</span>
              </div>
            </div>
            
            <!-- 性别分布 -->
            <div class="stats-card">
              <div class="stats-card-header">
                <span class="stats-card-title">性别分布</span>
                <van-icon name="balance-o" color="#ff976a" />
              </div>
              <div class="gender-stats">
                <div class="gender-item">
                  <span class="gender-label">男</span>
                  <span class="gender-value">{{ genderDistribution.male }}%</span>
                </div>
                <div class="gender-item">
                  <span class="gender-label">女</span>
                  <span class="gender-value">{{ genderDistribution.female }}%</span>
                </div>
              </div>
            </div>
            
            <!-- 行为分析 -->
            <div class="stats-card">
              <div class="stats-card-header">
                <span class="stats-card-title">购物转化</span>
                <van-icon name="shopping-cart-o" color="#ee0a24" />
              </div>
              <div class="stats-card-value">
                {{ Math.round(behaviorStats.conversionRate) }}
                <span class="stats-card-unit">%</span>
              </div>
              <div class="stats-card-footer">
                <span class="stats-card-label">
                  购物者: {{ behaviorStats.shoppers }} | 浏览者: {{ behaviorStats.browsers }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 年龄分布图表 -->
        <div class="chart-section" v-if="totalAgeAnalyzed > 0">
          <div class="section-title">
            <van-icon name="bar-chart-o" />
            <span>年龄分布</span>
            <van-tag type="primary" size="mini">{{ totalAgeAnalyzed }}人</van-tag>
          </div>
          
          <div class="age-chart">
            <div 
              v-for="(count, ageGroup) in ageDistribution" 
              :key="ageGroup"
              class="age-bar"
            >
              <div class="age-label">{{ ageGroup }}</div>
              <div class="age-progress">
                <van-progress 
                  :percentage="totalAgeAnalyzed > 0 ? Math.round((count / totalAgeAnalyzed) * 100) : 0"
                  :color="getAgeColor(ageGroup)"
                  :show-pivot="false"
                  stroke-width="8"
                />
              </div>
              <div class="age-count">{{ count }}</div>
            </div>
          </div>
        </div>

        <!-- 系统状态 -->
        <div class="status-section">
          <div class="section-title">
            <van-icon name="setting-o" />
            <span>系统状态</span>
          </div>
          
          <van-cell-group inset>
            <van-cell 
              title="分析帧数" 
              :value="analysisStatus.frameCount.toLocaleString()"
              icon="video-o"
            />
            <van-cell 
              title="连接状态" 
              :value="analysisStatus.isConnected ? '已连接' : '未连接'"
              icon="wifi-o"
            >
              <template #value>
                <van-tag 
                  :type="analysisStatus.isConnected ? 'success' : 'danger'"
                  size="medium"
                >
                  {{ analysisStatus.isConnected ? '已连接' : '未连接' }}
                </van-tag>
              </template>
            </van-cell>
            <van-cell 
              title="参与度评分" 
              :value="Math.round(behaviorStats.avgEngagement * 100) + '%'"
              icon="star-o"
            />
            <van-cell 
              title="平均停留时间" 
              :value="formatDuration(behaviorStats.avgDwellTime)"
              icon="clock-o"
            />
          </van-cell-group>
        </div>

        <!-- 快速操作 -->
        <div class="quick-actions">
          <div class="section-title">
            <van-icon name="apps-o" />
            <span>快速操作</span>
          </div>
          
          <van-grid :column-num="2" :border="false">
            <van-grid-item 
              icon="chart-trending-o" 
              text="详细分析"
              @click="goToAnalysis"
            />
            <van-grid-item 
              icon="records" 
              text="分析记录"
              @click="goToRecords"
            />
            <van-grid-item 
              icon="setting-o" 
              text="系统设置"
              @click="goToSettings"
            />
            <van-grid-item 
              icon="question-o" 
              text="帮助文档"
              @click="showHelp"
            />
          </van-grid>
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
import CameraCapture from '../components/CameraCapture.vue'

const router = useRouter()
const analyticsStore = useAnalyticsStore()

// 响应式数据
const activeTab = ref(0)
const loading = ref(false)
const sessionLoading = ref(true) // 会话加载状态
const cameraRef = ref(null)
let statsUpdateInterval = null

// 从store获取数据
const { 
  user, 
  analysisStatus, 
  realtimeStats, 
  behaviorStats, 
  ageDistribution,
  genderDistribution,
  totalAgeAnalyzed
} = analyticsStore

// 检查登录状态
onMounted(async () => {
  console.log('Home页面：开始加载')
  
  try {
    // 检查localStorage中的用户信息
    const savedUser = localStorage.getItem('user')
    console.log('Home页面：localStorage中的用户信息', savedUser)
    
    // 尝试恢复会话
    console.log('Home页面：尝试恢复会话')
    const sessionRestored = await analyticsStore.restoreSession()
    console.log('Home页面：会话恢复结果', sessionRestored)
    
    // 再次检查localStorage
    const savedUserAfter = localStorage.getItem('user')
    console.log('Home页面：恢复会话后的用户信息', savedUserAfter)
    
    // 如果已登录，启动定时更新
    if (user.isLoggedIn) {
      console.log('Home页面：用户已登录，启动定时更新')
      startStatsUpdate()
    } else {
      console.log('Home页面：用户未登录')
    }
    
    // 注意：如果会话恢复失败，路由守卫会自动处理跳转
  } finally {
    sessionLoading.value = false
    console.log('Home页面：加载完成')
  }
})

// 清理定时器
onUnmounted(() => {
  if (statsUpdateInterval) {
    clearInterval(statsUpdateInterval)
  }
})

// 启动统计数据更新
const startStatsUpdate = () => {
  // 每3秒更新一次统计数据
  statsUpdateInterval = setInterval(() => {
    if (analysisStatus.isRunning) {
      // 模拟数据更新
      updateMockStats()
    }
  }, 3000)
}

// 模拟统计数据更新
const updateMockStats = () => {
  // 模拟人数变化
  const variation = Math.random() * 4 - 2 // -2 到 +2 的变化
  const newActivePeople = Math.max(0, Math.round(realtimeStats.activePeople + variation))
  
  realtimeStats.activePeople = newActivePeople
  realtimeStats.totalPeople = Math.max(realtimeStats.totalPeople, newActivePeople)
  
  // 模拟年龄变化
  if (Math.random() > 0.7) {
    const ageGroups = Object.keys(ageDistribution)
    const randomGroup = ageGroups[Math.floor(Math.random() * ageGroups.length)]
    ageDistribution[randomGroup] = Math.max(0, ageDistribution[randomGroup] + (Math.random() > 0.5 ? 1 : -1))
  }
  
  // 模拟性别分布变化
  if (Math.random() > 0.8) {
    const genderChange = Math.random() > 0.5 ? 1 : -1
    realtimeStats.maleCount = Math.max(0, realtimeStats.maleCount + genderChange)
    realtimeStats.femaleCount = Math.max(0, realtimeStats.femaleCount - genderChange)
  }
  
  // 模拟行为数据变化
  if (Math.random() > 0.6) {
    behaviorStats.shoppers = Math.max(0, behaviorStats.shoppers + (Math.random() > 0.5 ? 1 : -1))
    behaviorStats.browsers = Math.max(0, behaviorStats.browsers + (Math.random() > 0.5 ? 1 : -1))
    behaviorStats.conversionRate = Math.min(100, Math.max(0, behaviorStats.conversionRate + (Math.random() * 4 - 2)))
  }
  
  // 更新最后更新时间
  analysisStatus.lastUpdate = new Date()
}

// 处理摄像头帧分析结果
const onFrameAnalyzed = (stats) => {
  // 更新分析状态
  analysisStatus.isRunning = true
  analysisStatus.isConnected = true
  analysisStatus.frameCount++
  analysisStatus.lastUpdate = new Date()
  
  // 更新统计数据
  if (stats.realtime) {
    realtimeStats.totalPeople = stats.realtime.total_people || realtimeStats.totalPeople
    realtimeStats.activePeople = stats.realtime.active_tracks || 0
    realtimeStats.avgAge = stats.realtime.avg_age || realtimeStats.avgAge
    realtimeStats.maleCount = stats.realtime.male_count || 0
    realtimeStats.femaleCount = stats.realtime.female_count || 0
  }
  
  if (stats.behavior) {
    behaviorStats.shoppers = stats.behavior.shoppers || 0
    behaviorStats.browsers = stats.behavior.browsers || 0
    behaviorStats.avgEngagement = stats.behavior.avg_engagement_score || 0
    behaviorStats.avgDwellTime = stats.behavior.avg_dwell_time || 0
    behaviorStats.conversionRate = stats.behavior.shopper_rate || 0
  }
  
  if (stats.age_distribution) {
    Object.assign(ageDistribution, stats.age_distribution)
  }
}

// 处理检测到的人脸
const onFacesDetected = (faces) => {
  console.log('检测到人脸:', faces.length)
  // 这里可以添加更多的人脸处理逻辑
}

// 处理摄像头错误
const onCameraError = (error) => {
  console.error('摄像头错误:', error)
  analysisStatus.isRunning = false
  analysisStatus.isConnected = false
  showFailToast('摄像头出现错误')
}

// 导航方法
const goToAnalysis = () => {
  router.push('/analysis')
}

const goToRecords = () => {
  router.push('/records')
}

const goToSettings = () => {
  router.push('/settings')
}

const showHelp = () => {
  showDialog({
    title: '帮助文档',
    message: `
AI人流分析系统使用指南：

1. 点击"开始分析"启动实时监控
2. 查看实时统计数据和图表
3. 在"详细分析"中查看更多信息
4. 在"分析记录"中查看历史数据
5. 在"系统设置"中调整参数

如需更多帮助，请联系技术支持。
    `,
  })
}

// 底部导航切换
const onTabChange = (index) => {
  const routes = ['/', '/analysis', '/records', '/settings']
  if (routes[index]) {
    router.push(routes[index])
  }
}

// 格式化时间
const formatTime = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleTimeString('zh-CN', { 
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 格式化持续时间
const formatDuration = (seconds) => {
  if (!seconds || seconds === 0) return '0秒'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}时${minutes}分${secs}秒`
  } else if (minutes > 0) {
    return `${minutes}分${secs}秒`
  } else {
    return `${secs}秒`
  }
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
</script>

<style scoped>
.home-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f7f8fa;
}

.home-navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.home-navbar :deep(.van-nav-bar__title) {
  color: white;
  font-weight: 600;
}

.home-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  padding-bottom: 60px;
}

.loading-prompt {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.prompt-card {
  background: white;
  border-radius: 16px;
  padding: 40px 20px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 300px;
}

.prompt-card h3 {
  margin: 16px 0 8px;
  color: #323233;
  font-size: 18px;
}

.prompt-card p {
  margin: 0 0 24px;
  color: #646566;
  font-size: 14px;
}

.main-content {
  /* 主要内容样式 */
}

.camera-section {
  margin-bottom: 20px;
}

.stats-section {
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stats-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stats-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stats-card-title {
  font-size: 14px;
  color: #646566;
  font-weight: 500;
}

.stats-card-value {
  font-size: 24px;
  font-weight: 700;
  color: #323233;
  margin-bottom: 8px;
}

.stats-card-unit {
  font-size: 14px;
  color: #646566;
  font-weight: 400;
}

.stats-card-footer {
  font-size: 12px;
  color: #969799;
}

.stats-card-label {
  font-size: 12px;
  color: #969799;
}

.gender-stats {
  display: flex;
  gap: 16px;
}

.gender-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.gender-label {
  font-size: 12px;
  color: #646566;
  margin-bottom: 4px;
}

.gender-value {
  font-size: 18px;
  font-weight: 600;
  color: #323233;
}

.chart-section {
  margin-bottom: 20px;
}

.age-chart {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.age-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.age-bar:last-child {
  margin-bottom: 0;
}

.age-label {
  width: 50px;
  font-size: 12px;
  color: #646566;
  font-weight: 500;
}

.age-progress {
  flex: 1;
}

.age-count {
  width: 30px;
  text-align: right;
  font-size: 12px;
  color: #646566;
  font-weight: 500;
}

.status-section {
  margin-bottom: 20px;
}

.quick-actions {
  margin-bottom: 20px;
}

.quick-actions :deep(.van-grid-item__content) {
  background: white;
  border-radius: 12px;
  margin: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.quick-actions :deep(.van-grid-item__content:active) {
  transform: scale(0.95);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.quick-actions :deep(.van-icon) {
  font-size: 24px;
  color: #1989fa;
  margin-bottom: 8px;
}

.quick-actions :deep(.van-grid-item__text) {
  font-size: 12px;
  color: #323233;
  font-weight: 500;
}

/* 移动端适配 */
@media (max-width: 480px) {
  .home-content {
    padding: 12px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .stats-card {
    padding: 12px;
  }
  
  .stats-card-value {
    font-size: 20px;
  }
  
  .control-icon {
    width: 50px;
    height: 50px;
  }
  
  .control-title {
    font-size: 16px;
  }
  
  .prompt-card {
    padding: 30px 16px;
  }
}
</style> 