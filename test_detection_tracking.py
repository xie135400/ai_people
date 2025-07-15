#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测和跟踪功能测试脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import cv2
import logging
from src.detector import PersonDetector
from src.tracker import PersonTracker

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_detection_only():
    """仅测试人员检测"""
    logger.info("=== 测试人员检测功能 ===")
    
    detector = PersonDetector()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    logger.info("开始人员检测测试，按 'q' 退出")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 检测人员
        detections = detector.detect_persons(frame)
        
        # 绘制检测结果
        result_frame = detector.draw_detections(frame, detections)
        
        # 显示检测数量
        cv2.putText(result_frame, f'Detected: {len(detections)}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('Person Detection Test', result_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

def test_detection_and_tracking():
    """测试人员检测和跟踪"""
    logger.info("=== 测试人员检测和跟踪功能 ===")
    
    # 初始化检测器和跟踪器
    detector = PersonDetector()
    tracker = PersonTracker()
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    logger.info("开始人员检测和跟踪测试，按 'q' 退出")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # 检测人员
        detections = detector.detect_persons(frame)
        
        # 更新跟踪
        tracks = tracker.update(detections, frame)
        
        # 绘制跟踪结果
        result_frame = tracker.draw_tracks(frame, tracks, show_path=True)
        
        # 显示统计信息
        stats = tracker.get_statistics()
        info_lines = [
            f'Frame: {frame_count}',
            f'Detections: {len(detections)}',
            f'Active Tracks: {stats["active_tracks"]}',
            f'Total Tracks: {stats["total_tracks"]}'
        ]
        
        for i, line in enumerate(info_lines):
            cv2.putText(result_frame, line, (10, 30 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imshow('Person Detection and Tracking Test', result_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # 输出最终统计
    final_stats = tracker.get_statistics()
    logger.info(f"测试完成 - 总帧数: {frame_count}, 总轨迹数: {final_stats['total_tracks']}")

def main():
    """主函数"""
    print("选择测试模式:")
    print("1. 仅测试人员检测")
    print("2. 测试人员检测和跟踪")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == '1':
        test_detection_only()
    elif choice == '2':
        test_detection_and_tracking()
    else:
        print("无效选择，默认运行检测和跟踪测试")
        test_detection_and_tracking()

if __name__ == "__main__":
    main() 