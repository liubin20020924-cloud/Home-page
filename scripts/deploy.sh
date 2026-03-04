#!/bin/bash

# 云户科技网站 - 自动部署脚本
# 用于 GitHub Webhook 触发或手动执行

set -e  # 遇到错误立即退出

# 配置
PROJECT_DIR="/opt/Home-page"
BACKUP_DIR="/opt/Home-page/backups"
LOG_FILE="/var/log/integrate-code/deploy.log"
REPO_URL="https://github.com/liubin20020924-cloud/Home-page.git"
APP_NAME="Home-page"
SERVICE_NAME="integrate-code"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# 创建备份
create_backup() {
    log_info "创建备份..."

    BACKUP_NAME="${APP_NAME}_$(date '+%Y%m%d_%H%M%S')"
    BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

    mkdir -p "$BACKUP_DIR"

    # 备份代码 (使用 rsync 避免"复制到自身"错误)
    if command -v rsync &> /dev/null; then
        rsync -av --delete "$PROJECT_DIR/" "$BACKUP_PATH/"
    else
        # 如果 rsync 不可用,使用 tar
        cd "$BACKUP_DIR"
        tar -czf "${BACKUP_NAME}.tar.gz" -C "$PROJECT_DIR" .
        BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
    fi

    # 保留最近 5 个备份
    cd "$BACKUP_DIR"
    ls -t | tail -n +6 | xargs rm -rf

    log_info "备份创建完成: $BACKUP_PATH"
}

# 拉取最新代码
pull_code() {
    log_info "拉取最新代码..."

    cd "$PROJECT_DIR"

    # 获取当前分支
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    log_info "当前分支: $CURRENT_BRANCH"

    # 使用智能拉取脚本（自动选择 GitHub 或 Gitee）
    log_info "使用智能拉取脚本..."
    if [ -f "./scripts/smart-pull.sh" ]; then
        bash ./scripts/smart-pull.sh
        if [ $? -eq 0 ]; then
            log_info "代码拉取完成"
        else
            log_error "智能拉取失败，尝试直接从 GitHub 拉取..."
            git fetch origin
            git reset --hard origin/main
            log_info "代码拉取完成"
        fi
    else
        log_warn "智能拉取脚本不存在，直接从 GitHub 拉取..."
        git fetch origin
        git reset --hard origin/main
        log_info "代码拉取完成"
    fi
}

# 更新依赖
update_dependencies() {
    log_info "更新依赖..."

    cd "$PROJECT_DIR"

    # 激活虚拟环境（如果使用）
    if [ -d "venv" ]; then
        log_info "检测到虚拟环境，正在激活..."
        source venv/bin/activate
    fi

    # 更新依赖
    pip install -r requirements.txt -q

    log_info "依赖更新完成"
}

# 数据库迁移（如需要）
migrate_database() {
    log_info "检查数据库迁移..."

    cd "$PROJECT_DIR"

    # 检查是否有新的迁移脚本
    if [ -d "database/patches" ]; then
        log_info "执行数据库迁移..."
        # 这里可以添加具体的迁移逻辑
    fi

    log_info "数据库迁移检查完成"
}

# 重启应用
restart_app() {
    log_info "重启应用..."

    cd "$PROJECT_DIR"

    # 停止旧进程
    pkill -f "app.py" || true
    sleep 2

    # 启动新进程（使用虚拟环境，如果存在）
    if [ -d "venv" ]; then
        log_info "使用虚拟环境启动应用..."
        nohup venv/bin/python app.py > /var/log/integrate-code/app.log 2>&1 &
    else
        log_info "使用系统Python启动应用..."
        nohup python3 app.py > /var/log/integrate-code/app.log 2>&1 &
    fi

    # 等待应用启动
    sleep 5

    # 检查进程状态
    if pgrep -f "app.py" > /dev/null; then
        log_info "应用启动成功"
    else
        log_error "应用启动失败"
        exit 1
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."

    MAX_RETRIES=10
    RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        # 检查应用是否响应
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ | grep -q "200\|302"; then
            log_info "健康检查通过"
            return 0
        fi

        RETRY_COUNT=$((RETRY_COUNT + 1))
        log_warn "健康检查失败，重试 $RETRY_COUNT/$MAX_RETRIES..."
        sleep 3
    done

    log_error "健康检查失败，超过最大重试次数"
    return 1
}

# 主部署流程
main() {
    log_info "========================================"
    log_info "开始部署: $APP_NAME"
    log_info "========================================"

    # 创建备份
    create_backup

    # 拉取代码
    pull_code

    # 更新依赖
    update_dependencies

    # 数据库迁移
    migrate_database

    # 重启应用
    restart_app

    # 健康检查
    if health_check; then
        log_info "========================================"
        log_info "部署成功!"
        log_info "========================================"
        exit 0
    else
        log_error "========================================"
        log_error "部署失败!"
        log_error "========================================"

        # 回滚
        log_warn "开始回滚..."
        rollback_to_latest_backup

        exit 1
    fi
}

# 回滚到最新备份
rollback_to_latest_backup() {
    log_info "回滚到最新备份..."

    # 获取最新备份
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR" | head -1)

    if [ -z "$LATEST_BACKUP" ]; then
        log_error "没有可用的备份"
        return 1
    fi

    log_info "使用备份: $LATEST_BACKUP"

    # 停止应用
    pkill -f "app.py" || true
    sleep 2

    # 恢复备份
    rm -rf "$PROJECT_DIR"/*
    cp -r "$BACKUP_DIR/$LATEST_BACKUP"/* "$PROJECT_DIR/"

    # 重启应用
    restart_app

    log_info "回滚完成"
}

# 执行部署
main
