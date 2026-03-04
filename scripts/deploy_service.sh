#!/bin/bash

# 云户科技网站 - 部署服务管理脚本
# 用于安装、配置和管理云主机自动部署服务（GitHub版本）

set -e

# 配置
PROJECT_DIR="/opt/Home-page"
LOG_DIR="/var/log/integrate-code"
SERVICE_NAME="webhook-receiver"
WEBHOOK_SECRET="your-webhook-secret-here"

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

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用 root 权限运行此脚本"
        exit 1
    fi
}

# 创建必要目录
create_directories() {
    log_step "创建必要目录..."
    mkdir -p "$LOG_DIR"
    mkdir -p "$PROJECT_DIR/backups"
    log_info "目录创建完成"
}

# 设置脚本权限
set_permissions() {
    log_step "设置脚本权限..."
    chmod +x "$PROJECT_DIR/scripts/deploy.sh"
    chmod +x "$PROJECT_DIR/scripts/rollback.sh"
    chmod +x "$PROJECT_DIR/scripts/check_and_deploy.sh"
    chmod +x "$PROJECT_DIR/scripts/webhook_receiver_github.py"
    chmod +x "$PROJECT_DIR/scripts/check_and_deploy_github.sh"
    log_info "权限设置完成"
}

# 创建 webhook 接收器服务
create_webhook_service() {
    log_step "创建 GitHub webhook 接收器服务..."

    cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=CloudDoors GitHub Webhook Receiver
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="WEBHOOK_SECRET=$WEBHOOK_SECRET"
ExecStart=/usr/bin/python3 $PROJECT_DIR/scripts/webhook_receiver_github.py
Restart=always
RestartSec=10

# 日志
StandardOutput=append:$LOG_DIR/webhook.log
StandardError=append:$LOG_DIR/webhook-error.log

[Install]
WantedBy=multi-user.target
EOF

    log_info "服务文件创建完成"
}

# 创建自动检测定时任务
create_cron_job() {
    log_step "配置自动检测定时任务..."

    # 添加 crontab 任务（每5分钟检查一次）
    (crontab -l 2>/dev/null | grep -v "check_and_deploy.sh"; echo "*/5 * * * * $PROJECT_DIR/scripts/check_and_deploy_github.sh >> $LOG_DIR/auto-deploy.log 2>&1") | crontab -

    log_info "定时任务配置完成（每5分钟检查一次）"
}

# 启用并启动服务
start_services() {
    log_step "启用并启动服务..."
    
    # 重新加载 systemd
    systemctl daemon-reload
    
    # 启用服务
    systemctl enable $SERVICE_NAME
    
    # 启动服务
    systemctl start $SERVICE_NAME
    
    # 等待服务启动
    sleep 2
    
    # 检查服务状态
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_info "服务启动成功"
    else
        log_error "服务启动失败"
        systemctl status $SERVICE_NAME
        exit 1
    fi
}

# 配置防火墙（如果需要）
configure_firewall() {
    log_step "配置防火墙..."
    
    if command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=9000/tcp 2>/dev/null || true
        firewall-cmd --reload 2>/dev/null || true
        log_info "防火墙配置完成（已开放端口 9000）"
    elif command -v ufw &> /dev/null; then
        ufw allow 9000/tcp 2>/dev/null || true
        log_info "防火墙配置完成（已开放端口 9000）"
    else
        log_warn "未检测到防火墙，跳过配置"
    fi
}

# 测试 webhook 接收器
test_webhook() {
    log_step "测试 webhook 接收器..."
    
    RESPONSE=$(curl -s http://localhost:9000/webhook/health 2>&1)
    
    if echo "$RESPONSE" | grep -q "ok"; then
        log_info "Webhook 接收器运行正常"
    else
        log_error "Webhook 接收器测试失败: $RESPONSE"
        return 1
    fi
}

# 显示配置信息
show_info() {
    echo ""
    echo "=========================================="
    echo "配置完成！"
    echo "=========================================="
    echo ""
    echo "服务状态："
    echo "  - Webhook 接收器：$(systemctl is-active $SERVICE_NAME)"
    echo "  - 自动检测任务：已配置（每5分钟）"
    echo ""
    echo "相关端口："
    echo "  - Webhook 接收器：9000"
    echo ""
    echo "日志位置："
    echo "  - Webhook 日志：$LOG_DIR/webhook.log"
    echo "  - 部署日志：$LOG_DIR/deploy.log"
    echo "  - 自动检测日志：$LOG_DIR/auto-deploy.log"
    echo ""
    echo "常用命令："
    echo "  - 查看服务状态：systemctl status $SERVICE_NAME"
    echo "  - 重启服务：systemctl restart $SERVICE_NAME"
    echo "  - 查看日志：tail -f $LOG_DIR/webhook.log"
    echo "  - 手动检测更新：$PROJECT_DIR/scripts/check_and_deploy.sh"
    echo ""
    echo "下一步："
    echo "  1. 配置 Gitee Webhook"
    echo "  2. 修改 webhook_receiver.py 中的 WEBHOOK_SECRET"
    echo "  3. 修改 check_and_deploy.sh 中的 WEBHOOK_SECRET"
    echo ""
}

# 主安装流程
main() {
    echo "=========================================="
    echo "云户科技网站 - 自动部署服务安装"
    echo "=========================================="
    echo ""
    
    # 检查 root 权限
    check_root
    
    # 创建目录
    create_directories
    
    # 设置权限
    set_permissions
    
    # 创建 webhook 服务
    create_webhook_service
    
    # 创建定时任务
    create_cron_job
    
    # 启动服务
    start_services
    
    # 配置防火墙
    configure_firewall
    
    # 测试 webhook
    test_webhook
    
    # 显示信息
    show_info
}

# 执行安装
main
