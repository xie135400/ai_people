#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的年龄分析功能
比较优化前后的年龄识别准确性
"""

import cv2
import numpy as np
import os
import time
import json
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional

# 导入人脸分析器
from src.face_analyzer import FaceAnalyzer
from src.age_config import get_age_correction_factors

# 测试图像目录
TEST_IMAGES_DIR = "data/test_images"

# 测试结果保存目录
RESULTS_DIR = "data/analysis_records"

def ensure_dir(directory):
    """确保目录存在"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def load_test_data(test_data_file: str) -> Dict:
    """
    加载测试数据集
    
    Args:
        test_data_file: 测试数据文件路径
        
    Returns:
        测试数据字典
    """
    try:
        if os.path.exists(test_data_file):
            with open(test_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 如果文件不存在，返回默认测试数据
            return {
                "images": [
                    {"path": "child_male_1.jpg", "true_age": 8, "gender": "Male"},
                    {"path": "child_female_1.jpg", "true_age": 7, "gender": "Female"},
                    {"path": "teen_male_1.jpg", "true_age": 16, "gender": "Male"},
                    {"path": "teen_female_1.jpg", "true_age": 15, "gender": "Female"},
                    {"path": "young_male_1.jpg", "true_age": 24, "gender": "Male"},
                    {"path": "young_female_1.jpg", "true_age": 23, "gender": "Female"},
                    {"path": "adult_male_1.jpg", "true_age": 35, "gender": "Male"},
                    {"path": "adult_female_1.jpg", "true_age": 34, "gender": "Female"},
                    {"path": "middle_male_1.jpg", "true_age": 45, "gender": "Male"},
                    {"path": "middle_female_1.jpg", "true_age": 44, "gender": "Female"},
                    {"path": "senior_male_1.jpg", "true_age": 65, "gender": "Male"},
                    {"path": "senior_female_1.jpg", "true_age": 64, "gender": "Female"}
                ]
            }
    except Exception as e:
        print(f"加载测试数据失败: {e}")
        return {"images": []}

def test_age_accuracy(analyzer: FaceAnalyzer, image_path: str, true_age: int, 
                      true_gender: str) -> Tuple[float, float, str, float]:
    """
    测试单张图像的年龄识别准确性
    
    Args:
        analyzer: 人脸分析器
        image_path: 图像路径
        true_age: 真实年龄
        true_gender: 真实性别
        
    Returns:
        (预测年龄, 年龄误差, 预测性别, 置信度)
    """
    try:
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图像: {image_path}")
            return 0, 999, "Unknown", 0
            
        # 检测人脸
        faces = analyzer.detect_faces(image)
        
        if not faces:
            print(f"未检测到人脸: {image_path}")
            return 0, 999, "Unknown", 0
            
        # 获取最大的人脸（通常是主要人物）
        main_face = max(faces, key=lambda face: (face.bbox[2] - face.bbox[0]) * (face.bbox[3] - face.bbox[1]))
        
        # 计算年龄误差
        predicted_age = main_face.age
        age_error = abs(predicted_age - true_age)
        
        # 获取性别和置信度
        predicted_gender = main_face.gender
        confidence = main_face.age_confidence if main_face.age_confidence else 0.5
        
        return predicted_age, age_error, predicted_gender, confidence
        
    except Exception as e:
        print(f"测试图像失败: {e}")
        return 0, 999, "Unknown", 0

def run_tests(use_optimized: bool = True) -> Dict:
    """
    运行所有测试
    
    Args:
        use_optimized: 是否使用优化后的分析器
        
    Returns:
        测试结果
    """
    # 确保目录存在
    ensure_dir(TEST_IMAGES_DIR)
    ensure_dir(RESULTS_DIR)
    
    # 加载测试数据
    test_data = load_test_data(os.path.join(TEST_IMAGES_DIR, "test_data.json"))
    
    # 初始化分析器
    analyzer = FaceAnalyzer(use_insightface=True)
    
    results = {
        "overall": {"total": 0, "age_error_sum": 0, "gender_correct": 0},
        "by_age_group": {
            "children": {"total": 0, "age_error_sum": 0, "gender_correct": 0},
            "teens": {"total": 0, "age_error_sum": 0, "gender_correct": 0},
            "young_adults": {"total": 0, "age_error_sum": 0, "gender_correct": 0},
            "adults": {"total": 0, "age_error_sum": 0, "gender_correct": 0},
            "middle_aged": {"total": 0, "age_error_sum": 0, "gender_correct": 0},
            "seniors": {"total": 0, "age_error_sum": 0, "gender_correct": 0}
        },
        "by_gender": {
            "Male": {"total": 0, "age_error_sum": 0, "gender_correct": 0},
            "Female": {"total": 0, "age_error_sum": 0, "gender_correct": 0}
        },
        "detailed_results": []
    }
    
    # 获取年龄校正因子（用于日志显示）
    correction_factors = get_age_correction_factors()
    
    # 运行测试
    for image_data in test_data["images"]:
        image_path = os.path.join(TEST_IMAGES_DIR, image_data["path"])
        true_age = image_data["true_age"]
        true_gender = image_data["gender"]
        
        # 如果图像不存在，跳过
        if not os.path.exists(image_path):
            print(f"图像不存在，跳过: {image_path}")
            continue
            
        # 测试图像
        predicted_age, age_error, predicted_gender, confidence = test_age_accuracy(
            analyzer, image_path, true_age, true_gender
        )
        
        # 如果测试失败，跳过
        if age_error == 999:
            continue
            
        # 更新整体结果
        results["overall"]["total"] += 1
        results["overall"]["age_error_sum"] += age_error
        if predicted_gender == true_gender:
            results["overall"]["gender_correct"] += 1
            
        # 更新性别分组结果
        results["by_gender"][true_gender]["total"] += 1
        results["by_gender"][true_gender]["age_error_sum"] += age_error
        if predicted_gender == true_gender:
            results["by_gender"][true_gender]["gender_correct"] += 1
            
        # 更新年龄分组结果
        age_group = get_age_group(true_age)
        results["by_age_group"][age_group]["total"] += 1
        results["by_age_group"][age_group]["age_error_sum"] += age_error
        if predicted_gender == true_gender:
            results["by_age_group"][age_group]["gender_correct"] += 1
            
        # 保存详细结果
        # 查找应用的校正因子
        correction = "未知"
        if true_gender in correction_factors:
            for (min_age, max_age), factor in correction_factors[true_gender].items():
                if min_age <= true_age <= max_age:
                    correction = f"{factor:+.1f}"
                    break
                    
        results["detailed_results"].append({
            "image": image_data["path"],
            "true_age": true_age,
            "predicted_age": predicted_age,
            "age_error": age_error,
            "true_gender": true_gender,
            "predicted_gender": predicted_gender,
            "confidence": confidence,
            "age_group": age_group,
            "correction_applied": correction
        })
        
        # 打印测试结果
        print(f"图像: {image_data['path']}")
        print(f"  真实年龄: {true_age}, 预测年龄: {predicted_age}, 误差: {age_error}")
        print(f"  真实性别: {true_gender}, 预测性别: {predicted_gender}")
        print(f"  置信度: {confidence:.2f}, 校正: {correction}")
        print("-" * 50)
    
    # 计算平均误差和准确率
    if results["overall"]["total"] > 0:
        results["overall"]["avg_age_error"] = results["overall"]["age_error_sum"] / results["overall"]["total"]
        results["overall"]["gender_accuracy"] = results["overall"]["gender_correct"] / results["overall"]["total"]
        
        for gender in ["Male", "Female"]:
            if results["by_gender"][gender]["total"] > 0:
                results["by_gender"][gender]["avg_age_error"] = results["by_gender"][gender]["age_error_sum"] / results["by_gender"][gender]["total"]
                results["by_gender"][gender]["gender_accuracy"] = results["by_gender"][gender]["gender_correct"] / results["by_gender"][gender]["total"]
                
        for age_group in results["by_age_group"]:
            if results["by_age_group"][age_group]["total"] > 0:
                results["by_age_group"][age_group]["avg_age_error"] = results["by_age_group"][age_group]["age_error_sum"] / results["by_age_group"][age_group]["total"]
                results["by_age_group"][age_group]["gender_accuracy"] = results["by_age_group"][age_group]["gender_correct"] / results["by_age_group"][age_group]["total"]
    
    # 保存结果
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    result_file = os.path.join(RESULTS_DIR, f"age_test_{'optimized' if use_optimized else 'original'}_{timestamp}.json")
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"测试结果已保存到: {result_file}")
    
    return results

