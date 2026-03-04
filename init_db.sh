#!/bin/bash
# MariaDB 数据库初始化脚本

echo "正在初始化数据库..."
sudo mariadb < database/init_database.sql

if [ $? -eq 0 ]; then
    echo "✅ 数据库初始化成功！"
    echo ""
    echo "数据库信息："
    echo "  - clouddoors_db (官网系统)"
    echo "  - YHKB (知识库系统)"
    echo "  - casedb (工单系统)"
    echo ""
    echo "默认管理员账号："
    echo "  用户名：admin"
    echo "  密码：YHKB@2024"
else
    echo "❌ 数据库初始化失败！"
    exit 1
fi
