# 快速部署设置指南

> 本文档帮助你在云主机上快速设置自动化部署

---

## 📋 前提条件

- ✅ 云主机已安装 Python 3.8+
- ✅ 云主机已安装 Git
- ✅ 云主机已安装 MySQL/MariaDB
- ✅ Gitee 仓库已创建
- ✅ GitHub 仓库已创建

---

## 🚀 快速部署步骤

### 第一步：在云主机上准备环境

```bash
# 1. 登录云主机
ssh root@your-server-ip

# 2. 创建部署目录
mkdir -p /opt/integrate-code
mkdir -p /opt/integrate-code/backups
mkdir -p /var/log/integrate-code

# 3. 克隆 Gitee 仓库
cd /opt/integrate-code
git clone https://gitee.com/your-username/integrate-code.git
cd integrate-code

# 4. 安装 Python 依赖
pip3 install -r requirements.txt

# 5. 复制环境变量模板
cp .env.example .env

# 6. 编辑环境变量（根据实际情况修改）
nano .env

# 7. 初始化数据库（如果需要）
bash init_db.sh
```

### 第二步：配置部署脚本

```bash
# 1. 设置脚本可执行权限
cd /opt/integrate-code
chmod +x scripts/deploy.sh
chmod +x scripts/rollback.sh

# 2. 修改部署脚本中的配置
nano scripts/deploy.sh

# 修改以下内容：
# - REPO_URL: 改为你的 Gitee 仓库地址
# - APP_NAME: 改为你的应用名称（默认就是 integrate-code）
```

### 第三步：配置 systemd 服务

```bash
# 1. 创建 systemd 服务文件
cat > /etc/systemd/system/integrate-code.service << 'EOF'
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
EOF

# 2. 重新加载 systemd
systemctl daemon-reload

# 3. 启用服务
systemctl enable integrate-code

# 4. 启动服务
systemctl start integrate-code

# 5. 检查状态
systemctl status integrate-code
```

### 第四步：配置 Webhook（可选 - 实现自动部署）

#### 方案 A：使用 Gitee Webhook

```bash
# 1. 安装 webhook 接收器依赖
cd /opt/integrate-code
pip3 install flask

# 2. 修改 webhook 接收器配置
nano scripts/webhook_receiver.py

# 修改以下内容：
# - WEBHOOK_SECRET: 设置你的 Webhook 密钥

# 3. 启动 webhook 接收器
nohup python3 scripts/webhook_receiver.py > /var/log/integrate-code/webhook.log 2>&1 &

# 4. 配置 Gitee Webhook
# 进入 Gitee 仓库设置 → WebHooks → 添加 WebHook
# URL: http://your-server-ip:9000/webhook/gitee
# 密码: 你设置的 WEBHOOK_SECRET
# 选择事件：推送事件
```

#### 方案 B：使用 GitHub Action 自动同步（推荐）

```bash
# 1. 生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "github-action" -f ~/.ssh/github_gitee_rsa

# 2. 复制私钥内容（后面需要配置到 GitHub）
cat ~/.ssh/github_gitee_rsa

# 3. 复制公钥内容
cat ~/.ssh/github_gitee_rsa.pub

# 4. 添加公钥到 Gitee
# 进入 Gitee 设置 → SSH 公钥 → 粘贴公钥 → 确定

# 5. 在 GitHub 上配置 Secrets
# 进入 GitHub 仓库 → Settings → Secrets and variables → Actions
# 添加 New repository secret
# Name: SSH_PRIVATE_KEY
# Value: 粘贴私钥内容（包括 BEGIN 和 END 行）

# 6. 确保 .github/workflows/sync-to-gitee.yml 文件存在并配置正确
# 修改 source-repo 和 destination-repo 为你的仓库地址
```

### 第五步：测试部署

```bash
# 1. 手动测试部署
cd /opt/integrate-code
./scripts/deploy.sh

# 2. 查看部署日志
tail -f /var/log/integrate-code/deploy.log

# 3. 检查应用状态
curl -I http://localhost:5000/

# 4. 检查服务状态
systemctl status integrate-code
```

### 第六步：配置防火墙（如果需要）

```bash
# 开放必要端口
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --permanent --add-port=9000/tcp
firewall-cmd --reload
```

---

## 📝 完整工作流程

### 日常开发流程

1. **本地开发**
   ```bash
   # 在本地开发新功能
   git add .
   git commit -m "feat: 添加新功能"
   git push origin 2.2
   ```

2. **创建 PR**
   - 在 GitHub 上创建 Pull Request
   - 从 `2.2` 合并到 `main`

3. **审核合并**
   - 代码审核通过
   - 合并到 `main`

4. **自动部署**（使用 GitHub Action）
   - GitHub Action 自动同步到 Gitee
   - 云主机自动检测更新
   - 自动执行部署

### 手动部署流程

如果不想使用自动部署，可以手动触发：

```bash
# 登录云主机
ssh root@your-server-ip

# 执行部署
cd /opt/integrate-code
./scripts/deploy.sh
```

---

## 🔧 故障排查

### 问题 1: 部署脚本执行失败

```bash
# 查看部署日志
tail -f /var/log/integrate-code/deploy.log

# 检查脚本权限
ls -la scripts/deploy.sh

# 确保脚本可执行
chmod +x scripts/deploy.sh
```

### 问题 2: 应用启动失败

```bash
# 查看应用日志
tail -f /var/log/integrate-code/app.log

# 手动启动测试
cd /opt/integrate-code
python3 app.py

# 检查环境变量
cat .env
```

### 问题 3: GitHub Action 同步失败

```bash
# 检查 GitHub Secrets 配置
# 进入 GitHub 仓库 → Settings → Secrets and variables → Actions
# 确认 SSH_PRIVATE_KEY 已正确配置

# 检查 SSH 密钥是否正确
# 在云主机上测试 SSH 连接
ssh -i ~/.ssh/github_gitee_rsa git@gitee.com

# 查看 GitHub Action 日志
# 进入 GitHub 仓库 → Actions → 查看运行记录
```

### 问题 4: Webhook 不工作

```bash
# 查看 webhook 接收器日志
tail -f /var/log/integrate-code/webhook.log

# 检查 webhook 接收器进程
ps aux | grep webhook_receiver

# 手动测试 webhook
curl -X POST http://localhost:9000/webhook/gitee \
  -H "X-Gitee-Token: your-secret" \
  -H "Content-Type: application/json" \
  -d '{"ref": "refs/heads/main"}'
```

---

## 🎯 最佳实践

### 1. 部署前检查清单

- [ ] 所有测试通过
- [ ] 代码审核完成
- [ ] 文档已更新
- [ ] `.env` 配置正确
- [ ] 数据库迁移脚本已准备

### 2. 备份策略

- 部署脚本自动创建备份
- 保留最近 5 个备份
- 备份位置：`/opt/integrate-code/backups/`

### 3. 回滚方案

```bash
# 快速回滚到上一版本
cd /opt/integrate-code
./scripts/rollback.sh

# 按提示选择要回滚的版本
```

### 4. 监控建议

```bash
# 监控应用日志
tail -f /var/log/integrate-code/app.log

# 监控部署日志
tail -f /var/log/integrate-code/deploy.log

# 监控服务状态
systemctl status integrate-code -f
```

---

## 📞 技术支持

如有问题，请查看详细文档：
- [CI/CD 部署文档](../docs/CI_CD_DEPLOYMENT_GUIDE.md)
- [系统配置指南](../docs/CONFIGURATION_GUIDE.md)

---

**文档版本**: v1.0  
**最后更新**: 2026-03-02
