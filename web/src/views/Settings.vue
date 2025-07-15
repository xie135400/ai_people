<template>
  <div class="settings-container">
    <van-nav-bar title="设置" left-arrow @click-left="$router.back()" />
    
    <div class="settings-content">
      <div class="placeholder">
        <van-icon name="setting-o" size="60" />
        <h3>设置</h3>
        <p>设置功能正在开发中...</p>
      </div>
    </div>

    <van-tabbar v-model="activeTab">
      <van-tabbar-item icon="home-o" to="/">主页</van-tabbar-item>
      <van-tabbar-item icon="chart-trending-o" to="/analysis">分析</van-tabbar-item>
      <van-tabbar-item icon="records" to="/records">记录</van-tabbar-item>
      <van-tabbar-item icon="setting-o" to="/settings">设置</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref(3)
</script>

<style scoped>
.settings-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f7f8fa;
}

.settings-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder {
  text-align: center;
  color: #646566;
}

.placeholder h3 {
  margin: 16px 0 8px;
  color: #323233;
}
</style> 