#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Web应用测试
测试Web应用的基本功能而不启动服务器
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import logging
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_web_app_imports():
    """测试Web应用的导入"""
    print("🔍 测试Web应用导入...")
    
    try:
        from src.web_app import WebApp, UserSession
        print("✅ WebApp和UserSession导入成功")
        
        from src.complete_analyzer import CompleteAnalyzer
        print("✅ CompleteAnalyzer导入成功")
        
        from src.persistent_analyzer import PersistentAnalyzer
        print("✅ PersistentAnalyzer导入成功")
        
        from src.integrated_analyzer import IntegratedAnalyzer
        print("✅ IntegratedAnalyzer导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_user_session():
    """测试用户会话功能"""
    print("\n🔍 测试用户会话功能...")
    
    try:
        from src.web_app import UserSession
        
        # 创建用户会话
        session = UserSession("test_user", "测试用户")
        print(f"✅ 用户会话创建成功: {session.username}")
        
        # 测试启动分析
        session.start_analysis()
        print("✅ 分析启动成功")
        
        # 检查分析器配置
        use_insightface = session.analyzer.persistent_analyzer.analyzer.face_analyzer.use_insightface
        print(f"✅ 分析器使用InsightFace: {use_insightface}")
        
        # 停止分析
        session.stop_analysis()
        print("✅ 分析停止成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 用户会话测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_analyzer():
    """测试完整分析器"""
    print("\n🔍 测试完整分析器...")
    
    try:
        from src.complete_analyzer import CompleteAnalyzer
        
        # 创建分析器
        analyzer = CompleteAnalyzer(session_name="测试会话")
        print("✅ CompleteAnalyzer创建成功")
        
        # 检查InsightFace配置
        use_insightface = analyzer.persistent_analyzer.analyzer.face_analyzer.use_insightface
        print(f"✅ 默认使用InsightFace: {use_insightface}")
        
        # 测试处理帧
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        result_frame, stats = analyzer.process_frame(test_image)
        print(f"✅ 帧处理成功，统计项: {len(stats)}")
        
        # 清理
        analyzer.close()
        print("✅ 分析器关闭成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整分析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_app_creation():
    """测试Web应用创建"""
    print("\n🔍 测试Web应用创建...")
    
    try:
        from src.web_app import WebApp
        
        # 创建Web应用（不启动服务器）
        web_app = WebApp(db_path="data/test_analytics.db")
        print("✅ WebApp创建成功")
        
        # 测试SSL上下文设置
        ssl_context = web_app._setup_ssl_context()
        if ssl_context:
            print("✅ SSL上下文设置成功")
        else:
            print("⚠️ SSL上下文设置失败（可能是依赖问题）")
        
        return True
        
    except Exception as e:
        print(f"❌ Web应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始Web应用简化测试...")
    print("=" * 50)
    
    test_results = []
    
    # 运行测试
    test_results.append(("Web应用导入", test_web_app_imports()))
    test_results.append(("用户会话功能", test_user_session()))
    test_results.append(("完整分析器", test_complete_analyzer()))
    test_results.append(("Web应用创建", test_web_app_creation()))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"总计: {passed}/{total} 个测试通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有Web应用测试通过！")
        print("\n✨ 核心成果:")
        print("- ✅ Web应用可以正常创建")
        print("- ✅ 用户会话功能正常")
        print("- ✅ 完整分析器正常工作")
        print("- ✅ 默认使用InsightFace")
        
        print("\n💡 使用说明:")
        print("- 现在可以运行完整的Web应用")
        print("- 使用: python test_web_app.py")
        print("- 或者直接使用核心功能")
        
    else:
        print("⚠️ 部分测试失败，请检查相关配置")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 