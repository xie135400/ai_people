#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消费行为分析模块
实现停留时间计算、区域热力图、行为模式识别等功能
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional, Any
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import math

from .integrated_analyzer import PersonProfile
from .tracker import PersonTrack

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Zone:
    """区域定义"""
    name: str
    polygon: List[Tuple[int, int]]  # 多边形顶点
    color: Tuple[int, int, int] = (0, 255, 0)
    zone_type: str = "general"  # general, entrance, checkout, product_area
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """判断点是否在区域内"""
        return cv2.pointPolygonTest(np.array(self.polygon, dtype=np.int32), point, False) >= 0

@dataclass
class BehaviorEvent:
    """行为事件"""
    person_id: int
    event_type: str  # enter_zone, exit_zone, dwell, move, stop
    zone_name: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    position: Optional[Tuple[int, int]] = None
    duration: Optional[float] = None  # 持续时间（秒）
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PersonBehavior:
    """人员行为分析结果"""
    person_id: int
    total_dwell_time: float = 0.0  # 总停留时间
    zone_visits: Dict[str, int] = field(default_factory=dict)  # 区域访问次数
    zone_dwell_times: Dict[str, float] = field(default_factory=dict)  # 各区域停留时间
    path_length: float = 0.0  # 移动路径长度
    avg_speed: float = 0.0  # 平均移动速度
    stop_count: int = 0  # 停留次数
    events: List[BehaviorEvent] = field(default_factory=list)
    
    # 行为特征
    is_browser: bool = False  # 是否为浏览者
    is_shopper: bool = False  # 是否为购物者
    engagement_score: float = 0.0  # 参与度评分

