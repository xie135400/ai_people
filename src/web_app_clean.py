#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
干净的WebSocket处理函数
"""

# 这是一个干净的WebSocket端点实现
websocket_endpoint_code = '''
        @self.app.websocket("/ws/{user_id}")
        async def websocket_endpoint(websocket: WebSocket, user_id: str):
            """WebSocket连接，用于实时数据推送和视频帧处理"""
            logger.info(f"WebSocket连接请求: user_id={user_id}")
            logger.info(f"当前用户会话: {list(self.user_sessions.keys())}")
            
            session = None
            try:
                await websocket.accept()
                logger.info(f"WebSocket连接已接受: user_id={user_id}")
                
                if user_id not in self.user_sessions:
                    logger.warning(f"用户会话不存在: {user_id}")
                    await websocket.close(code=4004, reason="用户会话不存在")
                    return
                
                self.websocket_connections[user_id] = websocket
                session = self.user_sessions[user_id]
                
                logger.info(f"WebSocket连接已建立: {session.username}")
                
                # 发送连接成功消息
                try:
                    welcome_message = {
                        "type": "connection_established",
                        "user_id": user_id,
                        "username": session.username,
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(welcome_message))
                    logger.info(f"已发送欢迎消息给用户: {session.username}")
                except Exception as e:
                    logger.error(f"发送欢迎消息失败: {e}")
                    raise
                
                while True:
                    try:
                        # 接收消息
                        message = await websocket.receive_text()
                        logger.debug(f"收到WebSocket消息: {message}")
                        data = json.loads(message)
                        
                        if data.get("type") == "video_frame":
                            # 处理视频帧
                            frame_data = data.get("frame")
                            if frame_data and session.is_running:
                                logger.debug(f"处理用户 {session.username} 的视频帧")
                                result_frame, stats = session.process_frame(frame_data)
                                
                                # 发送处理结果
                                response = {
                                    "type": "frame_result",
                                    "frame": result_frame,
                                    "stats": {
                                        "realtime": stats.get("realtime", {}) if stats else {},
                                        "behavior": stats.get("behavior", {}) if stats else {},
                                        "age_distribution": self._get_age_distribution(session),
                                        "frame_count": session.frame_count,
                                        "username": session.username,
                                        "timestamp": datetime.now().isoformat()
                                    }
                                }
                                await websocket.send_text(json.dumps(response))
                                logger.debug(f"已发送处理结果给用户 {session.username}")
                            else:
                                logger.warning(f"用户 {session.username} 帧处理条件不满足: frame_data={bool(frame_data)}, is_running={session.is_running}")
                        
                        elif data.get("type") == "get_stats":
                            # 发送统计数据
                            if session.analyzer and session.is_running:
                                realtime_stats = session.analyzer.persistent_analyzer.get_realtime_statistics()
                                behavior_stats = session.analyzer.behavior_analyzer.get_behavior_summary()
                                age_distribution = self._get_age_distribution(session)
                            else:
                                realtime_stats = {"total_people": 0, "active_tracks": 0, "avg_age": None, "male_count": 0, "female_count": 0}
                                behavior_stats = {"shoppers": 0, "browsers": 0, "avg_engagement_score": 0, "avg_dwell_time": 0, "shopper_rate": 0}
                                age_distribution = {"0-17": 0, "18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
                            
                            response = {
                                "type": "stats_update",
                                "data": {
                                    "realtime": realtime_stats,
                                    "behavior": behavior_stats,
                                    "age_distribution": age_distribution,
                                    "frame_count": session.frame_count,
                                    "is_running": session.is_running,
                                    "username": session.username,
                                    "timestamp": datetime.now().isoformat()
                                }
                            }
                            await websocket.send_text(json.dumps(response))
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON解析错误: {e}")
                        error_response = {
                            "type": "error",
                            "message": "消息格式错误",
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send_text(json.dumps(error_response))
                    except Exception as e:
                        logger.error(f"处理WebSocket消息时出错: {e}")
                        logger.error(f"错误类型: {type(e)}")
                        import traceback
                        logger.error(f"错误堆栈: {traceback.format_exc()}")
                        
                        # 发送错误响应
                        try:
                            error_response = {
                                "type": "error",
                                "message": str(e),
                                "timestamp": datetime.now().isoformat()
                            }
                            await websocket.send_text(json.dumps(error_response))
                        except:
                            # 如果连发送错误消息都失败了，就断开连接
                            break
                    
            except WebSocketDisconnect as e:
                logger.info(f"WebSocket连接断开: {session.username if session else user_id}, code={e.code}")
            except Exception as e:
                logger.error(f"WebSocket错误: {e}")
                logger.error(f"错误类型: {type(e)}")
                import traceback
                logger.error(f"错误堆栈: {traceback.format_exc()}")
                
                # 尝试发送错误消息给客户端
                try:
                    if 'websocket' in locals():
                        error_message = {
                            "type": "error",
                            "message": str(e),
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send_text(json.dumps(error_message))
                except:
                    pass
            finally:
                if user_id in self.websocket_connections:
                    del self.websocket_connections[user_id]
                logger.info(f"WebSocket连接已移除: {user_id}")
'''

print("干净的WebSocket端点代码已准备好") 