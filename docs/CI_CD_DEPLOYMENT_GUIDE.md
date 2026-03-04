# 云户科技网站 - CI/CD 部署文档

> 本文档描述完整的代码上线流程，从开发到生产环境的自动化部署

---

## 📋 目录

1. [部署流程概述](#部署流程概述)
2. [本地开发流程](#本地开发流程)
3. [Git 工作流](#git-工作流)
4. [CI/CD 自动化部署](#cicd-自动化部署)
5. [云主机部署脚本](#云主机部署脚本)
6. [回滚方案](#回滚方案)
7. [故障排查](#故障排查)

---

## 部署流程概述

### 完整流程图

```
本地开发 → GitHub → Gitee → 云主机 → 部署完成
   ↓         ↓       ↓       ↓
  测试    Pull Request   同步   自动部署
```

### 流程说明

1. **本地开发**
   - 在 `2.2` 分支开发新功能
   - 本地测试验证
   - 提交代码到 GitHub `2.2` 分支

2. **代码审核**
   - 创建 Pull Request 从 `2.2` 到 `main`
   - 代码审核通过后合并到 `main`

3. **代码同步**
   - GitHub `main` 分支自动同步到 Gitee
   - 使用 GitHub Action 或手动同步

4. **自动部署**
   - 云主机检测到 Gitee 更新
   - 拉取最新代码
   - 自动重启应用
   - 健康检查验证

---

## 本地开发流程

### 1. 开发环境准备

#### 1.1 克隆代码

```bash
# 克隆 GitHub 仓库
git clone https://github.com/your-username/integrate-code.git
cd integrate-code

# 创建并切换到开发分支
git checkout -b 2.2
```

#### 1.2 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env
```

#### 1.3 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

#### 1.4 初始化数据库

```bash
# 执行数据库初始化脚本
bash init_db.sh
```

### 2. 开发工作流

#### 2.1 开发新功能

```bash
# 确保在 2.2 分支
git checkout 2.2

# 创建功能分支（可选）
git checkout -b feature/your-feature-name

# 开发代码...

# 查看修改
git status

# 添加修改
git add .

# 提交修改
git commit -m "feat: 添加新功能描述"
```

#### 2.2 本地测试

```bash
# 启动开发服务器
python app.py

# 或使用启动脚本
./start.sh

# 访问应用测试功能
# http://localhost:5000/
```

#### 2.3 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=common --cov=routes --cov=services --cov-report=html
```

#### 2.4 代码检查

```bash
# 检查代码规范
flake8 routes/ common/ services/

# 检查安全漏洞
bandit -r routes/ common/ services/

# 检查依赖
python scripts/check_dependencies.py
```

### 3. 提交到 GitHub

```bash
# 推送到 GitHub
git push origin 2.2

# 如果是功能分支
git push origin feature/your-feature-name
```

---

## Git 工作流

### 分支策略

| 分支 | 用途 | 说明 |
|------|------|------|
| `main` | 生产环境 | 稳定版本，直接部署到生产环境 |
| `2.2` | 开发环境 | 当前开发分支 |
| `feature/*` | 功能分支 | 从 `2.2` 创建，开发完成后合并回 `2.2` |
| `hotfix/*` | 紧急修复 | 从 `main` 创建，修复后合并回 `main` 和 `2.2` |

### Pull Request 流程

#### 步骤 1: 创建 PR

```bash
# 确保代码已推送到 GitHub
git push origin 2.2

# 在 GitHub 上创建 PR
# 从: 2.2
# 到: main
```

#### 步骤 2: 代码审核

1. **自动检查**
   - CI 自动运行测试
   - 代码规范检查
   - 安全扫描

2. **人工审核**
   - 代码审查
   - 功能验证
   - 批准合并

#### 步骤 3: 合并到 main

```bash
# 审核通过后合并到 main
# GitHub 操作界面：Merge Pull Request
```

### 分支保护规则

**main 分支保护设置**：

1. **要求 Pull Request**
   - ✅ 不允许直接推送到 main
   - ✅ 所有更改必须通过 PR

2. **要求状态检查**
   - ✅ 必须通过 CI 测试
   - ✅ 必须通过代码检查

3. **要求审核**
   - ✅ 至少 1 个审核批准
   - ✅ 管理员可以绕过

4. **限制谁可以推送**
   - ✅ 仅管理员和指定人员

---

## CI/CD 自动化部署

### 方案 1: GitHub Action 自动同步

#### 1.1 创建 GitHub Action 配置

**创建文件**: `.github/workflows/sync-to-gitee.yml`

```yaml
name: Sync to Gitee

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Sync to Gitee
        uses: wearerequired/git-mirror-action@master
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
        with:
          source-repo: "git@github.com:your-username/integrate-code.git"
          destination-repo: "git@gitee.com:your-username/integrate-code.git"
```

#### 1.2 配置 SSH 密钥

```bash
# 生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "github-action" -f ~/.ssh/github_gitee_rsa

# 复制私钥内容
cat ~/.ssh/github_gitee_rsa

# 添加公钥到 Gitee
cat ~/.ssh/github_gitee_rsa.pub
```

**配置 GitHub Secrets**：
- 进入 GitHub 仓库设置
- Secrets and variables → Actions
- 添加 `SSH_PRIVATE_KEY`（私钥内容）

**配置 Gitee SSH**：
- 进入 Gitee 设置
- SSH 公钥
- 粘贴公钥内容

### 方案 2: Webhook 触发部署

#### 2.1 创建 Webhook 接收器

**创建文件**: `scripts/webhook_receiver.py`

```python
"""Webhook 接收器 - 接收 Gitee 推送通知"""
from flask import Flask, request, jsonify
import subprocess
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gitee Webhook 密钥
WEBHOOK_SECRET = 'your-webhook-secret-here'

@app.route('/webhook/gitee', methods=['POST'])
def gitee_webhook():
    """接收 Gitee Webhook"""
    # 验证签名
    signature = request.headers.get('X-Gitee-Token')
    if signature != WEBHOOK_SECRET:
        logger.warning("Invalid webhook signature")
        return jsonify({'error': 'Invalid signature'}), 401

    # 解析 payload
    payload = request.json
    ref = payload.get('ref', '')
    branch = ref.replace('refs/heads/', '') if ref else ''

    # 只处理 main 分支的推送
    if branch == 'main':
        logger.info(f"Received push event for branch: {branch}")
        
        try:
            # 执行部署脚本
            result = subprocess.run(
                ['/bin/bash', '/home/user/integrate-code/scripts/deploy.sh'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("Deployment successful")
                return jsonify({'message': 'Deployment started'}), 200
            else:
                logger.error(f"Deployment failed: {result.stderr}")
                return jsonify({'error': 'Deployment failed'}), 500
                
        except subprocess.TimeoutExpired:
            logger.error("Deployment timeout")
            return jsonify({'error': 'Deployment timeout'}), 500
        except Exception as e:
            logger.error(f"Deployment error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    else:
        logger.info(f"Ignoring push event for branch: {branch}")
        return jsonify({'message': 'Ignored'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
```

#### 2.2 配置 Gitee Webhook

1. 进入 Gitee 仓库设置
2. WebHooks 管理 → 添加 WebHook
3. URL: `http://your-server-ip:9000/webhook/gitee`
4. 密码: `your-webhook-secret-here`
5. 选择事件：推送事件

---

## 云主机部署脚本

### 1. 创建部署目录

```bash
# 登录云主机
ssh user@your-server-ip

# 创建部署目录
mkdir -p /opt/integrate-code
cd /opt/integrate-code

# 克隆 Gitee 仓库
git clone https://gitee.com/your-username/integrate-code.git
```

### 2. 创建部署脚本

**创建文件**: `scripts/deploy.sh`

```bash
#!/bin/bash

# 云户科技网站 - 自动部署脚本
# 用于 Gitee Webhook 触发或手动执行

set -e  # 遇到错误立即退出

# 配置
PROJECT_DIR="/opt/integrate-code"
BACKUP_DIR="/opt/integrate-code/backups"
LOG_FILE="/var/log/integrate-code/deploy.log"
REPO_URL="https://gitee.com/your-username/integrate-code.git"
APP_NAME="integrate-code"
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
    
    # 备份代码
    cp -r "$PROJECT_DIR" "$BACKUP_PATH"
    
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
    
    # 拉取最新代码
    git fetch origin
    git reset --hard origin/main
    
    log_info "代码拉取完成"
}

# 更新依赖
update_dependencies() {
    log_info "更新依赖..."
    
    cd "$PROJECT_DIR"
    
    # 激活虚拟环境（如果使用）
    if [ -d "venv" ]; then
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
    
    # 启动新进程
    nohup python3 app.py > /var/log/integrate-code/app.log 2>&1 &
    
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
```

### 3. 设置脚本权限

```bash
# 设置脚本可执行权限
chmod +x scripts/deploy.sh

# 创建日志目录
mkdir -p /var/log/integrate-code
```

### 4. 配置 systemd 服务

**创建文件**: `/etc/systemd/system/integrate-code.service`

```ini
[Unit]
Description=CloudDoors Website - Integrate Code
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/integrate-code
Environment="PATH=/opt/integrate-code/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /opt/integrate-code/app.py
Restart=always
RestartSec=10

# 日志
StandardOutput=append:/var/log/integrate-code/app.log
StandardError=append:/var/log/integrate-code/error.log

[Install]
WantedBy=multi-user.target
```

**启用服务**：

```bash
# 重新加载 systemd
systemctl daemon-reload

# 启用服务
systemctl enable integrate-code

# 启动服务
systemctl start integrate-code

# 查看状态
systemctl status integrate-code

# 查看日志
journalctl -u integrate-code -f
```

### 5. 手动部署命令

```bash
# 登录云主机
ssh user@your-server-ip

# 进入项目目录
cd /opt/integrate-code

# 执行部署脚本
./scripts/deploy.sh
```

### 6. 配置 Gitee SSH 密钥（免密拉取）

```bash
# 生成 SSH 密钥
ssh-keygen -t rsa -b 4096 -C "deploy-server" -f ~/.ssh/gitee_deploy

# 复制公钥
cat ~/.ssh/gitee_deploy.pub

# 添加到 Gitee SSH 公钥
# 进入 Gitee 设置 → SSH 公钥 → 粘贴公钥
```

---

## 回滚方案

### 1. 手动回滚

```bash
# 登录云主机
ssh user@your-server-ip

# 进入项目目录
cd /opt/integrate-code

# 查看备份
ls -lh /opt/integrate-code/backups/

# 选择要回滚的版本
BACKUP_VERSION="integrate-code_20260302_150000"

# 停止服务
systemctl stop integrate-code

# 恢复备份
rm -rf /opt/integrate-code/*
cp -r /opt/integrate-code/backups/$BACKUP_VERSION/* /opt/integrate-code/

# 启动服务
systemctl start integrate-code

# 检查状态
systemctl status integrate-code
```

### 2. 快速回滚脚本

**创建文件**: `scripts/rollback.sh`

```bash
#!/bin/bash

# 快速回滚脚本

PROJECT_DIR="/opt/integrate-code"
BACKUP_DIR="/opt/integrate-code/backups"

# 列出可用备份
echo "可用的备份:"
ls -lt "$BACKUP_DIR" | grep -E "^d" | head -10

echo ""
echo "请输入要回滚的版本（例如: integrate-code_20260302_150000）:"
read BACKUP_VERSION

BACKUP_PATH="$BACKUP_DIR/$BACKUP_VERSION"

if [ ! -d "$BACKUP_PATH" ]; then
    echo "错误: 备份不存在"
    exit 1
fi

echo "确认要回滚到 $BACKUP_VERSION 吗? (y/n)"
read CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "取消回滚"
    exit 0
fi

echo "开始回滚..."

# 停止服务
systemctl stop integrate-code

# 恢复备份
rm -rf "$PROJECT_DIR"/*
cp -r "$BACKUP_PATH"/* "$PROJECT_DIR/"

# 启动服务
systemctl start integrate-code

echo "回滚完成"
```

---

## 故障排查

### 1. 查看部署日志

```bash
# 查看部署日志
tail -f /var/log/integrate-code/deploy.log

# 查看应用日志
tail -f /var/log/integrate-code/app.log

# 查看 systemd 日志
journalctl -u integrate-code -f
```

### 2. 检查服务状态

```bash
# 检查服务状态
systemctl status integrate-code

# 检查端口占用
netstat -tlnp | grep 5000

# 检查进程
ps aux | grep app.py
```

### 3. 测试应用响应

```bash
# 测试首页
curl -I http://localhost:5000/

# 测试健康检查端点
curl http://localhost:5000/api/health

# 测试 API
curl http://localhost:5000/kb/auth/check-login
```

### 4. 常见问题

#### 问题 1: Git 拉取失败

```bash
# 检查 Git 配置
cd /opt/integrate-code
git remote -v

# 重新配置远程仓库
git remote set-url origin https://gitee.com/your-username/integrate-code.git

# 拉取测试
git fetch origin
```

#### 问题 2: 依赖安装失败

```bash
# 手动安装依赖
cd /opt/integrate-code
pip install -r requirements.txt

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 问题 3: 应用启动失败

```bash
# 查看错误日志
tail -100 /var/log/integrate-code/app.log

# 手动启动测试
cd /opt/integrate-code
python3 app.py

# 检查环境变量
cat .env
```

---

## 最佳实践

### 1. 版本号管理

在 `config.py` 或 `__init__.py` 中定义版本号：

```python
VERSION = "3.2.0"
```

### 2. 数据库变更

每次数据库变更都需要创建迁移脚本：

```
database/patches/v3.2_to_v3.3/
├── 001_add_user_index.sql
├── 002_update_status_field.sql
└── apply_patches.sh
```

### 3. 部署前检查清单

- [ ] 所有测试通过
- [ ] 代码审核完成
- [ ] 文档已更新
- [ ] 数据库迁移脚本已准备
- [ ] 备份已完成
- [ ] 回滚方案已测试

### 4. 部署时间建议

- **非紧急部署**: 选择业务低峰期（如凌晨）
- **紧急修复**: 可以随时部署，但要确保有回滚方案
- **重大更新**: 提前通知用户，维护窗口

---

## 监控和告警

### 1. 应用监控

```bash
# 创建监控脚本
# scripts/monitor.sh

#!/bin/bash

# 检查应用健康状态
HEALTH_URL="http://localhost:5000/kb/auth/check-login"

if ! curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" | grep -q "200\|401"; then
    echo "应用不健康，发送告警..."
    # 发送邮件或钉钉告警
fi
```

### 2. 日志监控

```bash
# 监控错误日志
tail -f /var/log/integrate-code/app.log | grep --line-buffered ERROR | while read line; do
    echo "检测到错误: $line"
    # 发送告警
done
```

---

## 附录

### A. 完整部署目录结构

```
/opt/integrate-code/
├── app.py                          # 应用入口
├── config.py                       # 配置文件
├── requirements.txt                # Python 依赖
├── .env                            # 环境变量
├── routes/                         # 路由模块
├── common/                         # 公共模块
├── services/                       # 业务逻辑
├── templates/                      # 模板文件
├── static/                         # 静态资源
├── database/                       # 数据库脚本
├── scripts/                        # 脚本
│   ├── deploy.sh                   # 部署脚本 ⭐
│   ├── rollback.sh                 # 回滚脚本 ⭐
│   └── webhook_receiver.py         # Webhook 接收器
└── logs/                           # 日志文件
    ├── app.log                     # 应用日志
    └── deploy.log                  # 部署日志

/var/log/integrate-code/
├── app.log                         # 应用日志
└── error.log                       # 错误日志

/opt/integrate-code/backups/
├── integrate-code_20260302_150000/  # 备份 1
├── integrate-code_20260302_160000/  # 备份 2
└── ...
```

### B. 端口和防火墙

```bash
# 开放防火墙端口
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --permanent --add-port=9000/tcp
firewall-cmd --reload
```

### C. Nginx 配置（可选）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

**文档版本**: v1.0  
**最后更新**: 2026-03-02  
**维护者**: DevOps Team
