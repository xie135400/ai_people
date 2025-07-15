# 移动端WebSocket迁移说明

## 概述

移动端已从使用HTTP API接口改为使用WebSocket协议，与PC端保持一致的通信方式。

## 主要修改

### 1. WebSocket连接地址修改

**修改前：**
```javascript
const wsUrl = `ws://localhost:3000/ws/${userId}` // 通过Vite代理
```

**修改后：**
```javascript
const wsUrl = `ws://localhost:8443/ws/${userId}` // 直接连接后端
```

### 2. 视频帧传输方式修改

**修改前：**
```javascript
// 使用HTTP POST发送FormData
const formData = new FormData()
formData.append('frame', blob, 'frame.jpg')
formData.append('user_id', props.userId)

const response = await fetch('/api/analyze-frame', {
  method: 'POST',
  body: formData
})
```

**修改后：**
```javascript
// 使用WebSocket发送base64编码的图像数据
const reader = new FileReader()
reader.onload = function(e) {
  const base64Data = e.target.result
  
  window.wsService.send({
    type: 'video_frame',
    frame: base64Data,
    user_id: props.userId,
    timestamp: Date.now()
  })
}
reader.readAsDataURL(blob)
```

### 3. 消息处理机制

**新增消息类型：**
- `connection`: 连接确认
- `video_frame`: 视频帧数据
- `frame_result`: 帧处理结果
- `get_stats`: 请求统计数据
- `stats_update`: 统计数据更新

### 4. 统计数据获取方式

**修改前：**
```javascript
// 通过HTTP API轮询获取统计数据
const response = await fetch(`/api/stats/${userId}`)
```

**修改后：**
```javascript
// 通过WebSocket请求统计数据
wsService.send({
  type: 'get_stats',
  user_id: userId,
  timestamp: new Date().toISOString()
})
```

## 技术实现

### WebSocket服务增强

1. **全局访问点**：设置`window.wsService`供其他组件使用
2. **消息路由**：根据消息类型分发到相应的处理函数
3. **自动重连**：网络中断时自动重连
4. **状态管理**：统一的连接状态管理

### CameraCapture组件修改

1. **帧数据处理**：将blob转换为base64通过WebSocket发送
2. **结果接收**：通过全局回调接收帧处理结果
3. **人脸框显示**：实时显示检测到的人脸框

### Analytics Store增强

1. **轮询机制**：定期请求统计数据
2. **数据同步**：实时更新统计数据
3. **生命周期管理**：正确清理定时器和连接

## 配置文件修改

### Vite配置

移除了WebSocket代理配置，因为现在直接连接到后端：

```javascript
// 移除了这部分配置
'/ws': {
  target: 'ws://localhost:8443',
  ws: true,
  changeOrigin: true,
}
```

## 测试

运行测试脚本验证WebSocket连接：

```bash
cd web
node test_mobile_websocket.js
```

## 兼容性

- 与PC端使用相同的WebSocket协议
- 支持所有现有的消息类型
- 保持相同的数据格式和结构

## 优势

1. **统一协议**：移动端和PC端使用相同的WebSocket协议
2. **实时性**：更好的实时数据传输性能
3. **减少延迟**：直接连接，无需代理转发
4. **更好的错误处理**：统一的错误处理机制
5. **资源效率**：减少HTTP请求开销

## 注意事项

1. 确保后端WebSocket服务正在运行（端口8443）
2. 移动端需要在启动分析后建立WebSocket连接
3. 正确处理连接断开和重连逻辑
4. 及时清理全局对象和定时器 