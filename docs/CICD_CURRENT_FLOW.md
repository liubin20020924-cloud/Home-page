# CI/CD 当前流程说明

## 📋 当前的 CI/CD 流程

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
│     - 测试用例执行              │
│     - 代码覆盖率报告            │
│                                 │
│  2. 代码检查 (flake8)           │
│     - 代码风格检查              │
│     - 代码质量检查              │
│                                 │
│  3. 安全检查 (bandit)           │
│     - 安全漏洞扫描              │
│     - 依赖项检查                │
│                                 │
│  4. Webhook 通知                │
│     - 发送 webhook 到云主机     │
│     - 包含版本和提交信息        │
└────────┬────────────────────────┘
         │ POST /webhook/github
         ▼
┌─────────────────────────────────┐
│  云主机 Webhook 接收器          │
│  (webhook_receiver_github.py)   │
│                                 │
│  - 端口: 9000                   │
│  - 验证签名 (可选)              │
│  - 触发部署脚本                 │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  云主机部署脚本                 │
│  (scripts/deploy.sh)            │
│                                 │
│  1. 使用 smart-pull.sh 拉取代码  │
│     - 检测 GitHub 速度          │
│     - 从 GitHub 拉取代码        │
│                                 │
│  2. 备份当前版本                │
│     - 保留最近 5 个备份         │
│                                 │
│  3. 安装依赖                    │
│     - pip install -r requirements.txt
│                                 │
│  4. 重启应用                    │
│     - systemctl restart flask-app
│                                 │
│  5. 记录部署日志                │
│     - 版本信息                  │
│     - 部署时间                  │
│     - 部署状态                  │
└─────────────────────────────────┘
```

## 🎯 关键配置

### GitHub Secrets 配置

| Secret 名称 | 值 | 说明 |
|-------------|---|------|
| `WEBHOOK_URL` | `http://10.10.10.250:9000` | 云主机 webhook 地址 |
| `WEBHOOK_SECRET` | `生成的密钥` (可选) | Webhook 签名密钥 |

### 云主机配置

```bash
# .env 文件配置
WEBHOOK_URL=cloud-doors.com:9000
WEBHOOK_SECRET=your-secret-here  # 如果启用了签名验证

# Git 代理配置 (必需)
git config --global http.https://github.com.proxy http://proxy-server:port
```

## 📊 流程详细说明

### 步骤 1: 本地开发

```bash
# 1. 创建功能分支
git checkout -b feat/new-feature

# 2. 开发并提交
git add .
git commit -m "feat: 添加新功能"

# 3. 推送到 GitHub
git push origin feat/new-feature
```

### 步骤 2: 创建 Pull Request

1. 在 GitHub 仓库页面
2. 点击 "Pull requests"
3. 点击 "New pull request"
4. 选择 `feat/new-feature` → `main`
5. 填写 PR 描述
6. 点击 "Create pull request"

### 步骤 3: CI/CD 自动执行

GitHub Actions 自动执行:
- ✅ 单元测试
- ✅ 代码检查
- ✅ 安全检查

如果所有检查通过:
- ✅ 合并 PR 到 main 分支
- ✅ 触发 Webhook 通知

### 步骤 4: 云主机自动部署

Webhook 接收器收到通知后:
- ✅ 从 GitHub 拉取最新代码
- ✅ 备份当前版本
- ✅ 安装依赖
- ✅ 重启应用
- ✅ 记录日志

## 🔍 监控和验证

### 1. 查看 GitHub Actions 状态

访问: `https://github.com/liubin20020924-cloud/Home-page/actions`

查看:
- Workflow 运行状态
- 测试结果
- 部署通知状态

### 2. 查看云主机部署日志

```bash
# SSH 到云主机
ssh root@10.10.10.250

# 查看 webhook 日志
sudo journalctl -u webhook-receiver.service -f

# 查看部署日志
tail -f /var/log/integrate-code/deployment.log

# 查看应用日志
tail -f /var/log/integrate-code/app.log
```

