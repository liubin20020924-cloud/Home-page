#!/bin/bash

# 快速修复 webhook - 直接覆盖并重启

set -e

PROJECT_DIR="/opt/Home-page"
cd "$PROJECT_DIR"

echo "=========================================="
echo "快速修复 Webhook Receiver"
echo "=========================================="

# 1. 确保代码是最新的
echo "1. 确保代码是最新的..."
git fetch origin
git reset --hard origin/main
CURRENT_COMMIT=$(git rev-parse --short HEAD)
echo "当前版本: $CURRENT_COMMIT"
echo ""

# 2. 验证代码
echo "2. 验证代码..."
if grep -q "isinstance(raw_payload, str)" scripts/webhook_receiver_github.py; then
    echo "✅ 代码已包含类型检查修复"
else
    echo "❌ 代码不包含修复，退出"
    exit 1
fi
echo ""

# 3. 杀死所有 webhook 进程
echo "3. 停止所有 webhook 进程..."
pkill -9 -f "webhook_receiver_github.py" || true
pkill -9 -f "webhook.*receiver" || true
killall -9 python3 2>/dev/null || true
sleep 3

# 4. 确认没有残留
echo "4. 检查残留进程..."
if pgrep -f "webhook" > /dev/null; then
    echo "⚠️  仍有残留进程，再次清理..."
    ps aux | grep webhook | grep -v grep | awk '{print $2}' | xargs -r kill -9
    sleep 2
fi
echo "✅ 所有进程已停止"
echo ""

# 5. 禁用并停止 systemd 服务（如果存在）
echo "5. 处理 systemd 服务..."
if systemctl list-unit-files | grep -q webhook-receiver; then
    echo "停止并禁用 webhook-receiver 服务..."
    systemctl stop webhook-receiver 2>/dev/null || true
    systemctl disable webhook-receiver 2>/dev/null || true
    echo "✅ Systemd 服务已停止"
fi
echo ""

# 6. 手动启动（不使用 systemd）
echo "6. 手动启动 webhook receiver..."
if [ -d "venv" ]; then
    echo "使用虚拟环境: venv/bin/python"
    nohup venv/bin/python /opt/Home-page/scripts/webhook_receiver_github.py \
        > /var/log/integrate-code/webhook.log 2>&1 &
else
    echo "使用系统 Python: python3"
    nohup python3 /opt/Home-page/scripts/webhook_receiver_github.py \
        > /var/log/integrate-code/webhook.log 2>&1 &
fi
echo "✅ 进程已启动"
echo ""

# 7. 等待并验证
echo "7. 等待启动完成..."
sleep 5

if pgrep -f "webhook_receiver_github.py" > /dev/null; then
    PID=$(pgrep -f "webhook_receiver_github.py")
    echo "✅ 进程运行中 (PID: $PID)"

    # 显示进程信息
    echo ""
    echo "进程详情:"
    ps -p $PID -o pid,ppid,cmd
    echo ""

    # 测试端点
    echo "测试健康检查端点:"
    sleep 2
    if curl -s http://localhost:9000/webhook/health; then
        echo ""
        echo "✅ Webhook 端点响应正常"
    else
        echo "❌ Webhook 端点无响应"
        echo ""
        echo "日志内容:"
        tail -30 /var/log/integrate-code/webhook.log
    fi
else
    echo "❌ 进程未启动"
    echo ""
    echo "日志内容:"
    tail -30 /var/log/integrate-code/webhook.log
    exit 1
fi

echo ""
echo "=========================================="
echo "修复完成！"
echo "=========================================="
echo ""
echo "下次推送代码时，webhook 通知应该会成功"
