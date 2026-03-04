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
