# 云户科技网站 - 版本管理规范

> 本文档定义完整的版本管理流程，包括 Git 工作流、提交规范、分支策略和自动部署

---

## 📋 目录

1. [版本号规范](#版本号规范)
2. [Git 提交规范](#git-提交规范)
3. [分支管理规范](#分支管理规范)
4. [版本发布流程](#版本发布流程)
5. [变更日志管理](#变更日志管理)
6. [代码同步流程](#代码同步流程)

---

## 版本号规范

### 版本号格式

采用 **语义化版本控制** (Semantic Versioning 2.0.0)

```
主版本号.次版本号.修订号 (MAJOR.MINOR.PATCH)
```

示例: `1.2.3`

- **主版本号 (MAJOR)**: 不兼容的 API 修改
- **次版本号 (MINOR)**: 向下兼容的功能性新增
- **修订号 (PATCH)**: 向下兼容的问题修正

### 版本号示例

| 版本号 | 说明 |
|--------|------|
| `1.0.0` | 首次正式发布 |
| `1.0.1` | 修复 Bug |
| `1.1.0` | 新增功能 |
| `2.0.0` | 重大更新（不兼容变更） |

### 预发布版本号

对于开发中的版本，可以使用预发布标识：

```
主版本号.次版本号.修订号-预发布标识.预发布版本号
```

示例: `1.2.3-beta.1`, `1.2.3-rc.2`

预发布标识：
- `alpha`: 内部测试版本
- `beta`: 公开测试版本
- `rc`: 发布候选版本 (Release Candidate)

---

## Git 提交规范

### 提交信息格式

采用 [Conventional Commits](https://www.conventionalcommits.org/) 规范

```
<类型>(<范围>): <简短描述>

<详细描述>

<关联信息>
```

### 提交类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(case): 添加工单满意度评价功能` |
| `fix` | 修复 Bug | `fix(auth): 修复登录后session过期问题` |
| `docs` | 文档更新 | `docs: 更新API文档` |
| `style` | 代码格式调整 | `style: 统一代码缩进` |
| `refactor` | 重构 | `refactor(db): 优化数据库连接池` |
| `perf` | 性能优化 | `perf(api): 优化查询速度` |
| `test` | 测试相关 | `test(auth): 添加登录测试用例` |
| `chore` | 构建/工具更新 | `chore: 更新依赖包` |
| `revert` | 回滚提交 | `revert: 回滚 feat(case)` |

### 提交范围

| 范围 | 说明 |
|------|------|
| `home` | 官网系统 |
| `kb` | 知识库系统 |
| `case` | 工单系统 |
| `auth` | 认证模块 |
| `db` | 数据库 |
| `api` | API 接口 |
| `ui` | 用户界面 |
| `deploy` | 部署脚本 |
| `config` | 配置文件 |

### 提交示例

#### 简单提交
```
feat(case): 添加工单满意度评价功能
```

#### 完整提交
```
feat(case): 添加工单满意度评价功能

- 新增 satisfaction 数据表
- 添加满意度评价 API 接口
- 工单详情页显示评价入口
- 管理员报表新增满意度统计

Closes #123
```

#### 修复 Bug
```
fix(auth): 修复登录后session过期问题

问题描述：
- 用户登录成功后，session 有效期设置为 1 小时
- 但配置文件中设置为 3 小时
- 导致用户频繁需要重新登录

解决方案：
- 修改 session.permanent 设置逻辑
- 统一使用配置文件中的 SESSION_TIMEOUT

Fixes #456
```

#### 文档更新
```
docs: 更新部署文档

- 添加云主机自动部署说明
- 补充故障排查章节
- 更新环境变量配置示例
```

### 提交规范检查清单

提交代码前，确保提交信息：

- [ ] 使用规范的提交类型
- [ ] 简短描述不超过 50 个字符
- [ ] 简短描述使用祈使句（如 "添加" 而非 "添加了"）
- [ ] 详细描述（如果需要）说明变更原因和影响
- [ ] 关联相关 Issue 或 PR

---

## 分支管理规范

### 分支策略

#### 主要分支

| 分支 | 用途 | 说明 |
|------|------|------|
| `main` | 生产环境 | 稳定版本，只接受经过审核的合并 |
| `develop` | 开发主分支 | 集成各功能分支，准备发布到 main |
| `v1.2.x` | 版本维护分支 | 修复特定版本的 Bug |

#### 辅助分支

| 分支类型 | 命名格式 | 用途 | 合并目标 |
|---------|---------|------|---------|
| 功能分支 | `feat/<功能名>` | 开发新功能 | `develop` |
| 修复分支 | `fix/<问题描述>` | 修复 Bug | `develop` |
| 热修复分支 | `hotfix/<问题描述>` | 紧急修复生产问题 | `main` 和 `develop` |
| 重构分支 | `refactor/<模块名>` | 代码重构 | `develop` |
| 文档分支 | `docs/<文档名>` | 文档更新 | `develop` |

### 分支命名示例

```
feat/case-satisfaction
fix/auth-session-timeout
hotfix/database-connection
refactor/user-auth
docs/api-documentation
```

### 分支生命周期

#### 功能分支工作流

```
develop
    ↓ (创建)
feat/case-satisfaction
    ↓ (开发测试)
    ↓ (Pull Request)
develop
    ↓ (合并发布)
main
```

#### 热修复分支工作流

```
main
    ↓ (创建)
hotfix/critical-bug
    ↓ (开发测试)
    ↓ (Pull Request)
main  ← 1. 同时合并
    ↓ (反向合并)
develop
```

### 分支保护规则

#### main 分支保护

```yaml
保护规则:
  要求 Pull Request: ✅
  要求状态检查: ✅
    - CI 测试通过
    - 代码规范检查通过
  要求审核: ✅
    - 至少 1 个审核批准
  限制推送:
    - 管理员可以强制推送（禁止直接推送）
```

#### develop 分支保护

```yaml
保护规则:
  要求 Pull Request: ✅
  要求状态检查: ✅
  限制推送:
    - 指定开发者可以推送
```

### 分支操作规范

#### 创建分支

```bash
# 从 develop 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feat/case-satisfaction

# 从 main 创建热修复分支
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug
```

#### 合并分支

```bash
# 合并功能分支到 develop
git checkout develop
git merge feat/case-satisfaction

# 合并热修复分支到 main 和 develop
git checkout main
git merge hotfix/critical-bug
git checkout develop
git merge hotfix/critical-bug
```

#### 删除分支

```bash
# 删除已合并的本地分支
git branch -d feat/case-satisfaction

# 删除远程分支
git push origin --delete feat/case-satisfaction
```

---

## 版本发布流程

### 发布周期

| 版本类型 | 发布周期 | 说明 |
|---------|---------|------|
| 大版本 (x.0.0) | 按需发布 | 重大架构变更 |
| 中版本 (x.y.0) | 每月/每季度 | 新功能发布 |
| 小版本 (x.y.z) | 每周/双周 | Bug 修复 |
| 热修复 | 随时发布 | 紧急问题修复 |

### 发布步骤

#### 1. 准备发布

```bash
# 1. 切换到 develop
git checkout develop
git pull origin develop

# 2. 更新版本号
# 编辑 config.py 或 __init__.py
# VERSION = "1.2.3"

# 3. 运行完整测试
pytest
```

#### 2. 创建发布分支

```bash
# 创建发布分支
git checkout -b release/1.2.3

# 更新 CHANGELOG.md
# 添加本次版本的所有变更

# 提交版本变更
git add .
git commit -m "chore(release): 准备发布 1.2.3"
```

#### 3. 合并到 main

```bash
# 合并到 main
git checkout main
git merge release/1.2.3

# 打标签
git tag -a v1.2.3 -m "Release version 1.2.3"

# 推送到远程
git push origin main
git push origin v1.2.3
```

#### 4. 合并回 develop

```bash
# 合并回 develop（保持同步）
git checkout develop
git merge release/1.2.3

# 推送到远程
git push origin develop
```

#### 5. 清理分支

```bash
# 删除发布分支
git branch -d release/1.2.3
git push origin --delete release/1.2.3
```

#### 6. GitHub Release

```bash
# 在 GitHub 上创建 Release
# - 选择标签 v1.2.3
# - 填写发布说明（从 CHANGELOG.md 复制）
# - 发布
```

---

## 变更日志管理

### CHANGELOG.md 格式

```markdown
# 更新日志 (CHANGELOG)

本文档记录所有项目的重大变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增 (Added)
- 待添加的功能

### 变更 (Changed)
- 待变更的功能

### 废弃 (Deprecated)
- 待废弃的功能

### 移除 (Removed)
- 待移除的功能

### 修复 (Fixed)
- 待修复的问题

### 安全 (Security)
- 待修复的安全问题

---

## [1.2.3] - 2026-03-04

### 新增 (Added)
- 工单系统新增满意度评价功能
- 添加用户头像上传功能
- 知识库支持全文搜索

### 变更 (Changed)
- 优化登录页面UI
- 调整数据库连接池配置

### 修复 (Fixed)
- 修复工单详情页无法显示附件的问题
- 修复 session 过期导致的登录异常
- 修复邮件通知发送失败的问题

### 安全 (Security)
- 升级 Flask 到 3.0.3 修复安全漏洞

---

## [1.2.2] - 2026-02-20

### 新增 (Added)
- 添加工单统计报表功能
- 支持工单批量操作

### 修复 (Fixed)
- 修复用户注册时的验证错误
```

### 更新 CHANGELOG

#### 自动生成 CHANGELOG

```bash
# 使用 git-changelog 工具
pip install git-changelog

# 生成变更日志
git-changelog -o CHANGELOG.md
```

#### 手动更新

每次发布时，手动更新 CHANGELOG.md：

1. 将 `[未发布]` 的内容移到新版本
2. 添加新版本号和发布日期
3. 清空 `[未发布]` 部分
4. 提交变更

---

## 代码同步流程

### 完整工作流

```
本地开发
    ↓ git push
GitHub (2.2 分支)
    ↓ Pull Request
GitHub (main 分支)
    ↓ GitHub Action
Gitee (main 分支)
    ↓ 云主机检测
云主机自动部署
```

### GitHub → Gitee 同步

#### 方案 1: GitHub Action 自动同步（推荐）

**配置文件**: `.github/workflows/sync-to-gitee.yml`

```yaml
name: Sync to Gitee

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Sync to Gitee
        uses: wearerequired/git-mirror-action@master
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
        with:
          source-repo: "git@github.com:your-username/integrate-code.git"
          destination-repo: "git@gitee.com:your-username/integrate-code.git"
```

#### 方案 2: 手动同步

```bash
# 添加 Gitee 远程仓库
git remote add gitee https://gitee.com/your-username/integrate-code.git

# 推送到 Gitee
git push gitee main
```

### 云主机自动部署

#### 自动检测机制

云主机通过 cron 定时任务检测 Gitee 更新：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每5分钟检查一次）
*/5 * * * * /opt/integrate-code/scripts/check_and_deploy.sh >> /var/log/integrate-code/auto-deploy.log 2>&1
```

**检测脚本**: `scripts/check_and_deploy.sh`

```bash
#!/bin/bash

# 云户科技网站 - 自动检测并部署脚本
# 定时检查 Gitee 更新，自动触发部署

set -e

# 配置
PROJECT_DIR="/opt/integrate-code"
LOG_FILE="/var/log/integrate-code/auto-deploy.log"
WEBHOOK_URL="http://localhost:9000/webhook/gitee"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_info() {
    echo "[INFO] $1" | tee -a "$LOG_FILE"
    log "INFO: $1"
}

# 检查远程更新
check_updates() {
    cd "$PROJECT_DIR"
    
    # 获取本地最新提交
    LOCAL_COMMIT=$(git rev-parse HEAD)
    
    # 获取远程最新提交
    git fetch origin main
    REMOTE_COMMIT=$(git rev-parse origin/main)
    
    # 比较提交
    if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
        log_info "检测到新版本"
        log_info "本地: $LOCAL_COMMIT"
        log_info "远程: $REMOTE_COMMIT"
        return 0  # 有更新
    else
        log_info "已是最新版本"
        return 1  # 无更新
    fi
}

# 触发部署
trigger_deployment() {
    log_info "触发部署..."
    
    # 调用 Webhook 触发部署
    RESPONSE=$(curl -s -X POST "$WEBHOOK_URL" \
        -H "X-Gitee-Token: ${WEBHOOK_SECRET}" \
        -H "Content-Type: application/json" \
        -d '{"ref": "refs/heads/main"}')
    
    if echo "$RESPONSE" | grep -q "Deployment started"; then
        log_info "部署已触发"
        return 0
    else
        log_info "部署触发失败: $RESPONSE"
        return 1
    fi
}

# 主流程
main() {
    log_info "=========================================="
    log_info "开始检查更新..."
    log_info "=========================================="
    
    # 检查更新
    if check_updates; then
        # 有更新，触发部署
        trigger_deployment
    fi
    
    log_info "检查完成"
}

# 执行
main
```

### 云主机服务配置

#### Webhook 接收器服务

**systemd 服务文件**: `/etc/systemd/system/webhook-receiver.service`

```ini
[Unit]
Description=CloudDoors Webhook Receiver
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/integrate-code
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="WEBHOOK_SECRET=your-webhook-secret-here"
ExecStart=/usr/bin/python3 /opt/integrate-code/scripts/webhook_receiver.py
Restart=always
RestartSec=10

# 日志
StandardOutput=append:/var/log/integrate-code/webhook.log
StandardError=append:/var/log/integrate-code/webhook-error.log

[Install]
WantedBy=multi-user.target
```

**启用服务**:

```bash
# 重新加载 systemd
systemctl daemon-reload

# 启用服务
systemctl enable webhook-receiver

# 启动服务
systemctl start webhook-receiver

# 查看状态
systemctl status webhook-receiver
```

---

## 最佳实践

### 代码提交前

- [ ] 本地测试通过
- [ ] 代码格式化完成
- [ ] 提交信息符合规范
- [ ] 关联相关 Issue
- [ ] 更新相关文档

### 合并代码前

- [ ] Pull Request 审核通过
- [ ] CI 测试全部通过
- [ ] 代码规范检查通过
- [ ] 无合并冲突

### 发布前

- [ ] 版本号更新正确
- [ ] CHANGELOG.md 已更新
- [ ] 完整测试通过
- [ ] 备份已完成
- [ ] 回滚方案已准备

### 部署后

- [ ] 健康检查通过
- [ ] 监控日志无异常
- [ ] 关键功能测试正常
- [ ] 用户反馈收集

---

## 常见问题

### Q1: 如何回滚已发布的版本？

```bash
# 查看标签
git tag -l

# 回滚到指定标签
git checkout v1.2.2

# 或使用 git reset
git reset --hard v1.2.2
```

### Q2: 如何处理合并冲突？

```bash
# 合并时遇到冲突
git merge feature/xxx

# 查看冲突文件
git status

# 手动解决冲突后
git add .
git commit -m "fix: 解决合并冲突"
```

### Q3: 如何撤销已推送的提交？

```bash
# 撤销最后一次提交（保留更改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃更改）
git reset --hard HEAD~1

# 强制推送（慎用）
git push origin main --force
```

### Q4: 如何查看提交历史？

```bash
# 查看提交历史
git log --oneline

# 查看图形化历史
git log --graph --oneline --all

# 查看指定文件的变更
git log -p -- app.py
```

---

## 附录

### A. Git 常用命令

```bash
# 克隆仓库
git clone <repository-url>

# 查看状态
git status

# 添加文件
git add .
git add <file>

# 提交
git commit -m "message"

# 推送
git push origin <branch>

# 拉取
git pull origin <branch>

# 创建分支
git checkout -b <branch>

# 切换分支
git checkout <branch>

# 合并分支
git merge <branch>

# 删除分支
git branch -d <branch>

# 查看日志
git log
git log --oneline

# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add <name> <url>
```

### B. 版本号变更记录

| 版本号 | 日期 | 说明 |
|--------|------|------|
| 1.0.0 | 2026-03-02 | 首次正式发布 |

---

**文档版本**: v1.0  
**最后更新**: 2026-03-04  
**维护者**: DevOps Team
