#!/bin/bash

# Git 配置检查脚本
# 检查并显示当前 Git 配置状态

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

# 检查 Git 是否安装
check_git_installed() {
    log_step "检查 Git 安装状态..."

    if ! command -v git &> /dev/null; then
        log_error "Git 未安装"
        log_info "请安装 Git: apt-get install git (Ubuntu/Debian) 或 yum install git (CentOS/RHEL)"
        exit 1
    fi

    GIT_VERSION=$(git --version)
    log_info "Git 版本: $GIT_VERSION"
}

# 检查 Git 用户配置
check_user_config() {
    log_step "检查 Git 用户配置..."

    USER_NAME=$(git config --global user.name 2>/dev/null)
    USER_EMAIL=$(git config --global user.email 2>/dev/null)

    if [ -z "$USER_NAME" ]; then
        log_warn "未配置用户名"
        log_info "建议设置: git config --global user.name 'Your Name'"
    else
        log_info "用户名: $USER_NAME"
    fi

    if [ -z "$USER_EMAIL" ]; then
        log_warn "未配置用户邮箱"
        log_info "建议设置: git config --global user.email 'your.email@example.com'"
    else
        log_info "用户邮箱: $USER_EMAIL"
    fi
}

# 检查网络配置
check_network_config() {
    log_step "检查 Git 网络配置..."

    # 检查缓冲区大小
    POST_BUFFER=$(git config --global http.postBuffer 2>/dev/null)
    MAX_REQUEST_BUFFER=$(git config --global http.maxRequestBuffer 2>/dev/null)

    if [ -n "$POST_BUFFER" ]; then
        log_info "HTTP POST 缓冲区: $(($POST_BUFFER / 1024 / 1024)) MB"
    else
        log_warn "未配置 HTTP POST 缓冲区（建议 524288000 = 500MB）"
    fi

    if [ -n "$MAX_REQUEST_BUFFER" ]; then
        log_info "HTTP 请求缓冲区: $MAX_REQUEST_BUFFER"
    else
        log_warn "未配置 HTTP 请求缓冲区（建议 100M）"
    fi

    # 检查压缩设置
    COMPRESSION=$(git config --global core.compression 2>/dev/null)
    if [ -n "$COMPRESSION" ]; then
        log_info "压缩级别: $COMPRESSION"
    else
        log_warn "未配置压缩级别（建议设置为 9）"
    fi
}

# 检查代理配置
check_proxy_config() {
    log_step "检查 Git 代理配置..."

    GITHUB_PROXY=$(git config --global --get http.https://github.com.proxy 2>/dev/null)
    HTTP_PROXY=$(git config --global --get http.proxy 2>/dev/null)
    HTTPS_PROXY=$(git config --global --get https.proxy 2>/dev/null)

    if [ -n "$GITHUB_PROXY" ]; then
        log_info "GitHub 专用代理: $GITHUB_PROXY"
    else
        log_warn "未配置 GitHub 专用代理"
        log_info "如需配置: git config --global http.https://github.proxy http://proxy-server:port"
    fi

    if [ -n "$HTTP_PROXY" ]; then
        log_info "HTTP 通用代理: $HTTP_PROXY"
    fi

    if [ -n "$HTTPS_PROXY" ]; then
        log_info "HTTPS 通用代理: $HTTPS_PROXY"
    fi

    if [ -z "$GITHUB_PROXY" ] && [ -z "$HTTP_PROXY" ] && [ -z "$HTTPS_PROXY" ]; then
        log_warn "未配置任何代理，直接访问 GitHub 可能较慢"
    fi
}

# 检查凭证存储
check_credential_helper() {
    log_step "检查凭证存储配置..."

    CREDENTIAL_HELPER=$(git config --global credential.helper 2>/dev/null)

    if [ -z "$CREDENTIAL_HELPER" ]; then
        log_warn "未配置凭证存储"
        log_info "建议配置: git config --global credential.helper store"
    else
        log_info "凭证存储方式: $CREDENTIAL_HELPER"
    fi
}

# 检查项目远程仓库
check_remote_repos() {
    log_step "检查项目远程仓库..."

    if [ ! -d "/opt/Home-page/.git" ]; then
        log_warn "项目目录不是一个 Git 仓库: /opt/Home-page"
        return
    fi

    cd /opt/Home-page 2>/dev/null || return

    REPOS=$(git remote -v 2>/dev/null)
    if [ -z "$REPOS" ]; then
        log_warn "未配置远程仓库"
    else
        log_info "远程仓库配置:"
        echo "$REPOS"
    fi

    # 检查 origin 远程仓库
    if git remote | grep -q "^origin$"; then
        ORIGIN_URL=$(git remote get-url origin 2>/dev/null)
        if [[ "$ORIGIN_URL" == *"github.com"* ]]; then
            log_info "origin 远程仓库: GitHub"
        elif [[ "$ORIGIN_URL" == *"gitee.com"* ]]; then
            log_warn "origin 远程仓库: Gitee（当前 CI/CD 流程已去除 Gitee）"
        else
            log_info "origin 远程仓库: $ORIGIN_URL"
        fi
    fi
}

# 测试 GitHub 连接
test_github_connection() {
    log_step "测试 GitHub 连接..."

    # 测试 GitHub 可访问性
    if curl -s --connect-timeout 5 https://github.com > /dev/null 2>&1; then
        log_info "GitHub 连接正常"
    else
        log_warn "无法直接连接 GitHub"

        # 尝试使用代理
        GITHUB_PROXY=$(git config --global --get http.https://github.com.proxy 2>/dev/null)
        if [ -n "$GITHUB_PROXY" ]; then
            log_info "尝试通过代理连接 GitHub..."
            if curl -s --connect-timeout 5 --proxy "$GITHUB_PROXY" https://github.com > /dev/null 2>&1; then
                log_info "通过代理连接 GitHub 成功"
            else
                log_error "通过代理连接 GitHub 失败，请检查代理配置"
            fi
        fi
    fi
}

# 显示所有 Git 配置
show_all_config() {
    log_step "所有 Git 配置..."

    git config --global --list 2>/dev/null || log_info "无全局配置"
}

# 主流程
main() {
    echo ""
    echo "=========================================="
    echo "Git 配置检查"
    echo "=========================================="
    echo ""

    check_git_installed
    check_user_config
    check_network_config
    check_proxy_config
    check_credential_helper
    check_remote_repos
    test_github_connection

    echo ""
    log_step "Git 配置详情"
    show_all_config

    echo ""
    echo "=========================================="
    echo "检查完成"
    echo "=========================================="
    echo ""
    echo "推荐的配置步骤："
    echo ""
    echo "1. 配置用户信息："
    echo "   git config --global user.name 'Your Name'"
    echo "   git config --global user.email 'your.email@example.com'"
    echo ""
    echo "2. 配置缓冲区（大文件传输）："
    echo "   git config --global http.postBuffer 524288000"
    echo "   git config --global http.maxRequestBuffer 100M"
    echo ""
    echo "3. 配置代理（如需访问 GitHub）："
    echo "   git config --global http.https://github.proxy http://proxy-server:port"
    echo ""
    echo "4. 配置凭证存储："
    echo "   git config --global credential.helper store"
    echo ""
}

# 执行
main
