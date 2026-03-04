# 云户科技网站 - 快速配置指南（简化版）

> 云主机直接从GitHub拉取代码，无需Gitee中转

---

## 🎯 简化方案概述

**自动化流程**：
```
本地开发 → Git提交 → GitHub → 云主机检测/通知 → 自动部署
```

**核心优势**：
- ✅ 配置简单（只需GitHub）
- ✅ 无需SSH密钥（使用Personal Access Token）
- ✅ 部署延迟低（5分钟或实时）
- ✅ 维护成本低

---

## 📦 仓库信息

- **GitHub**: https://github.com/liubin20020924-cloud/Home-page.git
- **项目路径**: `/opt/Home-page`

---

## 🚀 快速配置步骤

### 第一步：云主机克隆GitHub仓库

```bash
# 克隆仓库
cd /opt
git clone https://github.com/liubin20020924-cloud/Home-page.git

# 进入项目目录
cd /opt/Home-page
```

---

### 第二步：配置GitHub Personal Access Token

#### 2.1 生成Personal Access Token

1. 访问：https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 配置Token权限：
   - ✅ `repo` - 完整仓库访问权限
   - ✅ `workflow` - GitHub Actions权限
4. 点击 **Generate token**
5. **复制Token**（只显示一次，请妥善保存）

#### 2.2 配置Git凭据

```bash
# 配置Git凭据
git config --global credential.helper store

# 测试拉取（会提示输入用户名和Token）
git pull

# 输入：
# Username: liubin20020924-cloud
# Password: <粘贴刚才生成的Personal Access Token>
```

**配置成功后**，后续拉取和推送都不需要输入密码。

---

### 第三步：生成Webhook密钥

```bash
# 生成强密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

复制生成的密钥（例如：`abc123xyz456def789...`）

---

### 第四步：配置Webhook密钥文件

```bash
# 编辑GitHub版Webhook接收器
nano /opt/Home-page/scripts/webhook_receiver_github.py
# 找到这一行:
# WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-webhook-secret-here')
# 替换为:
# WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '上面生成的密钥')

# 编辑GitHub版自动检测脚本
nano /opt/Home-page/scripts/check_and_deploy_github.sh
# 找到这一行:
# WEBHOOK_SECRET="your-webhook-secret-here"
# 替换为:
# WEBHOOK_SECRET="上面生成的密钥"
```

---

### 第五步：安装部署服务

```bash
# 运行一键安装脚本
bash /opt/Home-page/scripts/deploy_service.sh
```

该脚本会自动：
- 创建必要的目录
- 设置文件权限
- 创建systemd服务
- 配置定时任务（每5分钟）
- 配置防火墙规则（开放9000端口）
- 启动服务

---

### 第六步：验证服务状态

```bash
# 查看webhook服务
systemctl status webhook-receiver

# 查看定时任务
crontab -l
# 应该看到: */5 * * * * /opt/Home-page/scripts/check_and_deploy_github.sh

# 查看服务日志
tail -f /var/log/integrate-code/webhook.log

# 查看自动部署日志
tail -f /var/log/integrate-code/auto-deploy.log
```

---

## 🔔 可选：配置GitHub Webhook（实时触发）

如果希望代码推送到GitHub后**立即**触发部署（而不是等待5分钟）：

### 1. 在GitHub添加Webhook

访问：https://github.com/liubin20020924-cloud/Home-page/settings/hooks

点击 **Add webhook**，配置：

- **Payload URL**: `http://your-server-ip:9000/webhook/github`
- **Content type**: `application/json`
- **Secret**: 填写第四步生成的WEBHOOK_SECRET
- **Events**: 选择 **Just the push event**
- **Active**: ✅ 勾选

点击 **Add webhook**。

### 2. 配置GitHub Secrets（用于Actions通知）

访问：https://github.com/liubin20020924-cloud/Home-page/settings/secrets/actions

添加以下Secrets：

**WEBHOOK_URL**:
```
http://your-server-ip:9000
```

**WEBHOOK_SECRET**:
```
第四步生成的密钥
```

### 3. 测试Webhook

推送任意代码到GitHub，查看：
- GitHub Webhook是否成功（绿色✓）
- 云主机是否立即开始部署

---

## ✅ 测试完整流程

### 1. 本地修改代码

