<template>
  <div class="settings-container">
    <!-- 顶部导航 -->
    <div class="settings-header">
      <van-nav-bar 
        title="设置" 
        left-arrow 
        @click-left="$router.back()" 
        class="settings-navbar"
      />
    </div>
    
    <div class="settings-content">
      <!-- 用户信息 -->
      <div class="user-card">
        <div class="user-info-wrapper">
          <div class="avatar-container">
            <van-image
              round
              width="80"
              height="80"
              fit="cover"
              :src="userInfo.avatar || 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'"
            />
            <div class="avatar-badge" @click="uploadAvatar">
              <van-icon name="photograph" />
            </div>
          </div>
          <div class="user-details">
            <h2 class="user-name">{{ userInfo.username }}</h2>
            <div class="user-role">
              <van-tag round type="primary" size="medium">{{ userInfo.role }}</van-tag>
            </div>
            <van-button 
              size="small" 
              type="primary" 
              plain 
              round 
              icon="edit" 
              class="edit-profile-btn"
              @click="editProfile"
            >
              编辑资料
            </van-button>
          </div>
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="quick-actions">
        <div class="action-item" @click="showLanguageOptions">
          <div class="action-icon language">
            <van-icon name="guide-o" />
          </div>
          <div class="action-text">语言</div>
        </div>
        <div class="action-item" @click="toggleDarkMode">
          <div class="action-icon theme" :class="{ 'active': darkMode }">
            <van-icon :name="darkMode ? 'moon-o' : 'sunny-o'" />
          </div>
          <div class="action-text">{{ darkMode ? '深色' : '浅色' }}</div>
        </div>
        <div class="action-item" @click="toggleNotifications">
          <div class="action-icon notification" :class="{ 'active': notifications.enabled }">
            <van-icon :name="notifications.enabled ? 'bell' : 'bell-o'" />
          </div>
          <div class="action-text">通知</div>
        </div>
        <div class="action-item" @click="showClearCacheConfirm">
          <div class="action-icon cache">
            <van-icon name="delete-o" />
          </div>
          <div class="action-text">清除缓存</div>
        </div>
      </div>

      <!-- 设置列表 -->
      <div class="settings-groups">
        <!-- 应用设置 -->
        <div class="settings-group">
          <div class="group-header">
            <van-icon name="apps-o" class="group-icon" />
            <span>应用设置</span>
          </div>
          
          <div class="settings-list">
            <div class="settings-item" @click="showLanguageOptions">
              <div class="item-content">
                <van-icon name="guide-o" class="item-icon" />
                <span class="item-title">语言</span>
              </div>
              <div class="item-action">
                <span class="item-value">{{ languageOptions[currentLanguage] }}</span>
                <van-icon name="arrow" />
              </div>
            </div>
            
            <div class="settings-item">
              <div class="item-content">
                <van-icon name="eye-o" class="item-icon" />
                <span class="item-title">深色模式</span>
              </div>
              <div class="item-action">
                <van-switch v-model="darkMode" size="24" @change="toggleDarkMode" />
              </div>
            </div>
            
            <div class="settings-item">
              <div class="item-content">
                <van-icon name="replay" class="item-icon" />
                <span class="item-title">数据自动刷新</span>
              </div>
              <div class="item-action">
                <van-switch v-model="autoRefresh" size="24" />
              </div>
            </div>
            
            <div class="settings-item" @click="showRefreshOptions">
              <div class="item-content">
                <van-icon name="clock-o" class="item-icon" />
                <span class="item-title">刷新间隔</span>
              </div>
              <div class="item-action">
                <span class="item-value">{{ refreshIntervalOptions[currentRefreshInterval] }}</span>
                <van-icon name="arrow" />
              </div>
            </div>
          </div>
        </div>
        
        <!-- 通知设置 -->
        <div class="settings-group">
          <div class="group-header">
            <van-icon name="bell" class="group-icon" />
            <span>通知设置</span>
          </div>
          
          <div class="settings-list">
            <div class="settings-item">
              <div class="item-content">
                <van-icon name="bell" class="item-icon" />
                <span class="item-title">接收通知</span>
              </div>
              <div class="item-action">
                <van-switch v-model="notifications.enabled" size="24" />
              </div>
            </div>
            
            <div class="settings-item" :class="{ 'disabled': !notifications.enabled }">
              <div class="item-content">
                <van-icon name="friends-o" class="item-icon" />
                <span class="item-title">人流量预警</span>
              </div>
              <div class="item-action">
                <van-switch v-model="notifications.peopleAlert" size="24" :disabled="!notifications.enabled" />
              </div>
            </div>
            
            <div class="settings-item" :class="{ 'disabled': !notifications.enabled }">
              <div class="item-content">
                <van-icon name="warning-o" class="item-icon" />
                <span class="item-title">行为异常提醒</span>
              </div>
              <div class="item-action">
                <van-switch v-model="notifications.behaviorAlert" size="24" :disabled="!notifications.enabled" />
              </div>
            </div>
            
            <div class="settings-item" :class="{ 'disabled': !notifications.enabled }">
              <div class="item-content">
                <van-icon name="info-o" class="item-icon" />
                <span class="item-title">系统状态通知</span>
              </div>
              <div class="item-action">
                <van-switch v-model="notifications.systemAlert" size="24" :disabled="!notifications.enabled" />
              </div>
            </div>
          </div>
        </div>
        
        <!-- 系统信息 -->
        <div class="settings-group">
          <div class="group-header">
            <van-icon name="cluster-o" class="group-icon" />
            <span>系统信息</span>
          </div>
          
          <div class="settings-list">
            <div class="settings-item">
              <div class="item-content">
                <van-icon name="label-o" class="item-icon" />
                <span class="item-title">版本号</span>
              </div>
              <div class="item-action">
                <span class="item-value highlight">v{{ appVersion }}</span>
              </div>
            </div>
            
            <div class="settings-item">
              <div class="item-content">
                <van-icon name="qr" class="item-icon" />
                <span class="item-title">设备ID</span>
              </div>
              <div class="item-action">
                <span class="item-value">{{ deviceId }}</span>
              </div>
            </div>
            
            <div class="settings-item">
              <div class="item-content">
                <van-icon name="chart-trending-o" class="item-icon" />
                <span class="item-title">存储空间</span>
              </div>
              <div class="item-action">
                <span class="item-value">{{ storageUsage }}</span>
              </div>
            </div>
            
            <div class="settings-item" @click="checkUpdate">
              <div class="item-content">
                <van-icon name="upgrade" class="item-icon" />
                <span class="item-title">检查更新</span>
              </div>
              <div class="item-action">
                <van-icon name="arrow" />
              </div>
            </div>
            
            <div class="settings-item" @click="showClearCacheConfirm">
              <div class="item-content">
                <van-icon name="delete-o" class="item-icon" />
                <span class="item-title">清除缓存</span>
              </div>
              <div class="item-action">
                <van-icon name="arrow" />
              </div>
            </div>
          </div>
        </div>
        
        <!-- 关于 -->
        <div class="settings-group">
          <div class="group-header">
            <van-icon name="info-o" class="group-icon" />
            <span>关于</span>
          </div>
          
          <div class="settings-list">
            <div class="settings-item" @click="showUserAgreement">
              <div class="item-content">
                <van-icon name="description" class="item-icon" />
                <span class="item-title">用户协议</span>
              </div>
              <div class="item-action">
                <van-icon name="arrow" />
              </div>
            </div>
            
            <div class="settings-item" @click="showPrivacyPolicy">
              <div class="item-content">
                <van-icon name="shield-o" class="item-icon" />
                <span class="item-title">隐私政策</span>
              </div>
              <div class="item-action">
                <van-icon name="arrow" />
              </div>
            </div>
            
            <div class="settings-item" @click="contactUs">
              <div class="item-content">
                <van-icon name="service-o" class="item-icon" />
                <span class="item-title">联系我们</span>
              </div>
              <div class="item-action">
                <van-icon name="arrow" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="logout-section">
        <van-button 
          block 
          type="danger" 
          class="logout-button"
          @click="showLogoutConfirm"
        >
          退出登录
        </van-button>
      </div>
    </div>

    <!-- 底部导航 -->
    <van-tabbar v-model="activeTab" @change="onTabChange" class="settings-tabbar">
      <van-tabbar-item icon="home-o" to="/">主页</van-tabbar-item>
      <van-tabbar-item icon="chart-trending-o" to="/analysis">分析</van-tabbar-item>
      <van-tabbar-item icon="records" to="/records">记录</van-tabbar-item>
      <van-tabbar-item icon="setting-o" to="/settings">设置</van-tabbar-item>
    </van-tabbar>

    <!-- 弹出层 -->
    <van-action-sheet
      v-model="showLanguage"
      :actions="languageActions"
      cancel-text="取消"
      close-on-click-action
      @select="selectLanguage"
    />
    
    <van-action-sheet
      v-model="showRefresh"
      :actions="refreshActions"
      cancel-text="取消"
      close-on-click-action
      @select="selectRefreshInterval"
    />
    
    <van-dialog
      v-model="showLogout"
      title="退出登录"
      show-cancel-button
      @confirm="logout"
    >
      <div class="dialog-content">
        确定要退出登录吗？
      </div>
    </van-dialog>
    
    <van-dialog
      v-model="showClearCache"
      title="清除缓存"
      show-cancel-button
      @confirm="clearCache"
    >
      <div class="dialog-content">
        确定要清除所有缓存数据吗？此操作不可恢复。
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import { useAnalyticsStore } from '../stores/analytics'