def get_age_group(age: int) -> str:
    """根据年龄获取年龄组"""
    if age <= 12:
        return "children"
    elif age <= 17:
        return "teens"
    elif age <= 25:
        return "young_adults"
    elif age <= 35:
        return "adults"
    elif age <= 55:
        return "middle_aged"
    else:
        return "seniors"

def plot_results(results: Dict, save_path: Optional[str] = None):
    """
    绘制测试结果图表
    
    Args:
        results: 测试结果
        save_path: 保存路径，如果为None则显示图表
    """
    # 创建图表
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. 整体年龄误差和性别准确率
    axs[0, 0].bar(['平均年龄误差', '性别准确率'], 
                [results["overall"]["avg_age_error"], results["overall"]["gender_accuracy"]])
    axs[0, 0].set_title('整体性能')
    axs[0, 0].set_ylim([0, max(results["overall"]["avg_age_error"], results["overall"]["gender_accuracy"]) * 1.2])
    
    # 2. 按性别分组的年龄误差
    gender_errors = [results["by_gender"]["Male"]["avg_age_error"], 
                    results["by_gender"]["Female"]["avg_age_error"]]
    axs[0, 1].bar(['男性', '女性'], gender_errors)
    axs[0, 1].set_title('按性别分组的年龄误差')
    axs[0, 1].set_ylim([0, max(gender_errors) * 1.2])
    
    # 3. 按年龄组分组的年龄误差
    age_groups = ['儿童', '青少年', '青年', '成年', '中年', '老年']
    age_group_errors = [
        results["by_age_group"]["children"]["avg_age_error"],
        results["by_age_group"]["teens"]["avg_age_error"],
        results["by_age_group"]["young_adults"]["avg_age_error"],
        results["by_age_group"]["adults"]["avg_age_error"],
        results["by_age_group"]["middle_aged"]["avg_age_error"],
        results["by_age_group"]["seniors"]["avg_age_error"]
    ]
    axs[1, 0].bar(age_groups, age_group_errors)
    axs[1, 0].set_title('按年龄组分组的年龄误差')
    axs[1, 0].set_ylim([0, max(age_group_errors) * 1.2])
    
    # 4. 按年龄组分组的性别准确率
    age_group_accuracy = [
        results["by_age_group"]["children"]["gender_accuracy"],
        results["by_age_group"]["teens"]["gender_accuracy"],
        results["by_age_group"]["young_adults"]["gender_accuracy"],
        results["by_age_group"]["adults"]["gender_accuracy"],
        results["by_age_group"]["middle_aged"]["gender_accuracy"],
        results["by_age_group"]["seniors"]["gender_accuracy"]
    ]
    axs[1, 1].bar(age_groups, age_group_accuracy)
    axs[1, 1].set_title('按年龄组分组的性别准确率')
    axs[1, 1].set_ylim([0, 1.0])
    
    plt.tight_layout()
    
    # 保存或显示图表
    if save_path:
        plt.savefig(save_path)
        print(f"结果图表已保存到: {save_path}")
    else:
        plt.show()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='测试优化后的年龄分析功能')
    parser.add_argument('--original', action='store_true', help='测试原始（未优化）版本')
    parser.add_argument('--plot', action='store_true', help='绘制结果图表')
    args = parser.parse_args()
    
    print("=" * 50)
    print(f"测试{'原始' if args.original else '优化'}版本的年龄分析")
    print("=" * 50)
    
    # 运行测试
    results = run_tests(not args.original)
    
    # 打印汇总结果
    print("\n测试结果汇总:")
    print(f"总样本数: {results['overall']['total']}")
    
    # 修复：检查是否有测试样本
    if results['overall']['total'] > 0:
        print(f"平均年龄误差: {results['overall']['avg_age_error']:.2f}岁")
        print(f"性别识别准确率: {results['overall']['gender_accuracy']*100:.1f}%")
        
        print("\n按性别分组结果:")
        for gender in ["Male", "Female"]:
            if results["by_gender"][gender]["total"] > 0:
                print(f"  {gender}: 样本数 {results['by_gender'][gender]['total']}, " +
                    f"平均年龄误差 {results['by_gender'][gender]['avg_age_error']:.2f}岁, " +
                    f"性别准确率 {results['by_gender'][gender]['gender_accuracy']*100:.1f}%")
        
        print("\n按年龄组分组结果:")
        age_group_names = {
            "children": "儿童(0-12)",
            "teens": "青少年(13-17)",
            "young_adults": "青年(18-25)",
            "adults": "成年(26-35)",
            "middle_aged": "中年(36-55)",
            "seniors": "老年(56+)"
        }
        for age_group, name in age_group_names.items():
            if results["by_age_group"][age_group]["total"] > 0:
                print(f"  {name}: 样本数 {results['by_age_group'][age_group]['total']}, " +
                    f"平均年龄误差 {results['by_age_group'][age_group]['avg_age_error']:.2f}岁, " +
                    f"性别准确率 {results['by_age_group'][age_group]['gender_accuracy']*100:.1f}%")
        
        # 绘制结果图表
        if args.plot:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            plot_path = os.path.join(RESULTS_DIR, f"age_test_plot_{'original' if args.original else 'optimized'}_{timestamp}.png")
            plot_results(results, plot_path)
    else:
        print("没有测试样本，请将测试图像放入 data/test_images 目录并确保 test_data.json 中的配置正确")

if __name__ == "__main__":
    main() 