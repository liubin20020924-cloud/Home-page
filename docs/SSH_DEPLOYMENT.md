# SSH 部署配置指南

## 概述

SSH 方案是 Webhook 的备用部署通知方式,可以在 Webhook 不可用时使用,或者作为主要部署方式。

## 优势

✅ **可靠性高**: 不依赖 HTTP 连接
✅ **安全性强**: 使用 SSH 密钥认证
✅ **独立性强**: 不依赖外部网络服务
✅ **灵活性大**: 可以执行任意命令

## 配置步骤

### 1. 云主机配置

#### 1.1 生成 SSH 密钥对

在云主机上执行:

```bash
# SSH 登录云主机
ssh root@10.10.10.250

# 生成 SSH 密钥对
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key

# 或使用 RSA 密钥
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key
```

#### 1.2 配置公钥认证

```bash
# 将公钥添加到 authorized_keys
cat ~/.ssh/github_deploy_key.pub >> ~/.ssh/authorized_keys

# 设置正确的权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/github_deploy_key
chmod 644 ~/.ssh/github_deploy_key.pub

# 测试 SSH 连接
ssh -i ~/.ssh/github_deploy_key root@localhost
```

#### 1.3 允许 root SSH 登录

```bash
# 编辑 SSH 配置
vim /etc/ssh/sshd_config

# 确保以下配置:
PubkeyAuthentication yes
PermitRootLogin yes

# 重启 SSH 服务
sudo systemctl restart sshd
```

### 2. GitHub Secrets 配置

#### 2.1 获取私钥

在云主机上执行:

```bash
# 显示私钥 (复制完整的输出)
cat ~/.ssh/github_deploy_key
```

输出类似:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
...
-----END OPENSSH PRIVATE KEY-----
```

⚠️ **重要**: 复制完整的私钥,包括 `-----BEGIN` 和 `-----END` 行!

#### 2.2 配置 GitHub Secrets

进入 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

**Secret 1: SSH_HOST**
```
Name: SSH_HOST
Value: 10.10.10.252  # 云主机 IP 地址或域名
```

**Secret 2: SSH_USERNAME**
```
Name: SSH_USERNAME
Value: root  # SSH 用户名
```

**Secret 3: SSH_PRIVATE_KEY**
```
Name: SSH_PRIVATE_KEY
Value: 粘贴刚才复制的完整私钥
```

**Secret 4: SSH_PORT** (可选)
```
Name: SSH_PORT
Value: 22  # SSH 端口,默认 22
```

### 3. 测试 SSH 部署

#### 3.1 推送测试代码

```bash
# 本地
echo "Test SSH deployment" > test-ssh-deploy.txt
git add test-ssh-deploy.txt
git commit -m "test(ci-cd): 测试SSH部署方案"
git push origin main
```

#### 3.2 查看 GitHub Actions

进入 GitHub 仓库 → **Actions** 标签,查看:

1. "Notify cloud server via SSH (备用方案)" 步骤
2. 应该看到类似输出:
   ```
   ==========================================
   通过 SSH 通知云服务器部署...
   ==========================================
   SSH Host: 10.10.10.252
   SSH Port: 22
   SSH Username: root
   添加主机到 known_hosts...
   测试 SSH 连接...
   SSH 连接成功,触发部署...
   执行部署脚本...
   ...
   ==========================================
   SSH 部署通知已发送
   ==========================================
   ```

#### 3.3 验证部署

```bash
# SSH 到云主机
ssh root@10.10.10.250

# 查看部署日志
tail -f /var/log/integrate-code/deployment.log

# 查看测试文件
cd /opt/Home-page
ls -la test-ssh-deploy.txt
```

## 部署方式选择

### 方式 1: 仅使用 SSH

如果只想使用 SSH 方式:

1. **不配置** `WEBHOOK_URL` Secret
2. **配置** SSH 相关 Secrets

这样 GitHub Actions 会跳过 Webhook 通知,只使用 SSH 方式。

### 方式 2: Webhook + SSH 双保险 (推荐)

配置两种方式:

1. **配置** `WEBHOOK_URL` Secret
2. **配置** SSH 相关 Secrets

这样:
- Webhook 正常时,使用 Webhook 方式
- Webhook 失败时,SSH 方式仍然可以工作

### 方式 3: 仅使用 Webhook

1. **配置** `WEBHOOK_URL` Secret
2. **不配置** SSH 相关 Secrets

这样只使用 Webhook 方式,跳过 SSH 步骤。

## SSH 密钥管理

### 密钥轮换

定期更换 SSH 密钥以提高安全性:

```bash
# 1. 生成新密钥
ssh-keygen -t ed25519 -C "github-actions-deploy-v2" -f ~/.ssh/github_deploy_key_v2

