<template>
  <div class="camera-capture">
    <!-- 摄像头预览区域 -->
    <div class="camera-preview" :class="{ 'preview-active': isCapturing }">
      <video
        ref="videoRef"
        :style="{ display: isCapturing ? 'block' : 'none' }"
        autoplay
        playsinline
        muted
        class="camera-video"
      />
      
      <!-- 摄像头未启动时的占位符 -->
      <div v-if="!isCapturing" class="camera-placeholder">
        <van-icon name="video-o" size="60" />
        <p>摄像头未启动</p>
        <p class="placeholder-desc">点击开始分析以启动摄像头</p>
      </div>
      
      <!-- 分析状态覆盖层 -->
      <div v-if="isCapturing" class="analysis-overlay">
        <div class="analysis-info">
          <van-tag type="success" size="small">实时分析中</van-tag>
          <span class="fps-counter">{{ fps }} FPS</span>
        </div>
        
        <!-- 人脸检测框 -->
        <div 
          v-for="(face, index) in detectedFaces" 
          :key="index"
          class="face-box"
          :style="getFaceBoxStyle(face)"
        >
          <div class="face-info">
            <span v-if="face.age">{{ Math.round(face.age) }}岁</span>
            <span v-if="face.gender">{{ face.gender === 'male' ? '男' : '女' }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 摄像头控制按钮 -->
    <div class="camera-controls">
      <van-button
        v-if="!isCapturing"
        type="primary"
        :loading="isStarting"
        @click="startCapture"
        round
        block
        size="large"
      >
        {{ isStarting ? '启动摄像头中...' : '启动摄像头' }}
      </van-button>
      
      <van-button
        v-else
        type="danger"
        :loading="isStopping"
        @click="stopCapture"
        round
        block
        size="large"
      >
        {{ isStopping ? '停止中...' : '停止摄像头' }}
      </van-button>
    </div>
    
    <!-- 摄像头设置 -->
    <div class="camera-settings" v-if="isCapturing">
      <van-cell-group inset>
        <van-cell title="前置摄像头" center>
          <template #right-icon>
            <van-switch v-model="useFrontCamera" @change="switchCamera" />
          </template>
        </van-cell>
        <van-cell title="分析频率" :value="getAnalysisFrequencyText()" @click="showAnalysisFrequencyPicker" is-link />
        <van-cell title="检测到的人脸" :value="detectedFaces.length + '个'" />
      </van-cell-group>
    </div>

    <!-- 分析频率选择器 -->
    <van-popup v-model="showFrequencyPicker" position="bottom">
      <van-picker
        :columns="frequencyOptions"
        @confirm="onFrequencyConfirm"
        @cancel="showFrequencyPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { showToast, showFailToast } from 'vant'
import { getConfigItem, setConfigItem } from '../utils/config'

const props = defineProps({
  userId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['frame-analyzed', 'faces-detected', 'error'])

// 响应式数据
const videoRef = ref(null)
const isCapturing = ref(false)
const isStarting = ref(false)
const isStopping = ref(false)
const useFrontCamera = ref(getConfigItem('useFrontCamera'))
const fps = ref(0)
const analysisInterval = ref(getConfigItem('analysisInterval')) // 从配置读取分析间隔
const detectedFaces = ref([])
const showFrequencyPicker = ref(false)

// 分析频率选项
const frequencyOptions = [
  { text: '0.5秒一次', value: 500 },
  { text: '1秒一次', value: 1000 },
  { text: '2秒一次', value: 2000 },
  { text: '3秒一次', value: 3000 },
  { text: '5秒一次', value: 5000 }
]

// 媒体流和分析相关
let mediaStream = null
let analysisTimer = null
let fpsCounter = 0
let lastFpsUpdate = Date.now()
let canvas = null
let ctx = null

// 页面加载时初始化
onMounted(() => {
  initializeCanvas()
  // 设置全局访问点，以便WebSocket服务可以调用
  window.cameraCapture = {
    handleFrameResult: handleFrameResult
  }
})

// 页面卸载时清理资源
onUnmounted(() => {
  cleanup()
  // 清理全局访问点
  if (window.cameraCapture) {
    delete window.cameraCapture
  }
})

// 初始化画布
const initializeCanvas = () => {
  canvas = document.createElement('canvas')
  ctx = canvas.getContext('2d')
}

// 启动摄像头
const startCapture = async () => {
  try {
    isStarting.value = true
    
    // 检查浏览器支持
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('您的浏览器不支持摄像头功能')
    }
    
    // 请求摄像头权限
    const constraints = {
      video: {
        facingMode: useFrontCamera.value ? 'user' : 'environment',
        width: { ideal: 640 },
        height: { ideal: 480 }
      },
      audio: false
    }
    
    mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
    
    // 等待下一帧确保video元素已渲染
    await nextTick()
    
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
      
      // 等待视频加载完成
      await new Promise((resolve) => {
        videoRef.value.onloadedmetadata = resolve
      })
      
      isCapturing.value = true
      startAnalysis()
      showToast('摄像头启动成功')
    }
    
  } catch (error) {
    console.error('启动摄像头失败:', error)
    let errorMessage = '启动摄像头失败'
    
    if (error.name === 'NotAllowedError') {
      errorMessage = '请允许访问摄像头权限'
    } else if (error.name === 'NotFoundError') {
      errorMessage = '未找到可用的摄像头'
    } else if (error.name === 'NotReadableError') {
      errorMessage = '摄像头被其他应用占用'
    }
    
    showFailToast(errorMessage)
    emit('error', error)
  } finally {
    isStarting.value = false
  }
}

