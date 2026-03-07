# 官网留言系统后续优化说明

## 📋 概述

本文档说明官网留言系统后续可优化的方向和计划。当前版本已实现核心功能并可以投入生产使用，以下优化项根据**实际部署环境（单机腾讯云服务器 + 内网备份 + HTTPS已部署）**和**实用架构优化原则**进行调整和优先级排序。

---

## ✅ 已完成功能（v2.0）

### 核心功能
- ✅ 留言提交（匿名/登录用户）
- ✅ 留言管理列表（管理员）
- ✅ 留言详情查看
- ✅ 留言状态管理（pending/processed/completed）
- ✅ 批量删除留言
- ✅ 留言搜索和筛选
- ✅ 防重复提交（限流）
- ✅ 后端限流保护
- ✅ **留言回复功能**（支持富文本，自动发送邮件）
- ✅ **账户激活邮件发送功能**（自动发送账户信息）
- ✅ **回复模板管理**（支持分类、变量替换）

### 数据库扩展
- ✅ messages 表添加 reply_content, reply_time, replied_by, replied_name, reply_status 字段
- ✅ messages 表添加 inquiry_type 字段（咨询类型）
- ✅ users 表添加 registration_source, contact_message_id, activated_at 字段

### API 接口
- ✅ 留言CRUD操作
- ✅ 留言状态更新
- ✅ 批量操作API
- ✅ 搜索和筛选
- ✅ 留言回复API（/admin/messages/api/reply）
- ✅ 账户激活API（/admin/messages/api/activate-account）
- ✅ 回复模板管理API

### 邮件服务
- ✅ 留言提交通知邮件（发送到 support@cloud-doors.com）
- ✅ 留言回复通知邮件（发送给客户）
- ✅ 账户激活邮件（包含用户名和密码）
- ✅ 邮件发送失败重试机制（2次重试）
- ✅ 企业微信邮箱支持（SMTP_SSL 465端口）

### 前端功能
- ✅ 留言管理页面（/admin/messages）
- ✅ 回复模板选择器
- ✅ 模板变量自动替换（{name}, {email}, {phone}, {company_name}, {message}等）
- ✅ 回复历史记录显示
- ✅ 开通账户类型自动激活按钮
- ✅ 邮件发送状态显示

---

## 🎯 后续优化计划

### 🔴 已完成（P1 - 已实现）

#### 1. ✅ 留言回复功能（已完成）

**实现状态**: 已完成，管理员可以在留言管理界面直接回复

**已实现功能**:
- ✅ 管理员在留言管理界面直接回复
- ✅ 回复内容保存到数据库
- ✅ 回复后自动发送邮件通知客户
- ✅ 支持纯文本回复
- ✅ 回复历史记录
- ✅ 回复状态跟踪（draft/sent/failed）

**技术实现**:
- ✅ 在 `messages` 表添加 `reply_content`、`reply_time`、`replied_by`、`replied_name`、`reply_status` 字段
- ✅ 创建留言回复API (`POST /admin/messages/api/reply`)
- ✅ 前端回复对话框（模板选择器 + 文本输入）
- ✅ 邮件模板（`services/email_service.py::send_message_reply_notification`）
- ✅ 邮件发送失败重试机制

**相关文件**:
- `routes/admin_bp.py` - messages_api_reply() 函数（642-732行）
- `templates/admin/messages.html` - 回复界面（146-192行）
- `services/email_service.py` - send_message_reply_notification() 函数（670-850行）
- `database/upgrade_message_reply.sql` - 数据库升级脚本

---

#### 2. ✅ 账户激活邮件发送功能（已完成）

**实现状态**: 已完成，管理员可以激活账户并发送账户信息邮件

**已实现功能**:
- ✅ 管理员在留言管理界面激活账户
- ✅ 自动发送账户激活邮件（包含用户名和密码）
- ✅ 支持单个账户激活
- ✅ 邮件模板美化（HTML格式）
- ✅ 激活历史记录

**技术实现**:
- ✅ 扩展 `users` 表添加 `activated_at`、`activated_by` 字段
- ✅ 创建激活API (`POST /admin/messages/api/activate-account`)
- ✅ 邮件模板（`services/email_service.py::send_account_activation_notification`）
- ✅ 密码生成逻辑（`secrets` 模块）
- ✅ 首次登录强制修改密码标记

