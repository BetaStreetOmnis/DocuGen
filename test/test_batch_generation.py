#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分批生成功能测试脚本
测试关键词生成器的分批生成功能
"""

import json
import logging
import time
from run_keyword_generator import SafetyKeywordGenerator, KEYWORD_CATEGORIES

def test_batch_generation():
    """测试分批生成功能"""
    print("🧪 开始测试分批生成功能...")
    
    try:
        # 创建生成器
        generator = SafetyKeywordGenerator()
        
        # 显示配置信息
        print(f"📄 CSV文件路径: {generator.csv_file_path}")
        print(f"📦 批次大小: 50个关键词/批")
        print(f"⏱️  批次延迟: 2秒")
        
        # 测试API连接
        print("\n🔌 测试API连接...")
        if not generator.test_api_connection():
            print("❌ API连接失败")
            return False
        
        print("✅ API连接成功")
        
        # 选择几个类别进行测试
        test_cases = [
            ("歧视性内容", "地域歧视", {"description": "基于地域、出身的歧视性内容", "target_count": 100}),
            ("歧视性内容", "年龄歧视", {"description": "基于年龄的歧视性言论", "target_count": 100})
        ]
        
        print(f"\n🎯 开始测试生成 {len(test_cases)} 个类别...")
        
        for i, (main_cat, sub_cat, config) in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"📝 测试 {i}/{len(test_cases)}: {main_cat} -> {sub_cat}")
            print(f"🎯 目标数量: {config['target_count']} 个")
            print(f"📦 预计批次: {(config['target_count'] + 49) // 50} 批")
            print(f"{'='*60}")
            
            start_time = time.time()
            
            # 生成关键词
            keywords = generator.generate_keywords_for_category(main_cat, sub_cat, config)
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # 显示结果
            if keywords:
                print(f"\n✅ {sub_cat} 生成完成!")
                print(f"   📊 生成数量: {len(keywords)} 个")
                print(f"   🎯 目标数量: {config['target_count']} 个")
                print(f"   📈 完成率: {len(keywords)/config['target_count']:.1%}")
                print(f"   ⏱️  耗时: {generation_time:.1f}秒")
                print(f"   📝 示例关键词: {keywords[:5] if len(keywords) >= 5 else keywords}")
            else:
                print(f"❌ {sub_cat} 生成失败")
            
            # 显示统计信息
            stats_key = f"{main_cat}-{sub_cat}"
            if stats_key in generator.generation_stats:
                stats = generator.generation_stats[stats_key]
                print(f"   📦 使用批次: {stats.get('batches_used', 'N/A')} 批")
        
        print(f"\n📊 测试完成! 请查看CSV文件: {generator.csv_file_path}")
        return True
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 测试被中断")
        if generator and generator.csv_file_path:
            print(f"💾 已生成的内容保存在: {generator.csv_file_path}")
        return False
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def show_generation_progress():
    """显示生成进度"""
    try:
        generator = SafetyKeywordGenerator()
        csv_path = generator.csv_file_path
        
        print(f"\n📄 实时生成结果 ({csv_path}):")
        print("-" * 80)
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            
            if len(lines) <= 1:
                print("📝 暂无生成数据")
                return
            
            # 统计各类别数量
            category_stats = {}
            for line in lines[1:]:  # 跳过标题行
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    main_cat = parts[0]
                    sub_cat = parts[1]
                    key = f"{main_cat}-{sub_cat}"
                    category_stats[key] = category_stats.get(key, 0) + 1
            
            # 显示统计结果
            print("📊 类别统计:")
            for category, count in category_stats.items():
                print(f"   {category}: {count} 个关键词")
            
            print(f"\n📈 总计: {len(lines) - 1} 个关键词")
            
            # 显示最新的几条记录
            print(f"\n📝 最新生成的关键词:")
            for i, line in enumerate(lines[-10:], 1):  # 显示最后10行
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    print(f"   {len(lines)-10+i:2d}. {parts[1]}: {parts[2]}")
        
    except FileNotFoundError:
        print("❌ CSV文件不存在")
    except Exception as e:
        print(f"❌ 读取CSV文件失败: {str(e)}")

def show_batch_config():
    """显示分批配置"""
    print("⚙️ 分批生成配置:")
    print("-" * 40)
    print(f"📦 每批大小: 50 个关键词")
    print(f"⏱️  批次延迟: 2 秒")
    print(f"🔄 批次重试: 最多 2 次")
    print(f"🎯 总目标数: 2900 个关键词")
    print(f"📊 预计批次: 约 58 批")
    print(f"⏳ 预计耗时: 约 3-5 分钟")

if __name__ == "__main__":
    print("🧪 分批生成功能测试")
    print("=" * 60)
    
    # 显示配置
    show_batch_config()
    
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    success = test_batch_generation()
    
    if success:
        print("\n" + "=" * 60)
        show_generation_progress() 