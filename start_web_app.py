#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用启动脚本
用于启动AI人流分析Web应用
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入web应用
from src.web_app import WebApp

def main():
    """主函数"""
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='AI人流分析Web应用')
    parser.add_argument('--host', type=str, default='localhost', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口号')
    parser.add_argument('--no-ssl', action='store_true', help='禁用SSL（使用HTTP而不是HTTPS）')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    print(f"启动AI人流分析Web应用...")
    print(f"主机: {args.host}")
    print(f"端口: {args.port}")
    print(f"SSL: {'禁用' if args.no_ssl else '启用'}")
    
    # 创建并运行Web应用
    web_app = WebApp()
    web_app.run(host=args.host, port=args.port, use_ssl=not args.no_ssl)

if __name__ == "__main__":
    main() 