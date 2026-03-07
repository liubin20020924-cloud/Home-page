#!/bin/bash
# =====================================================
# 智能数据库同步脚本 (Linux/macOS)
# =====================================================

echo ""
echo "===================================================="
echo "   云户科技 - 智能数据库同步工具 (Linux/macOS)"
echo "===================================================="
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python3"
    exit 1
fi

# 检查 PyMySQL 是否安装
if ! python3 -c "import pymysql" &> /dev/null; then
    echo "[提示] PyMySQL 未安装，正在安装..."
    pip3 install pymysql
    if [ $? -ne 0 ]; then
        echo "[错误] PyMySQL 安装失败"
        exit 1
    fi
fi

# 获取参数
HOST=${1:-localhost}
PORT=${2:-3306}
USER=${3:-root}

# 密码从命令行参数或环境变量读取
if [ -z "$4" ]; then
    read -s -p "请输入MySQL密码（留空表示无密码）: " PASSWORD
    echo ""
else
    PASSWORD=$4
fi

# 执行同步
echo ""
echo "[开始] 执行数据库同步..."
echo ""
python3 "$(dirname "$0")/sync_database.py" "$HOST" "$PORT" "$USER" "$PASSWORD"

if [ $? -eq 0 ]; then
    echo ""
    echo "[成功] 数据库同步完成"
else
    echo ""
    echo "[失败] 数据库同步失败"
fi

echo ""
