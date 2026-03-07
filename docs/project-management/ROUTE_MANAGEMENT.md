# 路由管理文档

> **更新时间**: 2026-03-07
> **负责人**: 高级软件工程师
> **目的**: 统一规划所有页面和API的访问地址，解决当前路由混乱问题

---

## 📊 当前路由现状分析

### 问题分析
1. **命名不统一**: 有的用 `-`，有的用 `/`
2. **层级混乱**: 同级功能和子功能混在一起
3. **重复路由**: 多个蓝图有相似功能的路由
4. **API分散**: API路由混杂在不同蓝图中

### 现有蓝图结构

| 蓝图 | 前缀 | 用途 | 状态 |
|-----|------|------|------|
| home_bp | `/` | 官网系统 | ✅ 正常 |
| kb_bp | `/kb` | 知识库前台 | ✅ 正常 |
| kb_management_bp | `/kb/MGMT` | 知识库管理 | ⚠️ 前缀不规范 |
| case_bp | `/case` | 工单系统 | ✅ 正常 |
| auth_bp | `/auth` | 统一认证 | ✅ 正常 |
| user_management_bp | `/user-mgmt` | 用户管理 | ⚠️ 前缀不规范 |
| unified_bp | `/unified` | 统一API | ⚠️ 用途不明确 |
| api_bp | `/api` | API路由 | ⚠️ 用途不明确 |

---

## 🎯 统一路由规划

### 1. 命名规范

#### 蓝图命名
- 统一使用小写字母和下划线
- 格式: `{system}_bp`
- 示例: `home_bp`, `kb_bp`, `auth_bp`

#### URL前缀
- 统一使用小写字母和连字符
- 格式: `/{system-name}`
- 示例: `/user-mgmt`, `/kb-admin`

#### 路由路径
- 单词间使用连字符 `-`
- API路径使用小写和下划线
- 示例: `/user-list`, `/api/create_user`

### 2. 分层级规划

#### L1: 系统级（主要入口）
```
/                    - 官网首页
/kb                  - 知识库
/case                - 工单系统
/admin               - 管理后台（统一入口）
```

#### L2: 功能级（模块入口）
```
/admin/
  /dashboard          - 仪表板
  /users             - 用户管理
  /messages          - 留言管理
  /monitoring        - 监控管理
  /kb-admin          - 知识库管理
  /case-admin        - 工单管理
```

#### L3: 操作级（具体功能）
```
/admin/users/
  /list              - 用户列表
  /create            - 创建用户
  /edit/<id>         - 编辑用户
  /delete/<id>       - 删除用户

/admin/messages/
  /list              - 留言列表
  /view/<id>         - 查看留言
  /update-status/<id> - 更新状态
```

---

## 📝 路由迁移计划

### Phase 1: 修复现有蓝图命名

#### user_management_bp
- **当前前缀**: `/user-mgmt`
- **建议前缀**: `/admin/users`
- **理由**: 纳入统一管理后台

#### kb_management_bp
- **当前前缀**: `/kb/MGMT`
- **建议前缀**: `/admin/kb`
- **理由**: 纳入统一管理后台

#### unified_bp
- **当前前缀**: `/unified`
- **建议操作**: 合并到 auth_bp 或废弃
- **理由**: 功能与 auth_bp 重复

#### api_bp
- **当前前缀**: `/api`
- **建议前缀**: 保持 `/api`
- **理由**: API 路由前缀

### Phase 2: 统一管理后台路由

#### admin_bp (新建)
```
/admin/                     - 管理后台首页
/admin/dashboard/           - 仪表板
/admin/login/               - 登录
/admin/logout/              - 登出

/admin/users/               - 用户管理
  /list                     - 用户列表
  /create                   - 创建用户
  /edit/<id>                - 编辑用户
  /delete/<id>              - 删除用户
  /api/list                 - 用户列表API
  /api/create               - 创建用户API
  /api/update/<id>          - 更新用户API
  /api/delete/<id>          - 删除用户API

/admin/messages/            - 留言管理
  /list                     - 留言列表
  /view/<id>                - 查看留言
  /api/list                 - 留言列表API
  /api/update-status/<id>   - 更新状态API
  /api/delete/<id>          - 删除留言API

/admin/monitoring/          - 监控管理
  /dashboard                - 监控仪表板
  /api/metrics              - 监控指标API
  /api/alerts               - 告警列表API

/admin/kb/                  - 知识库管理
  /list                     - 文章列表
  /create                   - 创建文章
  /edit/<id>                - 编辑文章
  /api/list                 - 文章列表API
  /api/create               - 创建文章API
  /api/update/<id>          - 更新文章API
  /api/delete/<id>          - 删除文章API

/admin/case/                - 工单管理
  /list                     - 工单列表
  /view/<id>                - 查看工单
  /api/list                 - 工单列表API
  /api/update-status/<id>   - 更新状态API
```

