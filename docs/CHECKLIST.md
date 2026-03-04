# 自动部署配置检查清单

> 云户科技网站 - 自动部署系统配置进度追踪

---

## 仓库信息

- GitHub: https://github.com/liubin20020924-cloud/Home-page.git
- Gitee: https://gitee.com/liubin_studies/Home-page.git

---

## GitHub 配置

- [ ] 生成SSH密钥对
  ```bash
  ssh-keygen -t rsa -b 4096 -C "github-gitee-sync" -f ~/.ssh/github_gitee_rsa
  ```

- [ ] 复制私钥内容到GitHub Secret `SSH_PRIVATE_KEY`
  ```bash
  cat ~/.ssh/github_gitee_rsa
  ```

- [ ] 复制公钥内容到Gitee SSH公钥
  ```bash
  cat ~/.ssh/github_gitee_rsa.pub
  ```

- [ ] GitHub仓库配置Secrets
  - [ ] `SSH_PRIVATE_KEY`: 已添加私钥完整内容
  - [ ] `GITEE_REPO`: 值为 `liubin_studies/Home-page`

- [ ] 测试GitHub Actions同步
  - [ ] 推送测试提交到GitHub
  - [ ] 验证Actions工作流成功
  - [ ] 确认Gitee仓库已同步

---

## Gitee 配置

- [ ] 登录Gitee
- [ ] 进入个人设置 → SSH公钥
- [ ] 添加GitHub同步的SSH公钥
- [ ] 标题填写: `GitHub Sync Key`
- [ ] 测试SSH连接: `ssh -T git@gitee.com`

---

## 云主机配置

### 准备工作

- [ ] 确认云主机操作系统为Linux
- [ ] 确认已安装Git: `git --version`
- [ ] 确认已安装Python3: `python3 --version`
- [ ] 确认已安装pip: `pip3 --version`

### Webhook密钥配置

- [ ] 生成Webhook密钥
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- [ ] 编辑webhook接收器密钥
  ```bash
  nano /opt/integrate-code/scripts/webhook_receiver.py
  # 替换: WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '生成的密钥')
  ```

- [ ] 编辑自动检测脚本密钥
  ```bash
  nano /opt/integrate-code/scripts/check_and_deploy.sh
  # 替换: WEBHOOK_SECRET="生成的密钥"
  ```

### 服务安装

- [ ] 运行一键安装脚本
  ```bash
  bash /opt/integrate-code/scripts/deploy_service.sh
  ```

### 验证服务

- [ ] webhook-receiver服务运行中
  ```bash
  systemctl status webhook-receiver
  ```

- [ ] 定时任务已配置
  ```bash
  crontab -l
  # 应该看到: */5 * * * * /opt/integrate-code/scripts/check_and_deploy.sh
  ```

- [ ] 防火墙规则已添加
  ```bash
  firewall-cmd --list-ports
  # 应该包含: 9000/tcp
  ```

### 日志验证

- [ ] 查看webhook日志
  ```bash
  tail -f /var/log/integrate-code/webhook.log
  ```

- [ ] 查看自动部署日志
  ```bash
  tail -f /var/log/integrate-code/auto-deploy.log
  ```

- [ ] 查看部署日志
  ```bash
  tail -f /var/log/integrate-code/deploy.log
  ```

---

## 完整流程测试

### 1. GitHub → Gitee 同步测试

- [ ] 创建测试分支: `git checkout -b feat/test-deploy`
- [ ] 提交测试代码
- [ ] 推送到GitHub: `git push origin feat/test-deploy`
- [ ] 创建Pull Request
- [ ] 合并到main分支
- [ ] 验证GitHub Actions成功
- [ ] 验证Gitee已同步

### 2. Gitee → 云主机 部署测试

- [ ] 等待最多5分钟(定时检查周期)
- [ ] 查看自动部署日志确认触发
- [ ] 查看部署日志确认完成
- [ ] 验证应用正常运行
- [ ] 检查备份目录: `/opt/integrate-code/backups/`

### 3. 回滚测试(可选)

- [ ] 运行回滚脚本
  ```bash
  bash /opt/integrate-code/scripts/rollback.sh
  ```
- [ ] 选择要恢复的备份版本
- [ ] 验证回滚成功

---

## 配置完成检查

### 基础配置

- [ ] GitHub仓库可访问
- [ ] Gitee仓库可访问
- [ ] SSH密钥已配置
- [ ] GitHub Secrets已添加
- [ ] Gitee SSH公钥已添加

### 自动同步

- [ ] GitHub Actions工作流运行正常
- [ ] 代码可自动同步到Gitee
- [ ] 提交信息格式正确

### 自动部署

- [ ] webhook-receiver服务运行正常
- [ ] 定时任务正常执行
- [ ] 自动检测到更新
- [ ] 自动部署成功
- [ ] 应用正常重启

### 监控和日志

- [ ] 服务日志正常输出
- [ ] 部署日志正常记录
- [ ] 自动部署日志正常记录
- [ ] 备份文件正常创建

---

## 常见问题检查

### GitHub Actions失败

- [ ] SSH_PRIVATE_KEY格式正确(包含BEGIN/END行)
- [ ] GITEE_REPO值为 `liubin_studies/Home-page`
- [ ] SSH密钥无密码保护
- [ ] Gitee SSH公钥正确添加

### Gitee同步失败

- [ ] SSH连接测试通过
- [ ] Gitee仓库存在且可访问
- [ ] 分支名称为main

### 云主机部署失败

- [ ] webhook服务运行正常
- [ ] Webhook密钥配置一致
- [ ] 端口9000未被占用
- [ ] 防火墙规则已添加
- [ ] Git仓库配置正确

---

## 配置完成确认

当以上所有项目都完成后,您的自动部署系统就完全配置好了!

**完成标志**:
- [ ] ✅ GitHub提交 → 自动同步到Gitee
- [ ] ✅ Gitee更新 → 云主机自动检测(5分钟内)
- [ ] ✅ 云主机自动部署 → 应用自动重启
- [ ] ✅ 部署失败 → 自动回滚
- [ ] ✅ 完整日志记录

---

## 日常使用流程

配置完成后,日常开发流程:

1. **本地开发**
   ```bash
   git checkout -b feat/your-feature
   # 编写代码
   git commit -m "feat(home: 添加新功能"
   git push origin feat/your-feature
   ```

2. **合并到main**
   - 在GitHub创建Pull Request
   - 代码审查
   - 合并到main分支

3. **自动部署**
   - GitHub Actions自动同步到Gitee(1-2分钟)
   - 云主机自动检测并部署(最多5分钟)
   - 应用自动更新上线

---

## 相关文档

- [仓库配置快速指南](./REPO_CONFIG_GUIDE.md)
- [版本管理规范](./VERSION_MANAGEMENT_GUIDE.md)
- [版本管理快速指南](./QUICK_START_VERSIONING.md)
- [自动部署配置](./AUTO_DEPLOY_SETUP.md)
- [CI/CD部署指南](./CI_CD_DEPLOYMENT_GUIDE.md)

---

**祝您配置顺利!** 🚀
