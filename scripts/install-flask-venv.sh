#!/bin/bash

# 为虚拟环境安装Flask依赖

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 检查虚拟环境
check_venv() {
    if [ ! -d "/opt/Home-page/venv" ]; then
        log_error "虚拟环境不存在：/opt/Home-page/venv"
        echo ""
        echo "请先创建虚拟环境："
        echo "  cd /opt/Home-page"
        echo "  python3 -m venv venv"
        exit 1
    fi

    log_info "✓ 虚拟环境已存在"
}

# 为虚拟环境安装Flask
install_flask_in_venv() {
    log_info "为虚拟环境安装Flask..."

    cd /opt/Home-page

    # 激活虚拟环境
    source venv/bin/activate

    # 检查pip是否可用
    if command -v pip &> /dev/null; then
        log_info "使用pip安装Flask..."
        pip install flask -q
    elif command -v pip3 &> /dev/null; then
        log_warn "警告：使用pip3可能指向系统Python"
        pip3 install flask -q
    else
        log_error "pip命令不可用"
        echo ""
        echo "请确保虚拟环境已正确激活"
        exit 1
    fi

    # 验证安装
    python -c "import flask; print('Flask版本:', flask.__version__)"

    # 退出虚拟环境
    deactivate

    log_info "✓ Flask安装完成"
}

# 安装其他依赖
install_other_dependencies() {
    log_info "检查其他依赖..."

    cd /opt/Home-page

    # 激活虚拟环境
    source venv/bin/activate

    # 部署脚本需要的依赖
    log_info "安装部署脚本依赖..."
    pip install flask -q 2>/dev/null || log_warn "Flask已安装"

    # 检查应用需要的依赖
    if [ -f "requirements.txt" ]; then
        log_info "安装应用依赖..."
        pip install -r requirements.txt -q
    fi

    # 退出虚拟环境
    deactivate

    log_info "✓ 依赖安装完成"
}

# 重启webhook服务
restart_webhook() {
    log_info "重启webhook-receiver服务..."

    systemctl daemon-reload
    systemctl stop webhook-receiver 2>/dev/null || true
    sleep 1
    systemctl start webhook-receiver
    sleep 2

    if systemctl is-active --quiet webhook-receiver; then
        log_info "✓ webhook-receiver服务运行成功"
    else
        log_error "✗ webhook-receiver服务启动失败"
        echo ""
        echo "查看日志："
        echo "  journalctl -u webhook-receiver -n 20"
        exit 1
    fi
}

# 主流程
main() {
    echo ""
    echo "=========================================="
    echo "为虚拟环境安装Flask"
    echo "=========================================="
    echo ""

    # 检查虚拟环境
    check_venv

    echo ""

    # 安装Flask
    install_flask_in_venv

    echo ""

    # 安装其他依赖
    install_other_dependencies

    echo ""

    # 重启webhook服务
    restart_webhook

    echo ""
    echo "=========================================="
    echo "完成！"
    echo "=========================================="
    echo ""
    echo "验证步骤："
    echo ""
    echo "1. 检查Flask已安装："
    echo "   cd /opt/Home-page"
    echo "   source venv/bin/activate"
    echo "   python -c \"import flask; print('Flask:', flask.__version__)\""
    echo ""
    echo "2. 检查webhook服务："
    echo "   systemctl status webhook-receiver"
    echo ""
    echo "3. 测试健康检查："
    echo "   curl http://localhost:9000/webhook/health"
    echo ""
}

# 执行
main
