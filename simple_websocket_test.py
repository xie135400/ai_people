#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的WebSocket测试脚本
"""

import asyncio
import websockets
import json
import sys

async def test_websocket():
    """测试WebSocket连接"""
    uri = "ws://localhost:8443/ws/test-user-123"
    
    try:
        print(f"尝试连接到: {uri}")
        async with websockets.connect(uri) as websocket:
            print("WebSocket连接成功!")
            
            # 发送测试消息
            test_message = {
                "type": "get_stats",
                "timestamp": "2024-01-01T00:00:00"
            }
            await websocket.send(json.dumps(test_message))
            print(f"发送消息: {test_message}")
            
            # 接收响应
            response = await websocket.recv()
            print(f"收到响应: {response}")
            
    except Exception as e:
        print(f"连接失败: {e}")
        print(f"错误类型: {type(e)}")
        import traceback
        traceback.print_exc()

async def test_with_session():
    """先创建会话再测试WebSocket"""
    import aiohttp
    
    try:
        # 创建会话
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:8443/api/create-session', 
                                   json={'username': 'test-user'}) as resp:
                result = await resp.json()
                print(f"会话创建结果: {result}")
                
                if result.get('status') == 'success':
                    user_id = result['user_id']
                    
                    # 测试WebSocket连接
                    uri = f"ws://localhost:8443/ws/{user_id}"
                    print(f"尝试连接到: {uri}")
                    
                    async with websockets.connect(uri) as websocket:
                        print("WebSocket连接成功!")
                        
                        # 接收欢迎消息
                        welcome = await websocket.recv()
                        print(f"收到欢迎消息: {welcome}")
                        
                        # 发送测试消息
                        test_message = {
                            "type": "get_stats",
                            "timestamp": "2024-01-01T00:00:00"
                        }
                        await websocket.send(json.dumps(test_message))
                        print(f"发送消息: {test_message}")
                        
                        # 接收响应
                        response = await websocket.recv()
                        print(f"收到响应: {response}")
                        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== 简单WebSocket测试 ===")
    asyncio.run(test_websocket())
    
    print("\n=== 带会话的WebSocket测试 ===")
    asyncio.run(test_with_session()) 