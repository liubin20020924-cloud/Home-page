# 分支说明文档

本文档用于记录项目中各分支的用途，便于快速定位和理解各分支的功能。

---

## 主分支

### main
- **用途**: 生产环境主分支
- **状态**: ✅ 稳定
- **最新提交**: `7000af8 feat(database): 添加智能数据库同步脚本` (2026-03-07)
- **说明**: 所有功能开发完成后合并到此分支，经过测试后部署到生产环境
- **已合并分支**:
  - feat/service-guarantee-page ✅
  - feat/contact-button-adjustment ✅
  - feat/user-management-ui ✅
  - feat/unified-admin-dashboard ✅
- **最新功能**:
  - ✅ 智能数据库同步脚本 (sync_database.py)
  - ✅ 数据库升级脚本 (upgrade_to_v2.sql)
  - ✅ 完整初始化脚本 (init_database.sql v2.0)
  - ✅ 统一管理后台 (用户管理、留言管理、监控管理)

---

## 功能开发分支

### feat/service-guarantee-page
- **用途**: 服务保障体系页面开发
- **状态**: ✅ 已完成并合并到main
- **最新提交**: `cd243be fix(home): 修复服务保障页面联系我们按钮跳转路径`
- **本地状态**: 领先1个提交，落后6个提交 (存在未同步的本地修改)
- **说明**:
  - 开发服务保障体系页面
  - 调整Hero区域高度和内容
  - 添加103和3083双释义说明
  - 优化八个标准服务动作展示方式
  - 调整区域背景色交替
  - 修复联系我们按钮跳转路径
- **相关文件**:
  - `templates/home/service-guarantee.html`

### feat/contact-button-adjustment
- **用途**: 联系我们按钮调整
- **状态**: ✅ 已完成并合并到main
- **最新提交**: `a371744 fix: 修复顶部导航栏联系我们按钮跳转问题`
- **本地状态**: 已同步
- **说明**:
  - 调整联系我们表单的按钮样式
  - 优化表单交互体验
  - 调整提交按钮样式和交互效果
- **相关文件**:
  - `templates/home/index.html` (联系表单部分)

### feat/contact-form-features
- **用途**: 联系我们在线留言功能开发
- **状态**: 🔄 开发中 (未合并)
- **最新提交**: `c915771 feat: 完成联系表单/留言管理功能` (2026-03-07)
- **本地状态**: 与远程同步 (最新提交已在远程)
- **说明**:
  - **留言提交功能**:
    - 添加咨询类型选择（开通账户/技术咨询）
    - 修复用户存在性判断逻辑
    - 开通账户：创建客户账户并发送邮件
    - 技术咨询：不创建账户，只发送邮件
    - 联系电话改为必填
  - **留言管理功能**:
    - 留言列表查询（支持搜索和筛选）
    - 留言详情查看
    - 留言状态更新
    - 批量删除留言
  - **留言回复功能** (已完成):
    - 管理员可直接回复留言
    - 回复内容保存到数据库
    - 回复后自动发送邮件通知客户
    - 回复历史记录
    - 回复状态跟踪
  - **账户激活功能** (已完成):
    - 管理员可激活账户并发送账户信息
    - 自动生成临时密码
    - 邮件包含用户名、密码和登录地址
    - 首次登录强制修改密码提示
  - **回复模板管理** (已完成):
    - 创建、编辑、删除回复模板
    - 按分类管理（通用/账户/技术/计费/其他）
    - 支持变量替换（{name}, {email}, {phone}等）
    - 模板使用统计
- **相关文件**:
  - `templates/home/index.html` (联系表单部分)
  - `routes/home_bp.py` (表单提交处理)
  - `routes/admin_bp.py` (留言管理、回复、激活)
  - `routes/reply_templates_bp.py` (回复模板管理)
  - `templates/admin/messages.html` (留言管理页面)
  - `templates/admin/reply_templates.html` (模板管理页面)
  - `services/email_service.py` (邮件发送服务)
  - `database/init_database.sql` (完整数据库结构)
  - `database/upgrade_to_v2.sql` (数据库升级脚本)
  - `database/sync_database.py` (智能同步脚本)
- **已完成**:
  - ✅ 留言提交（支持咨询类型）
  - ✅ 留言管理（列表、详情、状态更新、删除）
  - ✅ 留言回复（邮件通知）
  - ✅ 账户激活（邮件发送账户信息）
  - ✅ 回复模板管理（分类、变量替换）
- **待完成**:
  - ⏳ 留言统计分析
  - ⏳ 留言导出功能
  - ⏳ 留言标签分类
