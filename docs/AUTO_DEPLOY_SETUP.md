# 云主机自动部署配置指南

> 本文档指导您完成云主机自动部署的完整配置

---

## 📋 目录

1. [配置概述](#配置概述)
2. [GitHub 配置](#github-配置)
3. [Gitee 配置](#gitee-配置)
4. [云主机配置](#云主机配置)
5. [测试流程](#测试流程)
6. [常见问题](#常见问题)

---

## 配置概述

### 完整流程图

```
本地开发 → GitHub → GitHub Action → Gitee → 云主机检测 → 自动部署
   ↓         ↓           ↓            ↓            ↓
  提交    main分支     自动同步      定时检查    拉取+重启
```

### 自动化组件

| 组件 | 说明 |
|------|------|
| GitHub Action | 自动同步代码到 Gitee |
| Gitee | 代码托管镜像 |
| 云主机定时任务 | 每5分钟检测 Gitee 更新 |
| Webhook 接收器 | 接收部署请求 |
| 部署脚本 | 拉取代码并重启应用 |

---

## GitHub 配置

### 1. 生成 SSH 密钥

```bash
# 生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "github-action" -f ~/.ssh/github_gitee_rsa

# 复制私钥内容（配置到 GitHub Secrets）
cat ~/.ssh/github_gitee_rsa

# 复制公钥内容（配置到 Gitee）
cat ~/.ssh/github_gitee_rsa.pub
```

### 2. 配置 Gitee SSH 公钥

1. 登录 Gitee
2. 进入 **设置** → **SSH 公钥**
3. 点击 **添加公钥**
4. 粘贴公钥内容 (`~/.ssh/github_gitee_rsa.pub`)
5. 点击 **确定**

### 3. 配置 GitHub Secrets

1. 进入 GitHub 仓库
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**

添加以下 Secrets：

| Secret Name | 说明 | 示例值 |
|-------------|------|--------|
| `SSH_PRIVATE_KEY` | SSH 私钥内容 | 私钥完整内容（包括 BEGIN 和 END 行） |
| `GITEE_REPO` | Gitee 仓库路径 | `liubin_studies/Home-page` |

**SSH_PRIVATE_KEY 格式**:

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtc...
...
-----END OPENSSH PRIVATE KEY-----
```

### 4. 验证 GitHub Actions

1. 推送代码到 GitHub main 分支
2. 进入 **Actions** 标签
3. 查看 "Sync to Gitee" 或 "CI/CD Pipeline" 工作流
4. 确认工作流成功执行

---

## Gitee 配置

### 1. 配置 Gitee Webhook（可选）

如果使用 Webhook 触发部署（而非定时检测）：

1. 进入 Gitee 仓库
2. 进入 **管理** → **WebHooks**
3. 点击 **添加 WebHook**

**WebHook 配置**:

| 配置项 | 值 |
|--------|-----|
| URL | `http://your-server-ip:9000/webhook/gitee` |
| 密码 | `your-webhook-secret-here` |
| 推送事件 | ✅ 推送事件 |

### 2. 验证 Webhook

```bash
# 在云主机上测试 Webhook
curl -X POST http://localhost:9000/webhook/gitee \
  -H "X-Gitee-Token: your-webhook-secret" \
  -H "Content-Type: application/json" \
  -d '{"ref": "refs/heads/main"}'
```

预期响应：
```json
{
  "message": "Deployment started"
}
```

---

## 云主机配置

### 1. 准备工作

#### 1.1 登录云主机

```bash
ssh root@your-server-ip
```

#### 1.2 克隆代码

```bash
# 创建项目目录
mkdir -p /opt/integrate-code
cd /opt/integrate-code

# 从 Gitee 克隆代码
git clone https://gitee.com/your-username/integrate-code.git
cd integrate-code
```

#### 1.3 安装依赖

```bash
# 安装 Python 依赖
pip3 install -r requirements.txt

# 安装 webhook 接收器依赖
pip3 install flask
```

#### 1.4 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

### 2. 配置自动部署服务

#### 2.1 修改密钥配置

```bash
# 修改 webhook 接收器密钥
nano scripts/webhook_receiver.py

# 修改以下行：
WEBHOOK_SECRET = 'your-webhook-secret-here'  # 改为实际密钥
```

```bash
# 修改自动检测脚本密钥
nano scripts/check_and_deploy.sh

# 修改以下行：
WEBHOOK_SECRET="your-webhook-secret-here"  # 改为实际密钥
```

#### 2.2 安装部署服务

```bash
# 运行服务安装脚本
bash scripts/deploy_service.sh
```

安装脚本会自动完成以下操作：
- 创建必要目录
- 设置脚本权限
- 创建 systemd 服务
- 配置定时任务（每5分钟）
- 配置防火墙
- 启动服务

### 3. 配置 systemd 服务

#### 3.1 主应用服务

**服务文件**: `/etc/systemd/system/integrate-code.service`

```ini
[Unit]
Description=CloudDoors Website - Integrate Code
After=network.target mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/integrate-code
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /opt/integrate-code/app.py
Restart=always
RestartSec=10

# 日志
StandardOutput=append:/var/log/integrate-code/app.log
StandardError=append:/var/log/integrate-code/error.log

[Install]
WantedBy=multi-user.target
```

#### 3.2 Webhook 接收器服务

**服务文件**: `/etc/systemd/system/webhook-receiver.service`

```ini
[Unit]
Description=CloudDoors Webhook Receiver
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/integrate-code
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="WEBHOOK_SECRET=your-webhook-secret-here"
ExecStart=/usr/bin/python3 /opt/integrate-code/scripts/webhook_receiver.py
Restart=always
RestartSec=10

# 日志
StandardOutput=append:/var/log/integrate-code/webhook.log
StandardError=append:/var/log/integrate-code/webhook-error.log

[Install]
WantedBy=multi-user.target
```

#### 3.3 启动服务

```bash
# 重新加载 systemd
systemctl daemon-reload

# 启用主应用服务
systemctl enable integrate-code
systemctl start integrate-code

# 启用 webhook 接收器服务
systemctl enable webhook-receiver
systemctl start webhook-receiver

# 查看服务状态
systemctl status integrate-code
systemctl status webhook-receiver
```

### 4. 配置防火墙

```bash
# 开放应用端口
firewall-cmd --permanent --add-port=5000/tcp

# 开放 Webhook 端口
firewall-cmd --permanent --add-port=9000/tcp

# 重新加载防火墙
firewall-cmd --reload
```

---

## 测试流程

### 1. 测试 Webhook 接收器

```bash
# 测试健康检查端点
curl http://localhost:9000/webhook/health

# 预期响应：
# {
#   "status": "ok",
#   "message": "Webhook service is running"
# }

# 测试 Webhook 触发
curl -X POST http://localhost:9000/webhook/gitee \
  -H "X-Gitee-Token: your-webhook-secret" \
  -H "Content-Type: application/json" \
  -d '{"ref": "refs/heads/main"}'
```

### 2. 测试自动检测脚本

```bash
# 手动运行检测脚本
cd /opt/integrate-code
bash scripts/check_and_deploy.sh

# 查看日志
tail -f /var/log/integrate-code/auto-deploy.log
```

### 3. 测试完整部署流程

```bash
# 1. 在本地提交代码
git add .
git commit -m "feat: 测试自动部署"
git push origin main

# 2. 在 GitHub 查看 Actions
#   - 确认 "Sync to Gitee" 工作流成功

# 3. 等待 5 分钟（或手动触发检测）
cd /opt/integrate-code
bash scripts/check_and_deploy.sh

# 4. 查看部署日志
tail -f /var/log/integrate-code/deploy.log

# 5. 查看应用状态
systemctl status integrate-code
```

---

## 常见问题

### Q1: Webhook 服务无法启动

**检查步骤**:

```bash
# 查看服务状态
systemctl status webhook-receiver

# 查看错误日志
journalctl -u webhook-receiver -n 50

# 查看应用日志
tail -f /var/log/integrate-code/webhook-error.log
```

**可能原因**:
- 端口 9000 被占用
- Python 环境问题
- 脚本权限问题

**解决方案**:
```bash
# 检查端口占用
netstat -tlnp | grep 9000

# 停止占用进程
pkill -f webhook_receiver

# 检查 Python 环境
which python3
python3 --version

# 重新设置权限
chmod +x /opt/integrate-code/scripts/*.sh
chmod +x /opt/integrate-code/scripts/*.py
```

### Q2: GitHub Action 同步失败

**检查步骤**:

1. 进入 GitHub 仓库 → Actions → 查看失败的工作流
2. 点击失败的 job 查看详细日志

**可能原因**:
- SSH 私钥配置错误
- Gitee 仓库路径错误
- 网络连接问题

**解决方案**:
```bash
# 重新生成 SSH 密钥
ssh-keygen -t rsa -b 4096 -C "github-action" -f ~/.ssh/github_gitee_rsa

# 测试 SSH 连接
ssh -i ~/.ssh/github_gitee_rsa git@gitee.com

# 确认 Gitee 仓库路径
# 格式：your-username/integrate-code
```

### Q3: 云主机无法检测到更新

**检查步骤**:

```bash
# 查看自动检测日志
tail -f /var/log/integrate-code/auto-deploy.log

# 检查定时任务
crontab -l | grep check_and_deploy

# 手动运行检测脚本
bash /opt/integrate-code/scripts/check_and_deploy.sh
```

**可能原因**:
- Git 配置错误
- 密钥配置错误
- 网络连接问题

**解决方案**:
```bash
# 检查 Git 配置
cd /opt/integrate-code
git remote -v

# 测试 Git 拉取
git fetch origin main

# 检查密钥配置
grep WEBHOOK_SECRET scripts/check_and_deploy.sh
```

### Q4: 部署失败后应用无法启动

**检查步骤**:

```bash
# 查看部署日志
tail -f /var/log/integrate-code/deploy.log

# 查看应用日志
tail -f /var/log/integrate-code/app.log

# 手动启动测试
cd /opt/integrate-code
python3 app.py
```

**回滚方案**:

```bash
# 查看可用备份
ls -lh /opt/integrate-code/backups/

# 使用回滚脚本
bash /opt/integrate-code/scripts/rollback.sh
```

---

## 监控和维护

### 查看服务状态

```bash
# 查看所有相关服务
systemctl status integrate-code webhook-receiver

# 实时查看服务日志
journalctl -u integrate-code -f
journalctl -u webhook-receiver -f
```

### 查看部署日志

```bash
# 部署日志
tail -f /var/log/integrate-code/deploy.log

# 应用日志
tail -f /var/log/integrate-code/app.log

# Webhook 日志
tail -f /var/log/integrate-code/webhook.log

# 自动检测日志
tail -f /var/log/integrate-code/auto-deploy.log
```

### 备份管理

```bash
# 查看备份列表
ls -lh /opt/integrate-code/backups/

# 手动创建备份
cp -r /opt/integrate-code /opt/integrate-code/backups/manual_backup_$(date +%Y%m%d_%H%M%S)

# 清理旧备份（保留最近 5 个）
cd /opt/integrate-code/backups
ls -t | tail -n +6 | xargs rm -rf
```

---

## 附录

### A. 端口列表

| 端口 | 服务 | 说明 |
|------|------|------|
| 5000 | Flask 应用 | 主应用服务 |
| 9000 | Webhook 接收器 | 部署触发服务 |

### B. 目录结构

```
/opt/integrate-code/
├── app.py
├── config.py
├── .env
├── routes/
├── common/
├── services/
├── scripts/
│   ├── deploy.sh
│   ├── rollback.sh
│   ├── check_and_deploy.sh
│   ├── webhook_receiver.py
│   └── deploy_service.sh
└── logs/

/var/log/integrate-code/
├── app.log
├── error.log
├── deploy.log
├── webhook.log
└── auto-deploy.log
```

### C. 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 操作系统 | CentOS 7+ / Ubuntu 18.04+ | CentOS 8 / Ubuntu 20.04 |
| Python | 3.8 | 3.9+ |
| 内存 | 512MB | 1GB+ |
| 磁盘 | 10GB | 20GB+ |
| CPU | 1 核 | 2 核+ |

---

**文档版本**: v1.0  
**最后更新**: 2026-03-04  
**维护者**: DevOps Team
