# GitHub Actions 同步故障排查指南

> 解决 "Sync to Gitee" 工作流失败问题 (Exit Code 128)

---

## 🚨 常见错误: Exit Code 128

Exit Code 128 通常是 Git 权限或配置问题。

---

## 🔍 排查步骤

### 1. 检查 GitHub Secrets 配置

访问：https://github.com/liubin20020924-cloud/Home-page/settings/secrets/actions

#### 检查 SSH_PRIVATE_KEY

**问题**: 私钥格式不正确

**解决方法**:

1. 确保私钥包含完整的BEGIN和END行：

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtc...
[完整的私钥内容]
-----END OPENSSH PRIVATE KEY-----
```

2. **不要**复制以下任何额外内容：
   - ❌ "-----BEGIN RSA PRIVATE KEY-----" (错误的格式)
   - ❌ 任何注释或说明文字
   - ❌ 引号或换行符

3. 重新生成密钥（如果需要）：

```bash
# 生成新的SSH密钥对
ssh-keygen -t rsa -b 4096 -C "github-gitee-sync" -f ~/.ssh/github_gitee_rsa -N ""

# 查看私钥（复制完整内容，包括BEGIN和END行）
cat ~/.ssh/github_gitee_rsa

# 查看公钥（配置到Gitee）
cat ~/.ssh/github_gitee_rsa.pub
```

#### 检查 GITEE_REPO

**问题**: 仓库路径错误

**正确值**:
```
liubin_studies/Home-page
```

**错误示例**:
- ❌ `https://gitee.com/liubin_studies/Home-page.git` (包含协议)
- ❌ `git@gitee.com:liubin_studies/Home-page.git` (包含服务器地址)
- ❌ `liubin_studies/Home-page.git` (包含.git后缀)

---

### 2. 检查 Gitee SSH 公钥配置

访问：https://gitee.com/profile/sshkeys

#### 检查公钥是否正确添加

1. 查看已添加的公钥列表
2. 确认有标题为 `GitHub Sync Key` 的公钥
3. 删除旧的公钥（如果存在）
4. 重新添加新的公钥：

```bash
# 复制公钥内容
cat ~/.ssh/github_gitee_rsa.pub
```

**粘贴到Gitee时**:
- 标题: `GitHub Sync Key`
- 公钥内容: 完整复制 `cat ~/.ssh/github_gitee_rsa.pub` 的输出
- 类型: 选择 "部署密钥" 或 "SSH公钥"

---

### 3. 测试 SSH 连接

在本地测试SSH连接是否正常：

```bash
# 测试连接到Gitee
ssh -T git@gitee.com
```

**期望输出**:
```
Hi liubin_studies! You've successfully authenticated, but Gitee does not provide shell access.
```

**如果连接失败**:
```
Permission denied (publickey)
```

这表示SSH公钥未正确配置。

---

### 4. 查看 GitHub Actions 日志

访问：https://github.com/liubin20020924-cloud/Home-page/actions

点击最新的 "Sync to Gitee" 工作流，查看详细日志：

#### 错误信息分析

**错误1**: `Permission denied (publickey)`
- **原因**: SSH密钥配置错误
- **解决**: 重新检查SSH_PRIVATE_KEY和Gitee公钥

**错误2**: `fatal: repository 'git@gitee.com:liubin_studies/Home-page.git' not found`
- **原因**: GITEE_REPO路径错误
- **解决**: 修改为 `liubin_studies/Home-page`

**错误3**: `Could not read from remote repository`
- **原因**: 仓库不存在或无访问权限
- **解决**: 确认Gitee仓库存在且公开

---

## 🔧 常见问题解决方案

### 问题1: 私钥带有密码保护

**错误**: `Enter passphrase for key '/home/runner/.ssh/github_gitee_rsa':`

**解决**: 生成无密码的SSH密钥

```bash
# 生成无密码的密钥（使用 -N "" 参数）
ssh-keygen -t rsa -b 4096 -C "github-gitee-sync" -f ~/.ssh/github_gitee_rsa -N ""

# 重新配置
# 1. 复制新的私钥到GitHub Secret: SSH_PRIVATE_KEY
cat ~/.ssh/github_gitee_rsa

# 2. 复制新的公钥到Gitee
cat ~/.ssh/github_gitee_rsa.pub
```

---

### 问题2: 使用了错误的密钥格式

