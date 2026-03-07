# 云户科技网站 - 文档中心

> 项目文档索引和快速导航指南

---

## 📚 核心文档

### 项目总览

| 文档 | 说明 | 适用场景 |
|------|------|----------|
| [项目说明](./README.md) | 项目整体介绍和快速开始 | 首次了解项目 |
| [更新日志](./CHANGELOG.md) | 版本更新历史、功能改进、问题修复 | 了解最新功能 |
| [配置指南](./CONFIGURATION_GUIDE.md) | 系统配置详细说明 | 环境部署 |

### CI/CD 自动化部署

| 文档 | 说明 | 适用场景 |
|------|------|----------|
| [CI/CD文档索引](./CICD/README.md) | CI/CD完整文档目录导航 | 了解CI/CD文档结构 |
| [完整实施指南](./CICD/00-COMPLETE_GUIDE.md) | CI/CD完整实施流程 | 新项目部署 |
| [快速参考](./CICD/01-QUICK_REFERENCE.md) | 常用命令、配置速查 | 日常运维 |
| [部署指南](./CICD/02-DEPLOYMENT_GUIDE.md) | 详细的部署流程 | 初次部署 |

### 系统指南

| 文档 | 说明 | 目标读者 |
|------|------|----------|
| [统一用户管理指南](./UNIFIED_SYSTEM_GUIDE.md) | 用户注册、登录、权限控制、用户管理 | 所有用户 |
| [统一用户管理优化计划](./UNIFIED_SYSTEM_OPTIMIZATION_PLAN.md) | 用户管理后续优化方向和实施计划 | 开发人员/管理员 |
| [工单系统指南](./工单系统设计文档.md) | 工单创建、跟踪、论坛式交流、满意度评价 | 客户/客服/管理员 |
| [工单系统优化计划](./CASE_SYSTEM_OPTIMIZATION_PLAN.md) | 工单系统后续优化方向和实施计划 | 开发人员/管理员 |
| [知识库系统指南](./KB_SYSTEM_GUIDE.md) | 知识库浏览、搜索、文档管理 | 知识库用户 |
| [知识库系统优化计划](./KB_SYSTEM_OPTIMIZATION_PLAN.md) | 知识库系统后续优化方向和实施计划 | 开发人员/管理员 |
| [官网系统指南](./HOME_SYSTEM_GUIDE.md) | 官网首页、产品展示、留言系统 | 所有用户 |
| [留言系统优化计划](./MESSAGE_OPTIMIZATION_PLAN.md) | 留言系统后续优化方向和实施计划 | 开发人员/管理员 |

---

## 📖 文档结构

```
docs/
├── README.md                              # 本文件 - 文档索引
├── CHANGELOG.md                           # 版本更新日志
├── CONFIGURATION_GUIDE.md                 # 系统配置指南
├── CICD/                                  # CI/CD自动化部署文档目录
│   ├── README.md                          # CI/CD文档索引
│   ├── 00-COMPLETE_GUIDE.md              # 完整实施指南
│   ├── 01-QUICK_REFERENCE.md            # 快速参考
│   ├── 02-DEPLOYMENT_GUIDE.md           # 部署指南
│   ├── 03-CURRENT_FLOW.md               # 当前流程
│   ├── 04-DEPLOYMENT_HISTORY.md         # 部署历史
│   ├── 10-GIT_CONFIG_SOLUTION.md        # Git配置方案
│   ├── 11-PROXY_SETUP.md                # 代理设置
│   ├── 12-AUTO_DEPLOY_SETUP.md          # 自动部署配置
│   ├── 20-SSH_DEPLOYMENT.md             # SSH部署
│   ├── 21-SIMPLIFIED_CI_CD.md           # 简化CI/CD
│   ├── 22-QUICK_SETUP.md                # 快速设置
│   ├── 23-TEST_GUIDE.md                 # 测试指南
│   ├── 30-WEBHOOK_TROUBLESHOOTING.md    # Webhook故障排查
│   ├── 31-SERVICE_TROUBLESHOOTING.md    # 服务故障排查
│   ├── 40-FINAL_SUMMARY.md              # 最终总结
│   └── 41-IMPLEMENTATION_SUMMARY.md      # 实施总结
├── UNIFIED_SYSTEM_GUIDE.md                # 统一用户管理系统指南
├── UNIFIED_SYSTEM_OPTIMIZATION_PLAN.md     # 统一用户管理系统优化计划
├── CASE_SYSTEM_OPTIMIZATION_PLAN.md       # 工单系统优化计划
├── KB_SYSTEM_OPTIMIZATION_PLAN.md         # 知识库系统优化计划
├── MESSAGE_OPTIMIZATION_PLAN.md           # 留言系统优化计划
├── 工单系统设计文档.md                   # 工单系统设计文档
├── KB_SYSTEM_GUIDE.md                    # 知识库系统指南
├── HOME_SYSTEM_GUIDE.md                   # 官网系统指南
├── USER_REGISTRATION_GUIDE.md             # 用户注册指南
└── VERSION_MANAGEMENT_GUIDE.md           # 版本管理指南
```