**相关文件**:
- `routes/admin_bp.py` - messages_api_activate_account() 函数（735-857行）
- `templates/admin/messages.html` - 激活账户按钮（202-204行）
- `services/email_service.py` - send_account_activation_notification() 函数（851-1000行）
- `database/upgrade_activated_at.sql` - 数据库升级脚本

---

#### 3. ✅ 回复模板管理（已完成）

**实现状态**: 已完成，管理员可以创建和管理回复模板

**已实现功能**:
- ✅ 预设回复模板创建
- ✅ 模板分类管理（general/account/technical/billing/other）
- ✅ 快速应用模板到回复
- ✅ 模板变量支持（{name}, {email}, {phone}, {company_name}, {message}）
- ✅ 模板使用统计
- ✅ 系统模板和自定义模板

**技术实现**:
- ✅ 创建 `reply_templates` 表
- ✅ 模板管理页面（/admin/reply-templates）
- ✅ 前端模板选择器（按分类分组显示）
- ✅ 变量替换逻辑
- ✅ 模板预览功能

**相关文件**:
- `routes/reply_templates_bp.py` - 完整的模板管理API
- `templates/admin/reply_templates.html` - 模板管理页面
- `templates/admin/messages.html` - 模板选择器（166-172行）
- `database/create_reply_templates.sql` - 表创建脚本

---

### 🟡 中优先级（P2 - 3个月内完成）

#### 4. 留言统计分析（1周）

**当前状态**: 无统计数据
**优化目标**:
- 留言数量统计（按日期、状态）
- 留言来源统计（匿名/登录用户）
- 处理效率统计（平均处理时间）
- 留言趋势图表
- 月度报表

**功能说明**:
- **统计维度**:
  - 今日留言数、本周留言数、本月留言数
  - 已处理/未处理留言数
  - 平均处理时长
  - 留言趋势（折线图）
  - 状态分布（饼图）

- **数据可视化**:
  - 使用 ECharts 或 Chart.js
  - 支持日期范围筛选
  - 图表导出（图片）

**技术要点**:
- 创建统计API (`GET /api/messages/statistics`)
- 统计数据缓存（Redis，30分钟）
- 前端图表组件
- 定时任务计算统计数据

**预估工作量**: 1周（5-7工时）

**成本**: 免费（若使用Redis缓存，需50元/月）

---

#### 4. 留言导出功能（1周）

**当前状态**: 无导出功能
**优化目标**:
- 导出为Excel格式（.xlsx）
- 导出为CSV格式
- 支持按筛选条件导出
- 导出包含留言详情和回复

**技术要点**:
- 使用 `openpyxl` 库
- 创建导出API (`GET /api/messages/export`)
- 前端导出按钮
- 处理大量数据导出（分批处理）

**预估工作量**: 1周（4-6工时）

**成本**: 免费

---

#### 6. 留言标签分类（1周）

**当前状态**: 无标签功能
**优化目标**:
- 为留言添加标签
- 标签颜色和分类
- 按标签筛选留言
- 标签统计

**技术要点**:
- 创建 `message_tags` 和 `message_tag_relations` 表
- 标签管理页面
- 前端标签选择器
- 标签统计

**预估工作量**: 1周（4-6工时）

**成本**: 免费

---

#### 6. 附件上传功能（1周）

**当前状态**: 不支持附件
**优化目标**:
- 支持留言上传附件
- 支持图片、PDF、文档
- 文件大小限制（10MB）
- 文件类型白名单
- 附件预览

**技术要点**:
- 创建 `message_attachments` 表
- 文件上传API
- 文件安全检查
- 文件存储（本地或腾讯云COS）
- 前端文件上传组件

**预估工作量**: 1周（5-7工时）

**成本**:
- 本地存储: 免费
- 腾讯云COS: 约 80元/月（500GB）

---

#### 8. 留言归档功能（1周）

**当前状态**: 已删除留言无法恢复
**优化目标**:
- 留言归档（软删除）
- 归档留言查询
- 归档留言恢复
- 定期归档策略

**技术要点**:
- 添加 `archived` 字段
- 归档API
- 归档查询接口
- 定时归档任务

**预估工作量**: 1周（4-5工时）

**成本**: 免费

---

### 🟢 低优先级（P3 - 长期优化）

