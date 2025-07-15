#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复导入问题的脚本
将所有相对导入改为绝对导入
"""

import os
import re

def fix_file_imports(file_path):
    """修复单个文件的导入"""
    print(f"修复文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原文件
    backup_path = file_path + '.backup_import_fix'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 替换相对导入
    replacements = [
        (r'from \.complete_analyzer import', 'from complete_analyzer import'),
        (r'from \.database import', 'from database import'),
        (r'from \.persistent_analyzer import', 'from persistent_analyzer import'),
        (r'from \.behavior_analyzer import', 'from behavior_analyzer import'),
        (r'from \.tracker import', 'from tracker import'),
        (r'from \.face_analyzer import', 'from face_analyzer import'),
        (r'from \.integrated_analyzer import', 'from integrated_analyzer import'),
        (r'from \.detector import', 'from detector import'),
        (r'from \.age_config import', 'from age_config import'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  已修复: {file_path}")

def main():
    """主函数"""
    src_dir = 'src'
    
    # 需要修复的文件列表
    files_to_fix = [
        'integrated_analyzer.py',
        'web_app.py',
        'complete_analyzer.py',
        'face_analyzer.py',
        'persistent_analyzer.py',
        'tracker.py',
        'behavior_analyzer.py'
    ]
    
    print("开始修复导入问题...")
    
    for filename in files_to_fix:
        file_path = os.path.join(src_dir, filename)
        if os.path.exists(file_path):
            fix_file_imports(file_path)
        else:
            print(f"文件不存在: {file_path}")
    
    print("导入修复完成！")
    print("现在可以使用以下命令启动应用:")
    print("python run_web_app.py --port 8443 --no-ssl")

if __name__ == "__main__":
    main() 