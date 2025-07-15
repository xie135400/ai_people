#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行为分析和完整系统测试脚本
集成优化的年龄分析功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import cv2
import numpy as np
import logging
from src.behavior_analyzer import BehaviorAnalyzer, Zone
from src.complete_analyzer import CompleteAnalyzer

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_behavior_analyzer_only():
    """仅测试行为分析器"""
    logger.info("=== 测试行为分析器（含优化年龄分析）===")
    
    from src.persistent_analyzer import PersistentAnalyzer
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    # 获取实际摄像头分辨率
    ret, test_frame = cap.read()
    if not ret:
        logger.error("无法读取摄像头帧")
        cap.release()
        return
    
    frame_height, frame_width = test_frame.shape[:2]
    logger.info(f"摄像头分辨率: {frame_width}x{frame_height}")
    
    # 初始化分析器（启用优化的年龄分析）
    persistent_analyzer = PersistentAnalyzer(
        session_name="行为分析测试_优化年龄",
        use_insightface=True,
        save_interval=10
    )
    
    behavior_analyzer = BehaviorAnalyzer(frame_width=frame_width, frame_height=frame_height)
    
    # 添加自定义区域示例
    custom_zone = Zone(
        name="custom_area",
        polygon=[(100, 100), (200, 100), (200, 200), (100, 200)],
        color=(255, 255, 0),
        zone_type="custom"
    )
    behavior_analyzer.add_zone(custom_zone)
    
    logger.info("开始测试行为分析（含优化年龄分析）")
    logger.info("按键说明:")
    logger.info("  'q' - 退出")
    logger.info("  'h' - 切换热力图显示")
    logger.info("  'z' - 切换区域显示")
    logger.info("  'b' - 切换行为信息显示")
    logger.info("  's' - 显示统计信息")
    logger.info("  'a' - 显示年龄分析详情")
    logger.info("  'r' - 重置年龄历史")
    
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
            
            # 显示统计信息（包含优化的年龄信息）
            behavior_summary = behavior_analyzer.get_behavior_summary()
            realtime_stats = persistent_analyzer.get_realtime_statistics()
            
            if behavior_summary:
                info_lines = [
                    f"People: {behavior_summary['total_people']}",
                    f"Avg Dwell: {behavior_summary['avg_dwell_time']:.1f}s",
                    f"Shoppers: {behavior_summary['shoppers']} ({behavior_summary['shopper_rate']:.1%})",
                    f"Browsers: {behavior_summary['browsers']} ({behavior_summary['browser_rate']:.1%})",
                    f"Avg Engagement: {behavior_summary['avg_engagement_score']:.1f}"
                ]
                
                # 添加优化的年龄信息
                if realtime_stats.get('avg_age'):
                    info_lines.append(f"Avg Age: {realtime_stats['avg_age']:.1f}")
                info_lines.append(f"Male: {realtime_stats.get('male_count', 0)}, Female: {realtime_stats.get('female_count', 0)}")
                
                for i, line in enumerate(info_lines):
                    # 添加背景提高可读性
                    text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                    cv2.rectangle(result_frame, (8, 30 + i * 20 - 15), 
                                 (12 + text_size[0], 30 + i * 20 + 5), (0, 0, 0), -1)
                    cv2.putText(result_frame, line, (10, 30 + i * 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            cv2.imshow('Behavior Analysis Test (Optimized Age)', result_frame)
            
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
                
                # 显示优化的年龄统计
                logger.info("=== 年龄分析统计 ===")
                logger.info(f"总人数: {realtime_stats.get('total_people', 0)}")
                logger.info(f"平均年龄: {realtime_stats.get('avg_age', 'N/A')}")
                logger.info(f"性别分布 - 男性: {realtime_stats.get('male_count', 0)}, 女性: {realtime_stats.get('female_count', 0)}")
            
            elif key == ord('a'):
                # 显示年龄分析详情
                face_analyzer = persistent_analyzer.analyzer.face_analyzer
                age_stats = face_analyzer.get_age_statistics()
                logger.info("=== 年龄分析详情 ===")
                logger.info(f"跟踪的人数: {age_stats['total_people_tracked']}")
                
                if 'avg_age' in age_stats and age_stats['avg_age']:
                    logger.info(f"平均年龄: {age_stats['avg_age']:.1f}")
                    logger.info(f"年龄标准差: {age_stats['age_std']:.1f}")
                
                if 'age_distribution' in age_stats and age_stats['age_distribution']:
                    logger.info("年龄分布:")
                    for age_range, count in age_stats['age_distribution'].items():
                        logger.info(f"  {age_range}: {count}人")
                
                if 'confidence_stats' in age_stats and age_stats['confidence_stats']:
                    conf_stats = age_stats['confidence_stats']
                    logger.info(f"置信度统计:")
                    logger.info(f"  平均: {conf_stats['avg_confidence']:.3f}")
                    logger.info(f"  最小: {conf_stats['min_confidence']:.3f}")
                    logger.info(f"  最大: {conf_stats['max_confidence']:.3f}")
                
                if 'quality_stats' in age_stats and age_stats['quality_stats']:
                    qual_stats = age_stats['quality_stats']
                    logger.info(f"质量统计:")
                    logger.info(f"  平均: {qual_stats['avg_quality']:.3f}")
                    logger.info(f"  最小: {qual_stats['min_quality']:.3f}")
                    logger.info(f"  最大: {qual_stats['max_quality']:.3f}")
            
            elif key == ord('r'):
                # 重置年龄历史
                face_analyzer = persistent_analyzer.analyzer.face_analyzer
                face_analyzer.age_optimizer.age_histories.clear()
                logger.info("年龄历史已重置")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        persistent_analyzer.close()

def test_complete_system():
    """测试完整AI人流分析系统（含优化年龄分析）"""
    logger.info("=== 测试完整AI人流分析系统（含优化年龄分析）===")
    
    # 获取实际摄像头分辨率
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("无法打开摄像头")
        return
    
    ret, test_frame = cap.read()
    if not ret:
        logger.error("无法读取摄像头帧")
        cap.release()
        return
    
    frame_height, frame_width = test_frame.shape[:2]
    logger.info(f"摄像头分辨率: {frame_width}x{frame_height}")
    
    # 初始化完整分析器（使用实际分辨率）
    analyzer = CompleteAnalyzer(
        session_name="完整系统测试_优化年龄",
        use_insightface=True,
        save_interval=15,
        frame_width=frame_width,
        frame_height=frame_height
    )
    
    # 添加自定义区域示例
    analyzer.add_custom_zone(
        name="vip_area",
        polygon=[(int(frame_width*0.6), int(frame_height*0.6)), 
                (int(frame_width*0.9), int(frame_height*0.6)), 
                (int(frame_width*0.9), int(frame_height*0.9)), 
                (int(frame_width*0.6), int(frame_height*0.9))],
        color=(255, 0, 255),
        zone_type="vip"
    )
    
    logger.info("开始测试完整AI人流分析系统（含优化年龄分析）")
    logger.info("按键说明:")
    logger.info("  'q' - 退出")
    logger.info("  'h' - 切换热力图显示")
    logger.info("  'z' - 切换区域显示")
    logger.info("  'b' - 切换行为信息显示")
    logger.info("  't' - 切换轨迹显示")
    logger.info("  'f' - 切换人脸显示")
    logger.info("  's' - 切换统计信息显示")
    logger.info("  'd' - 切换数据库信息显示")
    logger.info("  'a' - 显示年龄分析详情")
    logger.info("  'r' - 重置年龄历史")
    logger.info("  'e' - 导出统计信息")
    logger.info("  'p' - 显示性能指标")
    logger.info("  'SPACE' - 立即保存数据")
    
    try:
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 处理帧
            result_frame, stats = analyzer.process_frame(frame)
            
            # 显示结果
            cv2.imshow('Complete AI Analytics System (Optimized Age)', result_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('h'):
                analyzer.toggle_display_option('show_heatmap')
            elif key == ord('z'):
                analyzer.toggle_display_option('show_zones')
            elif key == ord('b'):
                analyzer.toggle_display_option('show_behavior_info')
            elif key == ord('t'):
                analyzer.toggle_display_option('show_tracks')
            elif key == ord('f'):
                analyzer.toggle_display_option('show_faces')
            elif key == ord('s'):
                analyzer.toggle_display_option('show_statistics')
            elif key == ord('d'):
                analyzer.toggle_display_option('show_db_info')
            elif key == ord('a'):
                # 显示年龄分析详情
                face_analyzer = analyzer.persistent_analyzer.analyzer.face_analyzer
                age_stats = face_analyzer.get_age_statistics()
                logger.info("=== 年龄分析详情 ===")
                logger.info(f"跟踪的人数: {age_stats['total_people_tracked']}")
                
                if 'avg_age' in age_stats and age_stats['avg_age']:
                    logger.info(f"平均年龄: {age_stats['avg_age']:.1f}")
                    logger.info(f"年龄标准差: {age_stats['age_std']:.1f}")
                
                if 'age_distribution' in age_stats and age_stats['age_distribution']:
                    logger.info("年龄分布:")
                    for age_range, count in age_stats['age_distribution'].items():
                        logger.info(f"  {age_range}: {count}人")
                
                if 'confidence_stats' in age_stats and age_stats['confidence_stats']:
                    conf_stats = age_stats['confidence_stats']
                    logger.info(f"置信度统计:")
                    logger.info(f"  平均: {conf_stats['avg_confidence']:.3f}")
                    logger.info(f"  最小: {conf_stats['min_confidence']:.3f}")
                    logger.info(f"  最大: {conf_stats['max_confidence']:.3f}")
                
                if 'quality_stats' in age_stats and age_stats['quality_stats']:
                    qual_stats = age_stats['quality_stats']
                    logger.info(f"质量统计:")
                    logger.info(f"  平均: {qual_stats['avg_quality']:.3f}")
                    logger.info(f"  最小: {qual_stats['min_quality']:.3f}")
                    logger.info(f"  最大: {qual_stats['max_quality']:.3f}")
            
            elif key == ord('r'):
                # 重置年龄历史
                face_analyzer = analyzer.persistent_analyzer.analyzer.face_analyzer
                face_analyzer.age_optimizer.age_histories.clear()
                logger.info("年龄历史已重置")
            elif key == ord('e'):
                # 导出统计信息
                filepath = analyzer.export_statistics()
                if filepath:
                    logger.info(f"✅ 统计信息已导出: {filepath}")
            elif key == ord('p'):
                # 显示性能指标
                metrics = analyzer.get_performance_metrics()
                logger.info("=== 性能指标 ===")
                for key, value in metrics.items():
                    logger.info(f"{key}: {value}")
            elif key == ord(' '):
                # 立即保存数据
                analyzer.save_current_data()
                logger.info("✅ 手动保存数据完成")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        # 显示最终统计（包含优化的年龄信息）
        final_stats = analyzer._collect_statistics()
        logger.info("=== 最终统计信息（含优化年龄分析）===")
        
        realtime = final_stats.get('realtime', {})
        behavior = final_stats.get('behavior', {})
        
        logger.info(f"总处理帧数: {realtime.get('frame_count', 0)}")
        logger.info(f"检测到的总人数: {realtime.get('total_people', 0)}")
        logger.info(f"平均年龄: {realtime.get('avg_age', 'N/A')}")
        logger.info(f"性别分布 - 男性: {realtime.get('male_count', 0)}, 女性: {realtime.get('female_count', 0)}")
        
        if behavior:
            logger.info(f"平均停留时间: {behavior.get('avg_dwell_time', 0):.1f}秒")
            logger.info(f"购物者: {behavior.get('shoppers', 0)} ({behavior.get('shopper_rate', 0):.1%})")
            logger.info(f"浏览者: {behavior.get('browsers', 0)} ({behavior.get('browser_rate', 0):.1%})")
            logger.info(f"平均参与度: {behavior.get('avg_engagement_score', 0):.1f}")
        
        # 区域统计
        zones = final_stats.get('zones', {})
        if zones:
            logger.info("=== 区域统计 ===")
            for zone_name, zone_stats in zones.items():
                logger.info(f"{zone_name}: 访问{zone_stats['total_visits']}次, "
                           f"独立访客{zone_stats['unique_visitors']}人, "
                           f"平均停留{zone_stats['avg_dwell_time']:.1f}秒")
        
        # 年龄分析详细统计
        face_analyzer = analyzer.persistent_analyzer.analyzer.face_analyzer
        age_stats = face_analyzer.get_age_statistics()
        if age_stats['total_people_tracked'] > 0:
            logger.info("=== 年龄分析最终统计 ===")
            logger.info(f"跟踪的人数: {age_stats['total_people_tracked']}")
            
            if 'avg_age' in age_stats and age_stats['avg_age']:
                logger.info(f"平均年龄: {age_stats['avg_age']:.1f} ± {age_stats['age_std']:.1f}")
            
            if 'age_distribution' in age_stats and age_stats['age_distribution']:
                logger.info("年龄分布:")
                for age_range, count in age_stats['age_distribution'].items():
                    percentage = (count / age_stats['total_people_tracked']) * 100
                    logger.info(f"  {age_range}: {count}人 ({percentage:.1f}%)")
            
            if 'confidence_stats' in age_stats and age_stats['confidence_stats']:
                conf_stats = age_stats['confidence_stats']
                logger.info(f"年龄预测置信度: {conf_stats['avg_confidence']:.3f} "
                           f"(范围: {conf_stats['min_confidence']:.3f} - {conf_stats['max_confidence']:.3f})")
        
        # 性能指标
        metrics = analyzer.get_performance_metrics()
        logger.info("=== 性能指标 ===")
        logger.info(f"检测总人数: {metrics['total_people_detected']}")
        logger.info(f"处理帧数: {metrics['frames_processed']}")
        logger.info(f"平均停留时间: {metrics['avg_dwell_time']:.1f}秒")
        logger.info(f"参与度: {metrics['engagement_rate']:.2%}")
        logger.info(f"转化率: {metrics['conversion_rate']:.2%}")
        logger.info(f"浏览率: {metrics['browse_rate']:.2%}")
        
        # 关闭分析器
        analyzer.close()

def demo_zone_configuration():
    """演示区域配置功能"""
    logger.info("=== 区域配置演示 ===")
    
    # 创建行为分析器
    behavior_analyzer = BehaviorAnalyzer(frame_width=640, frame_height=480)
    
    # 添加多个自定义区域
    zones_config = [
        {
            'name': 'entrance',
            'polygon': [(0, 0), (200, 0), (200, 150), (0, 150)],
            'color': (255, 0, 0),
            'type': 'entrance'
        },
        {
            'name': 'electronics',
            'polygon': [(200, 0), (400, 0), (400, 200), (200, 200)],
            'color': (0, 255, 0),
            'type': 'product_area'
        },
        {
            'name': 'clothing',
            'polygon': [(400, 0), (640, 0), (640, 200), (400, 200)],
            'color': (0, 0, 255),
            'type': 'product_area'
        },
        {
            'name': 'checkout',
            'polygon': [(200, 350), (640, 350), (640, 480), (200, 480)],
            'color': (255, 255, 0),
            'type': 'checkout'
        }
    ]
    
    # 清空默认区域并添加自定义区域
    behavior_analyzer.zones = []
    for zone_config in zones_config:
        zone = Zone(
            name=zone_config['name'],
            polygon=zone_config['polygon'],
            color=zone_config['color'],
            zone_type=zone_config['type']
        )
        behavior_analyzer.add_zone(zone)
    
    # 创建一个示例图像来显示区域配置
    demo_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    demo_frame = behavior_analyzer.draw_zones(demo_frame)
    
    # 添加说明文字
    cv2.putText(demo_frame, "Zone Configuration Demo", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(demo_frame, "Press any key to continue...", (10, 460), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imshow('Zone Configuration Demo', demo_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    logger.info("区域配置演示完成")

def main():
    """主函数"""
    print("选择测试模式:")
    print("1. 仅测试行为分析器")
    print("2. 测试完整AI人流分析系统")
    print("3. 区域配置演示")
    
    choice = input("请输入选择 (1, 2 或 3): ").strip()
    
    if choice == '1':
        test_behavior_analyzer_only()
    elif choice == '2':
        test_complete_system()
    elif choice == '3':
        demo_zone_configuration()
    else:
        print("无效选择，默认运行完整系统测试")
        test_complete_system()

if __name__ == "__main__":
    main() 