- **下一步**: 等待合并到 main 分支
- **说明**:
  - **留言提交功能**:
    - 添加咨询类型选择（开通账户/技术咨询）
    - 修复用户存在性判断逻辑
    - 开通账户：创建客户账户并发送邮件
    - 技术咨询：不创建账户，只发送邮件
    - 联系电话改为必填
  - **留言管理功能**:
    - 留言列表查询（支持搜索和筛选）
    - 留言详情查看
    - 留言状态更新
    - 批量删除留言
  - **留言回复功能** (新增):
    - 管理员可直接回复留言
    - 回复内容保存到数据库
    - 回复后自动发送邮件通知客户
    - 回复历史记录
    - 回复状态跟踪
  - **账户激活功能** (新增):
    - 管理员可激活账户并发送账户信息
    - 自动生成临时密码
    - 邮件包含用户名、密码和登录地址
    - 首次登录强制修改密码提示
  - **回复模板管理** (新增):
    - 创建、编辑、删除回复模板
    - 按分类管理（通用/账户/技术/计费/其他）
    - 支持变量替换（{name}, {email}, {phone}等）
    - 模板使用统计
- **相关文件**:
  - `templates/home/index.html` (联系表单部分)
  - `routes/home_bp.py` (表单提交处理)
  - `routes/admin_bp.py` (留言管理、回复、激活)
  - `routes/reply_templates_bp.py` (回复模板管理)
  - `templates/admin/messages.html` (留言管理页面)
  - `templates/admin/reply_templates.html` (模板管理页面)
  - `services/email_service.py` (邮件发送服务)
  - `database/upgrade_message_table.sql` (添加phone字段)
  - `database/upgrade_message_reply.sql` (添加回复字段)
  - `database/upgrade_inquiry_type.sql` (添加咨询类型)
  - `database/upgrade_activated_at.sql` (添加激活时间)
  - `database/create_reply_templates.sql` (创建模板表)
- **已完成**:
  - ✅ 留言提交（支持咨询类型）
  - ✅ 留言管理（列表、详情、状态更新、删除）
  - ✅ 留言回复（邮件通知）
  - ✅ 账户激活（邮件发送账户信息）
  - ✅ 回复模板管理（分类、变量替换）
- **待完成**:
  - ⏳ 留言统计分析
  - ⏳ 留言导出功能
  - ⏳ 留言标签分类

### feat/user-management-ui
- **用途**: 用户管理界面功能修改
- **状态**: ✅ 已完成并合并到main
- **最新提交**: `8b7607d feat(user-mgmt): 优化用户管理界面功能`
- **本地状态**: 已同步
- **说明**:
  - 修复删除用户功能：从锁定用户改为真正删除用户
  - 新增用户列表搜索功能：
    - 支持按用户名、邮箱、角色、状态、公司名称搜索
    - 状态搜索支持下拉选择（正常/禁用/锁定）
    - AJAX动态更新，无需刷新页面
    - 清除搜索条件功能
  - 优化搜索栏布局和交互体验
- **相关文件**:
  - `routes/auth_bp.py` (删除用户API)
  - `routes/user_management_bp.py` (搜索API)
  - `templates/user_management/dashboard.html` (前端界面和交互)

### feat/monitoring-alerting
- **用途**: 系统监控与告警功能
- **状态**: ⚠️ 基础功能已完成，已集成到统一管理后台 (部分功能在main分支)
- **最新提交**: `80de3ef feat: 实现系统监控与告警功能`
- **本地状态**: 已同步
- **说明**:
  - 实现系统监控服务 (monitoring_service.py)
    - 系统资源监控 (CPU、内存、磁盘、网络)
    - 告警规则与多级告警 (warning/critical)
    - 邮件通知支持
    - API性能追踪
  - 实现监控中间件 (monitoring_middleware.py)
    - 请求响应时间追踪
    - 错误率统计
    - 性能装饰器
  - 实现监控路由 (monitoring_bp.py)
    - 监控仪表板页面
    - 实时指标 API
    - 告警历史 API
    - 健康检查端点
  - 已集成到统一管理后台 (`/admin/monitoring`)
  - 更新依赖文件 (psutil==5.9.6, Flask-Login==0.6.3)
  - 添加监控文档 (docs/IMPLEMENTATION_SUMMARY_MONITORING.md)
- **已实现**:
  - ✅ 系统资源监控（CPU、内存、磁盘、网络）
  - ✅ 告警规则与多级告警
  - ✅ 邮件通知支持
  - ✅ API性能追踪
  - ✅ 监控仪表板页面（集成到统一管理后台）
  - ✅ 实时指标 API
  - ✅ 告警历史 API
- **待完善**:
  - ⏳ 添加历史数据持久化
  - ⏳ 支持自定义监控指标
  - ⏳ 优化告警通知模板
- **相关文件**:
  - `services/monitoring_service.py`
  - `middlewares/monitoring_middleware.py`
  - `routes/monitoring_bp.py`
  - `routes/admin_bp.py` (统一管理后台集成)
  - `templates/admin/monitoring.html`
  - `docs/IMPLEMENTATION_SUMMARY_MONITORING.md`