---

## 🚀 快速导航

### 按用户角色查找

| 角色 | 推荐阅读文档 |
|------|-------------|
| **新用户** | 项目说明 → 系统指南（对应系统） |
| **管理员** | 统一用户管理 → 工单系统 → 配置指南 |
| **客服** | 工单系统 → 知识库系统 |
| **开发者** | 配置指南 → 更新日志 |
| **客户** | 工单系统 → 知识库系统 |

### 按功能查找

| 功能 | 文档 | 章节 |
|------|--------|------|
| 用户注册/登录 | [统一用户管理](./UNIFIED_SYSTEM_GUIDE.md) | 用户注册、登录 |
| 用户权限管理 | [统一用户管理](./UNIFIED_SYSTEM_GUIDE.md) | 权限控制 |
| 提交工单 | [工单系统](./工单系统设计文档.md) | 提交工单 |
| 工单回复交流 | [工单系统](./工单系统设计文档.md) | 工单详情 |
| 满意度评价 | [工单系统](./工单系统设计文档.md) | 满意度评价 |
| 工单统计报表 | [工单系统](./工单系统设计文档.md) | 工单统计 |
| 知识库搜索 | [知识库系统](./KB_SYSTEM_GUIDE.md) | 知识搜索 |
| 知识库管理 | [知识库系统](./KB_SYSTEM_GUIDE.md) | 知识管理 |
| 留言功能 | [官网系统](./HOME_SYSTEM_GUIDE.md) | 留言系统 |
| 邮件配置 | [配置指南](./CONFIGURATION_GUIDE.md) | 邮件配置 |

---

## 📝 版本信息

### 当前版本: v2.8
### 发布日期: 2026-02-26
### 主要更新:
- ✅ 新增工单满意度评价功能
- ✅ 新增工单统计报表页面
- ✅ 优化工单查询权限（客户/客服/管理员）
- ✅ 完善工单系统设计文档
- ✅ 整理文档结构，保留核心文档

---

## 💡 使用提示

### 文档阅读建议

1. **首次访问**：先阅读对应系统的指南文档
2. **配置问题**：查看 [配置指南](./CONFIGURATION_GUIDE.md)
3. **版本更新**：查看 [更新日志](./CHANGELOG.md)
4. **功能查找**：使用浏览器搜索 `Ctrl+F` 快速定位

### 系统快速链接

- **统一登录**: `/unified/`
- **工单系统**: `/case/`
- **知识库系统**: `/kb/`
- **官网首页**: `/`

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

<div align="center">

**文档版本**: v2.1  
**最后更新**: 2026-02-26  
**维护者**: 云户科技技术团队

</div>
