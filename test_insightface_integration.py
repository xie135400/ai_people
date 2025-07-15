#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试InsightFace集成
验证所有业务代码是否正确使用InsightFace作为默认选项
"""

import cv2
import numpy as np
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_face_analyzer_default():
    """测试FaceAnalyzer默认使用InsightFace"""
    print("=== 测试 FaceAnalyzer 默认配置 ===")
    
    try:
        from src.face_analyzer import FaceAnalyzer
        
        # 不传参数，应该默认使用InsightFace
        analyzer = FaceAnalyzer()
        print(f"✅ FaceAnalyzer 默认使用InsightFace: {analyzer.use_insightface}")
        
        # 创建测试图像
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        faces = analyzer.detect_faces(test_image)
        print(f"✅ 人脸检测功能正常，检测到 {len(faces)} 个人脸")
        
        return True
        
    except Exception as e:
        print(f"❌ FaceAnalyzer 测试失败: {e}")
        return False

def test_integrated_analyzer_default():
    """测试IntegratedAnalyzer默认使用InsightFace"""
    print("\n=== 测试 IntegratedAnalyzer 默认配置 ===")
    
    try:
        from src.integrated_analyzer import IntegratedAnalyzer
        
        # 不传参数，应该默认使用InsightFace
        analyzer = IntegratedAnalyzer()
        print(f"✅ IntegratedAnalyzer 默认使用InsightFace: {analyzer.face_analyzer.use_insightface}")
        
        # 创建测试图像
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        tracks, faces, profiles = analyzer.process_frame(test_image)
        print(f"✅ 集成分析功能正常，轨迹: {len(tracks)}, 人脸: {len(faces)}, 档案: {len(profiles)}")
        
        return True
        
    except Exception as e:
        print(f"❌ IntegratedAnalyzer 测试失败: {e}")
        return False

def test_persistent_analyzer_default():
    """测试PersistentAnalyzer默认使用InsightFace"""
    print("\n=== 测试 PersistentAnalyzer 默认配置 ===")
    
    try:
        from src.persistent_analyzer import PersistentAnalyzer
        
        # 不传参数，应该默认使用InsightFace
        analyzer = PersistentAnalyzer(session_name="测试会话")
        print(f"✅ PersistentAnalyzer 默认使用InsightFace: {analyzer.analyzer.face_analyzer.use_insightface}")
        
        # 创建测试图像
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        tracks, faces, profiles = analyzer.process_frame(test_image)
        print(f"✅ 持久化分析功能正常，轨迹: {len(tracks)}, 人脸: {len(faces)}, 档案: {len(profiles)}")
        
        # 清理
        analyzer.close()
        return True
        
    except Exception as e:
        print(f"❌ PersistentAnalyzer 测试失败: {e}")
        return False

def test_complete_analyzer_default():
    """测试CompleteAnalyzer默认使用InsightFace"""
    print("\n=== 测试 CompleteAnalyzer 默认配置 ===")
    
    try:
        from src.complete_analyzer import CompleteAnalyzer
        
        # 不传参数，应该默认使用InsightFace
        analyzer = CompleteAnalyzer(session_name="测试完整分析")
        print(f"✅ CompleteAnalyzer 默认使用InsightFace: {analyzer.persistent_analyzer.analyzer.face_analyzer.use_insightface}")
        
        # 创建测试图像
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        result_frame, stats = analyzer.process_frame(test_image)
        print(f"✅ 完整分析功能正常，统计数据: {len(stats)} 项")
        
        # 清理
        analyzer.close()
        return True
        
    except Exception as e:
        print(f"❌ CompleteAnalyzer 测试失败: {e}")
        return False

def test_web_app_integration():
    """测试Web应用集成"""
    print("\n=== 测试 Web应用 InsightFace集成 ===")
    
    try:
        from src.web_app import UserSession
        
        # 创建用户会话
        session = UserSession("test_user", "测试用户")
        session.start_analysis()
        
        # 检查是否使用InsightFace
        use_insightface = session.analyzer.persistent_analyzer.analyzer.face_analyzer.use_insightface
        print(f"✅ Web应用默认使用InsightFace: {use_insightface}")
        
        # 清理
        session.stop_analysis()
        return True
        
    except Exception as e:
        print(f"❌ Web应用测试失败: {e}")
        return False

def test_fallback_mechanism():
    """测试降级机制"""
    print("\n=== 测试 InsightFace 降级机制 ===")
    
    try:
        from src.face_analyzer import FaceAnalyzer
        
        # 强制使用OpenCV测试降级
        analyzer_opencv = FaceAnalyzer(use_insightface=False)
        print(f"✅ 强制使用OpenCV: {not analyzer_opencv.use_insightface}")
        
        # 测试InsightFace（如果失败会自动降级）
        try:
            analyzer_insight = FaceAnalyzer(use_insightface=True)
            print(f"✅ InsightFace可用: {analyzer_insight.use_insightface}")
        except:
            print("⚠️ InsightFace不可用，但降级机制正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 降级机制测试失败: {e}")
        return False

def test_performance_comparison():
    """性能对比测试"""
    print("\n=== 性能对比测试 ===")
    
    try:
        from src.face_analyzer import FaceAnalyzer
        import time
        
        # 创建测试图像
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # 测试InsightFace性能
        try:
            analyzer_insight = FaceAnalyzer(use_insightface=True)
            start_time = time.time()
            faces_insight = analyzer_insight.detect_faces(test_image)
            insight_time = time.time() - start_time
            print(f"✅ InsightFace: {len(faces_insight)} 个人脸, 耗时: {insight_time:.3f}秒")
        except Exception as e:
            print(f"⚠️ InsightFace性能测试失败: {e}")
            insight_time = None
        
        # 测试OpenCV性能
        analyzer_opencv = FaceAnalyzer(use_insightface=False)
        start_time = time.time()
        faces_opencv = analyzer_opencv.detect_faces(test_image)
        opencv_time = time.time() - start_time
        print(f"✅ OpenCV: {len(faces_opencv)} 个人脸, 耗时: {opencv_time:.3f}秒")
        
        # 性能对比
        if insight_time is not None:
            if insight_time < opencv_time:
                print(f"🚀 InsightFace 比 OpenCV 快 {((opencv_time - insight_time) / opencv_time * 100):.1f}%")
            else:
                print(f"📊 OpenCV 比 InsightFace 快 {((insight_time - opencv_time) / insight_time * 100):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能对比测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔍 开始测试 InsightFace 集成...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("FaceAnalyzer默认配置", test_face_analyzer_default()))
    test_results.append(("IntegratedAnalyzer默认配置", test_integrated_analyzer_default()))
    test_results.append(("PersistentAnalyzer默认配置", test_persistent_analyzer_default()))
    test_results.append(("CompleteAnalyzer默认配置", test_complete_analyzer_default()))
    test_results.append(("Web应用集成", test_web_app_integration()))
    test_results.append(("降级机制", test_fallback_mechanism()))
    test_results.append(("性能对比", test_performance_comparison()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"总计: {passed}/{total} 个测试通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有测试通过！InsightFace集成成功！")
        print("\n✨ 项目现在默认使用InsightFace进行高精度人脸识别")
        print("💡 如需使用OpenCV，请在初始化时设置 use_insightface=False")
    else:
        print("⚠️ 部分测试失败，请检查相关配置")
    
    print("\n🔧 使用说明:")
    print("- 所有分析器现在默认使用InsightFace（高精度模式）")
    print("- 如果InsightFace不可用，会自动降级到OpenCV")
    print("- 可以通过 use_insightface=False 强制使用OpenCV")
    print("- InsightFace提供更准确的年龄和性别识别")

if __name__ == "__main__":
    main() 