### feat/unified-admin-dashboard
- **用途**: 统一管理后台
- **状态**: ✅ 已完成并合并到main
- **最新提交**: `469f3dd feat(admin): 完成统一管理后台开发`
- **本地状态**: 已同步
- **说明**:
  - 创建统一管理路由 (admin_bp.py)
  - 创建管理后台模板
    - base.html: 统一布局和导航
    - dashboard.html: 仪表板页面
    - users.html: 用户管理页面
    - messages.html: 留言管理页面
    - monitoring.html: 监控管理页面
    - login.html: 登录页面
  - 整合三个核心模块
    - 用户管理 (UI 和 API 已完成)
    - 留言管理 (UI 和 API 已完成)
    - 监控管理 (已完成)
  - 实现统一登录认证和权限控制
- **已实现功能**:
  1. ✅ 用户管理 CRUD API（列表/创建/更新/删除）
  2. ✅ 留言管理 CRUD API（列表/更新状态/删除）
  3. ✅ 统一登录认证（基于 session）
  4. ✅ 权限控制（基于 role，仅 admin 可访问）
  5. ✅ 搜索功能（用户列表支持多条件搜索）
  6. ✅ 统计信息卡片（总用户数、活跃用户、管理员、锁定用户）
  7. ✅ 登录记录查看
  8. ✅ 留言回复功能（邮件通知）
  9. ✅ 账户激活功能（邮件发送账户信息）
- **相关文件**:
  - `routes/admin_bp.py`
  - `templates/admin/`
  - `docs/UNIFIED_ADMIN_DASHBOARD.md`
- **访问地址**:
  - 管理后台首页: `/admin/`
  - 登录页面: `/admin/login`
  - 用户管理: `/admin/users`
  - 留言管理: `/admin/messages`
  - 监控管理: `/admin/monitoring`
  - 回复模板: `/admin/reply-templates`

---

## 其他分支

### develop
- **用途**: 开发集成分支
- **状态**: 未创建
- **说明**: 用于集成多个功能分支，进行联调测试

---

## 分支状态说明

### 状态标识
- ✅ **已完成**: 功能开发完成并已合并到main分支
- ⚠️ **部分完成**: 基础功能已完成，但仍有待完善的部分
- ⏳ **开发中**: 正在开发中，尚未完成
- 🔄 **已合并**: 已合并到main分支

### 同步状态
- **已同步**: 本地与远程保持一致
- **领先X个提交**: 本地有X个提交未推送到远程
- **落后X个提交**: 远程有X个提交未拉取到本地

---

## 分支命名规范

- `feat/xxx`: 新功能开发
- `fix/xxx`: 问题修复
- `docs/xxx`: 文档更新
- `style/xxx`: 代码格式调整
- `refactor/xxx`: 代码重构
- `perf/xxx`: 性能优化
- `test/xxx`: 测试相关
- `chore/xxx`: 构建过程或工具变动

---

## 分支管理流程

1. 从main分支创建新的功能分支
2. 在功能分支上进行开发
3. 开发完成后提交代码
4. 推送到远程仓库
5. 切换到main分支
6. 合并功能分支到main
7. 推送main分支到远程
8. 可选：删除已合并的功能分支

---

## 当前分支总览

| 分支名称 | 状态 | 最新提交 | 是否已合并 | 说明 |
|---------|------|---------|-----------|------|
| main | ✅ 稳定 | 7000af8 | - | 生产主分支 |
| feat/service-guarantee-page | ✅ 已完成 | ff97628 | ✅ 是 | 服务保障页面 |
| feat/contact-button-adjustment | ✅ 已完成 | a371744 | ✅ 是 | 联系按钮调整 |
| feat/contact-form-features | 🔄 开发中 | c915771 | ❌ 否 | 联系表单/留言管理/回复模板 |
| feat/user-management-ui | ✅ 已完成 | 8b7607d | ✅ 是 | 用户管理UI |
| feat/monitoring-alerting | ⚠️ 部分完成 | 80de3ef | ❌ 否 | 监控与告警（已集成到main） |
| feat/unified-admin-dashboard | ✅ 已完成 | 469f3dd | ✅ 是 | 统一管理后台 |

---

## 功能完成情况详细说明

### feat/contact-form-features 分支

#### 已完成的核心功能

**1. 留言提交功能** ✅
- 支持两种咨询类型：开通账户、技术咨询
- 开通账户类型：自动创建客户账户（禁用状态）
- 技术咨询类型：不创建账户，仅发送通知邮件
- 联系电话改为必填字段
- 自动发送邮件通知到 support@cloud-doors.com

