#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket连接调试脚本
"""

import requests
import json
import time

def test_websocket_debug():
    """调试WebSocket连接问题"""
    
    # 1. 测试基本HTTP连接
    print("=== 测试基本HTTP连接 ===")
    try:
        response = requests.get("http://localhost:8443/")
        print(f"HTTP连接成功: {response.status_code}")
    except Exception as e:
        print(f"HTTP连接失败: {e}")
        return
    
    # 2. 创建用户会话
    print("\n=== 创建用户会话 ===")
    try:
        response = requests.post("http://localhost:8443/api/create-session", 
                               json={"username": "debug-user"})
        result = response.json()
        print(f"会话创建结果: {result}")
        
        if result.get("status") != "success":
            print("会话创建失败")
            return
        
        user_id = result["user_id"]
        print(f"用户ID: {user_id}")
        
    except Exception as e:
        print(f"会话创建失败: {e}")
        return
    
    # 3. 测试WebSocket连接信息
    print("\n=== 测试WebSocket连接信息 ===")
    try:
        response = requests.get(f"http://localhost:8443/api/websocket-test/{user_id}")
        result = response.json()
        print(f"WebSocket测试结果: {result}")
        
        if not result.get("user_exists"):
            print("警告: 用户不存在")
        
    except Exception as e:
        print(f"WebSocket测试失败: {e}")
        return
    
    # 4. 测试分析器创建
    print("\n=== 测试分析器创建 ===")
    try:
        response = requests.post(f"http://localhost:8443/api/start/{user_id}")
        result = response.json()
        print(f"分析器启动结果: {result}")
        
    except Exception as e:
        print(f"分析器启动失败: {e}")
    
    # 5. 检查用户状态
    print("\n=== 检查用户状态 ===")
    try:
        response = requests.get(f"http://localhost:8443/api/status/{user_id}")
        result = response.json()
        print(f"用户状态: {result}")
        
    except Exception as e:
        print(f"获取用户状态失败: {e}")
    
    # 6. 获取实时统计
    print("\n=== 获取实时统计 ===")
    try:
        response = requests.get(f"http://localhost:8443/api/realtime-stats/{user_id}")
        result = response.json()
        print(f"实时统计: {result}")
        
    except Exception as e:
        print(f"获取实时统计失败: {e}")
    
    print(f"\n=== 调试完成 ===")
    print(f"用户ID: {user_id}")
    print(f"WebSocket URL: ws://localhost:8443/ws/{user_id}")
    print("可以在浏览器中使用这个用户ID测试WebSocket连接")

if __name__ == "__main__":
    test_websocket_debug() 