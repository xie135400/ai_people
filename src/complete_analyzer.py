#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整分析器
集成所有功能模块：人员检测跟踪、人脸分析、数据持久化、行为分析
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
import logging
from datetime import datetime
import json
import os

from persistent_analyzer import PersistentAnalyzer
from behavior_analyzer import BehaviorAnalyzer, Zone
from tracker import PersonTrack
from face_analyzer import FaceInfo
from integrated_analyzer import PersonProfile

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteAnalyzer:
    """完整的AI人流分析系统"""
    
    def __init__(self, session_name: str = None, use_insightface: bool = True,
                 db_config: Dict = None, save_interval: int = 30,
                 record_interval: int = 300, auto_record: bool = True,
                 frame_width: int = 640, frame_height: int = 480):
        """
        初始化完整分析器
        
        Args:
            session_name: 会话名称
            use_insightface: 是否使用InsightFace（默认True，使用高精度模式）
            db_config: 数据库配置字典，如果为None则使用默认MySQL配置
            save_interval: 数据保存间隔（秒）
            record_interval: 分析记录生成间隔（秒），默认5分钟
            auto_record: 是否自动生成分析记录
            frame_width: 视频帧宽度
            frame_height: 视频帧高度
        """
        # 初始化持久化分析器
        self.persistent_analyzer = PersistentAnalyzer(
            session_name=session_name,
            use_insightface=use_insightface,
            db_config=db_config,
            save_interval=save_interval,
            record_interval=record_interval
        )
        
        # 设置父分析器引用，用于获取行为分析数据
        self.persistent_analyzer.parent_analyzer = self
        
        # 初始化行为分析器
        self.behavior_analyzer = BehaviorAnalyzer(
            frame_width=frame_width,
            frame_height=frame_height
        )
        
        # 显示配置
        self.display_config = {
            'show_tracks': True,
            'show_faces': True,
            'show_zones': True,
            'show_heatmap': False,
            'show_behavior_info': True,
            'show_statistics': True,
            'show_db_info': False
        }
        
        # 统计数据
        self.session_stats = {}
        
        # 分析记录配置
        self.auto_record = auto_record
        self.record_interval = record_interval
        
        # 创建分析记录导出目录
        self.export_dir = "data/analysis_records"
        os.makedirs(self.export_dir, exist_ok=True)
        
        logger.info("完整AI人流分析系统初始化完成")
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        处理单帧图像
        
        Args:
            frame: 输入图像
            
        Returns:
            (处理后的图像, 统计信息)
        """
        # 1. 基础分析（人员检测、跟踪、人脸识别、数据存储）
        tracks, faces, profiles = self.persistent_analyzer.process_frame(frame)
        
        # 2. 行为分析
        self.behavior_analyzer.update_behavior_analysis(tracks, profiles)
        
        # 3. 绘制结果
        result_frame = self._draw_complete_results(frame, tracks, faces)
        
        # 4. 收集统计信息
        stats = self._collect_statistics()
        
        return result_frame, stats
    
    def _draw_complete_results(self, frame: np.ndarray, tracks: List[PersonTrack], 
                              faces: List[FaceInfo]) -> np.ndarray:
        """绘制完整的分析结果"""
        result_frame = frame.copy()
        
        # 绘制热力图（如果启用）
        if self.display_config['show_heatmap']:
            result_frame = self.behavior_analyzer.draw_heatmap(result_frame, alpha=0.4)
        
        # 绘制区域（如果启用）
        if self.display_config['show_zones']:
            result_frame = self.behavior_analyzer.draw_zones(result_frame)
        
        # 绘制基础分析结果（轨迹、人脸）
        if self.display_config['show_tracks'] or self.display_config['show_faces']:
            result_frame = self.persistent_analyzer.draw_results(
                result_frame, tracks, faces, 
                show_db_info=self.display_config['show_db_info']
            )
        
        # 绘制行为信息（如果启用）
        if self.display_config['show_behavior_info']:
            result_frame = self.behavior_analyzer.draw_behavior_info(result_frame, tracks)
        
        # 绘制统计信息（如果启用）
        if self.display_config['show_statistics']:
            result_frame = self._draw_statistics(result_frame)
        
        return result_frame
    
    def _draw_statistics(self, frame: np.ndarray) -> np.ndarray:
        """绘制统计信息"""
        result_frame = frame.copy()
        
        # 获取各种统计信息
        realtime_stats = self.persistent_analyzer.get_realtime_statistics()
        behavior_summary = self.behavior_analyzer.get_behavior_summary()
        
        # 准备显示信息
        info_lines = []
        
        # 基础统计
        info_lines.append(f"Frame: {realtime_stats.get('frame_count', 0)}")
        info_lines.append(f"Total People: {realtime_stats.get('total_people', 0)}")
        info_lines.append(f"Active: {realtime_stats.get('active_tracks', 0)}")
        
        # 人脸分析统计
        if realtime_stats.get('avg_age'):
            info_lines.append(f"Avg Age: {realtime_stats['avg_age']:.1f}")
        info_lines.append(f"Male: {realtime_stats.get('male_count', 0)}, Female: {realtime_stats.get('female_count', 0)}")
        
        # 行为分析统计
        if behavior_summary:
            info_lines.append(f"Avg Dwell: {behavior_summary.get('avg_dwell_time', 0):.1f}s")
            info_lines.append(f"Shoppers: {behavior_summary.get('shoppers', 0)} ({behavior_summary.get('shopper_rate', 0):.1%})")
            info_lines.append(f"Browsers: {behavior_summary.get('browsers', 0)} ({behavior_summary.get('browser_rate', 0):.1%})")
            info_lines.append(f"Avg Engagement: {behavior_summary.get('avg_engagement_score', 0):.1f}")
        
        # 分析记录信息
        record_count = self.persistent_analyzer.record_count
        info_lines.append(f"Records: {record_count}")
        
        # 绘制信息
        for i, line in enumerate(info_lines):
            y_pos = 30 + i * 20
            cv2.putText(result_frame, line, (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            # 添加黑色背景提高可读性
            text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(result_frame, (8, y_pos - 15), (12 + text_size[0], y_pos + 5), (0, 0, 0), -1)
            cv2.putText(result_frame, line, (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return result_frame
    
    def _collect_statistics(self) -> Dict:
        """收集所有统计信息"""
        stats = {}
        
        # 实时统计
        stats['realtime'] = self.persistent_analyzer.get_realtime_statistics()
        
        # 行为分析统计
        stats['behavior'] = self.behavior_analyzer.get_behavior_summary()
        
        # 区域统计
        stats['zones'] = self.behavior_analyzer.get_zone_statistics()
        
        # 数据库统计（如果需要）
        try:
            stats['database'] = self.persistent_analyzer.get_session_statistics()
        except:
            stats['database'] = {}
        
        # 分析记录统计
        try:
            stats['records'] = {
                'count': self.persistent_analyzer.record_count,
                'last_record_time': self.persistent_analyzer.last_record_time
            }
        except:
            stats['records'] = {'count': 0}
        
        return stats
    
    def toggle_display_option(self, option: str):
        """切换显示选项"""
        if option in self.display_config:
            self.display_config[option] = not self.display_config[option]
            logger.info(f"{option}: {'开启' if self.display_config[option] else '关闭'}")
        else:
            logger.warning(f"未知的显示选项: {option}")
    
    def add_custom_zone(self, name: str, polygon: List[Tuple[int, int]], 
                       color: Tuple[int, int, int] = (0, 255, 0), zone_type: str = "custom"):
        """添加自定义区域"""
        zone = Zone(name=name, polygon=polygon, color=color, zone_type=zone_type)
        self.behavior_analyzer.add_zone(zone)
    
    def save_current_data(self):
        """立即保存当前数据"""
        # 获取当前轨迹和人脸（需要从最后一次处理中获取）
        # 这里简化处理，实际应用中可能需要缓存最后的结果
        self.persistent_analyzer.save_current_frame_data([], [])
        logger.info("手动保存数据完成")
    
    def create_analysis_record(self, custom_name: str = None, additional_data: Dict = None) -> int:
        """
        创建分析记录
        
        Args:
            custom_name: 自定义记录名称
            additional_data: 附加数据
            
        Returns:
            记录ID
        """
        # 获取当前轨迹和人脸（需要从最后一次处理中获取）
        record_id = self.persistent_analyzer.create_analysis_record_now(
            [], [], custom_name, additional_data
        )
        logger.info(f"创建分析记录: {record_id}")
        return record_id
    
    def get_analysis_records(self, limit: int = 20) -> List[Dict]:
        """
        获取分析记录列表
        
        Args:
            limit: 最大返回数量
            
        Returns:
            分析记录列表
        """
        return self.persistent_analyzer.get_analysis_records(limit)
    
    def export_analysis_record(self, record_id: Optional[int] = None, filepath: Optional[str] = None) -> str:
        """
        导出分析记录到JSON文件
        
        Args:
            record_id: 记录ID，如果为None则导出最新记录
            filepath: 导出文件路径，如果为None则自动生成
            
        Returns:
            导出文件路径
        """
        # 获取记录
        records = self.persistent_analyzer.get_analysis_records(1)
        if not records:
            logger.warning("没有可导出的分析记录")
            return ""
        
        record = None
        if record_id is not None:
            # 获取指定ID的记录
            db = self.persistent_analyzer.db
            record = db.get_analysis_record(record_id)
            if not record:
                logger.warning(f"未找到ID为{record_id}的分析记录")
                return ""
        else:
            # 使用最新记录
            record = records[0]
        
        # 生成文件路径
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            record_name = record.get('record_name', '').replace(' ', '_')
            filepath = os.path.join(self.export_dir, f"record_{record_name}_{timestamp}.json")
        
        # 处理不能序列化的对象
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, set):
                return list(obj)
            return str(obj)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False, indent=2, default=json_serializer)
            
            logger.info(f"分析记录已导出到: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"导出分析记录失败: {e}")
            return ""
    
    def export_statistics(self, filepath: str = None) -> str:
        """导出统计信息到JSON文件"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/statistics_{timestamp}.json"
        
        stats = self._collect_statistics()
        
        # 处理不能序列化的对象
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, set):
                return list(obj)
            return str(obj)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2, default=json_serializer)
            
            logger.info(f"统计信息已导出到: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"导出统计信息失败: {e}")
            return ""
    
    def get_performance_metrics(self) -> Dict:
        """获取性能指标"""
        realtime_stats = self.persistent_analyzer.get_realtime_statistics()
        behavior_summary = self.behavior_analyzer.get_behavior_summary()
        
        metrics = {
            'total_people_detected': realtime_stats.get('total_people', 0),
            'active_tracks': realtime_stats.get('active_tracks', 0),
            'frames_processed': realtime_stats.get('frame_count', 0),
            'avg_dwell_time': behavior_summary.get('avg_dwell_time', 0),
            'engagement_rate': behavior_summary.get('avg_engagement_score', 0) / 100,  # 转换为0-1范围
            'conversion_rate': behavior_summary.get('shopper_rate', 0),  # 购物者比例作为转化率
            'browse_rate': behavior_summary.get('browser_rate', 0)
        }
        
        return metrics
    
    def close(self):
        """关闭分析器和数据库连接"""
        try:
            self.persistent_analyzer.close()
            logger.info("完整分析器已关闭")
        except Exception as e:
            logger.error(f"关闭分析器失败: {e}")
    
    def stop(self):
        """停止分析但不关闭数据库连接"""
        try:
            # 保存最后的分析记录，但不关闭数据库
            # 注意: end_session方法内部会创建一条最终分析记录，不需要额外创建
            if hasattr(self.persistent_analyzer, 'end_session'):
                self.persistent_analyzer.end_session()
            logger.info("分析已停止，数据库连接保持打开")
        except Exception as e:
            logger.error(f"停止分析失败: {e}")

def test_complete_analyzer():
    """测试完整分析器"""
    analyzer = CompleteAnalyzer(
        session_name="测试完整分析",
        use_insightface=True,
        save_interval=10,  # 每10秒保存一次
        record_interval=30  # 每30秒生成一次分析记录
    )
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    logger.info("开始测试完整分析，按 'q' 退出, 按 's' 保存数据, 按 'r' 创建分析记录, 按 'e' 导出记录")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 处理帧
            result_frame, stats = analyzer.process_frame(frame)
            
            # 显示结果
            cv2.imshow('Complete Analyzer Test', result_frame)
            
            # 键盘控制
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                analyzer.save_current_data()
            elif key == ord('r'):
                analyzer.create_analysis_record("手动测试记录", {"manual_trigger": True})
            elif key == ord('e'):
                filepath = analyzer.export_analysis_record()
                logger.info(f"导出分析记录: {filepath}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        analyzer.close()

if __name__ == "__main__":
    test_complete_analyzer() 