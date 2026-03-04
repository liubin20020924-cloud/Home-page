# 版本管理快速指南

> 快速开始使用版本管理规范

---

## 🚀 快速开始

### 1. 本地开发流程

```bash
# 1. 切换到开发分支
git checkout develop

# 2. 创建功能分支
git checkout -b feat/your-feature-name

# 3. 开发代码...

# 4. 提交代码（遵循提交规范）
git add .
git commit -m "feat(case): 添加新功能"

# 5. 推送到 GitHub
git push origin feat/your-feature-name
```

### 2. 创建 Pull Request

1. 在 GitHub 上创建 Pull Request
2. 从 `feat/your-feature-name` 合并到 `develop`
3. 填写 PR 描述：
   - 变更说明
   - 关联 Issue
   - 测试情况

### 3. 合并到 main

1. PR 审核通过后合并到 `develop`
2. 定期从 `develop` 创建 Release 到 `main`

### 4. 自动部署

- 代码合并到 `main` 后自动触发 GitHub Action
- GitHub Action 自动同步到 Gitee
- 云主机检测更新后自动部署

---

## 📝 提交规范速查

### 提交类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(case): 添加满意度评价` |
| `fix` | 修复 Bug | `fix(auth): 修复登录问题` |
| `docs` | 文档更新 | `docs: 更新部署文档` |
| `style` | 代码格式 | `style: 统一缩进` |
| `refactor` | 重构 | `refactor(db): 优化连接池` |
| `perf` | 性能优化 | `perf(api): 优化查询` |
| `test` | 测试 | `test(auth): 添加测试` |
| `chore` | 构建/工具 | `chore: 更新依赖` |

### 提交范围

- `home` - 官网系统
- `kb` - 知识库系统
- `case` - 工单系统
- `auth` - 认证模块
- `db` - 数据库
- `api` - API 接口
- `ui` - 用户界面
- `deploy` - 部署脚本
- `config` - 配置文件

### 提交格式

```bash
# 简单提交
git commit -m "feat(case): 添加新功能"

# 完整提交
git commit -m "feat(case): 添加新功能

- 新增功能 A
- 新增功能 B
- 修复问题 C

Closes #123"
```

---

## 🔀 分支管理

### 分支命名

```
feat/<功能名>          # 功能分支
fix/<问题描述>         # 修复分支
hotfix/<问题描述>      # 热修复分支
refactor/<模块名>      # 重构分支
docs/<文档名>         # 文档分支
```

### 分支操作

```bash
# 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feat/your-feature

# 合并功能分支
git checkout develop
git merge feat/your-feature

# 删除分支
git branch -d feat/your-feature
git push origin --delete feat/your-feature
```

---

## 📦 版本发布

### 发布步骤

```bash
# 1. 切换到 develop
git checkout develop
git pull origin develop

# 2. 更新版本号（编辑 config.py）
# VERSION = "1.2.3"

# 3. 创建发布分支
git checkout -b release/1.2.3

# 4. 更新 CHANGELOG.md
# 添加本次版本的所有变更

# 5. 提交版本变更
git add .
git commit -m "chore(release): 准备发布 1.2.3"

# 6. 合并到 main
git checkout main
git merge release/1.2.3

# 7. 打标签
git tag -a v1.2.3 -m "Release version 1.2.3"

# 8. 推送到远程
git push origin main
git push origin v1.2.3

# 9. 合并回 develop
git checkout develop
git merge release/1.2.3
git push origin develop

# 10. 创建 GitHub Release
#    进入 GitHub 仓库 → Releases → Create Release
#    选择标签 v1.2.3，填写发布说明
```

---

## 📚 相关文档

- [版本管理规范](./VERSION_MANAGEMENT_GUIDE.md) - 完整规范
- [自动部署配置](./AUTO_DEPLOY_SETUP.md) - 部署配置
- [CI/CD 部署文档](./CI_CD_DEPLOYMENT_GUIDE.md) - CI/CD 流程

---

**文档版本**: v1.0  
**最后更新**: 2026-03-04
