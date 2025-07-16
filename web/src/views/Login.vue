<template>
  <div class="login-container">
    <!-- 顶部装饰 -->
    <div class="login-header">
      <div class="logo-container">
        <div class="logo">
          <van-icon name="cluster-o" class="logo-icon" />
        </div>
        <h1 class="title">AI人流分析系统</h1>
        <p class="subtitle">智能分析 · 精准洞察 · 数据驱动</p>
      </div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="card-header">
        <h2>欢迎使用</h2>
        <p>输入用户名开始您的分析之旅</p>
      </div>
      
      <van-form @submit="handleLogin" class="login-form">
        <van-field
          v-model="form.username"
          name="username"
          placeholder="请输入用户名（可选）"
          :rules="[{ required: false, message: '请输入用户名' }]"
          class="username-field"
        >
          <template #left-icon>
            <van-icon name="contact" class="field-icon" />
          </template>
        </van-field>

        <div class="login-actions">
          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
            loading-text="登录中..."
            class="login-button"
            size="large"
          >
            <van-icon name="play-circle-o" class="button-icon" />
            开始分析
          </van-button>
        </div>
      </van-form>
    </div>

    <!-- 功能介绍 -->
    <div class="features-section">
      <h3 class="features-title">核心功能</h3>
      <div class="features-grid">
        <div 
          v-for="feature in features" 
          :key="feature.title" 
          class="feature-item"
        >
          <div class="feature-icon-wrapper" :class="`feature-${feature.color}`">
            <van-icon :name="feature.icon" class="feature-icon" />
          </div>
          <div class="feature-text">
            <div class="feature-title">{{ feature.title }}</div>
            <div class="feature-desc">{{ feature.desc }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 版权信息 -->
    <div class="footer">
      <p class="copyright">© 2024 AI人流分析系统</p>
      <p class="version">v1.0.0</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalyticsStore } from '../stores/analytics'
import { showToast, showFailToast } from 'vant'
import { authLogger } from '../utils/logger'

const router = useRouter()
const analyticsStore = useAnalyticsStore()

const loading = ref(false)
const form = reactive({
  username: ''
})

// 检查是否已有缓存的用户信息
onMounted(() => {
  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    try {
      const userData = JSON.parse(savedUser)
      // 如果有缓存的用户名，填充到表单中
      if (userData.username) {
        form.username = userData.username
      }
    } catch (error) {
      console.error('读取缓存用户信息失败:', error)
    }
  }
})

const features = [
  { 
    icon: 'eye-o', 
    title: '实时监控', 
    desc: '实时捕捉场景中的人流变化',
    color: 'blue'
  },
  { 
    icon: 'chart-trending-o', 
    title: '数据分析', 
    desc: '深度分析人流数据和趋势',
    color: 'purple'
  },
  { 
    icon: 'friends-o', 
    title: '人流统计', 
    desc: '精确统计区域内的人数变化',
    color: 'green'
  },
  { 
    icon: 'bar-chart-o', 
    title: '年龄分布', 
    desc: '分析客群的年龄层次结构',
    color: 'orange'
  },
  { 
    icon: 'user-o', 
    title: '性别识别', 
    desc: '识别并统计不同性别比例',
    color: 'red'
  },
  { 
    icon: 'clock-o', 
    title: '行为分析', 
    desc: '分析停留时间和互动模式',
    color: 'teal'
  }
]

const handleLogin = async () => {
  try {
    loading.value = true
    
    authLogger.info('开始登录流程')
    
    // 创建会话
    authLogger.debug('创建会话')
    await analyticsStore.createSession(form.username || null)
    
    // 自动启动分析（建立WebSocket连接）
    authLogger.debug('启动分析')
    await analyticsStore.startAnalysis()
    
    showToast('登录成功！')
    
    // 获取重定向路径或默认跳转到主页
    const redirectPath = router.currentRoute.value.query.redirect || '/'
    authLogger.info('准备跳转到', redirectPath)
    router.push(redirectPath)
    
  } catch (error) {
    authLogger.error('登录失败:', error)
    showFailToast(error.message || '登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #4b79cf 0%, #7e57c2 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E"),
    linear-gradient(135deg, #4b79cf 0%, #7e57c2 100%);
  z-index: 0;
}

.login-header {
  padding: 50px 20px 20px;
  position: relative;
  z-index: 1;
}

.logo-container {
  text-align: center;
}

.logo {
  width: 90px;
  height: 90px;
  margin: 0 auto 20px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.18);
  animation: float 6s ease-in-out infinite;
}

.logo-icon {
  font-size: 50px;
  color: white;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0;
}

.login-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  margin: 10px 20px 30px;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.18);
  z-index: 1;
  animation: fadeIn 1s ease-out;
}

.card-header {
  text-align: center;
  margin-bottom: 24px;
}

.card-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px;
}

.card-header p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.login-form {
  margin-bottom: 20px;
}

.username-field {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.username-field :deep(.van-field__left-icon) {
  margin-right: 10px;
}

.field-icon {
  font-size: 20px;
  color: #7e57c2;
}

.login-actions {
  margin-top: 24px;
}

.login-button {
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #4b79cf 0%, #7e57c2 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(126, 87, 194, 0.4);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-button:active {
  transform: translateY(2px);
  box-shadow: 0 2px 8px rgba(126, 87, 194, 0.4);
}

.button-icon {
  font-size: 18px;
  margin-right: 8px;
  vertical-align: middle;
}

.features-section {
  background: white;
  margin: 0 20px 30px;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  z-index: 1;
  position: relative;
  animation: slideUp 1s ease-out;
}

.features-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 20px;
  text-align: center;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.05);
}

.feature-icon-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.feature-blue {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.feature-purple {
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
}

.feature-green {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.feature-orange {
  background: linear-gradient(135deg, #fad961 0%, #f76b1c 100%);
}

.feature-red {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
}

.feature-teal {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.feature-icon {
  font-size: 24px;
  color: white;
}

.feature-text {
  flex: 1;
}

.feature-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.feature-desc {
  font-size: 12px;
  color: #666;
}

.footer {
  text-align: center;
  padding: 20px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: auto;
  z-index: 1;
  position: relative;
}

.copyright {
  font-size: 14px;
  margin-bottom: 4px;
}

.version {
  font-size: 12px;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 移动端适配 */
@media (max-width: 480px) {
  .login-header {
    padding: 40px 20px 20px;
  }
  
  .logo {
    width: 80px;
    height: 80px;
  }
  
  .logo-icon {
    font-size: 40px;
  }
  
  .title {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .login-card {
    padding: 20px;
    margin: 10px 15px 20px;
  }
  
  .card-header h2 {
    font-size: 20px;
  }
  
  .features-section {
    padding: 20px;
    margin: 0 15px 20px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-item {
    padding: 10px;
  }
  
  .feature-icon-wrapper {
    width: 40px;
    height: 40px;
  }
  
  .feature-icon {
    font-size: 20px;
  }
}
</style> 