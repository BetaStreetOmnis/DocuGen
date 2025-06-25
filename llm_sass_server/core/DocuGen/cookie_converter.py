#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cookie格式转换工具
将浏览器中的cookie字符串转换为JSON格式
作者: BetaStreetOmnis
日期: 2024-01-19
"""

import json
import re
from urllib.parse import unquote

def parse_cookie_string(cookie_string):
    """
    解析cookie字符串为字典
    支持多种常见的cookie格式
    """
    cookies = {}
    
    # 清理字符串
    cookie_string = cookie_string.strip()
    
    # 方法1: 处理标准的 key=value; key2=value2 格式
    if ';' in cookie_string:
        pairs = cookie_string.split(';')
        for pair in pairs:
            pair = pair.strip()
            if '=' in pair:
                key, value = pair.split('=', 1)
                key = key.strip()
                value = value.strip()
                # URL解码
                try:
                    value = unquote(value)
                except:
                    pass
                cookies[key] = value
    
    # 方法2: 处理换行分隔的格式
    elif '\n' in cookie_string:
        lines = cookie_string.split('\n')
        for line in lines:
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                try:
                    value = unquote(value)
                except:
                    pass
                cookies[key] = value
    
    # 方法3: 处理单个 key=value 格式
    elif '=' in cookie_string:
        key, value = cookie_string.split('=', 1)
        key = key.strip()
        value = value.strip()
        try:
            value = unquote(value)
        except:
            pass
        cookies[key] = value
    
    return cookies

def format_as_json(cookies, indent=2):
    """将cookies字典格式化为JSON"""
    return json.dumps(cookies, ensure_ascii=False, indent=indent)

def format_as_header(cookies):
    """将cookies字典格式化为HTTP请求头格式"""
    return '; '.join([f"{k}={v}" for k, v in cookies.items()])

def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("                Cookie格式转换工具")
    print("           Browser Cookie to JSON Converter")
    print("=" * 60)
    print()

def main():
    """主函数"""
    print_banner()
    
    print("📝 请输入您的cookie字符串:")
    print("支持的格式:")
    print("  1. key1=value1; key2=value2; key3=value3")
    print("  2. key1=value1")
    print("     key2=value2")
    print("     key3=value3")
    print("  3. 单个cookie: key=value")
    print()
    print("请粘贴您的cookie内容 (输入完成后按两次回车):")
    
    # 读取多行输入
    lines = []
    empty_lines = 0
    
    while True:
        try:
            line = input()
            if line.strip() == "":
                empty_lines += 1
                if empty_lines >= 2:  # 连续两个空行表示输入结束
                    break
            else:
                empty_lines = 0
                lines.append(line)
        except KeyboardInterrupt:
            print("\n\n⏹️ 用户取消操作")
            return
        except EOFError:
            break
    
    if not lines:
        print("❌ 没有输入任何内容")
        return
    
    # 合并所有行
    cookie_string = '\n'.join(lines)
    
    print("\n🔄 开始转换...")
    
    try:
        # 解析cookies
        cookies = parse_cookie_string(cookie_string)
        
        if not cookies:
            print("❌ 未能解析出任何有效的cookie")
            return
        
        print(f"✅ 成功解析出 {len(cookies)} 个cookie")
        print("\n" + "="*60)
        
        # 显示解析结果
        print("📋 解析出的Cookie列表:")
        print("-" * 30)
        for i, (key, value) in enumerate(cookies.items(), 1):
            # 限制显示长度
            display_value = value if len(value) <= 50 else value[:47] + "..."
            print(f"  {i:2d}. {key} = {display_value}")
        
        print("\n" + "="*60)
        
        # JSON格式输出
        print("📄 JSON格式:")
        print("-" * 30)
        json_output = format_as_json(cookies)
        print(json_output)
        
        print("\n" + "="*60)
        
        # HTTP请求头格式输出
        print("🌐 HTTP请求头格式:")
        print("-" * 30)
        header_output = format_as_header(cookies)
        print(f"Cookie: {header_output}")
        
        print("\n" + "="*60)
        
        # 保存选项
        save_choice = input("\n💾 是否保存到文件? (y/N): ").strip().lower()
        
        if save_choice in ['y', 'yes']:
            timestamp = json.loads(json.dumps({"time": "now"}))  # 获取当前时间
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存JSON文件
            json_filename = f"cookies_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                f.write(json_output)
            
            # 保存文本文件
            txt_filename = f"cookies_{timestamp}.txt"
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write("Cookie解析结果\n")
                f.write("="*50 + "\n\n")
                f.write(f"解析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Cookie数量: {len(cookies)}\n\n")
                
                f.write("Cookie列表:\n")
                f.write("-"*30 + "\n")
                for i, (key, value) in enumerate(cookies.items(), 1):
                    f.write(f"{i:2d}. {key} = {value}\n")
                
                f.write(f"\nJSON格式:\n")
                f.write("-"*30 + "\n")
                f.write(json_output)
                
                f.write(f"\n\nHTTP请求头格式:\n")
                f.write("-"*30 + "\n")
                f.write(f"Cookie: {header_output}")
            
            print(f"✅ 文件已保存:")
            print(f"   📄 JSON: {json_filename}")
            print(f"   📄 详细: {txt_filename}")
        
        print("\n🎉 转换完成!")
        
    except Exception as e:
        print(f"❌ 转换过程中发生错误: {e}")
        print("💡 请检查输入格式是否正确")

if __name__ == "__main__":
    main() 