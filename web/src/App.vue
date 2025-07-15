<template>
  <div id="app" class="app-container">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAnalyticsStore } from './stores/analytics'

const analyticsStore = useAnalyticsStore()

onMounted(() => {
  // 初始化应用
  console.log('AI人流分析系统 - 移动端启动')
})
</script>

<style scoped>
.app-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background-color: #f7f8fa;
}
</style> 