# Gitee CI/CD 配置指南

## 概述

本项目已从 GitHub 迁移到 Gitee,使用 Gitee Actions 进行 CI/CD 自动化。

## CI/CD 流程

```
本地代码推送
    ↓
Gitee 仓库
    ↓
Gitee Actions CI/CD Pipeline
    ├─ 单元测试 (pytest)
    ├─ 代码检查 (flake8)
    ├─ 安全检查 (bandit)
    └─ Webhook 通知云主机
        ↓
云主机自动部署
```

## 配置步骤

### 1. Gitee Secrets 配置

在 Gitee 仓库中配置以下 Secrets:

**Settings** → **仓库设置** → **Gitee Go** → **变量配置**

| Secret 名称 | 说明 | 示例值 | 是否必需 |
|-------------|------|--------|----------|
| `WEBHOOK_URL` | 云主机 webhook 接收地址 | `http://10.10.10.250:9000` | ✅ 必需 |
| `GITEE_WEBHOOK_SECRET` | Webhook 签名密钥 | 随机生成的密钥 | ⚪ 可选 |

### 2. 生成 Webhook 密钥 (可选)

如果需要增强安全性,可以生成 webhook 密钥:

```bash
python scripts/generate-webhook-secret.py
```

然后将生成的密钥配置到:
- Gitee Secrets: `GITEE_WEBHOOK_SECRET`
- 云主机 `.env` 文件: `GITEE_WEBHOOK_SECRET=生成的密钥`

### 3. 云主机配置

在云主机的 `.env` 文件中添加:

```env
# Webhook 配置
WEBHOOK_URL=cloud-doors.com:9000
GITEE_WEBHOOK_SECRET=your-generated-secret-here  # 如果启用了签名验证
```

### 4. 更新云主机 webhook 服务

```bash
# SSH 到云主机
ssh root@10.10.10.250

# 进入项目目录
cd /opt/Home-page

# 拉取最新代码
git pull origin main

# 更新 webhook 服务配置
sudo systemctl stop webhook-receiver

# 使用新的 Gitee webhook 接收器
sudo sed -i 's/webhook_receiver_github.py/webhook_receiver_gitee.py/g' /etc/systemd/system/webhook-receiver.service

# 重载并启动服务
sudo systemctl daemon-reload
sudo systemctl start webhook-receiver
sudo systemctl enable webhook-receiver

# 查看服务状态
sudo systemctl status webhook-receiver
```

## CI/CD Workflow 说明

### 触发条件

- **Push**: main, develop, feat/*, fix/*, hotfix/* 分支
- **Pull Request**: 到 main 或 develop 分支

### 任务列表

1. **Run Tests**
   - 运行单元测试
   - 生成代码覆盖率报告
   - 使用 pytest 框架

2. **Code Lint**
   - 使用 flake8 检查代码质量
   - 使用 bandit 进行安全检查

3. **Security Check**
   - 依赖项安全检查
   - 不检查配置安全性(环境变量单独配置)

4. **Auto Merge to Main** (可选)
   - PR 通过所有检查后自动合并
   - 需要添加 `auto-merge` 标签

5. **Notify Cloud Server** (仅 main 分支)
   - 通过 Webhook 通知云主机
   - 触发自动部署流程
   - 记录部署日志和版本信息

## 使用说明

### 正常开发流程

```bash
# 1. 创建功能分支
git checkout -b feat/your-feature

# 2. 开发并提交
git add .
git commit -m "feat: 添加新功能"

# 3. 推送到 Gitee
git push origin feat/your-feature

# 4. 在 Gitee 创建 Pull Request

# 5. 通过 CI/CD 检查后合并到 main
```

### 直接推送到 main (紧急修复)

```bash
git checkout main
git pull origin main

# 修改代码
git add .
git commit -m "fix: 紧急修复"
git push origin main

# Gitee Actions 会自动触发部署
```

## 监控和调试

### 查看 CI/CD 状态

1. 进入 Gitee 仓库
2. 点击 **Gitee Go** 标签
3. 查看运行历史和日志

### 查看云主机部署日志

```bash
# 查看 webhook 服务日志
sudo journalctl -u webhook-receiver.service -f

# 查看部署日志
tail -f /var/log/integrate-code/deployment.log

# 查看 webhook 详细日志
tail -f /var/log/integrate-code/webhook.log
```

### 验证部署

```bash
# 测试 webhook 健康检查
curl http://10.10.10.250:9000/webhook/health

# 查看当前版本
curl http://10.10.10.250:9000/webhook/version

# 查看部署日志
curl http://10.10.10.250:9000/webhook/logs
```

## 常见问题

### Q1: CI/CD Pipeline 失败怎么办?

A: 检查以下项:
1. 查看 Gitee Actions 日志了解具体错误
2. 确保所有依赖项都正确安装
3. 检查代码是否通过 flake8 和 bandit 检查

### Q2: Webhook 通知失败怎么办?

A: 检查以下项:
1. 确认云主机 webhook 服务正在运行
2. 确认 `WEBHOOK_URL` 配置正确
3. 检查防火墙是否开放 9000 端口
4. 查看云主机 webhook 服务日志

### Q3: 部署没有触发怎么办?

A: 检查以下项:
1. 确认推送到了 main 分支
2. 查看 Gitee Actions 是否执行成功
3. 检查 Webhook 通知步骤是否成功
4. 查看云主机是否收到 webhook 请求

## 迁移记录

### 从 GitHub 迁移到 Gitee

- ✅ 创建 Gitee Actions CI/CD workflow
- ✅ 创建 Gitee webhook 接收器
- ✅ 移除 GitHub 同步流程
- ✅ 简化配置(无需 GITEE_REPO 和 GITEE_TOKEN)
- ✅ 更新文档和脚本

### 优势

- 简化 CI/CD 流程,无需同步
- 减少配置复杂度
- 降低维护成本
- 部署延迟更低
- 团队协作更清晰

## 参考资料

- [Gitee Actions 官方文档](https://help.gitee.com/actions/)
- [Gitee Webhook 文档](https://help.gitee.com/webhook/)
- [Pytest 文档](https://docs.pytest.org/)
- [Flake8 文档](https://flake8.pycqa.org/)
- [Bandit 文档](https://bandit.readthedocs.io/)
