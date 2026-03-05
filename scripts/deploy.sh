#!/bin/bash

# 云户科技网站 - 自动部署脚本
# 用于 GitHub Webhook 触发或手动执行

set -e  # 遇到错误立即退出

# 配置
PROJECT_DIR="/opt/Home-page"
BACKUP_DIR="/var/backups/Home-page"  # 改为 /var/backups 下的项目目录
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

    # 备份代码 (使用 rsync 并确保路径不包含子目录)
    # 避免将项目目录复制到自己的子目录导致错误
    if command -v rsync &> /dev/null; then
        # 确保备份目录不在项目目录内
        if [[ "$BACKUP_PATH" != "$PROJECT_DIR/"* ]]; then
            rsync -av --delete "$PROJECT_DIR/" "$BACKUP_PATH/"
        else
            log_error "备份路径在项目目录内,跳过备份"
            return 1
        fi
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

    # 直接从 GitHub 拉取（确保获取最新代码）
    log_info "从 GitHub 拉取最新代码..."
    git fetch origin
    if [ $? -eq 0 ]; then
        git reset --hard origin/main
        log_info "代码拉取完成"
        log_info "当前版本: $(git rev-parse --short HEAD)"
    else
        log_error "GitHub 拉取失败，尝试备用方案..."
        # 如果 smart-pull 存在，使用智能拉取
        if [ -f "./scripts/smart-pull.sh" ]; then
            bash ./scripts/smart-pull.sh
        fi
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

# 重启 webhook receiver
restart_webhook() {
    log_info "重启 webhook receiver 服务..."

    cd "$PROJECT_DIR"

    # 强制停止所有 webhook 进程
    log_info "停止所有 webhook 进程..."
    pkill -9 -f "webhook_receiver_github.py" || true
    pkill -9 -f "webhook.*receiver" || true
    sleep 2

    # 确保没有残留进程
    if pgrep -f "webhook_receiver_github.py" > /dev/null; then
        log_warn "检测到残留进程，强制清理..."
        killall -9 python3 || true
        sleep 2
    fi

    # 重启 systemd 服务
    if systemctl list-unit-files | grep -q webhook-receiver; then
        log_info "使用 systemd 重启 webhook-receiver 服务..."
        systemctl restart webhook-receiver
        sleep 5

        # 检查服务状态
        if systemctl is-active --quiet webhook-receiver; then
            log_info "✅ Webhook receiver 服务重启成功"
            systemctl status webhook-receiver --no-pager | head -5
        else
            log_warn "⚠️  Webhook receiver 服务启动失败，查看日志:"
            journalctl -u webhook-receiver -n 20 --no-pager
            log_info "尝试手动启动..."

            # 备用方案：手动启动
            if [ -d "venv" ]; then
                log_info "使用虚拟环境手动启动..."
                nohup venv/bin/python scripts/webhook_receiver_github.py > /var/log/integrate-code/webhook.log 2>&1 &
            else
                log_info "使用系统Python手动启动..."
                nohup python3 scripts/webhook_receiver_github.py > /var/log/integrate-code/webhook.log 2>&1 &
            fi

            sleep 3

            # 检查进程
            if pgrep -f "webhook_receiver_github.py" > /dev/null; then
                log_info "✅ Webhook receiver 手动启动成功"
            else
                log_error "❌ Webhook receiver 启动失败"
                return 1
            fi
        fi
    else
        log_warn "webhook-receiver 服务不存在，手动启动..."

        # 备用方案
        if [ -d "venv" ]; then
            nohup venv/bin/python scripts/webhook_receiver_github.py > /var/log/integrate-code/webhook.log 2>&1 &
        else
            nohup python3 scripts/webhook_receiver_github.py > /var/log/integrate-code/webhook.log 2>&1 &
        fi

        sleep 3

        if pgrep -f "webhook_receiver_github.py" > /dev/null; then
            log_info "✅ Webhook receiver 手动启动成功"
        else
            log_error "❌ Webhook receiver 启动失败"
            return 1
        fi
    fi

    # 验证文件是否更新
    log_info "验证 webhook receiver 代码版本..."
    if grep -q "isinstance(raw_payload, str)" scripts/webhook_receiver_github.py; then
        log_info "✅ Webhook receiver 代码已更新（包含类型检查）"
    else
        log_error "❌ Webhook receiver 代码未更新！"
        log_error "请检查代码拉取是否成功"
        return 1
    fi

    # 确保 deploy.sh 有执行权限（git pull 可能会重置权限）
    log_info "设置部署脚本执行权限..."
    chmod +x ./scripts/deploy.sh
    log_info "✅ 权限设置完成"

    log_info "Webhook receiver 重启完成"
    return 0
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

    # 重启 webhook receiver
    restart_webhook

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