// 停止摄像头
const stopCapture = async () => {
  try {
    isStopping.value = true
    cleanup()
    isCapturing.value = false
    detectedFaces.value = []
    fps.value = 0
    showToast('摄像头已停止')
  } catch (error) {
    console.error('停止摄像头失败:', error)
    showFailToast('停止摄像头失败')
  } finally {
    isStopping.value = false
  }
}

// 切换摄像头
const switchCamera = async () => {
  // 保存摄像头设置
  setConfigItem('useFrontCamera', useFrontCamera.value)
  
  if (isCapturing.value) {
    await stopCapture()
    // 等待一下再重新启动
    setTimeout(() => {
      startCapture()
    }, 500)
  }
}

// 开始分析
const startAnalysis = () => {
  if (!videoRef.value || !canvas || !ctx) return
  
  analysisTimer = setInterval(() => {
    captureAndAnalyze()
  }, analysisInterval.value)
}

// 捕获并分析帧
const captureAndAnalyze = async () => {
  if (!videoRef.value || !canvas || !ctx) return
  
  try {
    const video = videoRef.value
    const videoWidth = video.videoWidth
    const videoHeight = video.videoHeight
    
    if (videoWidth === 0 || videoHeight === 0) return
    
    // 设置画布尺寸
    canvas.width = videoWidth
    canvas.height = videoHeight
    
    // 绘制当前帧到画布
    ctx.drawImage(video, 0, 0, videoWidth, videoHeight)
    
    // 转换为blob
    canvas.toBlob(async (blob) => {
      if (blob) {
        await sendFrameToBackend(blob)
        updateFPS()
      }
    }, 'image/jpeg', 0.8)
    
  } catch (error) {
    console.error('捕获帧失败:', error)
  }
}

// 发送帧到后端分析（通过WebSocket）
const sendFrameToBackend = async (blob) => {
  try {
    // 将blob转换为base64
    const reader = new FileReader()
    reader.onload = function(e) {
      const base64Data = e.target.result
      
      // 通过WebSocket发送视频帧数据
      if (window.wsService && window.wsService.ws && window.wsService.ws.readyState === WebSocket.OPEN) {
        window.wsService.send({
          type: 'video_frame',
          frame: base64Data,
          user_id: props.userId,
          timestamp: Date.now()
        })
      } else {
        // 如果WebSocket未连接，等待一段时间后重试
        if (window.wsService && window.wsService.getReadyState() === 'CONNECTING') {
          // 只在开发环境打印连接状态
          if (process.env.NODE_ENV === 'development') {
            console.log('WebSocket正在连接中，等待连接完成...')
          }
          setTimeout(() => {
            sendFrameToBackend(blob)
          }, 500)
        } else {
          // 只在开发环境打印警告
          if (process.env.NODE_ENV === 'development') {
            console.warn('WebSocket未连接，无法发送帧数据，状态:', window.wsService ? window.wsService.getReadyState() : 'wsService不存在')
          }
          
          // 如果wsService不存在，尝试重新建立连接
          if (!window.wsService && props.userId) {
            // 延迟一段时间后重试
            setTimeout(() => {
              sendFrameToBackend(blob)
            }, 1000)
          }
        }
      }
    }
    reader.readAsDataURL(blob)
    
  } catch (error) {
    console.error('发送帧到后端失败:', error)
  }
}

