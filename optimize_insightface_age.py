#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InsightFace年龄识别优化工具
用于应用高级年龄优化算法，提高年龄识别准确性
"""

import os
import sys
import time
import shutil
import logging
import argparse
from pathlib import Path
import cv2
import numpy as np
import json
from typing import Dict, Any, List, Tuple, Optional

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("age_optimizer")

# 项目路径
PROJECT_DIR = Path(__file__).parent
SRC_DIR = PROJECT_DIR / 'src'
DATA_DIR = PROJECT_DIR / 'data'
TEST_IMAGES_DIR = DATA_DIR / 'test_images'
TEST_DATA_PATH = TEST_IMAGES_DIR / 'test_data.json'
RECORDS_DIR = DATA_DIR / 'analysis_records'

# 确保目录存在
TEST_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
RECORDS_DIR.mkdir(parents=True, exist_ok=True)

class AgeOptimizer:
    """年龄优化器，用于改进InsightFace年龄分析"""
    
    def __init__(self):
        """初始化优化器"""
        self.backup_files = []
        
    def backup_file(self, file_path: Path) -> Path:
        """备份文件"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.with_suffix(f".backup_{timestamp}")
        shutil.copy2(file_path, backup_path)
        logger.info(f"已备份文件: {backup_path}")
        self.backup_files.append(backup_path)
        return backup_path
    
    def get_optimized_age_config(self) -> Dict[str, Any]:
        """获取优化后的年龄配置"""
        return {
            "age_correction_factors": {
                "Male": {
                    (0, 6): -2.2,     # 幼儿男性校正
                    (7, 12): -1.9,    # 儿童男性校正
                    (13, 15): -1.4,   # 初中男性校正
                    (16, 17): -1.1,   # 高中男性校正
                    (18, 22): -0.8,   # 大学男性校正
                    (23, 25): -0.5,   # 青年男性校正
                    (26, 30): 0.2,    # 青年男性校正
                    (31, 35): 0.5,    # 青壮年男性校正
                    (36, 40): 1.0,    # 中年男性校正
                    (41, 45): 1.5,    # 中年男性校正
                    (46, 50): 2.3,    # 中老年男性校正
                    (51, 55): 2.8,    # 中老年男性校正
                    (56, 60): 3.7,    # 老年男性校正
                    (61, 65): 4.3,    # 老年男性校正
                    (66, 70): 5.0,    # 高龄男性校正
                    (71, 80): 5.8,    # 高龄男性校正
                    (81, 100): 6.5    # 高龄男性校正
                },
                "Female": {
                    (0, 6): -1.8,     # 幼儿女性校正
                    (7, 12): -1.5,    # 儿童女性校正
                    (13, 15): -1.2,   # 初中女性校正
                    (16, 17): -0.9,   # 高中女性校正
                    (18, 22): -0.6,   # 大学女性校正
                    (23, 25): -0.3,   # 青年女性校正
                    (26, 30): 0.3,    # 青年女性校正
                    (31, 35): 0.7,    # 青壮年女性校正
                    (36, 40): 1.2,    # 中年女性校正
                    (41, 45): 1.8,    # 中年女性校正
                    (46, 50): 2.5,    # 中老年女性校正
                    (51, 55): 3.2,    # 中老年女性校正
                    (56, 60): 3.9,    # 老年女性校正
                    (61, 65): 4.5,    # 老年女性校正
                    (66, 70): 5.2,    # 高龄女性校正
                    (71, 80): 6.0,    # 高龄女性校正
                    (81, 100): 6.8    # 高龄女性校正
                }
            },
            "age_mapping": {
                (0, 2): "婴儿",
                (3, 6): "幼儿",
                (7, 12): "儿童",
                (13, 17): "青少年",
                (18, 25): "青年",
                (26, 35): "成年",
                (36, 55): "中年",
                (56, 100): "老年"
            },
            "age_history_length": 30,  # 历史记录长度
            "quality_threshold": 0.4,  # 质量阈值
            "confidence_threshold": 0.6,  # 置信度阈值
            "optimal_face_size": 120,  # 最佳人脸尺寸
            "optimal_sharpness": 100.0,  # 最佳清晰度
            "clahe_clip_limit": 2.0,  # CLAHE裁剪限制
            "clahe_grid_size": (8, 8),  # CLAHE网格大小
            "contrast_alpha": 1.1,  # 对比度系数
            "brightness_beta": 5,  # 亮度增强
            "usm_amount": 1.5,  # USM锐化程度
            "usm_radius": 2.0,  # USM锐化半径
            "denoise_h": 5,  # 降噪强度色彩
            "denoise_template_window_size": 7,  # 降噪模板窗口大小
            "denoise_search_window_size": 21  # 降噪搜索窗口大小
        }
    
    def update_age_config(self) -> bool:
        """更新年龄配置文件"""
        config_file = SRC_DIR / 'age_config.py'
        
        # 备份原始文件
        self.backup_file(config_file)
        
        # 检查文件是否已经包含优化内容
        with open(config_file, 'r') as f:
            content = f.read()
            
        if "get_age_correction_factors" in content and "(0, 6)" in content:
            logger.info("配置文件已是最新版本，无需更新")
            return False
        
        # 创建优化后的配置文件
        optimized_config = """import json
from typing import Dict, Tuple, Any, List

def get_age_correction_factors() -> Dict[str, Dict[Tuple[int, int], float]]:
    \"\"\"获取年龄校正因子
    
    返回:
        Dict[str, Dict[Tuple[int, int], float]]: 按性别和年龄段的校正因子
    \"\"\"
    return {
        "Male": {
            (0, 6): -2.2,     # 幼儿男性校正
            (7, 12): -1.9,    # 儿童男性校正
            (13, 15): -1.4,   # 初中男性校正
            (16, 17): -1.1,   # 高中男性校正
            (18, 22): -0.8,   # 大学男性校正
            (23, 25): -0.5,   # 青年男性校正
            (26, 30): 0.2,    # 青年男性校正
            (31, 35): 0.5,    # 青壮年男性校正
            (36, 40): 1.0,    # 中年男性校正
            (41, 45): 1.5,    # 中年男性校正
            (46, 50): 2.3,    # 中老年男性校正
            (51, 55): 2.8,    # 中老年男性校正
            (56, 60): 3.7,    # 老年男性校正
            (61, 65): 4.3,    # 老年男性校正
            (66, 70): 5.0,    # 高龄男性校正
            (71, 80): 5.8,    # 高龄男性校正
            (81, 100): 6.5    # 高龄男性校正
        },
        "Female": {
            (0, 6): -1.8,     # 幼儿女性校正
            (7, 12): -1.5,    # 儿童女性校正
            (13, 15): -1.2,   # 初中女性校正
            (16, 17): -0.9,   # 高中女性校正
            (18, 22): -0.6,   # 大学女性校正
            (23, 25): -0.3,   # 青年女性校正
            (26, 30): 0.3,    # 青年女性校正
            (31, 35): 0.7,    # 青壮年女性校正
            (36, 40): 1.2,    # 中年女性校正
            (41, 45): 1.8,    # 中年女性校正
            (46, 50): 2.5,    # 中老年女性校正
            (51, 55): 3.2,    # 中老年女性校正
            (56, 60): 3.9,    # 老年女性校正
            (61, 65): 4.5,    # 老年女性校正
            (66, 70): 5.2,    # 高龄女性校正
            (71, 80): 6.0,    # 高龄女性校正
            (81, 100): 6.8    # 高龄女性校正
        }
    }

def get_age_mapping() -> Dict[Tuple[int, int], str]:
    \"\"\"获取年龄映射
    
    返回:
        Dict[Tuple[int, int], str]: 年龄段到描述的映射
    \"\"\"
    return {
        (0, 2): "婴儿",
        (3, 6): "幼儿",
        (7, 12): "儿童",
        (13, 17): "青少年",
        (18, 25): "青年",
        (26, 35): "成年",
        (36, 55): "中年",
        (56, 100): "老年"
    }

def get_age_config() -> Dict[str, Any]:
    \"\"\"获取年龄分析配置
    
    返回:
        Dict[str, Any]: 年龄分析配置
    \"\"\"
    return {
        "age_history_length": 30,  # 历史记录长度
        "quality_threshold": 0.4,  # 质量阈值
        "confidence_threshold": 0.6,  # 置信度阈值
        "optimal_face_size": 120,  # 最佳人脸尺寸
        "optimal_sharpness": 100.0,  # 最佳清晰度
        "clahe_clip_limit": 2.0,  # CLAHE裁剪限制
        "clahe_grid_size": (8, 8),  # CLAHE网格大小
        "contrast_alpha": 1.1,  # 对比度系数
        "brightness_beta": 5,  # 亮度增强
        "usm_amount": 1.5,  # USM锐化程度
        "usm_radius": 2.0,  # USM锐化半径
        "denoise_h": 5,  # 降噪强度色彩
        "denoise_template_window_size": 7,  # 降噪模板窗口大小
        "denoise_search_window_size": 21  # 降噪搜索窗口大小
    }

def save_test_data(data: Dict[str, Any], file_path: str) -> None:
    \"\"\"保存测试数据
    
    参数:
        data (Dict[str, Any]): 测试数据
        file_path (str): 文件路径
    \"\"\"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_test_data(file_path: str) -> Dict[str, Any]:
    \"\"\"加载测试数据
    
    参数:
        file_path (str): 文件路径
        
    返回:
        Dict[str, Any]: 测试数据
    \"\"\"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
"""
        
        # 写入优化后的配置
        with open(config_file, 'w') as f:
            f.write(optimized_config)
            
        return True
    
    def create_test_data(self) -> None:
        """创建测试数据配置"""
        test_data = {
            "test_images": {
                "child_male_1.jpg": {"age": 8, "gender": "Male"},
                "child_female_1.jpg": {"age": 10, "gender": "Female"},
                "teen_male_1.jpg": {"age": 15, "gender": "Male"},
                "teen_female_1.jpg": {"age": 16, "gender": "Female"},
                "young_male_1.jpg": {"age": 22, "gender": "Male"},
                "young_female_1.jpg": {"age": 24, "gender": "Female"},
                "adult_male_1.jpg": {"age": 32, "gender": "Male"},
                "adult_female_1.jpg": {"age": 30, "gender": "Female"},
                "middle_male_1.jpg": {"age": 45, "gender": "Male"},
                "middle_female_1.jpg": {"age": 42, "gender": "Female"},
                "senior_male_1.jpg": {"age": 65, "gender": "Male"},
                "senior_female_1.jpg": {"age": 68, "gender": "Female"}
            }
        }
        
        # 保存测试数据
        with open(TEST_DATA_PATH, 'w') as f:
            json.dump(test_data, f, indent=4)
            
        logger.info(f"已创建测试数据配置: {TEST_DATA_PATH}")
        logger.info("请将测试图像放入测试图像目录中")
    
    def apply_optimization(self) -> None:
        """应用优化"""
        # 备份关键文件
        face_analyzer_path = SRC_DIR / 'face_analyzer.py'
        age_config_path = SRC_DIR / 'age_config.py'
        
        self.backup_file(face_analyzer_path)
        self.backup_file(age_config_path)
        
        logger.info("所有文件已成功备份，开始应用优化...")
        
        # 更新配置文件
        logger.info(f"更新配置文件: {age_config_path}")
        self.update_age_config()
        
        logger.info("优化应用完成，正在测试优化效果...")
        
        # 运行测试
        logger.info("运行优化测试...")
        os.system(f"python {PROJECT_DIR}/test_optimized_age_analysis.py")
    
    def run_interactive(self) -> None:
        """运行交互式菜单"""
        while True:
            print("\n" + "=" * 50)
            print("InsightFace年龄优化工具")
            print("=" * 50)
            print("1. 应用优化")
            print("2. 创建测试数据")
            print("3. 测试优化效果")
            print("4. 恢复备份")
            print("0. 退出")
            
            choice = input("\n请选择操作: ")
            
            if choice == "1":
                self.apply_optimization()
            elif choice == "2":
                self.create_test_data()
            elif choice == "3":
                os.system(f"python {PROJECT_DIR}/test_optimized_age_analysis.py")
            elif choice == "4":
                # 列出备份文件
                backups = list(SRC_DIR.glob("*.backup_*"))
                if not backups:
                    print("没有找到备份文件")
                    continue
                    
                print("\n可用的备份文件:")
                for i, backup in enumerate(backups):
                    print(f"{i+1}. {backup.name}")
                    
                backup_choice = input("\n请选择要恢复的备份文件编号(0取消): ")
                if backup_choice == "0":
                    continue
                    
                try:
                    idx = int(backup_choice) - 1
                    if 0 <= idx < len(backups):
                        backup_file = backups[idx]
                        original_file = SRC_DIR / backup_file.name.split(".backup_")[0]
                        shutil.copy2(backup_file, original_file)
                        print(f"已恢复文件: {original_file}")
                    else:
                        print("无效的选择")
                except ValueError:
                    print("请输入有效的数字")
            elif choice == "0":
                break
            else:
                print("无效的选择，请重试")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='InsightFace年龄优化工具')
    parser.add_argument('--apply', action='store_true', help='应用优化')
    parser.add_argument('--create-test-data', action='store_true', help='创建测试数据')
    parser.add_argument('--test', action='store_true', help='测试优化效果')
    
    args = parser.parse_args()
    
    optimizer = AgeOptimizer()
    
    if args.apply:
        optimizer.apply_optimization()
        logger.info("年龄优化应用完成！")
    elif args.create_test_data:
        optimizer.create_test_data()
    elif args.test:
        os.system(f"python {PROJECT_DIR}/test_optimized_age_analysis.py")
    else:
        optimizer.run_interactive()

if __name__ == "__main__":
    main() 