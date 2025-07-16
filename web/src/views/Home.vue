<template>
  <div class="home-container">
    <!-- 顶部导航 -->
    <div class="home-header">
      <div class="status-indicator" :class="{ active: analysisStatus.isRunning }">
        <div class="status-dot"></div>
        <span>{{ analysisStatus.isRunning ? '运行中' : '已停止' }}</span>
      </div>
      
      <div class="header-title">
        <h1>{{ user.username || 'AI人流分析' }}</h1>
        <p class="header-subtitle">实时智能监控</p>
      </div>
      
      <div class="connection-status" :class="{ connected: analysisStatus.isConnected }">
        <van-icon :name="analysisStatus.isConnected ? 'success' : 'cross'" />
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="home-content">
      <!-- 会话加载中 -->
      <div v-if="sessionLoading" class="loading-prompt">
        <div class="prompt-card">
          <div class="loading-animation">
            <van-loading size="36" color="#4b79cf" />
          </div>
          <h3>正在恢复会话</h3>
          <p>请稍候，正在加载您的分析数据...</p>
        </div>
      </div>

      <!-- 用户已登录时显示完整功能 -->
      <div v-else class="main-content">
        <!-- 摄像头和控制面板 -->
        <div class="camera-section">
          <div class="camera-container">
            <CameraCapture 
              :user-id="user.id"
              @frame-analyzed="onFrameAnalyzed"
              @faces-detected="onFacesDetected"
              @error="onCameraError"
              ref="cameraRef"
            />
            
            <div class="camera-overlay" v-if="analysisStatus.isRunning">
              <div class="analysis-badge">
                <van-icon name="eye-o" />
                <span>实时分析中</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 实时数据概览 -->
        <div class="dashboard-overview">
          <div class="overview-header">
            <h2>实时数据概览</h2>
            <div class="last-update" v-if="analysisStatus.lastUpdate">
              <van-icon name="underway-o" />
              <span>{{ formatTime(analysisStatus.lastUpdate) }}</span>
            </div>
          </div>
          
          <div class="stats-cards">
            <!-- 人流统计 -->
            <div class="stat-card people-card">
              <div class="stat-icon">
                <van-icon name="friends-o" />
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ realtimeStats.activePeople }}</div>
                <div class="stat-label">当前人数</div>
                <div class="stat-trend">
                  <span>总计: {{ realtimeStats.totalPeople }}</span>
                </div>
              </div>
            </div>
            
            <!-- 平均年龄 -->
            <div class="stat-card age-card">
              <div class="stat-icon">
                <van-icon name="user-o" />
              </div>
              <div class="stat-content">
                <div class="stat-value">
                  {{ realtimeStats.avgAge ? Math.round(realtimeStats.avgAge) : '-' }}
                  <span v-if="realtimeStats.avgAge" class="stat-unit">岁</span>
                </div>
                <div class="stat-label">平均年龄</div>
                <div class="stat-trend">
                  <span>实时计算</span>
                </div>
              </div>
            </div>
            
            <!-- 性别分布 -->
            <div class="stat-card gender-card">
              <div class="stat-icon">
                <van-icon name="balance-o" />
              </div>
              <div class="stat-content">
                <div class="gender-distribution">
                  <div class="gender-bar">
                    <div class="male-bar" :style="{width: genderDistribution.male + '%'}">
                      <van-icon name="contact" />
                    </div>
                    <div class="female-bar" :style="{width: genderDistribution.female + '%'}">
                      <van-icon name="like" />
                    </div>
                  </div>
                  <div class="gender-values">
                    <span class="male-value">{{ genderDistribution.male }}%</span>
                    <span class="female-value">{{ genderDistribution.female }}%</span>
                  </div>
                </div>
                <div class="stat-label">性别分布</div>
              </div>
            </div>
            
            <!-- 购物转化 -->
            <div class="stat-card conversion-card">
              <div class="stat-icon">
                <van-icon name="shopping-cart-o" />
              </div>
              <div class="stat-content">
                <div class="stat-value">
                  {{ Math.round(behaviorStats.conversionRate) }}
                  <span class="stat-unit">%</span>
                </div>
                <div class="stat-label">购物转化</div>
                <div class="stat-trend">
                  <span>购物者: {{ behaviorStats.shoppers }} | 浏览者: {{ behaviorStats.browsers }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 年龄分布图表 -->
        <div class="dashboard-section age-distribution-section" v-if="totalAgeAnalyzed > 0">
          <div class="section-header">
            <h2>
              <van-icon name="bar-chart-o" />
              年龄分布
            </h2>
            <div class="section-badge">{{ totalAgeAnalyzed }}人</div>
          </div>
          
          <div class="age-chart">
            <div 
              v-for="(count, ageGroup) in ageDistribution" 
              :key="ageGroup"
              class="age-bar"
            >
              <div class="age-label">{{ ageGroup }}</div>
              <div class="age-progress">
                <div 
                  class="age-progress-bar" 
                  :style="{
                    width: totalAgeAnalyzed > 0 ? (count / totalAgeAnalyzed * 100) + '%' : '0%',
                    backgroundColor: getAgeColor(ageGroup)
                  }"
                ></div>
              </div>
              <div class="age-count">{{ count }}</div>
            </div>
          </div>
        </div>

        <!-- 系统状态 -->
        <div class="dashboard-section system-status-section">
          <div class="section-header">
            <h2>
              <van-icon name="setting-o" />
              系统状态
            </h2>
          </div>
          
          <div class="status-cards">
            <div class="status-card">
              <div class="status-card-icon">
                <van-icon name="video-o" />
              </div>
              <div class="status-card-content">
                <div class="status-card-value">{{ analysisStatus.frameCount.toLocaleString() }}</div>
                <div class="status-card-label">分析帧数</div>
              </div>
            </div>
            
            <div class="status-card">
              <div class="status-card-icon">
                <van-icon name="wifi-o" :class="{ 'connected-icon': analysisStatus.isConnected }" />
              </div>
              <div class="status-card-content">
                <div class="status-card-value">
                  <span :class="{ 'connected-text': analysisStatus.isConnected }">
                    {{ analysisStatus.isConnected ? '已连接' : '未连接' }}
                  </span>
                </div>
                <div class="status-card-label">连接状态</div>
              </div>
            </div>
            
            <div class="status-card">
              <div class="status-card-icon">
                <van-icon name="star-o" />
              </div>
              <div class="status-card-content">
                <div class="status-card-value">{{ Math.round(behaviorStats.avgEngagement * 100) }}%</div>
                <div class="status-card-label">参与度评分</div>
              </div>
            </div>
            
            <div class="status-card">
              <div class="status-card-icon">
                <van-icon name="clock-o" />
              </div>
              <div class="status-card-content">
                <div class="status-card-value">{{ formatDuration(behaviorStats.avgDwellTime) }}</div>
                <div class="status-card-label">平均停留时间</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="dashboard-section quick-actions-section">
          <div class="section-header">
            <h2>
              <van-icon name="apps-o" />
              快速操作
            </h2>
          </div>
          
          <div class="action-buttons">
            <div class="action-button" @click="goToAnalysis">
              <div class="action-icon">
                <van-icon name="chart-trending-o" />
              </div>
              <div class="action-label">详细分析</div>
            </div>
            
            <div class="action-button" @click="goToRecords">
              <div class="action-icon">
                <van-icon name="records" />
              </div>
              <div class="action-label">分析记录</div>
            </div>
            
            <div class="action-button" @click="goToSettings">
              <div class="action-icon">
                <van-icon name="setting-o" />
              </div>
              <div class="action-label">系统设置</div>
            </div>
            
            <div class="action-button" @click="showHelp">
              <div class="action-icon">
                <van-icon name="question-o" />
              </div>
              <div class="action-label">帮助文档</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <van-tabbar v-model="activeTab" @change="onTabChange" class="custom-tabbar">
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
import { authLogger } from '../utils/logger'

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
  authLogger.info('Home页面开始加载')
  
  try {
    // 检查localStorage中的用户信息
    const savedUser = localStorage.getItem('user')
    authLogger.debug('localStorage中的用户信息', savedUser ? '存在' : '不存在')
    
    // 尝试恢复会话
    authLogger.debug('尝试恢复会话')
    const sessionRestored = await analyticsStore.restoreSession()
    authLogger.info('会话恢复结果', sessionRestored)
    
    // 如果已登录，启动定时更新
    if (user.isLoggedIn) {
      authLogger.info('用户已登录，启动定时更新')
      startStatsUpdate()
    } else {
      authLogger.debug('用户未登录')
    }
    
    // 注意：如果会话恢复失败，路由守卫会自动处理跳转
  } finally {
    sessionLoading.value = false
    authLogger.info('Home页面加载完成')
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
  // 只在开发环境打印人脸检测信息
  if (process.env.NODE_ENV === 'development') {
    console.log('检测到人脸:', faces.length)
  }
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
  background-color: #f5f7fa;
  position: relative;
}