### 3. 验证部署结果

```bash
# 检查 Git 提交
cd /opt/Home-page
git log -1

# 检查文件更新
ls -la

# 检查应用状态
sudo systemctl status flask-app

# 测试应用访问
curl http://10.10.10.250:5000
```

## ⚡ 快速部署 (直接推送到 main)

对于紧急修复,可以直接推送到 main:

```bash
# 警告: 仅用于紧急修复
git checkout main
git pull origin main

# 修改代码
vim app.py

# 提交并推送
git add .
git commit -m "fix: 紧急修复"
git push origin main

# CI/CD 自动执行并部署
```

## 🔄 分支策略

### 分支说明

| 分支 | 用途 | CI/CD |
|------|------|-------|
| `main` | 生产环境 | ✅ 完整 CI/CD + 自动部署 |
| `develop` | 开发环境 | ✅ CI/CD + 无部署 |
| `feat/*` | 功能分支 | ✅ CI/CD + 无部署 |
| `fix/*` | 修复分支 | ✅ CI/CD + 无部署 |
| `hotfix/*` | 热修复分支 | ✅ CI/CD + 自动部署 (合并到 main) |

### 推荐工作流程

```
开发流程:
1. 从 main 创建 feat/your-feature 分支
2. 在功能分支开发
3. 推送到 GitHub
4. 创建 PR 到 main
5. 等待 CI/CD 检查通过
6. 代码审查
7. 合并到 main
8. 自动部署到生产环境

紧急修复:
1. 从 main 创建 hotfix/urgent-fix 分支
2. 修复问题
3. 推送到 GitHub
4. 创建 PR 到 main (标记为紧急)
5. 快速审查
6. 合并到 main
7. 自动部署到生产环境
```

## 🆘 故障排查

### 问题 1: GitHub Actions 失败

**检查项**:
1. 查看错误日志
2. 检查测试是否通过
3. 检查代码检查是否通过
4. 检查 webhook 通知是否成功

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

# 检查端口
sudo netstat -tulpn | grep 9000

# 测试 webhook
curl http://10.10.10.250:9000/webhook/health
```

### 问题 3: 云主机拉取代码失败

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

### 问题 4: 部署失败

**检查项**:
1. 部署日志
2. 应用日志
3. 依赖安装日志
4. 服务状态

**解决方法**:
```bash
# 查看部署日志
tail -100 /var/log/integrate-code/deployment.log

# 手动执行部署
cd /opt/Home-page
bash ./scripts/deploy.sh

# 检查服务状态
sudo systemctl status flask-app

# 回滚到上一个版本
bash ./scripts/rollback.sh
```

## 📊 性能指标

### 典型时间消耗

| 步骤 | 时间 | 说明 |
|------|------|------|
| 单元测试 | 1-2 分钟 | pytest 执行 |
| 代码检查 | 30秒-1分钟 | flake8 + bandit |
| Webhook 通知 | <5秒 | HTTP 请求 |
| 代码拉取 | 30秒-2分钟 | 取决于代理速度 |
| 依赖安装 | 1-3分钟 | pip install |
| 应用重启 | 10-30秒 | systemctl |
| **总计** | **3-9分钟** | 从提交到部署完成 |

### 部署频率

- 正常开发: 每天 3-5 次
- 紧急修复: 随时
- 版本发布: 每周 1-2 次

## 📚 相关文档

- [CI/CD 完整总结](./CICD_SUMMARY.md)
- [Webhook 配置指南](./WEBHOOK_TROUBLESHOOTING.md)
- [代理配置指南](./PROXY_SETUP.md)
- [版本管理规范](./VERSION_MANAGEMENT_GUIDE.md)
- [GitHub Actions 配置](./CICD_SUMMARY.md#github-actions-配置)

---

**当前流程确认**: ✅ 本地 → GitHub → GitHub Actions → Webhook → 云主机自动部署

**最后更新**: 2026-03-04