const router = useRouter()
const analyticsStore = useAnalyticsStore()
const activeTab = ref(3)

// 用户信息
const userInfo = reactive({
  username: '管理员',
  role: '系统管理员',
  avatar: ''
})

// 应用设置
const darkMode = ref(false)
const autoRefresh = ref(true)
const currentLanguage = ref('zh')
const currentRefreshInterval = ref('30s')

const languageOptions = {
  zh: '中文',
  en: 'English'
}

const refreshIntervalOptions = {
  '10s': '10秒',
  '30s': '30秒',
  '1m': '1分钟',
  '5m': '5分钟',
  'off': '关闭'
}

// 通知设置
const notifications = reactive({
  enabled: true,
  peopleAlert: true,
  behaviorAlert: true,
  systemAlert: false
})

// 系统信息
const appVersion = ref('1.0.0')
const deviceId = ref('AI-PEOPLE-' + Math.random().toString(36).substring(2, 10).toUpperCase())
const storageUsage = ref('23.5 MB / 1 GB')

// 弹出层控制
const showLanguage = ref(false)
const showRefresh = ref(false)
const showLogout = ref(false)
const showClearCache = ref(false)

// 语言选项
const languageActions = [
  { name: '中文', value: 'zh' },
  { name: 'English', value: 'en' }
]

