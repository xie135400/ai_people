#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试InsightFace人脸识别功能
"""

import cv2
import numpy as np
from src.face_analyzer import FaceAnalyzer
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_insightface_with_image():
    """使用测试图像测试InsightFace功能"""
    try:
        # 创建InsightFace分析器
        print("正在初始化InsightFace分析器...")
        analyzer = FaceAnalyzer(use_insightface=True)
        print("InsightFace分析器初始化成功！")
        
        # 创建一个测试图像（纯色背景）
        test_image = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        # 在图像上绘制一些文本
        cv2.putText(test_image, "InsightFace Test", (200, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 检测人脸（这个测试图像中没有人脸，但可以验证功能正常）
        faces = analyzer.detect_faces(test_image)
        print(f"检测到 {len(faces)} 个人脸")
        
        # 测试统计功能
        stats = analyzer.get_age_statistics()
        print("年龄统计信息:", stats)
        
        print("InsightFace功能测试完成！")
        return True
        
    except Exception as e:
        print(f"InsightFace测试失败: {e}")
        return False

def test_opencv_fallback():
    """测试OpenCV备选方案"""
    try:
        print("正在测试OpenCV备选方案...")
        analyzer = FaceAnalyzer(use_insightface=False)
        print("OpenCV分析器初始化成功！")
        
        # 创建测试图像
        test_image = np.ones((480, 640, 3), dtype=np.uint8) * 128
        cv2.putText(test_image, "OpenCV Test", (200, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 检测人脸
        faces = analyzer.detect_faces(test_image)
        print(f"检测到 {len(faces)} 个人脸")
        
        print("OpenCV备选方案测试完成！")
        return True
        
    except Exception as e:
        print(f"OpenCV测试失败: {e}")
        return False

def compare_performance():
    """比较InsightFace和OpenCV的性能"""
    print("\n=== 性能比较 ===")
    
    # 创建测试图像
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # 测试InsightFace
    try:
        import time
        analyzer_insight = FaceAnalyzer(use_insightface=True)
        
        start_time = time.time()
        faces_insight = analyzer_insight.detect_faces(test_image)
        insight_time = time.time() - start_time
        
        print(f"InsightFace: {len(faces_insight)} 个人脸, 耗时: {insight_time:.3f}秒")
    except Exception as e:
        print(f"InsightFace性能测试失败: {e}")
    
    # 测试OpenCV
    try:
        analyzer_opencv = FaceAnalyzer(use_insightface=False)
        
        start_time = time.time()
        faces_opencv = analyzer_opencv.detect_faces(test_image)
        opencv_time = time.time() - start_time
        
        print(f"OpenCV: {len(faces_opencv)} 个人脸, 耗时: {opencv_time:.3f}秒")
    except Exception as e:
        print(f"OpenCV性能测试失败: {e}")

def main():
    """主测试函数"""
    print("=== InsightFace 功能测试 ===")
    
    # 测试InsightFace
    insightface_success = test_insightface_with_image()
    
    # 测试OpenCV备选方案
    opencv_success = test_opencv_fallback()
    
    # 性能比较
    if insightface_success:
        compare_performance()
    
    # 总结
    print("\n=== 测试总结 ===")
    print(f"InsightFace: {'✅ 可用' if insightface_success else '❌ 不可用'}")
    print(f"OpenCV: {'✅ 可用' if opencv_success else '❌ 不可用'}")
    
    if insightface_success:
        print("\n🎉 恭喜！InsightFace已成功安装并可以正常使用！")
        print("现在你可以享受更高精度的人脸识别功能了。")
    elif opencv_success:
        print("\n⚠️  InsightFace不可用，但OpenCV备选方案正常工作。")
        print("建议参考requirements.txt中的安装说明重新安装InsightFace。")
    else:
        print("\n❌ 所有人脸识别方案都不可用，请检查安装。")

if __name__ == "__main__":
    main() 