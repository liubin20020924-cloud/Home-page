#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""代码统计脚本"""

import os
from pathlib import Path
from collections import defaultdict

def count_lines(filepath):
    """统计文件行数"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return 0

def get_file_size(filepath):
    """获取文件大小（KB）"""
    try:
        return os.path.getsize(filepath) / 1024
    except:
        return 0

def count_code_and_comments(filepath):
    """统计代码行和注释行"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            code_lines = 0
            comment_lines = 0
            empty_lines = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    empty_lines += 1
                elif stripped.startswith('#') or stripped.startswith('//'):
                    comment_lines += 1
                else:
                    code_lines += 1
            
            return code_lines, comment_lines, empty_lines
    except:
        return 0, 0, 0

def main():
    root = Path('e:/Integrate-code')
    
    # 初始化统计数据
    stats = defaultdict(lambda: {
        'files': [],
        'lines': 0,
        'size': 0,
        'code_lines': 0,
        'comment_lines': 0,
        'empty_lines': 0
    })
    
    extensions = ['py', 'html', 'css', 'js', 'sql', 'md']
    
    # 遍历文件
    for ext in extensions:
        pattern = f'*.{ext}'
        for filepath in root.rglob(pattern):
            # 跳过某些目录
            if any(x in str(filepath) for x in ['__pycache__', '.git', 'venv', 'env']):
                continue
                
            lines = count_lines(filepath)
            size = get_file_size(filepath)
            
            stats[ext]['files'].append({
                'path': filepath,
                'name': filepath.name,
                'lines': lines,
                'size': size
            })
            stats[ext]['lines'] += lines
            stats[ext]['size'] += size
            
            # 对于 Python 文件，统计代码和注释
            if ext == 'py':
                code, comment, empty = count_code_and_comments(filepath)
                stats[ext]['code_lines'] += code
                stats[ext]['comment_lines'] += comment
                stats[ext]['empty_lines'] += empty
    
    # 输出统计结果
    print("=" * 70)
    print(" * 代码统计报告  * ")
    print("=" * 70)
    
    # 各类型统计
    for ext in ['py', 'html', 'css', 'js', 'sql', 'md']:
        if not stats[ext]['files']:
            continue
            
        data = stats[ext]
        print(f"\n### {ext.upper()} 文件统计")
        print("-" * 70)
        print(f"文件数量: {len(data['files'])}")
        print(f"总行数: {data['lines']:,}")
        print(f"总大小: {data['size']:.2f} KB ({data['size']/1024:.2f} MB)")
        
        if data['files']:
            avg_lines = data['lines'] // len(data['files'])
            print(f"平均行数: {avg_lines:,}")
        
        # Python 文件的详细统计
        if ext == 'py':
            print(f"\n  代码行: {data['code_lines']:,}")
            print(f"  注释行: {data['comment_lines']:,}")
            print(f"  空行: {data['empty_lines']:,}")
            if data['lines'] > 0:
                code_ratio = (data['code_lines'] / data['lines']) * 100
                print(f"  代码密度: {code_ratio:.1f}%")
        
        # 最大的文件
        if data['files']:
            sorted_files = sorted(data['files'], key=lambda x: x['lines'], reverse=True)[:5]
            print(f"\n最大文件 (Top 5):")
            for i, file in enumerate(sorted_files, 1):
                print(f"  {i}. {file['name']}: {file['lines']:,} 行 ({file['size']:.2f} KB)")
    
    # 总体统计
    print("\n" + "=" * 70)
    print("### 总体统计")
    print("=" * 70)
    
    total_lines = sum(d['lines'] for d in stats.values())
    total_size = sum(d['size'] for d in stats.values())
    total_files = sum(len(d['files']) for d in stats.values())
    
    print(f"总文件数: {total_files}")
    print(f"总代码行数: {total_lines:,}")
    print(f"总大小: {total_size:.2f} KB ({total_size/1024:.2f} MB)")
    
    # 代码分布
    print("\n" + "=" * 70)
    print("### 代码分布")
    print("-" * 70)
    
    code_distribution = {
        'Python (.py)': stats['py']['lines'],
        'HTML': stats['html']['lines'],
        'CSS': stats['css']['lines'],
        'JavaScript': stats['js']['lines'],
        'SQL': stats['sql']['lines'],
        'Markdown': stats['md']['lines']
    }
    
    sorted_dist = sorted(code_distribution.items(), key=lambda x: x[1], reverse=True)
    
    for name, lines in sorted_dist:
        if total_lines > 0:
            percentage = (lines / total_lines) * 100
            bar = '█' * int(percentage / 5)
            print(f"{name:20s} {lines:6,} 行 ({percentage:5.1f}%) {bar}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
