#!/bin/bash

# 云户科技网站 - 智能拉取脚本
# 自动选择最快的源（GitHub或Gitee）进行拉取

set -e

# 配置
PROJECT_DIR="/opt/Home-page"
LOG_FILE="/var/log/integrate-code/smart-pull.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
    log "INFO: $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    log "WARN: $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    log "ERROR: $1"
}

# 测试GitHub速度
test_github_speed() {
    local timeout_seconds=5
    local temp_file=$(mktemp)

    # 测试下载速度
    local speed=$(timeout $timeout_seconds curl -o "$temp_file" -s -w '%{speed_download}' https://github.com 2>/dev/null || echo "0")
    rm -f "$temp_file"

    echo "$speed"
}

# 从Gitee拉取
pull_from_gitee() {
    log_info "从Gitee拉取..."

    cd "$PROJECT_DIR" || {
        log_error "项目目录不存在: $PROJECT_DIR"
        return 1
    }

    # 检查gitee远程仓库是否存在
    if ! git remote | grep -q gitee; then
        log_info "Gitee远程仓库未配置，正在添加..."
        git remote add gitee https://gitee.com/liubin_studies/Home-page.git
    fi

    # 从Gitee拉取
    if git fetch gitee main; then
        git reset --hard gitee/main
        log_info "从Gitee拉取成功"
        return 0
    else
        log_error "从Gitee拉取失败"
        return 1
    fi
}

# 从GitHub拉取
pull_from_github() {
    log_info "从GitHub拉取..."

    cd "$PROJECT_DIR" || {
        log_error "项目目录不存在: $PROJECT_DIR"
        return 1
    }

    # 从GitHub拉取
    if git fetch origin main; then
        git reset --hard origin/main
        log_info "从GitHub拉取成功"
        return 0
    else
        log_error "从GitHub拉取失败"
        return 1
    fi
}

# 主逻辑
main() {
    log_info "=========================================="
    log_info "开始智能拉取..."
    log_info "=========================================="

    # 已迁移到 Gitee，直接从 Gitee 拉取
    log_info "项目已迁移到 Gitee，直接从 Gitee 拉取..."

    if pull_from_gitee; then
        log_info "=========================================="
        log_info "拉取完成（源: Gitee）"
        log_info "=========================================="
    else
        log_error "从Gitee拉取失败"
        return 1
    fi

    # 获取当前提交信息
    if cd "$PROJECT_DIR" 2>/dev/null; then
        CURRENT_COMMIT=$(git rev-parse HEAD | cut -c1-7)
        CURRENT_TIME=$(git log -1 --format='%ci' $CURRENT_COMMIT)
        CURRENT_MESSAGE=$(git log -1 --format='%s' $CURRENT_COMMIT)

        log_info "当前版本: $CURRENT_COMMIT"
        log_info "提交时间: $CURRENT_TIME"
        log_info "提交信息: $CURRENT_MESSAGE"
    fi
}

# 执行
main
