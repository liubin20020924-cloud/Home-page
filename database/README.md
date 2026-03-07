# 数据库脚本管理文档

## 概述

本文档描述云户科技系统的数据库脚本组织结构和使用方法。系统包含三个数据库:
- `clouddoors_db` - 官网系统
- `YHKB` - 知识库系统
- `casedb` - 工单系统

## 脚本目录结构

```
database/
├── README.md                           # 本文档
├── INIT_DATABASE_GUIDE.md              # 数据库数据库初始化指南
├── init_database.sql                   # 完整初始化脚本 v2.0 (全新安装，包含所有功能)
├── upgrade_to_v2.sql                   # 数据库升级脚本 v1.0→v2.0 (升级现有数据库)
├── init_database.bat                   # Windows自动化初始化脚本
├── init_database.sh                    # Linux/macOS自动化初始化脚本
├── execute_upgrade.py                  # Python升级脚本执行器
├── create_reply_templates.py           # 回复模板数据复模板数据初始化脚本
└── legacy/                             # 旧版脚本(已废弃)
    ├── migrate_case_db.sql
    ├── patch_kb_name_length.sql
    └── README_KB_NAME_PATCH.md
```

## 使用场景

### ⚠️ 重要提示：选择正确的脚本

**请根据你的实际情况选择合适的脚本：**

- **全新安装**（全新数据库）→ 使用 `init_database.sql`
- **升级现有数据库**（已有数据）→ 使用 `upgrade_to_v2.sql`
- **不要**在已有数据的数据库上执行 `init_database.sql`

### 场景1: 全新安装 (全新环境)

使用 `init_database.sql` 创建所有数据库、表结构和初始数据。

**适用情况：**
- ✅ 全新安装的服务器
- ✅ 数据库尚未创建
- ✅ 可以清空数据库重建

**执行方式：**

```bash
# 方式1: 使用自动化脚本(推荐)
# Windows:
cd database
init_database.bat root

# Linux/macOS:
cd database
chmod +x init_database.sh
./init_database.sh root

# 方式2: MySQL客户端
mysql -h localhost -u root -p < database/init_database.sql
```

**详细说明:** 参见 `INIT_DATABASE_GUIDE.md`

**注意事项：**
- 此脚本会**创建三个新数据库**
- 包含完整的表结构和初始数据
- 默认管理员账号: `admin` / `YHKB@2024`
- 版本 v2.0 包含所有功能（留言系统、回复模板、账户激活等）
- **⚠️ 不可在已有数据的数据库上执行！**

### 场景2: 升级现有数据库 (已部署环境)

使用 `upgrade_to_v2.sql` 升级现有数据库。

**适用情况：**
- ✅ 已有运行中的生产数据库
- ✅ 数据库中已有数据（用户、留言、工单等）
- ✅ 需要添加新字段但不影响现有数据
- ✅ 保留所有现有数据

**执行方式：**

```bash
# 1. 备份数据库(重要!)
mysqldump -h localhost -u root -p \
  --databases clouddoors_db YHKB casedb > backup_$(date +%Y%m%d).sql

# 2. 执行升级脚本
mysql -h localhost -u root -p < database/upgrade_to_v2.sql

# 3. 验证升级结果
# 脚本会自动显示升级结果和表结构
```

**升级内容：**

1. **messages 表 (官网留言表)**
   - 添加 `phone` 字段
   - 添加 `company_name` 字段
   - 添加回复相关字段：`reply_content`, `reply_time`, `replied_by`, `replied_name`, `reply_status`
   - 添加 `inquiry_type` 字段（咨询类型）
   - 创建所有相关索引

2. **users 表 (统一用户表)**
   - 添加 `registration_source` 字段（注册来源）
   - 添加 `contact_message_id` 字段（关联留言ID）
   - 添加 `activated_at` 字段（激活时间）
   - 创建相关索引

3. **reply_templates 表 (回复模板表)**
   - 创建完整的回复模板表
   - 插入 5 个系统预设模板

**注意事项：**
- ⚠️ 升级前**务必备份数据**
- ✅ 脚本是幂等的，可重复执行
- ✅ 使用 `ADD COLUMN IF NOT EXISTS` 安全升级
- ✅ 不会影响现有数据
- ✅ 只添加缺失的字段和表

### 场景3: 旧版本升级 (从 v2.1-v2.5)

如果你的数据库版本是 v2.1-v2.5，需要先升级到 v2.0，然后再使用 `upgrade_to_v2.sql`。

详见 `patches/UPGRADE_v2.0_README.md`。

## 数据库结构概览

### clouddoors_db (官网系统)

**表结构：**
- `messages` - 官网留言表（完整版本，包含回复和咨询类型字段）
- `reply_templates` - 回复模板表

### YHKB (知识库系统)

**表结构：**
- `KB-info` - 知识库信息表
- `users` - 统一用户表（与工单系统共用）
- `mgmt_login_logs` - 知识库登录日志表

### casedb (工单系统)

**表结构：**
- `tickets` - 工单表
- `messages` - 工单聊天消息表
- `satisfaction` - 工单满意度评价表

**重要：**
- `casedb.users` 表已废弃，统一使用 `YHKB.users` 表
- 工单系统通过 `submit_user` 字段关联统一用户表

## 版本管理规范

### 命名规范

