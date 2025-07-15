#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Vue3移动端应用
"""

import requests
import time
import json

def test_vue_app():
    """测试Vue3应用是否正常运行"""
    
    # 等待开发服务器启动
    print("等待Vue3开发服务器启动...")
    time.sleep(5)
    
    # 测试前端页面
    print("=== 测试前端页面 ===")
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        print(f"前端页面状态: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 前端页面正常访问")
            
            # 检查是否包含Vue应用内容
            content = response.text
            if 'AI人流分析系统' in content:
                print("✅ 页面内容正确")
            else:
                print("❌ 页面内容异常")
                
        else:
            print(f"❌ 前端页面访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 前端页面测试失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试API代理
    print("=== 测试API代理 ===")
    try:
        # 测试create-session API
        response = requests.post(
            "http://localhost:3000/api/create-session",
            json={"username": "Vue3测试用户"},
            timeout=10
        )
        
        print(f"API代理状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API代理正常工作")
            print(f"返回数据: {data}")
        else:
            print(f"❌ API代理失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ API代理测试失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试移动端适配
    print("=== 测试移动端适配 ===")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        }
        
        response = requests.get("http://localhost:3000", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ 移动端访问正常")
            
            # 检查viewport meta标签
            content = response.text
            if 'viewport' in content and 'width=device-width' in content:
                print("✅ 移动端适配正确")
            else:
                print("❌ 移动端适配可能有问题")
                
        else:
            print(f"❌ 移动端访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 移动端测试失败: {e}")

if __name__ == "__main__":
    print("开始测试Vue3移动端应用...")
    print("="*60)
    test_vue_app()
    print("测试完成!") 