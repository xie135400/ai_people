#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持久化分析器
集成数据库存储功能与现有的分析器
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
import logging
from datetime import datetime
import threading
import time

from integrated_analyzer import IntegratedAnalyzer, PersonProfile
from database import DatabaseManager
from tracker import PersonTrack
from face_analyzer import FaceInfo

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersistentAnalyzer:
    """持久化分析器"""
    
    def __init__(self, session_name: str = None, use_insightface: bool = True, 
                 db_config: Dict = None, save_interval: int = 30,
                 record_interval: int = 300):
        """
        初始化持久化分析器
        
        Args:
            session_name: 会话名称
            use_insightface: 是否使用InsightFace（默认True，使用高精度模式）
            db_config: 数据库配置字典，如果为None则使用默认MySQL配置
            save_interval: 数据保存间隔（秒）
            record_interval: 分析记录生成间隔（秒），默认5分钟
        """
        # 初始化集成分析器
        self.analyzer = IntegratedAnalyzer(use_insightface=use_insightface)
        
        # 初始化数据库
        self.db = DatabaseManager(db_config)
        
        # 创建会话
        if session_name is None:
            session_name = f"会话_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.session_id = self.db.create_session(session_name)
        self.session_name = session_name
        
        # 数据保存配置
        self.save_interval = save_interval
        self.last_save_time = time.time()
        self.person_db_ids = {}  # track_id -> person_id 映射
        
        # 分析记录配置
        self.record_interval = record_interval
        self.last_record_time = time.time()
        self.record_count = 0
        
        # 线程安全锁
        self.lock = threading.Lock()
        
        logger.info(f"持久化分析器初始化完成 - 会话: {session_name} (ID: {self.session_id})")
    
    def process_frame(self, frame: np.ndarray) -> Tuple[List[PersonTrack], List[FaceInfo], Dict[int, PersonProfile]]:
        """
        处理单帧图像并保存数据
        
        Args:
            frame: 输入图像
            
        Returns:
            (人员轨迹列表, 人脸信息列表, 人员档案字典)
        """
        # 使用集成分析器处理帧
        tracks, faces, profiles = self.analyzer.process_frame(frame)
        
        current_time = time.time()
        
        # 定期保存数据
        if current_time - self.last_save_time >= self.save_interval:
            self._save_data_batch(profiles, tracks, faces)
            self.last_save_time = current_time
        
        # 定期生成分析记录
        if current_time - self.last_record_time >= self.record_interval:
            self._create_analysis_record(tracks, faces, profiles)
            self.last_record_time = current_time
        
        return tracks, faces, profiles
    
    def _save_data_batch(self, profiles: Dict[int, PersonProfile], 
                        tracks: List[PersonTrack], faces: List[FaceInfo]):
        """
        批量保存数据
        
        Args:
            profiles: 人员档案字典
            tracks: 当前轨迹列表
            faces: 当前人脸列表
        """
        with self.lock:
            try:
                # 保存人员档案
                for track_id, profile in profiles.items():
                    person_data = {
                        'track_id': track_id,
                        'first_seen': profile.first_seen,
                        'last_seen': profile.last_seen,
                        'total_frames': profile.total_frames,
                        'faces_detected': profile.faces_detected,
                        'avg_age': profile.avg_age,
                        'dominant_gender': profile.dominant_gender,
                        'gender_confidence': profile.gender_confidence
                    }
                    
                    person_id = self.db.save_person(self.session_id, person_data)
                    self.person_db_ids[track_id] = person_id
                
                # 保存当前活跃轨迹的位置信息
                for track in tracks:
                    if track.track_id in self.person_db_ids:
                        person_id = self.person_db_ids[track.track_id]
                        self.db.save_position(
                            person_id, 
                            track.center[0], 
                            track.center[1], 
                            datetime.now(),
                            self.analyzer.frame_count
                        )
                
                # 保存人脸信息（如果有的话）
                for face in faces:
                    # 这里需要关联人脸到具体的人员，简化处理
                    # 实际应用中可能需要更复杂的关联逻辑
                    if self.person_db_ids:
                        # 使用第一个可用的person_id（简化处理）
                        person_id = list(self.person_db_ids.values())[0]
                        face_data = {
                            'age': face.age,
                            'gender': face.gender,
                            'gender_confidence': face.gender_confidence,
                            'bbox': face.bbox,
                            'confidence': face.confidence,
                            'timestamp': datetime.now()
                        }
                        self.db.save_face(person_id, face_data)
                
                logger.debug(f"批量保存数据完成 - 人员: {len(profiles)}, 轨迹: {len(tracks)}, 人脸: {len(faces)}")
                
            except Exception as e:
                logger.error(f"数据保存失败: {e}")
    
    def _create_analysis_record(self, tracks: List[PersonTrack], faces: List[FaceInfo], 
                               profiles: Dict[int, PersonProfile]):
        """
        创建分析记录
        
        Args:
            tracks: 当前轨迹列表
            faces: 当前人脸列表
            profiles: 人员档案字典
        """
        with self.lock:
            try:
                # 获取实时统计信息
                realtime_stats = self.get_realtime_statistics()
                
                # 尝试获取行为分析统计信息（如果有的话）
                behavior_stats = {}
                zone_stats = {}
                try:
                    from complete_analyzer import CompleteAnalyzer
                    if hasattr(self, 'parent_analyzer') and isinstance(self.parent_analyzer, CompleteAnalyzer):
                        behavior_stats = self.parent_analyzer.behavior_analyzer.get_behavior_summary()
                        zone_stats = self.parent_analyzer.behavior_analyzer.get_zone_statistics()
                except (ImportError, AttributeError):
                    pass
                
                # 准备分析记录数据
                self.record_count += 1
                record_data = {
                    'session_id': self.session_id,
                    'record_name': f"记录_{self.session_name}_{self.record_count}",
                    'timestamp': datetime.now(),
                    'total_people': realtime_stats.get('total_people', 0),
                    'active_tracks': realtime_stats.get('active_tracks', 0),
                    'avg_age': realtime_stats.get('avg_age'),
                    'male_count': realtime_stats.get('male_count', 0),
                    'female_count': realtime_stats.get('female_count', 0),
                    'avg_dwell_time': behavior_stats.get('avg_dwell_time', 0.0),
                    'engagement_score': behavior_stats.get('avg_engagement_score', 0.0),
                    'shopper_count': behavior_stats.get('shoppers', 0),
                    'browser_count': behavior_stats.get('browsers', 0),
                    'zone_data': zone_stats,
                    'additional_data': {
                        'frame_count': realtime_stats.get('frame_count', 0),
                        'faces_detected': len(faces),
                        'age_distribution': realtime_stats.get('age_distribution', {}),
                        'gender_distribution': {
                            'male': realtime_stats.get('male_count', 0),
                            'female': realtime_stats.get('female_count', 0)
                        },
                        'processing_time': realtime_stats.get('processing_time', 0.0),
                        'timestamp': datetime.now().isoformat()
                    }
                }
                
                # 保存分析记录
                record_id = self.db.save_analysis_record(record_data)
                logger.info(f"创建分析记录: {record_data['record_name']} (ID: {record_id})")
                
                return record_id
                
            except Exception as e:
                logger.error(f"创建分析记录失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return None
    
    def save_current_frame_data(self, tracks: List[PersonTrack], faces: List[FaceInfo]):
        """
        立即保存当前帧数据
        
        Args:
            tracks: 当前轨迹列表
            faces: 当前人脸列表
        """
        profiles = self.analyzer.person_profiles
        self._save_data_batch(profiles, tracks, faces)
        
        # 同时创建一个分析记录
        self._create_analysis_record(tracks, faces, profiles)
    
    def create_analysis_record_now(self, tracks: List[PersonTrack], faces: List[FaceInfo], 
                                  custom_name: str = None, additional_data: Dict = None):
        """
        立即创建一个分析记录
        
        Args:
            tracks: 当前轨迹列表
            faces: 当前人脸列表
            custom_name: 自定义记录名称
            additional_data: 附加数据
            
        Returns:
            记录ID
        """
        profiles = self.analyzer.person_profiles
        
        # 保存当前帧数据
        self._save_data_batch(profiles, tracks, faces)
        
        # 创建分析记录
        with self.lock:
            try:
                # 获取实时统计信息
                realtime_stats = self.get_realtime_statistics()
                
                # 尝试获取行为分析统计信息（如果有的话）
                behavior_stats = {}
                zone_stats = {}
                try:
                    from complete_analyzer import CompleteAnalyzer
                    if hasattr(self, 'parent_analyzer') and isinstance(self.parent_analyzer, CompleteAnalyzer):
                        behavior_stats = self.parent_analyzer.behavior_analyzer.get_behavior_summary()
                        zone_stats = self.parent_analyzer.behavior_analyzer.get_zone_statistics()
                except (ImportError, AttributeError):
                    pass
                
                # 准备分析记录数据
                self.record_count += 1
                record_name = custom_name or f"手动记录_{self.session_name}_{self.record_count}"
                
                # 合并附加数据
                extra_data = {
                    'frame_count': realtime_stats.get('frame_count', 0),
                    'faces_detected': len(faces),
                    'age_distribution': realtime_stats.get('age_distribution', {}),
                    'gender_distribution': {
                        'male': realtime_stats.get('male_count', 0),
                        'female': realtime_stats.get('female_count', 0)
                    },
                    'processing_time': realtime_stats.get('processing_time', 0.0),
                    'timestamp': datetime.now().isoformat(),
                    'is_manual': True
                }
                
                if additional_data:
                    extra_data.update(additional_data)
                
                record_data = {
                    'session_id': self.session_id,
                    'record_name': record_name,
                    'timestamp': datetime.now(),
                    'total_people': realtime_stats.get('total_people', 0),
                    'active_tracks': realtime_stats.get('active_tracks', 0),
                    'avg_age': realtime_stats.get('avg_age'),
                    'male_count': realtime_stats.get('male_count', 0),
                    'female_count': realtime_stats.get('female_count', 0),
                    'avg_dwell_time': behavior_stats.get('avg_dwell_time', 0.0),
                    'engagement_score': behavior_stats.get('avg_engagement_score', 0.0),
                    'shopper_count': behavior_stats.get('shoppers', 0),
                    'browser_count': behavior_stats.get('browsers', 0),
                    'zone_data': zone_stats,
                    'additional_data': extra_data
                }
                
                # 保存分析记录
                record_id = self.db.save_analysis_record(record_data)
                logger.info(f"手动创建分析记录: {record_name} (ID: {record_id})")
                
                return record_id
                
            except Exception as e:
                logger.error(f"手动创建分析记录失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return None
    
    def end_session(self):
        """结束当前会话但不关闭数据库连接"""
        try:
            # 最后一次保存数据
            profiles = self.analyzer.person_profiles
            self._save_data_batch(profiles, [], [])
            
            # 获取最终统计信息
            stats = self.analyzer.get_statistics()
            
            # 创建最终分析记录 - 只创建一次
            self._create_analysis_record([], [], profiles)
            
            # 结束会话
            self.db.end_session(self.session_id, stats)
            
            logger.info(f"会话结束: {self.session_name}")
            logger.info(f"最终统计: 总人数={stats['total_people']}, "
                       f"平均年龄={stats.get('avg_age', 'N/A')}, "
                       f"男性={stats['male_count']}, 女性={stats['female_count']}")
            
        except Exception as e:
            logger.error(f"结束会话失败: {e}")
    
    def get_session_statistics(self) -> Dict:
        """获取当前会话的数据库统计信息"""
        return self.db.get_session_statistics(self.session_id)
    
    def get_realtime_statistics(self) -> Dict:
        """获取实时统计信息"""
        # 传递当前轨迹信息以获得准确的当前人数
        current_tracks = getattr(self.analyzer, '_current_tracks', [])
        return self.analyzer.get_statistics(current_tracks)
    
    def get_analysis_records(self, limit: int = 20) -> List[Dict]:
        """
        获取当前会话的分析记录
        
        Args:
            limit: 最大返回数量
            
        Returns:
            分析记录列表
        """
        return self.db.get_analysis_records(self.session_id, limit)
    
    def draw_results(self, frame: np.ndarray, tracks: List[PersonTrack], 
                    faces: List[FaceInfo], show_db_info: bool = True) -> np.ndarray:
        """
        绘制分析结果
        
        Args:
            frame: 输入图像
            tracks: 人员轨迹列表
            faces: 人脸信息列表
            show_db_info: 是否显示数据库信息
            
        Returns:
            绘制了分析结果的图像
        """
        # 使用集成分析器绘制基本结果
        result_frame = self.analyzer.draw_integrated_results(frame, tracks, faces)
        
        if show_db_info:
            # 添加数据库会话信息
            session_info = [
                f"Session: {self.session_name}",
                f"Session ID: {self.session_id}",
                f"Save Interval: {self.save_interval}s",
                f"Record Interval: {self.record_interval}s",
                f"Records: {self.record_count}"
            ]
            
            for i, info in enumerate(session_info):
                cv2.putText(result_frame, info, (10, frame.shape[0] - 80 + i * 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return result_frame
    
    def close(self):
        """关闭分析器和数据库连接"""
        try:
            # 确保会话已结束
            self.end_session()
            # 关闭数据库连接
            self.db.close()
            logger.info("持久化分析器已关闭")
        except Exception as e:
            logger.error(f"关闭分析器失败: {e}")

def test_persistent_analyzer():
    """测试持久化分析器"""
    # 初始化持久化分析器
    analyzer = PersistentAnalyzer(
        session_name="测试持久化分析",
        use_insightface=True,
        save_interval=10,  # 每10秒保存一次
        record_interval=30  # 每30秒生成一次分析记录
    )
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    logger.info("开始测试持久化分析，按 'q' 退出, 按 's' 立即保存数据, 按 'r' 创建分析记录")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 处理帧
            tracks, faces, profiles = analyzer.process_frame(frame)
            
            # 绘制结果
            result_frame = analyzer.draw_results(frame, tracks, faces)
            
            # 显示结果
            cv2.imshow('Persistent Analyzer Test', result_frame)
            
            # 键盘控制
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 手动保存数据
                analyzer.save_current_frame_data(tracks, faces)
                logger.info("手动保存数据")
            elif key == ord('r'):
                # 手动创建分析记录
                record_id = analyzer.create_analysis_record_now(
                    tracks, faces, 
                    custom_name="手动测试记录",
                    additional_data={"manual_trigger": True, "note": "测试手动创建记录"}
                )
                logger.info(f"手动创建分析记录: {record_id}")
    
    finally:
        # 关闭资源
        cap.release()
        cv2.destroyAllWindows()
        analyzer.close()

if __name__ == "__main__":
    test_persistent_analyzer() 