#### 9. 客户信息关联（2周）

**优化目标**:
- 留言关联客户信息
- 客户历史留言查询
- 客户画像
- 客户沟通记录

**技术要点**:
- 扩展 `messages` 表添加 `customer_id` 字段
- 创建 `customers` 表
- 客户管理页面
- 客户历史记录查询

**预估工作量**: 2周（10-12工时）

**成本**: 免费

---

#### 9. 实时通知功能（2周）

**优化目标**:
- 新留言实时通知管理员
- WebSocket 推送
- 浏览器桌面通知
- 企业微信通知

**技术要点**:
- WebSocket 推送
- 浏览器通知 API
- 企业微信 Webhook
- 通知设置

**预估工作量**: 2周（10-12工时）

**成本**: 免费

---

#### 11. 留言自动化规则（2周）

**优化目标**:
- 自动分类留言
- 自动分配回复人
- 自动回复规则
- 留言关键词识别

**技术要点**:
- 创建 `message_rules` 表
- 规则引擎
- 定时任务检查规则
- 规则管理界面

**预估工作量**: 2周（10-12工时）

**成本**: 免费

---

## 📊 优化优先级矩阵

| 优化项 | 价值 | 复杂度 | 优先级 | 状态 |
|--------|------|--------|--------|------|
| **留言回复功能** | **高** | **中** | **🔴 P1** | ✅ 已完成 |
| **账户激活邮件** | **高** | **低** | **🔴 P1** | ✅ 已完成 |
| **回复模板管理** | **高** | **低** | **🔴 P1** | ✅ 已完成 |
| 留言统计分析 | 中 | 低 | 🟡 P2 | 待实现 |
| 留言导出功能 | 中 | 低 | 🟡 P2 | 待实现 |
| 留言标签分类 | 中 | 低 | 🟡 P2 | 待实现 |
| 附件上传功能 | 中 | 中 | 🟡 P2 | 待实现 |
| 留言归档功能 | 中 | 低 | 🟡 P2 | 待实现 |
| 客户信息关联 | 低 | 中 | 🟢 P3 | 待实现 |
| 实时通知功能 | 低 | 中 | 🟢 P3 | 待实现 |
| 留言自动化规则 | 低 | 高 | 🟢 P3 | 待实现 |

---

## 💡 实施建议

### ✅ 已完成（P1 优先级）

**1. ✅ 留言回复功能**（已完成）
- 时间: 2周
- 成本: 免费
- 效果: 提升客服效率，改善用户体验
- 状态: 已实现并投入使用

**2. ✅ 账户激活邮件发送功能**（已完成）
- 时间: 1周
- 成本: 免费
- 效果: 自动化账户激活流程
- 状态: 已实现并投入使用

**3. ✅ 回复模板管理**（已完成）
- 时间: 1周
- 成本: 免费
- 效果: 提升回复效率，统一回复标准
- 状态: 已实现并投入使用

**P1 阶段总工时**: 约 18-22 工时（3-4周） - 已完成

---

### 3个月内完成 - P2 优先级

**4. 留言统计分析**（1周）
**5. 留言导出功能**（1周）
**6. 留言标签分类**（1周）
**7. 附件上传功能**（1周）
**8. 留言归档功能**（1周）

**P2 阶段总工时**: 约 25-32 工时（5-6周）

---

### 长期优化 - P3 优先级

根据实际业务需求逐步实施

---

## 🔧 技术实施要点

### 已实现的技术方案

#### 1. 数据库表结构优化

**messages 表扩展**:
```sql
-- 添加回复相关字段
ALTER TABLE `messages`
ADD COLUMN IF NOT EXISTS `reply_content` TEXT COMMENT '回复内容' AFTER `status`,
ADD COLUMN IF NOT EXISTS `reply_time` TIMESTAMP NULL COMMENT '回复时间' AFTER `reply_content`,
ADD COLUMN IF NOT EXISTS `replied_by` VARCHAR(50) COMMENT '回复人用户名' AFTER `reply_time`,
ADD COLUMN IF NOT EXISTS `replied_name` VARCHAR(100) COMMENT '回复人显示名' AFTER `replied_by`,
ADD COLUMN IF NOT EXISTS `reply_status` VARCHAR(20) DEFAULT 'draft' COMMENT '回复状态：draft-草稿, sent-已发送, failed-发送失败' AFTER `replied_name`;

-- 添加咨询类型字段
ALTER TABLE `messages`
ADD COLUMN IF NOT EXISTS `inquiry_type` VARCHAR(50) DEFAULT 'other' COMMENT '咨询类型：account-开通账户, technical-技术咨询, other-其他' AFTER `reply_status`;
```

