# Git 远程仓库配置指南

## 概述

本项目已将 Git 远程仓库从 GitHub 迁移到 Gitee。

## 当前配置

```bash
# 查看远程仓库配置
git remote -v

# 输出示例:
origin  https://gitee.com/liubin_studies/Home-page.git (fetch)
origin  https://gitee.com/liubin_studies/Home-page.git (push)
```

## 配置说明

### 本地开发环境

**操作命令**:
```bash
# 修改远程仓库地址为 Gitee
git remote set-url origin https://gitee.com/liubin_studies/Home-page.git

# 验证配置
git remote -v
```

**常用操作**:
```bash
# 推送代码到 Gitee
git push origin main

# 拉取最新代码
git pull origin main

# 克隆仓库
git clone https://gitee.com/liubin_studies/Home-page.git
```

### 云主机环境

云主机的 `smart-pull.sh` 脚本会自动从 Gitee 拉取代码:

```bash
# 手动触发拉取
cd /opt/Home-page
bash ./scripts/smart-pull.sh

# 或使用自动检测脚本
bash ./scripts/check_and_deploy.sh
```

## 团队成员配置

### 新团队成员加入

1. **克隆仓库**
```bash
git clone https://gitee.com/liubin_studies/Home-page.git
cd Home-page
```

2. **配置个人信息**
```bash
git config user.name "您的名字"
git config user.email "您的邮箱"
```

3. **创建开发分支**
```bash
git checkout -b feat/your-feature
```

4. **开发并提交**
```bash
git add .
git commit -m "feat: 添加新功能"
git push origin feat/your-feature
```

5. **在 Gitee 创建 Pull Request**
   - 访问 Gitee 仓库
   - 点击 "合并请求"
   - 创建 PR 到 main 分支
   - 等待 CI/CD 检查通过后合并

### 现有团队成员更新

如果您之前使用的是 GitHub 远程仓库:

```bash
# 查看当前配置
git remote -v

# 如果显示的是 GitHub 地址,执行:
git remote set-url origin https://gitee.com/liubin_studies/Home-page.git

# 验证更新
git remote -v

# 拉取 Gitee 最新代码
git fetch origin
git checkout main
git pull origin main
```

## SSH 配置 (推荐)

为了更安全的推送,可以配置 SSH 密钥:

### 1. 生成 SSH 密钥

```bash
# 生成 ed25519 密钥 (推荐)
ssh-keygen -t ed25519 -C "your-email@example.com"

# 或使用 RSA 密钥
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

### 2. 查看公钥

```bash
cat ~/.ssh/id_ed25519.pub
# 或
cat ~/.ssh/id_rsa.pub
```

### 3. 添加到 Gitee

1. 登录 Gitee
2. 点击右上角头像 → **设置**
3. 左侧菜单选择 **SSH 公钥**
4. 点击 **添加公钥**
5. 粘贴公钥内容
6. 设置标题,例如: "开发环境 - Work PC"
7. 点击 **确定**

### 4. 测试连接

```bash
ssh -T git@gitee.com
```

如果看到类似输出,说明配置成功:
```
Hi username! You've successfully authenticated, but Gitee.com does not provide shell access.
```

### 5. 使用 SSH 地址

```bash
# 修改为 SSH 地址
git remote set-url origin git@gitee.com:liubin_studies/Home-page.git

# 验证
git remote -v
```

## 多远程仓库配置

如果需要同时推送/拉取多个仓库:

```bash
# 添加 GitHub 作为备用远程仓库
git remote add github https://github.com/liubin20020924-cloud/Home-page.git

# 查看所有远程仓库
git remote -v

# 推送到 Gitee
git push origin main

# 推送到 GitHub (如果需要)
git push github main

# 同时推送到两个仓库
git push origin main && git push github main
```

## 常见问题

### Q1: 推送时提示认证失败

**A**: 检查以下几点:
1. 确认 Gitee 账号密码正确
2. 如果使用 HTTPS,确认有推送权限
3. 如果使用 SSH,确认密钥已添加到 Gitee

### Q2: 拉取时提示冲突

**A**: 解决方法:
```bash
# 方法1: 保留本地修改
git pull origin main --rebase

# 方法2: 放弃本地修改
git reset --hard origin/main

# 方法3: 手动合并
git fetch origin
git merge origin/main
# 解决冲突后
git add .
git commit -m "merge: 解决合并冲突"
```

### Q3: 如何查看提交历史

**A**:
```bash
# 查看最近10次提交
git log --oneline -10

# 查看图形化历史
git log --graph --oneline --all

# 查看特定分支
git log origin/main --oneline -10
```

### Q4: 如何撤销提交

**A**:
```bash
# 撤销最后一次提交(保留修改)
git reset --soft HEAD~1

# 撤销最后一次提交(不保留修改)
git reset --hard HEAD~1

# 撤销已推送的提交(需谨慎)
git revert HEAD
git push origin main
```

## 最佳实践

### 1. 分支管理

```bash
# 功能分支
feat/feature-name

# 修复分支
fix/bug-name

# 热修复分支
hotfix/urgent-fix

# 开发分支
develop
```

### 2. 提交信息规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链相关

**示例**:
```bash
git commit -m "feat(auth): 添加用户登录功能"
git commit -m "fix(api): 修复工单查询接口错误"
git commit -m "docs(readme): 更新安装说明"
```

### 3. 工作流程

```bash
# 1. 创建功能分支
git checkout -b feat/new-feature

# 2. 开发并提交
git add .
git commit -m "feat: 添加新功能"

# 3. 推送到 Gitee
git push origin feat/new-feature

# 4. 在 Gitee 创建 PR
# 等待 CI/CD 检查通过

# 5. 合并后删除本地分支
git checkout main
git pull origin main
git branch -d feat/new-feature
```

## 相关文档

- [Gitee CI/CD 配置指南](./GITEE_CICD_SETUP.md)
- [Gitee 迁移报告](./MIGRATION_TO_GITEE.md)
- [版本管理规范](./VERSION_MANAGEMENT_GUIDE.md)
- [快速开始指南](./QUICK_START_VERSIONING.md)

---

配置完成时间: 2026-03-04
Gitee 仓库地址: https://gitee.com/liubin_studies/Home-page
