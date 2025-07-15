#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试create-session接口的username参数
"""

import requests
import json

def test_create_session_with_username():
    """测试带用户名的会话创建"""
    url = "http://localhost:8443/api/create-session"
    
    # 测试1: 提供用户名
    test_username = "测试用户_张三"
    payload = {"username": test_username}
    
    print("=== 测试1: 提供用户名 ===")
    print(f"请求URL: {url}")
    print(f"请求数据: {payload}")
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        print(f"响应状态: {response.status_code}")
        print(f"响应数据: {data}")
        
        if data.get("status") == "success":
            returned_username = data.get("username")
            if returned_username == test_username:
                print("✅ 测试通过: 用户名正确使用")
            else:
                print(f"❌ 测试失败: 期望用户名 '{test_username}', 实际返回 '{returned_username}'")
        else:
            print("❌ 测试失败: 会话创建失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试2: 不提供用户名
    print("=== 测试2: 不提供用户名 ===")
    print(f"请求URL: {url}")
    print("请求数据: {}")
    
    try:
        response = requests.post(url, json={})
        data = response.json()
        
        print(f"响应状态: {response.status_code}")
        print(f"响应数据: {data}")
        
        if data.get("status") == "success":
            returned_username = data.get("username")
            if returned_username and returned_username.startswith("用户_"):
                print("✅ 测试通过: 自动生成用户名")
            else:
                print(f"❌ 测试失败: 期望自动生成用户名, 实际返回 '{returned_username}'")
        else:
            print("❌ 测试失败: 会话创建失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试3: 提供空用户名
    print("=== 测试3: 提供空用户名 ===")
    payload = {"username": ""}
    print(f"请求URL: {url}")
    print(f"请求数据: {payload}")
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        print(f"响应状态: {response.status_code}")
        print(f"响应数据: {data}")
        
        if data.get("status") == "success":
            returned_username = data.get("username")
            if returned_username and returned_username.startswith("用户_"):
                print("✅ 测试通过: 空用户名时自动生成")
            else:
                print(f"❌ 测试失败: 期望自动生成用户名, 实际返回 '{returned_username}'")
        else:
            print("❌ 测试失败: 会话创建失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("开始测试create-session接口的username参数处理...")
    print("="*60)
    test_create_session_with_username()
    print("测试完成!") 