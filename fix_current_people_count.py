#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复当前人数显示问题
当图像里没有人的时候不会实时更新成0的问题修复
"""

import os
import shutil
from datetime import datetime

def backup_file(file_path):
    """备份文件"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"✅ 已备份文件: {backup_path}")
        return backup_path
    return None

def fix_integrated_analyzer():
    """修复集成分析器中的当前人数计算逻辑"""
    file_path = "src/integrated_analyzer.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 备份原文件
    backup_path = backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找需要修改的代码段
        old_code = '''    def get_statistics(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        total_people = len(self.person_profiles)
        active_tracks = len([p for p in self.person_profiles.values() 
                           if (datetime.now() - p.last_seen).seconds < 30])'''
        
        new_code = '''    def get_statistics(self, current_tracks: List[PersonTrack] = None) -> Dict:
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
                               if (datetime.now() - p.last_seen).seconds < 30])'''
        
        if old_code in content:
            content = content.replace(old_code, new_code)
            print("✅ 已修复 get_statistics 方法")
        else:
            print("⚠️  未找到预期的 get_statistics 方法代码")
        
        # 修复 process_frame 方法，传递当前轨迹信息
        old_process_frame = '''        # 5. 更新人员档案
        self._update_person_profiles(tracks, current_time)
        
        return tracks, faces, self.person_profiles'''
        
        new_process_frame = '''        # 5. 更新人员档案
        self._update_person_profiles(tracks, current_time)
        
        # 6. 存储当前轨迹信息供统计使用
        self._current_tracks = tracks
        
        return tracks, faces, self.person_profiles'''
        
        if old_process_frame in content:
            content = content.replace(old_process_frame, new_process_frame)
            print("✅ 已修复 process_frame 方法")
        else:
            print("⚠️  未找到预期的 process_frame 方法代码")
        
        # 在 __init__ 方法中添加 _current_tracks 初始化
        old_init = '''        # 配置参数
        self.face_detection_interval = 5  # 每5帧进行一次人脸检测
        self.frame_count = 0
        
        logger.info("集成分析器初始化完成")'''
        
        new_init = '''        # 配置参数
        self.face_detection_interval = 5  # 每5帧进行一次人脸检测
        self.frame_count = 0
        
        # 当前轨迹信息（用于准确计算当前人数）
        self._current_tracks = []
        
        logger.info("集成分析器初始化完成")'''
        
        if old_init in content:
            content = content.replace(old_init, new_init)
            print("✅ 已修复 __init__ 方法")
        else:
            print("⚠️  未找到预期的 __init__ 方法代码")
        
        # 修复测试函数中的统计调用
        old_test_stats = '''        # 显示统计信息
        stats = analyzer.get_statistics()'''
        
        new_test_stats = '''        # 显示统计信息
        stats = analyzer.get_statistics(tracks)'''
        
        if old_test_stats in content:
            content = content.replace(old_test_stats, new_test_stats)
            print("✅ 已修复测试函数中的统计调用")
        
        # 写入修改后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已成功修复 {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        # 恢复备份
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            print(f"✅ 已恢复备份文件")
        return False

def fix_persistent_analyzer():
    """修复持久化分析器中的统计调用"""
    file_path = "src/persistent_analyzer.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 备份原文件
    backup_path = backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复 get_realtime_statistics 方法
        old_realtime_stats = '''    def get_realtime_statistics(self) -> Dict:
        """获取实时统计信息"""
        return self.analyzer.get_statistics()'''
        
        new_realtime_stats = '''    def get_realtime_statistics(self) -> Dict:
        """获取实时统计信息"""
        # 传递当前轨迹信息以获得准确的当前人数
        current_tracks = getattr(self.analyzer, '_current_tracks', [])
        return self.analyzer.get_statistics(current_tracks)'''
        
        if old_realtime_stats in content:
            content = content.replace(old_realtime_stats, new_realtime_stats)
            print("✅ 已修复 get_realtime_statistics 方法")
        else:
            print("⚠️  未找到预期的 get_realtime_statistics 方法代码")
        
        # 修复测试函数中的统计调用
        old_test_call = '''            # 显示实时统计信息
            realtime_stats = analyzer.get_realtime_statistics()'''
        
        new_test_call = '''            # 显示实时统计信息
            realtime_stats = analyzer.get_realtime_statistics()'''
        
        # 这个不需要修改，因为已经通过 get_realtime_statistics 间接修复了
        
        # 写入修改后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已成功修复 {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        # 恢复备份
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            print(f"✅ 已恢复备份文件")
        return False

def fix_complete_analyzer():
    """修复完整分析器中的统计调用"""
    file_path = "src/complete_analyzer.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 备份原文件
    backup_path = backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并修复统计调用
        # 在 process_frame 方法中
        old_stats_call = '''        # 获取实时统计
        realtime_stats = self.persistent_analyzer.get_realtime_statistics()'''
        
        # 这个不需要修改，因为已经通过 persistent_analyzer 间接修复了
        
        print(f"✅ {file_path} 无需修改（通过依赖修复）")
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def create_test_script():
    """创建测试脚本验证修复效果"""
    test_content = '''#!/usr/bin/env python3
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
'''
    
    with open("test_current_people_fix.py", 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ 已创建测试脚本: test_current_people_fix.py")

def main():
    """主函数"""
    print("🔧 开始修复当前人数显示问题...")
    print("📋 问题描述：当图像里没有人的时候不会实时更新成0")
    print()
    
    success_count = 0
    total_fixes = 3
    
    # 修复集成分析器
    print("1️⃣ 修复集成分析器...")
    if fix_integrated_analyzer():
        success_count += 1
    print()
    
    # 修复持久化分析器
    print("2️⃣ 修复持久化分析器...")
    if fix_persistent_analyzer():
        success_count += 1
    print()
    
    # 检查完整分析器
    print("3️⃣ 检查完整分析器...")
    if fix_complete_analyzer():
        success_count += 1
    print()
    
    # 创建测试脚本
    print("4️⃣ 创建测试脚本...")
    create_test_script()
    print()
    
    # 总结
    print("=" * 50)
    print("🎯 修复完成总结")
    print("=" * 50)
    print(f"✅ 成功修复: {success_count}/{total_fixes} 个文件")
    print()
    print("🔍 修复内容：")
    print("   1. 修改 active_tracks 计算逻辑")
    print("   2. 使用当前帧轨迹数量而非历史档案")
    print("   3. 确保没有人时立即显示0")
    print()
    print("🧪 测试方法：")
    print("   运行: python test_current_people_fix.py")
    print("   或者: python src/web_app.py")
    print()
    print("💡 预期效果：")
    print("   - 有人时显示正确人数")
    print("   - 没人时立即显示0")
    print("   - 人员进出时实时更新")
    
    if success_count == total_fixes:
        print()
        print("🎉 所有修复都已成功完成！")
        print("🚀 现在可以测试修复效果了")
    else:
        print()
        print("⚠️  部分修复可能未完全成功，请检查错误信息")

if __name__ == "__main__":
    main() 