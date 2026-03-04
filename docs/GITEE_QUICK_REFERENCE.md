# Gitee 快速参考卡

## 📌 当前配置

```bash
# 远程仓库
origin  https://gitee.com/liubin_studies/Home-page.git

# Gitee Actions
.gitee/workflows/ci-cd.yml

# Webhook 接收器
scripts/webhook_receiver_gitee.py
```

## 🚀 常用命令

### 日常开发

```bash
# 拉取最新代码
git pull origin main

# 提交代码
git add .
git commit -m "feat: 描述"
git push origin main

# 创建功能分支
git checkout -b feat/your-feature
git push origin feat/your-feature
```

### 云主机部署

```bash
# SSH 登录
ssh root@10.10.10.250

# 查看部署日志
tail -f /var/log/integrate-code/deployment.log

# 查看 webhook 日志
sudo journalctl -u webhook-receiver.service -f

# 手动触发部署
cd /opt/Home-page && bash ./scripts/deploy.sh
```

## 🔧 配置清单

### Gitee Secrets (必需)
- `WEBHOOK_URL` = `http://10.10.10.250:9000`

### 云主机 .env
```env
WEBHOOK_URL=cloud-doors.com:9000
GITEE_WEBHOOK_SECRET=your-secret-here  # 可选
```

## 📊 CI/CD 流程

```
推送代码到 Gitee
    ↓
Gitee Actions 执行
    ├─ 单元测试
    ├─ 代码检查
    ├─ 安全检查
    └─ Webhook 通知
        ↓
云主机自动部署
```

## 🆘 故障排查

### 推送失败
```bash
# 检查远程仓库
git remote -v

# 检查分支
git branch -a

# 强制推送 (谨慎使用)
git push origin main --force-with-lease
```

### CI/CD 失败
1. 查看 Gitee Actions 日志
2. 检查测试是否通过
3. 检查代码检查是否通过
4. 查看 webhook 日志

### 部署未触发
```bash
# 检查 webhook 服务
curl http://10.10.10.250:9000/webhook/health

# 检查 Secrets 配置
# Gitee → Settings → Gitee Go → 变量配置
```

## 📚 相关文档

- [Gitee CI/CD 配置指南](./GITEE_CICD_SETUP.md)
- [Git 远程仓库配置指南](./GIT_REMOTE_SETUP.md)
- [Gitee 迁移报告](./MIGRATION_TO_GITEE.md)

---

**注意**: 所有后续提交将直接推送到 Gitee,不再同步到 GitHub。
