# 云户科技网站 - 文档中心

> 项目文档索引和快速导航指南

---

## 📚 核心文档

### 项目总览

| 文档 | 说明 | 适用场景 |
|------|------|----------|
| [项目说明](../README.md) | 项目整体介绍和快速开始 | 首次了解项目 |
| [更新日志](./CHANGELOG.md) | 版本更新历史、功能改进、问题修复 | 了解最新功能 |
| [配置指南](./configuration/CONFIGURATION_GUIDE.md) | 系统配置详细说明 | 环境部署 |

### CI/CD 自动化部署

| 文档 | 说明 | 适用场景 |
|------|------|----------|
| [CI/CD文档索引](./CICD/README.md) | CI/CD完整文档目录导航 | 了解CI/CD文档结构 |
| [快速开始](./CICD/00-QUICK_START.md) | CI/CD快速开始指南 | 新项目部署 |
| [部署指南](./CICD/02-CONFIGURATION.md) | 详细的部署流程 | 初次部署 |

---

## 📖 系统指南

| 文档 | 说明 | 目标读者 |
|------|------|----------|
| [官网系统指南](./system-guides/HOME_SYSTEM_GUIDE.md) | 官网首页、产品展示、留言系统 | 所有用户 |
| [知识库系统指南](./system-guides/KB_SYSTEM_GUIDE.md) | 知识库浏览、搜索、文档管理 | 知识库用户 |
| [统一用户管理指南](./system-guides/UNIFIED_SYSTEM_GUIDE.md) | 用户注册、登录、权限控制、用户管理 | 所有用户 |
| [用户注册指南](./system-guides/USER_REGISTRATION_GUIDE.md) | 用户注册流程和详细说明 | 新用户 |
| [工单系统指南](./system-guides/工单系统设计文档.md) | 工单创建、跟踪、论坛式交流、满意度评价 | 客户/客服/管理员 |

---

## 🚀 优化计划

| 文档 | 说明 | 适用场景 |
|------|------|----------|
| [实用架构优化方案](./architecture/PRAGMATIC_ARCHITECTURE_OPTIMIZATION.md) | 基于实际部署环境的系统架构优化方案（推荐首先阅读）| 系统架构师/管理员 |
| [优化文档索引](./optimization-plans/OPTIMIZATION_INDEX.md) | 所有优化文档的总览索引和路线图 | 开发人员/管理员 |
| [留言系统优化计划](./optimization-plans/MESSAGE_SYSTEM_OPTIMIZATION_PLAN.md) | 留言系统后续优化方向和实施计划 | 开发人员/管理员 |
| [工单系统优化计划](./optimization-plans/CASE_SYSTEM_OPTIMIZATION_PLAN.md) | 工单系统后续优化方向和实施计划 | 开发人员/管理员 |
| [知识库系统优化计划](./optimization-plans/KB_SYSTEM_OPTIMIZATION_PLAN.md) | 知识库系统后续优化方向和实施计划 | 开发人员/管理员 |
| [统一用户管理优化计划](./optimization-plans/UNIFIED_SYSTEM_OPTIMIZATION_PLAN.md) | 用户管理后续优化方向和实施计划 | 开发人员/管理员 |
| [前端代码优化建议](./optimization-plans/FRONTEND_OPTIMIZATION_GUIDE.md) | 全面前端代码分析和优化建议 | 前端开发/代码审查 |
| [优化更新总结](./optimization-plans/OPTIMIZATION_UPDATE_SUMMARY.md) | 优化文档更新总结 | 开发人员/管理员 |

---

## 🏗️ 架构设计

| 文档 | 说明 | 适用场景 |
|------|------|----------|
| [实用架构优化方案](./architecture/PRAGMATIC_ARCHITECTURE_OPTIMIZATION.md) | 基于实际部署环境的系统架构优化方案 | 系统架构师/管理员 |
| [系统架构优化（理论版）](./architecture/SYSTEM_ARCHITECTURE_OPTIMIZATION.md) | 理论性的系统架构优化建议 | 系统架构师 |

---

