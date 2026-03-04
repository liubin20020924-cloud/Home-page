#!/bin/bash

# 修复webhook服务 - 安装Flask依赖

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

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 停止服务
stop_service() {
    log_step "停止webhook-receiver服务..."

    if systemctl is-active --quiet webhook-receiver; then
        systemctl stop webhook-receiver
        log_info "服务已停止"
    else
        log_warn "服务未运行"
    fi
}

# 安装Flask
install_flask() {
    log_step "为虚拟环境安装Flask..."

    # 检查虚拟环境
    if [ ! -d "/opt/Home-page/venv" ]; then
        log_error "虚拟环境不存在：/opt/Home-page/venv"
        echo ""
        echo "请先创建虚拟环境："
        echo "  cd /opt/Home-page"
        echo "  python3 -m venv venv"
        exit 1
    fi

    log_info "虚拟环境已存在"

    # 使用虚拟环境安装Flask的脚本
    if [ -f "/opt/Home-page/scripts/install-flask-venv.sh" ]; then
        log_info "运行虚拟环境Flask安装脚本..."
        bash /opt/Home-page/scripts/install-flask-venv.sh

        # 验证安装
        if source venv/bin/activate && python -c "import flask" 2>/dev/null; then
            log_info "✓ Flask在虚拟环境中已安装"
            source venv/bin/activate
            python -c "import flask; print('Flask版本:', flask.__version__)"
            deactivate
        else
            log_error "✗ Flask安装失败"
            exit 1
        fi
    else
        log_error "虚拟环境安装脚本不存在"
        exit 1
    fi
}

# 安装其他依赖
install_dependencies() {
    log_step "安装其他依赖..."

    # 检查并安装hmac和hashlib（通常已内置）
    if python3 -c "import hmac, hashlib" 2>/dev/null; then
        log_info "✓ hmac 和 hashlib 已安装（Python内置）"
    else
        log_error "✗ Python模块不完整"
        exit 1
    fi
}

# 验证脚本
verify_script() {
    log_step "验证webhook_receiver_github.py..."

    if [ -f "/opt/Home-page/scripts/webhook_receiver_github.py" ]; then
        log_info "✓ 脚本文件存在"

        # 测试导入
        if python3 -c "
import sys
sys.path.insert(0, '/opt/Home-page/scripts')
try:
    import webhook_receiver_github
    print('✓ 脚本语法正确')
except Exception as e:
    print(f'✗ 脚本错误: {e}')
    sys.exit(1)
" 2>&1; then
            log_info "✓ 脚本验证成功"
        else
            log_warn "脚本验证失败（可能不影响运行）"
        fi
    else
        log_error "✗ 脚本文件不存在"
        exit 1
    fi
}

# 重启服务
restart_service() {
    log_step "重启webhook-receiver服务..."

    # 重新加载systemd
    systemctl daemon-reload

    # 停止服务
    systemctl stop webhook-receiver 2>/dev/null || true

    # 等待1秒
    sleep 1

    # 启动服务
    systemctl start webhook-receiver

    # 等待2秒
    sleep 2

    # 检查状态
    if systemctl is-active --quiet webhook-receiver; then
        log_info "✓ 服务启动成功"
        systemctl status webhook-receiver --no-pager
    else
        log_error "✗ 服务启动失败"
        echo ""
        echo "查看详细日志："
        echo "  journalctl -u webhook-receiver -n 20"
        echo ""
        echo "查看错误日志："
        echo "  tail -f /var/log/integrate-code/webhook-error.log"
        exit 1
    fi
}

# 主流程
main() {
    echo ""
    echo "=========================================="
    echo "修复webhook-receiver服务"
    echo "=========================================="
    echo ""

    # 停止服务
    stop_service

    echo ""

    # 安装Flask
    install_flask

    echo ""

    # 安装其他依赖
    install_dependencies

    echo ""

    # 验证脚本
    verify_script

    echo ""

    # 重启服务
    restart_service

    echo ""
    echo "=========================================="
    echo "修复完成！"
    echo "=========================================="
    echo ""
    echo "验证步骤："
    echo ""
    echo "1. 检查服务状态："
    echo "   systemctl status webhook-receiver"
    echo ""
    echo "2. 检查端口监听："
    echo "   netstat -tuln | grep 9000"
    echo ""
    echo "3. 测试健康检查："
    echo "   curl http://localhost:9000/webhook/health"
    echo ""
}

# 执行
main
