# AI人流分析系统

<div align="center">
  <img src="static/placeholder.jpg" alt="AI人流分析系统" width="600"/>
  <p>基于YOLO + DeepSORT + InsightFace的智能零售分析系统</p>
</div>

## 📋 项目概述

AI人流分析系统是一个智能零售分析解决方案，结合了计算机视觉和深度学习技术，用于分析店内顾客行为、人流量和人口统计数据。系统可以帮助零售商了解顾客的购物习惯、店内热门区域，并提供数据驱动的决策支持。

### 🌟 核心功能

- **人员检测与跟踪**：使用YOLOv8进行高精度人员检测，DeepSORT算法实现多目标跟踪
- **人脸分析**：通过InsightFace进行人脸检测、年龄和性别识别
- **行为分析**：分析顾客停留时间、移动轨迹、区域热力图等
- **数据存储**：使用SQLite数据库存储分析数据，支持历史查询和趋势分析
- **实时监控**：基于FastAPI的Web界面，支持实时数据可视化和分析
- **多区域分析**：支持自定义区域划分，分析不同区域的客流情况

## 🔧 技术架构

系统采用模块化设计，主要组件包括：

```
CompleteAnalyzer (完整分析器)
├── PersistentAnalyzer (持久化分析器)
│   ├── IntegratedAnalyzer (集成分析器)
│   │   ├── PersonDetector (人员检测)
│   │   ├── PersonTracker (人员跟踪)
│   │   └── FaceAnalyzer (人脸分析)
│   └── DatabaseManager (数据库管理)
└── BehaviorAnalyzer (行为分析器)
```

### 🛠️ 技术栈

- **检测**: YOLOv8 (ultralytics)
- **跟踪**: DeepSORT (deep-sort-realtime)
- **人脸**: InsightFace (主要) / OpenCV (备用)
- **数据库**: SQLite (可升级至PostgreSQL)
- **后端**: FastAPI
- **前端**: HTML/CSS/JavaScript
- **部署**: 支持M1 Mac ARM架构

## 📊 主要特性

### 人员检测与跟踪

- 高精度人员检测，适应各种光照条件
- 稳定的多目标跟踪，支持ID保持和轨迹分析
- 轨迹可视化，直观展示人员移动路径

### 人脸分析

- 双重人脸检测方案（InsightFace优先，OpenCV备用）
- 高精度年龄性别识别，支持年龄优化算法
- 人员档案管理，关联轨迹与人脸属性

### 行为分析

- 区域管理：支持自定义多边形区域（入口、商品区、结账区等）
- 热力图：实时生成人员活动热力图，支持高斯分布热度叠加
- 行为事件：记录进入/离开区域、停留、移动等行为事件
- 停留分析：计算总停留时间、区域停留时间、停留次数
- 行为分类：自动识别购物者(Shopper)和浏览者(Browser)
- 参与度评分：基于多维度指标的综合参与度评估

### 数据管理

- 数据库设计：4张核心表（sessions, persons, positions, faces）
- 数据模型：PersonRecord, PositionRecord, FaceRecord, SessionRecord
- 统计查询：年龄分布、性别比例、轨迹分析等
- 数据清理：自动清理过期数据

### Web应用

- 实时监控：WebSocket实时数据传输
- 多用户支持：独立的用户会话管理
- 数据可视化：图表展示各类统计数据
- 分析记录：保存和导出分析结果

## 🚀 安装指南

### 系统要求

- Python 3.8+
- CUDA支持（可选，用于GPU加速）
- 摄像头或视频输入

### 基本安装

1. 克隆仓库

```bash
git clone https://github.com/xie135400/ai_people.git
cd ai_people
```

2. 创建虚拟环境

```bash
# 使用venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 或使用conda
conda create -n ai_people_env python=3.10
conda activate ai_people_env
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

### InsightFace安装（M1 Mac）

在M1 Mac上安装InsightFace需要特殊步骤：

```bash
# 1. 创建conda环境
conda create -n insightface_env python=3.10
conda activate insightface_env

# 2. 安装依赖
conda install -c conda-forge numpy cython cmake onnxruntime opencv

