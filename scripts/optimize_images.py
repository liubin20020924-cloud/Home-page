#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片优化脚本
功能:
1. 批量压缩图片
2. 转换为 WebP 格式
3. 生成不同尺寸的响应式图片
4. 添加水印（可选）
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageOps
import argparse
from typing import Tuple, Optional

class ImageOptimizer:
    """图片优化器"""
    
    def __init__(self, input_dir: str, output_dir: str = None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir) if output_dir else self.input_dir / 'optimized'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def get_max_size(self, img: Image.Image, max_width: int = 1200, max_height: int = 1200) -> Tuple[int, int]:
        """计算缩放后的尺寸"""
        if img.width <= max_width and img.height <= max_height:
            return img.width, img.height
            
        ratio = min(max_width / img.width, max_height / img.height)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
        return new_width, new_height
    
    def optimize_single(self, input_path: Path, quality: int = 85, max_width: int = 1200) -> bool:
        """优化单张图片"""
        try:
            # 打开图片
            img = Image.open(input_path)
            
            # 转换为 RGB 模式（去除透明度）
            if img.mode in ('RGBA', 'LA'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整大小
            new_width, new_height = self.get_max_size(img, max_width)
            if new_width != img.width or new_height != img.height:
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # 保存为 WebP 格式
            filename = input_path.stem
            output_path = self.output_dir / f"{filename}.webp"
            
            img.save(output_path, 'WEBP', quality=quality, method=6, optimize=True)
            print(f"✓ 优化完成: {input_path.name} ({img.width}x{img.height} -> {new_width}x{new_height})")
            
            # 同时保存优化后的 JPG 作为后备
            output_jpg = self.output_dir / f"{filename}_opt.jpg"
            img.save(output_jpg, 'JPEG', quality=quality, optimize=True, progressive=True)
            
            return True
            
        except Exception as e:
            print(f"✗ 处理失败: {input_path.name} - {str(e)}")
            return False
    
    def create_responsive_images(self, input_path: Path, sizes: list = None) -> bool:
        """创建响应式图片"""
        if sizes is None:
            sizes = [
                (320, 240, 'sm'),
                (640, 480, 'md'),
                (1024, 768, 'lg'),
                (1200, 900, 'xl'),
            ]
        
        try:
            img = Image.open(input_path)
            filename = input_path.stem
            
            for max_width, max_height, suffix in sizes:
                # 计算缩放比例
                ratio = min(max_width / img.width, max_height / img.height)
                if ratio >= 1:
                    continue
                    
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                resized = img.resize((new_width, new_height), Image.LANCZOS)
                
                # 保存
                output_path = self.output_dir / f"{filename}-{suffix}.webp"
                resized.save(output_path, 'WEBP', quality=85, optimize=True)
                print(f"  → 创建响应式: {filename}-{suffix}.webp ({new_width}x{new_height})")
            
            return True
            
        except Exception as e:
            print(f"✗ 创建响应式失败: {input_path.name} - {str(e)}")
            return False
    
    def batch_optimize(self, quality: int = 85, max_width: int = 1200, create_responsive: bool = False):
        """批量优化图片"""
        # 支持的图片格式
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp')
        
        # 查找所有图片文件
        image_files = []
        for ext in supported_formats:
            image_files.extend(self.input_dir.glob(f"*{ext}"))
            image_files.extend(self.input_dir.glob(f"*{ext.upper()}"))
        
        if not image_files:
            print(f"未找到支持的图片文件: {self.input_dir}")
            return
        
        print(f"找到 {len(image_files)} 张图片")
        print(f"输出目录: {self.output_dir}")
        print("=" * 50)
        
        success_count = 0
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] 处理: {image_path.name}")
            
            # 优化原图
            if self.optimize_single(image_path, quality, max_width):
                success_count += 1
            
            # 创建响应式版本
            if create_responsive:
                self.create_responsive_images(image_path)
        
        print("\n" + "=" * 50)
        print(f"优化完成！成功: {success_count}/{len(image_files)}")
        print(f"优化后图片保存在: {self.output_dir}")
        
        # 统计文件大小
        self.compare_sizes(image_files)
    
    def compare_sizes(self, original_files: list):
        """对比原始和优化后的文件大小"""
        total_original = 0
        total_optimized = 0
        
        print("\n文件大小对比:")
        print("-" * 50)
        print(f"{'文件名':<30} {'原始大小':>15} {'优化后':>15} {'节省':>15}")
        print("-" * 50)
        
        for original_path in original_files:
            filename = original_path.stem
            
            # 查找原始文件大小
            if original_path.exists():
                total_original += original_path.stat().st_size
                original_size = original_path.stat().st_size
            else:
                continue
            
            # 查找优化后的文件大小
            webp_path = self.output_dir / f"{filename}.webp"
            if webp_path.exists():
                optimized_size = webp_path.stat().st_size
                total_optimized += optimized_size
                saved = original_size - optimized_size
                saved_percent = (saved / original_size) * 100 if original_size > 0 else 0
            else:
                optimized_size = 0
                saved = 0
                saved_percent = 0
            
            print(f"{filename:<30} {self.format_size(original_size):>15} {self.format_size(optimized_size):>15} {saved_percent:>14.1f}%")
        
        print("-" * 50)
        if total_original > 0:
            total_saved = total_original - total_optimized
            total_saved_percent = (total_saved / total_original) * 100
            print(f"{'总计':<30} {self.format_size(total_original):>15} {self.format_size(total_optimized):>15} {total_saved_percent:>14.1f}%")
            print(f"节省空间: {self.format_size(total_saved)}")
    
    @staticmethod
    def format_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:7.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='图片批量优化工具')
    parser.add_argument('input_dir', help='输入图片目录')
    parser.add_argument('-o', '--output', help='输出目录（默认: input_dir/optimized）')
    parser.add_argument('-q', '--quality', type=int, default=85, help='WebP 质量 (1-100, 默认: 85)')
    parser.add_argument('-w', '--width', type=int, default=1200, help='最大宽度 (默认: 1200)')
    parser.add_argument('-r', '--responsive', action='store_true', help='创建响应式图片')
    parser.add_argument('--sm-only', action='store_true', help='仅小尺寸优化 (max_width=640)')
    
    args = parser.parse_args()
    
    # 小尺寸模式
    max_width = 640 if args.sm_only else args.width
    
    print("=" * 50)
    print("图片批量优化工具")
    print("=" * 50)
    print(f"输入目录: {args.input_dir}")
    print(f"输出目录: {args.output if args.output else args.input_dir + '/optimized'}")
    print(f"质量: {args.quality}")
    print(f"最大宽度: {max_width}")
    print(f"响应式: {'是' if args.responsive else '否'}")
    print("=" * 50)
    
    optimizer = ImageOptimizer(args.input_dir, args.output)
    optimizer.batch_optimize(
        quality=args.quality,
        max_width=max_width,
        create_responsive=args.responsive
    )


if __name__ == '__main__':
    main()
