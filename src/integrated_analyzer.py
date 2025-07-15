#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成分析模块
将人员检测跟踪与人脸分析结合
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
import logging
from dataclasses import dataclass, field
from datetime import datetime

from .detector import PersonDetector
from .tracker import PersonTracker, PersonTrack
from .face_analyzer import FaceAnalyzer, FaceInfo

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PersonProfile:
    """人员档案数据类"""
    track_id: int
    first_seen: datetime
    last_seen: datetime
    total_frames: int = 0
    
    # 人脸信息
    faces_detected: int = 0
    age_estimates: List[int] = field(default_factory=list)
    age_confidences: List[float] = field(default_factory=list)  # 年龄置信度
    age_qualities: List[float] = field(default_factory=list)    # 人脸质量
    gender_estimates: List[str] = field(default_factory=list)
    
    # 统计属性
    avg_age: Optional[float] = None
    age_confidence: float = 0.0  # 平均年龄置信度
    avg_face_quality: float = 0.0  # 平均人脸质量
    dominant_gender: Optional[str] = None
    gender_confidence: float = 0.0
    
    # 轨迹信息
    positions: List[Tuple[int, int, datetime]] = field(default_factory=list)
    
    def update_face_info(self, face: FaceInfo):
        """更新人脸信息"""
        self.faces_detected += 1
        
        if face.age is not None:
            self.age_estimates.append(face.age)
            
            # 更新年龄置信度
            if face.age_confidence is not None:
                self.age_confidences.append(face.age_confidence)
                self.age_confidence = sum(self.age_confidences) / len(self.age_confidences)
            
            # 更新人脸质量
            if face.face_quality is not None:
                self.age_qualities.append(face.face_quality)
                self.avg_face_quality = sum(self.age_qualities) / len(self.age_qualities)
            
            # 计算加权平均年龄（基于置信度和质量）
            if self.age_confidences and self.age_qualities:
                weights = []
                for conf, qual in zip(self.age_confidences, self.age_qualities):
                    weight = conf * qual
                    weights.append(weight)
                
                if sum(weights) > 0:
                    weighted_sum = sum(age * weight for age, weight in zip(self.age_estimates, weights))
                    total_weight = sum(weights)
                    self.avg_age = weighted_sum / total_weight
                else:
                    self.avg_age = sum(self.age_estimates) / len(self.age_estimates)
            else:
                self.avg_age = sum(self.age_estimates) / len(self.age_estimates)
        
        if face.gender is not None:
            self.gender_estimates.append(face.gender)
            # 计算主要性别
            if self.gender_estimates:
                male_count = self.gender_estimates.count('Male')
                female_count = self.gender_estimates.count('Female')
                if male_count > female_count:
                    self.dominant_gender = 'Male'
                    self.gender_confidence = male_count / len(self.gender_estimates)
                else:
                    self.dominant_gender = 'Female'
                    self.gender_confidence = female_count / len(self.gender_estimates)
    
    def update_position(self, center: Tuple[int, int], timestamp: datetime):
        """更新位置信息"""
        self.positions.append((center[0], center[1], timestamp))
        self.last_seen = timestamp
        self.total_frames += 1
        
        # 限制位置历史长度
        if len(self.positions) > 100:
            self.positions = self.positions[-100:]

