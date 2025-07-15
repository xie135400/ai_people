<template>
  <div class="analysis-container">
    <!-- 顶部导航 -->
    <van-nav-bar 
      title="数据分析"
      left-arrow
      @click-left="$router.back()"
      class="analysis-navbar"
    >
      <template #right>
        <van-icon 
          name="refresh" 
          @click="refreshData"
          :class="{ 'rotating': loading }"
        />
      </template>
    </van-nav-bar>

    <!-- 主要内容 -->
    <div class="analysis-content">
      <!-- 实时监控面板 -->
      <div class="monitor-panel" v-if="analysisStatus.isRunning">
        <div class="monitor-header">
          <div class="monitor-title">
            <van-icon name="video-o" />
            <span>实时监控</span>
          </div>
          <div class="monitor-status">
            <van-tag type="success" size="small">运行中</van-tag>
            <span class="monitor-time">{{ formatTime(analysisStatus.lastUpdate) }}</span>
          </div>
        </div>
        
        <div class="monitor-stats">
          <div class="monitor-item">
            <div class="monitor-value">{{ analysisStatus.frameCount.toLocaleString() }}</div>
            <div class="monitor-label">处理帧数</div>
          </div>
          <div class="monitor-item">
            <div class="monitor-value">{{ realtimeStats.activePeople }}</div>
            <div class="monitor-label">当前人数</div>
          </div>
          <div class="monitor-item">
            <div class="monitor-value">{{ realtimeStats.totalPeople }}</div>
            <div class="monitor-label">总计人数</div>
          </div>
        </div>
      </div>

      <!-- 数据概览 -->
      <div class="overview-section">
        <div class="section-title">
          <van-icon name="chart-trending-o" />
          <span>数据概览</span>
        </div>
        
        <div class="overview-grid">
          <!-- 人流趋势 -->
          <div class="overview-card">
            <div class="card-header">
              <h3>人流趋势</h3>
              <van-icon name="friends-o" color="#1989fa" />
            </div>
            <div class="card-content">
              <div class="trend-chart">
                <div class="trend-line">
                  <div 
                    v-for="(point, index) in peopleCountHistory" 
                    :key="index"
                    class="trend-point"
                    :style="{ 
                      left: `${(index / (peopleCountHistory.length - 1)) * 100}%`,
                      bottom: `${(point / maxPeopleCount) * 100}%`
                    }"
                  ></div>
                </div>
              </div>
              <div class="trend-stats">
                <div class="trend-stat">
                  <span class="stat-label">峰值</span>
                  <span class="stat-value">{{ maxPeopleCount }}</span>
                </div>
                <div class="trend-stat">
                  <span class="stat-label">平均</span>
                  <span class="stat-value">{{ avgPeopleCount }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 年龄分析 -->
          <div class="overview-card">
            <div class="card-header">
              <h3>年龄分析</h3>
              <van-icon name="user-o" color="#07c160" />
            </div>
            <div class="card-content">
              <div class="age-pie-chart">
                <div class="pie-center">
                  <div class="pie-value">{{ totalAgeAnalyzed }}</div>
                  <div class="pie-label">总人数</div>
                </div>
                <div class="pie-segments">
                  <div 
                    v-for="(count, ageGroup) in ageDistribution" 
                    :key="ageGroup"
                    class="pie-segment"
                    :style="{ 
                      background: getAgeColor(ageGroup),
                      width: `${(count / totalAgeAnalyzed) * 100}%`
                    }"
                  ></div>
                </div>
              </div>
              <div class="age-legend">
                <div 
                  v-for="(count, ageGroup) in ageDistribution" 
                  :key="ageGroup"
                  class="legend-item"
                  v-show="count > 0"
                >
                  <div 
                    class="legend-color" 
                    :style="{ background: getAgeColor(ageGroup) }"
                  ></div>
                  <span class="legend-text">{{ ageGroup }}岁</span>
                  <span class="legend-count">{{ count }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 性别分布 -->
          <div class="overview-card">
            <div class="card-header">
              <h3>性别分布</h3>
              <van-icon name="balance-o" color="#ff976a" />
            </div>
            <div class="card-content">
              <div class="gender-chart">
                <div class="gender-bar">
                  <div class="gender-segment male" :style="{ width: `${genderDistribution.male}%` }">
                    <span v-if="genderDistribution.male > 15">{{ genderDistribution.male }}%</span>
                  </div>
                  <div class="gender-segment female" :style="{ width: `${genderDistribution.female}%` }">
                    <span v-if="genderDistribution.female > 15">{{ genderDistribution.female }}%</span>
                  </div>
                </div>
              </div>
              <div class="gender-legend">
                <div class="legend-item">
                  <div class="legend-color male"></div>
                  <span>男性 {{ realtimeStats.maleCount }}人</span>
                </div>
                <div class="legend-item">
                  <div class="legend-color female"></div>
                  <span>女性 {{ realtimeStats.femaleCount }}人</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 行为分析 -->
          <div class="overview-card">
            <div class="card-header">
              <h3>行为分析</h3>
              <van-icon name="shopping-cart-o" color="#ee0a24" />
            </div>
            <div class="card-content">
              <div class="behavior-metrics">
                <div class="metric-item">
                  <div class="metric-circle">
                    <van-circle
                      :current-rate="behaviorStats.conversionRate"
                      :rate="100"
                      :speed="100"
                      :stroke-width="60"
                      color="#ee0a24"
                      layer-color="#f7f8fa"
                      :text="Math.round(behaviorStats.conversionRate) + '%'"
                    />
                  </div>
                  <div class="metric-label">转化率</div>
                </div>
                <div class="metric-item">
                  <div class="metric-circle">
                    <van-circle
                      :current-rate="behaviorStats.avgEngagement * 100"
                      :rate="100"
                      :speed="100"
                      :stroke-width="60"
                      color="#07c160"
                      layer-color="#f7f8fa"
                      :text="Math.round(behaviorStats.avgEngagement * 100) + '%'"
                    />
                  </div>
                  <div class="metric-label">参与度</div>
                </div>
              </div>
              <div class="behavior-stats">
                <div class="behavior-stat">
                  <span class="stat-label">购物者</span>
                  <span class="stat-value">{{ behaviorStats.shoppers }}</span>
                </div>
                <div class="behavior-stat">
                  <span class="stat-label">浏览者</span>
                  <span class="stat-value">{{ behaviorStats.browsers }}</span>
                </div>
                <div class="behavior-stat">
                  <span class="stat-label">停留时间</span>
                  <span class="stat-value">{{ formatDuration(behaviorStats.avgDwellTime) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 详细数据表 -->
      <div class="detail-section">
        <div class="section-title">
          <van-icon name="records" />
          <span>详细数据</span>
        </div>
        
        <van-cell-group inset>
          <van-cell 
            title="实时人数" 
            :value="realtimeStats.activePeople + ' 人'"
            icon="friends-o"
          />
          <van-cell 
            title="累计人数" 
            :value="realtimeStats.totalPeople + ' 人'"
            icon="user-circle-o"
          />
          <van-cell 
            title="平均年龄" 
            :value="realtimeStats.avgAge ? Math.round(realtimeStats.avgAge) + ' 岁' : '暂无数据'"
            icon="user-o"
          />
          <van-cell 
            title="男性比例" 
            :value="genderDistribution.male + '%'"
            icon="user-o"
          />
          <van-cell 
            title="女性比例" 
            :value="genderDistribution.female + '%'"
            icon="user-o"
          />
          <van-cell 
            title="购物转化率" 
            :value="Math.round(behaviorStats.conversionRate) + '%'"
            icon="shopping-cart-o"
          />
          <van-cell 
            title="平均参与度" 
            :value="Math.round(behaviorStats.avgEngagement * 100) + '%'"
            icon="star-o"
          />
          <van-cell 
            title="平均停留时间" 
            :value="formatDuration(behaviorStats.avgDwellTime)"
            icon="clock-o"
          />
          <van-cell 
            title="处理帧数" 
            :value="analysisStatus.frameCount.toLocaleString()"
            icon="video-o"
          />
        </van-cell-group>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalyticsStore } from '../stores/analytics'
import { showToast, showFailToast } from 'vant'

const router = useRouter()
const analyticsStore = useAnalyticsStore()

// 响应式数据
const activeTab = ref(1)
const loading = ref(false)
const peopleCountHistory = ref([])

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

// 计算属性
const maxPeopleCount = computed(() => {
  return Math.max(...peopleCountHistory.value, realtimeStats.activePeople) || 1
})

const avgPeopleCount = computed(() => {
  if (peopleCountHistory.value.length === 0) return 0
  const sum = peopleCountHistory.value.reduce((a, b) => a + b, 0)
  return Math.round(sum / peopleCountHistory.value.length)
})

// 页面加载
onMounted(() => {
  if (!user.isLoggedIn) {
    router.push('/login')
    return
  }
  
  // 初始化历史数据
  generateMockHistory()
})

// 生成模拟历史数据
const generateMockHistory = () => {
  const history = []
  const baseCount = realtimeStats.activePeople || 5
  
  for (let i = 0; i < 20; i++) {
    const variation = Math.random() * 6 - 3 // -3 到 +3 的随机变化
    const count = Math.max(0, Math.round(baseCount + variation))
    history.push(count)
  }
  
  peopleCountHistory.value = history
}

// 刷新数据
const refreshData = async () => {
  try {
    loading.value = true
    
    // 模拟刷新延迟
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新历史数据
    generateMockHistory()
    
    showToast('数据已刷新')
  } catch (error) {
    showFailToast('刷新失败')
  } finally {
    loading.value = false
  }
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
    return `${hours}时${minutes}分`
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
.analysis-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--background-color);
}

.analysis-navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.analysis-navbar :deep(.van-nav-bar__title) {
  color: white;
  font-weight: 600;
}

.analysis-navbar :deep(.van-icon) {
  color: white;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.analysis-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  padding-bottom: 60px;
}

.monitor-panel {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-light);
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.monitor-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
}

