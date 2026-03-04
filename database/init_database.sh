#!/bin/bash
# =====================================================
# 云户科技网站数据库初始化脚本 (Linux/macOS)
# 用于全新部署系统时初始化数据库
# 版本: v2.0
# 创建时间: 2026-02-27
# =====================================================

echo "===================================================="
echo "云户科技网站数据库初始化脚本 (v2.0)"
echo "===================================================="
echo ""

# 检查参数
if [ -z "$1" ]; then
    echo "用法: ./init_database.sh [MySQL用户名]"
    echo "示例: ./init_database.sh root"
    echo ""
    echo "注意: 首次运行会提示输入MySQL密码"
    exit 1
fi

MYSQL_USER=$1
MYSQL_HOST=${2:-localhost}
MYSQL_PORT=${3:-3306}

echo "配置信息:"
echo "  MySQL用户: $MYSQL_USER"
echo "  MySQL主机: $MYSQL_HOST"
echo "  MySQL端口: $MYSQL_PORT"
echo ""

# 检查SQL文件是否存在
if [ ! -f "init_database.sql" ]; then
    echo "错误: 找不到 init_database.sql 文件"
    exit 1
fi

echo "正在执行数据库初始化..."
echo "请输入MySQL密码:"
echo ""

# 执行初始化脚本
mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p < init_database.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "===================================================="
    echo "数据库初始化成功!"
    echo "===================================================="
    echo ""
    echo "默认管理员账号:"
    echo "  用户名: admin"
    echo "  密码: YHKB@2024"
    echo ""
    echo "重要: 生产环境部署后请立即修改默认密码！"
    echo "===================================================="
else
    echo ""
    echo "===================================================="
    echo "数据库初始化失败!"
    echo "请检查:"
    echo "1. MySQL服务是否启动"
    echo "2. 用户名和密码是否正确"
    echo "3. 用户是否有创建数据库的权限"
    echo "===================================================="
fi

echo ""
