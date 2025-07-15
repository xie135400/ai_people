import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '../utils/api'
import { wsService } from '../utils/websocket'

export const useAnalyticsStore = defineStore('analytics', () => {
  // 状态
  const user = ref({
    id: null,
    username: null,
    isLoggedIn: false
  })
  
  const analysisStatus = ref({
    isRunning: false,
    isConnected: false,
    frameCount: 0,
    lastUpdate: null
  })
  
  const realtimeStats = ref({
    totalPeople: 23,
    activePeople: 8,
    avgAge: 32.5,
    maleCount: 5,
    femaleCount: 3
  })
  
  const behaviorStats = ref({
    shoppers: 3,
    browsers: 5,
    avgEngagement: 0.65,
    avgDwellTime: 145,
    conversionRate: 37.5
  })
  
  const ageDistribution = ref({
    '0-17': 2,
    '18-25': 4,
    '26-35': 6,
    '36-45': 3,
    '46-55': 2,
    '56-65': 1,
    '65+': 0
  })
  
  const records = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // 统计数据轮询定时器
  let statsPollingTimer = null
  // 会话检查定时器
  let sessionCheckTimer = null
  
  // 计算属性
  const genderDistribution = computed(() => {
    const total = realtimeStats.value.maleCount + realtimeStats.value.femaleCount
    return {
      male: total > 0 ? Math.round((realtimeStats.value.maleCount / total) * 100) : 0,
      female: total > 0 ? Math.round((realtimeStats.value.femaleCount / total) * 100) : 0
    }
  })
  
  const totalAgeAnalyzed = computed(() => {
    return Object.values(ageDistribution.value).reduce((sum, count) => sum + count, 0)
  })
  
  // 方法
  const createSession = async (username) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiService.createSession(username)
      
      if (response.status === 'success') {
        user.value = {
          id: response.user_id,
          username: response.username,
          isLoggedIn: true
        }
        
        // 存储到本地存储
        localStorage.setItem('user', JSON.stringify(user.value))
        
        // 开始会话检查
        startSessionCheck()
        
        return response
      } else {
        throw new Error(response.message || '创建会话失败')
      }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const startAnalysis = async () => {
    try {
      if (!user.value.id) {
        throw new Error('请先登录')
      }
      
      loading.value = true
      error.value = null
      
      const response = await apiService.startAnalysis(user.value.id)
      
      if (response.status === 'success') {
        analysisStatus.value.isRunning = true
        // 连接WebSocket
        wsService.connect(user.value.id, onWebSocketMessage)
        
        // 定期请求统计数据
        startStatsPolling()
        
        // 开始会话检查
        startSessionCheck()
        
        return response
      } else {
        throw new Error(response.message || '启动分析失败')
      }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const stopAnalysis = async () => {
    try {
      if (!user.value.id) {
        throw new Error('请先登录')
      }
      
      loading.value = true
      error.value = null
      
      const response = await apiService.stopAnalysis(user.value.id)
      
      if (response.status === 'success') {
        analysisStatus.value.isRunning = false
        // 停止统计数据轮询
        stopStatsPolling()
        // 断开WebSocket
        wsService.disconnect()
        return response
      } else {
        throw new Error(response.message || '停止分析失败')
      }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const loadRecords = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiService.getRecords()
      records.value = response.records || []
      
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const onWebSocketMessage = (data) => {
    try {
      if (data.type === 'connection_established') {
        analysisStatus.value.isConnected = true
        console.log('WebSocket连接已建立')
      } else if (data.type === 'frame_result') {
        analysisStatus.value.frameCount++
        analysisStatus.value.lastUpdate = new Date()
        
        if (data.stats) {
          updateStats(data.stats)
        }
      } else if (data.type === 'stats_update') {
        updateStats(data.data)
      } else if (data.type === 'error') {
        error.value = data.message
      }
    } catch (err) {
      console.error('处理WebSocket消息失败:', err)
    }
  }
  
  const updateStats = (stats) => {
    if (stats.realtime) {
      realtimeStats.value = {
        totalPeople: stats.realtime.total_people || 0,
        activePeople: stats.realtime.active_tracks || 0,
        avgAge: stats.realtime.avg_age,
        maleCount: stats.realtime.male_count || 0,
        femaleCount: stats.realtime.female_count || 0
      }
    }
    
    if (stats.behavior) {
      behaviorStats.value = {
        shoppers: stats.behavior.shoppers || 0,
        browsers: stats.behavior.browsers || 0,
        avgEngagement: stats.behavior.avg_engagement_score || 0,
        avgDwellTime: stats.behavior.avg_dwell_time || 0,
        conversionRate: stats.behavior.shopper_rate || 0
      }
    }
    
    if (stats.age_distribution) {
      ageDistribution.value = { ...stats.age_distribution }
    }
  }
  
  const logout = () => {
    user.value = {
      id: null,
      username: null,
      isLoggedIn: false
    }
    
    analysisStatus.value = {
      isRunning: false,
      isConnected: false,
      frameCount: 0,
      lastUpdate: null
    }
    
    // 清除本地存储
    localStorage.removeItem('user')
    
    // 停止统计数据轮询
    stopStatsPolling()
    
    // 停止会话检查
    stopSessionCheck()
    
    // 断开WebSocket
    wsService.disconnect()
  }
  
  const restoreSession = async () => {
    try {
      const savedUser = localStorage.getItem('user')
      if (savedUser) {
        const userData = JSON.parse(savedUser)
        
        // 验证会话是否仍然有效
        try {
          const response = await apiService.getSessionStatus(userData.id)
          if (response.user_id === userData.id) {
            // 会话仍然有效，恢复用户状态
            user.value = userData
            
            // 重新建立WebSocket连接
            if (!analysisStatus.value.isConnected) {
              await startAnalysis()
            }
            
            console.log('会话恢复成功:', userData.username)
            return true
          }
        } catch (error) {
          console.log('会话已过期，需要重新登录')
          localStorage.removeItem('user')
          return false
        }
      }
    } catch (err) {
      console.error('恢复会话失败:', err)
      localStorage.removeItem('user')
      return false
    }
    return false
  }

  // 开始统计数据轮询
  const startStatsPolling = () => {
    if (statsPollingTimer) {
      clearInterval(statsPollingTimer)
    }
    
    // 每3秒请求一次统计数据
    statsPollingTimer = setInterval(() => {
      if (wsService && wsService.isConnected()) {
        wsService.requestStats()
      } else {
        console.log('WebSocket未连接，跳过统计数据请求')
      }
    }, 3000)
  }

  // 停止统计数据轮询
  const stopStatsPolling = () => {
    if (statsPollingTimer) {
      clearInterval(statsPollingTimer)
      statsPollingTimer = null
    }
  }

  // 开始会话检查
  const startSessionCheck = () => {
    if (sessionCheckTimer) {
      clearInterval(sessionCheckTimer)
    }
    
    // 每30秒检查一次会话状态
    sessionCheckTimer = setInterval(async () => {
      if (user.value.id) {
        try {
          await apiService.getSessionStatus(user.value.id)
        } catch (error) {
          console.log('会话已过期，自动退出登录')
          logout()
        }
      }
    }, 30000)
  }

  // 停止会话检查
  const stopSessionCheck = () => {
    if (sessionCheckTimer) {
      clearInterval(sessionCheckTimer)
      sessionCheckTimer = null
    }
  }
  
  return {
    // 状态
    user,
    analysisStatus,
    realtimeStats,
    behaviorStats,
    ageDistribution,
    records,
    loading,
    error,
    
    // 计算属性
    genderDistribution,
    totalAgeAnalyzed,
    
    // 方法
    createSession,
    startAnalysis,
    stopAnalysis,
    loadRecords,
    logout,
    restoreSession
  }
}) 