# SSH 部署快速配置

## 🚀 快速配置 (5 分钟)

### 1. 云主机: 生成 SSH 密钥

```bash
# SSH 登录云主机
ssh root@10.10.10.250

# 生成密钥
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy_key

# 配置公钥
cat ~/.ssh/github_deploy_key.pub >> ~/.ssh/authorized_keys

# 设置权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/github_deploy_key
```

### 2. 云主机: 复制私钥

```bash
# 显示私钥 (复制完整输出)
cat ~/.ssh/github_deploy_key
```

⚠️ **复制完整的私钥**,包括 `-----BEGIN` 和 `-----END` 行!

### 3. GitHub: 配置 Secrets

进入 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

**Secret 1: SSH_HOST**
```
Value: 10.10.10.250  # 云主机 IP
```

**Secret 2: SSH_USERNAME**
```
Value: root
```

**Secret 3: SSH_PRIVATE_KEY**
```
Value: 粘贴刚才复制的完整私钥
```

### 4. 测试

```bash
# 本地推送测试
echo "Test SSH deployment" > test-ssh.txt
git add test-ssh.txt
git commit -m "test(ssh): 测试SSH部署"
git push origin main
```

### 5. 验证

查看 GitHub Actions 的 "Notify cloud server via SSH" 步骤,应该看到:
```
SSH 连接成功,触发部署...
执行部署脚本...
```

## ✅ 配置检查清单

- [ ] 云主机生成 SSH 密钥对
- [ ] 公钥添加到 authorized_keys
- [ ] 设置正确的文件权限
- [ ] 私钥复制到 GitHub Secrets
- [ ] 测试 SSH 连接成功
- [ ] 测试部署成功

## 📊 部署方式对比

| 方式 | Webhook | SSH |
|------|---------|-----|
| 配置 | WEBHOOK_URL | SSH_HOST + SSH_USERNAME + SSH_PRIVATE_KEY |
| 可靠性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 推荐场景 | 一般情况 | 高可靠性要求 |

## 🎯 推荐配置

**Webhook + SSH 双保险** (推荐):
- 配置 `WEBHOOK_URL`
- 配置 SSH Secrets
- Webhook 正常时使用 Webhook
- Webhook 失败时自动使用 SSH

## 🆘 常见问题

**Q: SSH 连接超时?**
```bash
# 检查防火墙
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --reload
```

**Q: 认证失败?**
```bash
# 测试密钥
ssh -i ~/.ssh/github_deploy_key -vvv root@localhost
```

**Q: 密钥格式错误?**
```bash
# 确保复制完整的私钥
cat ~/.ssh/github_deploy_key
```

## 📚 详细文档

完整配置指南: [docs/SSH_DEPLOYMENT.md](./SSH_DEPLOYMENT.md)

---

配置完成后,您就有了 Webhook 和 SSH 两种部署方式! 🚀