/* 顶部导航样式 */
.home-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #4b79cf 0%, #7e57c2 100%);
  color: white;
  position: relative;
  z-index: 10;
}

.status-indicator {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #969799;
  margin-right: 6px;
}

.status-indicator.active .status-dot {
  background-color: #07c160;
  box-shadow: 0 0 10px rgba(7, 193, 96, 0.6);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(7, 193, 96, 0.6); }
  70% { box-shadow: 0 0 0 6px rgba(7, 193, 96, 0); }
  100% { box-shadow: 0 0 0 0 rgba(7, 193, 96, 0); }
}

.header-title {
  text-align: center;
}

.header-title h1 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.header-subtitle {
  font-size: 12px;
  margin: 0;
  opacity: 0.8;
}

.connection-status {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.connection-status.connected {
  background: rgba(7, 193, 96, 0.2);
  border-color: rgba(7, 193, 96, 0.3);
}

.connection-status .van-icon {
  font-size: 16px;
  color: #ee0a24;
}

.connection-status.connected .van-icon {
  color: #07c160;
}

/* 主要内容区域样式 */
.home-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  padding-bottom: 80px;
}

/* 加载提示样式 */
.loading-prompt {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.prompt-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  max-width: 300px;
  animation: fadeIn 0.5s ease-out;
}