### Phase 3: API路由统一

#### 统一API前缀
```
/api/auth/                  - 认证相关API
  /login                    - 登录
  /logout                   - 登出
  /check-login              - 检查登录状态

/api/users/                 - 用户API
  /list                     - 用户列表
  /create                   - 创建用户
  /update/<id>              - 更新用户
  /delete/<id>              - 删除用户
  /reset-password/<id>      - 重置密码

/api/kb/                    - 知识库API
  /search                   - 搜索
  /article/<id>             - 文章详情

/api/case/                  - 工单API
  /list                     - 工单列表
  /create                   - 创建工单
  /update/<id>              - 更新工单

/api/monitoring/            - 监控API
  /metrics                  - 监控指标
  /alerts                   - 告警列表
  /health                   - 健康检查
```

---

## 🔄 实施步骤

### 步骤 1: 创建新的 admin_bp
- [ ] 创建 `routes/admin_bp.py`
- [ ] 设计统一布局模板
- [ ] 实现仪表板首页

### 步骤 2: 迁移用户管理
- [ ] 将 `user_management_bp` 的路由迁移到 `admin_bp`
- [ ] 更新所有相关链接
- [ ] 测试所有功能

### 步骤 3: 迁移知识库管理
- [ ] 将 `kb_management_bp` 的路由迁移到 `admin_bp`
- [ ] 更新所有相关链接
- [ ] 测试所有功能

### 步骤 4: 迁移监控管理
- [ ] 将 `monitoring_bp` 的路由迁移到 `admin_bp`
- [ ] 更新所有相关链接
- [ ] 测试所有功能

### 步骤 5: 清理废弃路由
- [ ] 评估 `unified_bp` 和 `api_bp` 的必要性
- [ ] 合并或废弃重复路由
- [ ] 更新文档

### 步骤 6: 全面测试
- [ ] 测试所有页面访问
- [ ] 测试所有API接口
- [ ] 测试权限控制
- [ ] 性能测试

---

## 📊 路由对照表

### 官网系统 (home_bp)
| 功能 | 当前路由 | 建议路由 | 状态 |
|-----|---------|---------|------|
| 首页 | `/` | `/` | ✅ 保持 |
| 关于我们 | `/about` | `/about` | ✅ 保持 |
| 产品部件 | `/parts` | `/parts` | ✅ 保持 |
| 服务保障 | `/service-guarantee` | `/service-guarantee` | ✅ 保持 |
| 案例展示 | `/cases` | `/cases` | ✅ 保持 |

### 知识库系统 (kb_bp)
| 功能 | 当前路由 | 建议路由 | 状态 |
|-----|---------|---------|------|
| 知识库首页 | `/kb/` | `/kb/` | ✅ 保持 |
| 登录 | `/kb/auth/login` | `/kb/login` | ⚠️ 需调整 |
| 登出 | `/kb/auth/logout` | `/kb/logout` | ⚠️ 需调整 |
| 修改密码 | `/kb/auth/change-password` | `/kb/change-password` | ⚠️ 需调整 |

### 工单系统 (case_bp)
| 功能 | 当前路由 | 建议路由 | 状态 |
|-----|---------|---------|------|
| 工单列表 | `/case/` | `/case/` | ✅ 保持 |
| 登录 | `/case/api/login` | `/case/login` | ⚠️ 需调整 |
| 登出 | `/case/api/logout` | `/case/logout` | ⚠️ 需调整 |

### 管理后台 (待整合)
| 模块 | 当前路由 | 建议路由 | 状态 |
|-----|---------|---------|------|
| 用户管理 | `/user-mgmt/` | `/admin/users/` | ⏳ 待迁移 |
| 知识库管理 | `/kb/MGMT/` | `/admin/kb/` | ⏳ 待迁移 |
| 监控管理 | `/monitoring/` | `/admin/monitoring/` | ⏳ 待迁移 |
| 统一认证 | `/auth/` | `/admin/auth/` | ⏳ 待迁移 |

---

## 📌 注意事项

1. **向后兼容**: 迁移过程中保留旧路由的重定向
2. **文档更新**: 同步更新所有文档中的路由引用
3. **SEO影响**: 主要页面路由变更需考虑SEO
4. **测试覆盖**: 确保所有路由都有对应的测试用例
5. **权限控制**: 迁移时重新审查权限配置

---

## 📅 预计工期

- Phase 1: 0.5 天
- Phase 2: 1 天
- Phase 3: 1 天
- Phase 4: 0.5 天
- Phase 5: 0.5 天
- Phase 6: 1 天

**总计**: 4 天

---

## 🔗 相关文档

- [分支说明文档](./BRANCHES.md)
- [统一管理后台开发计划](../UNIFIED_ADMIN_DASHBOARD.md)
- [配置指南](../configuration/CONFIGURATION_GUIDE.md)
