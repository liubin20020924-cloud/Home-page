#!/bin/bash

# 腾讯云主机Git一键配置脚本

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

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用 root 权限运行此脚本"
        exit 1
    fi
}

# 配置Git
setup_git() {
    log_step "配置Git..."

    # 增加缓冲区大小（大文件传输）
    git config --global http.postBuffer 524288000 2>/dev/null || true
    git config --global http.maxRequestBuffer 100M 2>/dev/null || true

    # 启用最大压缩
    git config --global core.compression 9 2>/dev/null || true

    # 配置凭证存储
    git config --global credential.helper store 2>/dev/null || true

    log_info "Git配置完成"
}

# 添加Gitee远程仓库
setup_gitee_remote() {
    log_step "添加Gitee远程仓库..."

    cd /opt/Home-page 2>/dev/null || {
        log_error "项目目录不存在: /opt/Home-page"
        exit 1
    }

    # 检查是否已存在gitee远程仓库
    if git remote | grep -q gitee; then
        log_info "Gitee远程仓库已存在"
    else
        git remote add gitee https://gitee.com/liubin_studies/Home-page.git
        log_info "Gitee远程仓库已添加"
    fi

    # 显示配置的远程仓库
    log_info "当前远程仓库:"
    git remote -v
}

# 配置智能拉取脚本
setup_smart_pull() {
    log_step "配置智能拉取脚本..."

    cd /opt/Home-page 2>/dev/null || {
        log_error "项目目录不存在: /opt/Home-page"
        exit 1
    }

    # 设置脚本权限
    chmod +x scripts/smart-pull.sh 2>/dev/null || true

    log_info "智能拉取脚本已配置"
}

# 测试拉取
test_pull() {
    log_step "测试智能拉取..."

    cd /opt/Home-page 2>/dev/null || {
        log_error "项目目录不存在: /opt/Home-page"
        exit 1
    }

    # 执行智能拉取
    if bash scripts/smart-pull.sh; then
        log_info "智能拉取测试成功"
    else
        log_warn "智能拉取测试失败，请检查配置"
    fi
}

# 创建日志目录
create_log_dir() {
    log_step "创建日志目录..."

    mkdir -p /var/log/integrate-code 2>/dev/null || true

    log_info "日志目录创建完成"
}

# 主流程
main() {
    echo ""
    echo "=========================================="
    echo "腾讯云主机Git一键配置"
    echo "=========================================="
    echo ""

    # 检查root权限
    check_root

    # 创建日志目录
    create_log_dir

    # 配置Git
    setup_git

    # 添加Gitee远程仓库
    setup_gitee_remote

    # 配置智能拉取脚本
    setup_smart_pull

    # 测试拉取
    test_pull

    echo ""
    echo "=========================================="
    echo "配置完成！"
    echo "=========================================="
    echo ""
    echo "下一步操作："
    echo ""
    echo "1. 运行部署服务安装脚本："
    echo "   bash /opt/Home-page/scripts/deploy_service.sh"
    echo ""
    echo "2. 手动测试部署："
    echo "   bash /opt/Home-page/scripts/deploy.sh"
    echo ""
    echo "3. 查看配置："
    echo "   git remote -v"
    echo "   git config --global --list"
    echo ""
}

# 执行
main
