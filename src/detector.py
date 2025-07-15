#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人员检测模块
使用YOLO模型进行人员检测
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonDetector:
    """人员检测器"""
    
    def __init__(self, model_path: str = 'yolov8n.pt', confidence: float = 0.5):
        """
        初始化检测器
        
        Args:
            model_path: YOLO模型路径
            confidence: 置信度阈值
        """
        self.model_path = model_path
        self.confidence = confidence
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载YOLO模型"""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"成功加载YOLO模型: {self.model_path}")
        except Exception as e:
            logger.error(f"加载YOLO模型失败: {e}")
            raise
    
    def detect_persons(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        检测图像中的人员
        
        Args:
            frame: 输入图像 (BGR格式)
            
        Returns:
            检测结果列表，每个元素为 (x1, y1, x2, y2, confidence)
        """
        if self.model is None:
            logger.error("模型未加载")
            return []
        
        try:
            # 运行检测
            results = self.model(frame, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # 获取类别ID (0 = person)
                        class_id = int(box.cls[0])
                        if class_id == 0:  # 只检测人员
                            confidence = float(box.conf[0])
                            if confidence >= self.confidence:
                                # 获取边界框坐标
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                                detections.append((
                                    int(x1), int(y1), int(x2), int(y2), confidence
                                ))
            
            logger.debug(f"检测到 {len(detections)} 个人员")
            return detections
            
        except Exception as e:
            logger.error(f"人员检测失败: {e}")
            return []
    
    def draw_detections(self, frame: np.ndarray, detections: List[Tuple[int, int, int, int, float]]) -> np.ndarray:
        """
        在图像上绘制检测结果
        
        Args:
            frame: 输入图像
            detections: 检测结果
            
        Returns:
            绘制了检测框的图像
        """
        result_frame = frame.copy()
        
        for x1, y1, x2, y2, conf in detections:
            # 绘制边界框
            cv2.rectangle(result_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 绘制置信度标签
            label = f'Person: {conf:.2f}'
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(result_frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), (0, 255, 0), -1)
            cv2.putText(result_frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return result_frame

# 添加YOLODetector类，与PersonDetector类完全相同，只是改名以兼容test_web_simple.py
class YOLODetector(PersonDetector):
    """YOLO检测器，与PersonDetector功能相同，为了兼容性而添加"""
    
    def __init__(self, model_path: str = 'yolov8n.pt', conf_threshold: float = 0.5):
        """
        初始化检测器
        
        Args:
            model_path: YOLO模型路径
            conf_threshold: 置信度阈值
        """
        super().__init__(model_path=model_path, confidence=conf_threshold)
    
    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        检测图像中的人员（兼容接口）
        
        Args:
            frame: 输入图像
            
        Returns:
            检测结果列表
        """
        return self.detect_persons(frame)

def test_detector():
    """测试检测器"""
    detector = PersonDetector()
    
    # 测试摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    logger.info("开始测试人员检测，按 'q' 退出")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 检测人员
        detections = detector.detect_persons(frame)
        
        # 绘制结果
        result_frame = detector.draw_detections(frame, detections)
        
        # 显示结果
        cv2.imshow('Person Detection', result_frame)
        
        # 按 'q' 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_detector() 