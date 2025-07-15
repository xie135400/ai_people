#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTPS依赖安装脚本
安装运行HTTPS Web应用所需的依赖包
"""

import subprocess
import sys
import os

def run_command(cmd):
    """运行命令并显示输出"""
    print(f"🔧 执行: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False

def main():
    """主函数"""
    print("🔐 AI人流分析系统 - HTTPS依赖安装")
    print("=" * 50)
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"🐍 Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        return
    
    print("✅ Python版本符合要求")
    
    # 安装依赖包
    packages = [
        "cryptography",  # SSL证书生成
        "requests",      # HTTP请求（ngrok）
        "uvicorn[standard]",  # Web服务器
        "fastapi",       # Web框架
        "websockets",    # WebSocket支持
    ]
    
    print(f"\n📦 准备安装 {len(packages)} 个依赖包:")
    for pkg in packages:
        print(f"  - {pkg}")
    
    print("\n🚀 开始安装...")
    
    failed_packages = []
    
    for package in packages:
        print(f"\n📦 安装 {package}...")
        if run_command(f"{sys.executable} -m pip install {package}"):
            print(f"✅ {package} 安装成功")
        else:
            print(f"❌ {package} 安装失败")
            failed_packages.append(package)
    
    print("\n" + "=" * 50)
    
    if not failed_packages:
        print("🎉 所有依赖包安装成功！")
        print("\n📋 可用的启动脚本:")
        print("  🔐 自签名HTTPS: python test_web_https.py")
        print("  🌐 Ngrok HTTPS: python test_web_ngrok.py")
        print("  📱 标准版本: python test_web_app.py")
        
        print("\n🔧 验证安装:")
        print("  python -c \"import cryptography; print('cryptography OK')\"")
        print("  python -c \"import uvicorn; print('uvicorn OK')\"")
        print("  python -c \"import fastapi; print('fastapi OK')\"")
        
    else:
        print(f"❌ {len(failed_packages)} 个包安装失败:")
        for pkg in failed_packages:
            print(f"  - {pkg}")
        
        print("\n💡 解决建议:")
        print("  1. 升级pip: python -m pip install --upgrade pip")
        print("  2. 使用国内镜像:")
        print("     pip install -i https://pypi.tuna.tsinghua.edu.cn/simple cryptography")
        print("  3. 检查网络连接")
        print("  4. 手动安装失败的包")
    
    # 检查ngrok（可选）
    print("\n🌐 检查Ngrok（可选）:")
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ngrok已安装")
            print(f"   版本: {result.stdout.strip()}")
        else:
            print("❌ Ngrok未安装")
    except FileNotFoundError:
        print("❌ Ngrok未安装")
        print("   如需使用公网HTTPS，请安装ngrok:")
        print("   1. 访问 https://ngrok.com/download")
        print("   2. 下载并安装")
        print("   3. 注册账号获取authtoken")
        print("   4. 运行: ngrok authtoken YOUR_TOKEN")

if __name__ == "__main__":
    main() 