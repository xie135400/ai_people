#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分析记录功能
"""

import cv2
import time
import logging
import json
import os
from datetime import datetime

from src.complete_analyzer import CompleteAnalyzer

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_analysis_records():
    """测试分析记录功能"""
    # 初始化完整分析器
    analyzer = CompleteAnalyzer(
        session_name="分析记录测试",
        use_insightface=True,
        save_interval=5,  # 每5秒保存一次数据
        record_interval=15,  # 每15秒生成一次分析记录
        auto_record=True
    )
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    logger.info("开始测试分析记录功能")
    logger.info("按 'q' 退出, 按 'r' 创建手动分析记录, 按 'e' 导出记录, 按 'l' 列出记录")
    
    try:
        start_time = time.time()
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("无法读取摄像头帧")
                break
            
            # 处理帧
            result_frame, stats = analyzer.process_frame(frame)
            frame_count += 1
            
            # 显示结果
            cv2.imshow('Analysis Records Test', result_frame)
            
            # 显示记录数
            record_count = analyzer.persistent_analyzer.record_count
            cv2.putText(result_frame, f"Records: {record_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 键盘控制
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                # 创建手动分析记录
                record_name = f"手动记录_{datetime.now().strftime('%H%M%S')}"
                record_id = analyzer.create_analysis_record(
                    custom_name=record_name,
                    additional_data={"manual_trigger": True, "test_data": "测试数据"}
                )
                logger.info(f"创建手动分析记录: {record_name} (ID: {record_id})")
            elif key == ord('e'):
                # 导出最新记录
                filepath = analyzer.export_analysis_record()
                if filepath:
                    logger.info(f"导出分析记录: {filepath}")
                    
                    # 显示记录内容
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            record_data = json.load(f)
                        logger.info(f"记录内容: {json.dumps(record_data, ensure_ascii=False, indent=2)[:200]}...")
                    except Exception as e:
                        logger.error(f"读取导出记录失败: {e}")
            elif key == ord('l'):
                # 列出所有记录
                records = analyzer.get_analysis_records(limit=5)
                logger.info(f"最近5条分析记录:")
                for i, record in enumerate(records):
                    logger.info(f"{i+1}. {record.get('record_name')} - {record.get('timestamp')} - 人数: {record.get('total_people')}")
            
            # 每隔30秒显示一次记录统计
            elapsed_time = time.time() - start_time
            if int(elapsed_time) % 30 == 0 and int(elapsed_time) > 0:
                records = analyzer.get_analysis_records(limit=100)
                logger.info(f"当前分析记录数: {len(records)}")
                
                # 计算平均帧率
                fps = frame_count / elapsed_time
                logger.info(f"平均帧率: {fps:.1f} FPS")
    
    finally:
        # 关闭资源
        cap.release()
        cv2.destroyAllWindows()
        
        # 获取所有记录
        records = analyzer.get_analysis_records(limit=100)
        logger.info(f"测试结束，共生成 {len(records)} 条分析记录")
        
        # 导出最终记录
        analyzer.create_analysis_record("最终测试记录", {"is_final": True, "test_completed": True})
        filepath = analyzer.export_analysis_record()
        logger.info(f"最终分析记录已导出: {filepath}")
        
        # 关闭分析器
        analyzer.close()

if __name__ == "__main__":
    test_analysis_records() 