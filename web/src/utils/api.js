import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      // 服务器返回错误状态码
      const message = error.response.data?.detail || error.response.data?.message || '请求失败'
      return Promise.reject(new Error(message))
    } else if (error.request) {
      // 请求发送失败
      return Promise.reject(new Error('网络连接失败'))
    } else {
      // 其他错误
      return Promise.reject(new Error(error.message || '未知错误'))
    }
  }
)

export const apiService = {
  // 创建会话
  createSession(username) {
    return api.post('/create-session', { username })
  },
  
  // 获取会话状态
  getSessionStatus(userId) {
    return api.get(`/status/${userId}`)
  },
  
  // 开始分析
  startAnalysis(userId) {
    return api.post(`/start/${userId}`)
  },
  
  // 停止分析
  stopAnalysis(userId) {
    return api.post(`/stop/${userId}`)
  },
  
  // 获取分析记录
  getRecords() {
    return api.get('/records/all')
  },
  
  // 获取单个记录详情
  getRecordDetail(recordId) {
    return api.get(`/record/all/${recordId}`)
  },
  
  // 获取统计数据
  getStats(userId) {
    return api.get(`/stats/${userId}`)
  }
}

export default api 