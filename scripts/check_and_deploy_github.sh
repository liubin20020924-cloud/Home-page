#!/bin/bash

# 云户科技网站 - 自动检测并部署脚本（GitHub版）
# 定时检查 GitHub 更新，自动触发部署

set -e

# 配置
PROJECT_DIR="/opt/Home-page"
LOG_FILE="/var/log/integrate-code/auto-deploy.log"
WEBHOOK_SECRET="your-webhook-secret-here"  # 请修改为实际密钥
WEBHOOK_URL="http://localhost:9000/webhook/github"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
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

# 检查远程更新
check_updates() {
    cd "$PROJECT_DIR" || exit 1

    # 获取本地最新提交
    LOCAL_COMMIT=$(git rev-parse HEAD)

    # 获取远程最新提交
    git fetch origin main 2>&1 || {
        log_error "无法获取远程更新"
        return 1
    }

    REMOTE_COMMIT=$(git rev-parse origin/main)

    # 比较提交
    if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
        log_info "检测到新版本"
        log_info "本地: ${LOCAL_COMMIT:0:7}"
        log_info "远程: ${REMOTE_COMMIT:0:7}"

        # 获取更新信息
        NEW_COMMITS=$(git log --oneline $LOCAL_COMMIT..$REMOTE_COMMIT)
        log_info "新增提交:"
        echo "$NEW_COMMITS" | while read commit; do
            log_info "  - $commit"
        done

        return 0  # 有更新
    else
        log_info "已是最新版本"
        return 1  # 无更新
    fi
}

# 触发部署
trigger_deployment() {
    log_info "触发部署..."

    # 调用 Webhook 触发部署
    RESPONSE=$(curl -s -X POST "$WEBHOOK_URL" \
        -H "X-Hub-Signature-256: $WEBHOOK_SECRET" \
        -H "Content-Type: application/json" \
        -d '{"ref": "refs/heads/main"}' 2>&1)

    if echo "$RESPONSE" | grep -q "Deployment started\|Deployment triggered"; then
        log_info "部署已触发"
        return 0
    else
        log_error "部署触发失败: $RESPONSE"
        return 1
    fi
}

# 主流程
main() {
    log_info "=========================================="
    log_info "开始检查更新..."
    log_info "=========================================="

    # 检查更新
    if check_updates; then
        # 有更新，触发部署
        if trigger_deployment; then
            log_info "=========================================="
            log_info "自动部署流程已启动"
            log_info "=========================================="
        else
            log_error "=========================================="
            log_error "自动部署触发失败，请手动处理"
            log_error "=========================================="
            exit 1
        fi
    fi

    log_info "检查完成"
}

# 执行
main
