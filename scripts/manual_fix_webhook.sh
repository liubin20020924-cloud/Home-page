#!/bin/bash

# 手动重启 webhook receiver 的诊断脚本
# 用于调试 webhook receiver 无法重启的问题

set -e

PROJECT_DIR="/opt/Home-page"
cd "$PROJECT_DIR"

echo "=========================================="
echo "Webhook Receiver 诊断和修复脚本"
echo "=========================================="
echo ""

# 1. 检查当前代码版本
echo "1. 检查 webhook_receiver_github.py 代码版本..."
if grep -q "isinstance(raw_payload, str)" scripts/webhook_receiver_github.py; then
    echo "✅ 代码文件已更新（包含类型检查）"
else
    echo "❌ 代码文件未更新！"
    echo "正在重新拉取代码..."
    git fetch origin
    git reset --hard origin/main
    if grep -q "isinstance(raw_payload, str)" scripts/webhook_receiver_github.py; then
        echo "✅ 代码已重新拉取"
    else
        echo "❌ 代码拉取失败，请检查 Git 连接"
        exit 1
    fi
fi
echo ""

# 2. 查找所有 webhook 相关进程
echo "2. 查找所有 webhook 相关进程..."
ps aux | grep webhook | grep -v grep || echo "未找到 webhook 进程"
echo ""

# 3. 强制停止所有 webhook 进程
echo "3. 强制停止所有 webhook 进程..."
pkill -9 -f "webhook_receiver_github.py" 2>/dev/null || echo "没有需要停止的进程"
pkill -9 -f "webhook.*receiver" 2>/dev/null || echo "没有需要停止的进程"
sleep 2

# 4. 检查是否还有残留进程
echo "4. 检查残留进程..."
REMAINING=$(ps aux | grep webhook | grep -v grep || echo "")
if [ -n "$REMAINING" ]; then
    echo "⚠️  发现残留进程，强制清理..."
    killall -9 python3 2>/dev/null || echo "没有 python3 进程需要清理"
    sleep 2
else
    echo "✅ 所有进程已停止"
fi
echo ""

# 5. 检查 systemd 服务
echo "5. 检查 systemd 服务状态..."
if systemctl list-unit-files | grep -q webhook-receiver; then
    echo "webhook-receiver 服务存在"
    systemctl status webhook-receiver --no-pager | head -5
    echo ""
else
    echo "⚠️  webhook-receiver 服务不存在，将使用手动启动"
fi
echo ""

# 6. 启动 webhook receiver
echo "6. 启动 webhook receiver..."
if [ -d "venv" ]; then
    echo "使用虚拟环境启动..."
    nohup venv/bin/python scripts/webhook_receiver_github.py > /var/log/integrate-code/webhook.log 2>&1 &
else
    echo "使用系统 Python 启动..."
    nohup python3 scripts/webhook_receiver_github.py > /var/log/integrate-code/webhook.log 2>&1 &
fi

sleep 3
echo ""

# 7. 验证进程启动
echo "7. 验证进程状态..."
if pgrep -f "webhook_receiver_github.py" > /dev/null; then
    PID_LIST=$(pgrep -f "webhook_receiver_github.py" | tr '\n' ' ')
    echo "✅ Webhook receiver 进程已启动 (PID: $PID_LIST)"

    # 显示所有相关进程
    echo "所有 webhook 进程:"
    ps aux | grep webhook_receiver_github.py | grep -v grep
else
    echo "❌ Webhook receiver 进程启动失败"
    echo "查看日志："
    tail -20 /var/log/integrate-code/webhook.log
    exit 1
fi
echo ""

# 8. 测试 webhook 端点
echo "8. 测试 webhook 端点..."
sleep 2
if curl -s http://localhost:9000/webhook/health > /dev/null 2>&1; then
    echo "✅ Webhook 端点响应正常"
    curl -s http://localhost:9000/webhook/health | head -5
else
    echo "❌ Webhook 端点无响应"
    echo "查看日志："
    tail -30 /var/log/integrate-code/webhook.log
fi
echo ""

echo "=========================================="
echo "诊断和修复完成"
echo "=========================================="
echo ""
echo "如果问题仍然存在，请检查："
echo "1. /var/log/integrate-code/webhook.log"
echo "2. systemctl status webhook-receiver"
echo "3. journalctl -u webhook-receiver -n 50"