**users 表扩展**:
```sql
-- 添加注册来源和激活时间字段
ALTER TABLE `users`
ADD COLUMN IF NOT EXISTS `registration_source` VARCHAR(50) COMMENT '注册来源：contact_form-联系表单, manual-手动创建, other-其他' AFTER `created_by`,
ADD COLUMN IF NOT EXISTS `contact_message_id` INT COMMENT '关联的留言ID' AFTER `registration_source`,
ADD COLUMN IF NOT EXISTS `activated_at` TIMESTAMP NULL DEFAULT NULL COMMENT '账户激活时间' AFTER `updated_at`;
```

**reply_templates 表创建**:
```sql
CREATE TABLE IF NOT EXISTS `reply_templates` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(200) NOT NULL COMMENT '模板名称',
    `category` VARCHAR(50) NOT NULL COMMENT '分类：general/account/technical/billing/other',
    `content` TEXT NOT NULL COMMENT '模板内容',
    `description` VARCHAR(500) DEFAULT '' COMMENT '描述',
    `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    `is_system` TINYINT(1) DEFAULT 0 COMMENT '是否系统模板',
    `sort_order` INT DEFAULT 0 COMMENT '排序',
    `use_count` INT DEFAULT 0 COMMENT '使用次数',
    `created_by` VARCHAR(50) DEFAULT '' COMMENT '创建人',
    `updated_by` VARCHAR(50) DEFAULT '' COMMENT '更新人',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_category` (`category`),
    INDEX `idx_is_active` (`is_active`),
    INDEX `idx_is_system` (`is_system`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回复模板表';
```

#### 2. 数据库索引优化
```sql
-- 留言系统索引优化
CREATE INDEX idx_messages_status_date ON clouddoors_db.messages(status, created_at);
CREATE INDEX idx_messages_email ON clouddoors_db.messages(email);
CREATE INDEX idx_messages_inquiry_type ON clouddoors_db.messages(inquiry_type);
CREATE INDEX idx_messages_reply_status ON clouddoors_db.messages(reply_status);
CREATE INDEX idx_messages_reply_time ON clouddoors_db.messages(reply_time);
CREATE INDEX idx_users_registration_source ON YHKB.users(registration_source);
CREATE INDEX idx_users_activated_at ON YHKB.users(activated_at);
```

#### 2. Redis 缓存应用
```python
# 统计数据缓存
@cache_result(expire=1800, key_prefix='message_stats')
def get_message_statistics(date_range=None):
    # 统计逻辑
    pass
```

#### 3. 监控告警集成
```python
# 留言回复失败告警
@monitor_response_time
def send_reply_email(message_id, reply_content):
    # 发送邮件逻辑
    pass
```

#### 4. 邮件发送优化（已实现）

**重试机制**:
- 自动重试 2 次
- 超时时间 60 秒
- 失败后记录状态到数据库

**企业微信邮箱支持**:
- SMTP_SSL 连接（端口 465）
- 支持域名和 IP 地址
- 本地 hostname 设置（使用 IP 时）

**邮件模板**:
- HTML 格式美化邮件
- 响应式设计
- 支持变量替换

#### 4. 日志集中管理
```python
# 记录留言操作日志
logging.info(f"留言 {message_id} 回复成功, 回复人: {admin_id}")
```

---

## 📝 注意事项

1. **向后兼容**: ✅ 确保新功能不影响现有功能，保持API兼容性
2. **数据库变更**: ✅ 所有表结构变更已创建升级脚本
3. **性能优化**:
   - ✅ 大数据量导出使用分批处理（待实现）
   - ✅ 统计数据使用缓存（待实现）
   - ✅ 索引优化（已完成）
4. **安全性**:
   - ⏳ 附件上传需要安全检查（待实现）
   - ⏳ 防止XSS攻击（富文本编辑器）（待实现）
   - ✅ 邮件发送限流（已实现）