**初始化脚本：**
- 文件名：`init_database.sql`
- 位置：`database/` 根目录
- 作用：创建完整的数据库环境（全新安装）

**升级脚本：**
- 文件名：`upgrade_to_vX.sql`
- 位置：`database/` 根目录
- 作用：升级现有数据库结构
- 格式：`upgrade_to_vX.sql`（X 是目标版本号）

**补丁脚本：**
- 目录名：`vX.Y_to_vZ.Q`（版本范围）
- 文件名：`NNN_description.sql`（序号 + 描述）
  - `NNN`：三位数字序号(001, 002, 003...)
  - `description`：简短描述(小写+下划线)
- 必须包含 `README.md` 说明文档

### 补丁开发规范

1. **幂等性**：补丁可重复执行，不会报错
2. **安全性**：不会删除数据，只修改结构
3. **可回滚**：提供回滚SQL（在README中说明）
4. **验证性**：包含验证SQL，确认修改成功
5. **文档化**：详细说明变更内容和影响范围

**补丁模板：**

```sql
-- =====================================================
-- 补丁描述: [简短描述]
-- 影响数据库: [数据库名]
-- 创建时间: [YYYY-MM-DD]
-- 版本范围: v2.1 -> v2.2
-- =====================================================

USE `[数据库名]`;

-- 1. 检查是否已应用
-- (使用INFORMATION_SCHEMA检查字段/索引是否存在)

-- 2. 执行修改
-- ALTER TABLE / CREATE INDEX 等

-- 3. 验证结果
-- 查询表结构或数据确认修改成功

-- 4. 完成提示
SELECT '补丁执行完成!' AS status;
```

## 备份与恢复

### 备份

```bash
# 备份所有数据库
mysqldump -h localhost -u root -p \
  --databases clouddoors_db YHKB casedb \
  --single-transaction \
  --routines \
  --triggers \
  > backup_all_$(date +%Y%m%d_%H%M%S).sql

# 备份单个数据库
mysqldump -h localhost -u root -p \
  YHKB > backup_yhkb_$(date +%Y%m%d).sql

# 仅备份数据(不含结构)
mysqldump -h localhost -u root -p \
  --no-create-info \
  YHKB > backup_yhkb_data_$(date +%Y%m%d).sql
```

### 恢复

```bash
# 恢复所有数据库
mysql -h localhost -u root -p < backup_all_20260307.sql

# 恢复单个数据库
mysql -h localhost -u root -p YHKB < backup_yhkb_20260307.sql
```

## 常见问题

### Q1: 我该使用哪个脚本？

**A：**
- 全新安装（无数据）→ `init_database.sql`
- 升级现有数据库（有数据）→ `upgrade_to_v2.sql`
- **⚠️ 不要在已有数据的数据库上执行 `init_database.sql`！**

### Q2: 执行升级脚本时报错 "Duplicate column name"

**A：** 升级脚本使用 `ADD COLUMN IF NOT EXISTS`，已具备幂等性，会自动跳过已存在的字段/索引，可忽略此提示。

### Q3: 升级后数据丢失

**A：** 请立即停止应用，从备份文件恢复，并检查升级SQL是否有删除操作。

### Q4: 如何知道当前数据库版本

**A：** 查询数据库表结构：
```sql
-- 检查 messages 表是否有 inquiry_type 字段（v2.0 新增）
SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'clouddoors_db' AND TABLE_NAME = 'messages' AND COLUMN_NAME = 'inquiry_type';

-- 检查 reply_templates 表是否存在（v2.0 新增）
SHOW TABLES FROM clouddoors_db LIKE 'reply_templates';
```

### Q5: 升级脚本执行中断怎么办

**A：** 重新执行升级脚本即可，脚本已设计为幂等操作，不会重复应用变更。

### Q6: init_database.sql 和 upgrade_to_v2.sql 的区别？

**A：**
- `init_database.sql`：全新安装，**创建**所有数据库和表
- `upgrade_to_v2.sql`：升级现有数据库，**添加**缺失的字段和表
- `init_database.sql` 包含 `upgrade_to_v2.sql` 的所有内容

### Q7: 可以在已有数据的数据库上执行 init_database.sql 吗？

**A：** **不可以！**
- `CREATE TABLE IF NOT EXISTS` 只会跳过已存在的表
- **不会添加新字段或修改现有表结构**
- 结果是：表结构没有更新，新功能无法使用

## 安全建议

1. **定期备份**：每天至少备份一次数据库
2. **升级前备份**：执行升级脚本前必须备份
3. **测试环境验证**：先在测试环境验证脚本，再应用到生产环境
4. **权限控制**：生产环境数据库账号应限制为必需的最小权限
5. **审计日志**：记录所有数据库变更操作

## 快速参考

| 场景 | 使用脚本 | 说明 |
|------|---------|------|
| 全新安装 | `init_database.sql` | 创建所有数据库和表 |
| 升级现有数据库 | `upgrade_to_v2.sql` | 添加新字段和表，保留数据 |
| 旧版本升级 | `patches/upgrade_v2.0_integration.sql` | 从 v2.1-v2.5 升级 |

## 联系支持

如有数据库相关问题，请联系技术支持团队。

---

**最后更新**: 2026-03-07
**维护人员**: 云户科技技术团队
**文档版本**: 3.0
