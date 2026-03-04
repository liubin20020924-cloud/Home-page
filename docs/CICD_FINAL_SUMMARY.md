# CI/CD 最终配置总结

## 📋 当前 CI/CD 流程 (最终版)

```
┌─────────────────┐
│  本地开发环境    │
│  编写代码并提交  │
└────────┬─────────┘
         │ git push origin main
         ▼
┌─────────────────────────────────┐
│  GitHub 仓库                    │
│  - main 分支                    │
│  - 代码存储                     │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  GitHub Actions CI/CD Pipeline  │
│                                 │
│  1. 单元测试 (pytest)           │
│  2. 代码检查 (flake8)           │
│  3. 安全检查 (bandit)           │
│                                 │
│  4. 部署通知 (二选一)           │
│     ├─ 方案 A: Webhook          │
│     │  - POST /webhook/github    │
│     │  - 云主机端口 9000         │
│     │                          │
│     └─ 方案 B: SSH (备用)       │
│        - SSH 直接执行部署        │
│        - 不依赖 HTTP 连接        │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  云主机                         │
│                                 │
│  1. 通过代理从 GitHub 拉取      │
│  2. 备份当前版本                │
│  3. 安装/更新依赖               │
│  4. 重启应用                    │
│  5. 记录部署日志                │
└─────────────────────────────────┘
```

## 🎯 配置清单

### GitHub Secrets 配置

#### Webhook 方案 (方案 A)

| Secret 名称 | 值 | 必需 |
|-------------|---|------|
| `WEBHOOK_URL` | `http://10.10.10.250:9000` | ✅ |
| `WEBHOOK_SECRET` | 生成的密钥 | ⚪ |

#### SSH 方案 (方案 B)

| Secret 名称 | 值 | 必需 |
|-------------|---|------|
| `SSH_HOST` | `10.10.10.250` | ✅ |
| `SSH_USERNAME` | `root` | ✅ |
| `SSH_PRIVATE_KEY` | SSH 私钥 | ✅ |
| `SSH_PORT` | `22` | ⚪ |

### 云主机配置

#### 必需配置

```bash
# 1. Git 代理 (必需)
git config --global http.https://github.com.proxy http://proxy-server:port

# 2. .env 文件
WEBHOOK_URL=cloud-doors.com:9000
WEBHOOK_SECRET=your-secret-here  # 如果启用了签名验证

# 3. Webhook 服务
sudo systemctl start webhook-receiver
sudo systemctl enable webhook-receiver

# 4. 应用服务
sudo systemctl start flask-app
sudo systemctl enable flask-app
```

#### SSH 配置 (如果使用 SSH 方案)

```bash
# 1. 生成 SSH 密钥
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy_key

# 2. 配置公钥
cat ~/.ssh/github_deploy_key.pub >> ~/.ssh/authorized_keys

# 3. 设置权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/github_deploy_key

# 4. 测试连接
ssh -i ~/.ssh/github_deploy_key root@localhost
```

## 📊 部署方案对比

| 方案 | 配置难度 | 可靠性 | 安全性 | 推荐场景 |
|------|---------|--------|--------|----------|
| **Webhook** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 一般情况 |
| **SSH** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 高可靠性要求 |
| **双保险** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 生产环境(推荐) |

## 🚀 使用流程

### 正常开发流程

```bash
# 1. 创建功能分支
git checkout -b feat/new-feature

# 2. 开发并提交
git add .
git commit -m "feat: 添加新功能"
git push origin feat/new-feature

# 3. 在 GitHub 创建 PR

# 4. 等待 CI/CD 检查通过

# 5. 合并 PR
# 6. 自动部署到云主机
```

### 紧急修复流程

```bash
# 1. 切换到 main 分支
git checkout main
git pull origin main

# 2. 修复问题
vim app.py

# 3. 提交并推送
git add .
git commit -m "fix: 紧急修复"
git push origin main

# 4. 自动部署
```

## 📈 性能指标

| 步骤 | 时间 | 说明 |
|------|------|------|
| 单元测试 | 1-2 分钟 | pytest |
| 代码检查 | 30秒-1分钟 | flake8 + bandit |
| Webhook 通知 | <5秒 | HTTP 请求 |
| SSH 通知 | <10秒 | SSH 连接 |
| 代码拉取 | 30秒-2分钟 | 取决于代理 |
| 依赖安装 | 1-3分钟 | pip install |
| 应用重启 | 10-30秒 | systemctl |
| **总计** | **3-9分钟** | 从提交到部署完成 |

## 📚 文档索引

### 快速配置指南

