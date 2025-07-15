/**
 * 应用配置管理
 */

// 默认配置
const DEFAULT_CONFIG = {
  analysisInterval: 1000, // 分析频率（毫秒）
  useFrontCamera: true,   // 使用前置摄像头
  autoLogin: true,        // 自动登录
  sessionTimeout: 30000   // 会话检查间隔（毫秒）
}

// 配置键名
const CONFIG_KEY = 'ai_people_config'

/**
 * 获取配置
 */
export function getConfig() {
  try {
    const saved = localStorage.getItem(CONFIG_KEY)
    if (saved) {
      return { ...DEFAULT_CONFIG, ...JSON.parse(saved) }
    }
  } catch (error) {
    console.error('获取配置失败:', error)
  }
  return DEFAULT_CONFIG
}

/**
 * 保存配置
 */
export function saveConfig(config) {
  try {
    const merged = { ...getConfig(), ...config }
    localStorage.setItem(CONFIG_KEY, JSON.stringify(merged))
    return merged
  } catch (error) {
    console.error('保存配置失败:', error)
    return getConfig()
  }
}

/**
 * 获取单个配置项
 */
export function getConfigItem(key) {
  return getConfig()[key]
}

/**
 * 设置单个配置项
 */
export function setConfigItem(key, value) {
  const config = getConfig()
  config[key] = value
  return saveConfig(config)
}

/**
 * 重置配置
 */
export function resetConfig() {
  localStorage.removeItem(CONFIG_KEY)
  return DEFAULT_CONFIG
}

export default {
  getConfig,
  saveConfig,
  getConfigItem,
  setConfigItem,
  resetConfig,
  DEFAULT_CONFIG
} 