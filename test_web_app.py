#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用测试脚本
启动AI人流分析系统的Web界面（浏览器摄像头版本）
支持多用户同时使用
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import logging
import webbrowser
import time
import threading
from src.web_app import WebApp

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def open_browser(url: str, delay: int = 2):
    """延迟打开浏览器"""
    time.sleep(delay)
    try:
        webbrowser.open(url)
        logger.info(f"已在浏览器中打开: {url}")
    except Exception as e:
        logger.error(f"无法打开浏览器: {e}")

def main():
    """主函数"""
    print("🚀 启动AI人流分析系统Web界面（HTTPS版本）")
    print("=" * 60)
    
    # 创建Web应用
    web_app = WebApp(db_path="data/analytics.db")
    
    # 设置服务器参数
    host = "0.0.0.0"  # 使用localhost以支持摄像头权限
    port = 8000
    use_ssl = True  # 启用HTTPS
    
    protocol = "https" if use_ssl else "http"
    url = f"{protocol}://{host}:{port}"
    
    print(f"📡 服务器地址: {url}")
    print(f"📊 数据库路径: data/analytics.db")
    print(f"🔐 HTTPS模式: {'启用' if use_ssl else '禁用'}")
    print("=" * 60)
    
    print("\n🌟 功能特性:")
    print("  🔐 HTTPS安全连接")
    print("  ✅ 浏览器摄像头支持")
    print("  ✅ 多用户同时使用")
    print("  ✅ 用户会话管理")
    print("  ✅ 实时视频流显示")
    print("  ✅ 人员检测与跟踪")
    print("  ✅ 年龄性别识别")
    print("  ✅ 行为分析（购物者/浏览者）")
    print("  ✅ 实时统计数字显示")
    print("  ✅ 性别分布数字显示")
    print("  🎂 年龄分布数字显示")
    print("  ✅ WebSocket实时更新")
    print("  ✅ 自动会话清理")
    
    print("\n🎯 使用说明:")
    print("  1. 在浏览器中打开页面")
    print("  2. 如果使用自签名证书，点击'高级'→'继续访问'")
    print("  3. 输入用户名（可选）并点击'开始使用'")
    print("  4. 授权摄像头权限")
    print("  5. 点击'开始分析'启动AI检测")
    print("  6. 实时查看人流统计和行为分析")
    print("  7. 查看年龄分布和性别分布数字")
    print("  8. 点击'退出登录'结束会话")
    print("  9. 按Ctrl+C停止服务器")
    
    print("\n🔐 HTTPS证书说明:")
    print("  📜 自动生成自签名SSL证书")
    print("  📁 证书保存在 certs/ 目录")
    print("  ⚠️  浏览器会显示'不安全'警告，这是正常的")
    print("  ✅ 点击'高级'→'继续访问localhost'即可")
    print("  🔄 证书有效期1年，到期自动重新生成")
    
    print("\n👥 多用户支持:")
    print("  🔄 每个用户独立会话")
    print("  📱 支持多个浏览器同时使用")
    print("  🎥 每个用户使用自己的摄像头")
    print("  📊 独立的统计数据")
    print("  🧹 自动清理无活动会话（30分钟）")
    
    print("\n📊 年龄分布功能:")
    print("  🎂 7个年龄段：0-17, 18-25, 26-35, 36-45, 46-55, 56-65, 65+")
    print("  📈 实时更新数字显示")
    print("  🎨 彩色编码显示")
    print("  📱 响应式设计")
    
    print("\n🔧 技术特性:")
    print("  🔐 HTTPS/SSL加密连接")
    print("  🌐 基于WebRTC的浏览器摄像头")
    print("  🔌 WebSocket实时通信")
    print("  🎯 Base64图像传输")
    print("  ⚡ 5 FPS实时处理")
    print("  🛡️ 用户会话隔离")
    print("  📝 详细调试信息")
    
    print("\n" + "=" * 60)
    
    # 延迟打开浏览器
    browser_thread = threading.Thread(target=open_browser, args=(url, 3))
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # 启动Web服务器
        logger.info("启动Web服务器...")
        web_app.run(host=host, port=port, use_ssl=use_ssl)
        
    except KeyboardInterrupt:
        print("\n\n🛑 用户中断，正在关闭服务器...")
        logger.info("Web服务器已关闭")
        
    except Exception as e:
        logger.error(f"Web服务器启动失败: {e}")
        print(f"\n❌ 启动失败: {e}")
        print("\n💡 解决建议:")
        print("  1. 检查端口8000是否被占用")
        print("  2. 确保已安装所有依赖包")
        print("  3. 安装cryptography库: pip install cryptography")
        print("  4. 检查浏览器是否支持WebRTC")
        print("  5. 确保浏览器允许摄像头权限")
        print("  6. 查看日志获取详细错误信息")

if __name__ == "__main__":
    main() 