#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL数据库测试脚本
"""

import sys
import os
import logging
from datetime import datetime

# 确保src目录在Python路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, current_dir)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """测试数据库连接"""
    try:
        from src.database import DatabaseManager
        from src.db_config import DatabaseConfig
        
        print("=== 测试MySQL数据库连接 ===")
        
        # 获取配置
        config = DatabaseConfig.get_pymysql_config()
        print(f"数据库配置: {config['host']}:{config['port']}/{config['database']}")
        
        # 创建数据库管理器
        db = DatabaseManager()
        print("✓ 数据库连接成功")
        
        return db
        
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return None

def test_basic_operations(db):
    """测试基本数据库操作"""
    try:
        print("\n=== 测试基本数据库操作 ===")
        
        # 测试创建会话
        session_name = f"测试会话_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_id = db.create_session(session_name)
        print(f"✓ 创建会话成功: {session_name} (ID: {session_id})")
        
        # 测试保存人员
        person_data = {
            'track_id': 1,
            'first_seen': datetime.now(),
            'last_seen': datetime.now(),
            'total_frames': 100,
            'faces_detected': 10,
            'avg_age': 25.5,
            'dominant_gender': 'male',
            'gender_confidence': 0.8
        }
        person_id = db.save_person(session_id, person_data)
        print(f"✓ 保存人员成功 (ID: {person_id})")
        
        # 测试保存位置
        db.save_position(person_id, 100, 200, datetime.now(), 1)
        print("✓ 保存位置成功")
        
        # 测试保存人脸
        face_data = {
            'age': 26,
            'gender': 'male',
            'gender_confidence': 0.85,
            'bbox': [50, 50, 150, 150],
            'confidence': 0.9,
            'timestamp': datetime.now()
        }
        db.save_face(person_id, face_data)
        print("✓ 保存人脸成功")
        
        # 测试保存分析记录
        record_data = {
            'session_id': session_id,
            'record_name': '测试分析记录',
            'timestamp': datetime.now(),
            'total_people': 1,
            'active_tracks': 1,
            'avg_age': 25.5,
            'male_count': 1,
            'female_count': 0,
            'avg_dwell_time': 45.0,
            'engagement_score': 0.75,
            'shopper_count': 0,
            'browser_count': 1,
            'zone_data': {'zone1': {'count': 1}},
            'additional_data': {'frame_rate': 25}
        }
        record_id = db.save_analysis_record(record_data)
        print(f"✓ 保存分析记录成功 (ID: {record_id})")
        
        return session_id, person_id, record_id
        
    except Exception as e:
        print(f"✗ 基本操作测试失败: {e}")
        return None, None, None

def test_query_operations(db, session_id, person_id, record_id):
    """测试查询操作"""
    try:
        print("\n=== 测试查询操作 ===")
        
        # 测试获取会话列表
        sessions = db.get_sessions()
        print(f"✓ 获取会话列表成功，数量: {len(sessions)}")
        
        # 测试获取会话人员
        persons = db.get_session_persons(session_id)
        print(f"✓ 获取会话人员成功，数量: {len(persons)}")
        
        # 测试获取人员位置
        positions = db.get_person_positions(person_id)
        print(f"✓ 获取人员位置成功，数量: {len(positions)}")
        
        # 测试获取人员人脸
        faces = db.get_person_faces(person_id)
        print(f"✓ 获取人员人脸成功，数量: {len(faces)}")
        
        # 测试获取分析记录
        records = db.get_analysis_records(session_id)
        print(f"✓ 获取分析记录成功，数量: {len(records)}")
        
        # 测试获取单个分析记录
        record = db.get_analysis_record(record_id)
        if record:
            print(f"✓ 获取单个分析记录成功: {record['record_name']}")
        
        # 测试获取会话统计
        stats = db.get_session_statistics(session_id)
        print(f"✓ 获取会话统计成功")
        
        # 测试获取所有分析记录
        all_records = db.get_all_analysis_records(limit=10)
        print(f"✓ 获取所有分析记录成功，数量: {len(all_records)}")
        
        return True
        
    except Exception as e:
        print(f"✗ 查询操作测试失败: {e}")
        return False

def test_persistent_analyzer():
    """测试持久化分析器"""
    try:
        print("\n=== 测试持久化分析器 ===")
        
        from src.persistent_analyzer import PersistentAnalyzer
        import numpy as np
        
        # 创建持久化分析器
        analyzer = PersistentAnalyzer(
            session_name="测试持久化分析器",
            use_insightface=False,  # 使用基础模式避免依赖问题
            save_interval=5,
            record_interval=10
        )
        print("✓ 持久化分析器创建成功")
        
        # 创建测试图像
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # 处理测试帧
        tracks, faces, profiles = analyzer.process_frame(test_frame)
        print(f"✓ 处理测试帧成功 - 轨迹: {len(tracks)}, 人脸: {len(faces)}, 档案: {len(profiles)}")
        
        # 获取实时统计
        stats = analyzer.get_realtime_statistics()
        print(f"✓ 获取实时统计成功: {stats}")
        
        # 关闭分析器
        analyzer.close()
        print("✓ 持久化分析器关闭成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 持久化分析器测试失败: {e}")
        return False

def main():
    """主函数"""
    print("开始MySQL数据库测试...")
    
    # 测试数据库连接
    db = test_database_connection()
    if not db:
        print("数据库连接失败，测试终止")
        return
    
    # 测试基本操作
    session_id, person_id, record_id = test_basic_operations(db)
    if session_id is None:
        print("基本操作测试失败，测试终止")
        return
    
    # 测试查询操作
    if not test_query_operations(db, session_id, person_id, record_id):
        print("查询操作测试失败")
        return
    
    # 测试持久化分析器
    if not test_persistent_analyzer():
        print("持久化分析器测试失败")
        return
    
    print("\n=== 所有测试完成 ===")
    print("✓ MySQL数据库功能正常")
    print("现在可以运行Web应用程序了")

if __name__ == "__main__":
    main() 