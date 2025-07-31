<template>
  <div class="analysis-container">
    <!-- 顶部导航 -->
    <div class="analysis-header">
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
    </div>

    <!-- 主要内容 -->
    <div class="analysis-content">
      <!-- 实时监控面板 -->
      <div class="dashboard-card monitor-panel" v-if="analysisStatus.isRunning">
        <div class="card-header">
          <div class="header-title">
            <van-icon name="video-o" class="header-icon" />
            <span>实时监控</span>
          </div>
          <div class="monitor-status">
            <van-tag type="success" size="medium" round>运行中</van-tag>
            <span class="monitor-time">{{ formatTime(analysisStatus.lastUpdate) }}</span>
          </div>
        </div>
        
        <div class="monitor-stats">
          <div class="stat-card">
            <div class="stat-value highlight">{{ analysisStatus.frameCount.toLocaleString() }}</div>
            <div class="stat-label">处理帧数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value highlight">{{ realtimeStats.activePeople }}</div>
            <div class="stat-label">当前人数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value highlight">{{ realtimeStats.totalPeople }}</div>
            <div class="stat-label">总计人数</div>
          </div>
        </div>
      </div>

      <!-- 数据概览 -->
      <div class="section-header">
        <van-icon name="chart-trending-o" class="section-icon" />
        <span>数据概览</span>
      </div>
      
      <div class="dashboard-grid">
        <!-- 人流趋势 -->
        <div class="dashboard-card">
          <div class="card-header">
            <div class="header-title">
              <span>人流趋势</span>
            </div>
            <van-icon name="friends-o" class="header-icon" />
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
              <div class="trend-gradient"></div>
            </div>
            <div class="trend-stats">
              <div class="stat-item">
                <div class="stat-value">{{ maxPeopleCount }}</div>
                <div class="stat-label">峰值</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ avgPeopleCount }}</div>
                <div class="stat-label">平均</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 年龄分析 -->
        <div class="dashboard-card">
          <div class="card-header">
            <div class="header-title">
              <span>年龄分析</span>
            </div>
            <van-icon name="user-o" class="header-icon" />
          </div>
          <div class="card-content">
            <div class="age-distribution">
              <div class="age-segments">
                <div 
                  v-for="(count, ageGroup) in ageDistribution" 
                  :key="ageGroup"
                  class="age-segment"
                  :style="{ 
                    width: `${(count / totalAgeAnalyzed) * 100}%`,
                    background: getAgeColor(ageGroup)
                  }"
                  v-show="count > 0"
                >
                  <span v-if="(count / totalAgeAnalyzed) > 0.1">{{ Math.round((count / totalAgeAnalyzed) * 100) }}%</span>
                </div>
              </div>
              <div class="total-count">
                <span class="count-value">{{ totalAgeAnalyzed }}</span>
                <span class="count-label">总人数</span>
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
        <div class="dashboard-card">
          <div class="card-header">
            <div class="header-title">
              <span>性别分布</span>
            </div>
            <van-icon name="balance-o" class="header-icon" />
          </div>
          <div class="card-content">
            <div class="gender-chart">
              <div class="gender-ratio">
                <div class="gender-male" :style="{ width: `${genderDistribution.male}%` }">
                  <van-icon name="manager" />
                  <span>{{ genderDistribution.male }}%</span>
                </div>
                <div class="gender-female" :style="{ width: `${genderDistribution.female}%` }">
                  <span>{{ genderDistribution.female }}%</span>
                  <van-icon name="contact" />
                </div>
              </div>
              <div class="gender-counts">
                <div class="gender-count male">
                  <span class="count-label">男性</span>
                  <span class="count-value">{{ realtimeStats.maleCount }}人</span>
                </div>
                <div class="gender-count female">
                  <span class="count-label">女性</span>
                  <span class="count-value">{{ realtimeStats.femaleCount }}人</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 行为分析 -->
        <div class="dashboard-card">
          <div class="card-header">
            <div class="header-title">
              <span>行为分析</span>
            </div>
            <van-icon name="shopping-cart-o" class="header-icon" />
          </div>
          <div class="card-content">
            <div class="behavior-metrics">
              <div class="metric-card">
                <div class="metric-circle">
                  <van-circle
                    :current-rate="behaviorStats.conversionRate"
                    :rate="100"
                    :speed="100"
                    :stroke-width="10"
                    :size="80"
                    color="linear-gradient(to right, #1989fa, #07c160)"
                    layer-color="#f2f3f5"
                  >
                    <div class="circle-content">
                      <span class="circle-value">{{ Math.round(behaviorStats.conversionRate) }}%</span>
                      <span class="circle-label">转化率</span>
                    </div>
                  </van-circle>
                </div>
              </div>
              <div class="metric-card">
                <div class="metric-circle">
                  <van-circle
                    :current-rate="behaviorStats.avgEngagement * 100"
                    :rate="100"
                    :speed="100"
                    :stroke-width="10"
                    :size="80"
                    color="linear-gradient(to right, #ff976a, #ee0a24)"
                    layer-color="#f2f3f5"
                  >
                    <div class="circle-content">
                      <span class="circle-value">{{ Math.round(behaviorStats.avgEngagement * 100) }}%</span>
                      <span class="circle-label">参与度</span>
                    </div>
                  </van-circle>
                </div>
              </div>
            </div>
            <div class="behavior-stats">
              <div class="behavior-stat">
                <van-icon name="shopping-cart-o" />
                <span class="stat-label">购物者</span>
                <span class="stat-value">{{ behaviorStats.shoppers }}</span>
              </div>
              <div class="behavior-stat">
                <van-icon name="eye-o" />
                <span class="stat-label">浏览者</span>
                <span class="stat-value">{{ behaviorStats.browsers }}</span>
              </div>
              <div class="behavior-stat">
                <van-icon name="clock-o" />
                <span class="stat-label">停留时间</span>
                <span class="stat-value">{{ formatDuration(behaviorStats.avgDwellTime) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 详细数据表 -->
      <div class="section-header">
        <van-icon name="records" class="section-icon" />
        <span>详细数据</span>
      </div>
      
      <div class="detail-table">
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
            icon="manager"
          />
          <van-cell 
            title="女性比例" 
            :value="genderDistribution.female + '%'"
            icon="contact"
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
    <van-tabbar v-model="activeTab" @change="onTabChange" class="analysis-tabbar">
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
  background-color: #f7f8fa;
  color: #323233;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.analysis-header {
  position: sticky;
  top: 0;
  z-index: 100;
}

.analysis-navbar {
  background: linear-gradient(120deg, #3a7bd5, #00d2ff);
  box-shadow: 0 2px 12px rgba(58, 123, 213, 0.2);
}

.analysis-navbar :deep(.van-nav-bar__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.analysis-navbar :deep(.van-icon) {
  color: white;
  font-size: 20px;
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
  padding-bottom: 70px;
}

/* 卡片通用样式 */
.dashboard-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.dashboard-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.header-icon {
  font-size: 20px;
  color: #3a7bd5;
}

.card-content {
  padding: 16px;
}

/* 实时监控面板 */
.monitor-panel {
  background: linear-gradient(135deg, #3a7bd5 0%, #00d2ff 100%);
  color: white;
  margin-bottom: 24px;
}

.monitor-panel .card-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.monitor-panel .header-title {
  color: white;
}

.monitor-panel .header-icon {
  color: white;
}

.monitor-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.monitor-time {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.monitor-stats {
  display: flex;
  justify-content: space-around;
  padding: 16px 0;
}

.stat-card {
  text-align: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 12px;
  min-width: 80px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-value.highlight {
  font-size: 24px;
  color: white;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

/* 区块标题 */
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 24px 0 16px;
  font-size: 18px;
  font-weight: 600;
  color: #323233;
}

.section-icon {
  font-size: 20px;
  color: #3a7bd5;
}

/* 仪表盘网格 */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

/* 人流趋势 */
.trend-chart {
  height: 100px;
  position: relative;
  background: #f7f8fa;
  border-radius: 8px;
  margin-bottom: 16px;
  overflow: hidden;
}

.trend-line {
  position: relative;
  height: 100%;
}

.trend-point {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #3a7bd5;
  border-radius: 50%;
  transform: translate(-50%, 50%);
  z-index: 2;
}

.trend-point::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 16px;
  height: 16px;
  background: rgba(58, 123, 213, 0.2);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
}

.trend-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 50%;
  background: linear-gradient(to top, rgba(58, 123, 213, 0.1), transparent);
  z-index: 1;
}

.trend-stats {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
  background: #f7f8fa;
  border-radius: 8px;
  padding: 12px;
  min-width: 80px;
}

.stat-item .stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #3a7bd5;
  margin-bottom: 4px;
}

.stat-item .stat-label {
  font-size: 12px;
  color: #969799;
}

/* 年龄分析 */
.age-distribution {
  margin-bottom: 16px;
}

.age-segments {
  display: flex;
  height: 24px;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
}

.age-segment {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.total-count {
  text-align: center;
  margin-bottom: 16px;
}

.count-value {
  font-size: 24px;
  font-weight: 700;
  color: #323233;
  display: block;
}

.count-label {
  font-size: 12px;
  color: #969799;
}

.age-legend {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
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
  color: #969799;
  flex: 1;
}

.legend-count {
  color: #323233;
  font-weight: 500;
}

/* 性别分布 */
.gender-chart {
  padding: 8px 0;
}

.gender-ratio {
  display: flex;
  height: 40px;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 16px;
  background: #f7f8fa;
}

.gender-male, .gender-female {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: white;
  gap: 8px;
  transition: all 0.3s ease;
}

.gender-male {
  background: linear-gradient(to right, #3a7bd5, #00d2ff);
}

.gender-female {
  background: linear-gradient(to left, #ff6b6b, #ff9f43);
}

.gender-counts {
  display: flex;
  justify-content: space-around;
}

.gender-count {
  text-align: center;
  padding: 12px;
  border-radius: 8px;
  min-width: 100px;
}

.gender-count.male {
  background: rgba(58, 123, 213, 0.1);
}

.gender-count.female {
  background: rgba(255, 107, 107, 0.1);
}

.count-label {
  font-size: 12px;
  color: #969799;
  display: block;
  margin-bottom: 4px;
}

.count-value {
  font-size: 16px;
  font-weight: 600;
}

.gender-count.male .count-value {
  color: #3a7bd5;
}

.gender-count.female .count-value {
  color: #ff6b6b;
}

/* 行为分析 */
.behavior-metrics {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
}

.metric-circle {
  margin: 0 auto;
  position: relative;
}

.circle-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.circle-value {
  font-size: 16px;
  font-weight: 700;
  color: #323233;
  display: block;
}

.circle-label {
  font-size: 12px;
  color: #969799;
}

.behavior-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.behavior-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  background: #f7f8fa;
  border-radius: 8px;
  text-align: center;
}

.behavior-stat .van-icon {
  font-size: 24px;
  color: #3a7bd5;
  margin-bottom: 8px;
}

.behavior-stat .stat-label {
  font-size: 12px;
  color: #969799;
  margin-bottom: 4px;
}

.behavior-stat .stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

/* 详细数据表 */
.detail-table {
  margin-bottom: 24px;
}

.detail-table :deep(.van-cell) {
  align-items: center;
}

.detail-table :deep(.van-cell__title) {
  flex: 3;
}

.detail-table :deep(.van-cell__value) {
  flex: 2;
  color: #3a7bd5;
  font-weight: 500;
}

.detail-table :deep(.van-icon) {
  font-size: 18px;
  color: #3a7bd5;
}

/* 底部导航 */
.analysis-tabbar {
  box-shadow: 0 -1px 10px rgba(0, 0, 0, 0.05);
}

.analysis-tabbar :deep(.van-tabbar-item--active) {
  color: #3a7bd5;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .analysis-content {
    padding: 12px;
  }
  
  .section-header {
    margin: 16px 0 12px;
  }
  
  .behavior-stats {
    grid-template-columns: 1fr;
  }
  
  .age-legend {
    grid-template-columns: 1fr 1fr;
  }
  
  .monitor-stats {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .stat-card {
    flex: 1;
    min-width: 100px;
  }
}
</style> 