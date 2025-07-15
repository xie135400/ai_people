#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI人流分析Web应用启动脚本
"""

import sys
import os
import argparse

# 确保src目录在Python路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, current_dir)

# 设置环境变量
os.environ['PYTHONPATH'] = f"{src_dir}:{current_dir}:{os.environ.get('PYTHONPATH', '')}"

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
    
    try:
        # 导入并运行Web应用
        from web_app import WebApp
        web_app = WebApp()
        web_app.run(host=args.host, port=args.port, use_ssl=not args.no_ssl)
        
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 