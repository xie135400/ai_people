<template>
  <div class="login-container">
    <!-- 顶部装饰 -->
    <div class="login-header">
      <div class="logo-container">
        <div class="logo">🤖</div>
        <h1 class="title">AI人流分析系统</h1>
        <p class="subtitle">智能分析 · 精准洞察</p>
      </div>
    </div>

    <!-- 登录表单 -->
    <div class="login-form">
      <van-form @submit="handleLogin">
        <van-cell-group inset>
          <van-field
            v-model="form.username"
            name="username"
            label="用户名"
            placeholder="请输入用户名（可选）"
            :rules="[{ required: false, message: '请输入用户名' }]"
            left-icon="contact"
            maxlength="20"
            show-word-limit
          />
        </van-cell-group>

        <div class="login-actions">
          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
            loading-text="登录中..."
            class="login-button"
          >
            开始分析
          </van-button>
        </div>
      </van-form>
    </div>

    <!-- 功能介绍 -->
    <div class="features">
      <van-grid :column-num="3" :border="false">
        <van-grid-item
          v-for="feature in features"
          :key="feature.title"
          :icon="feature.icon"
          :text="feature.title"
          class="feature-item"
        />
      </van-grid>
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
  { icon: 'eye-o', title: '实时监控' },
  { icon: 'chart-trending-o', title: '数据分析' },
  { icon: 'friends-o', title: '人流统计' },
  { icon: 'bar-chart-o', title: '年龄分布' },
  { icon: 'user-o', title: '性别识别' },
  { icon: 'clock-o', title: '行为分析' }
]

const handleLogin = async () => {
  try {
    loading.value = true
    
    console.log('登录页面：开始登录流程')
    
    // 创建会话
    console.log('登录页面：创建会话')
    await analyticsStore.createSession(form.username || null)
    
    // 检查localStorage
    const savedUser = localStorage.getItem('user')
    console.log('登录页面：创建会话后的用户信息', savedUser)
    
    // 自动启动分析（建立WebSocket连接）
    console.log('登录页面：启动分析')
    await analyticsStore.startAnalysis()
    
    // 再次检查localStorage
    const savedUserAfter = localStorage.getItem('user')
    console.log('登录页面：启动分析后的用户信息', savedUserAfter)
    
    showToast('登录成功！')
    
    // 获取重定向路径或默认跳转到主页
    const redirectPath = router.currentRoute.value.query.redirect || '/'
    console.log('登录页面：准备跳转到', redirectPath)
    router.push(redirectPath)
    
  } catch (error) {
    console.error('登录失败:', error)
    showFailToast(error.message || '登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.login-header {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 20px 40px;
  position: relative;
}

.login-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: float 6s ease-in-out infinite;
}

.logo-container {
  text-align: center;
  z-index: 1;
}

.logo {
  font-size: 80px;
  margin-bottom: 20px;
  animation: pulse 2s infinite;
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

.login-form {
  padding: 0 20px 20px;
}

.login-actions {
  margin-top: 24px;
}

.login-button {
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #1989fa 0%, #1976d2 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(25, 137, 250, 0.4);
}

.features {
  background: white;
  margin: 20px;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.feature-item {
  padding: 16px 8px;
}

.feature-item :deep(.van-grid-item__content) {
  background: transparent;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.feature-item :deep(.van-grid-item__content:active) {
  background: var(--active-color);
  transform: scale(0.95);
}

.feature-item :deep(.van-icon) {
  font-size: 24px;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.feature-item :deep(.van-grid-item__text) {
  font-size: 12px;
  color: var(--text-color-2);
  font-weight: 500;
}

.footer {
  text-align: center;
  padding: 20px;
  color: rgba(255, 255, 255, 0.6);
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
  50% { transform: translateY(-20px); }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* 移动端适配 */
@media (max-width: 480px) {
  .login-header {
    padding: 40px 20px 30px;
  }
  
  .logo {
    font-size: 60px;
  }
  
  .title {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .features {
    margin: 16px;
    padding: 16px;
  }
}
</style> 