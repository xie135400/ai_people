import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: 'AI人流分析', keepAlive: true, requiresAuth: true }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('../views/Analysis.vue'),
    meta: { title: '实时分析', keepAlive: true, requiresAuth: true }
  },
  {
    path: '/records',
    name: 'Records',
    component: () => import('../views/Records.vue'),
    meta: { title: '分析记录', keepAlive: false, requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { title: '设置', keepAlive: false, requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录', keepAlive: false, requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // 检查是否需要登录
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  const isLoginPage = to.path === '/login'
  
  // 如果不是登录页面，检查登录状态
  if (!isLoginPage && requiresAuth) {
    console.log('路由守卫：检查页面', to.path, '是否需要登录')
    const savedUser = localStorage.getItem('user')
    
    if (!savedUser) {
      console.log('路由守卫：未找到用户缓存，跳转到登录页面')
      // 未登录，跳转到登录页面，并保存重定向路径
      next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
      return
    }
    
    try {
      const userData = JSON.parse(savedUser)
      console.log('路由守卫：找到用户缓存', userData)
      
      // 检查缓存是否过期（7天）
      const loginTime = new Date(userData.loginTime || userData.created_at || Date.now())
      const now = new Date()
      const daysSinceLogin = (now - loginTime) / (1000 * 60 * 60 * 24)
      
      console.log('路由守卫：登录时间检查', {
        loginTime: loginTime.toISOString(),
        daysSinceLogin: daysSinceLogin.toFixed(2)
      })
      
      if (daysSinceLogin > 7) {
        console.log('路由守卫：缓存已过期，清除并跳转到登录页面')
        // 缓存过期，清除并跳转到登录页面
        localStorage.removeItem('user')
        next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
        return
      }
      
      console.log('路由守卫：缓存有效，允许访问')
    } catch (error) {
      console.log('路由守卫：缓存数据异常，清除并跳转到登录页面', error)
      // 缓存数据异常，清除并跳转到登录页面
      localStorage.removeItem('user')
      next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
      return
    }
  }
  
  next()
})

export default router 