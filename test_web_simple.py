#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Web应用测试脚本
用于验证数据显示功能，包含年龄分布显示
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import logging
import webbrowser
import time
import threading
import json
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import random
import cv2
import numpy as np
from flask import Flask, Response, render_template, jsonify

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入项目模块
from src.face_analyzer import InsightFaceAnalyzer
from src.detector import YOLODetector
from src.tracker import PersonTracker

# 初始化Flask应用
app = Flask(__name__, 
           static_folder='static',
           template_folder='.')

# 全局变量
camera = None
output_frame = None
lock = threading.Lock()
analyzer = None
detector = None
tracker = None
current_people = 0
age_distribution = {
    "children": 0,      # 0-12
    "teens": 0,         # 13-17
    "young_adults": 0,  # 18-25
    "adults": 0,        # 26-35
    "middle_aged": 0,   # 36-55
    "seniors": 0        # 56+
}
gender_distribution = {"Male": 0, "Female": 0}

def initialize_models():
    """初始化模型"""
    global analyzer, detector, tracker
    
    try:
        # 初始化人脸分析器
        analyzer = InsightFaceAnalyzer()
        logger.info("人脸分析器初始化成功")
        
        # 初始化人体检测器
        detector = YOLODetector(model_path="yolov8n.pt", conf_threshold=0.25)
        logger.info("人体检测器初始化成功")
        
        # 初始化跟踪器
        tracker = PersonTracker(max_age=30)
        logger.info("跟踪器初始化成功")
        
        return True
    except Exception as e:
        logger.error(f"模型初始化失败: {e}")
        return False

def get_camera():
    """获取摄像头"""
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)  # 使用默认摄像头
        # 设置分辨率
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
    return camera

def process_frame():
    """处理视频帧"""
    global output_frame, lock, current_people, age_distribution, gender_distribution
    
    # 获取摄像头
    camera = get_camera()
    
    while True:
        success, frame = camera.read()
        if not success:
            logger.error("无法读取摄像头帧")
            break
            
        try:
            # 检测人体
            detections = detector.detect(frame)
            
            # 跟踪检测结果
            tracks = tracker.update(detections, frame)
            
            # 分析人脸
            face_results = analyzer.detect_faces(frame)
            
            # 分析每个检测到的人
            current_faces = []
            current_ages = []
            current_genders = []
            
            for track in tracks:
                x, y = track.center
                # 在帧上绘制跟踪ID
                cv2.putText(frame, f"ID: {track.track_id}", (int(x) - 10, int(y) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # 处理检测到的人脸
            for face in face_results:
                # 绘制人脸框
                bbox = face.bbox
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 2)
                
                # 显示年龄和性别
                gender = "男" if face.gender == "Male" else "女"
                cv2.putText(frame, f"{gender}, {face.age}岁", 
                           (bbox[0], bbox[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                # 收集统计数据
                current_faces.append(face)
                current_ages.append(face.age)
                current_genders.append(face.gender)
            
            # 更新人数统计
            current_people = len(tracks)
            
            # 更新年龄分布
            age_distribution = {
                "children": 0,      # 0-12
                "teens": 0,         # 13-17
                "young_adults": 0,  # 18-25
                "adults": 0,        # 26-35
                "middle_aged": 0,   # 36-55
                "seniors": 0        # 56+
            }
            
            for age in current_ages:
                if age <= 12:
                    age_distribution["children"] += 1
                elif age <= 17:
                    age_distribution["teens"] += 1
                elif age <= 25:
                    age_distribution["young_adults"] += 1
                elif age <= 35:
                    age_distribution["adults"] += 1
                elif age <= 55:
                    age_distribution["middle_aged"] += 1
                else:
                    age_distribution["seniors"] += 1
            
            # 更新性别分布
            gender_distribution = {"Male": 0, "Female": 0}
            for gender in current_genders:
                if gender in gender_distribution:
                    gender_distribution[gender] += 1
            
            # 在帧上显示当前人数
            cv2.putText(frame, f"当前人数: {current_people}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 使用锁保护共享资源
            with lock:
                output_frame = frame.copy()
        
        except Exception as e:
            logger.error(f"处理帧时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # 使用锁保护共享资源
            with lock:
                output_frame = frame.copy()

def generate_frames():
    """生成视频流"""
    global output_frame, lock
    
    while True:
        # 等待直到有处理过的帧
        with lock:
            if output_frame is None:
                continue
            
            # 编码帧为JPEG
            (flag, encoded_image) = cv2.imencode(".jpg", output_frame)
            
            if not flag:
                continue
        
        # 生成帧数据
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
             bytearray(encoded_image) + b'\r\n')

@app.route("/")
def index():
    """主页"""
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    """视频流路由"""
    return Response(generate_frames(),
                   mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/stats")
def stats():
    """获取统计数据"""
    global current_people, age_distribution, gender_distribution
    
    return jsonify({
        "current_people": current_people,
        "age_distribution": age_distribution,
        "gender_distribution": gender_distribution
    })

@app.route("/records")
def records():
    """显示历史记录页面"""
    return render_template("records.html")

def main():
    """主函数"""
    print("🧪 启动AI人流分析系统测试模式")
    print("=" * 50)
    print("📊 此模式使用模拟数据测试Web界面功能")
    print("✅ 实时数据更新")
    print("✅ WebSocket连接")
    print("✅ 图表显示")
    print("✅ 状态控制")
    print("🎂 年龄分布显示（新增）")
    print("=" * 50)
    
    # 初始化模型
    if initialize_models():
        # 启动处理线程
        t = threading.Thread(target=process_frame)
        t.daemon = True
        t.start()
        
        # 启动Flask应用
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    else:
        logger.error("模型初始化失败，应用无法启动")

if __name__ == "__main__":
    main() 