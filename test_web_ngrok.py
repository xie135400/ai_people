#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ngrok HTTPS Web应用测试脚本
使用ngrok创建HTTPS隧道，支持公网访问
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import logging
import webbrowser
import time
import threading
import subprocess
import json
import requests
from src.web_app import WebApp

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ngrok():
    """检查ngrok是否安装"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Ngrok已安装: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def start_ngrok(port: int):
    """启动ngrok隧道"""
    try:
        # 启动ngrok
        cmd = ['ngrok', 'http', str(port), '--log=stdout']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 等待ngrok启动
        time.sleep(3)
        
        # 获取ngrok URL
        try:
            response = requests.get('http://localhost:4040/api/tunnels')
            tunnels = response.json()
            
            for tunnel in tunnels['tunnels']:
                if tunnel['proto'] == 'https':
                    return tunnel['public_url'], process
            
            logger.error("未找到HTTPS隧道")
            return None, process
            
        except Exception as e:
            logger.error(f"获取ngrok URL失败: {e}")
            return None, process
            
    except Exception as e:
        logger.error(f"启动ngrok失败: {e}")
        return None, None

def open_browser(url: str, delay: int = 5):
    """延迟打开浏览器"""
    time.sleep(delay)
    try:
        webbrowser.open(url)
        logger.info(f"已在浏览器中打开: {url}")
    except Exception as e:
        logger.error(f"无法打开浏览器: {e}")

def main():
    """主函数"""
    print("🌐 启动AI人流分析系统 - Ngrok HTTPS版本")
    print("=" * 60)
    
    # 检查ngrok
    if not check_ngrok():
        print("❌ 未检测到ngrok，请先安装:")
        print("   1. 访问 https://ngrok.com/download")
        print("   2. 下载并安装ngrok")
        print("   3. 注册账号并获取authtoken")
        print("   4. 运行: ngrok authtoken YOUR_TOKEN")
        print("   5. 重新运行此脚本")
        return
    
    # 创建Web应用
    web_app = WebApp(db_path="data/analytics.db")
    
    # 设置服务器参数
    host = "localhost"
    port = 8000
    use_ssl = False  # ngrok提供HTTPS，本地使用HTTP
    
    print(f"🖥️  本地地址: http://{host}:{port}")
    print(f"📊 数据库路径: data/analytics.db")
    print(f"🌐 Ngrok隧道: 启动中...")
    print("=" * 60)
    
    print("\n🌟 Ngrok HTTPS功能:")
    print("  ✅ 真实的HTTPS证书")
    print("  ✅ 公网访问支持")
    print("  ✅ 无需处理证书警告")
    print("  ✅ 支持移动设备访问")
    print("  ✅ 自动WebSocket升级")
    
    print("\n🚀 启动ngrok隧道...")
    
    # 启动ngrok
    ngrok_url, ngrok_process = start_ngrok(port)
    
    if not ngrok_url:
        print("❌ Ngrok启动失败")
        return
    
    print(f"✅ Ngrok隧道已建立: {ngrok_url}")
    print(f"🔐 HTTPS地址: {ngrok_url}")
    
    print("\n📋 使用说明:")
    print("  1. 等待Web服务器启动")
    print("  2. 浏览器会自动打开ngrok URL")
    print("  3. 无需处理证书警告（真实HTTPS）")
    print("  4. 可以分享URL给其他人使用")
    print("  5. 支持手机等移动设备访问")
    print("  6. 输入用户名开始使用")
    print("  7. 授权摄像头权限")
    print("  8. 开始AI人流分析")
    
    print("\n🔧 技术信息:")
    print(f"  🌐 公网URL: {ngrok_url}")
    print(f"  🖥️  本地URL: http://{host}:{port}")
    print(f"  📊 Ngrok控制台: http://localhost:4040")
    print(f"  🔐 SSL终端: Ngrok服务器")
    print(f"  📱 移动设备: 支持")
    
    print("\n⚠️  注意事项:")
    print("  🔒 免费版ngrok会话有时间限制")
    print("  🌐 URL每次重启都会变化")
    print("  📊 可在 http://localhost:4040 查看流量")
    print("  🛡️  不要分享敏感数据的URL")
    
    print("\n" + "=" * 60)
    
    # 延迟打开浏览器
    browser_thread = threading.Thread(target=open_browser, args=(ngrok_url, 5))
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # 启动Web服务器
        print("🚀 正在启动Web服务器...")
        web_app.run(host=host, port=port, use_ssl=use_ssl)
        
    except KeyboardInterrupt:
        print("\n\n🛑 用户中断，正在关闭服务器...")
        if ngrok_process:
            ngrok_process.terminate()
        logger.info("Web服务器和Ngrok隧道已关闭")
        
    except Exception as e:
        logger.error(f"Web服务器启动失败: {e}")
        print(f"\n❌ 启动失败: {e}")
        if ngrok_process:
            ngrok_process.terminate()
        
        print("\n💡 解决建议:")
        print("  1. 检查端口8000是否被占用")
        print("  2. 确保ngrok authtoken已配置")
        print("  3. 检查网络连接")
        print("  4. 查看ngrok控制台: http://localhost:4040")
        print("  5. 重启ngrok服务")

if __name__ == "__main__":
    main() 