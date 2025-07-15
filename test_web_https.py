#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTPS Web应用测试脚本
启动AI人流分析系统的HTTPS Web界面
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

def open_browser(url: str, delay: int = 3):
    """延迟打开浏览器"""
    time.sleep(delay)
    try:
        webbrowser.open(url)
        logger.info(f"已在浏览器中打开: {url}")
    except Exception as e:
        logger.error(f"无法打开浏览器: {e}")

def main():
    """主函数"""
    print("🔐 启动AI人流分析系统HTTPS Web界面")
    print("=" * 60)
    
    # 创建Web应用
    web_app = WebApp(db_path="data/analytics.db")
    
    # 设置服务器参数
    host = "localhost"
    port = 8000
    use_ssl = True
    
    url = f"https://{host}:{port}"
    
    print(f"🌐 HTTPS地址: {url}")
    print(f"📊 数据库路径: data/analytics.db")
    print(f"🔐 SSL证书: 自动生成")
    print("=" * 60)
    
    print("\n🔐 HTTPS功能:")
    print("  ✅ 自动生成自签名SSL证书")
    print("  ✅ 支持浏览器摄像头权限")
    print("  ✅ 安全的WebSocket连接(WSS)")
    print("  ✅ 加密数据传输")
    print("  ✅ 多用户会话隔离")
    
    print("\n📋 使用步骤:")
    print("  1. 等待服务器启动完成")
    print("  2. 浏览器会自动打开页面")
    print("  3. 看到'不安全'警告是正常的")
    print("  4. 点击'高级'或'Advanced'")
    print("  5. 点击'继续访问localhost'")
    print("  6. 输入用户名开始使用")
    print("  7. 授权摄像头权限")
    print("  8. 开始AI人流分析")
    
    print("\n🔧 证书信息:")
    print("  📁 证书目录: certs/")
    print("  📜 证书文件: cert.pem")
    print("  🔑 私钥文件: key.pem")
    print("  ⏰ 有效期: 1年")
    print("  🏷️  主题: localhost")
    
    print("\n⚠️  浏览器警告处理:")
    print("  Chrome: 点击'高级' → '继续访问localhost(不安全)'")
    print("  Firefox: 点击'高级' → '接受风险并继续'")
    print("  Safari: 点击'显示详细信息' → '访问此网站'")
    print("  Edge: 点击'高级' → '继续到localhost(不安全)'")
    
    print("\n🚀 技术特性:")
    print("  🔐 TLS 1.2+ 加密")
    print("  🌐 WebSocket Secure (WSS)")
    print("  📱 响应式设计")
    print("  ⚡ 实时数据传输")
    print("  🛡️  用户会话安全")
    
    print("\n" + "=" * 60)
    
    # 延迟打开浏览器
    browser_thread = threading.Thread(target=open_browser, args=(url, 3))
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # 启动Web服务器
        print("🚀 正在启动HTTPS服务器...")
        web_app.run(host=host, port=port, use_ssl=use_ssl)
        
    except KeyboardInterrupt:
        print("\n\n🛑 用户中断，正在关闭服务器...")
        logger.info("HTTPS服务器已关闭")
        
    except Exception as e:
        logger.error(f"HTTPS服务器启动失败: {e}")
        print(f"\n❌ 启动失败: {e}")
        print("\n💡 解决建议:")
        print("  1. 安装cryptography库:")
        print("     pip install cryptography")
        print("  2. 检查端口8000是否被占用:")
        print("     netstat -an | grep 8000")
        print("  3. 确保有写入权限创建证书文件")
        print("  4. 检查防火墙设置")
        print("  5. 尝试使用不同端口:")
        print("     python test_web_https.py --port 8443")

if __name__ == "__main__":
    main() 