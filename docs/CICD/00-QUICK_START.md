# CI/CD 快速使用指南

> 快速完成 CI/CD 系统配置的步骤指南

---

## 📋 目录

1. [配置概览](#配置概览)
2. [云主机端配置](#云主机端配置)
3. [GitHub 端配置](#github-端配置)
4. [验证配置](#验证配置)
5. [测试部署](#测试部署)
6. [常见问题](#常见问题)

---

## 配置概览

### CI/CD 架构

```
GitHub Actions → Webhook/SSH → 云主机 → 部署完成
```

### 配置清单

| 配置项 | GitHub 端 | 云主机端 | 状态 |
|--------|-----------|----------|------|
| GitHub Actions Workflow | ✅ | ❌ | ⬜ |
| GitHub Secrets | ✅ | ❌ | ⬜ |
| GitHub Webhook | ✅ | ❌ | ⬜ |
| SSH 访问配置 | ⬜ | ✅ | ⬜ |
| Git 配置 | ❌ | ✅ | ⬜ |
| Webhook 服务 | ❌ | ✅ | ⬜ |
| 应用服务 | ❌ | ✅ | ⬜ |
| 环境变量 | ⬜ | ⬜ | ⬜ |

### 配置顺序

1. **GitHub 端配置**（约 10 分钟）
   - 配置 GitHub Actions Workflow
   - 配置 GitHub Secrets
   - 配置 GitHub Webhook

2. **云主机端配置**（约 20 分钟）
   - 配置 SSH 访问
   - 配置 Git 环境
   - 部署 Webhook 服务
   - 部署应用服务

3. **验证和测试**（约 5 分钟）
   - 测试 SSH 连接
   - 测试 Webhook 连接
   - 测试部署流程

---
## 云主机端配置

### 步骤 1：配置 SSH 访问

**时间**：约 3 分钟

**A. 生成 SSH 密钥对（如果还没有）**

```bash
# 在本地生成 SSH 密钥对
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_key

# 查看生成的密钥
ls -l ~/.ssh/github_actions_key*
```

**B. 将公钥添加到云主机**

```bash
# 复制公钥内容
cat ~/.ssh/github_actions_key.pub

# SSH 登录到云主机
ssh root@cloud-doors.com

# 在云主机上添加公钥到 authorized_keys
echo "[公钥内容]" >> ~/.ssh/authorized_keys

# 设置正确的权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

**C. 测试 SSH 连接**

```bash
# 从本地测试
ssh -i ~/.ssh/github_actions_key root@cloud-doors.com "echo 'SSH 连接成功'"

# 预期输出
# SSH 连接成功
```

---

### 步骤 2：配置 Git 环境

**时间**：约 5 分钟

**A. 配置 Git 全局设置**

```bash
# SSH 登录到云主机
ssh root@cloud-doors.com

# 配置用户信息
git config --global user.name "GitHub Actions"
git config --global user.email "actions@github.com"

# 配置凭证存储
git config --global credential.helper store

# 配置缓冲区（大文件传输）
git config --global http.postBuffer 524288000
git config --global http.maxRequestBuffer 100M

# 配置压缩
git config --global core.compression 9

# 验证配置
git config --global --list
```

**B. 配置 Git 代理（可选，推荐）**

```bash
# 如果需要通过代理访问 GitHub
git config --global http.https://github.proxy http://proxy-server:port

# 验证代理配置
git config --global --get http.https://github.proxy
```

**C. 添加远程仓库**

```bash
# 进入项目目录
cd /opt/Home-page

# 添加 GitHub 远程仓库
git remote add origin https://github.com/liubin20020924-cloud/Home-page.git

# 添加 Gitee 远程仓库（可选，作为后备）
git remote add gitee https://gitee.com/liubin_studies/Home-page.git

# 验证远程仓库
git remote -v
```

**D. 测试 Git 拉取**

```bash
# 拉取最新代码
git fetch origin main

# 查看当前状态
git status
```

---

### 步骤 3：部署 Webhook 服务

**时间**：约 8 分钟

**A. 准备环境**

```bash
# 确保项目目录存在
cd /opt/Home-page

# 激活虚拟环境
source venv/bin/activate

# 安装 Flask 依赖
pip install flask requests python-dotenv

# 退出虚拟环境
deactivate
```

**B. 配置环境变量**

```bash
# 创建 .env 文件
nano /opt/Home-page/.env
```

添加以下内容：
```bash
# Webhook 配置
WEBHOOK_URL=http://cloud-doors.com:9000
WEBHOOK_SECRET=[GitHub 端生成的 WEBHOOK_SECRET 密钥]

# 日志配置
LOG_FILE=/var/log/integrate-code/webhook.log

# 应用配置（根据实际情况填写）
DEBUG=False
SECRET_KEY=your-app-secret-key
DATABASE_URL=your-database-url
```

保存并退出（`Ctrl+X`，然后 `Y`，最后 `Enter`）

**C. 创建 Systemd 服务文件**

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

保存并退出。

**D. 配置防火墙**

```bash
# 开放 Webhook 服务端口
sudo ufw allow 9000/tcp

# 查看防火墙状态
sudo ufw status
```

**E. 启动 Webhook 服务**

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

**F. 验证 Webhook 服务**

```bash
# 测试健康检查端点
curl http://localhost:9000/webhook/health

# 预期返回
# {"status": "healthy", "timestamp": "..."}

# 测试版本查询端点
curl http://localhost:9000/webhook/version

# 查看服务日志
sudo journalctl -u webhook-receiver -n 50
```

---

## GitHub 端配置

### 步骤 1：配置 GitHub Actions Workflow

**时间**：约 2 分钟

**操作步骤**：

1. 确认 Workflow 文件存在：
   ```
   .github/workflows/ci-cd.yml
   ```

2. 检查 Workflow 配置是否正确：

```yaml
name: CI/CD Pipeline

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:

jobs:
  # ... jobs 配置
```

3. 如果文件不存在，创建 Workflow 文件：
   ```bash
   # 在项目根目录创建
   mkdir -p .github/workflows
   nano .github/workflows/ci-cd.yml
   ```

4. 提交并推送：
   ```bash
   git add .github/workflows/ci-cd.yml
   git commit -m "feat: add CI/CD workflow"
   git push origin main
   ```

**验证方法**：
- 访问：`https://github.com/liubin20020924-cloud/Home-page/actions`
- 查看 Actions 是否自动运行

---

### 步骤 2：配置 GitHub Secrets

**时间**：约 5 分钟

**必需的 Secrets**：

| Secret 名称 | 说明 | 示例值 | 必需 |
|-----------|------|---------|------|
| `WEBHOOK_URL` | Webhook 服务地址 | `http://cloud-doors.com:9000` | ✅ |
| `WEBHOOK_SECRET` | Webhook 签名密钥 | `a1b2c3d4e5f6...` | ⚪ |
| `SSH_HOST` | 云主机地址 | `cloud-doors.com` | ✅ |
| `SSH_USERNAME` | SSH 用户名 | `root` 或 `ubuntu` | ✅ |
| `SSH_PORT` | SSH 端口 | `22` | ⚪ |
| `SSH_PRIVATE_KEY` | SSH 私钥 | `-----BEGIN RSA PRIVATE KEY-----...` | ✅ |

**配置步骤**：

1. 进入仓库设置：
   ```
   https://github.com/liubin20020924-cloud/Home-page/settings
   ```

2. 选择：`Secrets and variables` → `Actions`

3. 点击：`New repository secret`

4. 逐个添加 Secret：

   **A. 添加 WEBHOOK_URL**
   - Name: `WEBHOOK_URL`
   - Value: `http://cloud-doors.com:9000`
   - 点击：`Add secret`

   **B. 生成并添加 WEBHOOK_SECRET**
   ```bash
   # 在本地生成密钥
   openssl rand -hex 32
   # 或
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
   - Name: `WEBHOOK_SECRET`
   - Value: [生成的 32 字节密钥]
   - 点击：`Add secret`

   **C. 添加 SSH_HOST**
   - Name: `SSH_HOST`
   - Value: `cloud-doors.com`
   - 点击：`Add secret`

   **D. 添加 SSH_USERNAME**
   - Name: `SSH_USERNAME`
   - Value: `root` 或 `ubuntu`
   - 点击：`Add secret`

   **E. 生成并添加 SSH_PRIVATE_KEY**
   ```bash
   # 生成 SSH 密钥对（如果还没有）
   ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_key

   # 复制私钥内容
   cat ~/.ssh/github_actions_key
   ```
   - Name: `SSH_PRIVATE_KEY`
   - Value: [完整的私钥内容，包括 `-----BEGIN PRIVATE KEY-----` 和 `-----END PRIVATE KEY-----`]
   - 点击：`Add secret`

5. 验证所有 Secrets 已添加：
   - 刷新页面
   - 检查所有必需的 Secrets 是否在列表中

**注意事项**：
- ❌ 不要将 Secrets 写入代码
- ❌ 不要在日志中输出 Secret 值
- ✅ 定期轮换密钥
- ✅ 使用最小权限原则

---

### 步骤 3：配置 GitHub Webhook

**时间**：约 3 分钟

**配置步骤**：

1. 进入仓库设置：
   ```
   https://github.com/liubin20020924-cloud/Home-page/settings/hooks
   ```

2. 点击：`Add webhook`

3. 填写配置：

   **Payload URL**:
   ```
   http://cloud-doors.com:9000/webhook/github
   ```

   **Content type**:
   ```
   application/json
   ```

   **Secret**:
   ```
   [上面生成的 WEBHOOK_SECRET 密钥]
   ```

   **Which events would you like to trigger this webhook?**:
   - 选择：`Push events`
   - 勾选：`Just the push event`
   - Branch: `main`

   **Active**:
   - ✅ 勾选

4. 点击：`Add webhook`

5. 验证配置：
   - 查看页面顶部是否显示绿色勾选
   - 查看 "Recent Deliveries" 是否有最近的推送记录

**验证方法**：
```bash
# 在云主机上测试 Webhook 服务
curl http://cloud-doors.com:9000/webhook/health

# 预期返回
# {"status": "healthy", "timestamp": "..."}
```

---



### 步骤 4：部署应用服务

**时间**：约 5 分钟

**A. 创建 Systemd 服务文件**

```bash
# 创建服务文件
sudo nano /etc/systemd/system/Home-page.service
```

复制以下内容：
```ini
[Unit]
Description=Home Page Application
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/Home-page
Environment="PATH=/opt/Home-page/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/Home-page/venv/bin/python /opt/Home-page/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

保存并退出。

**B. 配置防火墙**

```bash
# 开放应用端口
sudo ufw allow 5000/tcp

# 开放 HTTP/HTTPS 端口（如果使用 Nginx）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

**C. 启动应用服务**

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable Home-page

# 启动服务
sudo systemctl start Home-page

# 查看服务状态
sudo systemctl status Home-page
```

预期输出：
```
● Home-page.service - Home Page Application
   Loaded: loaded (/etc/systemd/system/Home-page.service; enabled; vendor preset: enabled)
   Active: active (running) since ...
```

**D. 验证应用服务**

```bash
# 测试应用是否正常访问
curl http://localhost:5000

# 查看应用日志
sudo journalctl -u Home-page -n 50
```

---

## 验证配置

### 验证清单

| 检查项 | 命令 | 预期结果 |
|--------|------|---------|
| GitHub Actions | 访问 Actions 页面 | ✅ Workflow 列表存在 |
| GitHub Secrets | 访问 Secrets 页面 | ✅ 所有必需 Secrets 已添加 |
| GitHub Webhook | 查看 Webhooks 页面 | ✅ Webhook 已配置，状态正常 |
| SSH 连接 | `ssh -i ~/.ssh/github_actions_key root@cloud-doors.com` | ✅ 成功连接 |
| Git 配置 | `git config --global --list` | ✅ 配置正确 |
| Webhook 服务 | `curl http://cloud-doors.com:9000/webhook/health` | ✅ 返回 healthy |
| 应用服务 | `curl http://cloud-doors.com:5000` | ✅ 应用正常响应 |

### 综合验证命令

```bash
# 1. GitHub 端验证（在浏览器访问）
# https://github.com/liubin20020924-cloud/Home-page/actions
# https://github.com/liubin20020924-cloud/Home-page/settings/secrets/actions
# https://github.com/liubin20020924-cloud/Home-page/settings/hooks

# 2. SSH 连接验证
ssh -i ~/.ssh/github_actions_key root@cloud-doors.com "echo 'SSH OK'"

# 3. 云主机端验证（SSH 登录后执行）
# 检查所有服务状态
sudo systemctl status Home-page webhook-receiver

# 检查防火墙规则
sudo ufw status

# 检查 Git 配置
git config --global --list

# 检查远程仓库
git remote -v

# 4. Webhook 服务验证
curl http://cloud-doors.com:9000/webhook/health

# 5. 应用服务验证
curl http://cloud-doors.com:5000
```

---

## 测试部署

### 测试 1：手动触发部署

**目的**：验证 GitHub Actions 和 SSH 部署是否正常

**步骤**：

1. 在 GitHub 仓库页面：
   - 进入 `Actions` 标签页
   - 选择 `CI/CD Pipeline` workflow
   - 点击 `Run workflow`
   - 选择 `main` 分支
   - 点击：`Run workflow`

2. 观察 Actions 运行：
   - 查看 workflow 是否开始执行
   - 检查每个 job 的执行状态
   - 查看日志输出

3. 检查云主机：
   ```bash
   # SSH 登录
   ssh root@cloud-doors.com

   # 查看最新提交
   cd /opt/Home-page
   git log -1

   # 查看部署日志
   tail -f /var/log/integrate-code/deploy.log
   ```

**预期结果**：
- ✅ GitHub Actions workflow 成功完成
- ✅ 云主机代码已更新
- ✅ 应用服务自动重启
- ✅ 应用正常运行

---

### 测试 2：Push 触发部署

**目的**：验证 Push 事件自动触发部署

**步骤**：

1. 在本地修改代码：
   ```bash
   # 修改任意文件（如 README.md）
   echo "# Test deployment $(date)" >> README.md

   # 提交并推送
   git add README.md
   git commit -m "test: test automatic deployment"
   git push origin main
   ```

2. 观察 GitHub Actions：
   - 自动访问 `Actions` 页面
   - 查看 workflow 是否自动触发
   - 检查执行状态

3. 检查 Webhook 触发：
   - 访问 GitHub Webhooks 页面
   - 查看 `Recent Deliveries`
   - 确认最新的推送已触发

4. 验证部署：
   ```bash
   # SSH 登录云主机
   ssh root@cloud-doors.com

   # 查看最新提交
   cd /opt/Home-page
   git log -1

   # 验证文件已更新
   tail -5 README.md
   ```

**预期结果**：
- ✅ Push 自动触发 GitHub Actions
- ✅ Webhook 成功触发
- ✅ 代码自动更新到云主机
- ✅ 应用正常运行

---

### 测试 3：Webhook 直接触发

**目的**：验证 Webhook 服务是否能独立接收触发

**步骤**：

1. 模拟 GitHub Webhook 请求：
   ```bash
   # 在本地或云主机上执行
   WEBHOOK_SECRET="[GitHub 中的密钥]"
   PAYLOAD='{"ref":"refs/heads/main"}'
   SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" | awk '{print $2}')

   curl -X POST http://cloud-doors.com:9000/webhook/github \
     -H "Content-Type: application/json" \
     -H "X-Hub-Signature-256: sha256=$SIGNATURE" \
     -d "$PAYLOAD"
   ```

2. 观察 Webhook 日志：
   ```bash
   ssh root@cloud-doors.com
   sudo journalctl -u webhook-receiver -f
   ```

3. 观察部署日志：
   ```bash
   tail -f /var/log/integrate-code/deploy.log
   ```

**预期结果**：
- ✅ Webhook 请求成功接收（HTTP 200）
- ✅ 部署脚本自动执行
- ✅ 代码更新完成
- ✅ 应用服务重启

---

## 常见问题

### 问题 1：GitHub Actions 失败

**错误信息**：
```
Error: Permission denied (publickey)
```

**原因**：SSH 密钥配置不正确

**解决方案**：
1. 检查 GitHub Secret `SSH_PRIVATE_KEY` 是否正确
2. 确保私钥格式完整，包含 `-----BEGIN PRIVATE KEY-----` 和 `-----END PRIVATE KEY-----`
3. 确保云主机的 `authorized_keys` 包含对应的公钥
4. 测试 SSH 连接：
   ```bash
   ssh -i ~/.ssh/github_actions_key root@cloud-doors.com
   ```

---

### 问题 2：Webhook 不触发

**错误信息**：
```
Webhook delivery failed
```

**原因**：Webhook URL 或密钥配置错误

**解决方案**：
1. 检查 GitHub Webhook URL 是否正确：
   ```
   http://cloud-doors.com:9000/webhook/github
   ```

2. 检查云主机防火墙是否开放 9000 端口：
   ```bash
   sudo ufw status
   sudo ufw allow 9000/tcp
   ```

3. 检查 Webhook 服务是否运行：
   ```bash
   sudo systemctl status webhook-receiver
   ```

4. 检查 Webhook 密钥是否一致：
   ```bash
   # GitHub 端
   # 记录在 Secrets 中的 WEBHOOK_SECRET

   # 云主机端
   cat /opt/Home-page/.env | grep WEBHOOK_SECRET
   ```

5. 测试 Webhook 服务：
   ```bash
   curl http://cloud-doors.com:9000/webhook/health
   ```

---

### 问题 3：部署失败

**错误信息**：
```
Deploy failed: script error
```

**原因**：部署脚本执行失败

**解决方案**：
1. 查看部署日志：
   ```bash
   ssh root@cloud-doors.com
   tail -50 /var/log/integrate-code/deploy.log
   ```

2. 手动执行部署脚本：
   ```bash
   cd /opt/Home-page
   bash scripts/deploy.sh
   ```

3. 检查文件权限：
   ```bash
   chmod +x /opt/Home-page/scripts/*.sh
   ```

4. 检查虚拟环境：
   ```bash
   source /opt/Home-page/venv/bin/activate
   python --version
   ```

---

### 问题 4：应用无法访问

**错误信息**：
```
Connection refused
```

**原因**：应用服务未运行或防火墙阻止

**解决方案**：
1. 检查服务状态：
   ```bash
   sudo systemctl status Home-page
   ```

2. 检查端口监听：
   ```bash
   sudo netstat -tlnp | grep 5000
   ```

3. 检查防火墙：
   ```bash
   sudo ufw status
   sudo ufw allow 5000/tcp
   ```

4. 重启服务：
   ```bash
   sudo systemctl restart Home-page
   ```

---

## 相关文档

- [CI/CD 完整介绍](./01-INTRODUCTION.md) - 了解 CI/CD 系统架构和概念
- [CI/CD 配置指南](./02-CONFIGURATION.md) - 详细的配置说明
- [CI/CD 部署历史](./03-DEPLOYMENT_HISTORY.md) - 部署过程记录
- [CI/CD 功能设计](./04-FEATURES.md) - 功能设计和实现细节
- [CI/CD 故障排除](./05-TROUBLESHOOTING.md) - 完整的故障排除指南
- [CI/CD 测试指南](./06-TESTING.md) - 详细的测试步骤
- [脚本使用说明](../SCRIPTS.md) - 所有脚本的功能说明

---

<div align="center">

**文档版本**: v1.0
**创建日期**: 2026-03-04
**维护者**: 云户科技技术团队

</div>
