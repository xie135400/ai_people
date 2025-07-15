#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
年龄识别准确度测试脚本
"""

import cv2
import numpy as np
import time
from src.integrated_analyzer import IntegratedAnalyzer
from src.age_config import get_age_config

def test_age_accuracy():
    """测试年龄识别准确度"""
    print("🎯 年龄识别准确度测试")
    print("=" * 50)
    
    # 初始化分析器
    analyzer = IntegratedAnalyzer(use_insightface=True)
    config = get_age_config()
    
    print(f"配置信息:")
    print(f"- JPEG质量范围: {config['min_jpeg_quality']}-{config['max_jpeg_quality']}")
    print(f"- 分辨率缩放范围: {config['min_scale']}-{config['max_scale']}")
    print(f"- 人脸检测间隔: {config['face_detection_interval']}帧")
    print(f"- 年龄历史长度: {config['age_history_length']}")
    print()
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return
    
    print("📹 摄像头已启动，开始测试...")
    print("按 'q' 退出测试")
    print()
    
    frame_count = 0
    age_predictions = []
    processing_times = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        start_time = time.time()
        
        # 处理帧
        tracks, faces, profiles = analyzer.process_frame(frame)
        
        processing_time = time.time() - start_time
        processing_times.append(processing_time)
        
        # 绘制结果
        result_frame = analyzer.draw_integrated_results(frame, tracks, faces)
        
        # 收集年龄预测数据
        for face in faces:
            if face.age is not None:
                age_predictions.append({
                    'age': face.age,
                    'confidence': face.age_confidence or 0.5,
                    'quality': face.face_quality or 0.5,
                    'frame': frame_count
                })
        
        # 显示统计信息
        stats = analyzer.get_statistics(tracks)
        
        # 计算平均处理时间
        avg_processing_time = np.mean(processing_times[-30:]) if processing_times else 0
        
        info_lines = [
            f"帧数: {frame_count}",
            f"当前人数: {stats['active_tracks']}",
            f"总检测人数: {stats['total_people']}",
            f"平均年龄: {stats['avg_age']:.1f}" if stats['avg_age'] else "平均年龄: N/A",
            f"处理时间: {processing_time*1000:.1f}ms",
            f"平均处理时间: {avg_processing_time*1000:.1f}ms",
            f"年龄预测数: {len(age_predictions)}"
        ]
        
        # 显示配置状态
        if hasattr(analyzer, '_adaptive_mode'):
            info_lines.append(f"自适应模式: {'开启' if analyzer._adaptive_mode else '关闭'}")
            info_lines.append(f"检测间隔: {analyzer.face_detection_interval}帧")
        
        for i, line in enumerate(info_lines):
            cv2.putText(result_frame, line, (10, 30 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # 显示年龄预测质量统计
        if age_predictions:
            recent_predictions = age_predictions[-10:]  # 最近10个预测
            avg_confidence = np.mean([p['confidence'] for p in recent_predictions])
            avg_quality = np.mean([p['quality'] for p in recent_predictions])
            
            quality_lines = [
                f"最近预测置信度: {avg_confidence:.3f}",
                f"最近预测质量: {avg_quality:.3f}"
            ]
            
            for i, line in enumerate(quality_lines):
                cv2.putText(result_frame, line, (10, 300 + i * 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        cv2.imshow('Age Recognition Accuracy Test', result_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果统计")
    print("=" * 50)
    
    if age_predictions:
        confidences = [p['confidence'] for p in age_predictions]
        qualities = [p['quality'] for p in age_predictions]
        
        print(f"总年龄预测数: {len(age_predictions)}")
        print(f"平均置信度: {np.mean(confidences):.3f}")
        print(f"平均质量分: {np.mean(qualities):.3f}")
        print(f"高置信度预测比例: {len([c for c in confidences if c > 0.7]) / len(confidences) * 100:.1f}%")
        print(f"高质量预测比例: {len([q for q in qualities if q > 0.7]) / len(qualities) * 100:.1f}%")
    
    if processing_times:
        print(f"平均处理时间: {np.mean(processing_times)*1000:.1f}ms")
        print(f"最大处理时间: {np.max(processing_times)*1000:.1f}ms")
        print(f"处理时间标准差: {np.std(processing_times)*1000:.1f}ms")
    
    print(f"总处理帧数: {frame_count}")
    
    final_stats = analyzer.get_statistics()
    print(f"最终统计 - 总人数: {final_stats['total_people']}, 平均年龄: {final_stats['avg_age']}")

if __name__ == "__main__":
    test_age_accuracy()