// 刷新间隔选项
const refreshActions = [
  { name: '10秒', value: '10s' },
  { name: '30秒', value: '30s' },
  { name: '1分钟', value: '1m' },
  { name: '5分钟', value: '5m' },
  { name: '关闭', value: 'off' }
]

// 底部导航切换
const onTabChange = (index) => {
  const routes = ['/', '/analysis', '/records', '/settings']
  if (routes[index]) {
    router.push(routes[index])
  }
}

// 显示语言选项
const showLanguageOptions = () => {
  showLanguage.value = true
}

// 选择语言
const selectLanguage = (action) => {
  currentLanguage.value = action.value
  showToast(`已切换到${action.name}`)
}

// 显示刷新间隔选项
const showRefreshOptions = () => {
  showRefresh.value = true
}

// 选择刷新间隔
const selectRefreshInterval = (action) => {
  currentRefreshInterval.value = action.value
  showToast(`已设置刷新间隔为${action.name}`)
}

// 切换深色模式
const toggleDarkMode = (value) => {
  if (typeof value !== 'boolean') {
    darkMode.value = !darkMode.value
    value = darkMode.value
  }
  // 实际应用中这里会修改全局样式
  showToast(`${value ? '已开启' : '已关闭'}深色模式`)
}

// 切换通知
const toggleNotifications = () => {
  notifications.enabled = !notifications.enabled
  showToast(`${notifications.enabled ? '已开启' : '已关闭'}通知`)
}

// 上传头像
const uploadAvatar = () => {
  showToast('上传头像功能开发中...')
}

// 编辑资料
const editProfile = () => {
  showToast('编辑资料功能开发中...')
}

// 检查更新
const checkUpdate = () => {
  showToast('正在检查更新...')
  setTimeout(() => {
    showSuccessToast('当前已是最新版本')
  }, 1500)
}

// 显示退出登录确认
const showLogoutConfirm = () => {
  showLogout.value = true
}

// 退出登录
const logout = () => {
  // 调用store中的logout方法清除用户状态
  analyticsStore.logout()
  
  // 手动清除localStorage中的用户信息
  localStorage.removeItem('user')
  
  showSuccessToast('已退出登录')
  
  // 延迟跳转到登录页面
  setTimeout(() => {
    router.push('/login')
  }, 800)
}

// 显示清除缓存确认
const showClearCacheConfirm = () => {
  showClearCache.value = true
}

