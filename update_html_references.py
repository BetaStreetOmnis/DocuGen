#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML文件CDN引用更新器
将HTML文件中的CDN引用替换为本地引用
"""

import os
import re

class HTMLUpdater:
    def __init__(self, html_dir="static/html"):
        self.html_dir = html_dir
        
        # CDN URL到本地路径的映射
        self.url_replacements = {
            # Bootstrap CSS
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css": 
                "/static/lib/bootstrap/bootstrap.min.css",
            
            # Bootstrap JS
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js": 
                "/static/lib/bootstrap/bootstrap.bundle.min.js",
            
            # Bootstrap Icons
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css": 
                "/static/lib/bootstrap-icons/bootstrap-icons.css",
            
            # jQuery
            "https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js": 
                "/static/lib/jquery/jquery.min.js",
            
            # JSONEditor CSS
            "https://cdn.jsdelivr.net/npm/jsoneditor@9.9.0/dist/jsoneditor.min.css": 
                "/static/lib/jsoneditor/jsoneditor.min.css",
            
            # JSONEditor JS
            "https://cdn.jsdelivr.net/npm/jsoneditor@9.9.0/dist/jsoneditor.min.js": 
                "/static/lib/jsoneditor/jsoneditor.min.js",
            
            # EasyMDE CSS
            "https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css": 
                "/static/lib/easymde/easymde.min.css",
            
            # EasyMDE JS
            "https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js": 
                "/static/lib/easymde/easymde.min.js",
            
            # Chart.js
            "https://cdn.jsdelivr.net/npm/chart.js": 
                "/static/lib/chartjs/chart.min.js",
            
            # Marked.js
            "https://cdn.jsdelivr.net/npm/marked/marked.min.js": 
                "/static/lib/marked/marked.min.js",
        }
        
        # 需要替换的相对路径映射（用于修复已有的相对路径）
        self.relative_path_replacements = {
            "../lib/bootstrap/bootstrap.min.css": "/static/lib/bootstrap/bootstrap.min.css",
            "../lib/bootstrap/bootstrap.bundle.min.js": "/static/lib/bootstrap/bootstrap.bundle.min.js",
            "../lib/bootstrap-icons/bootstrap-icons.css": "/static/lib/bootstrap-icons/bootstrap-icons.css",
            "../lib/jquery/jquery.min.js": "/static/lib/jquery/jquery.min.js",
            "../lib/jsoneditor/jsoneditor.min.css": "/static/lib/jsoneditor/jsoneditor.min.css",
            "../lib/jsoneditor/jsoneditor.min.js": "/static/lib/jsoneditor/jsoneditor.min.js",
            "../lib/easymde/easymde.min.css": "/static/lib/easymde/easymde.min.css",
            "../lib/easymde/easymde.min.js": "/static/lib/easymde/easymde.min.js",
            "../lib/chartjs/chart.min.js": "/static/lib/chartjs/chart.min.js",
            "../lib/marked/marked.min.js": "/static/lib/marked/marked.min.js",
        }
    
    def update_html_files(self):
        """更新HTML文件中的CDN引用"""
        print(f"🔄 更新HTML文件中的CDN引用...")
        print(f"HTML目录: {self.html_dir}")
        
        if not os.path.exists(self.html_dir):
            print(f"❌ HTML目录不存在: {self.html_dir}")
            return
        
        html_files = [f for f in os.listdir(self.html_dir) if f.endswith('.html')]
        print(f"找到 {len(html_files)} 个HTML文件")
        
        updated_count = 0
        
        for html_file in html_files:
            file_path = os.path.join(self.html_dir, html_file)
            print(f"\n🔄 处理文件: {html_file}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                replacements_made = []
                
                # 替换CDN URL
                for cdn_url, local_path in self.url_replacements.items():
                    if cdn_url in content:
                        content = content.replace(cdn_url, local_path)
                        replacements_made.append(f"  ✓ {cdn_url} → {local_path}")
                
                # 替换已有的相对路径为绝对路径
                for relative_path, absolute_path in self.relative_path_replacements.items():
                    if relative_path in content:
                        content = content.replace(relative_path, absolute_path)
                        replacements_made.append(f"  ✓ {relative_path} → {absolute_path}")
                
                # 处理Google Fonts（移除或注释掉）
                google_fonts_pattern = r'<link[^>]*href="https://fonts\.googleapis\.com/[^"]*"[^>]*>'
                google_fonts_matches = re.findall(google_fonts_pattern, content)
                
                if google_fonts_matches:
                    for match in google_fonts_matches:
                        # 注释掉Google Fonts引用而不是删除
                        commented = f"<!-- {match} -->"
                        content = content.replace(match, commented)
                        replacements_made.append(f"  ✓ Google Fonts 已注释: {match[:50]}...")
                
                # 只有内容发生变化时才写入文件
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ 更新完成: {html_file}")
                    if replacements_made:
                        print("\n".join(replacements_made))
                    updated_count += 1
                else:
                    print(f"ℹ️  无需更新: {html_file}")
                    
            except Exception as e:
                print(f"❌ 处理文件失败 {html_file}: {str(e)}")
        
        print(f"\n📊 更新完成: {updated_count}/{len(html_files)} 个文件已更新")
    
    def check_local_resources(self):
        """检查本地资源文件是否存在"""
        print("🔍 检查本地资源文件...")
        
        missing_files = []
        existing_files = []
        
        for cdn_url, local_path in self.url_replacements.items():
            # 转换绝对路径为相对路径
            full_path = local_path.replace("/static/", "static/")
            
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                existing_files.append(f"✅ {full_path} ({file_size} bytes)")
            else:
                missing_files.append(f"❌ {full_path}")
        
        print(f"\n📊 资源文件检查结果:")
        print(f"存在: {len(existing_files)} 个")
        print(f"缺失: {len(missing_files)} 个")
        
        if existing_files:
            print(f"\n✅ 存在的文件:")
            for file_info in existing_files:
                print(f"  {file_info}")
        
        if missing_files:
            print(f"\n❌ 缺失的文件:")
            for file_path in missing_files:
                print(f"  {file_path}")
            print(f"\n⚠️  请先下载缺失的资源文件")
        
        return len(missing_files) == 0
    
    def run(self):
        """运行完整的更新流程"""
        print("🎯 HTML文件CDN引用更新工具")
        print("=" * 50)
        
        # 检查本地资源
        if not self.check_local_resources():
            print("\n⚠️  发现缺失的资源文件，建议先下载资源再更新HTML文件")
            response = input("是否仍要继续更新HTML文件？(y/N): ")
            if response.lower() != 'y':
                print("操作已取消")
                return
        
        # 更新HTML文件
        self.update_html_files()
        
        print("\n🎉 HTML文件更新完成！")
        print("现在所有HTML文件都使用本地资源引用了。")

if __name__ == "__main__":
    updater = HTMLUpdater()
    updater.run() 