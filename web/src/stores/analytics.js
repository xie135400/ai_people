import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '../utils/api'
import { wsService } from '../utils/websocket'
import { authLogger } from '../utils/logger'

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
        
        // 存储到本地存储（包含时间戳）
        const userWithTimestamp = {
          ...user.value,
          loginTime: new Date().toISOString(),
          lastActivity: new Date().toISOString()
        }
        localStorage.setItem('user', JSON.stringify(userWithTimestamp))
        
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
      
      // 如果已经在运行中，直接返回成功
      if (analysisStatus.value.isRunning) {
        authLogger.info('分析已在运行中，跳过重复启动')
        return { status: 'success', message: '分析已在运行中' }
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
        authLogger.info('WebSocket连接已建立')
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
      authLogger.error('处理WebSocket消息失败:', err)
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
        
        // 检查缓存是否过期（7天）
        const loginTime = new Date(userData.loginTime || userData.created_at || Date.now())
        const now = new Date()
        const daysSinceLogin = (now - loginTime) / (1000 * 60 * 60 * 24)
        
        if (daysSinceLogin > 7) {
          authLogger.info('用户缓存已过期，需要重新登录')
          localStorage.removeItem('user')
          return false
        }
        
        // 临时禁用会话验证，直接恢复用户状态
        authLogger.info('恢复用户状态（跳过会话验证）:', userData.username)
        user.value = {
          id: userData.id,
          username: userData.username,
          isLoggedIn: true
        }
        
        // 更新最后活动时间
        const updatedUser = {
          ...userData,
          lastActivity: new Date().toISOString()
        }
        localStorage.setItem('user', JSON.stringify(updatedUser))
        
        // 重新建立WebSocket连接
        if (!analysisStatus.value.isConnected) {
          try {
            // 直接连接WebSocket，不调用startAnalysis避免"分析已在运行中"错误
            wsService.connect(userData.id, onWebSocketMessage)
            analysisStatus.value.isConnected = true
            authLogger.info('WebSocket连接已重新建立')
          } catch (error) {
            authLogger.error('重新建立WebSocket连接失败:', error)
          }
        }
        
        authLogger.info('会话恢复成功:', userData.username)
        return true
        
        // 以下是原来的会话验证代码，暂时注释掉
        /*
        // 验证会话是否仍然有效
        try {
          console.log('正在验证会话状态，用户ID:', userData.id)
          const response = await apiService.getSessionStatus(userData.id)
          console.log('会话状态验证响应:', response)
          
          if (response.user_id === userData.id) {
            // 会话仍然有效，恢复用户状态
            user.value = {
              id: userData.id,
              username: userData.username,
              isLoggedIn: true
            }
            
            // 更新最后活动时间
            const updatedUser = {
              ...userData,
              lastActivity: new Date().toISOString()
            }
            localStorage.setItem('user', JSON.stringify(updatedUser))
            
            // 重新建立WebSocket连接
            if (!analysisStatus.value.isConnected) {
              await startAnalysis()
            }
            
            console.log('会话恢复成功:', userData.username)
            return true
          } else {
            console.log('会话验证失败，用户ID不匹配')
            localStorage.removeItem('user')
            return false
          }
        } catch (error) {
          console.log('会话验证出错:', error)
          // 如果是网络错误或服务器错误，不要删除缓存，而是跳过验证
          if (error.message.includes('网络') || error.message.includes('Failed to fetch')) {
            console.log('网络错误，跳过会话验证，直接恢复用户状态')
            user.value = {
              id: userData.id,
              username: userData.username,
              isLoggedIn: true
            }
            return true
          }
          
          console.log('会话已过期，需要重新登录')
          localStorage.removeItem('user')
          return false
        }
        */
      }
          } catch (err) {
        authLogger.error('恢复会话失败:', err)
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
        authLogger.debug('WebSocket未连接，跳过统计数据请求')
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
          authLogger.info('会话已过期，自动退出登录')
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