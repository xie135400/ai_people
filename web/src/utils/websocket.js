import { wsLogger } from './logger'

class WebSocketService {
  constructor() {
    this.ws = null
    this.userId = null
    this.onMessage = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 3000
    this.isConnecting = false
    this.isManualClose = false
  }

  connect(userId, onMessage) {
    if (this.isConnecting) {
      wsLogger.debug('WebSocket正在连接中...')
      return
    }

    this.userId = userId
    this.onMessage = onMessage
    this.isManualClose = false
    this.isConnecting = true

    const wsUrl = `ws://localhost:8443/ws/${userId}`
    wsLogger.info('连接WebSocket:', wsUrl)

    try {
      this.ws = new WebSocket(wsUrl)
      
      // 设置全局访问点，以便其他组件可以发送消息
      window.wsService = this
      
      this.ws.onopen = () => {
        wsLogger.info('WebSocket连接已建立')
        this.isConnecting = false
        this.reconnectAttempts = 0
        
        // 发送连接确认（与PC端兼容）
        this.send({
          type: 'connection',
          user_id: userId,
          timestamp: new Date().toISOString()
        })
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // 只在调试模式下打印详细消息，减少生产环境的输出
          if (data.type === 'frame_result') {
            wsLogger.debug('收到帧分析结果')
            // 通知 CameraCapture 组件
            if (window.cameraCapture) {
              window.cameraCapture.handleFrameResult(data)
            }
          } else {
            wsLogger.debug('收到WebSocket消息:', data.type)
          }
          
          if (this.onMessage) {
            this.onMessage(data)
          }
        } catch (error) {
          wsLogger.error('解析WebSocket消息失败:', error)
        }
      }

      this.ws.onclose = (event) => {
        wsLogger.info('WebSocket连接已关闭:', event.code, event.reason)
        this.isConnecting = false
        
        if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          wsLogger.info(`WebSocket重连尝试 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`)
          
          setTimeout(() => {
            this.connect(this.userId, this.onMessage)
          }, this.reconnectInterval)
        }
      }

      this.ws.onerror = (error) => {
        wsLogger.error('WebSocket错误:', error)
        this.isConnecting = false
        
        if (this.onMessage) {
          this.onMessage({
            type: 'error',
            message: 'WebSocket连接错误'
          })
        }
      }
    } catch (error) {
      wsLogger.error('创建WebSocket连接失败:', error)
      this.isConnecting = false
      
      if (this.onMessage) {
        this.onMessage({
          type: 'error',
          message: '创建WebSocket连接失败'
        })
      }
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(data))
        
        // 只在调试模式下打印发送的消息，减少生产环境的输出
        if (data.type === 'video_frame') {
          wsLogger.debug('发送视频帧数据')
        } else {
          wsLogger.debug('发送WebSocket消息:', data.type)
        }
      } catch (error) {
        wsLogger.error('发送WebSocket消息失败:', error)
      }
    } else {
      wsLogger.debug('WebSocket未连接，无法发送消息')
    }
  }

  disconnect() {
    this.isManualClose = true
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    this.userId = null
    this.onMessage = null
    this.reconnectAttempts = 0
    this.isConnecting = false
    
    // 清理全局访问点
    if (window.wsService === this) {
      delete window.wsService
    }
    
    wsLogger.info('WebSocket已手动断开')
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }

  getReadyState() {
    if (!this.ws) return 'CLOSED'
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING'
      case WebSocket.OPEN:
        return 'OPEN'
      case WebSocket.CLOSING:
        return 'CLOSING'
      case WebSocket.CLOSED:
        return 'CLOSED'
      default:
        return 'UNKNOWN'
    }
  }

  // 请求统计数据
  requestStats() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.send({
        type: 'get_stats',
        user_id: this.userId,
        timestamp: new Date().toISOString()
      })
    } else {
      wsLogger.debug('WebSocket未连接，无法请求统计数据，状态:', this.getReadyState())
    }
  }

  // 检查是否已连接
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

export const wsService = new WebSocketService()
export default wsService 