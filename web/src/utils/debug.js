/**
 * localStorage 调试工具
 */

// 原始的 localStorage 方法
const originalSetItem = localStorage.setItem;
const originalRemoveItem = localStorage.removeItem;
const originalClear = localStorage.clear;

// 重写 localStorage.setItem
localStorage.setItem = function(key, value) {
  console.log(`🔧 localStorage.setItem: ${key}`, value);
  console.trace('调用堆栈');
  return originalSetItem.apply(this, arguments);
};

// 重写 localStorage.removeItem
localStorage.removeItem = function(key) {
  console.log(`🗑️ localStorage.removeItem: ${key}`);
  console.trace('调用堆栈');
  return originalRemoveItem.apply(this, arguments);
};

// 重写 localStorage.clear
localStorage.clear = function() {
  console.log('🧹 localStorage.clear');
  console.trace('调用堆栈');
  return originalClear.apply(this, arguments);
};

// 监控特定键的变化
export function watchLocalStorageKey(key) {
  const checkInterval = 1000; // 每秒检查一次
  let lastValue = localStorage.getItem(key);
  
  const intervalId = setInterval(() => {
    const currentValue = localStorage.getItem(key);
    if (currentValue !== lastValue) {
      console.log(`📊 localStorage[${key}] 变化:`, {
        from: lastValue,
        to: currentValue,
        timestamp: new Date().toISOString()
      });
      lastValue = currentValue;
    }
  }, checkInterval);
  
  return () => clearInterval(intervalId);
}

// 打印当前 localStorage 状态
export function printLocalStorageState() {
  console.log('📋 当前 localStorage 状态:');
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    const value = localStorage.getItem(key);
    console.log(`  ${key}:`, value);
  }
}

// 监控所有 localStorage 操作
export function startLocalStorageMonitoring() {
  console.log('🔍 开始监控 localStorage 操作');
  
  // 监控 user 键的变化
  const stopWatching = watchLocalStorageKey('user');
  
  // 每5秒打印一次状态
  const statusInterval = setInterval(() => {
    const userInfo = localStorage.getItem('user');
    if (userInfo) {
      try {
        const userData = JSON.parse(userInfo);
        console.log('👤 用户状态:', {
          id: userData.id,
          username: userData.username,
          loginTime: userData.loginTime,
          lastActivity: userData.lastActivity
        });
      } catch (e) {
        console.log('👤 用户状态: 解析失败', userInfo);
      }
    } else {
      console.log('👤 用户状态: 无缓存');
    }
  }, 5000);
  
  return () => {
    stopWatching();
    clearInterval(statusInterval);
  };
}

export default {
  watchLocalStorageKey,
  printLocalStorageState,
  startLocalStorageMonitoring
}; 