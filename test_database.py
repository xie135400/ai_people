#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库和持久化功能测试脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import cv2
import logging
from datetime import datetime
from src.database import DatabaseManager
from src.persistent_analyzer import PersistentAnalyzer

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_only():
    """仅测试数据库功能"""
    logger.info("=== 测试数据库功能 ===")
    
    # 创建测试数据库
    db = DatabaseManager("data/test_analytics.db")
    
    try:
        # 创建测试会话
        session_id = db.create_session("数据库测试会话")
        print(f"✅ 创建会话: {session_id}")
        
        # 保存测试人员数据
        person_data = {
            'track_id': 1,
            'first_seen': datetime.now(),
            'last_seen': datetime.now(),
            'total_frames': 150,
            'faces_detected': 8,
            'avg_age': 28.5,
            'dominant_gender': 'Female',
            'gender_confidence': 0.85
        }
        
        person_id = db.save_person(session_id, person_data)
        print(f"✅ 保存人员: {person_id}")
        
        # 保存多个位置信息
        positions = [(100, 200), (110, 205), (120, 210), (130, 215)]
        for i, (x, y) in enumerate(positions):
            db.save_position(person_id, x, y, datetime.now(), i+1)
        print(f"✅ 保存位置信息: {len(positions)} 个点")
        
        # 保存多个人脸信息
        faces = [
            {'age': 28, 'gender': 'Female', 'gender_confidence': 0.9, 
             'bbox': (50, 50, 150, 150), 'confidence': 0.95},
            {'age': 29, 'gender': 'Female', 'gender_confidence': 0.8, 
             'bbox': (55, 55, 155, 155), 'confidence': 0.88}
        ]
        
        for face_data in faces:
            face_data['timestamp'] = datetime.now()
            db.save_face(person_id, face_data)
        print(f"✅ 保存人脸信息: {len(faces)} 个人脸")
        
        # 添加第二个人员
        person_data2 = {
            'track_id': 2,
            'first_seen': datetime.now(),
            'last_seen': datetime.now(),
            'total_frames': 80,
            'faces_detected': 3,
            'avg_age': 35.0,
            'dominant_gender': 'Male',
            'gender_confidence': 0.75
        }
        
        person_id2 = db.save_person(session_id, person_data2)
        print(f"✅ 保存第二个人员: {person_id2}")
        
        # 获取会话统计信息
        stats = db.get_session_statistics(session_id)
        print(f"✅ 会话统计:")
        print(f"   总人数: {stats.get('total_people', 0)}")
        print(f"   平均年龄: {stats.get('avg_age', 'N/A')}")
        print(f"   男性: {stats.get('male_count', 0)}, 女性: {stats.get('female_count', 0)}")
        print(f"   总帧数: {stats.get('total_frames', 0)}")
        print(f"   总人脸: {stats.get('total_faces', 0)}")
        print(f"   年龄分布: {stats.get('age_distribution', {})}")
        
        # 结束会话
        db.end_session(session_id, {
            'total_people': 2,
            'frame_count': 230,
            'avg_age': 31.75,
            'male_count': 1,
            'female_count': 1
        })
        print("✅ 会话结束")
        
        # 获取会话列表
        sessions = db.get_sessions()
        print(f"✅ 会话列表: {len(sessions)} 个会话")
        for session in sessions[:3]:  # 显示前3个
            print(f"   会话 {session['id']}: {session['session_name']} "
                  f"({session['start_time']} - {session.get('end_time', '进行中')})")
        
        # 获取人员详细信息
        persons = db.get_session_persons(session_id)
        print(f"✅ 人员详细信息: {len(persons)} 个人员")
        for person in persons:
            print(f"   人员 {person['id']}: 轨迹ID={person['track_id']}, "
                  f"年龄={person['avg_age']}, 性别={person['dominant_gender']}")
            
            # 获取位置轨迹
            positions = db.get_person_positions(person['id'])
            print(f"     位置记录: {len(positions)} 个点")
            
            # 获取人脸记录
            faces = db.get_person_faces(person['id'])
            print(f"     人脸记录: {len(faces)} 个人脸")
        
    except Exception as e:
        logger.error(f"数据库测试失败: {e}")
        
    finally:
        db.close()

