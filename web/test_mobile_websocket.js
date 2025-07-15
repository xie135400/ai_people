#!/usr/bin/env node

/**
 * 测试移动端WebSocket连接
 */

const WebSocket = require('ws');
const axios = require('axios');

async function testMobileWebSocket() {
  console.log('=== 测试移动端WebSocket连接 ===');
  
  try {
    // 1. 创建会话
    console.log('1. 创建用户会话...');
    const sessionResponse = await axios.post('http://localhost:8443/api/create-session', {
      username: 'mobile-test-user'
    });
    
    if (sessionResponse.data.status !== 'success') {
      throw new Error('创建会话失败');
    }
    
    const userId = sessionResponse.data.user_id;
    console.log(`✅ 会话创建成功，用户ID: ${userId}`);
    
    // 2. 启动分析
    console.log('2. 启动分析...');
    const startResponse = await axios.post(`http://localhost:8443/api/start/${userId}`);
    
    if (startResponse.data.status !== 'success') {
      console.log('⚠️  启动分析失败，但继续测试WebSocket连接');
    } else {
      console.log('✅ 分析启动成功');
    }
    
    // 3. 测试WebSocket连接
    console.log('3. 测试WebSocket连接...');
    const wsUrl = `ws://localhost:8443/ws/${userId}`;
    console.log(`连接URL: ${wsUrl}`);
    
    const ws = new WebSocket(wsUrl);
    
    ws.on('open', () => {
      console.log('✅ WebSocket连接已建立');
      
      // 发送连接确认
      const connectionMessage = {
        type: 'connection',
        user_id: userId,
        timestamp: new Date().toISOString()
      };
      
      ws.send(JSON.stringify(connectionMessage));
      console.log('📤 已发送连接确认消息');
      
      // 请求统计数据
      setTimeout(() => {
        const statsMessage = {
          type: 'get_stats',
          user_id: userId,
          timestamp: new Date().toISOString()
        };
        
        ws.send(JSON.stringify(statsMessage));
        console.log('📤 已发送统计数据请求');
      }, 1000);
      
      // 模拟发送视频帧
      setTimeout(() => {
        const frameMessage = {
          type: 'video_frame',
          frame: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=',
          user_id: userId,
          timestamp: Date.now()
        };
        
        ws.send(JSON.stringify(frameMessage));
        console.log('📤 已发送模拟视频帧');
      }, 2000);
    });
    
    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data);
        console.log('📥 收到消息:', message.type);
        
        if (message.type === 'connection_established') {
          console.log('✅ 连接确认消息已收到');
        } else if (message.type === 'stats_update') {
          console.log('✅ 统计数据已收到:', message.data);
        } else if (message.type === 'frame_result') {
          console.log('✅ 帧处理结果已收到');
        }
      } catch (error) {
        console.log('📥 收到原始消息:', data.toString());
      }
    });
    
    ws.on('close', (code, reason) => {
      console.log(`🔌 WebSocket连接已关闭: ${code} - ${reason}`);
    });
    
    ws.on('error', (error) => {
      console.error('❌ WebSocket错误:', error);
    });
    
    // 保持连接5秒
    setTimeout(() => {
      console.log('🔚 测试完成，关闭连接');
      ws.close();
    }, 5000);
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
  }
}

// 运行测试
testMobileWebSocket(); 