class IntegratedAnalyzer:
    """集成分析器"""
    
    def __init__(self, use_insightface: bool = True):
        """
        初始化集成分析器
        
        Args:
            use_insightface: 是否使用InsightFace进行人脸分析（默认True，使用高精度模式）
        """
        # 初始化各个组件
        self.person_detector = PersonDetector()
        self.person_tracker = PersonTracker()
        self.face_analyzer = FaceAnalyzer(use_insightface=use_insightface)
        
        # 人员档案存储
        self.person_profiles: Dict[int, PersonProfile] = {}
        
        # 配置参数
        self.face_detection_interval = 6  # 每6帧进行一次人脸检测（准确性优化）
        self.frame_count = 0
        
        # 当前轨迹信息（用于准确计算当前人数）
        self._current_tracks = []
        
        # 高级性能优化：自适应参数
        self._processing_times = []
        self._adaptive_mode = False
        self._skip_frames = 0
        
        logger.info("集成分析器初始化完成")
    
    def process_frame(self, frame: np.ndarray) -> Tuple[List[PersonTrack], List[FaceInfo], Dict[int, PersonProfile]]:
        """
        处理单帧图像
        
        Args:
            frame: 输入图像
            
        Returns:
            (人员轨迹列表, 人脸信息列表, 人员档案字典)
        """
        self.frame_count += 1
        current_time = datetime.now()
        start_time = current_time
        
        # 高级优化：自适应处理
        if self._adaptive_mode and self._skip_frames > 0:
            self._skip_frames -= 1
            return self._current_tracks, [], self.person_profiles
        
        # 1. 人员检测
        detections = self.person_detector.detect_persons(frame)
        
        # 2. 人员跟踪
        tracks = self.person_tracker.update(detections, frame)
        
        # 3. 人脸检测（间隔执行以提高性能）
        faces = []
        if self.frame_count % self.face_detection_interval == 0:
            # 创建跟踪信息字典供人脸分析器使用
            track_dict = {track.track_id: track for track in tracks}
            
            # 使用优化的人脸检测（包含多帧融合）
            faces = self.face_analyzer.detect_faces_with_tracking(frame, track_dict)
        
        # 4. 关联人脸与轨迹
        self._associate_faces_with_tracks(tracks, faces, current_time)
        
        # 5. 更新人员档案
        self._update_person_profiles(tracks, current_time)
        
        # 6. 存储当前轨迹信息供统计使用
        self._current_tracks = tracks
        
        # 高级优化：性能监控和自适应调整
        processing_time = (datetime.now() - start_time).total_seconds()
        self._processing_times.append(processing_time)
        
        # 保持最近100次的处理时间
        if len(self._processing_times) > 100:
            self._processing_times = self._processing_times[-100:]
        
        # 自适应调整：如果处理时间过长，启用跳帧
        if len(self._processing_times) >= 10:
            avg_time = sum(self._processing_times[-10:]) / 10
            if avg_time > 0.25:  # 如果平均处理时间超过250ms（更宽松的阈值）
                self._adaptive_mode = True
                self._skip_frames = 2  # 跳过接下来的2帧
                self.face_detection_interval = min(10, self.face_detection_interval + 1)
                logger.debug(f"启用自适应模式：平均处理时间 {avg_time:.3f}s")
            elif avg_time < 0.1 and self._adaptive_mode:
                self._adaptive_mode = False
                self.face_detection_interval = max(5, self.face_detection_interval - 1)
                logger.debug(f"关闭自适应模式：平均处理时间 {avg_time:.3f}s")
        
        return tracks, faces, self.person_profiles
    
    def _associate_faces_with_tracks(self, tracks: List[PersonTrack], faces: List[FaceInfo], timestamp: datetime):
        """
        关联人脸检测结果与人员轨迹
        
        Args:
            tracks: 人员轨迹列表
            faces: 人脸信息列表
            timestamp: 时间戳
        """
        if not faces or not tracks:
            return
        
        # 计算人脸与轨迹的重叠度
        for face in faces:
            face_x1, face_y1, face_x2, face_y2 = face.bbox
            face_center = ((face_x1 + face_x2) // 2, (face_y1 + face_y2) // 2)
            
            best_track = None
            best_overlap = 0
            
            for track in tracks:
                track_x1, track_y1, track_x2, track_y2 = track.bbox
                
                # 计算重叠区域
                overlap_x1 = max(face_x1, track_x1)
                overlap_y1 = max(face_y1, track_y1)
                overlap_x2 = min(face_x2, track_x2)
                overlap_y2 = min(face_y2, track_y2)
                
                if overlap_x1 < overlap_x2 and overlap_y1 < overlap_y2:
                    overlap_area = (overlap_x2 - overlap_x1) * (overlap_y2 - overlap_y1)
                    face_area = (face_x2 - face_x1) * (face_y2 - face_y1)
                    overlap_ratio = overlap_area / face_area if face_area > 0 else 0
                    
                    if overlap_ratio > best_overlap and overlap_ratio > 0.3:  # 至少30%重叠
                        best_overlap = overlap_ratio
                        best_track = track
            
            # 如果找到匹配的轨迹，更新档案
            if best_track is not None:
                track_id = best_track.track_id
                if track_id not in self.person_profiles:
                    self.person_profiles[track_id] = PersonProfile(
                        track_id=track_id,
                        first_seen=timestamp,
                        last_seen=timestamp
                    )
                
                self.person_profiles[track_id].update_face_info(face)
    
    def _update_person_profiles(self, tracks: List[PersonTrack], timestamp: datetime):
        """
        更新人员档案
        
        Args:
            tracks: 人员轨迹列表
            timestamp: 时间戳
        """
        for track in tracks:
            track_id = track.track_id
            
            # 创建或更新档案
            if track_id not in self.person_profiles:
                self.person_profiles[track_id] = PersonProfile(
                    track_id=track_id,
                    first_seen=timestamp,
                    last_seen=timestamp
                )
            
            # 更新位置信息
            self.person_profiles[track_id].update_position(track.center, timestamp)
    
    def draw_integrated_results(self, frame: np.ndarray, tracks: List[PersonTrack], 
                              faces: List[FaceInfo], show_profiles: bool = True) -> np.ndarray:
        """
        绘制集成分析结果
        
        Args:
            frame: 输入图像
            tracks: 人员轨迹列表
            faces: 人脸信息列表
            show_profiles: 是否显示人员档案信息
            
        Returns:
            绘制了分析结果的图像
        """
        result_frame = frame.copy()
        
        # 1. 绘制人员轨迹
        result_frame = self.person_tracker.draw_tracks(result_frame, tracks, show_path=True)
        
        # 2. 绘制人脸检测结果
        result_frame = self.face_analyzer.draw_faces(result_frame, faces)
        
        # 3. 绘制人员档案信息
        if show_profiles:
            for track in tracks:
                track_id = track.track_id
                if track_id in self.person_profiles:
                    profile = self.person_profiles[track_id]
                    x1, y1, x2, y2 = track.bbox
                    
                    # 准备档案信息
                    profile_info = []
                    if profile.avg_age is not None:
                        age_text = f"Age: {profile.avg_age:.1f}"
                        if profile.age_confidence > 0:
                            age_text += f" (conf: {profile.age_confidence:.2f})"
                        profile_info.append(age_text)
                    
                    if profile.dominant_gender is not None:
                        gender_text = f"Gender: {profile.dominant_gender}"
                        if profile.gender_confidence > 0:
                            gender_text += f" ({profile.gender_confidence:.2f})"
                        profile_info.append(gender_text)
                    
                    if profile.avg_face_quality > 0:
                        profile_info.append(f"Quality: {profile.avg_face_quality:.2f}")
                    
                    profile_info.append(f"Frames: {profile.total_frames}")
                    profile_info.append(f"Faces: {profile.faces_detected}")
                    
                    # 根据年龄置信度选择颜色
                    if profile.age_confidence > 0.8:
                        text_color = (0, 255, 0)  # 高置信度 - 绿色
                    elif profile.age_confidence > 0.6:
                        text_color = (0, 255, 255)  # 中等置信度 - 黄色
                    else:
                        text_color = (255, 255, 0)  # 低置信度 - 青色
                    
                    # 绘制档案信息
                    for i, info in enumerate(profile_info):
                        info_y = y2 + 20 + (i * 15)
                        
                        # 添加背景提高可读性
                        text_size = cv2.getTextSize(info, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
                        cv2.rectangle(result_frame, (x1, info_y - 12), 
                                     (x1 + text_size[0] + 4, info_y + 3), (0, 0, 0), -1)
                        
                        cv2.putText(result_frame, info, (x1 + 2, info_y), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1)
        
        return result_frame
    
    def get_statistics(self, current_tracks: List[PersonTrack] = None) -> Dict:
        """
        获取统计信息
        
        Args:
            current_tracks: 当前帧的轨迹列表（用于准确计算当前人数）
        
        Returns:
            统计信息字典
        """
        total_people = len(self.person_profiles)
        
        # 修复：当前人数应该基于当前帧的轨迹数量，而不是历史档案
        if current_tracks is not None:
            # 使用当前帧的轨迹数量作为当前人数
            active_tracks = len(current_tracks)
        else:
            # 备用方案：基于最近30秒内的档案
            active_tracks = len([p for p in self.person_profiles.values() 
                               if (datetime.now() - p.last_seen).seconds < 30])
        
        # 年龄统计
        ages = [p.avg_age for p in self.person_profiles.values() if p.avg_age is not None]
        avg_age = sum(ages) / len(ages) if ages else None
        
        # 性别统计
        genders = [p.dominant_gender for p in self.person_profiles.values() 
                  if p.dominant_gender is not None]
        male_count = genders.count('Male')
        female_count = genders.count('Female')
        
        # 年龄分布统计
        age_distribution = {
            "0-17": 0, "18-25": 0, "26-35": 0, 
            "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0
        }
        
        for profile in self.person_profiles.values():
            if profile.avg_age is not None:
                age = profile.avg_age
                if age < 18:
                    age_distribution["0-17"] += 1
                elif age < 26:
                    age_distribution["18-25"] += 1
                elif age < 36:
                    age_distribution["26-35"] += 1
                elif age < 46:
                    age_distribution["36-45"] += 1
                elif age < 56:
                    age_distribution["46-55"] += 1
                elif age < 66:
                    age_distribution["56-65"] += 1
                else:
                    age_distribution["65+"] += 1
        
        return {
            'total_people': total_people,
            'active_tracks': active_tracks,
            'avg_age': avg_age,
            'male_count': male_count,
            'female_count': female_count,
            'frame_count': self.frame_count,
            'age_distribution': age_distribution
        }

def test_integrated_analyzer():
    """测试集成分析器"""
    # 初始化分析器（尝试使用InsightFace）
    analyzer = IntegratedAnalyzer(use_insightface=True)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    logger.info("开始测试集成分析，按 'q' 退出")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 处理帧
        tracks, faces, profiles = analyzer.process_frame(frame)
        
        # 绘制结果
        result_frame = analyzer.draw_integrated_results(frame, tracks, faces)
        
        # 显示统计信息
        stats = analyzer.get_statistics(tracks)
        info_lines = [
            f"Frame: {stats['frame_count']}",
            f"Total People: {stats['total_people']}",
            f"Active: {stats['active_tracks']}",
            f"Avg Age: {stats['avg_age']:.1f}" if stats['avg_age'] else "Avg Age: N/A",
            f"Male: {stats['male_count']}, Female: {stats['female_count']}"
        ]
        
        for i, line in enumerate(info_lines):
            cv2.putText(result_frame, line, (10, 30 + i * 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imshow('Integrated Analysis Test', result_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # 输出最终统计
    final_stats = analyzer.get_statistics()
    logger.info(f"测试完成 - 总人数: {final_stats['total_people']}, "
               f"平均年龄: {final_stats['avg_age']}, "
               f"男性: {final_stats['male_count']}, 女性: {final_stats['female_count']}")

if __name__ == "__main__":
    test_integrated_analyzer() 