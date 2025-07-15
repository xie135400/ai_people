#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试当前人数显示修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.integrated_analyzer import IntegratedAnalyzer
import numpy as np

def test_fix():
    """快速测试修复效果"""
    print("🧪 快速测试当前人数显示修复...")
    
    # 初始化分析器
    analyzer = IntegratedAnalyzer(use_insightface=False)  # 不使用InsightFace以加快测试
    
    # 创建一个空的测试图像
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    print("📝 测试场景1：空图像（无人员）")
    tracks, faces, profiles = analyzer.process_frame(test_frame)
    stats = analyzer.get_statistics(tracks)
    
    print(f"   当前轨迹数: {len(tracks)}")
    print(f"   当前人数 (active_tracks): {stats['active_tracks']}")
    print(f"   总人数 (total_people): {stats['total_people']}")
    
    # 验证结果
    if stats['active_tracks'] == 0:
        print("   ✅ 测试通过：没有人时正确显示0")
    else:
        print("   ❌ 测试失败：没有人时未显示0")
    
    print()
    print("📝 测试场景2：模拟有人员的情况")
    
    # 模拟检测结果（假设有2个人）
    from src.tracker import PersonTrack
    from datetime import datetime
    
    mock_tracks = [
        PersonTrack(
            track_id=1,
            bbox=(100, 100, 200, 300),
            confidence=0.9,
            center=(150, 200),
            timestamp=datetime.now(),
            age=1
        ),
        PersonTrack(
            track_id=2,
            bbox=(300, 100, 400, 300),
            confidence=0.8,
            center=(350, 200),
            timestamp=datetime.now(),
            age=1
        )
    ]
    
    # 手动设置当前轨迹
    analyzer._current_tracks = mock_tracks
    
    # 获取统计信息
    stats = analyzer.get_statistics(mock_tracks)
    
    print(f"   模拟轨迹数: {len(mock_tracks)}")
    print(f"   当前人数 (active_tracks): {stats['active_tracks']}")
    print(f"   总人数 (total_people): {stats['total_people']}")
    
    # 验证结果
    if stats['active_tracks'] == 2:
        print("   ✅ 测试通过：有人时正确显示人数")
    else:
        print("   ❌ 测试失败：有人时人数显示错误")
    
    print()
    print("📝 测试场景3：人员离开后（空轨迹）")
    
    # 清空轨迹
    empty_tracks = []
    stats = analyzer.get_statistics(empty_tracks)
    
    print(f"   当前轨迹数: {len(empty_tracks)}")
    print(f"   当前人数 (active_tracks): {stats['active_tracks']}")
    print(f"   总人数 (total_people): {stats['total_people']}")
    
    # 验证结果
    if stats['active_tracks'] == 0:
        print("   ✅ 测试通过：人员离开后正确显示0")
    else:
        print("   ❌ 测试失败：人员离开后未显示0")
    
    print()
    print("🎯 测试总结")
    print("=" * 40)
    print("修复内容：")
    print("  - 当前人数基于当前帧轨迹数量计算")
    print("  - 不再依赖历史档案的时间判断")
    print("  - 确保没有人时立即显示0")
    print()
    print("预期效果：")
    print("  ✅ 有人时显示正确人数")
    print("  ✅ 没人时立即显示0")
    print("  ✅ 人员进出时实时更新")
    print()
    print("🚀 修复已完成，可以启动Web应用测试实际效果！")
    print("   运行: python src/web_app.py")

if __name__ == "__main__":
    test_fix() 