**错误**: GitHub Actions使用RSA密钥而非OpenSSH格式

**解决**: 确保使用OpenSSH格式

```bash
# 生成OpenSSH格式的密钥
ssh-keygen -t rsa -b 4096 -C "github-gitee-sync" -f ~/.ssh/github_gitee_rsa -N "" -m PEM

# 或者使用ed25519（更安全）
ssh-keygen -t ed25519 -C "github-gitee-sync" -f ~/.ssh/github_gitee_rsa -N ""
```

---

### 问题3: Gitee仓库权限问题

**错误**: `fatal: could not read Username`

**解决**: 确保使用SSH而非HTTPS

1. 在Gitee仓库设置中启用SSH访问
2. 确认仓库权限为公开或有写权限

---

## 📝 完整重新配置流程

如果以上步骤都无法解决，请按照以下流程重新配置：

### 步骤1: 删除旧的GitHub Secrets

1. 访问：https://github.com/liubin20020924-cloud/Home-page/settings/secrets/actions
2. 删除 `SSH_PRIVATE_KEY` 和 `GITEE_REPO`

### 步骤2: 删除旧的Gitee SSH公钥

1. 访问：https://gitee.com/profile/sshkeys
2. 删除旧的SSH公钥

### 步骤3: 生成新的SSH密钥

```bash
# 删除旧密钥
rm -f ~/.ssh/github_gitee_rsa ~/.ssh/github_gitee_rsa.pub

# 生成新密钥（无密码，OpenSSH格式）
ssh-keygen -t rsa -b 4096 -C "github-gitee-sync" -f ~/.ssh/github_gitee_rsa -N ""

# 查看私钥（复制完整内容）
cat ~/.ssh/github_gitee_rsa

# 查看公钥（复制完整内容）
cat ~/.ssh/github_gitee_rsa.pub
```

### 步骤4: 配置GitHub Secrets

访问：https://github.com/liubin20020924-cloud/Home-page/settings/secrets/actions

**添加 SSH_PRIVATE_KEY**:
- Name: `SSH_PRIVATE_KEY`
- Value: 粘贴 `cat ~/.ssh/github_gitee_rsa` 的完整输出（包括BEGIN和END行）

**添加 GITEE_REPO**:
- Name: `GITEE_REPO`
- Value: `liubin_studies/Home-page`

### 步骤5: 配置Gitee SSH公钥

访问：https://gitee.com/profile/sshkeys

**添加SSH公钥**:
- 标题: `GitHub Sync Key`
- 公钥内容: 粘贴 `cat ~/.ssh/github_gitee_rsa.pub` 的完整输出

### 步骤6: 测试

```bash
# 测试SSH连接
ssh -T git@gitee.com

# 应该看到: Hi liubin_studies! You've successfully authenticated...
```

### 步骤7: 触发GitHub Actions

推送任意代码到GitHub，查看Actions是否成功。

---

## 🧪 手动测试同步

在本地手动测试同步到Gitee：

```bash
# 添加Gitee远程仓库
git remote add gitee git@gitee.com:liubin_studies/Home-page.git

# 测试推送到Gitee
git push gitee main:main
```

如果本地推送成功，说明SSH配置正确，问题可能在GitHub Actions。

---

## 📞 获取帮助

如果以上方法都无法解决问题：

1. **查看GitHub Actions详细日志**
   - 访问工作流页面
   - 点击失败的步骤
   - 复制完整错误信息

2. **检查仓库设置**
   - 确认Gitee仓库存在
   - 确认仓库是公开的

3. **参考官方文档**
   - [GitHub Actions文档](https://docs.github.com/en/actions)
   - [Gitee SSH文档](https://gitee.com/help/articles/4181)

---

## ✅ 成功标志

当配置正确时，您应该看到：

```
✅ 测试SSH连接到Gitee...
Hi liubin_studies! You've successfully authenticated...

Gitee仓库路径: liubin_studies/Home-page

当前远程仓库:
origin    https://github.com/liubin20020924-cloud/Home-page.git (fetch)
gitee     git@gitee.com:liubin_studies/Home-page.git (push)

开始推送到Gitee...
To gitee.com:liubin_studies/Home-page.git
   xxx..yyy  main -> main

✅ 代码已成功同步到 Gitee
```

---

**建议**: 按照上述流程仔细检查每个步骤，特别注意SSH密钥的格式和完整性！