def test_persistent_analyzer():
    """测试持久化分析器"""
    logger.info("=== 测试持久化分析器 ===")
    
    # 初始化持久化分析器
    analyzer = PersistentAnalyzer(
        session_name="持久化分析测试",
        use_insightface=True,
        save_interval=5  # 每5秒保存一次（测试用）
    )
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    logger.info("开始测试持久化分析")
    logger.info("按键说明:")
    logger.info("  'q' - 退出")
    logger.info("  's' - 立即保存数据")
    logger.info("  'i' - 显示数据库统计信息")
    
    try:
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 处理帧
            tracks, faces, profiles = analyzer.process_frame(frame)
            
            # 绘制结果
            result_frame = analyzer.draw_results(frame, tracks, faces)
            
            # 显示实时统计信息
            realtime_stats = analyzer.get_realtime_statistics()
            info_lines = [
                f"Frame: {realtime_stats['frame_count']}",
                f"Total People: {realtime_stats['total_people']}",
                f"Active: {realtime_stats['active_tracks']}",
                f"Avg Age: {realtime_stats['avg_age']:.1f}" if realtime_stats['avg_age'] else "Avg Age: N/A",
                f"Male: {realtime_stats['male_count']}, Female: {realtime_stats['female_count']}"
            ]
            
            for i, line in enumerate(info_lines):
                cv2.putText(result_frame, line, (10, 30 + i * 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # 显示保存状态
            save_status = f"Next save in: {analyzer.save_interval - (analyzer.analyzer.frame_count % analyzer.save_interval)}s"
            cv2.putText(result_frame, save_status, (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
            
            cv2.imshow('Persistent Analysis Test', result_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 立即保存数据
                analyzer.save_current_frame_data(tracks, faces)
                logger.info("✅ 手动保存数据完成")
            elif key == ord('i'):
                # 显示数据库统计信息
                try:
                    db_stats = analyzer.get_session_statistics()
                    logger.info("=== 当前数据库统计 ===")
                    logger.info(f"总人数: {db_stats.get('total_people', 0)}")
                    logger.info(f"平均年龄: {db_stats.get('avg_age', 'N/A')}")
                    logger.info(f"男性: {db_stats.get('male_count', 0)}, 女性: {db_stats.get('female_count', 0)}")
                    logger.info(f"总帧数: {db_stats.get('total_frames', 0)}")
                    logger.info(f"总人脸: {db_stats.get('total_faces', 0)}")
                except Exception as e:
                    logger.error(f"获取数据库统计失败: {e}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        # 获取最终的数据库统计
        try:
            db_stats = analyzer.get_session_statistics()
            logger.info("=== 最终数据库统计信息 ===")
            logger.info(f"总人数: {db_stats.get('total_people', 0)}")
            logger.info(f"平均年龄: {db_stats.get('avg_age', 'N/A')}")
            logger.info(f"男性: {db_stats.get('male_count', 0)}, 女性: {db_stats.get('female_count', 0)}")
            logger.info(f"总帧数: {db_stats.get('total_frames', 0)}")
            logger.info(f"总人脸: {db_stats.get('total_faces', 0)}")
            logger.info(f"年龄分布: {db_stats.get('age_distribution', {})}")
        except Exception as e:
            logger.error(f"获取最终统计失败: {e}")
        
        # 关闭分析器
        analyzer.close()

def main():
    """主函数"""
    print("选择测试模式:")
    print("1. 仅测试数据库功能")
    print("2. 测试持久化分析器（摄像头 + 数据库）")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == '1':
        test_database_only()
    elif choice == '2':
        test_persistent_analyzer()
    else:
        print("无效选择，默认运行数据库测试")
        test_database_only()

if __name__ == "__main__":
    main() 