## 📋 项目管理

| 文档 | 说明 | 适用场景 |
|------|------|----------|
| [分支说明文档](./project-management/BRANCHES.md) | Git 分支命名规范和管理策略 | 所有开发者 |
| [版本管理规范](./project-management/VERSION_MANAGEMENT_GUIDE.md) | 版本号规范、提交规范、发布流程 | 所有开发者 |
| [脚本说明文档](./project-management/SCRIPTS.md) | 项目中使用的脚本说明和用法 | 运维/开发者 |

---

## ⚙️ 配置文档

| 文档 | 说明 | 适用场景 |
|------|------|----------|
| [配置指南](./configuration/CONFIGURATION_GUIDE.md) | 系统配置详细说明 | 环境部署 |
| [Webhook 清理说明](./configuration/CLEANUP_WEBHOOK.md) | Webhook 清理和故障排查 | 运维 |

---

## 🗂️ 文档结构

```
docs/
├── README.md                              # 本文件 - 文档索引
├── CHANGELOG.md                           # 版本更新日志
│
├── system-guides/                         # 系统使用指南
│   ├── HOME_SYSTEM_GUIDE.md               # 官网系统使用指南
│   ├── KB_SYSTEM_GUIDE.md                 # 知识库系统使用指南
│   ├── UNIFIED_SYSTEM_GUIDE.md           # 统一用户管理使用指南
│   ├── USER_REGISTRATION_GUIDE.md        # 用户注册指南
│   └── 工单系统设计文档.md                    # 工单系统设计文档
│
├── optimization-plans/                      # 优化计划
│   ├── MESSAGE_SYSTEM_OPTIMIZATION_PLAN.md        # 留言系统优化计划
│   ├── CASE_SYSTEM_OPTIMIZATION_PLAN.md          # 工单系统优化计划
│   ├── KB_SYSTEM_OPTIMIZATION_PLAN.md            # 知识库系统优化计划
│   ├── UNIFIED_SYSTEM_OPTIMIZATION_PLAN.md       # 用户管理优化计划
│   ├── FRONTEND_OPTIMIZATION_GUIDE.md           # 前端优化指南
│   ├── OPTIMIZATION_INDEX.md                    # 优化文档索引
│   └── OPTIMIZATION_UPDATE_SUMMARY.md          # 优化更新总结
│
├── architecture/                           # 架构设计
│   ├── PRAGMATIC_ARCHITECTURE_OPTIMIZATION.md  # 实用架构优化方案（推荐）
│   └── SYSTEM_ARCHITECTURE_OPTIMIZATION.md     # 系统架构优化（理论版）
│
├── project-management/                    # 项目管理
│   ├── BRANCHES.md                          # 分支说明文档
│   ├── VERSION_MANAGEMENT_GUIDE.md    # 版本管理规范
│   └── SCRIPTS.md                           # 脚本说明文档
│
├── configuration/                         # 配置文档
│   ├── CONFIGURATION_GUIDE.md         # 配置指南
│   └── CLEANUP_WEBHOOK.md            # Webhook 清理说明
│
└── CICD/                                  # CI/CD 文档
    ├── README.md                          # CI/CD 文档索引
    ├── 00-QUICK_START.md              # 快速开始
    ├── 01-INTRODUCTION.md             # 介绍
    ├── 02-CONFIGURATION.md           # 配置
    ├── 03-DEPLOYMENT_HISTORY.md       # 部署历史
    ├── 04-FEATURES.md                # 功能说明
    ├── 05-TROUBLESHOOTING.md        # 故障排查
    ├── 06-TESTING.md                 # 测试
    └── 07-SECURITY.md               # 安全
```

---

## 🎯 快速导航

### 按用户角色查找

| 角色 | 推荐阅读文档 |
|------|-------------|
| **新用户** | 项目说明 → 系统指南（对应系统） |
| **管理员** | 统一用户管理 → 工单系统 → 架构优化方案 → 配置指南 |
| **客服** | 工单系统 → 知识库系统 |
| **开发者** | 配置指南 → 优化计划 → 项目管理 |
| **客户** | 工单系统 → 知识库系统 |