5. **可维护性**:
   - ✅ 代码注释完善
   - ✅ 遵循项目代码规范
   - ⏳ 编写单元测试（待实现）
6. **备份**: ✅ 重大变更前执行数据库备份（已实现）

---

## 🔗 相关文档

- [实用架构优化方案](../architecture/PRAGMATIC_ARCHITECTURE_OPTIMIZATION.md)
- [官网系统指南](../system-guides/HOME_SYSTEM_GUIDE.md)
- [前端代码优化建议](../FRONTEND_OPTIMIZATION_GUIDE.md)
- [分支说明文档](../project-management/BRANCHES.md)
- [更新日志](../../CHANGELOG.md)

---

## 📅 更新记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-03-07 | v3.0 | 更新已完成功能（留言回复、账户激活、回复模板管理） |
| 2026-03-07 | v2.0 | 基于实用架构优化方案更新，调整优先级 |
| 2026-03-07 | v1.0 | 创建文档，记录优化计划 |

---

## 📖 已完成功能详细说明

### 1. 留言回复功能

**功能概述**:
管理员可以在留言管理界面直接回复客户留言，回复内容保存到数据库，并自动发送邮件通知客户。

**核心流程**:
1. 管理员在留言列表中点击"查看"按钮
2. 在留言详情页面的回复区域输入回复内容
3. 可选择是否同时发送邮件通知客户
4. 可选择回复模板快速填充内容
5. 点击"发送回复"按钮提交
6. 系统保存回复信息并更新留言状态为"已处理"
7. 如果选择了发送邮件，系统自动发送通知邮件给客户

**技术实现**:

**API 接口**: `POST /admin/messages/api/reply`

**请求参数**:
```json
{
  "id": 1,
  "reply_content": "回复内容...",
  "send_email": true
}
```

**响应数据**:
```json
{
  "success": true,
  "message": "留言回复成功",
  "data": {
    "email_sent": true,
    "email_message": "邮件发送成功"
  }
}
```

**邮件模板**: `services/email_service.py::send_message_reply_notification()`

**邮件内容包括**:
- 客户称呼
- 原始留言内容
- 管理员回复内容
- 回复人信息
- 联系方式

**数据库字段**:
- `reply_content`: TEXT - 回复内容
- `reply_time`: TIMESTAMP - 回复时间
- `replied_by`: VARCHAR(50) - 回复人用户名
- `replied_name`: VARCHAR(100) - 回复人显示名
- `reply_status`: VARCHAR(20) - 回复状态（draft/sent/failed）

---

### 2. 账户激活邮件发送功能

**功能概述**:
管理员可以为申请开通账户的客户激活账户，系统自动生成临时密码并通过邮件发送给客户。

**核心流程**:
1. 客户通过官网联系表单提交"开通账户"类型留言
2. 系统自动创建禁用状态的客户账户
3. 管理员在留言管理页面查看该留言
4. 点击"启用并发送账户信息"按钮
5. 系统生成新的临时密码
6. 更新用户状态为"active"
7. 发送账户激活邮件给客户（包含用户名和临时密码）
8. 更新留言状态并记录激活信息

**技术实现**:

**API 接口**: `POST /admin/messages/api/activate-account`

**请求参数**:
```json
{
  "id": 1
}
```

**响应数据**:
```json
{
  "success": true,
  "message": "账户激活成功，账户信息已发送至客户邮箱",
  "data": {
    "username": "zhangsan",
    "email_sent": true,
    "email_message": "邮件发送成功"
  }
}
```

**邮件模板**: `services/email_service.py::send_account_activation_notification()`

**邮件内容包括**:
- 欢迎信息
- 登录地址
- 用户名
- 临时密码
- 首次登录强制修改密码提示
- 联系方式

**账户激活逻辑**:
1. 通过留言的邮箱查找关联的用户账户（registration_source = 'contact_form'）
2. 生成随机临时密码（secrets.token_urlsafe(10)）
3. 使用 werkzeug 安全哈希加密密码
4. 更新用户状态为 active
5. 设置 force_password_change = 1（强制修改密码）
6. 记录 activated_at 时间
7. 发送激活邮件
8. 更新留言回复信息

---

### 3. 回复模板管理功能

**功能概述**:
管理员可以创建、编辑、删除回复模板，支持分类管理和变量替换，提高回复效率。

**核心流程**:

