#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时保存功能测试脚本
测试关键词生成器的增量保存功能
"""

import json
import logging
import time
from run_keyword_generator import SafetyKeywordGenerator

def test_realtime_save():
    """测试实时保存功能"""
    print("🧪 开始测试实时保存功能...")
    
    try:
        # 创建生成器
        generator = SafetyKeywordGenerator()
        
        # 显示CSV文件路径
        print(f"📄 CSV文件路径: {generator.csv_file_path}")
        
        # 测试API连接
        print("\n🔌 测试API连接...")
        if not generator.test_api_connection():
            print("❌ API连接失败")
            return False
        
        print("✅ API连接成功")
        
        # 测试生成几个类别
        test_categories = [
            ("地域歧视", 10),
            ("种族歧视", 10)
        ]
        
        print("\n🎯 开始测试生成...")
        for category, count in test_categories:
            print(f"\n📝 生成类别: {category} (目标: {count}个)")
            
            # 生成关键词
            keywords = generator.generate_keywords_for_category(category, count)
            
            if keywords:
                print(f"✅ 成功生成 {len(keywords)} 个关键词")
                print(f"   示例: {keywords[:3] if len(keywords) >= 3 else keywords}")
            else:
                print("❌ 生成失败")
            
            # 等待一下，模拟真实使用场景
            time.sleep(2)
        
        print(f"\n📊 测试完成! 请查看CSV文件: {generator.csv_file_path}")
        return True
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 测试被中断")
        print(f"💾 已生成的内容保存在: {generator.csv_file_path}")
        return False
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False

def show_csv_content():
    """显示CSV文件内容"""
    try:
        generator = SafetyKeywordGenerator()
        csv_path = generator.csv_file_path
        
        print(f"\n📄 CSV文件内容 ({csv_path}):")
        print("-" * 60)
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:20], 1):  # 只显示前20行
                print(f"{i:2d}: {line.strip()}")
            
            if len(lines) > 20:
                print(f"... 还有 {len(lines) - 20} 行")
        
        print(f"\n📊 总计: {len(lines)} 行 (包含标题行)")
        
    except FileNotFoundError:
        print("❌ CSV文件不存在")
    except Exception as e:
        print(f"❌ 读取CSV文件失败: {str(e)}")

if __name__ == "__main__":
    print("🧪 实时保存功能测试")
    print("=" * 50)
    
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    success = test_realtime_save()
    
    if success:
        print("\n" + "=" * 50)
        show_csv_content() 