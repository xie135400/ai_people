#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用模块
基于FastAPI的AI人流分析Web界面
使用浏览器摄像头进行分析，支持多用户
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading
import cv2
import numpy as np
import base64
from pathlib import Path
import traceback
import uuid
import time
import ssl
import os
import ipaddress

from src.complete_analyzer import CompleteAnalyzer
from src.database import DatabaseManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserSession:
    """用户会话类"""
    def __init__(self, user_id: str, username: str = None):
        self.user_id = user_id
        self.username = username or f"用户_{user_id[:8]}"
        self.analyzer = None
        self.is_running = False
        self.frame_count = 0
        self.current_frame = None
        self.current_stats = {}
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
    def start_analysis(self, db_config: Dict = None):
        """启动分析"""
        if not self.is_running:
            self.analyzer = CompleteAnalyzer(
                session_name=f"{self.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                use_insightface=True,
                db_config=db_config,
                save_interval=10
            )
            self.is_running = True
            self.frame_count = 0
            logger.info(f"用户 {self.username} 开始分析")
    
    def stop_analysis(self):
        """停止分析"""
        if self.is_running:
            self.is_running = False
            if self.analyzer:
                try:
                    self.analyzer.close()
                except Exception as e:
                    logger.error(f"关闭分析器失败: {e}")
                finally:
                    self.analyzer = None
            logger.info(f"用户 {self.username} 停止分析")
    
    def process_frame(self, frame_data: str):
        """处理来自浏览器的视频帧"""
        try:
            if not self.is_running or not self.analyzer:
                logger.warning(f"用户 {self.username}: 处理条件不满足 - is_running={self.is_running}, analyzer={bool(self.analyzer)}")
                return None, {}
            
            # 解码base64图像
            header, encoded = frame_data.split(',', 1)
            image_data = base64.b64decode(encoded)
            
            # 转换为numpy数组
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                logger.warning(f"用户 {self.username}: 无法解码图像")
                return None, {}
            
            logger.debug(f"用户 {self.username}: 成功解码图像，尺寸: {frame.shape}")
            
            # 处理帧
            result_frame, stats = self.analyzer.process_frame(frame)
            
            if result_frame is None:
                logger.warning(f"用户 {self.username}: 分析器返回空结果")
                return None, {}
            
            # 编码结果帧
            # 性能优化：降低JPEG质量以提高编码速度
            _, buffer = cv2.imencode('.jpg', result_frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            result_base64 = base64.b64encode(buffer).decode('utf-8')
            
            self.current_frame = f"data:image/jpeg;base64,{result_base64}"
            self.current_stats = stats
            self.frame_count += 1
            self.last_activity = datetime.now()
            
            logger.debug(f"用户 {self.username}: 帧处理完成，帧数: {self.frame_count}")
            
            return self.current_frame, stats
            
        except Exception as e:
            logger.error(f"用户 {self.username} 处理帧失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None, {}

class WebApp:
    """AI人流分析Web应用"""
    
    def __init__(self, db_config: Dict = None):
        """初始化Web应用"""
        self.app = FastAPI(title="AI人流分析系统", version="1.0.0")
        self.db_config = db_config
        self.db = DatabaseManager(db_config)
        
        # 用户会话管理
        self.user_sessions: Dict[str, UserSession] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        
        # SSL证书路径
        self.cert_dir = Path("certs")
        self.cert_file = self.cert_dir / "cert.pem"
        self.key_file = self.cert_dir / "key.pem"
        
        # 配置CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 设置路由
        self._setup_routes()
        
        # 创建静态文件目录
        self._setup_static_files()
        
        # 启动清理任务
        self._start_cleanup_task()
        
        logger.info("Web应用初始化完成")
    
    def _generate_self_signed_cert(self):
        """生成自签名SSL证书"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            import datetime
            
            # 创建证书目录
            self.cert_dir.mkdir(exist_ok=True)
            
            # 生成私钥
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # 创建证书主题
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AI People Analytics"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            # 创建证书
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("127.0.0.1"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # 保存证书
            with open(self.cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # 保存私钥
            with open(self.key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info(f"自签名SSL证书已生成: {self.cert_file}")
            return True
            
        except ImportError:
            logger.warning("cryptography库未安装，无法生成自签名证书")
            logger.info("请运行: pip install cryptography")
            return False
        except Exception as e:
            logger.error(f"生成SSL证书失败: {e}")
            return False
    
    def _setup_ssl_context(self):
        """设置SSL上下文"""
        if not self.cert_file.exists() or not self.key_file.exists():
            logger.info("SSL证书不存在，正在生成自签名证书...")
            if not self._generate_self_signed_cert():
                return None
        
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(self.cert_file, self.key_file)
            logger.info("SSL上下文配置成功")
            return ssl_context
        except Exception as e:
            logger.error(f"SSL上下文配置失败: {e}")
            return None
    
    def _setup_static_files(self):
        """设置静态文件目录"""
        static_dir = Path("static")
        static_dir.mkdir(exist_ok=True)
        
        # 挂载静态文件
        self.app.mount("/static", StaticFiles(directory="static"), name="static")
    
    def _start_cleanup_task(self):
        """启动清理任务"""
        def cleanup_inactive_sessions():
            while True:
                try:
                    current_time = datetime.now()
                    inactive_users = []
                    
                    for user_id, session in self.user_sessions.items():
                        # 清理30分钟无活动的会话
                        if (current_time - session.last_activity).seconds > 1800:
                            inactive_users.append(user_id)
                    
                    for user_id in inactive_users:
                        logger.info(f"清理无活动用户: {self.user_sessions[user_id].username}")
                        self.user_sessions[user_id].stop_analysis()
                        del self.user_sessions[user_id]
                        if user_id in self.websocket_connections:
                            del self.websocket_connections[user_id]
                    
                    time.sleep(300)  # 每5分钟检查一次
                except Exception as e:
                    logger.error(f"清理任务错误: {e}")
                    time.sleep(60)
        
        cleanup_thread = threading.Thread(target=cleanup_inactive_sessions)
        cleanup_thread.daemon = True
        cleanup_thread.start()
    
    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def read_root():
            """主页"""
            return self._get_main_page()
        
        @self.app.post("/api/create-session")
        async def create_session(request: Request):
            """创建用户会话"""
            username = None
            try:
                # 尝试解析JSON请求体
                body = await request.json()
                username = body.get("username") if body else None
            except:
                # 如果解析失败，username保持为None
                pass
            
            user_id = str(uuid.uuid4())
            session = UserSession(user_id, username)
            self.user_sessions[user_id] = session
            
            logger.info(f"创建用户会话: {session.username} (ID: {user_id})")
            
            return {
                "user_id": user_id,
                "username": session.username,
                "status": "success"
            }
        
        @self.app.get("/api/status/{user_id}")
        async def get_status(user_id: str):
            """获取用户状态"""
            if user_id not in self.user_sessions:
                raise HTTPException(status_code=404, detail="用户会话不存在")
            
            session = self.user_sessions[user_id]
            return {
                "user_id": user_id,
                "username": session.username,
                "is_running": session.is_running,
                "frame_count": session.frame_count,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            }
        
        @self.app.post("/api/start/{user_id}")
        async def start_analysis(user_id: str):
            """开始分析"""
            if user_id not in self.user_sessions:
                raise HTTPException(status_code=404, detail="用户会话不存在")
            
            try:
                session = self.user_sessions[user_id]
                if not session.is_running:
                    session.start_analysis(db_config=self.db_config)
                    return {"status": "success", "message": f"{session.username} 分析已开始"}
                else:
                    return {"status": "info", "message": f"{session.username} 分析已在运行中"}
            except Exception as e:
                logger.error(f"启动分析失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/stop/{user_id}")
        async def stop_analysis(user_id: str):
            """停止分析"""
            if user_id not in self.user_sessions:
                raise HTTPException(status_code=404, detail="用户会话不存在")
            
            try:
                session = self.user_sessions[user_id]
                if session.is_running:
                    session.stop_analysis()
                    return {"status": "success", "message": f"{session.username} 分析已停止"}
                else:
                    return {"status": "info", "message": f"{session.username} 分析未在运行"}
            except Exception as e:
                logger.error(f"停止分析失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/realtime-stats/{user_id}")
        async def get_realtime_stats(user_id: str):
            """获取实时统计数据"""
            if user_id not in self.user_sessions:
                return self._get_default_stats()
            
            try:
                session = self.user_sessions[user_id]
                if session.analyzer and session.is_running:
                    # 获取实时统计
                    realtime_stats = session.analyzer.persistent_analyzer.get_realtime_statistics()
                    behavior_stats = session.analyzer.behavior_analyzer.get_behavior_summary()
                    
                    # 获取年龄分布数据
                    age_distribution = self._get_age_distribution(session)
                    
                    return {
                        "realtime": realtime_stats,
                        "behavior": behavior_stats,
                        "age_distribution": age_distribution,
                        "frame_count": session.frame_count,
                        "username": session.username,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return self._get_default_stats(session.username)
            except Exception as e:
                logger.error(f"获取实时统计失败: {e}")
                return {"error": str(e)}
        
        @self.app.get("/api/users")
        async def get_active_users():
            """获取活跃用户列表"""
            users = []
            for user_id, session in self.user_sessions.items():
                users.append({
                    "user_id": user_id,
                    "username": session.username,
                    "is_running": session.is_running,
                    "frame_count": session.frame_count,
                    "last_activity": session.last_activity.isoformat()
                })
            return {"users": users, "total": len(users)}
        
        @self.app.websocket("/ws/{user_id}")
        async def websocket_endpoint(websocket: WebSocket, user_id: str):
            """WebSocket连接，用于实时数据推送和视频帧处理"""
            await websocket.accept()
            
            if user_id not in self.user_sessions:
                await websocket.close(code=4004, reason="用户会话不存在")
                return
            
            self.websocket_connections[user_id] = websocket
            session = self.user_sessions[user_id]
            
            logger.info(f"WebSocket连接已建立: {session.username}")
            
            try:
                while True:
                    # 接收消息
                    message = await websocket.receive_text()
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
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket连接断开: {session.username}")
            except Exception as e:
                logger.error(f"WebSocket错误: {e}")
            finally:
                if user_id in self.websocket_connections:
                    del self.websocket_connections[user_id]
                logger.info(f"WebSocket连接已移除: {session.username}")
    
        @self.app.get("/api/records/all")
        async def get_all_analysis_records(limit: int = Query(20, ge=1, le=100)):
            """获取所有用户的分析记录列表"""
            try:
                db = self.db
                # 获取所有记录，不限制用户
                records = db.get_all_analysis_records(limit)
                
                # 简化记录数据以减少传输量
                simplified_records = []
                for record in records:
                    record_data = {
                        "id": record.get("id"),
                        "record_name": record.get("record_name"),
                        "timestamp": record.get("timestamp"),
                        "total_people": record.get("total_people", 0),
                        "active_tracks": record.get("active_tracks", 0),
                        "avg_age": record.get("avg_age"),
                        "male_count": record.get("male_count", 0),
                        "female_count": record.get("female_count", 0),
                        "additional_data": record.get("additional_data", {})
                    }
                    simplified_records.append(record_data)
                
                return {"records": simplified_records}
            except Exception as e:
                logger.error(f"获取所有分析记录失败: {e}")
                raise HTTPException(status_code=500, detail=f"获取分析记录失败: {str(e)}")
        
        @self.app.get("/api/record/all/{record_id}")
        async def get_all_analysis_record_detail(record_id: int):
            """获取任意分析记录详情"""
            try:
                db = self.db
                record = db.get_analysis_record(record_id)
                
                if not record:
                    raise HTTPException(status_code=404, detail=f"未找到ID为{record_id}的分析记录")
                
                return {"record": record}
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"获取分析记录详情失败: {e}")
                raise HTTPException(status_code=500, detail=f"获取分析记录详情失败: {str(e)}")
        
        @self.app.post("/api/analyze-frame")
        async def analyze_frame(request: Request):
            """分析单个视频帧（移动端）"""
            try:
                form = await request.form()
                user_id = form.get("user_id")
                frame_file = form.get("frame")
                
                if not user_id or not frame_file:
                    raise HTTPException(status_code=400, detail="缺少必要参数")
                
                if user_id not in self.user_sessions:
                    raise HTTPException(status_code=404, detail="用户会话不存在")
                
                session = self.user_sessions[user_id]
                
                # 读取图像数据
                frame_data = await frame_file.read()
                
                # 转换为numpy数组
                import numpy as np
                import cv2
                
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is None:
                    raise HTTPException(status_code=400, detail="无效的图像数据")
                
                # 使用分析器处理帧
                if session.analyzer is None:
                    session.analyzer = CompleteAnalyzer(db_config=self.db_config)
                
                result = session.analyzer.analyze_frame(frame)
                
                # 更新会话统计
                session.frame_count += 1
                session.last_activity = datetime.now()
                
                # 提取人脸信息
                faces = []
                if result and 'faces' in result:
                    for face in result['faces']:
                        face_info = {
                            'box': {
                                'x': int(face.get('bbox', [0, 0, 0, 0])[0]),
                                'y': int(face.get('bbox', [0, 0, 0, 0])[1]),
                                'width': int(face.get('bbox', [0, 0, 0, 0])[2]),
                                'height': int(face.get('bbox', [0, 0, 0, 0])[3])
                            }
                        }
                        
                        if 'age' in face:
                            face_info['age'] = float(face['age'])
                        if 'gender' in face:
                            face_info['gender'] = face['gender']
                        
                        faces.append(face_info)
                
                # 构建响应
                response_data = {
                    "status": "success",
                    "faces": faces,
                    "frame_count": session.frame_count
                }
                
                # 添加统计数据
                if result and 'stats' in result:
                    response_data['stats'] = result['stats']
                
                return response_data
                
            except Exception as e:
                logger.error(f"分析帧失败: {e}")
                raise HTTPException(status_code=500, detail="分析帧失败")
        
        @self.app.get("/api/records/{user_id}")
        async def get_analysis_records(user_id: str, limit: int = Query(20, ge=1, le=100)):
            """获取指定用户的分析记录列表"""
            if user_id not in self.user_sessions:
                raise HTTPException(status_code=404, detail="用户会话不存在")
            
            session = self.user_sessions[user_id]
            try:
                db = self.db
                records = db.get_analysis_records(user_id, limit)
                
                simplified_records = []
                for record in records:
                    record_data = {
                        "id": record.get("id"),
                        "record_name": record.get("record_name"),
                        "timestamp": record.get("timestamp"),
                        "total_people": record.get("total_people", 0),
                        "active_tracks": record.get("active_tracks", 0),
                        "avg_age": record.get("avg_age"),
                        "male_count": record.get("male_count", 0),
                        "female_count": record.get("female_count", 0),
                        "additional_data": record.get("additional_data", {})
                    }
                    simplified_records.append(record_data)
                
                return {"records": simplified_records}
            except Exception as e:
                logger.error(f"获取用户 {user_id} 分析记录失败: {e}")
                raise HTTPException(status_code=500, detail=f"获取用户 {user_id} 分析记录失败: {str(e)}")
    
    def _get_default_stats(self, username: str = "未知用户"):
        """获取默认统计数据"""
        return {
            "realtime": {
                "total_people": 0,
                "active_tracks": 0,
                "avg_age": None,
                "male_count": 0,
                "female_count": 0
            },
            "behavior": {
                "shoppers": 0,
                "browsers": 0,
                "avg_engagement_score": 0,
                "avg_dwell_time": 0,
                "shopper_rate": 0
            },
            "age_distribution": {
                "0-17": 0, "18-25": 0, "26-35": 0, 
                "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0
            },
            "frame_count": 0,
            "username": username,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_age_distribution(self, session: UserSession):
        """获取年龄分布数据"""
        try:
            if not session.analyzer:
                return {"0-17": 0, "18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
            
            # 获取人员档案
            if hasattr(session.analyzer.persistent_analyzer, 'analyzer'):
                profiles = session.analyzer.persistent_analyzer.analyzer.person_profiles
            else:
                profiles = session.analyzer.persistent_analyzer.person_profiles
            
            age_groups = {
                "0-17": 0, "18-25": 0, "26-35": 0, 
                "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0
            }
            
            for track_id, profile in profiles.items():
                if profile.avg_age is not None:
                    age = profile.avg_age
                    if age < 18:
                        age_groups["0-17"] += 1
                    elif age < 26:
                        age_groups["18-25"] += 1
                    elif age < 36:
                        age_groups["26-35"] += 1
                    elif age < 46:
                        age_groups["36-45"] += 1
                    elif age < 56:
                        age_groups["46-55"] += 1
                    elif age < 66:
                        age_groups["56-65"] += 1
                    else:
                        age_groups["65+"] += 1
            
            return age_groups
            
        except Exception as e:
            logger.error(f"获取年龄分布失败: {e}")
            return {"0-17": 0, "18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
    
    def _get_main_page(self) -> str:
        """获取主页HTML"""
        return """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI人流分析系统</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 1rem;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .user-info {
                    background: rgba(255,255,255,0.1);
                    padding: 0.5rem 1rem;
                    border-radius: 20px;
                    display: inline-block;
                    margin-top: 0.5rem;
                }
                .container {
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 2rem;
                }
                .dashboard {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 2rem;
                    margin-bottom: 2rem;
                }
                .card {
                    background: white;
                    border-radius: 8px;
                    padding: 1.5rem;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }
                .card:hover {
                    transform: translateY(-2px);
                }
                .card h3 {
                    margin-top: 0;
                    color: #333;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 0.5rem;
                }
                .login-section {
                    background: white;
                    border-radius: 8px;
                    padding: 2rem;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                    margin-bottom: 2rem;
                }
                .login-section input {
                    padding: 0.75rem;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    margin: 0 0.5rem;
                    font-size: 1rem;
                    width: 200px;
                }
                .controls {
                    text-align: center;
                    margin-bottom: 2rem;
                }
                .btn {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    border-radius: 4px;
                    cursor: pointer;
                    margin: 0 0.5rem;
                    font-size: 1rem;
                    transition: background 0.2s;
                }
                .btn:hover {
                    background: #5a67d8;
                }
                .btn:disabled {
                    background: #ccc;
                    cursor: not-allowed;
                }
                .btn.stop {
                    background: #e53e3e;
                }
                .btn.stop:hover {
                    background: #c53030;
                }
                .status {
                    display: inline-block;
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    font-size: 0.875rem;
                    font-weight: bold;
                    margin-left: 1rem;
                }
                .status.running {
                    background: #48bb78;
                    color: white;
                }
                .status.stopped {
                    background: #e53e3e;
                    color: white;
                }
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 1rem;
                }
                .stat-item {
                    text-align: center;
                    padding: 1rem;
                    background: #f7fafc;
                    border-radius: 4px;
                }
                .stat-value {
                    font-size: 2rem;
                    font-weight: bold;
                    color: #667eea;
                }
                .stat-label {
                    font-size: 0.875rem;
                    color: #666;
                    margin-top: 0.5rem;
                }
                .age-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
                    gap: 0.5rem;
                }
                .age-item {
                    text-align: center;
                    padding: 0.5rem;
                    background: #f7fafc;
                    border-radius: 4px;
                    border-left: 3px solid #667eea;
                }
                .age-value {
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: #667eea;
                }
                .age-label {
                    font-size: 0.75rem;
                    color: #666;
                    margin-top: 0.25rem;
                }
                .video-container {
                    position: relative;
                    text-align: center;
                }
                #localVideo, #processedVideo {
                    max-width: 100%;
                    border-radius: 4px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    margin: 10px 0;
                }
                #localVideo {
                    border: 2px solid #4299e1;
                }
                #processedVideo {
                    border: 2px solid #48bb78;
                }
                .video-overlay {
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    background: rgba(0,0,0,0.7);
                    color: white;
                    padding: 0.5rem;
                    border-radius: 4px;
                    font-size: 0.875rem;
                }
                .connection-status {
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    font-size: 0.875rem;
                    font-weight: bold;
                }
                .connection-status.connected {
                    background: #48bb78;
                    color: white;
                }
                .connection-status.disconnected {
                    background: #e53e3e;
                    color: white;
                }
                .debug-info {
                    position: fixed;
                    bottom: 10px;
                    left: 10px;
                    background: rgba(0,0,0,0.8);
                    color: white;
                    padding: 0.5rem;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    font-family: monospace;
                    max-width: 300px;
                }
                .hidden {
                    display: none;
                }
                .camera-error {
                    background: #fed7d7;
                    color: #c53030;
                    padding: 1rem;
                    border-radius: 4px;
                    margin: 1rem 0;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div class="connection-status disconnected" id="connectionStatus">未连接</div>
            <div class="debug-info" id="debugInfo">调试信息</div>
            
            <div class="header">
                <h1>🤖 AI人流分析系统</h1>
                <p>实时人员检测 · 行为分析 · 数据洞察 · 年龄分布</p>
                <div class="user-info" id="userInfo" style="display: none;">
                    👤 <span id="currentUser">未登录</span>
                </div>
            </div>
            
            <div class="container">
                <!-- 登录区域 -->
                <div class="login-section" id="loginSection">
                    <h2>🚀 开始使用</h2>
                    <p>请输入您的用户名开始分析</p>
                    <input type="text" id="usernameInput" placeholder="输入用户名（可选）" maxlength="20">
                    <button id="loginBtn" class="btn">开始使用</button>
                    <div class="camera-error hidden" id="cameraError">
                        ❌ 无法访问摄像头，请确保已授权摄像头权限
                    </div>
                </div>
                
                <!-- 主界面 -->
                <div id="mainInterface" class="hidden">
                    <div class="controls">
                        <button id="startBtn" class="btn">开始分析</button>
                        <button id="stopBtn" class="btn stop">停止分析</button>
                        <button id="recordsBtn" class="btn" style="background: #4299e1;">查看分析记录</button>
                        <button id="logoutBtn" class="btn" style="background: #718096;">退出登录</button>
                        <span id="status" class="status stopped">已停止</span>
                    </div>
                    
                    <div class="dashboard">
                        <div class="card">
                            <h3>📹 实时视频</h3>
                            <div class="video-container">
                                <div style="margin-bottom: 10px;">
                                    <strong>📷 原始摄像头</strong>
                                    <video id="localVideo" autoplay muted width="320" height="240"></video>
                                </div>
                                <div>
                                    <strong>🤖 AI分析结果</strong>
                                    <img id="processedVideo" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIwIiBoZWlnaHQ9IjI0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjVmNWY1Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OTk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPueCueWHu+W8gOWni+WIhuaekDwvdGV4dD48L3N2Zz4=" alt="处理后的视频" width="320" height="240">
                                </div>
                                <div class="video-overlay">
                                    帧数: <span id="frameCount">0</span> | 
                                    状态: <span id="captureStatus">未开始</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h3>📊 实时统计</h3>
                            <div class="stats-grid">
                                <div class="stat-item">
                                    <div class="stat-value" id="totalPeople">0</div>
                                    <div class="stat-label">总人数</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value" id="activePeople">0</div>
                                    <div class="stat-label">当前人数</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value" id="avgAge">--</div>
                                    <div class="stat-label">平均年龄</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value" id="avgDwell">0s</div>
                                    <div class="stat-label">平均停留</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h3>👥 性别分布</h3>
                            <div class="stats-grid">
                                <div class="stat-item">
                                    <div class="stat-value" id="maleCount" style="color: #4299e1;">0</div>
                                    <div class="stat-label">男性</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value" id="femaleCount" style="color: #ed64a6;">0</div>
                                    <div class="stat-label">女性</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value" id="malePercent" style="color: #4299e1;">0%</div>
                                    <div class="stat-label">男性比例</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value" id="femalePercent" style="color: #ed64a6;">0%</div>
                                    <div class="stat-label">女性比例</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h3>🎂 年龄分布</h3>
                            <div class="age-grid">
                                <div class="age-item">
                                    <div class="age-value" id="age0_17">0</div>
                                    <div class="age-label">0-17岁</div>
                                </div>
                                <div class="age-item">
                                    <div class="age-value" id="age18_25">0</div>
                                    <div class="age-label">18-25岁</div>
                                </div>
                                <div class="age-item">
                                    <div class="age-value" id="age26_35">0</div>
                                    <div class="age-label">26-35岁</div>
                                </div>
                                <div class="age-item">
                                    <div class="age-value" id="age36_45">0</div>
                                    <div class="age-label">36-45岁</div>
                                </div>
                                <div class="age-item">
                                    <div class="age-value" id="age46_55">0</div>
                                    <div class="age-label">46-55岁</div>
                                </div>
                                <div class="age-item">
                                    <div class="age-value" id="age56_65">0</div>
                                    <div class="age-label">56-65岁</div>
                                </div>
                                <div class="age-item">
                                    <div class="age-value" id="age65_plus">0</div>
                                    <div class="age-label">65+岁</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h3>🛍️ 行为分析</h3>
                            <div class="stats-grid">
                                <div class="stat-item">
                                    <div class="stat-value" id="shoppers">0</div>
                                    <div class="stat-label">购物者</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value" id="browsers">0</div>
                                    <div class="stat-label">浏览者</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value" id="engagement">0</div>
                                    <div class="stat-label">参与度</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value" id="conversion">0%</div>
                                    <div class="stat-label">转化率</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                let ws = null;
                let localStream = null;
                let currentUserId = null;
                let currentUsername = null;
                let isAnalyzing = false;
                let frameInterval = null;
                
                // DOM元素
                const loginSection = document.getElementById('loginSection');
                const mainInterface = document.getElementById('mainInterface');
                const usernameInput = document.getElementById('usernameInput');
                const loginBtn = document.getElementById('loginBtn');
                const logoutBtn = document.getElementById('logoutBtn');
                const startBtn = document.getElementById('startBtn');
                const stopBtn = document.getElementById('stopBtn');
                const recordsBtn = document.getElementById('recordsBtn'); // 新增记录按钮
                const localVideo = document.getElementById('localVideo');
                const processedVideo = document.getElementById('processedVideo');
                const cameraError = document.getElementById('cameraError');
                const userInfo = document.getElementById('userInfo');
                const currentUser = document.getElementById('currentUser');
                const connectionStatus = document.getElementById('connectionStatus');
                const debugInfo = document.getElementById('debugInfo');
                
                // 登录功能
                loginBtn.onclick = async function() {
                    const username = usernameInput.value.trim() || null;
                    
                    // 隐藏之前的错误信息
                    cameraError.classList.add('hidden');
                    loginBtn.disabled = true;
                    loginBtn.textContent = '正在获取摄像头权限...';
                    
                    try {
                        // 检查浏览器支持
                        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                            throw new Error('您的浏览器不支持摄像头功能，请使用Chrome、Firefox或Safari等现代浏览器');
                        }
                        
                        // 检查是否为HTTPS或localhost
                        const isSecure = location.protocol === 'https:' || 
                                       location.hostname === 'localhost' || 
                                       location.hostname === '127.0.0.1';
                        
                        if (!isSecure) {
                            throw new Error('摄像头功能需要HTTPS连接或localhost访问。请使用 https:// 或 localhost 访问');
                        }
                        
                        console.log('正在请求摄像头权限...');
                        
                        // 请求摄像头权限
                        localStream = await navigator.mediaDevices.getUserMedia({ 
                            video: { 
                                width: { ideal: 640 }, 
                                height: { ideal: 480 },
                                facingMode: 'user'  // 前置摄像头
                            }, 
                            audio: false 
                        });
                        
                        console.log('摄像头权限获取成功');
                        localVideo.srcObject = localStream;
                        
                        // 等待视频加载
                        await new Promise((resolve) => {
                            localVideo.onloadedmetadata = resolve;
                        });
                        
                        console.log('摄像头视频流已准备就绪');
                        
                        // 创建用户会话
                        const response = await fetch('/api/create-session', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ username: username })
                        });
                        
                        const result = await response.json();
                        if (result.status === 'success') {
                            currentUserId = result.user_id;
                            currentUsername = result.username;
                            
                            // 切换界面
                            loginSection.classList.add('hidden');
                            mainInterface.classList.remove('hidden');
                            userInfo.style.display = 'block';
                            currentUser.textContent = currentUsername;
                            
                            // 连接WebSocket
                            connectWebSocket();
                            
                            console.log('登录成功:', result);
                        } else {
                            throw new Error('创建用户会话失败: ' + result.message);
                        }
                        
                    } catch (error) {
                        console.error('登录失败:', error);
                        
                        // 显示详细错误信息
                        let errorMessage = '<h4>❌ 无法访问摄像头</h4>';
                        
                        if (error.name === 'NotAllowedError') {
                            errorMessage += '<p><strong>原因：</strong>用户拒绝了摄像头权限</p>';
                            errorMessage += '<p><strong>解决方案：</strong></p>';
                            errorMessage += '<ul>';
                            errorMessage += '<li>点击地址栏左侧的摄像头图标</li>';
                            errorMessage += '<li>选择"允许"摄像头权限</li>';
                            errorMessage += '<li>刷新页面重试</li>';
                            errorMessage += '</ul>';
                        } else if (error.name === 'NotFoundError') {
                            errorMessage += '<p><strong>原因：</strong>未找到摄像头设备</p>';
                            errorMessage += '<p><strong>解决方案：</strong></p>';
                            errorMessage += '<ul>';
                            errorMessage += '<li>检查摄像头是否正确连接</li>';
                            errorMessage += '<li>确保摄像头驱动已安装</li>';
                            errorMessage += '<li>重启浏览器重试</li>';
                            errorMessage += '</ul>';
                        } else if (error.name === 'NotReadableError') {
                            errorMessage += '<p><strong>原因：</strong>摄像头被其他应用占用</p>';
                            errorMessage += '<p><strong>解决方案：</strong></p>';
                            errorMessage += '<ul>';
                            errorMessage += '<li>关闭其他使用摄像头的应用</li>';
                            errorMessage += '<li>重启浏览器</li>';
                            errorMessage += '<li>重新尝试</li>';
                            errorMessage += '</ul>';
                        } else if (error.name === 'OverconstrainedError') {
                            errorMessage += '<p><strong>原因：</strong>摄像头不支持请求的分辨率</p>';
                            errorMessage += '<p><strong>解决方案：</strong></p>';
                            errorMessage += '<ul>';
                            errorMessage += '<li>尝试使用不同的摄像头</li>';
                            errorMessage += '<li>更新摄像头驱动</li>';
                            errorMessage += '<li>联系技术支持</li>';
                            errorMessage += '</ul>';
                        } else {
                            errorMessage += '<p><strong>错误信息：</strong>' + error.message + '</p>';
                            errorMessage += '<p><strong>通用解决方案：</strong></p>';
                            errorMessage += '<ul>';
                            errorMessage += '<li>使用Chrome、Firefox或Safari浏览器</li>';
                            errorMessage += '<li>确保使用HTTPS或localhost访问</li>';
                            errorMessage += '<li>检查浏览器摄像头权限设置</li>';
                            errorMessage += '<li>重启浏览器重试</li>';
                            errorMessage += '</ul>';
                        }
                        
                        // 显示错误信息
                        cameraError.innerHTML = errorMessage;
                        cameraError.classList.remove('hidden');
                        
                        // 如果已获取到流，需要释放
                        if (localStream) {
                            localStream.getTracks().forEach(track => track.stop());
                            localStream = null;
                        }
                        
                    } finally {
                        loginBtn.disabled = false;
                        loginBtn.textContent = '开始使用';
                    }
                };
                
                // 退出登录
                logoutBtn.onclick = function() {
                    if (isAnalyzing) {
                        stopAnalysis();
                    }
                    
                    if (ws) {
                        ws.close();
                    }
                    
                    if (localStream) {
                        localStream.getTracks().forEach(track => track.stop());
                        localStream = null;
                    }
                    
                    // 重置状态
                    currentUserId = null;
                    currentUsername = null;
                    isAnalyzing = false;
                    
                    // 切换界面
                    mainInterface.classList.add('hidden');
                    loginSection.classList.remove('hidden');
                    userInfo.style.display = 'none';
                    cameraError.classList.add('hidden');
                    usernameInput.value = '';
                    
                    updateConnectionStatus('未连接', false);
                };
                
                // WebSocket连接
                function connectWebSocket() {
                    if (!currentUserId) return;
                    
                    try {
                        // 动态获取WebSocket地址
                        const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
                        const wsUrl = `${wsProtocol}//${location.host}/ws/${currentUserId}`;
                        
                        ws = new WebSocket(wsUrl);
                        
                        ws.onopen = function() {
                            console.log('WebSocket连接已建立');
                            updateConnectionStatus('已连接', true);
                        };
                        
                        ws.onmessage = function(event) {
                            try {
                                const data = JSON.parse(event.data);
                                console.log('收到WebSocket消息:', data.type);
                                
                                if (data.type === 'frame_result') {
                                    // 显示处理后的帧
                                    if (data.frame) {
                                        processedVideo.src = data.frame;
                                        document.getElementById('captureStatus').textContent = '已接收';
                                        console.log('处理后的帧已更新');
                                    }
                                    // 更新统计数据
                                    if (data.stats) {
                                        updateDashboard(data.stats);
                                    }
                                } else if (data.type === 'stats_update') {
                                    updateDashboard(data.data);
                                }
                                
                            } catch (error) {
                                console.error('解析WebSocket消息失败:', error);
                            }
                        };
                        
                        ws.onclose = function() {
                            console.log('WebSocket连接已关闭');
                            updateConnectionStatus('连接断开', false);
                            
                            // 自动重连
                            if (currentUserId) {
                                setTimeout(connectWebSocket, 3000);
                            }
                        };
                        
                        ws.onerror = function(error) {
                            console.error('WebSocket错误:', error);
                            updateConnectionStatus('连接错误', false);
                        };
                        
                    } catch (error) {
                        console.error('WebSocket连接失败:', error);
                        updateConnectionStatus('连接失败', false);
                    }
                }
                
                // 开始分析
                startBtn.onclick = async function() {
                    if (!currentUserId || isAnalyzing) return;
                    
                    try {
                        const response = await fetch(`/api/start/${currentUserId}`, { method: 'POST' });
                        const result = await response.json();
                        
                        if (result.status === 'success') {
                            isAnalyzing = true;
                            updateButtons();
                            startFrameCapture();
                            console.log('分析已开始');
                        } else {
                            alert('启动失败: ' + result.message);
                        }
                    } catch (error) {
                        console.error('启动分析失败:', error);
                        alert('启动失败: ' + error.message);
                    }
                };
                
                // 停止分析
                stopBtn.onclick = function() {
                    stopAnalysis();
                };
                
                function stopAnalysis() {
                    if (!currentUserId || !isAnalyzing) return;
                    
                    fetch(`/api/stop/${currentUserId}`, { method: 'POST' })
                        .then(response => response.json())
                        .then(result => {
                            isAnalyzing = false;
                            updateButtons();
                            stopFrameCapture();
                            console.log('分析已停止');
                        })
                        .catch(error => {
                            console.error('停止分析失败:', error);
                        });
                }
                
                // 帧捕获
                // 高级性能优化：智能帧跳过和动态调整
                let isProcessing = false;
                let lastFrameTime = 0;
                let frameSkipCount = 0;
                let adaptiveQuality = 0.6;
                let adaptiveScale = 0.8;
                
                function startFrameCapture() {
                    if (frameInterval) return;
                    
                    console.log('开始帧捕获...');
                    document.getElementById('captureStatus').textContent = '正在捕获';
                    
                    frameInterval = setInterval(() => {
                        if (isAnalyzing && localStream && ws && ws.readyState === WebSocket.OPEN) {
                            captureFrame();
                        } else {
                            console.log('帧捕获条件不满足:', {
                                isAnalyzing: isAnalyzing,
                                hasLocalStream: !!localStream,
                                wsReady: ws && ws.readyState === WebSocket.OPEN
                            });
                        }
                    }, 100); // 每100ms捕获一帧 (10 FPS)
                }
                
                function stopFrameCapture() {
                    if (frameInterval) {
                        clearInterval(frameInterval);
                        frameInterval = null;
                        console.log('帧捕获已停止');
                        document.getElementById('captureStatus').textContent = '已停止';
                    }
                }
                
                function captureFrame() {
                    try {
                        // 高级优化：如果上一帧还在处理中，跳过当前帧
                        if (isProcessing) {
                            frameSkipCount++;
                            if (frameSkipCount > 3) {
                                // 动态降低质量和分辨率
                                adaptiveQuality = Math.max(0.4, adaptiveQuality - 0.05);
                                adaptiveScale = Math.max(0.6, adaptiveScale - 0.05);
                                console.log('动态调整：质量=', adaptiveQuality, '缩放=', adaptiveScale);
                            }
                            return;
                        }
                        
                        // 检查视频是否准备就绪
                        if (!localVideo.videoWidth || !localVideo.videoHeight) {
                            return;
                        }
                        
                        // 高级优化：自适应帧间隔
                        const now = Date.now();
                        const minInterval = frameSkipCount > 5 ? 150 : 100; // 动态调整间隔
                        if (now - lastFrameTime < minInterval) {
                            return;
                        }
                        lastFrameTime = now;
                        
                        isProcessing = true;
                        frameSkipCount = 0;
                        
                        // 恢复质量和分辨率
                        adaptiveQuality = Math.min(0.6, adaptiveQuality + 0.01);
                        adaptiveScale = Math.min(0.8, adaptiveScale + 0.01);
                        
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        
                        canvas.width = localVideo.videoWidth * adaptiveScale;
                        canvas.height = localVideo.videoHeight * adaptiveScale;
                        
                        ctx.drawImage(localVideo, 0, 0, canvas.width, canvas.height);
                        const frameData = canvas.toDataURL('image/jpeg', adaptiveQuality);
                        
                        // 发送帧数据
                        ws.send(JSON.stringify({
                            type: 'video_frame',
                            frame: frameData
                        }));
                        
                        // 更新状态
                        document.getElementById('captureStatus').textContent = '正在发送';
                        
                        // 异步重置处理标志
                        setTimeout(() => {
                            isProcessing = false;
                        }, 30);
                        
                    } catch (error) {
                        console.error('捕获帧失败:', error);
                        isProcessing = false;
                    }
                }
                
                // 更新界面
                function updateButtons() {
                    startBtn.disabled = isAnalyzing;
                    stopBtn.disabled = !isAnalyzing;
                    
                    const status = document.getElementById('status');
                    if (isAnalyzing) {
                        status.textContent = '运行中';
                        status.className = 'status running';
                    } else {
                        status.textContent = '已停止';
                        status.className = 'status stopped';
                    }
                }
                
                function updateConnectionStatus(text, connected) {
                    connectionStatus.textContent = text;
                    connectionStatus.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
                }
                
                function updateDashboard(data) {
                    const realtime = data.realtime || {};
                    const behavior = data.behavior || {};
                    const ageDistribution = data.age_distribution || {};
                    
                    // 更新统计数字
                    document.getElementById('totalPeople').textContent = realtime.total_people || 0;
                    document.getElementById('activePeople').textContent = realtime.active_tracks || 0;
                    document.getElementById('avgAge').textContent = realtime.avg_age ? realtime.avg_age.toFixed(1) : '--';
                    document.getElementById('avgDwell').textContent = behavior.avg_dwell_time ? behavior.avg_dwell_time.toFixed(1) + 's' : '0s';
                    document.getElementById('frameCount').textContent = data.frame_count || 0;
                    
                    // 更新性别分布
                    const maleCount = realtime.male_count || 0;
                    const femaleCount = realtime.female_count || 0;
                    const totalGender = maleCount + femaleCount;
                    
                    document.getElementById('maleCount').textContent = maleCount;
                    document.getElementById('femaleCount').textContent = femaleCount;
                    
                    if (totalGender > 0) {
                        document.getElementById('malePercent').textContent = ((maleCount / totalGender) * 100).toFixed(1) + '%';
                        document.getElementById('femalePercent').textContent = ((femaleCount / totalGender) * 100).toFixed(1) + '%';
                    } else {
                        document.getElementById('malePercent').textContent = '0%';
                        document.getElementById('femalePercent').textContent = '0%';
                    }
                    
                    // 更新年龄分布
                    document.getElementById('age0_17').textContent = ageDistribution['0-17'] || 0;
                    document.getElementById('age18_25').textContent = ageDistribution['18-25'] || 0;
                    document.getElementById('age26_35').textContent = ageDistribution['26-35'] || 0;
                    document.getElementById('age36_45').textContent = ageDistribution['36-45'] || 0;
                    document.getElementById('age46_55').textContent = ageDistribution['46-55'] || 0;
                    document.getElementById('age56_65').textContent = ageDistribution['56-65'] || 0;
                    document.getElementById('age65_plus').textContent = ageDistribution['65+'] || 0;
                    
                    // 更新行为分析
                    document.getElementById('shoppers').textContent = behavior.shoppers || 0;
                    document.getElementById('browsers').textContent = behavior.browsers || 0;
                    document.getElementById('engagement').textContent = behavior.avg_engagement_score ? behavior.avg_engagement_score.toFixed(1) : 0;
                    document.getElementById('conversion').textContent = behavior.shopper_rate ? (behavior.shopper_rate * 100).toFixed(1) + '%' : '0%';
                    
                    // 更新调试信息
                    const totalAge = Object.values(ageDistribution).reduce((a, b) => a + b, 0);
                    const debugText = 
                        '用户: ' + (data.username || '未知') + '\\n' +
                        '最后更新: ' + new Date().toLocaleTimeString() + '\\n' +
                        '运行状态: ' + (data.is_running ? '是' : '否') + '\\n' +
                        '帧数: ' + (data.frame_count || 0) + '\\n' +
                        '总人数: ' + (realtime.total_people || 0) + '\\n' +
                        '当前人数: ' + (realtime.active_tracks || 0) + '\\n' +
                        '年龄分析人数: ' + totalAge;
                    debugInfo.textContent = debugText;
                }
                
                // 定期请求统计数据（备用方案）
                setInterval(() => {
                    if (currentUserId && (!ws || ws.readyState !== WebSocket.OPEN)) {
                        fetch(`/api/realtime-stats/${currentUserId}`)
                            .then(response => response.json())
                            .then(data => updateDashboard(data))
                            .catch(error => console.error('获取统计数据失败:', error));
                    }
                }, 2000);
                
                // 查看分析记录按钮
                recordsBtn.onclick = function() {
                    // 打开分析记录查看页面
                    window.open('/static/records.html', '_blank');
                };
                
                // 初始化
                updateButtons();
                updateConnectionStatus('未连接', false);
            </script>
        </body>
        </html>
        """
    
    def run(self, host: str = "localhost", port: int = 8000, use_ssl: bool = True):
        """运行Web应用"""
        if use_ssl:
            ssl_context = self._setup_ssl_context()
            if ssl_context:
                logger.info(f"启动HTTPS Web应用: https://{host}:{port}")
                uvicorn.run(
                    self.app, 
                    host=host, 
                    port=port, 
                    ssl_keyfile=str(self.key_file),
                    ssl_certfile=str(self.cert_file)
                )
            else:
                logger.warning("SSL配置失败，回退到HTTP模式")
                logger.info(f"启动HTTP Web应用: http://{host}:{port}")
                uvicorn.run(self.app, host=host, port=port)
        else:
            logger.info(f"启动HTTP Web应用: http://{host}:{port}")
            uvicorn.run(self.app, host=host, port=port)

def main():
    """主函数"""
    web_app = WebApp()
    web_app.run()

if __name__ == "__main__":
    main() 