| 文档 | 用途 |
|------|------|
| `docs/PROXY_QUICK_START.md` | 云主机代理快速配置 |
| `docs/SSH_QUICK_START.md` | SSH 部署快速配置 |
| `docs/WEBHOOK_TROUBLESHOOTING.md` | Webhook 问题排查 |

### 完整配置指南

| 文档 | 用途 |
|------|------|
| `docs/CICD_CURRENT_FLOW.md` | CI/CD 当前流程说明 |
| `docs/PROXY_SETUP.md` | 代理配置完整指南 |
| `docs/SSH_DEPLOYMENT.md` | SSH 部署完整指南 |
| `docs/CICD_SUMMARY.md` | CI/CD 完整总结 |

## ✅ 配置检查清单

### 本地环境

- [ ] Git 远程仓库配置为 GitHub
- [ ] 可以正常推送到 GitHub
- [ ] 可以正常拉取代码

### GitHub 配置

- [ ] GitHub Actions 已启用
- [ ] 至少配置一种部署方式 (Webhook 或 SSH)
- [ ] 配置了必要的 Secrets

### 云主机配置

- [ ] Git 代理已配置
- [ ] 可以正常从 GitHub 拉取代码
- [ ] Webhook 服务正在运行 (如果使用 Webhook)
- [ ] SSH 密钥已配置 (如果使用 SSH)
- [ ] 应用服务正在运行

### CI/CD 流程

- [ ] 推送代码触发 GitHub Actions
- [ ] 单元测试通过
- [ ] 代码检查通过
- [ ] 安全检查通过
- [ ] 部署通知成功
- [ ] 云主机收到通知
- [ ] 代码已部署
- [ ] 应用正常运行

## 🆘 故障排查

### 问题 1: GitHub Actions 失败

**检查项**:
1. 查看错误日志
2. 检查测试是否通过
3. 检查代码检查是否通过
4. 检查部署通知是否成功

**解决方法**:
- 修复代码问题
- 重新运行 workflow
- 检查 GitHub Secrets 配置

### 问题 2: Webhook 通知失败

**检查项**:
1. 云主机 webhook 服务是否运行
2. 端口 9000 是否开放
3. WEBHOOK_URL 配置是否正确
4. 网络连接是否正常

**解决方法**:
```bash
# 检查服务状态
sudo systemctl status webhook-receiver

# 重启服务
sudo systemctl restart webhook-receiver

# 测试 webhook
curl http://10.10.10.250:9000/webhook/health
```

### 问题 3: SSH 通知失败

**检查项**:
1. SSH 配置是否正确
2. SSH 密钥是否有效
3. 防火墙是否开放 SSH 端口
4. 网络连接是否正常

**解决方法**:
```bash
# 测试 SSH 连接
ssh -i ~/.ssh/github_deploy_key root@10.10.10.250

# 检查防火墙
sudo firewall-cmd --list-all

# 查看连接日志
sudo journalctl -u sshd
```

### 问题 4: 云主机拉取代码失败

**检查项**:
1. Git 代理是否配置
2. GitHub 连接是否正常
3. 代理服务是否可用

**解决方法**:
```bash
# 测试 GitHub 连接
curl --proxy http://proxy-server:port https://github.com

# 手动拉取测试
cd /opt/Home-page
git fetch origin

# 检查代理配置
git config --global --get http.https://github.com.proxy
```

## 🎉 总结

### 当前状态

✅ **CI/CD 流程**: 本地 → GitHub → GitHub Actions → Webhook/SSH → 云主机部署
✅ **部署方式**: Webhook 和 SSH 两种方案可选
✅ **代码存储**: 仅 GitHub,不再同步到 Gitee
✅ **文档完整**: 快速配置 + 完整指南 + 问题排查

### 关键配置

1. **GitHub Actions**: `.github/workflows/ci-cd.yml`
2. **Webhook 接收器**: `scripts/webhook_receiver_github.py`
3. **部署脚本**: `scripts/deploy.sh`
4. **智能拉取**: `scripts/smart-pull.sh`

### 优势

1. **自动化程度高**: 测试、检查、部署全自动
2. **可靠性高**: 双保险部署方案
3. **安全性强**: 签名验证 + SSH 密钥
4. **快速高效**: 3-9 分钟完成部署

### 下一步

1. **配置云主机代理** (必需)
2. **选择部署方式** (Webhook 或 SSH 或两者)
3. **测试完整流程**
4. **配置团队协作**

---

**配置状态**: ✅ 完成
**最后更新**: 2026-03-04
**CI/CD 流程**: 本地 → GitHub → GitHub Actions → Webhook/SSH → 云主机部署