// 更新FPS计数
const updateFPS = () => {
  fpsCounter++
  const now = Date.now()
  
  if (now - lastFpsUpdate >= 1000) {
    fps.value = fpsCounter
    fpsCounter = 0
    lastFpsUpdate = now
  }
}

// 处理来自WebSocket的帧分析结果
const handleFrameResult = (data) => {
  try {
    // 更新检测到的人脸
    if (data.faces && Array.isArray(data.faces)) {
      detectedFaces.value = data.faces
      emit('faces-detected', data.faces)
    }
    
    // 发送统计数据
    if (data.stats) {
      emit('frame-analyzed', data.stats)
    }
    
    // 只在开发环境打印详细信息
    if (process.env.NODE_ENV === 'development') {
      console.log('处理帧分析结果:', data)
    }
  } catch (error) {
    console.error('处理帧分析结果失败:', error)
  }
}

// 获取分析频率显示文本
const getAnalysisFrequencyText = () => {
  const option = frequencyOptions.find(opt => opt.value === analysisInterval.value)
  return option ? option.text : `${analysisInterval.value}ms`
}

// 显示分析频率选择器
const showAnalysisFrequencyPicker = () => {
  showFrequencyPicker.value = true
}

// 确认分析频率选择
const onFrequencyConfirm = (value) => {
  analysisInterval.value = value.value
  showFrequencyPicker.value = false
  
  // 保存到配置
  setConfigItem('analysisInterval', value.value)
  
  // 如果正在分析，重新启动分析以应用新的频率
  if (isCapturing.value) {
    // 停止当前分析
    if (analysisTimer) {
      clearInterval(analysisTimer)
      analysisTimer = null
    }
    // 重新开始分析
    startAnalysis()
  }
  
  showToast(`分析频率已设置为${value.text}`)
}

// 获取人脸框样式
const getFaceBoxStyle = (face) => {
  if (!face.box || !videoRef.value) return {}
  
  const video = videoRef.value
  const rect = video.getBoundingClientRect()
  const scaleX = rect.width / video.videoWidth
  const scaleY = rect.height / video.videoHeight
  
  return {
    left: `${face.box.x * scaleX}px`,
    top: `${face.box.y * scaleY}px`,
    width: `${face.box.width * scaleX}px`,
    height: `${face.box.height * scaleY}px`
  }
}

// 清理资源
const cleanup = () => {
  if (analysisTimer) {
    clearInterval(analysisTimer)
    analysisTimer = null
  }
  
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
  
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
}

// 暴露方法给父组件
defineExpose({
  startCapture,
  stopCapture,
  isCapturing
})
</script>

<style scoped>
.camera-capture {
  width: 100%;
}

.camera-preview {
  position: relative;
  width: 100%;
  height: 300px;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
}

.camera-preview.preview-active {
  background: transparent;
}

.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #646566;
}

.camera-placeholder p {
  margin: 8px 0;
  font-size: 16px;
}

.placeholder-desc {
  font-size: 12px !important;
  color: #969799;
}

.analysis-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.analysis-info {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.7);
  padding: 8px 12px;
  border-radius: 16px;
  color: white;
  font-size: 12px;
}

.fps-counter {
  font-weight: 500;
}

.face-box {
  position: absolute;
  border: 2px solid #07c160;
  border-radius: 4px;
  pointer-events: none;
}

.face-info {
  position: absolute;
  top: -24px;
  left: 0;
  background: rgba(7, 193, 96, 0.9);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  white-space: nowrap;
}

.face-info span {
  margin-right: 4px;
}

.face-info span:last-child {
  margin-right: 0;
}

.camera-controls {
  margin-bottom: 16px;
}

.camera-settings {
  /* 设置样式 */
}

/* 移动端适配 */
@media (max-width: 480px) {
  .camera-preview {
    height: 250px;
  }
  
  .analysis-info {
    top: 8px;
    right: 8px;
    padding: 6px 8px;
    font-size: 10px;
  }
  
  .face-info {
    font-size: 9px;
    padding: 1px 6px;
  }
}
</style> 