### 按功能查找

| 功能 | 文档 | 章节 |
|------|--------|------|
| 用户注册/登录 | [统一用户管理](./system-guides/UNIFIED_SYSTEM_GUIDE.md) | 用户注册、登录 |
| 用户权限管理 | [统一用户管理](./system-guides/UNIFIED_SYSTEM_GUIDE.md) | 权限控制 |
| 提交工单 | [工单系统](./system-guides/工单系统设计文档.md) | 提交工单 |
| 工单回复交流 | [工单系统](./system-guides/工单系统设计文档.md) | 工单详情 |
| 满意度评价 | [工单系统](./system-guides/工单系统设计文档.md) | 满意度评价 |
| 工单统计报表 | [工单系统](./system-guides/工单系统设计文档.md) | 工单统计 |
| 知识库搜索 | [知识库系统](./system-guides/KB_SYSTEM_GUIDE.md) | 知识搜索 |
| 知识库管理 | [知识库系统](./system-guides/KB_SYSTEM_GUIDE.md) | 知识管理 |
| 留言功能 | [官网系统](./system-guides/HOME_SYSTEM_GUIDE.md) | 留言系统 |
| 邮件配置 | [配置指南](./configuration/CONFIGURATION_GUIDE.md) | 邮件配置 |

---

## 💡 使用提示

### 文档阅读建议

1. **首次访问**：先阅读对应系统的指南文档
2. **配置问题**：查看 [配置指南](./configuration/CONFIGURATION_GUIDE.md)
3. **版本更新**：查看 [更新日志](./CHANGELOG.md)
4. **功能查找**：使用浏览器搜索 `Ctrl+F` 快速定位

### 系统快速链接

- **统一登录**: `/unified/`
- **工单系统**: `/case/`
- **知识库系统**: `/kb/`
- **官网首页**: `/`

---

## 📝 版本信息

### 当前版本: v2.9
### 发布日期: 2026-03-07
### 主要更新:
- ✅ 重组文档目录结构，按类型分类存放
- ✅ 更新所有文档链接引用
- ✅ 新增实用架构优化方案
- ✅ 新增留言系统优化计划
- ✅ 更新各系统优化文档的优先级
- ✅ 新增优化文档索引和更新总结

---

## 🤝 文档维护

### 文档更新规范

1. 保持文档简洁明了，避免重复内容
2. 每个系统只保留一份核心指南文档
3. 重大功能更新时同步更新对应文档
4. 临时修复文档不纳入核心文档

### 文档清理原则

- 删除过时的临时文档
- 删除重复内容的文档
- 删除代码审查/统计等非使用性文档
- 保留系统指南、配置指南、更新日志等核心文档

---

## 📊 文档目录说明

### 目录分类说明

- **system-guides/**: 系统使用指南，面向最终用户的操作手册
- **optimization-plans/**: 优化计划，面向开发人员和系统管理员的优化方案
- **architecture/**: 架构设计文档，面向系统架构师的技术文档
- **project-management/**: 项目管理文档，面向开发者的规范和流程说明
- **configuration/**: 配置文档，面向运维人员的配置指南
- **CICD/**: CI/CD 自动化文档，面向运维和开发人员的部署文档

### 文档命名规范

- 系统指南：`{SYSTEM}_SYSTEM_GUIDE.md` 或 `{SYSTEM}_设计文档.md`
- 优化计划：`{SYSTEM}_SYSTEM_OPTIMIZATION_PLAN.md` 或 `{FUNCTION}_OPTIMIZATION_GUIDE.md`
- 架构文档：`{TYPE}_ARCHITECTURE_OPTIMIZATION.md`
- 项目管理：`{TOPIC}.md`（如 BRANCHES, VERSION_MANAGEMENT_GUIDE）
- 配置文档：`{TOPIC}_GUIDE.md` 或 `{TOPIC}.md`

---

<div align="center">

**文档版本**: v3.0
**最后更新**: 2026-03-07
**维护者**: 云户科技技术团队

</div>
