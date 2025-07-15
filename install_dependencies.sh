#!/bin/bash
# AI人流分析系统 - 依赖安装脚本

echo "开始安装依赖..."

# 第一步：升级pip
echo "=== 第一步：升级pip ==="
pip install --upgrade pip

# 第二步：安装基础依赖
echo "=== 第二步：安装基础依赖 ==="
pip install numpy Cython wheel setuptools

# 第三步：检测并安装PyTorch
echo "=== 第三步：安装PyTorch ==="
echo "检测CUDA版本..."
if command -v nvidia-smi &> /dev/null; then
    echo "检测到NVIDIA GPU，安装GPU版本PyTorch"
    pip install torch torchvision torchaudio
else
    echo "未检测到NVIDIA GPU，安装CPU版本PyTorch"
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# 第四步：安装其他依赖
echo "=== 第四步：安装其他依赖 ==="
pip install opencv-python ultralytics fastapi uvicorn pandas deep_sort_realtime

# 第五步：单独安装insightface
echo "=== 第五步：安装insightface ==="
# 方法1：尝试直接安装
pip install insightface

# 如果上面失败，尝试从conda安装
if [ $? -ne 0 ]; then
    echo "pip安装失败，尝试conda安装..."
    conda install -c conda-forge insightface
fi

# 如果还是失败，提供替代方案
if [ $? -ne 0 ]; then
    echo "insightface安装失败，请手动安装："
    echo "1. conda install -c conda-forge insightface"
    echo "2. 或者使用预编译版本："
    echo "   pip install insightface-package"
    echo "3. 或者跳过insightface，使用opencv的人脸检测"
fi

echo "=== 安装完成 ==="
echo "运行 python test_environment.py 测试环境" 