#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析记录查看器
查看和管理保存的分析记录
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path

def view_database_records():
    """查看数据库中的记录"""
    db_path = "data/analytics.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查看会话表
        print("=== 分析会话 ===")
        cursor.execute("SELECT * FROM sessions ORDER BY start_time DESC LIMIT 10")
        sessions = cursor.fetchall()
        
        if sessions:
            print(f"{'ID':<5} {'会话名称':<30} {'开始时间':<20} {'结束时间':<20}")
            print("-" * 80)
            for session in sessions:
                session_id, session_name, start_time, end_time = session
                print(f"{session_id:<5} {session_name:<30} {start_time:<20} {end_time or '运行中':<20}")
        else:
            print("没有找到会话记录")
        
        # 查看分析记录表
        print("\n=== 分析记录 ===")
        cursor.execute("""
            SELECT ar.id, ar.record_name, ar.timestamp, ar.total_people, ar.avg_age, 
                   ar.male_count, ar.female_count, s.session_name
            FROM analysis_records ar
            LEFT JOIN sessions s ON ar.session_id = s.id
            ORDER BY ar.timestamp DESC LIMIT 10
        """)
        records = cursor.fetchall()
        
        if records:
            print(f"{'ID':<5} {'记录名称':<25} {'时间':<20} {'人数':<6} {'平均年龄':<8} {'男性':<6} {'女性':<6} {'会话':<20}")
            print("-" * 110)
            for record in records:
                record_id, record_name, timestamp, total_people, avg_age, male_count, female_count, session_name = record
                avg_age_str = f"{avg_age:.1f}" if avg_age else "N/A"
                print(f"{record_id:<5} {record_name:<25} {timestamp:<20} {total_people:<6} {avg_age_str:<8} {male_count:<6} {female_count:<6} {session_name:<20}")
        else:
            print("没有找到分析记录")
        
        conn.close()
        
    except Exception as e:
        print(f"查看数据库记录失败: {e}")

def view_json_records():
    """查看JSON文件中的记录"""
    records_dir = Path("data/analysis_records")
    
    if not records_dir.exists():
        print(f"分析记录目录不存在: {records_dir}")
        return
    
    json_files = list(records_dir.glob("*.json"))
    
    if not json_files:
        print("没有找到JSON分析记录文件")
        return
    
    print("\n=== JSON分析记录文件 ===")
    print(f"{'文件名':<50} {'大小':<10} {'修改时间':<20}")
    print("-" * 80)
    
    for json_file in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True):
        size = json_file.stat().st_size
        mtime = datetime.fromtimestamp(json_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{json_file.name:<50} {size:<10} {mtime:<20}")
    
    # 显示最新记录的详细信息
    if json_files:
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
        print(f"\n=== 最新记录详情: {latest_file.name} ===")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"记录名称: {data.get('record_name', 'N/A')}")
            print(f"时间戳: {data.get('timestamp', 'N/A')}")
            print(f"总人数: {data.get('total_people', 'N/A')}")
            print(f"当前人数: {data.get('active_tracks', 'N/A')}")
            print(f"平均年龄: {data.get('avg_age', 'N/A')}")
            print(f"男性人数: {data.get('male_count', 'N/A')}")
            print(f"女性人数: {data.get('female_count', 'N/A')}")
            
            # 显示年龄分布
            age_distribution = data.get('age_distribution', {})
            if age_distribution:
                print(f"年龄分布: {age_distribution}")
            
            # 显示行为分析
            behavior_analysis = data.get('behavior_analysis', {})
            if behavior_analysis:
                print(f"行为分析: {behavior_analysis}")
                
        except Exception as e:
            print(f"读取记录文件失败: {e}")

def main():
    """主函数"""
    print("AI人流分析记录查看器")
    print("=" * 50)
    
    # 查看数据库记录
    view_database_records()
    
    # 查看JSON记录
    view_json_records()
    
    print("\n" + "=" * 50)
    print("记录查看完成")
    print("你可以在Web界面中重新开始分析，之前的数据都已保存")

if __name__ == "__main__":
    main() 