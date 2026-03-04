#!/bin/bash
# 图片快速优化脚本
# 无需修改代码，直接运行即可优化所有图片

echo "======================================"
echo "   图片优化脚本"
echo "======================================"
echo ""

# 检查 Python 是否安装
if ! command -v python &> /dev/null; then
    echo "错误：未找到 Python，请先安装 Python 3"
    exit 1
fi

# 检查 Pillow 是否安装
if ! python -c "import PIL" 2>/dev/null; then
    echo "正在安装 Pillow..."
    pip install Pillow
fi

# 备份原图
echo "1. 备份原始图片..."
mkdir -p static/home/images/backup
mkdir -p static/case/images/backup
mkdir -p static/kb/images/backup

# 只备份 .jpg 文件
find static/home/images -maxdepth 1 -type f -name "*.jpg" -exec cp {} static/home/images/backup/ \;
find static/case/images -maxdepth 1 -type f -name "*.jpg" -exec cp {} static/case/images/backup/ \; 2>/dev/null
find static/kb/images -maxdepth 1 -type f -name "*.jpg" -exec cp {} static/kb/images/backup/ \; 2>/dev/null

echo "   ✓ 原图已备份到 backup 目录"
echo ""

# 优化首页图片
echo "2. 优化首页图片..."
python scripts/optimize_images.py static/home/images -o static/home/images/optimized -q 80 -w 1400
echo ""

# 应用优化后的首页图片
echo "3. 应用优化后的首页图片..."
cp static/home/images/optimized/*_opt.jpg static/home/images/ 2>/dev/null
echo "   ✓ 首页图片已更新"
echo ""

# 优化工单系统图片
if [ -d "static/case/images" ]; then
    echo "4. 优化工单系统图片..."
    python scripts/optimize_images.py static/case/images -o static/case/images/optimized -q 80 -w 800
    cp static/case/images/optimized/*_opt.jpg static/case/images/ 2>/dev/null
    echo "   ✓ 工单系统图片已更新"
    echo ""
fi

# 优化知识库图片
if [ -d "static/kb/images" ]; then
    echo "5. 优化知识库图片..."
    python scripts/optimize_images.py static/kb/images -o static/kb/images/optimized -q 80 -w 800
    cp static/kb/images/optimized/*_opt.jpg static/kb/images/ 2>/dev/null
    echo "   ✓ 知识库图片已更新"
    echo ""
fi

# 清理临时文件
echo "6. 清理优化后的临时文件..."
rm -rf static/home/images/optimized
rm -rf static/case/images/optimized 2>/dev/null
rm -rf static/kb/images/optimized 2>/dev/null

echo "======================================"
echo "   优化完成！"
echo "======================================"
echo ""
echo "原图片已备份到各目录的 backup 文件夹"
echo ""
echo "如需恢复原图，执行："
echo "  cp static/home/images/backup/*.jpg static/home/images/"
echo ""
echo "查看优化效果："
echo "  打开浏览器 F12 -> Network -> 刷新页面"
echo ""