# 2. 添加新公钥
cat ~/.ssh/github_deploy_key_v2.pub >> ~/.ssh/authorized_keys

# 3. 测试新密钥
ssh -i ~/.ssh/github_deploy_key_v2 root@localhost

# 4. 更新 GitHub Secrets
#    复制新私钥到 SSH_PRIVATE_KEY

# 5. 测试部署
#    推送测试代码

# 6. 删除旧密钥 (确认新密钥工作后)
# rm ~/.ssh/github_deploy_key
# rm ~/.ssh/github_deploy_key.pub
```

### 密钥权限

确保正确的文件权限:

```bash
# 私钥权限
chmod 600 ~/.ssh/github_deploy_key

# 公钥权限
chmod 644 ~/.ssh/github_deploy_key.pub

# SSH 目录权限
chmod 700 ~/.ssh

# authorized_keys 权限
chmod 600 ~/.ssh/authorized_keys
```

## 故障排查

### 问题 1: SSH 连接超时

**原因**: 防火墙阻止或网络不通

**解决方法**:
```bash
# 检查防火墙
sudo firewall-cmd --list-all  # CentOS/RHEL
sudo ufw status              # Ubuntu/Debian

# 开放 SSH 端口
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --reload

# 测试连接
telnet 10.10.10.252 22
```

### 问题 2: SSH 认证失败

**原因**: 密钥配置不正确

**解决方法**:
```bash
# 在云主机上测试
ssh -i ~/.ssh/github_deploy_key -vvv root@localhost

# 检查 authorized_keys
cat ~/.ssh/authorized_keys

# 检查 SSH 配置
sudo grep -E "PubkeyAuthentication|PermitRootLogin" /etc/ssh/sshd_config

# 重启 SSH 服务
sudo systemctl restart sshd
```

### 问题 3: 密钥格式错误

**原因**: 私钥复制不完整或格式错误

**解决方法**:
```bash
# 验证私钥格式
cat ~/.ssh/github_deploy_key

# 应该包含:
# -----BEGIN OPENSSH PRIVATE KEY-----
# ...
# -----END OPENSSH PRIVATE KEY-----

# 重新复制私钥,确保完整复制
```

### 问题 4: 部署脚本执行失败

**原因**: 脚本权限或路径问题

**解决方法**:
```bash
# 检查脚本权限
ls -la /opt/Home-page/scripts/deploy.sh

# 设置执行权限
chmod +x /opt/Home-page/scripts/deploy.sh

# 手动测试
cd /opt/Home-page
./scripts/deploy.sh

# 查看错误日志
tail -100 /var/log/integrate-code/deployment.log
```

## 安全建议

### 1. 使用专用密钥

为 GitHub Actions 创建专用的 SSH 密钥,不要使用其他用途的密钥。

### 2. 限制密钥用途

在 `~/.ssh/authorized_keys` 中使用 `command` 限制密钥只能执行特定命令:

```bash
# 编辑 authorized_keys
vim ~/.ssh/authorized_keys

# 添加限制:
command="cd /opt/Home-page && ./scripts/deploy.sh" ssh-ed25519 AAAA...
```

这样该密钥只能执行部署脚本,不能执行其他命令。

### 3. 定期轮换密钥

建议每 3-6 个月更换一次 SSH 密钥。

### 4. 监控 SSH 日志

定期查看 SSH 日志,监控异常登录:

```bash
# 查看 SSH 认证日志
sudo grep "Accepted" /var/log/secure | tail -20

# 查看失败登录
sudo grep "Failed" /var/log/secure | tail -20
```

### 5. 使用非 root 用户

考虑创建专用的部署用户,而不是使用 root:

```bash
# 创建部署用户
useradd -m -s /bin/bash deployer

# 配置 sudo 权限
visudo
# 添加: deployer ALL=(ALL) NOPASSWD: /opt/Home-page/scripts/deploy.sh

# 使用 deployer 用户
```

## 与 Webhook 方案对比

| 特性 | Webhook | SSH |
|------|---------|-----|
| 可靠性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 安全性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 配置复杂度 | ⭐⭐⭐⭐ | ⭐⭐ |
| 灵活性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 依赖 | HTTP 连接 | SSH 连接 |
| 推荐场景 | 一般情况 | 高可靠性要求 |

## 相关文档

- [CI/CD 当前流程](./CICD_CURRENT_FLOW.md)
- [Webhook 配置指南](./WEBHOOK_TROUBLESHOOTING.md)
- [CI/CD 完整总结](./CICD_SUMMARY.md)

---

**配置完成时间**: 2026-03-04
**配置负责人**: [您的名字]
