#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InsightFace 使用示例
展示如何在项目中使用InsightFace进行人脸识别
"""

import cv2
import numpy as np
from src.face_analyzer import FaceAnalyzer

def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 创建分析器（自动选择最佳方案）
    try:
        # 优先使用InsightFace
        analyzer = FaceAnalyzer(use_insightface=True)
        print("✅ 使用InsightFace（高精度模式）")
    except:
        # 降级到OpenCV
        analyzer = FaceAnalyzer(use_insightface=False)
        print("⚠️ 降级到OpenCV（兼容模式）")
    
    # 创建测试图像
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # 检测人脸
    faces = analyzer.detect_faces(test_image)
    print(f"检测到 {len(faces)} 个人脸")
    
    # 显示人脸信息
    for i, face in enumerate(faces):
        print(f"人脸 {i+1}:")
        print(f"  位置: {face.bbox}")
        print(f"  年龄: {face.age} (置信度: {face.age_confidence:.2f})")
        print(f"  性别: {face.gender} (置信度: {face.gender_confidence:.2f})")
        print(f"  质量: {face.face_quality:.2f}")

def example_with_tracking():
    """结合人员跟踪的示例"""
    print("\n=== 结合跟踪的示例 ===")
    
    analyzer = FaceAnalyzer(use_insightface=True)
    
    # 模拟跟踪数据
    mock_tracks = {
        1: type('Track', (), {'bbox': (100, 100, 200, 200)})(),
        2: type('Track', (), {'bbox': (300, 150, 400, 250)})(),
    }
    
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # 检测人脸并关联跟踪
    faces = analyzer.detect_faces_with_tracking(test_image, mock_tracks)
    
    print(f"检测到 {len(faces)} 个人脸（已关联跟踪）")
    
    # 获取统计信息
    stats = analyzer.get_age_statistics()
    print("年龄统计:", stats)

def example_comparison():
    """对比不同方案的示例"""
    print("\n=== 方案对比示例 ===")
    
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # InsightFace方案
    try:
        analyzer_insight = FaceAnalyzer(use_insightface=True)
        faces_insight = analyzer_insight.detect_faces(test_image)
        print(f"InsightFace: 检测到 {len(faces_insight)} 个人脸")
    except Exception as e:
        print(f"InsightFace不可用: {e}")
    
    # OpenCV方案
    analyzer_opencv = FaceAnalyzer(use_insightface=False)
    faces_opencv = analyzer_opencv.detect_faces(test_image)
    print(f"OpenCV: 检测到 {len(faces_opencv)} 个人脸")

def example_real_time():
    """实时处理示例（模拟）"""
    print("\n=== 实时处理示例 ===")
    
    analyzer = FaceAnalyzer(use_insightface=True)
    
    # 模拟视频帧处理
    for frame_id in range(5):
        # 创建模拟帧
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # 检测人脸
        faces = analyzer.detect_faces(frame)
        
        # 绘制结果
        result_frame = analyzer.draw_faces(frame, faces)
        
        print(f"帧 {frame_id}: 检测到 {len(faces)} 个人脸")
        
        # 在实际应用中，这里会显示或保存结果
        # cv2.imshow('Result', result_frame)

def main():
    """主函数"""
    print("🎯 InsightFace 使用示例")
    print("=" * 50)
    
    # 基础使用
    example_basic_usage()
    
    # 结合跟踪
    example_with_tracking()
    
    # 方案对比
    example_comparison()
    
    # 实时处理
    example_real_time()
    
    print("\n" + "=" * 50)
    print("✅ 示例运行完成！")
    print("\n💡 使用建议:")
    print("1. 优先使用InsightFace获得更高精度")
    print("2. 在性能要求高的场景可以使用OpenCV")
    print("3. 项目会自动处理降级，无需担心兼容性")

if __name__ == "__main__":
    main() 