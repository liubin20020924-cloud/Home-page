# 分支说明文档

本文档用于记录项目中各分支的用途，便于快速定位和理解各分支的功能。

---

## 主分支

### main
- **用途**: 生产环境主分支
- **状态**: 稳定
- **说明**: 所有功能开发完成后合并到此分支，经过测试后部署到生产环境

---

## 功能开发分支

### feat/service-guarantee-page
- **用途**: 服务保障体系页面开发
- **状态**: 已完成并合并到main
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
- **状态**: 已完成并合并到main
- **说明**:
  - 调整联系我们表单的按钮样式
  - 优化表单交互体验
  - 调整提交按钮样式和交互效果
- **相关文件**:
  - `templates/home/index.html` (联系表单部分)

### feat/contact-form-features
- **用途**: 联系我们在线留言功能开发
- **状态**: 开发中
- **说明**:
  - 添加咨询类型选择（开通账户/技术咨询）
  - 修复用户存在性判断逻辑
  - 开通账户：创建客户账户并发送邮件
  - 技术咨询：不创建账户，只发送邮件
  - 联系电话改为必填
- **相关文件**:
  - `templates/home/index.html` (联系表单部分)
  - `routes/home_bp.py` (表单提交处理)

### feat/user-management-ui
- **用途**: 用户管理界面功能修改
- **状态**: 已完成并合并到main
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
- **状态**: 基础功能已完成，待继续开发
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
  - 更新依赖文件 (psutil==5.9.6, Flask-Login==0.6.3)
  - 添加监控文档 (MONITORING_QUICK_START.md)
- **待完善**:
  - 添加用户认证和权限控制
  - 优化邮件通知模板
  - 添加历史数据持久化
  - 支持自定义监控指标
- **相关文件**:
  - `services/monitoring_service.py`
  - `middlewares/monitoring_middleware.py`
  - `routes/monitoring_bp.py`
  - `templates/monitoring/dashboard.html`

### feat/unified-admin-dashboard
- **用途**: 统一管理后台
- **状态**: ✅ 已完成
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

---

## 其他分支

### develop
- **用途**: 开发集成分支
- **状态**: 
- **说明**: 用于集成多个功能分支，进行联调测试

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
4. 切换到main分支，合并功能分支
5. 推送到远程仓库
6. 可选：删除已合并的功能分支

---

## 最后更新

- **更新时间**: 2026-03-07
- **更新人**: AI Assistant
- **备注**:
  - 添加 feat/monitoring-alerting 分支（系统监控与告警）
  - 添加 feat/unified-admin-dashboard 分支（统一管理后台）
  - 统一管理后台功能已完成，包含用户管理、留言管理、监控管理三大模块