.monitor-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.monitor-time {
  font-size: 12px;
  color: var(--text-color-2);
}

.monitor-stats {
  display: flex;
  justify-content: space-around;
}

.monitor-item {
  text-align: center;
}

.monitor-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 4px;
}

.monitor-label {
  font-size: 12px;
  color: var(--text-color-2);
}

.overview-section {
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
}

.overview-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.overview-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: var(--shadow-light);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.card-content {
  /* 内容样式 */
}

.trend-chart {
  height: 80px;
  position: relative;
  background: var(--background-color);
  border-radius: 8px;
  margin-bottom: 12px;
}

.trend-line {
  position: relative;
  height: 100%;
}

.trend-point {
  position: absolute;
  width: 6px;
  height: 6px;
  background: var(--primary-color);
  border-radius: 50%;
  transform: translate(-50%, 50%);
}

.trend-stats {
  display: flex;
  justify-content: space-around;
}

.trend-stat {
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: var(--text-color-2);
  display: block;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
}

.age-pie-chart {
  position: relative;
  margin-bottom: 16px;
}

.pie-center {
  text-align: center;
  margin-bottom: 12px;
}

.pie-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-color);
}

.pie-label {
  font-size: 12px;
  color: var(--text-color-2);
}

.pie-segments {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.pie-segment {
  height: 100%;
  transition: all 0.3s ease;
}

.age-legend {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-text {
  color: var(--text-color-2);
  flex: 1;
}

.legend-count {
  color: var(--text-color);
  font-weight: 500;
}

.gender-chart {
  margin-bottom: 16px;
}

.gender-bar {
  display: flex;
  height: 24px;
  border-radius: 12px;
  overflow: hidden;
  background: var(--background-color);
}

.gender-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  color: white;
  transition: all 0.3s ease;
}

.gender-segment.male {
  background: linear-gradient(135deg, #1989fa 0%, #1976d2 100%);
}

.gender-segment.female {
  background: linear-gradient(135deg, #ee0a24 0%, #f56565 100%);
}

.gender-legend {
  display: flex;
  justify-content: space-around;
}

.gender-legend .legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-color-2);
}

.gender-legend .legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.gender-legend .legend-color.male {
  background: #1989fa;
}

.gender-legend .legend-color.female {
  background: #ee0a24;
}

.behavior-metrics {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
}

.metric-item {
  text-align: center;
}

.metric-circle {
  width: 60px;
  height: 60px;
  margin: 0 auto 8px;
}

.metric-label {
  font-size: 12px;
  color: var(--text-color-2);
}

.behavior-stats {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.behavior-stat {
  text-align: center;
  padding: 8px;
  background: var(--background-color);
  border-radius: 8px;
}

.behavior-stat .stat-label {
  font-size: 12px;
  color: var(--text-color-2);
  display: block;
  margin-bottom: 4px;
}

.behavior-stat .stat-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
}

.detail-section {
  margin-bottom: 20px;
}

/* 移动端适配 */
@media (max-width: 480px) {
  .analysis-content {
    padding: 12px;
  }
  
  .overview-card {
    padding: 12px;
  }
  
  .monitor-panel {
    padding: 12px;
  }
  
  .monitor-stats {
    flex-direction: column;
    gap: 12px;
  }
  
  .monitor-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: var(--background-color);
    border-radius: 8px;
  }
  
  .monitor-value {
    font-size: 16px;
    margin-bottom: 0;
  }
  
  .trend-chart {
    height: 60px;
  }
  
  .pie-value {
    font-size: 20px;
  }
  
  .metric-circle {
    width: 50px;
    height: 50px;
  }
}
</style> 