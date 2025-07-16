/**
 * 日志管理工具
 */

const isDevelopment = process.env.NODE_ENV === 'development'

// 日志级别
const LOG_LEVELS = {
  ERROR: 0,
  WARN: 1,
  INFO: 2,
  DEBUG: 3
}

// 当前日志级别
const currentLogLevel = isDevelopment ? LOG_LEVELS.DEBUG : LOG_LEVELS.ERROR

// 日志颜色
const LOG_COLORS = {
  ERROR: '#ff4757',
  WARN: '#ffa502',
  INFO: '#3742fa',
  DEBUG: '#747d8c'
}

// 创建日志函数
const createLogger = (level, color) => {
  return (message, ...args) => {
    if (currentLogLevel >= level) {
      const timestamp = new Date().toISOString().substr(11, 8)
      const levelName = Object.keys(LOG_LEVELS)[level]
      
      if (isDevelopment) {
        console.log(
          `%c[${timestamp}] ${levelName}:`,
          `color: ${color}; font-weight: bold;`,
          message,
          ...args
        )
      } else if (level <= LOG_LEVELS.ERROR) {
        console.error(message, ...args)
      }
    }
  }
}

// 导出日志函数
export const logger = {
  error: createLogger(LOG_LEVELS.ERROR, LOG_COLORS.ERROR),
  warn: createLogger(LOG_LEVELS.WARN, LOG_COLORS.WARN),
  info: createLogger(LOG_LEVELS.INFO, LOG_COLORS.INFO),
  debug: createLogger(LOG_LEVELS.DEBUG, LOG_COLORS.DEBUG)
}

// 分类日志
export const wsLogger = {
  info: (message, ...args) => logger.info(`[WebSocket] ${message}`, ...args),
  error: (message, ...args) => logger.error(`[WebSocket] ${message}`, ...args),
  debug: (message, ...args) => logger.debug(`[WebSocket] ${message}`, ...args)
}

export const cameraLogger = {
  info: (message, ...args) => logger.info(`[Camera] ${message}`, ...args),
  error: (message, ...args) => logger.error(`[Camera] ${message}`, ...args),
  debug: (message, ...args) => logger.debug(`[Camera] ${message}`, ...args)
}

export const authLogger = {
  info: (message, ...args) => logger.info(`[Auth] ${message}`, ...args),
  error: (message, ...args) => logger.error(`[Auth] ${message}`, ...args),
  debug: (message, ...args) => logger.debug(`[Auth] ${message}`, ...args)
}

export const routerLogger = {
  info: (message, ...args) => logger.info(`[Router] ${message}`, ...args),
  error: (message, ...args) => logger.error(`[Router] ${message}`, ...args),
  debug: (message, ...args) => logger.debug(`[Router] ${message}`, ...args)
}

export default logger 