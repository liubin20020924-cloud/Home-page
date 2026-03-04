# 更新日志 (CHANGELOG)

本文档记录所有项目的重大变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增 (Added)
- 完整的版本管理系统
  - 语义化版本规范 (SemVer)
  - Conventional Commits 提交规范
  - Git 分支策略 (main/develop/feat/fix/hotfix)
  - 发布流程和标签管理
- GitHub Actions 自动化
  - 自动同步到 Gitee 工作流
  - 完整的 CI/CD 流水线
- 云主机自动部署系统
  - 部署脚本 (备份/更新/重启/回滚)
  - Webhook 接收器
  - 定时检测更新脚本 (每5分钟)
  - 服务安装脚本 (systemd + cron)
- 完善的文档体系
  - 版本管理规范文档
  - 版本管理快速参考指南
  - 自动部署配置指南
  - 仓库配置快速指南
  - 配置检查清单
  - 配置总结文档

### 变更 (Changed)
- 更新 `.gitignore` 添加部署相关忽略规则
- 更新 README.md 添加版本管理和部署文档链接
- 更新自动部署配置文档中的 Gitee 仓库路径

### 修复 (Fixed)
- 修复 `scripts/check_deploy_config.py` 的编码问题 (Windows GBK 兼容)
- 将 Unicode 符号替换为 ASCII 等效字符
- 移除已废弃的 trilium-py 依赖，改用直接 API 调用
  - 注释掉 `requirements.txt` 中的 trilium-py==0.8.5
  - 注释掉 `check_dependencies.py` 中的 trilium_py 依赖检查
  - 为所有使用 trilium-py 的代码添加 fallback 机制
  - 修复 `routes/api_bp.py` 中 Trilium 测试连接的 ImportError 处理
  - 修复 `routes/kb_bp.py` 中附件代理的 ImportError 处理
  - 修复 `common/trilium_helper.py` 中递归获取笔记的 ImportError 处理
  - 所有 Trilium 相关功能 现在支持在 trilium-py 未安装时通过 requests 直接调用 API

### 变更 (Changed)
- 重构 CI/CD 流程，实现自动合并到 main 分支
  - 更新 `.github/workflows/ci-cd.yml`：支持所有分支的 push 和 PR 触发
  - 添加自动合并任务：PR 通过所有检查后自动合并到 main 分支
  - 优化部署通知：支持 Webhook 和 SSH 两种方式
  - 添加部署摘要：在 GitHub Actions 中显示部署信息
- 新增 Development Helper 工作流
  - 支持通过 GitHub Actions 手动创建 PR
  - 支持配置自动合并选项
- 增强 webhook 接收器功能
  - 添加版本信息记录和查询 (`/webhook/version`)
  - 添加部署日志查询 (`/webhook/logs`)
  - 支持更详细的部署日志记录
  - 兼容 GitHub Webhook 标准格式和 CI/CD 通知格式
- 新增 CI/CD 快速参考文档 (`docs/CICD_QUICK_REFERENCE.md`)
  - 完整的分支策略说明
  - 详细的开发和部署工作流程
  - 常见问题解答和快速命令参考

---

## [1.0.0] - 2026-03-04

### 新增 (Added)
- 首次发布整合系统
  - 官网系统：企业展示、联系表单、留言管理
  - 知识库系统：文档浏览、搜索、Trilium 集成
  - 工单系统：工单提交、实时聊天、状态管理、满意度评价
- 统一用户认证系统
- 邮件通知功能
- WebSocket 实时通信
- 自动部署流程

### 变更 (Changed)
- 采用 Flask 3.0.3 框架
- 使用 MySQL/MariaDB 数据库
- 集成 Trilium 笔记服务

### 修复 (Fixed)
- 初始版本，无修复记录

---

## 版本说明

### 版本号格式

```
主版本号.次版本号.修订号 (MAJOR.MINOR.PATCH)
```

- **主版本号 (MAJOR)**: 不兼容的 API 修改
- **次版本号 (MINOR)**: 向下兼容的功能性新增
- **修订号 (PATCH)**: 向下兼容的问题修正

### 变更类型

- **新增 (Added)**: 新功能
- **变更 (Changed)**: 功能变更
- **废弃 (Deprecated)**: 即将移除的功能
- **移除 (Removed)**: 已移除的功能
- **修复 (Fixed)**: Bug 修复
- **安全 (Security)**: 安全漏洞修复

---

**文档版本**: v1.0  
**最后更新**: 2026-03-04
