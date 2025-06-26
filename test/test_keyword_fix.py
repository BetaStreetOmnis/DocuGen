#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试关键词生成器的错误修复
"""

import json
import logging
from run_keyword_generator import SafetyKeywordGenerator, LLM_CONFIG

def test_single_category():
    """测试单个类别的关键词生成"""
    print("🧪 测试关键词生成器错误修复")
    print("=" * 50)
    
    try:
        # 初始化生成器
        generator = SafetyKeywordGenerator()
        
        # 测试API连接
        print("1. 测试API连接...")
        if generator.test_api_connection():
            print("✅ API连接正常")
        else:
            print("❌ API连接失败")
            return
        
        # 测试单个类别生成
        print("\n2. 测试单个类别生成...")
        print("正在生成 '地域歧视' 类别的关键词...")
        
        config = {
            "description": "基于地域、出身的歧视性内容",
            "target_count": 50  # 减少数量用于测试
        }
        
        keywords = generator.generate_keywords_for_category(
            "歧视性内容", "地域歧视", config
        )
        
        print(f"✅ 成功生成 {len(keywords)} 个关键词")
        print("前10个关键词:")
        for i, kw in enumerate(keywords[:10], 1):
            print(f"  {i:2d}. {kw}")
        
        # 保存测试结果
        test_result = {
            "category": "地域歧视",
            "keywords": keywords,
            "count": len(keywords),
            "config": config
        }
        
        with open("test_result.json", "w", encoding="utf-8") as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 测试结果已保存到 test_result.json")
        print("🎉 测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        
        # 详细错误信息
        import traceback
        print("\n📋 详细错误信息:")
        traceback.print_exc()

def show_config():
    """显示当前配置"""
    print("\n🔧 当前配置:")
    print("-" * 30)
    print(f"API地址: {LLM_CONFIG['THIRD_PARTY_LLM_BASE_URL']}")
    print(f"模型名称: {LLM_CONFIG['THIRD_PARTY_MODEL_NAME']}")
    print(f"超时时间: {LLM_CONFIG['TIMEOUT']}秒")
    print(f"最大重试: {LLM_CONFIG['MAX_RETRIES']}次")
    print(f"最大Token: {LLM_CONFIG['MAX_TOKENS']}")
    print(f"并发数: {LLM_CONFIG['MAX_WORKERS']}")

if __name__ == "__main__":
    show_config()
    test_single_category() 