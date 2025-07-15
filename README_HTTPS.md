# AI人流分析系统 - HTTPS支持

## 🔐 HTTPS功能概述

本系统现已支持HTTPS访问，提供安全的Web界面和摄像头权限支持。

## 📋 支持的HTTPS方案

### 方案1：自签名证书（推荐用于开发）
- ✅ 自动生成SSL证书
- ✅ 本地localhost访问
- ✅ 支持摄像头权限
- ⚠️ 浏览器会显示"不安全"警告

### 方案2：Ngrok隧道（推荐用于演示）
- ✅ 真实HTTPS证书
- ✅ 公网访问支持
- ✅ 无证书警告
- ✅ 支持移动设备
- ⚠️ 需要安装ngrok

## 🚀 快速开始

### 1. 安装依赖
```bash
# 安装HTTPS相关依赖
python install_https_deps.py

# 或手动安装
pip install cryptography uvicorn[standard] fastapi websockets requests
```

### 2. 启动HTTPS服务

#### 方案1：自签名证书
```bash
python test_web_https.py
```
- 访问: https://localhost:8000
- 点击"高级" → "继续访问localhost"

#### 方案2：Ngrok隧道
```bash
# 先安装并配置ngrok
# 1. 下载: https://ngrok.com/download
# 2. 注册账号获取token
# 3. 配置: ngrok authtoken YOUR_TOKEN

python test_web_ngrok.py
```
- 自动获取公网HTTPS地址
- 无需处理证书警告

#### 方案3：标准版本（已升级支持HTTPS）
```bash
python test_web_app.py
```
- 默认启用HTTPS模式
- 自动生成自签名证书

## 🔧 技术细节

### SSL证书管理
- **证书目录**: `certs/`
- **证书文件**: `cert.pem`
- **私钥文件**: `key.pem`
- **有效期**: 1年
- **自动生成**: 首次启动时自动创建

### 浏览器兼容性
| 浏览器 | 自签名证书处理 |
|--------|----------------|
| Chrome | 点击"高级" → "继续访问localhost(不安全)" |
| Firefox | 点击"高级" → "接受风险并继续" |
| Safari | 点击"显示详细信息" → "访问此网站" |
| Edge | 点击"高级" → "继续到localhost(不安全)" |

### WebSocket安全连接
- HTTP模式: `ws://`
- HTTPS模式: `wss://`
- 自动协议检测和升级

## 📱 移动设备支持

### 使用Ngrok访问
```bash
python test_web_ngrok.py
```
- 获得类似 `https://abc123.ngrok.io` 的地址
- 可在手机浏览器中直接访问
- 支持摄像头权限（需要HTTPS）

### 局域网访问（需要真实证书）
如需在局域网内其他设备访问，需要：
1. 配置真实域名和证书
2. 或使用ngrok等隧道服务

## 🛡️ 安全注意事项

### 自签名证书
- ⚠️ 仅用于开发和测试
- ⚠️ 浏览器会显示警告
- ✅ 数据传输仍然加密
- ✅ 支持摄像头权限

### Ngrok隧道
- ✅ 真实SSL证书
- ⚠️ 免费版有会话限制
- ⚠️ URL每次重启会变化
- ⚠️ 不要分享包含敏感数据的URL

### 生产环境
- 🔒 使用真实SSL证书
- 🔒 配置防火墙规则
- 🔒 启用访问日志
- 🔒 定期更新证书

## 🔍 故障排除

### 证书生成失败
```bash
# 检查cryptography库
python -c "import cryptography; print('OK')"

# 重新安装
pip install --upgrade cryptography
```

### 端口被占用
```bash
# 检查端口占用
netstat -an | grep 8000

# 使用其他端口
python test_web_https.py --port 8443
```

### 摄像头权限问题
1. 确保使用HTTPS访问
2. 检查浏览器权限设置
3. 尝试刷新页面重新授权
4. 检查是否有其他应用占用摄像头

### Ngrok问题
```bash
# 检查ngrok状态
ngrok version

# 查看隧道信息
curl http://localhost:4040/api/tunnels

# 重新配置token
ngrok authtoken YOUR_TOKEN
```

## 📊 性能优化

### HTTPS性能
- SSL握手开销较小
- 现代浏览器优化良好
- 建议使用HTTP/2（uvicorn支持）

### 证书缓存
- 浏览器会缓存证书
- 首次访问较慢，后续访问快速
- 证书更新后需要清除浏览器缓存

## 🆕 更新日志

### v1.1.0 - HTTPS支持
- ✅ 添加自签名SSL证书生成
- ✅ 支持HTTPS/WSS协议
- ✅ 集成Ngrok隧道支持
- ✅ 自动协议检测
- ✅ 移动设备兼容性
- ✅ 详细的浏览器警告处理说明

## 📞 技术支持

如遇到HTTPS相关问题，请检查：
1. Python版本 >= 3.7
2. 依赖包是否正确安装
3. 防火墙和网络设置
4. 浏览器版本和设置
5. 证书文件权限

---

🔐 **安全提醒**: 在生产环境中，请使用由受信任CA签发的SSL证书，而不是自签名证书。 