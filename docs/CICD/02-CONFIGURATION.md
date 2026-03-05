# CI/CD 配置指南

> 云户科技网站 CI/CD 系统的完整配置说明和使用方法

---

## 📋 目录

1. [GitHub 配置](#github-配置)
   - [仓库信息](#仓库信息)
   - [GitHub Actions 配置](#github-actions-配置)
2. [云主机配置](#云主机配置)
   - [系统要求](#系统要求)
   - [项目目录结构](#项目目录结构)
   - [Git 配置](#git-配置)
   - [服务配置](#服务配置)
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
| `SSH_HOST` | 云主机地址 | ✅ |
| `SSH_USERNAME` | SSH 用户名 | ✅ |
| `SSH_PORT` | SSH 端口（默认22） | ⚪ |
| `SSH_PRIVATE_KEY` | SSH 私钥内容 | ✅ |

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
│   └── smart-pull.sh        # 智能拉取
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
└── error.log              # 错误日志
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

### 部署配置

**环境变量文件**: `.env`

```bash
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

# 重新加载 systemd
sudo systemctl daemon-reload

# 配置防火墙（开放必要端口）
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 5000/tcp  # 应用端口

# 启用防火墙（如果尚未启用）
sudo ufw enable

# 启用并启动服务
sudo systemctl enable --now Home-page

# 验证服务状态
sudo systemctl status Home-page
```

#### 步骤 5：配置 GitHub

1. 在 GitHub 配置 Secrets（见上方说明）
2. 测试 SSH 连接

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

# 查看服务状态
sudo systemctl status Home-page

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
  - [ ] SSH_HOST
  - [ ] SSH_USERNAME
  - [ ] SSH_PORT
  - [ ] SSH_PRIVATE_KEY
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
- [ ] 服务已启用并启动
- [ ] 日志目录已创建
- [ ] Git 代理已配置（如需要）
- [ ] 防火墙规则已设置
  - [ ] 端口 5000（应用）
  - [ ] 端口 22（SSH）

### 功能验证清单

- [ ] 应用可以正常访问
- [ ] 用户注册/登录功能正常
- [ ] 数据库连接正常
- [ ] 文件上传功能正常
- [ ] 部署日志正常记录
- [ ] 日志轮换已配置

---

## 故障排查入口

| 问题类型 | 参考文档 |
|---------|----------|
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
