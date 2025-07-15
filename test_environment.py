#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境依赖测试脚本
测试所有核心依赖是否安装成功
"""

def test_imports():
    """测试导入所有核心依赖"""
    print("=== 测试依赖导入 ===")
    
    try:
        import torch
        print(f"✅ torch: {torch.__version__}")
    except ImportError as e:
        print(f"❌ torch导入失败: {e}")
        return False
    
    try:
        import torchvision
        print(f"✅ torchvision: {torchvision.__version__}")
    except ImportError as e:
        print(f"❌ torchvision导入失败: {e}")
        return False
    
    try:
        import cv2
        print(f"✅ opencv-python: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ opencv-python导入失败: {e}")
        return False
    
    try:
        import ultralytics
        print(f"✅ ultralytics: {ultralytics.__version__}")
    except ImportError as e:
        print(f"❌ ultralytics导入失败: {e}")
        return False
    
    try:
        import fastapi
        print(f"✅ fastapi: {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ fastapi导入失败: {e}")
        return False
    
    try:
        from deep_sort_realtime.deepsort_tracker import DeepSort
        print("✅ deep_sort_realtime: 导入成功")
    except ImportError as e:
        print(f"❌ deep_sort_realtime导入失败: {e}")
        return False, None
    
    # 测试人脸识别库
    try:
        import insightface
        print(f"✅ insightface: {insightface.__version__}")
        face_lib = "insightface"
    except ImportError as e:
        print(f"⚠️ insightface导入失败: {e}")
        print("   将使用opencv人脸检测作为替代方案")
        # 测试opencv人脸检测
        try:
            import cv2
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            print("✅ opencv人脸检测: 可用")
            face_lib = "opencv"
        except Exception as e:
            print(f"❌ opencv人脸检测也失败: {e}")
            face_lib = None
    
    try:
        import numpy as np
        print(f"✅ numpy: {np.__version__}")
    except ImportError as e:
        print(f"❌ numpy导入失败: {e}")
        return False
    
    try:
        import pandas as pd
        print(f"✅ pandas: {pd.__version__}")
    except ImportError as e:
        print(f"❌ pandas导入失败: {e}")
        return False
    
    return True, face_lib

def test_gpu():
    """测试GPU可用性"""
    print("\n=== 测试GPU可用性 ===")
    
    import torch
    
    if torch.cuda.is_available():
        print(f"✅ CUDA可用")
        print(f"✅ GPU数量: {torch.cuda.device_count()}")
        print(f"✅ 当前GPU: {torch.cuda.get_device_name(0)}")
        print(f"✅ CUDA版本: {torch.version.cuda}")
        
        # 测试简单的GPU运算
        try:
            x = torch.randn(3, 3).cuda()
            y = torch.randn(3, 3).cuda()
            z = torch.mm(x, y)
            print("✅ GPU计算测试成功")
            return True
        except Exception as e:
            print(f"❌ GPU计算测试失败: {e}")
            return False
    else:
        print("❌ CUDA不可用，将使用CPU")
        return False

def test_camera():
    """测试摄像头可用性"""
    print("\n=== 测试摄像头可用性 ===")
    
    import cv2
    
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ 摄像头可用，图像尺寸: {frame.shape}")
                cap.release()
                return True
            else:
                print("❌ 摄像头无法读取图像")
                cap.release()
                return False
        else:
            print("❌ 无法打开摄像头")
            return False
    except Exception as e:
        print(f"❌ 摄像头测试失败: {e}")
        return False

def test_yolo():
    """测试YOLO模型加载"""
    print("\n=== 测试YOLO模型 ===")
    
    try:
        from ultralytics import YOLO
        
        # 加载预训练模型（会自动下载）
        model = YOLO('yolov8n.pt')
        print("✅ YOLO模型加载成功")
        return True
    except Exception as e:
        print(f"❌ YOLO模型加载失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始环境测试...\n")
    
    # 测试导入
    imports_ok, face_lib = test_imports()
    
    # 测试GPU
    gpu_ok = test_gpu()
    
    # 测试摄像头
    camera_ok = test_camera()
    
    # 测试YOLO
    yolo_ok = test_yolo()
    
    print("\n=== 测试结果汇总 ===")
    print(f"依赖导入: {'✅' if imports_ok else '❌'}")
    print(f"GPU可用性: {'✅' if gpu_ok else '❌'}")
    print(f"摄像头: {'✅' if camera_ok else '❌'}")
    print(f"YOLO模型: {'✅' if yolo_ok else '❌'}")
    print(f"人脸识别: {face_lib if face_lib else '❌'}")
    
    if imports_ok and camera_ok:
        print(f"\n🎉 环境配置成功！")
        if face_lib == "opencv":
            print("ℹ️ 将使用opencv进行人脸检测和年龄性别识别")
        print("可以开始下一阶段开发。")
        return True
    else:
        print("\n⚠️ 环境配置存在问题，请检查上述错误信息。")
        return False

if __name__ == "__main__":
    main() 