**2. 留言管理功能** ✅
- 留言列表查询（支持搜索和筛选）
- 按状态筛选（未处理/已处理/已完成）
- 留言详情查看
- 留言状态更新
- 批量删除留言
- 分页显示

**3. 留言回复功能** ✅
- 管理员可直接在留言管理页面回复
- 回复内容保存到数据库
- 回复后自动发送邮件通知客户
- 支持选择是否发送邮件
- 回复历史记录显示
- 回复状态跟踪（draft/sent/failed）
- 支持回复模板快速填充

**4. 账户激活功能** ✅
- 管理员可为申请开通账户的客户激活账户
- 自动生成随机临时密码
- 发送激活邮件（包含用户名、密码、登录地址）
- 首次登录强制修改密码提示
- 更新用户状态为 active
- 记录激活时间

**5. 回复模板管理功能** ✅
- 创建、编辑、删除回复模板
- 按分类管理（通用/账户相关/技术支持/计费相关/其他）
- 支持变量替换（{name}, {email}, {phone}, {company_name}, {message}, {username}）
- 模板预览功能
- 模板使用统计
- 系统模板和自定义模板
- 模板启用/禁用控制

#### 数据库变更

**messages 表扩展**:
```sql
-- 添加回复相关字段
reply_content TEXT
reply_time TIMESTAMP
replied_by VARCHAR(50)
replied_name VARCHAR(100)
reply_status VARCHAR(20)

-- 添加咨询类型字段
inquiry_type VARCHAR(50)
```

**users 表扩展**:
```sql
-- 添加注册来源和激活时间字段
registration_source VARCHAR(50)
contact_message_id INT
activated_at TIMESTAMP
```

**reply_templates 表创建**:
```sql
CREATE TABLE reply_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    description VARCHAR(500),
    is_active TINYINT(1) DEFAULT 1,
    is_system TINYINT(1) DEFAULT 0,
    sort_order INT DEFAULT 0,
    use_count INT DEFAULT 0,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

#### API 接口

**留言相关**:
- `POST /api/contact` - 提交留言
- `GET /admin/messages/api/list` - 获取留言列表
- `POST /admin/messages/api/update` - 更新留言状态
- `POST /admin/messages/api/delete` - 删除留言
- `POST /admin/messages/api/reply` - 回复留言
- `POST /admin/messages/api/activate-account` - 激活账户

**回复模板相关**:
- `GET /admin/reply-templates/api/list` - 获取模板列表
- `GET /admin/reply-templates/api/<id>` - 获取模板详情
- `POST /admin/reply-templates/api` - 创建模板
- `PUT /admin/reply-templates/api/<id>` - 更新模板
- `DELETE /admin/reply-templates/api/<id>` - 删除模板
- `POST /admin/reply-templates/api/<id>/increment-use` - 增加使用次数
- `POST /admin/reply-templates/api/preview` - 预览模板

#### 相关文档

- `docs/optimization-plans/MESSAGE_SYSTEM_OPTIMIZATION_PLAN.md` - 留言系统优化计划（v3.0）
- `docs/IMPLEMENTATION_SUMMARY_MONITORING.md` - 监控系统实现总结

#### 待完成的高级功能

- 留言统计分析（图表展示）
- 留言导出功能（Excel/CSV）
- 留言标签分类
- 附件上传功能
- 留言归档功能（软删除）

---

## 最后更新

- **更新时间**: 2026-03-07
- **更新人**: AI Assistant
- **备注**:
  - 更新所有分支的最新状态和提交信息
  - 添加分支状态标识和同步状态说明
  - 添加分支总览表格，便于快速查看
  - 统一管理后台功能已完成，包含用户管理、留言管理、监控管理三大模块
  - 监控与告警功能基础完成，已集成到统一管理后台
  - **main 分支最新更新**：
    - ✅ 智能数据库同步脚本 (sync_database.py) - 自动检测并补充缺失内容
    - ✅ 数据库升级脚本 (upgrade_to_v2.sql) - 升级现有数据库
    - ✅ 完整初始化脚本 (init_database.sql v2.0) - 包含所有功能
  - **联系表单功能分支**：
    - ✅ 留言提交（支持咨询类型：开通账户/技术咨询）
    - ✅ 留言管理（列表、详情、状态更新、删除）
    - ✅ 留言回复功能（支持邮件通知客户）
    - ✅ 账户激活功能（自动发送账户信息邮件）
    - ✅ 回复模板管理（支持分类和变量替换）
    - 🔄 待完成：统计分析、导出、标签分类等高级功能
  - **文档更新**：
    - `docs/optimization-plans/MESSAGE_SYSTEM_OPTIMIZATION_PLAN.md` 已更新至 v3.0
    - `database/README.md` 已更新，添加智能同步脚本说明
    - 记录了所有已完成功能的详细说明和技术实现
