#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试当前人数显示修复效果
"""

import cv2
import numpy as np
import time
from src.complete_analyzer import CompleteAnalyzer

def test_current_people_count():
    """测试当前人数显示修复效果"""
    print("🧪 开始测试当前人数显示修复效果...")
    print("📝 测试场景：")
    print("   1. 有人时显示正确人数")
    print("   2. 没人时立即显示0")
    print("   3. 人员进出时实时更新")
    print()
    
    # 初始化分析器
    analyzer = CompleteAnalyzer(
        session_name="当前人数修复测试",
        use_insightface=True
    )
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return
    
    print("📹 摄像头已启动，开始测试...")
    print("💡 提示：")
    print("   - 进入和离开摄像头视野观察人数变化")
    print("   - 注意当没有人时是否立即显示0")
    print("   - 按 'q' 退出测试")
    print()
    
    frame_count = 0
    last_people_count = -1
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 处理帧
            result_frame, stats = analyzer.process_frame(frame)
            
            # 获取当前人数
            current_people = stats.get('realtime', {}).get('active_tracks', 0)
            
            # 如果人数发生变化，打印日志
            if current_people != last_people_count:
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] 当前人数变化: {last_people_count} -> {current_people}")
                last_people_count = current_people
            
            # 在图像上显示详细信息
            info_lines = [
                f"Frame: {frame_count}",
                f"Current People: {current_people}",
                f"Total People: {stats.get('realtime', {}).get('total_people', 0)}",
                f"Test Status: {'PASS' if current_people >= 0 else 'FAIL'}"
            ]
            
            # 根据人数选择颜色
            if current_people == 0:
                color = (0, 255, 255)  # 黄色 - 没有人
            elif current_people > 0:
                color = (0, 255, 0)    # 绿色 - 有人
            else:
                color = (0, 0, 255)    # 红色 - 错误
            
            for i, line in enumerate(info_lines):
                y_pos = 30 + i * 25
                # 添加背景
                text_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                cv2.rectangle(result_frame, (10, y_pos - 20), 
                             (10 + text_size[0] + 10, y_pos + 5), (0, 0, 0), -1)
                # 添加文字
                cv2.putText(result_frame, line, (15, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # 添加测试说明
            instructions = [
                "Test Instructions:",
                "1. Enter/exit camera view",
                "2. Check if count updates to 0",
                "3. Press 'q' to quit"
            ]
            
            for i, instruction in enumerate(instructions):
                y_pos = result_frame.shape[0] - 80 + i * 20
                cv2.putText(result_frame, instruction, (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Current People Count Test', result_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        analyzer.close()
        
        print()
        print("🏁 测试完成！")
        print("📊 测试总结：")
        print(f"   - 总帧数: {frame_count}")
        print(f"   - 最终人数: {last_people_count}")
        print("✅ 如果人数能正确显示0，说明修复成功！")

if __name__ == "__main__":
    test_current_people_count()
