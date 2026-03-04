# CI/CD 流程快速参考

## 概述

新的 CI/CD 流程实现了从本地开发到生产部署的自动化：
```
本地开发 → GitHub 分支 → 创建 PR → 自动检查 → 合并到 main → 云主机自动部署
```

## 分支策略

| 分支类型 | 用途 | 触发 CI/CD | 自动部署 |
|---------|------|-----------|---------|
| `main` | 生产环境 | ✅ | ✅ (自动) |
| `develop` | 开发环境 | ✅ | ❌ |
| `feat/*` | 功能开发 | ✅ | ❌ |
| `fix/*` | Bug 修复 | ✅ | ❌ |
| `hotfix/*` | 紧急修复 | ✅ | ❌ |

## 工作流程

### 1. 本地开发

```bash
# 1. 从 develop 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feat/your-feature-name

# 2. 开发并提交
git add .
git commit -m "feat(api): 添加用户认证功能"

# 3. 推送到 GitHub
git push origin feat/your-feature-name
```

### 2. 创建 Pull Request

**方式 A: 通过 GitHub 网页界面**
1. 访问仓库页面，点击 "Pull requests" → "New pull request"
2. 选择源分支 `feat/your-feature-name`，目标分支 `main`
3. 添加标签 `auto-merge` (可选，推荐)
4. 提交 PR

**方式 B: 通过 GitHub Actions**
1. 进入仓库的 "Actions" 标签页
2. 选择 "Development Helper" 工作流
3. 点击 "Run workflow"
4. 填写参数：
   - `source_branch`: `feat/your-feature-name`
   - `target_branch`: `main`
   - `auto_merge`: `true`

### 3. CI/CD 自动检查

PR 创建后，GitHub Actions 会自动执行以下检查：

| 检查项 | 说明 | 耗时 |
|-------|------|------|
| 🧪 Run Tests | 运行单元测试 | ~2-3 分钟 |
| 🔍 Code Lint | 代码质量检查 | ~1 分钟 |
| 🔒 Security Check | 安全检查 | ~1 分钟 |

### 4. 自动合并

**自动合并条件：**
- ✅ 所有 CI/CD 检查通过
- ✅ PR 添加了 `auto-merge` 标签（或使用 GitHub CLI 自动合并）

**自动合并方式：**
- **方式 1 (推荐)**: PR 添加 `auto-merge` 标签，检查通过后自动合并
- **方式 2**: 使用 GitHub CLI 直接合并（不依赖标签）

### 5. 云主机自动部署

main 分支更新后，触发部署流程：

```
GitHub Actions → Webhook 通知云主机 → 执行部署脚本 → 应用更新
```

**部署过程：**
1. 创建当前版本备份
2. 拉取最新代码
3. 更新依赖
4. 重启应用服务
5. 记录部署信息

## 提交规范

使用 Conventional Commits 格式：

```bash
# 功能开发
git commit -m "feat(api): 添加用户认证功能"

# Bug 修复
git commit -m "fix(kb): 修复搜索结果排序错误"

# 文档更新
git commit -m "docs: 更新部署文档"

# 重构
git commit -m "refactor(db): 优化数据库连接池"

# 性能优化
git commit -m "perf(ui): 减少首屏加载时间"
```

**提交格式：**
```
<type>(<scope>): <subject>

<body>

<footer>
```

- **type**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`
- **scope**: 模块名称（api, kb, case, home, auth, db, ui, deploy 等）

## 版本号规范

遵循语义化版本 (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR**: 不兼容的 API 修改
- **MINOR**: 向下兼容的功能性新增
- **PATCH**: 向下兼容的问题修正

**发布版本时：**
```bash
# 更新版本号
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 回滚操作

如果部署出现问题，快速回滚：

```bash
# SSH 登录云主机
ssh user@your-server

# 执行回滚脚本
cd /opt/Home-page
./scripts/rollback.sh
```

## 监控部署

**查看部署状态：**
1. **GitHub Actions**: 进入仓库的 "Actions" 标签页
2. **云主机 Webhook**: 访问 `http://your-server:9000/webhook/health`
3. **部署日志**: SSH 登录云主机，查看 `/var/log/integrate-code/deploy.log`

**查看版本信息：**
```bash
curl http://your-server:9000/webhook/version
```

**查看部署日志：**
```bash
curl http://your-server:9000/webhook/logs
```

## 常见问题

### Q: PR 检查失败怎么办？
A:
1. 查看失败的检查项日志
2. 在本地修复问题
3. 提交新的 commit，PR 会自动重新触发检查

### Q: 如何跳过某些检查？
A: 不建议跳过检查。如果必须，可以在 commit message 中添加 `[skip ci]`：
```bash
git commit -m "chore: 更新配置 [skip ci]"
```

### Q: 如何取消自动合并？
A: 从 PR 中移除 `auto-merge` 标签

### Q: 多个 PR 同时提交到 main 会怎样？
A: GitHub Actions 会按顺序处理，避免并发冲突

### Q: 云主机没有收到部署通知？
A:
1. 检查 GitHub Secrets 中是否配置了 `WEBHOOK_URL`
2. 检查云主机防火墙是否开放 9000 端口
3. 检查 webhook 服务是否正常运行：`systemctl status webhook-receiver`

## GitHub Secrets 配置

需要在 GitHub 仓库中配置以下 Secrets：

| Secret 名称 | 说明 | 示例 |
|-----------|------|------|
| `WEBHOOK_URL` | 云主机 webhook 地址 | `http://your-server:9000` |
| `WEBHOOK_SECRET` | Webhook 验证密钥 | 随机生成的字符串 |

**配置步骤：**
1. 进入仓库页面
2. Settings → Secrets and variables → Actions
3. 点击 "New repository secret"
4. 添加上述 Secrets

## 云主机配置

确保云主机已配置：

1. **Webhook 服务** (已安装):
   ```bash
   systemctl status webhook-receiver
   ```

2. **防火墙规则**:
   ```bash
   # 开放 9000 端口
   firewall-cmd --permanent --add-port=9000/tcp
   firewall-cmd --reload
   ```

3. **部署脚本权限**:
   ```bash
   chmod +x /opt/Home-page/scripts/deploy.sh
   chmod +x /opt/Home-page/scripts/rollback.sh
   ```

## 快速命令参考

```bash
# 本地开发
git checkout develop && git pull origin develop
git checkout -b feat/new-feature
git add . && git commit -m "feat: 添加新功能"
git push origin feat/new-feature

# 创建 PR (使用 GitHub CLI)
gh pr create --base main --title "添加新功能" --body "PR 描述"

# 查看部署状态
gh run list --branch main

# 手动触发部署 (SSH 云主机)
ssh user@server "cd /opt/Home-page && ./scripts/deploy.sh"

# 回滚 (SSH 云主机)
ssh user@server "cd /opt/Home-page && ./scripts/rollback.sh"
```

---

**文档版本**: v1.0
**更新时间**: 2026-03-04