// 清除缓存
const clearCache = () => {
  showSuccessToast('缓存已清除')
}

// 显示用户协议
const showUserAgreement = () => {
  showToast('用户协议功能开发中...')
}

// 显示隐私政策
const showPrivacyPolicy = () => {
  showToast('隐私政策功能开发中...')
}

// 联系我们
const contactUs = () => {
  showToast('联系我们功能开发中...')
}
</script>

<style scoped>
.settings-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f7f8fa;
  color: #323233;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.settings-header {
  position: sticky;
  top: 0;
  z-index: 100;
}

.settings-navbar {
  background: linear-gradient(120deg, #3a7bd5, #00d2ff);
  box-shadow: 0 2px 12px rgba(58, 123, 213, 0.2);
}

.settings-navbar :deep(.van-nav-bar__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.settings-navbar :deep(.van-icon) {
  color: white;
  font-size: 20px;
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  padding-bottom: 70px;
}

/* 用户卡片 */
.user-card {
  background: linear-gradient(135deg, #3a7bd5, #00d2ff);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  color: white;
  box-shadow: 0 4px 20px rgba(58, 123, 213, 0.3);
  position: relative;
  overflow: hidden;
}

.user-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  z-index: 0;
}

.user-info-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
}

.avatar-container {
  position: relative;
  margin-right: 20px;
}

.avatar-badge {
  position: absolute;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  color: #3a7bd5;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.avatar-badge:hover {
  transform: scale(1.1);
}

.avatar-badge .van-icon {
  font-size: 16px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px;
  color: white;
}

.user-role {
  margin-bottom: 12px;
}

.edit-profile-btn {
  border-color: rgba(255, 255, 255, 0.8);
  color: white;
}

/* 快速操作 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.action-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.action-icon .van-icon {
  font-size: 24px;
  color: white;
}

.action-icon.language {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.action-icon.theme {
  background: linear-gradient(135deg, #5e72e4, #825ee4);
}

.action-icon.theme.active {
  background: linear-gradient(135deg, #11998e, #38ef7d);
}

.action-icon.notification {
  background: linear-gradient(135deg, #ff9a9e, #fad0c4);
}

.action-icon.notification.active {
  background: linear-gradient(135deg, #fa709a, #fee140);
}

.action-icon.cache {
  background: linear-gradient(135deg, #f5576c, #f093fb);
}

.action-text {
  font-size: 12px;
  color: #323233;
}

/* 设置组 */
.settings-groups {
  margin-bottom: 24px;
}

.settings-group {
  background: white;
  border-radius: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.group-header {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f5f5f5;
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.group-icon {
  font-size: 20px;
  margin-right: 8px;
  color: #3a7bd5;
}

.settings-list {
  padding: 8px 0;
}

.settings-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.settings-item:active {
  background-color: #f7f8fa;
}

.settings-item.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.item-content {
  display: flex;
  align-items: center;
}

.item-icon {
  font-size: 20px;
  margin-right: 12px;
  color: #3a7bd5;
}

.item-title {
  font-size: 15px;
  color: #323233;
}

.item-action {
  display: flex;
  align-items: center;
}

.item-value {
  font-size: 14px;
  color: #969799;
  margin-right: 8px;
}

.item-value.highlight {
  color: #3a7bd5;
  font-weight: 500;
}

/* 退出登录 */
.logout-section {
  padding: 16px 0;
  margin-bottom: 80px; /* 增加底部间距，避免被导航栏遮挡 */
}

.logout-button {
  border-radius: 12px;
  font-size: 16px;
  height: 48px;
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  border: none;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}

/* 底部导航 */
.settings-tabbar {
  box-shadow: 0 -1px 10px rgba(0, 0, 0, 0.05);
}

.settings-tabbar :deep(.van-tabbar-item--active) {
  color: #3a7bd5;
}

/* 弹窗内容 */
.dialog-content {
  padding: 24px 16px;
  text-align: center;
  color: #323233;
  font-size: 16px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .settings-content {
    padding: 12px;
  }
  
  .user-card {
    padding: 20px;
  }
  
  .user-name {
    font-size: 20px;
  }
  
  .quick-actions {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }
  
  .action-icon {
    width: 48px;
    height: 48px;
  }
}

@media (max-width: 480px) {
  .quick-actions {
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
  }
  
  .action-icon {
    width: 42px;
    height: 42px;
  }
  
  .action-icon .van-icon {
    font-size: 20px;
  }
  
  .action-text {
    font-size: 10px;
  }
}
</style> 