.loading-animation {
  margin-bottom: 20px;
}

.prompt-card h3 {
  margin: 0 0 10px;
  color: #323233;
  font-size: 18px;
}

.prompt-card p {
  margin: 0;
  color: #646566;
  font-size: 14px;
}

/* 摄像头区域样式 */
.camera-section {
  margin-bottom: 20px;
}

.camera-container {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.camera-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, 
    rgba(0, 0, 0, 0.3) 0%, 
    rgba(0, 0, 0, 0) 30%, 
    rgba(0, 0, 0, 0) 70%, 
    rgba(0, 0, 0, 0.3) 100%
  );
  pointer-events: none;
}

.analysis-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(7, 193, 96, 0.8);
  border-radius: 20px;
  padding: 4px 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: white;
  font-weight: 500;
  animation: fadeInDown 0.5s ease-out;
}

/* 数据概览样式 */
.dashboard-overview {
  margin-bottom: 20px;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.overview-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #323233;
  margin: 0;
}

.last-update {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #969799;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  animation: fadeIn 0.5s ease-out;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.people-card { animation-delay: 0.1s; }
.age-card { animation-delay: 0.2s; }
.gender-card { animation-delay: 0.3s; }
.conversion-card { animation-delay: 0.4s; }

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}

.people-card .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.age-card .stat-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.gender-card .stat-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.conversion-card .stat-icon {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
}

.stat-icon .van-icon {
  font-size: 24px;
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #323233;
  margin-bottom: 4px;
}

.stat-unit {
  font-size: 14px;
  color: #646566;
  font-weight: 400;
}

.stat-label {
  font-size: 12px;
  color: #969799;
  margin-bottom: 4px;
}

.stat-trend {
  font-size: 11px;
  color: #c8c9cc;
}

/* 性别分布样式 */
.gender-distribution {
  margin-bottom: 4px;
}

.gender-bar {
  height: 10px;
  background: #f2f3f5;
  border-radius: 5px;
  display: flex;
  overflow: hidden;
  margin-bottom: 4px;
}

.male-bar {
  height: 100%;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 4px;
}

.female-bar {
  height: 100%;
  background: linear-gradient(90deg, #ff9a9e 0%, #fad0c4 100%);
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-left: 4px;
}

.gender-bar .van-icon {
  font-size: 8px;
  color: white;
}

.gender-values {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 500;
}

.male-value {
  color: #4facfe;
}

.female-value {
  color: #ff9a9e;
}

/* 图表区域样式 */
.dashboard-section {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  animation: fadeIn 0.5s ease-out;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-header .van-icon {
  font-size: 18px;
}

.section-badge {
  background: #f2f3f5;
  border-radius: 12px;
  padding: 2px 8px;
  font-size: 12px;
  color: #646566;
}

.age-chart {
  padding: 8px 0;
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
  height: 8px;
  background: #f2f3f5;
  border-radius: 4px;
  overflow: hidden;
}

.age-progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.age-count {
  width: 30px;
  text-align: right;
  font-size: 12px;
  color: #646566;
  font-weight: 500;
}

/* 系统状态样式 */
.status-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.status-card {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: transform 0.3s ease;
}

.status-card:hover {
  transform: translateY(-2px);
}

.status-card-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #f2f3f5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.status-card-icon .van-icon {
  font-size: 20px;
  color: #969799;
}

.connected-icon {
  color: #07c160 !important;
}

.status-card-content {
  flex: 1;
}

.status-card-value {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
  margin-bottom: 2px;
}

.connected-text {
  color: #07c160;
}

.status-card-label {
  font-size: 12px;
  color: #969799;
}

/* 快速操作样式 */
.action-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.action-button {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
  border-radius: 16px;
  padding: 16px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
}

.action-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.action-button:active {
  transform: translateY(0);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.action-icon {
  width: 50px;
  height: 50px;
  border-radius: 15px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.action-icon .van-icon {
  font-size: 24px;
  color: #4b79cf;
}

.action-label {
  font-size: 14px;
  font-weight: 600;
  color: #323233;
}

/* 底部导航样式 */
.custom-tabbar {
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  overflow: hidden;
  padding-bottom: env(safe-area-inset-bottom, 0);
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInDown {
  from { 
    opacity: 0;
    transform: translateY(-10px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

/* 移动端适配 */
@media (max-width: 480px) {
  .home-content {
    padding: 12px;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .stat-card {
    padding: 12px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    margin-right: 12px;
  }
  
  .stat-icon .van-icon {
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 18px;
  }
  
  .status-cards {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-icon {
    width: 40px;
    height: 40px;
  }
  
  .action-icon .van-icon {
    font-size: 20px;
  }
  
  .action-label {
    font-size: 12px;
  }
  
  .prompt-card {
    padding: 24px 16px;
  }
}
</style> 