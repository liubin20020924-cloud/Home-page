# CI/CD 配置指南

> 云户科技网站 CI/CD 系统的完整配置说明和使用方法

---

## 📋 目录

1. [GitHub 配置](#github-配置)
   - [仓库信息](#仓库信息)
   - [GitHub Actions 配置](#github-actions-配置)
   - [Webhook 配置](#webhook-配置)
     - [生成 Webhook 密钥](#生成-webhook-密钥)
     - [GitHub Webhook 配置](#github-webhook-配置主要方式)
2. [云主机配置](#云主机配置)
   - [系统要求](#系统要求)
   - [项目目录结构](#项目目录结构)
   - [Git 配置](#git-配置)
   - [服务配置](#服务配置)
     - [Webhook 服务](#webhook-服务)
       - [部署 Webhook 服务](#部署-webhook-服务)
     - [应用服务](#应用服务)
3. [环境变量](#环境变量)
4. [快速开始](#快速开始)
5. [日常运维](#日常运维)
6. [配置清单](#配置清单)

---

## GitHub 配置

### 仓库信息

| 项目 | 信息 |
|------|------|
| 仓库地址 | https://github.com/liubin20020924-cloud/Home-page.git |
| 生产分支 | main |
| 开发分支 | develop（可选） |
| 功能分支前缀 | feat/, fix/, hotfix/ |

### GitHub Actions 配置

#### 主要 Workflow 文件

**文件**: `.github/workflows/ci-cd.yml`

**触发条件：**
```yaml
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:
```

**必需的 Secrets：**

| Secret 名称 | 说明 | 必需 |
|-----------|------|--------|
| `WEBHOOK_URL` | 云主机 Webhook 地址 | ✅ |
| `SSH_HOST` | 云主机地址 | ✅ |
| `SSH_USERNAME` | SSH 用户名 | ✅ |
| `SSH_PORT` | SSH 端口（默认22） | ⚪ |
| `SSH_PRIVATE_KEY` | SSH 私钥内容 | ✅ |
| `WEBHOOK_SECRET` | Webhook 签名密钥 | ⚪ |

#### Secrets 配置步骤

1. 进入仓库设置：`https://github.com/liubin20020924-cloud/Home-page/settings`
2. 选择：`Secrets and variables` → `Actions`
3. 点击：`New repository secret`
4. 填写：
   - Name: Secret 名称
   - Value: Secret 值
5. 点击：`Add secret`

**注意事项：**
- ❌ 不要将 Secrets 写入代码
- ❌ 不要在日志中输出 Secret 值
- ✅ 定期轮换密钥和 Token
- ✅ 使用最小权限原则

### Webhook 配置

#### 生成 Webhook 密钥

在配置 Webhook 之前，需要先生成一个安全的密钥。

**方法 1：使用脚本自动生成**
```bash
# 在项目根目录运行
python3 scripts/generate-webhook-secret.py
```

**方法 2：手动生成**
```bash
# 生成 32 字节的随机密钥
openssl rand -hex 32

# 或使用 Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**保存密钥：**
```bash
# 将生成的密钥保存到 .env 文件
echo "WEBHOOK_SECRET=your-generated-secret-here" >> /opt/Home-page/.env
```

#### GitHub Webhook 配置（主要方式）

**配置步骤：**

1. 进入 GitHub 仓库设置 → `Webhooks` → `Add webhook`
2. 填写配置：
   ```
   Payload URL: http://cloud-doors.com:9000/webhook/github
   Content type: application/json
   Secret: [上面生成的密钥]
   Which events would you like to trigger this webhook?
   - 选择 "Push events" → "Just the push event"
   Active: ✅ 勾选
   ```
3. 点击：`Add webhook`

**配置说明：**
- **Payload URL**: 云主机 Webhook 接收器地址
- **Content type**: 必须为 `application/json`
- **Secret**: 用于验证 Webhook 请求的密钥，必须与云主机 `.env` 中的 `WEBHOOK_SECRET` 一致
- **Events**: 只触发 `main` 分支的 push 事件

**在 GitHub Actions 中配置 Secret：**

将生成的 Webhook 密钥添加到 GitHub Secrets，供 Actions 使用：

1. 进入仓库设置 → `Secrets and variables` → `Actions`
2. 点击：`New repository secret`
3. 填写：
   - Name: `WEBHOOK_SECRET`
   - Value: [上面生成的密钥]
4. 点击：`Add secret`

**验证方法：**
```bash
# 1. 查看 Webhook 交付日志
# GitHub 仓库 → Settings → Webhooks → 查看最近交付

# 2. 在云主机测试 Webhook 服务
curl http://cloud-doors.com:9000/webhook/health

# 预期返回：{"status": "healthy", "timestamp": "..."}

# 3. 查看当前版本
curl http://cloud-doors.com:9000/webhook/version

# 4. 查看 Webhook 日志
sudo journalctl -u webhook-receiver -f
```

**故障排查：**
```bash
# 如果 Webhook 不触发，检查：
# 1. GitHub Webhook 交付日志是否显示错误
# 2. 云主机防火墙是否开放 9000 端口
sudo ufw allow 9000

# 3. Webhook 服务是否运行
sudo systemctl status webhook-receiver

# 4. 密钥是否正确
grep WEBHOOK_SECRET /opt/Home-page/.env
```

**测试 Webhook 连接：**
```bash
# 模拟 GitHub Webhook 请求（需要有效的签名）
WEBHOOK_SECRET="your-secret-here"
PAYLOAD='{"ref":"refs/heads/main"}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" | awk '{print $2}')

curl -X POST http://cloud-doors.com:9000/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=$SIGNATURE" \
  -d "$PAYLOAD"
```

---

## 云主机配置

### 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 操作系统 | Ubuntu 20.04+ | Ubuntu 22.04 LTS |
| Python | 3.8+ | 3.10+ |
| 内存 | 1GB | 2GB+ |
| 磁盘 | 10GB | 20GB+ |
| CPU | 1核 | 2核+ |

### 项目目录结构

```
/opt/Home-page/
├── app.py                    # 应用主程序
├── config.py                 # 配置文件
├── requirements.txt          # Python 依赖
├── routes/                  # 路由模块
├── services/                # 服务模块
├── templates/               # 模板文件
├── static/                  # 静态资源
├── database/               # 数据库文件
├── scripts/                 # 部署脚本
│   ├── deploy.sh            # 主部署脚本
│   ├── rollback.sh          # 回滚脚本
│   ├── smart-pull.sh        # 智能拉取
│   └── webhook_receiver_github.py
├── tests/                   # 测试文件
└── logs/                    # 日志目录
```

### Git 配置

#### 本地开发环境

```bash
# 配置用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 配置推送策略
git config --global push.default simple

# 启用凭证存储
git config --global credential.helper store
```

#### 云主机环境

```bash
# 配置 Git 代理（如果需要）
git config --global http.https://github.com.proxy http://proxy-server:port

# 验证配置
git config --global --get http.https://github.com.proxy

# 测试连接
git fetch --dry-run origin
```

### 服务配置

#### Webhook 服务

#### 部署 Webhook 服务

**前提条件：**
- ✅ 已完成 Git 配置（见上文）
- ✅ 已生成并配置 `WEBHOOK_SECRET` 到 `.env` 文件
- ✅ 已安装 Python 3 和相关依赖
- ✅ 已配置 GitHub Webhook（见上文）

**部署步骤：**

**步骤 1：准备环境**

```bash
# 确保项目目录存在
cd /opt/Home-page

# 确保虚拟环境存在
source venv/bin/activate

# 安装 Flask 依赖
pip install flask requests python-dotenv

# 退出虚拟环境
deactivate
```

**步骤 2：配置环境变量**

```bash
# 编辑 .env 文件
nano /opt/Home-page/.env
```

添加以下内容：
```bash
# Webhook 配置
WEBHOOK_URL=http://cloud-doors.com:9000
WEBHOOK_SECRET=your-generated-secret-here

# 日志配置
LOG_FILE=/var/log/integrate-code/webhook.log
```

**步骤 3：创建 Systemd 服务文件**

```bash
# 创建服务文件
sudo nano /etc/systemd/system/webhook-receiver.service
```

复制以下内容：
```ini
[Unit]
Description=Webhook Receiver Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/Home-page
Environment="PATH=/opt/Home-page/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /opt/Home-page/scripts/webhook_receiver_github.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

保存并退出（`Ctrl+X`，然后 `Y`，最后 `Enter`）

**步骤 4：配置防火墙**

```bash
# 开放 9000 端口（Webhook 服务端口）
sudo ufw allow 9000/tcp

# 查看防火墙状态
sudo ufw status
```

**步骤 5：启动 Webhook 服务**

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable webhook-receiver

# 启动服务
sudo systemctl start webhook-receiver

# 查看服务状态
sudo systemctl status webhook-receiver
```

预期输出：
```
● webhook-receiver.service - Webhook Receiver Service
   Loaded: loaded (/etc/systemd/system/webhook-receiver.service; enabled; vendor preset: enabled)
   Active: active (running) since ...
```

**步骤 6：验证 Webhook 服务**

```bash
# 1. 测试健康检查端点
curl http://localhost:9000/webhook/health

# 预期返回：{"status": "healthy", "timestamp": "..."}

# 2. 测试版本查询端点
curl http://localhost:9000/webhook/version

# 3. 查看服务日志
sudo journalctl -u webhook-receiver -n 50
```

**步骤 7：从外部测试（可选）**

```bash
# 从本地或另一台机器测试
curl http://cloud-doors.com:9000/webhook/health

# 如果返回 403，检查防火墙配置
# 如果返回 Connection refused，检查服务是否启动
```

**步骤 8：配置 Nginx 反向代理（可选，推荐）**

如果需要使用 HTTPS 或域名访问，建议配置 Nginx 反向代理：

```bash
# 创建 Nginx 配置文件
sudo nano /etc/nginx/sites-available/webhook
```

配置内容：
```nginx
server {
    listen 80;
    server_name cloud-doors.com;

    location /webhook/ {
        proxy_pass http://127.0.0.1:9000/webhook/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # GitHub Webhook 需要
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

启用配置：
```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/webhook /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

**Systemd 服务文件**: `/etc/systemd/system/webhook-receiver.service`

```ini
[Unit]
Description=Webhook Receiver Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/Home-page
Environment="PATH=/opt/Home-page/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /opt/Home-page/scripts/webhook_receiver_github.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**管理命令：**
```bash
# 启用服务
sudo systemctl enable webhook-receiver

# 启动服务
sudo systemctl start webhook-receiver

# 停止服务
sudo systemctl stop webhook-receiver

# 重启服务
sudo systemctl restart webhook-receiver

# 查看状态
sudo systemctl status webhook-receiver

# 查看日志
sudo journalctl -u webhook-receiver -f
```

#### 应用服务

**Systemd 服务文件**: `/etc/systemd/system/Home-page.service`

```ini
[Unit]
Description=Home-page Application
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/Home-page
Environment="PATH=/opt/Home-page/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /opt/Home-page/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**管理命令：**
```bash
# 启用服务
sudo systemctl enable Home-page

# 启动服务
sudo systemctl start Home-page

# 停止服务
sudo systemctl stop Home-page

# 重启服务
sudo systemctl restart Home-page

# 查看状态
sudo systemctl status Home-page

# 查看日志
sudo journalctl -u Home-page -f
```

### 日志配置

**日志目录结构：**
```
/var/log/Home-page/
├── deploy.log              # 部署日志
├── app.log                 # 应用日志
├── error.log              # 错误日志
└── webhook.log            # Webhook 日志
```

**日志轮换配置：**
```bash
# 创建 logrotate 配置文件
sudo nano /etc/logrotate.d/Home-page

# 配置内容：
/var/log/Home-page/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
}
```

---

## 环境变量

### 应用配置

**文件**: `config.py`

```python
class Config:
    # 应用配置
    DEBUG = False
    SECRET_KEY = 'your-secret-key-here'
    
    # 数据库配置
    DB_HOST = 'localhost'
    DB_USER = 'home-page'
    DB_PASSWORD = 'your-db-password'
    DB_NAME = 'home-page'
    
    # 邮件配置
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'noreply@example.com'
    MAIL_PASSWORD = 'your-mail-password'
    MAIL_DEFAULT_SENDER = 'noreply@example.com'
    
    # 文件上传配置
    UPLOAD_FOLDER = '/opt/Home-page/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### Webhook 配置

**环境变量文件**: `.env`

```bash
# Webhook 服务配置
WEBHOOK_URL=http://cloud-doors.com:9000
WEBHOOK_SECRET=your-webhook-secret-here
FLASK_ENV=production
LOG_LEVEL=INFO

# 部署配置
PROJECT_DIR=/opt/Home-page
BACKUP_DIR=/var/backups/Home-page
LOG_FILE=/var/log/Home-page/deploy.log
APP_NAME=Home-page
SERVICE_NAME=Home-page
```

---

## 快速开始

### 首次部署步骤

#### 步骤 1：克隆代码到云主机

```bash
# SSH 登录
ssh user@cloud-doors.com

# 克隆仓库
cd /opt
git clone https://github.com/liubin20020924-cloud/Home-page.git

# 进入项目目录
cd Home-page

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 步骤 2：配置环境

```bash
# 复制配置模板
cp config.example.py config.py

# 编辑配置文件
nano config.py

# 创建环境变量文件
nano .env

# 生成 Webhook 密钥
python3 scripts/generate-webhook-secret.py

# 将生成的密钥添加到 .env
echo "WEBHOOK_SECRET=your-generated-secret-here" >> .env

# 设置文件权限
chmod 600 config.py .env
```

#### 步骤 3：初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS home-page;"

# 初始化表结构
bash init_db.sh

# 导入初始数据（如果需要）
mysql home-page < database/init_data.sql
```

#### 步骤 4：配置服务

```bash
# 创建 systemd 服务文件
sudo cp scripts/Home-page.service /etc/systemd/system/

# 创建 webhook 服务
sudo cp scripts/webhook-receiver.service /etc/systemd/system/

# 重新加载 systemd
sudo systemctl daemon-reload

# 配置防火墙（开放必要端口）
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 5000/tcp  # 应用端口
sudo ufw allow 9000/tcp  # Webhook 端口

# 启用防火墙（如果尚未启用）
sudo ufw enable

# 启用并启动服务
sudo systemctl enable --now Home-page
sudo systemctl enable --now webhook-receiver

# 验证服务状态
sudo systemctl status Home-page webhook-receiver
```

#### 步骤 5：配置 GitHub

1. 在 GitHub 配置 Secrets（见上方说明）
2. 配置 Webhook（见上方说明）
3. 测试 Webhook 连接

```bash
# 在云主机测试
curl http://localhost:9000/webhook/health

# 应返回：
# {"status": "healthy", "version": "x.x.x"}
```

---

## 日常运维

### 常用命令

#### 部署相关

```bash
# 手动触发部署
cd /opt/Home-page
./scripts/deploy.sh

# 查看部署日志
tail -f /var/log/Home-page/deploy.log

# 回滚到指定版本
./scripts/rollback.sh Home-page_20260304_120000
```

#### 服务管理

```bash
# 重启应用服务
sudo systemctl restart Home-page

# 重启 webhook 服务
sudo systemctl restart webhook-receiver

# 查看服务状态
sudo systemctl status Home-page webhook-receiver

# 查看所有服务
systemctl list-units --type=service --state=running
```

#### 日志查看

```bash
# 查看应用日志
tail -f /var/log/Home-page/app.log

# 查看错误日志
tail -f /var/log/Home-page/error.log

# 查看部署日志
tail -f /var/log/Home-page/deploy.log

# 查看系统日志
journalctl -u Home-page -f
```

### 健康检查

```bash
# 应用健康检查
curl http://localhost:5000/health

# Webhook 健康检查
curl http://localhost:9000/webhook/health

# 查询当前版本
curl http://localhost:9000/webhook/version
```

### 备份管理

```bash
# 列出所有备份
ls -lh /var/backups/Home-page/

# 手动创建备份
./scripts/deploy.sh backup

# 删除过期备份
find /var/backups/Home-page/ -mtime +7 -exec rm -rf {} \;
```

---

## 配置清单

### GitHub 配置清单

- [ ] 仓库已创建
- [ ] Secrets 已配置
  - [ ] WEBHOOK_URL
  - [ ] SSH_HOST
  - [ ] SSH_USERNAME
  - [ ] SSH_PORT
  - [ ] SSH_PRIVATE_KEY
  - [ ] WEBHOOK_SECRET（可选）
- [ ] Webhook 已配置
- [ ] CI/CD workflow 已创建
- [ ] 提交规范已配置（`.commitlintrc.yml`）

### 云主机配置清单

- [ ] Python 3.10+ 已安装
- [ ] 虚拟环境已创建
- [ ] 依赖已安装（`pip install -r requirements.txt`）
- [ ] 数据库已初始化
- [ ] 配置文件已创建（`config.py`）
- [ ] 环境变量已设置（`.env`）
- [ ] systemd 服务已配置
  - [ ] Home-page.service
  - [ ] webhook-receiver.service
- [ ] 服务已启用并启动
- [ ] 日志目录已创建
- [ ] Git 代理已配置（如需要）
- [ ] 防火墙规则已设置
  - [ ] 端口 5000（应用）
  - [ ] 端口 9000（Webhook）
  - [ ] 端口 22（SSH）

### 功能验证清单

- [ ] 应用可以正常访问
- [ ] 用户注册/登录功能正常
- [ ] 数据库连接正常
- [ ] 文件上传功能正常
- [ ] Webhook 健康检查通过
- [ ] 部署日志正常记录
- [ ] 日志轮换已配置

---

## 故障排查入口

| 问题类型 | 参考文档 |
|---------|----------|
| Webhook 不触发 | [故障排除指南](./05-TROUBLESHOOTING.md) |
| 部署失败 | [故障排除指南](./05-TROUBLESHOOTING.md) |
| 服务启动失败 | [故障排除指南](./05-TROUBLESHOOTING.md) |
| Git 拉取失败 | [CI/CD 介绍](./01-INTRODUCTION.md) |
| CI/CD 检查失败 | [测试指南](./06-TESTING.md) |

---

<div align="center">

**文档版本**: v1.0  
**创建日期**: 2026-03-04  
**维护者**: 云户科技技术团队

</div>
