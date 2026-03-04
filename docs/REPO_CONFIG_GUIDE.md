# 仓库配置快速指南

> 云户科技网站 - GitHub和Gitee仓库配置

---

## 📌 仓库信息

- **GitHub仓库**: https://github.com/liubin20020924-cloud/Home-page.git
- **Gitee仓库**: https://gitee.com/liubin_studies/Home-page.git

---

## 🚀 快速配置步骤

### 第一步: 生成SSH密钥对

在本地或云主机上执行:

```bash
# 生成SSH密钥对
ssh-keygen -t rsa -b 4096 -C "github-gitee-sync" -f ~/.ssh/github_gitee_rsa

# 查看私钥(复制到GitHub Secrets)
cat ~/.ssh/github_gitee_rsa

# 查看公钥(复制到Gitee SSH公钥)
cat ~/.ssh/github_gitee_rsa.pub
```

**重要**: 私钥内容应包含完整的 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----` 行。

---

### 第二步: 配置Gitee SSH公钥

1. 登录 [Gitee](https://gitee.com/)
2. 进入 **个人设置** → **SSH 公钥**
3. 点击 **添加公钥**
4. 粘贴公钥内容(`cat ~/.ssh/github_gitee_rsa.pub` 的输出)
5. 标题填写: `GitHub Sync Key`
6. 点击 **确定**

---

### 第三步: 配置GitHub Secrets

1. 进入 [GitHub仓库](https://github.com/liubin20020924-cloud/Home-page)
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**

#### 添加Secret: SSH_PRIVATE_KEY

- **Name**: `SSH_PRIVATE_KEY`
- **Value**: 粘贴私钥的完整内容(`cat ~/.ssh/github_gitee_rsa` 的输出)

#### 添加Secret: GITEE_REPO

- **Name**: `GITEE_REPO`
- **Value**: `liubin_studies/Home-page`

---

### 第四步: 测试GitHub同步到Gitee

在本地执行以下命令测试:

```bash
# 确保在main分支
git checkout main

# 创建一个测试提交
git commit --allow-empty -m "test: 测试GitHub到Gitee同步"

# 推送到GitHub
git push origin main
```

验证步骤:
1. 访问 [GitHub Actions](https://github.com/liubin20020924-cloud/Home-page/actions)
2. 查看 "Sync to Gitee" 工作流是否成功
3. 访问 [Gitee仓库](https://gitee.com/liubin_studies/Home-page)
4. 确认代码已同步

---

### 第五步: 云主机配置

#### 5.1 生成Webhook密钥

在云主机上执行:

```bash
# 生成强密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

复制生成的密钥(例如: `abc123xyz456...`)

#### 5.2 配置Webhook密钥

编辑以下两个文件,替换密钥占位符:

```bash
# 编辑webhook接收器
nano /opt/integrate-code/scripts/webhook_receiver.py
# 找到这一行: WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-webhook-secret-here')
# 替换为: WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '上面生成的密钥')

# 编辑自动检测脚本
nano /opt/integrate-code/scripts/check_and_deploy.sh
# 找到这一行: WEBHOOK_SECRET="your-webhook-secret-here"
# 替换为: WEBHOOK_SECRET="上面生成的密钥"
```

#### 5.3 安装自动部署服务

```bash
# 运行一键安装脚本
bash /opt/integrate-code/scripts/deploy_service.sh
```

该脚本会自动:
- 创建必要的目录
- 设置文件权限
- 创建systemd服务
- 配置定时任务(每5分钟)
- 配置防火墙规则
- 启动服务

#### 5.4 验证服务状态

```bash
# 查看webhook服务状态
systemctl status webhook-receiver

# 查看定时任务
crontab -l

# 查看服务日志
tail -f /var/log/integrate-code/webhook.log

# 查看自动部署日志
tail -f /var/log/integrate-code/auto-deploy.log
```

---

### 第六步: 完整流程测试

1. **本地修改代码**

```bash
# 创建一个新功能分支
git checkout -b feat/test-deploy

# 修改文件或创建新文件
echo "测试自动部署" > test-deploy.txt
git add test-deploy.txt

# 按照版本管理规范提交
git commit -m "feat(home): 添加测试部署文件"

# 推送到GitHub
git push origin feat/test-deploy
```

2. **在GitHub创建Pull Request**

3. **合并Pull Request到main分支**

4. **验证流程**
   - GitHub Actions自动同步到Gitee(约1-2分钟)
   - 云主机每5分钟检查一次更新(最多5分钟)
   - 自动部署开始:
     - 创建备份
     - 拉取代码
     - 更新依赖
     - 重启服务
     - 健康检查

5. **查看部署日志**

```bash
# 云主机上查看部署日志
tail -f /var/log/integrate-code/deploy.log
```

---

## 📋 检查清单

完成配置后,确认以下项目:

- [ ] Gitee SSH公钥已配置
- [ ] GitHub Secret `SSH_PRIVATE_KEY` 已添加
- [ ] GitHub Secret `GITEE_REPO` 值为 `liubin_studies/Home-page`
- [ ] 云主机 `webhook_receiver.py` 密钥已更新
- [ ] 云主机 `check_and_deploy.sh` 密钥已更新
- [ ] 云主机服务 `webhook-receiver` 正在运行
- [ ] 云主机定时任务已配置(crontab中)
- [ ] 测试提交已成功触发完整流程

---

## 🔍 故障排查

### GitHub Actions失败

1. 检查Secrets是否正确配置
2. 查看Actions日志获取详细错误信息
3. 确认SSH密钥格式正确(包含完整的BEGIN/END行)

### Gitee未同步

1. 检查Gitee SSH公钥是否正确添加
2. 确认Gitee仓库路径是否为 `liubin_studies/Home-page`
3. 手动测试SSH连接: `ssh -T git@gitee.com`

### 云主机未自动部署

1. 检查webhook服务状态: `systemctl status webhook-receiver`
2. 检查服务日志: `journalctl -u webhook-receiver -f`
3. 检查自动部署日志: `tail /var/log/integrate-code/auto-deploy.log`
4. 确认密钥配置一致(webhook_receiver.py 和 check_and_deploy.sh)

---

## 📚 相关文档

- [版本管理规范](VERSION_MANAGEMENT_GUIDE.md)
- [版本管理快速指南](QUICK_START_VERSIONING.md)
- [自动部署配置指南](AUTO_DEPLOY_SETUP.md)
- [CI/CD部署指南](CI_CD_DEPLOYMENT_GUIDE.md)

---

## 📞 技术支持

如遇问题,请查看:
1. 相关文档的"常见问题"章节
2. GitHub Actions日志
3. 云主机服务日志
4. 自动部署日志

---

**配置完成后,您就可以享受自动化的版本管理、代码同步和自动部署流程了!** 🎉
