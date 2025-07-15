#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人脸分析和集成功能测试脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import cv2
import logging
from src.face_analyzer import FaceAnalyzer
from src.integrated_analyzer import IntegratedAnalyzer

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_face_analysis_only():
    """仅测试人脸分析"""
    logger.info("=== 测试人脸分析功能 ===")
    
    # 尝试使用InsightFace，失败则使用OpenCV
    analyzer = FaceAnalyzer(use_insightface=True)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    logger.info("开始人脸分析测试，按 'q' 退出")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 检测人脸
        faces = analyzer.detect_faces(frame)
        
        # 绘制结果
        result_frame = analyzer.draw_faces(frame, faces)
        
        # 显示统计信息
        cv2.putText(result_frame, f'Faces: {len(faces)}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # 显示详细信息
        for i, face in enumerate(faces):
            info = f"Face {i+1}: "
            if face.age is not None:
                info += f"Age {face.age}, "
            if face.gender is not None:
                info += f"Gender {face.gender}"
            
            cv2.putText(result_frame, info, (10, 60 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        cv2.imshow('Face Analysis Test', result_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

def test_integrated_analysis():
    """测试集成分析功能"""
    logger.info("=== 测试集成分析功能 ===")
    
    # 初始化集成分析器
    analyzer = IntegratedAnalyzer(use_insightface=True)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    logger.info("开始集成分析测试，按 'q' 退出")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 处理帧
        tracks, faces, profiles = analyzer.process_frame(frame)
        
        # 绘制结果
        result_frame = analyzer.draw_integrated_results(frame, tracks, faces)
        
        # 显示统计信息
        stats = analyzer.get_statistics()
        info_lines = [
            f"Frame: {stats['frame_count']}",
            f"Total People: {stats['total_people']}",
            f"Active Tracks: {stats['active_tracks']}",
            f"Avg Age: {stats['avg_age']:.1f}" if stats['avg_age'] else "Avg Age: N/A",
            f"Male: {stats['male_count']}, Female: {stats['female_count']}"
        ]
        
        for i, line in enumerate(info_lines):
            cv2.putText(result_frame, line, (10, 30 + i * 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imshow('Integrated Analysis Test', result_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # 输出最终统计
    final_stats = analyzer.get_statistics()
    logger.info(f"测试完成:")
    logger.info(f"  总人数: {final_stats['total_people']}")
    logger.info(f"  平均年龄: {final_stats['avg_age']:.1f}" if final_stats['avg_age'] else "  平均年龄: N/A")
    logger.info(f"  男性: {final_stats['male_count']}, 女性: {final_stats['female_count']}")
    logger.info(f"  总帧数: {final_stats['frame_count']}")

def main():
    """主函数"""
    print("选择测试模式:")
    print("1. 仅测试人脸分析")
    print("2. 测试集成分析（人员跟踪 + 人脸分析）")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == '1':
        test_face_analysis_only()
    elif choice == '2':
        test_integrated_analysis()
    else:
        print("无效选择，默认运行集成分析测试")
        test_integrated_analysis()

if __name__ == "__main__":
    main() 