class BehaviorAnalyzer:
    """消费行为分析器"""
    
    def __init__(self, frame_width: int = 640, frame_height: int = 480):
        """
        初始化行为分析器
        
        Args:
            frame_width: 视频帧宽度
            frame_height: 视频帧高度
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # 区域定义
        self.zones: List[Zone] = []
        
        # 行为分析数据
        self.person_behaviors: Dict[int, PersonBehavior] = {}
        self.person_last_positions: Dict[int, Tuple[Tuple[int, int], datetime]] = {}
        self.person_zone_states: Dict[int, Dict[str, bool]] = {}  # 人员在各区域的状态
        
        # 热力图数据
        self.heatmap = np.zeros((frame_height, frame_width), dtype=np.float32)
        self.heatmap_decay = 0.995  # 热力图衰减系数
        
        # 行为分析参数
        self.min_stop_duration = 2.0  # 最小停留时间（秒）
        self.min_movement_distance = 10  # 最小移动距离（像素）
        self.speed_threshold = 5.0  # 速度阈值（像素/秒）
        
        # 默认区域设置
        self._setup_default_zones()
        
        logger.info("消费行为分析器初始化完成")
    
    def _setup_default_zones(self):
        """设置默认区域"""
        # 入口区域（左上角）
        entrance_zone = Zone(
            name="entrance",
            polygon=[(0, 0), (self.frame_width//3, 0), 
                    (self.frame_width//3, self.frame_height//3), (0, self.frame_height//3)],
            color=(255, 0, 0),
            zone_type="entrance"
        )
        
        # 商品区域（中央）
        product_zone = Zone(
            name="product_area",
            polygon=[(self.frame_width//3, self.frame_height//3), 
                    (2*self.frame_width//3, self.frame_height//3),
                    (2*self.frame_width//3, 2*self.frame_height//3), 
                    (self.frame_width//3, 2*self.frame_height//3)],
            color=(0, 255, 0),
            zone_type="product_area"
        )
        
        # 结账区域（右下角）
        checkout_zone = Zone(
            name="checkout",
            polygon=[(2*self.frame_width//3, 2*self.frame_height//3), 
                    (self.frame_width, 2*self.frame_height//3),
                    (self.frame_width, self.frame_height), 
                    (2*self.frame_width//3, self.frame_height)],
            color=(0, 0, 255),
            zone_type="checkout"
        )
        
        self.zones = [entrance_zone, product_zone, checkout_zone]
    
    def add_zone(self, zone: Zone):
        """添加自定义区域"""
        self.zones.append(zone)
        logger.info(f"添加区域: {zone.name}")
    
    def update_behavior_analysis(self, tracks: List[PersonTrack], profiles: Dict[int, PersonProfile]):
        """
        更新行为分析
        
        Args:
            tracks: 当前轨迹列表
            profiles: 人员档案字典
        """
        current_time = datetime.now()
        
        # 更新热力图
        self._update_heatmap(tracks)
        
        # 分析每个人的行为
        for track in tracks:
            person_id = track.track_id
            position = track.center
            
            # 初始化人员行为数据
            if person_id not in self.person_behaviors:
                self.person_behaviors[person_id] = PersonBehavior(person_id=person_id)
                self.person_zone_states[person_id] = {zone.name: False for zone in self.zones}
            
            behavior = self.person_behaviors[person_id]
            
            # 分析移动和停留
            self._analyze_movement(person_id, position, current_time)
            
            # 分析区域访问
            self._analyze_zone_visits(person_id, position, current_time)
            
            # 更新总停留时间
            if person_id in profiles:
                profile = profiles[person_id]
                behavior.total_dwell_time = (current_time - profile.first_seen).total_seconds()
        
        # 计算行为特征
        self._calculate_behavior_features()
    
    def _update_heatmap(self, tracks: List[PersonTrack]):
        """更新热力图"""
        # 衰减现有热力图
        self.heatmap *= self.heatmap_decay
        
        # 添加当前位置的热度
        for track in tracks:
            x, y = track.center
            if 0 <= x < self.frame_width and 0 <= y < self.frame_height:
                # 使用高斯分布添加热度
                self._add_gaussian_heat(x, y, intensity=1.0, radius=20)
    
    def _add_gaussian_heat(self, x: int, y: int, intensity: float = 1.0, radius: int = 20):
        """在热力图上添加高斯热度"""
        y_min = max(0, y - radius)
        y_max = min(self.frame_height, y + radius + 1)
        x_min = max(0, x - radius)
        x_max = min(self.frame_width, x + radius + 1)
        
        for py in range(y_min, y_max):
            for px in range(x_min, x_max):
                distance = math.sqrt((px - x) ** 2 + (py - y) ** 2)
                if distance <= radius:
                    heat = intensity * math.exp(-(distance ** 2) / (2 * (radius / 3) ** 2))
                    self.heatmap[py, px] += heat
    
    def _analyze_movement(self, person_id: int, position: Tuple[int, int], current_time: datetime):
        """分析人员移动行为"""
        behavior = self.person_behaviors[person_id]
        
        if person_id in self.person_last_positions:
            last_pos, last_time = self.person_last_positions[person_id]
            
            # 计算移动距离和时间
            distance = math.sqrt((position[0] - last_pos[0]) ** 2 + (position[1] - last_pos[1]) ** 2)
            time_diff = (current_time - last_time).total_seconds()
            
            if time_diff > 0:
                speed = distance / time_diff
                
                # 更新路径长度
                behavior.path_length += distance
                
                # 更新平均速度
                if behavior.path_length > 0:
                    behavior.avg_speed = behavior.path_length / behavior.total_dwell_time if behavior.total_dwell_time > 0 else 0
                
                # 检测停留行为
                if speed < self.speed_threshold and time_diff >= self.min_stop_duration:
                    behavior.stop_count += 1
                    
                    # 记录停留事件
                    event = BehaviorEvent(
                        person_id=person_id,
                        event_type="stop",
                        timestamp=current_time,
                        position=position,
                        duration=time_diff,
                        metadata={"speed": speed, "distance": distance}
                    )
                    behavior.events.append(event)
        
        # 更新最后位置
        self.person_last_positions[person_id] = (position, current_time)
    
    def _analyze_zone_visits(self, person_id: int, position: Tuple[int, int], current_time: datetime):
        """分析区域访问行为"""
        behavior = self.person_behaviors[person_id]
        zone_states = self.person_zone_states[person_id]
        
        for zone in self.zones:
            is_in_zone = zone.contains_point(position)
            was_in_zone = zone_states[zone.name]
            
            if is_in_zone and not was_in_zone:
                # 进入区域
                behavior.zone_visits[zone.name] = behavior.zone_visits.get(zone.name, 0) + 1
                
                event = BehaviorEvent(
                    person_id=person_id,
                    event_type="enter_zone",
                    zone_name=zone.name,
                    timestamp=current_time,
                    position=position
                )
                behavior.events.append(event)
                
            elif not is_in_zone and was_in_zone:
                # 离开区域
                event = BehaviorEvent(
                    person_id=person_id,
                    event_type="exit_zone",
                    zone_name=zone.name,
                    timestamp=current_time,
                    position=position
                )
                behavior.events.append(event)
            
            elif is_in_zone:
                # 在区域内停留
                behavior.zone_dwell_times[zone.name] = behavior.zone_dwell_times.get(zone.name, 0) + 0.1  # 假设每次更新0.1秒
            
            zone_states[zone.name] = is_in_zone
    
    def _calculate_behavior_features(self):
        """计算行为特征"""
        for person_id, behavior in self.person_behaviors.items():
            # 计算参与度评分
            engagement_score = 0.0
            
            # 基于停留时间
            if behavior.total_dwell_time > 30:  # 超过30秒
                engagement_score += min(behavior.total_dwell_time / 300, 1.0) * 30  # 最多30分
            
            # 基于区域访问
            zone_visit_score = min(len(behavior.zone_visits) * 10, 30)  # 最多30分
            engagement_score += zone_visit_score
            
            # 基于停留次数
            stop_score = min(behavior.stop_count * 5, 20)  # 最多20分
            engagement_score += stop_score
            
            # 基于移动路径
            if behavior.path_length > 100:  # 移动距离超过100像素
                path_score = min(behavior.path_length / 1000 * 20, 20)  # 最多20分
                engagement_score += path_score
            
            behavior.engagement_score = engagement_score
            
            # 判断行为类型
            if behavior.total_dwell_time > 60 and len(behavior.zone_visits) >= 2:
                behavior.is_shopper = True
            elif behavior.total_dwell_time > 30 and behavior.stop_count >= 2:
                behavior.is_browser = True
    
    def get_zone_statistics(self) -> Dict[str, Dict]:
        """获取区域统计信息"""
        zone_stats = {}
        
        for zone in self.zones:
            stats = {
                'name': zone.name,
                'type': zone.zone_type,
                'total_visits': 0,
                'total_dwell_time': 0.0,
                'unique_visitors': set(),
                'avg_dwell_time': 0.0
            }
            
            for behavior in self.person_behaviors.values():
                if zone.name in behavior.zone_visits:
                    stats['total_visits'] += behavior.zone_visits[zone.name]
                    stats['unique_visitors'].add(behavior.person_id)
                
                if zone.name in behavior.zone_dwell_times:
                    stats['total_dwell_time'] += behavior.zone_dwell_times[zone.name]
            
            stats['unique_visitors'] = len(stats['unique_visitors'])
            if stats['unique_visitors'] > 0:
                stats['avg_dwell_time'] = stats['total_dwell_time'] / stats['unique_visitors']
            
            zone_stats[zone.name] = stats
        
        return zone_stats
    
    def get_behavior_summary(self) -> Dict:
        """获取行为分析摘要"""
        if not self.person_behaviors:
            return {}
        
        total_people = len(self.person_behaviors)
        
        # 计算平均值
        avg_dwell_time = sum(b.total_dwell_time for b in self.person_behaviors.values()) / total_people
        avg_path_length = sum(b.path_length for b in self.person_behaviors.values()) / total_people
        avg_engagement = sum(b.engagement_score for b in self.person_behaviors.values()) / total_people
        
        # 统计行为类型
        shoppers = sum(1 for b in self.person_behaviors.values() if b.is_shopper)
        browsers = sum(1 for b in self.person_behaviors.values() if b.is_browser)
        
        return {
            'total_people': total_people,
            'avg_dwell_time': avg_dwell_time,
            'avg_path_length': avg_path_length,
            'avg_engagement_score': avg_engagement,
            'shoppers': shoppers,
            'browsers': browsers,
            'shopper_rate': shoppers / total_people if total_people > 0 else 0,
            'browser_rate': browsers / total_people if total_people > 0 else 0
        }
    
    def draw_zones(self, frame: np.ndarray) -> np.ndarray:
        """绘制区域"""
        result_frame = frame.copy()
        
        for zone in self.zones:
            # 绘制区域边界
            pts = np.array(zone.polygon, dtype=np.int32)
            cv2.polylines(result_frame, [pts], True, zone.color, 2)
            
            # 绘制区域名称
            center_x = int(np.mean([p[0] for p in zone.polygon]))
            center_y = int(np.mean([p[1] for p in zone.polygon]))
            
            cv2.putText(result_frame, zone.name, (center_x - 30, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, zone.color, 2)
        
        return result_frame
    
    def draw_heatmap(self, frame: np.ndarray, alpha: float = 0.6) -> np.ndarray:
        """绘制热力图"""
        # 获取原始帧的尺寸
        frame_height, frame_width = frame.shape[:2]
        
        # 如果热力图尺寸与帧尺寸不匹配，调整热力图尺寸
        if self.heatmap.shape != (frame_height, frame_width):
            # 重新调整热力图尺寸
            self.heatmap = cv2.resize(self.heatmap, (frame_width, frame_height))
        
        # 归一化热力图
        if np.max(self.heatmap) > 0:
            normalized_heatmap = (self.heatmap / np.max(self.heatmap) * 255).astype(np.uint8)
        else:
            normalized_heatmap = self.heatmap.astype(np.uint8)
        
        # 应用颜色映射
        heatmap_colored = cv2.applyColorMap(normalized_heatmap, cv2.COLORMAP_JET)
        
        # 确保热力图和原始帧具有相同的通道数
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            # 原始帧是3通道彩色图像
            if len(heatmap_colored.shape) == 2:
                # 热力图是单通道，转换为3通道
                heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_GRAY2BGR)
        elif len(frame.shape) == 2:
            # 原始帧是单通道灰度图像
            if len(heatmap_colored.shape) == 3:
                # 热力图是3通道，转换为单通道
                heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2GRAY)
        
        # 确保尺寸完全匹配
        if heatmap_colored.shape != frame.shape:
            heatmap_colored = cv2.resize(heatmap_colored, (frame_width, frame_height))
            if len(frame.shape) == 3 and len(heatmap_colored.shape) == 2:
                heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_GRAY2BGR)
            elif len(frame.shape) == 2 and len(heatmap_colored.shape) == 3:
                heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2GRAY)
        
        # 与原图像混合
        try:
            result_frame = cv2.addWeighted(frame, 1 - alpha, heatmap_colored, alpha, 0)
        except cv2.error as e:
            logger.warning(f"热力图混合失败: {e}")
            logger.warning(f"原始帧形状: {frame.shape}, 热力图形状: {heatmap_colored.shape}")
            # 如果混合失败，返回原始帧
            result_frame = frame.copy()
        
        return result_frame
    
    def draw_behavior_info(self, frame: np.ndarray, tracks: List[PersonTrack]) -> np.ndarray:
        """绘制行为信息"""
        result_frame = frame.copy()
        
        for track in tracks:
            person_id = track.track_id
            if person_id in self.person_behaviors:
                behavior = self.person_behaviors[person_id]
                x1, y1, x2, y2 = track.bbox
                
                # 准备行为信息
                info_lines = []
                info_lines.append(f"ID: {person_id}")
                info_lines.append(f"Dwell: {behavior.total_dwell_time:.1f}s")
                info_lines.append(f"Stops: {behavior.stop_count}")
                info_lines.append(f"Engagement: {behavior.engagement_score:.1f}")
                
                if behavior.is_shopper:
                    info_lines.append("Type: Shopper")
                elif behavior.is_browser:
                    info_lines.append("Type: Browser")
                
                # 绘制信息
                for i, line in enumerate(info_lines):
                    y_pos = y1 - 10 - (len(info_lines) - i - 1) * 15
                    if y_pos < 15:
                        y_pos = y2 + 15 + i * 15
                    
                    cv2.putText(result_frame, line, (x1, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        return result_frame

def test_behavior_analyzer():
    """测试行为分析器"""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    from src.persistent_analyzer import PersistentAnalyzer
    
    # 初始化分析器
    persistent_analyzer = PersistentAnalyzer(
        session_name="行为分析测试",
        use_insightface=True,
        save_interval=10
    )
    
    behavior_analyzer = BehaviorAnalyzer(frame_width=640, frame_height=480)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    logger.info("开始测试行为分析")
    logger.info("按键说明:")
    logger.info("  'q' - 退出")
    logger.info("  'h' - 切换热力图显示")
    logger.info("  'z' - 切换区域显示")
    logger.info("  'b' - 切换行为信息显示")
    logger.info("  's' - 显示统计信息")
    
    show_heatmap = False
    show_zones = True
    show_behavior = True
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 处理帧
            tracks, faces, profiles = persistent_analyzer.process_frame(frame)
            
            # 更新行为分析
            behavior_analyzer.update_behavior_analysis(tracks, profiles)
            
            # 绘制结果
            result_frame = persistent_analyzer.draw_results(frame, tracks, faces, show_db_info=False)
            
            # 绘制区域
            if show_zones:
                result_frame = behavior_analyzer.draw_zones(result_frame)
            
            # 绘制热力图
            if show_heatmap:
                result_frame = behavior_analyzer.draw_heatmap(result_frame)
            
            # 绘制行为信息
            if show_behavior:
                result_frame = behavior_analyzer.draw_behavior_info(result_frame, tracks)
            
            # 显示统计信息
            behavior_summary = behavior_analyzer.get_behavior_summary()
            if behavior_summary:
                info_lines = [
                    f"People: {behavior_summary['total_people']}",
                    f"Avg Dwell: {behavior_summary['avg_dwell_time']:.1f}s",
                    f"Shoppers: {behavior_summary['shoppers']} ({behavior_summary['shopper_rate']:.1%})",
                    f"Browsers: {behavior_summary['browsers']} ({behavior_summary['browser_rate']:.1%})",
                    f"Avg Engagement: {behavior_summary['avg_engagement_score']:.1f}"
                ]
                
                for i, line in enumerate(info_lines):
                    cv2.putText(result_frame, line, (10, 30 + i * 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            cv2.imshow('Behavior Analysis Test', result_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('h'):
                show_heatmap = not show_heatmap
                logger.info(f"热力图显示: {'开启' if show_heatmap else '关闭'}")
            elif key == ord('z'):
                show_zones = not show_zones
                logger.info(f"区域显示: {'开启' if show_zones else '关闭'}")
            elif key == ord('b'):
                show_behavior = not show_behavior
                logger.info(f"行为信息显示: {'开启' if show_behavior else '关闭'}")
            elif key == ord('s'):
                # 显示详细统计
                zone_stats = behavior_analyzer.get_zone_statistics()
                logger.info("=== 区域统计 ===")
                for zone_name, stats in zone_stats.items():
                    logger.info(f"{zone_name}: 访问{stats['total_visits']}次, "
                               f"独立访客{stats['unique_visitors']}人, "
                               f"平均停留{stats['avg_dwell_time']:.1f}秒")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        persistent_analyzer.close()

if __name__ == "__main__":
    test_behavior_analyzer() 