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
├── INIT_DATABASE_GUIDE.md              # 数据库初始化指南
├── init_database.sql                   # 完整初始化脚本 v2.0 (新建环境,已包含所有补丁)
├── init_database.bat                   # Windows自动化Windows自动化初始化脚本
├── init_database.sh                    # Linux/macOS自动化初始化脚本
├── patches/                            # 补丁脚本目录(用于旧版本升级)
│   ├── UPGRADE_v2.0_README.md          # v2.0升级指南
│   ├── upgrade_v2.0_integration.sql    # 整合版补丁脚本(v2.1-v2.5)
│   ├── apply_upgrade_v2.0.bat          # Windows自动化升级脚本
│   └── apply_upgrade_v2.0.sh           # Linux/macOS自动化升级脚本
├── upgrade_case_v2.8.sql               # 可选: 工单满意度评价表(v2.8)
├── upgrade_case_v2.9_force_password_change.sql  # 可选: 强制修改密码(v2.9)
└── legacy/                             # 旧版脚本(已废弃)
    ├── migrate_case_db.sql
    ├── patch_kb_name_length.sql
    └── README_KB_NAME_PATCH.md
```

## 使用场景

### 场景1: 全新安装(新环境)

使用 `init_database.sql` 创建所有数据库、表结构和初始数据。

**执行方式:**

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

**注意事项:**
- 此脚本会创建三个新数据库
- 包含完整的表结构和初始数据
- 默认管理员账号: `admin` / `YHKB@2024`
- **版本 v2.0 已包含所有补丁内容，无需额外执行补丁脚本**
- 包含强制修改密码功能(`force_password_change`字段)

### 场景2: 升级现有数据库(已部署环境)

使用 `patches/` 目录下的整合补丁脚本升级现有数据库。

**版本历史:**

- **v2.0** (当前版本): 整合版补丁，包含 v2.1-v2.5 的所有变更
  - 工单表新增: assignee, resolution, submit_user, customer_contact_name, cc_emails
  - 知识库名称字段长度: VARCHAR(500)
  - 用户表新增: display_name, company_name, phone, force_password_change
  - 删除废弃字段: password_md5, real_name

**升级步骤:**

```bash
# 1. 备份数据库(重要!)
mysqldump -h localhost -u root -p \
  --databases clouddoors_db YHKB casedb > backup_$(date +%Y%m%d).sql

# 2. 执行整合版补丁脚本
# Windows:
cd database/patches
apply_upgrade_v2.0.bat root

# Linux/macOS:
cd database/patches
chmod +x apply_upgrade_v2.0.sh
./apply_upgrade_v2.0.sh root

# 方式2: 直接执行SQL
mysql -h localhost -u root -p < database/patches/upgrade_v2.0_integration.sql

# 3. 验证升级结果(见升级指南)
```

**详细说明:** 参见 `patches/UPGRADE_v2.0_README.md`

**注意事项:**
- 升级前务必备份数据
- 整合补丁脚本已包含 v2.1-v2.5 所有补丁，一次性执行即可
- 补丁是幂等的,可重复执行

### 场景3: 可选补丁

以下补丁不在整合版 v2.0 中，需要单独执行:

**v2.8 - 工单满意度评价表:**

```bash
mysql -h localhost -u root -p casedb < database/upgrade_case_v2.8.sql
```

**v2.9 - 强制修改密码字段:**
> 注意: 此补丁已整合到 v2.0 版本，新系统无需单独执行

### 场景4: 部分补丁修复

如果只需要应用某个特定补丁,可以直接手动修改SQL文件或执行特定部分。

## 补丁脚本说明

### v2.0 整合版升级包

**⚠️ 重要提示**: `init_database.sql` 已升级到 v2.0 版本，包含本升级包的所有内容。
- **全新安装**: 直接使用 `init_database.sql` 即可，无需执行补丁
- **从旧版本升级**: 需要执行 `patches/upgrade_v2.0_integration.sql`

**包含补丁:**

1. **知识库系统 (YHKB):**
   - 扩展 `KB_Name` 字段长度到 VARCHAR(500)
   - 删除废弃字段: `password_md5`, `real_name`
   - 添加新字段: `display_name`, `company_name`, `phone`, `force_password_change`
   - 在 `mgmt_login_logs` 表添加 `display_name` 字段

2. **工单系统 (casedb):**
   - 添加 `assignee` 字段(处理人)
   - 添加 `resolution` 字段(解决方案)
   - 添加 `submit_user` 字段(提交用户)
   - 添加 `customer_contact_name` 字段(联系人姓名)
   - 添加 `cc_emails` 字段(抄送邮箱)

详细说明见 `patches/UPGRADE_v2.0_README.md`。

## 数据库结构概览

### clouddoors_db (官网系统)

**表结构:**
- `messages` - 官网留言表

### YHKB (知识库系统)

**表结构:**
- `KB-info` - 知识库信息表
- `users` - 统一用户表(与工单系统共用)
- `mgmt_login_logs` - 知识库登录日志表

### casedb (工单系统)

**表结构:**
- `tickets` - 工单表
- `messages` - 工单聊天消息表
- `satisfaction` - 工单满意度评价表 (可选，v2.8)

**重要:**
- `casedb.users` 表已废弃,统一使用 `YHKB.users` 表
- 工单系统通过 `submit_user` 字段关联统一用户表

## 版本管理规范

### 命名规范

**初始化脚本:**
- 文件名: `init_database.sql`
- 位置: `database/` 根目录
- 作用: 创建完整的数据库环境

**补丁脚本:**
- 目录名: `vX.Y_to_vZ.Q` (版本范围)
- 文件名: `NNN_description.sql` (序号 + 描述)
  - `NNN`: 三位数字序号(001, 002, 003...)
  - `description`: 简短描述(小写+下划线)
- 必须包含 `README.md` 说明文档

### 补丁开发规范

1. **幂等性**: 补丁可重复执行,不会报错
2. **安全性**: 不会删除数据,只修改结构
3. **可回滚**: 提供回滚SQL(在README中说明)
4. **验证性**: 包含验证SQL,确认修改成功
5. **文档化**: 详细说明变更内容和影响范围

**补丁模板:**

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
mysql -h localhost -u root -p < backup_all_20260213.sql

# 恢复单个数据库
mysql -h localhost -u root -p YHKB < backup_yhkb_20260213.sql
```

## 常见问题

### Q1: 执行补丁时报错 "Duplicate column name"
**A:** 补丁已具备幂等性,会自动跳过已存在的字段/索引,可忽略此提示。

### Q2: 升级后数据丢失
**A:** 请立即停止应用,从备份文件恢复,并检查补丁SQL是否有删除操作。

### Q3: 如何知道当前数据库版本
**A:** 查看 `patches/` 目录下已执行的补丁,或查询数据库表结构推断版本。

### Q4: 补丁执行中断怎么办
**A:** 重新执行补丁即可,补丁已设计为幂等操作,不会重复应用变更。

### Q5: 如何回滚补丁
**A:** 查看对应补丁的 `README.md`,其中有详细的回滚SQL脚本。

## 安全建议

1. **定期备份**: 每天至少备份一次数据库
2. **升级前备份**: 执行补丁前必须备份
3. **测试环境验证**: 先在测试环境验证补丁,再应用到生产环境
4. **权限控制**: 生产环境数据库账号应限制为必需的最小权限
5. **审计日志**: 记录所有数据库变更操作

## 联系支持

如有数据库相关问题,请联系技术支持团队。

---

**最后更新**: 2026-02-27
**维护人员**: 云户科技技术团队
**文档版本**: 2.0