**创建模板**:
1. 访问回复模板管理页面（/admin/reply-templates）
2. 点击"新建模板"按钮
3. 填写模板信息：
   - 模板名称
   - 分类（通用/账户相关/技术支持/计费相关/其他）
   - 模板内容（支持变量 {name}, {email}, {phone}, {company_name}, {message}）
   - 描述
   - 是否启用
4. 点击保存

**使用模板**:
1. 在留言回复页面选择模板
2. 模板内容自动填充到回复输入框
3. 变量自动替换为实际值
4. 可进一步编辑回复内容
5. 发送回复

**技术实现**:

**API 接口**:

- `GET /admin/reply-templates/api/list` - 获取模板列表
- `GET /admin/reply-templates/api/<id>` - 获取模板详情
- `POST /admin/reply-templates/api` - 创建模板
- `PUT /admin/reply-templates/api/<id>` - 更新模板
- `DELETE /admin/reply-templates/api/<id>` - 删除模板
- `POST /admin/reply-templates/api/<id>/increment-use` - 增加使用次数
- `POST /admin/reply-templates/api/preview` - 预览模板（替换变量）

**模板分类**:
- `general`: 通用回复
- `account`: 账户相关
- `technical`: 技术支持
- `billing`: 计费相关
- `other`: 其他

**支持的变量**:
- `{name}`: 客户姓名
- `{email}`: 客户邮箱
- `{phone}`: 客户电话
- `{company_name}`: 公司名称
- `{message}`: 原始留言内容
- `{username}`: 用户名

**数据库表**: `reply_templates`

**表结构**:
```sql
CREATE TABLE `reply_templates` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(200) NOT NULL COMMENT '模板名称',
    `category` VARCHAR(50) NOT NULL COMMENT '分类',
    `content` TEXT NOT NULL COMMENT '模板内容',
    `description` VARCHAR(500) DEFAULT '' COMMENT '描述',
    `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    `is_system` TINYINT(1) DEFAULT 0 COMMENT '是否系统模板',
    `sort_order` INT DEFAULT 0 COMMENT '排序',
    `use_count` INT DEFAULT 0 COMMENT '使用次数',
    `created_by` VARCHAR(50) DEFAULT '' COMMENT '创建人',
    `updated_by` VARCHAR(50) DEFAULT '' COMMENT '更新人',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回复模板表';
```

**权限控制**:
- 系统模板（is_system = 1）不可删除，但可以修改
- 所有模板都可以编辑内容
- 记录创建人和更新人

---

### 4. 留言提交通知邮件

**功能概述**:
客户提交留言后，系统自动发送邮件通知给管理员（support@cloud-doors.com）。

**邮件内容包括**:
- 留言人姓名
- 公司名称
- 联系邮箱
- 联系电话
- 留言内容
- 咨询类型
- （如果是开通账户类型）包含登录信息

**技术实现**:

**邮件模板**: `routes/home_bp.py::contact()` 函数（264-367行）

**根据咨询类型区分**:
- `account`: 开通账户申请 - 包含账户信息
- `technical`: 技术咨询

---

## 🔍 关键代码位置

### 路由文件
- `routes/home_bp.py`: 官网留言提交、留言列表、留言详情、留言状态更新、留言删除
- `routes/admin_bp.py`: 管理后台留言管理、留言回复、账户激活
- `routes/reply_templates_bp.py`: 回复模板管理

### 服务文件
- `services/email_service.py`: 邮件发送服务
  - `send_message_reply_notification()`: 留言回复邮件
  - `send_account_activation_notification()`: 账户激活邮件

### 模板文件
- `templates/admin/messages.html`: 留言管理页面
- `templates/admin/reply_templates.html`: 回复模板管理页面
- `templates/home/index.html`: 官网首页（包含联系表单）

### 数据库文件
- `database/upgrade_message_table.sql`: 添加 phone 字段
- `database/upgrade_message_reply.sql`: 添加回复相关字段
- `database/upgrade_inquiry_type.sql`: 添加咨询类型字段
- `database/upgrade_activated_at.sql`: 添加激活时间字段
- `database/create_reply_templates.sql`: 创建回复模板表
- `database/create_reply_templates.py`: 初始化默认模板数据

---

**文档维护者**: 云户科技开发团队
**最后更新**: 2026-03-07