```bash
# 创建测试分支
git checkout -b feat/test-github-deploy

# 修改文件
echo "测试GitHub直接部署" > test-deploy.txt
git add test-deploy.txt

# 提交（遵循Conventional Commits规范）
git commit -m "test(deploy): 测试GitHub直接部署流程"

# 推送到GitHub
git push origin feat/test-github-deploy
```

### 2. 创建Pull Request

在GitHub创建PR并合并到main分支。

### 3. 等待自动部署

- **方案A（定时检测）**: 最多5分钟
- **方案B（Webhook触发）**: 立即（几秒内）

### 4. 验证部署结果

```bash
# 查看部署日志
tail -f /var/log/integrate-code/deploy.log

# 查看应用状态
systemctl status integrate-code

# 访问应用测试
curl http://localhost:5000
```

---

## 📊 两种触发方式对比

| 方式 | 延迟 | 配置复杂度 | 推荐场景 |
|------|------|-----------|---------|
| **定时检测** | 最多5分钟 | ⭐ 简单 | 不需要立即部署，配置最简单 |
| **Webhook触发** | 实时（秒级） | ⭐⭐ 中等 | 需要立即部署，适合生产环境 |

---

## 🔧 常用命令

```bash
# 手动触发部署
bash /opt/Home-page/scripts/deploy.sh

# 查看部署日志
tail -f /var/log/integrate-code/deploy.log

# 查看webhook日志
tail -f /var/log/integrate-code/webhook.log

# 查看自动检测日志
tail -f /var/log/integrate-code/auto-deploy.log

# 回滚到上一版本
bash /opt/Home-page/scripts/rollback.sh

# 重启webhook服务
systemctl restart webhook-receiver

# 查看定时任务
crontab -l

# 手动检测更新
bash /opt/Home-page/scripts/check_and_deploy_github.sh
```

---

## 📝 配置检查清单

完成配置后，确认以下项目：

### 基础配置
- [ ] GitHub仓库已克隆到 `/opt/Home-page`
- [ ] Git凭据已配置（使用Personal Access Token）
- [ ] `git pull` 可以正常拉取代码

### Webhook配置
- [ ] 已生成WEBHOOK_SECRET密钥
- [ ] `scripts/webhook_receiver_github.py` 密钥已更新
- [ ] `scripts/check_and_deploy_github.sh` 密钥已更新

### 服务配置
- [ ] `webhook-receiver` 服务正在运行
- [ ] 定时任务已配置（`crontab -l` 可看到）
- [ ] 防火墙规则已添加（端口9000）

### 验证测试
- [ ] 手动运行部署脚本成功
- [ ] 推送代码后自动检测到更新
- [ ] 自动部署成功，应用正常运行

---

## 🔍 故障排查

### Git拉取失败

```bash
# 错误: Authentication failed
# 解决: 重新配置Personal Access Token
git config --global credential.helper store
git pull
# 输入新的Token
```

### Webhook服务未启动

```bash
# 查看服务状态
systemctl status webhook-receiver

# 重启服务
systemctl restart webhook-receiver

# 查看错误日志
tail -f /var/log/integrate-code/webhook-error.log
```

### 自动检测未触发

```bash
# 查看定时任务
crontab -l

# 手动运行检测脚本
bash /opt/Home-page/scripts/check_and_deploy_github.sh

# 查看日志
tail -f /var/log/integrate-code/auto-deploy.log
```

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| **[简化版CI/CD配置](SIMPLIFIED_CI_CD.md)** | 详细的简化方案说明 |
| [版本管理规范](VERSION_MANAGEMENT_GUIDE.md) | 完整的版本管理规范 |
| [版本管理快速指南](QUICK_START_VERSIONING.md) | 版本管理快速参考 |
| [配置检查清单](CHECKLIST.md) | 配置进度追踪 |

---

## 🎉 配置完成

当以上所有步骤完成后，您就拥有了一个：

✅ **简单的CI/CD系统**
✅ **自动化部署流程**
✅ **实时或定时触发**
✅ **自动备份和回滚**

---

**日常开发流程**：
```bash
git checkout -b feat/your-feature
# 编写代码
git commit -m "feat(home: 添加新功能"
git push origin feat/your-feature
# 在GitHub创建PR并合并
# 等待自动部署完成！
```

---

**配置完成，享受自动化！** 🚀
