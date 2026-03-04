#!/bin/bash

# 详细诊断webhook-receiver服务问题

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 停止服务
stop_service() {
    log_info "停止webhook-receiver服务..."
    systemctl stop webhook-receiver 2>/dev/null || true
    sleep 1
}

# 测试脚本导入
test_imports() {
    log_info "测试Python模块导入..."

    cd /opt/Home-page
    source venv/bin/activate

    # 测试Flask导入
    python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/Home-page/scripts')
try:
    import flask
    print("✓ Flask可以导入，版本:", flask.__version__)
except ImportError as e:
    print("✗ Flask导入失败:", e)
    sys.exit(1)

try:
    import hmac
    print("✓ hmac模块可以导入")
except ImportError as e:
    print("✗ hmac模块导入失败:", e)
    sys.exit(1)

try:
    import hashlib
    print("✓ hashlib模块可以导入")
except ImportError as e:
    print("✗ hashlib模块导入失败:", e)
    sys.exit(1)

try:
    import subprocess
    print("✓ subprocess模块可以导入")
except ImportError as e:
    print("✗ subprocess模块导入失败:", e)
    sys.exit(1)

try:
    import logging
    print("✓ logging模块可以导入")
except ImportError as e:
    print("✗ logging模块导入失败:", e)
    sys.exit(1)

try:
    import os
    print("✓ os模块可以导入")
except ImportError as e:
    print("✗ os模块导入失败:", e)
    sys.exit(1)
EOF

    deactivate
}

# 测试脚本语法
test_syntax() {
    log_info "测试webhook_receiver_github.py语法..."

    cd /opt/Home-page
    source venv/bin/activate

    python3 -m py_compile scripts/webhook_receiver_github.py

    if [ $? -eq 0 ]; then
        log_info "✓ 脚本语法正确"
    else
        log_error "✗ 脚本语法错误"
        exit 1
    fi

    deactivate
}

# 手动运行脚本测试
test_manual_run() {
    log_info "手动运行webhook_receiver_github.py（10秒超时）..."

    cd /opt/Home-page
    source venv/bin/activate

    timeout 10 python3 scripts/webhook_receiver_github.py &
    PID=$!

    sleep 3

    # 检查进程是否还在运行
    if ps -p $PID > /dev/null; then
        log_info "✓ 脚本正在运行（PID: $PID）"
        
        # 测试端口监听
        sleep 2
        netstat -tuln | grep 9000 > /dev/null && \
            log_info "✓ 端口9000正在监听" || \
            log_error "✗ 端口9000未监听"

        # 停止测试进程
        kill $PID 2>/dev/null
        wait $PID 2>/dev/null
        log_info "✓ 测试进程已停止"
    else
        log_error "✗ 脚本启动失败"
        deactivate
        exit 1
    fi

    deactivate
}

# 检查服务文件
check_service_file() {
    log_info "检查systemd服务文件..."

    if [ -f "/etc/systemd/system/webhook-receiver.service" ]; then
        log_info "✓ 服务文件存在"
        echo ""
        echo "服务文件内容："
        echo "=========================================="
        cat /etc/systemd/system/webhook-receiver.service
        echo "=========================================="
    else
        log_error "✗ 服务文件不存在"
    fi
}

# 检查Python路径
check_python_path() {
    log_info "检查服务文件中的Python路径..."

    if [ -f "/etc/systemd/system/webhook-receiver.service" ]; then
        PYTHON_PATH=$(grep "ExecStart=" /etc/systemd/system/webhook-receiver.service | sed 's|ExecStart=.*python3 ||')

        if [ -n "$PYTHON_PATH" ]; then
            log_info "服务文件Python路径: $PYTHON_PATH"
        else
            log_error "服务文件中未找到Python路径"
        fi

        # 检查虚拟环境Python
        if [ -f "/opt/Home-page/venv/bin/python" ]; then
            log_info "虚拟环境Python存在: /opt/Home-page/venv/bin/python"
            echo ""
            echo "建议：修改服务文件使用虚拟环境Python"
            echo ""
            echo "ExecStart=/opt/Home-page/venv/bin/python /opt/Home-page/scripts/webhook_receiver_github.py"
        fi
    fi
}

# 主流程
main() {
    echo ""
    echo "=========================================="
    echo "详细诊断webhook-receiver服务"
    echo "=========================================="
    echo ""

    # 停止服务
    stop_service

    echo ""

    # 测试模块导入
    test_imports

    echo ""

    # 测试语法
    test_syntax

    echo ""

    # 手动运行测试
    test_manual_run

    echo ""

    # 检查服务文件
    check_service_file

    echo ""

    # 检查Python路径
    check_python_path

    echo ""
    echo "=========================================="
    echo "诊断完成"
    echo "=========================================="
    echo ""
    echo "根据诊断结果，可能需要："
    echo ""
    echo "1. 如果需要，修改服务文件使用虚拟环境Python："
    echo "   nano /etc/systemd/system/webhook-receiver.service"
    echo "   修改 ExecStart= 为："
    echo "   ExecStart=/opt/Home-page/venv/bin/python /opt/Home-page/scripts/webhook_receiver_github.py"
    echo ""
    echo "2. 重新加载systemd并重启服务："
    echo "   systemctl daemon-reload"
    echo "   systemctl restart webhook-receiver"
    echo ""
    echo "3. 查看服务状态："
    echo "   systemctl status webhook-receiver"
}

# 执行
main