# 3. 设置环境变量
export CPPFLAGS="-I$(python -c 'import numpy; print(numpy.get_include())')"
export ARCHFLAGS="-arch arm64"

# 4. 安装InsightFace
pip install insightface --no-cache-dir
```

详细指南请参考 `安装insightface指南.md`

## 📝 使用方法

### 基础测试

```bash
# 环境测试
python test_environment.py

# 检测跟踪测试
python test_detection_tracking.py

# 人脸分析测试
python test_face_analysis.py

# 行为分析测试
python test_behavior_analysis.py
```

### 启动Web应用

```bash
# 简化版Web应用（适合快速测试）
python test_web_simple.py

# 完整Web应用
python -m src.web_app
```

启动后访问 `http://localhost:8000` 打开Web界面

### HTTPS支持

```bash
# 安装HTTPS依赖
python install_https_deps.py

# 启动HTTPS服务
python test_web_https.py
```

## 📈 开发进度

- ✅ Phase 1: 环境搭建 (完成)
- ✅ Phase 2: 人员检测与跟踪 (完成)
- ✅ Phase 3: 人脸检测与属性识别 (完成)
- ✅ Phase 4: 数据结构与存储 (完成)
- ✅ Phase 5: 消费行为分析 (完成)
- ✅ Phase 6: InsightFace集成与优化 (完成)
- ⏳ Phase 7: 可视化与报表 (进行中)
- ⏳ Phase 8: 测试与优化 (计划中)

## 🔍 主要优化

### InsightFace年龄优化

系统实现了多项年龄识别优化技术：

1. **统计学校正**：
   - 17个年龄段的精细校正
   - 基于性别和年龄段的偏差校正

2. **图像预处理**：
   - CLAHE自适应直方图均衡化
   - 非局部均值降噪
   - USM锐化处理
   - 对比度增强

3. **质量评分系统**：
   - 人脸尺寸评分
   - 清晰度评分
   - 光照质量评分
   - 人脸对称性评分

4. **时序平滑处理**：
   - 质量加权平均
   - 异常值检测
   - 多帧融合

详情请参考 `InsightFace年龄优化报告.md`

## 📁 项目结构

```
ai_poeple/
├── src/                      # 核心源代码
│   ├── __init__.py
│   ├── detector.py           # 人员检测模块
│   ├── tracker.py            # 人员跟踪模块
│   ├── face_analyzer.py      # 人脸分析模块
│   ├── integrated_analyzer.py # 集成分析模块
│   ├── persistent_analyzer.py # 持久化分析模块
│   ├── complete_analyzer.py  # 完整分析模块
│   ├── behavior_analyzer.py  # 行为分析模块
│   ├── database.py           # 数据库管理模块
│   ├── web_app.py            # Web应用模块
│   └── age_config.py         # 年龄优化配置
├── data/                     # 数据存储目录
│   ├── analytics.db          # SQLite数据库
│   ├── test_images/          # 测试图像
│   └── analysis_records/     # 分析记录
├── static/                   # 静态资源
│   ├── records.html          # 记录页面
│   └── placeholder.jpg       # 占位图像
├── test_*.py                 # 各种测试脚本
├── optimize_insightface_age.py # 年龄优化工具
├── performance_optimizer.py  # 性能优化工具
├── requirements.txt          # 项目依赖
├── install_dependencies.sh   # 安装脚本
└── README.md                 # 项目说明
```

## 📊 性能指标

系统在以下硬件配置下测试通过：

- **CPU模式**：
  - 处理速度：10-15 FPS
  - 内存使用：约500MB

- **GPU模式**（CUDA）：
  - 处理速度：25-30 FPS
  - 内存使用：约800MB
  - GPU内存：约2GB

## 🔮 未来计划

- [ ] 多摄像头支持
- [ ] 客流预测算法
- [ ] 3D空间分析
- [ ] 移动端应用
- [ ] 云端部署方案
- [ ] 更多行为模式识别

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出新功能建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 联系方式

项目维护者 - [@yourusername](https://github.com/xie135400)

项目链接: [https://github.com/yourusername/ai_people](https://github.com/xie135400/ai_people) 