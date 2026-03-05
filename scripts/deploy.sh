#!/bin/bash

# 云户科技网站 - 自动部署脚本
# 用于 GitHub Actions SSH 触发或手动执行

set -e  # 遇到错误立即退出

# 配置
PROJECT_DIR="/opt/Home-page"
BACKUP_DIR="/var/backups/Home-page"
LOG_FILE="/var/log/Home-page/deploy.log"
REPO_URL="https://github.com/liubin20020924-cloud/Home-page.git"
APP_NAME="Home-page"
SERVICE_NAME="Home-page"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
    # 设置日志文件权限为仅所有者可读写
    if [ -f "$LOG_FILE" ]; then
        chmod 600 "$LOG_FILE"
    fi
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

# 验证提交签名（如果已配置）
verify_commit_signature() {
    log_info "验证提交签名..."

    cd "$PROJECT_DIR"

    # 检查是否配置了 GPG 签名验证
    if ! git config --get commit.gpgsign >/dev/null 2>&1; then
        log_warn "未配置 GPG 签名验证，跳过验证步骤"
        return 0
    fi

    # 验证最新提交的签名
    LATEST_COMMIT=$(git rev-parse origin/main)
    if ! git verify-commit "$LATEST_COMMIT" 2>/dev/null; then
        log_error "提交签名验证失败，拒绝部署"
        log_error "提交哈希: $LATEST_COMMIT"
        exit 1
    fi

    log_info "提交签名验证通过"
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
        # 验证提交签名（防止代码被篡改）
        verify_commit_signature
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

# 部署前环境检查
pre_deploy_check() {
    log_info "预部署检查..."

    # 检查磁盘空间（至少 1GB）
    AVAILABLE_SPACE=$(df -BG "$PROJECT_DIR" | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 1 ]; then
        log_error "磁盘空间不足，至少需要 1GB，当前: ${AVAILABLE_SPACE}GB"
        exit 1
    fi
    log_info "磁盘空间检查通过: ${AVAILABLE_SPACE}GB 可用"

    # 检查 Python 版本
    if ! command -v python3 &> /dev/null; then
        log_error "未找到 Python3"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    log_info "Python 版本: $PYTHON_VERSION"

    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        log_error "未找到 pip3"
        exit 1
    fi
    log_info "Pip 检查通过"

    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        log_warn "虚拟环境不存在，将使用系统 Python"
    else
        log_info "虚拟环境已存在"
    fi

    # 检查 requirements.txt
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt 文件不存在"
        exit 1
    fi
    log_info "requirements.txt 检查通过"

    # 检查部署脚本
    if [ ! -f "./scripts/deploy.sh" ]; then
        log_error "部署脚本不存在: ./scripts/deploy.sh"
        exit 1
    fi
    log_info "部署脚本检查通过"

    log_info "预部署检查通过"
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
        nohup venv/bin/python app.py > /var/log/Home-page/app.log 2>&1 &
    else
        log_info "使用系统Python启动应用..."
        nohup python3 app.py > /var/log/Home-page/app.log 2>&1 &
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

    # 部署前检查
    pre_deploy_check

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
