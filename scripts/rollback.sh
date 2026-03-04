#!/bin/bash

# 快速回滚脚本

PROJECT_DIR="/opt/integrate-code"
BACKUP_DIR="/opt/integrate-code/backups"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}可用备份列表:${NC}"
ls -lt "$BACKUP_DIR" | grep -E "^d" | head -10 | awk '{print NR": "$NF}'

echo ""
echo "请输入要回滚的版本号（例如: 1）："
read BACKUP_NUMBER

# 获取对应的备份名
BACKUP_NAME=$(ls -t "$BACKUP_DIR" | grep -E "^d" | head -10 | sed -n "${BACKUP_NUMBER}p")

if [ -z "$BACKUP_NAME" ]; then
    echo -e "${RED}错误: 备份不存在${NC}"
    exit 1
fi

BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

echo -e "${YELLOW}确认要回滚到 $BACKUP_NAME 吗? (y/n)${NC}"
read CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "取消回滚"
    exit 0
fi

echo "开始回滚..."

# 停止服务
echo "停止服务..."
pkill -f "app.py" || true
sleep 2

# 恢复备份
echo "恢复备份..."
rm -rf "$PROJECT_DIR"/*
cp -r "$BACKUP_PATH"/* "$PROJECT_DIR/"

# 启动服务
echo "启动服务..."
cd "$PROJECT_DIR"
nohup python3 app.py > /var/log/integrate-code/app.log 2>&1 &

# 等待应用启动
sleep 5

# 检查进程状态
if pgrep -f "app.py" > /dev/null; then
    echo -e "${GREEN}回滚完成，应用已启动${NC}"
else
    echo -e "${RED}回滚失败，应用启动异常${NC}"
    exit 1
fi
