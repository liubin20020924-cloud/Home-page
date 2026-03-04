# 数据库初始化指南

## 概述

本指南用于指导全新部署云户科技网站系统的数据库初始化。

**版本:** v2.0  
**创建时间:** 2026-02-27  
**适用场景:** 全新部署系统

## 文件说明

- `init_database.sql` - 数据库初始化SQL脚本
- `init_database.bat` - Windows自动化脚本
- `init_database.sh` - Linux/macOS自动化脚本

## 初始化内容

本脚本将创建三个数据库及其相关表：

### 1. 官网系统数据库 (clouddoors_db)
- `messages` - 官网留言表

### 2. 知识库系统数据库 (YHKB)
- `KB-info` - 知识库信息表
- `users` - 统一用户表
- `mgmt_login_logs` - 知识库登录日志表

### 3. 工单系统数据库 (casedb)
- `tickets` - 工单表
- `messages` - 工单聊天消息表
- `satisfaction` - 工单满意度评价表

## 使用方法

### Windows系统

1. 打开命令提示符(CMD)或PowerShell
2. 进入database目录：
   ```cmd
   cd e:\Integrate-code\database
   ```
3. 执行初始化脚本：
   ```cmd
   init_database.bat root
   ```
4. 按提示输入MySQL密码

### Linux/macOS系统

1. 打开终端
2. 进入database目录：
   ```bash
   cd /path/to/Integrate-code/database
   ```
3. 添加执行权限（首次运行）：
   ```bash
   chmod +x init_database.sh
   ```
4. 执行初始化脚本：
   ```bash
   ./init_database.sh root
   ```
5. 按提示输入MySQL密码

### 手动执行

如需手动执行，可以使用以下命令：

```bash
mysql -u root -p < init_database.sql
```

## 默认账号

初始化完成后，系统会创建一个默认管理员账号：

- **用户名:** admin
- **密码:** YHKB@2024

⚠️ **重要:** 生产环境部署后请立即修改默认密码！

## 验证验证初始化

初始化脚本执行完成后，可以通过以下方式验证：

### 1. 检查数据库是否创建
```sql
SHOW DATABASES;
```

应该看到以下三个数据库：
- clouddoors_db
- YHKB
- casedb

### 2. 检查表是否创建
```sql
USE YHKB;
SHOW TABLES;

USE casedb;
SHOW TABLES;

USE clouddoors_db;
SHOW TABLES;
```

### 3. 检查默认用户
```sql
USE YHKB;
SELECT id, username, display_name, role, status FROM users;
```

应该看到admin用户已创建。

## 数据库配置

确保`config.py`中的数据库配置与初始化的数据库一致：

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

DATABASES = {
    'YHKB': 'YHKB',
    'casedb': 'casedb',
    'clouddoors_db': 'clouddoors_db'
}
```

## 注意事项

1. **MySQL权限**: 执行初始化的用户需要有创建数据库的权限
2. **字符集**: 数据库使用utf8mb4字符集，支持完整的Unicode字符
3. **密码安全**: 生产环境必须修改默认密码
4. **备份**: 建议在初始化前备份现有数据库（如有）
5. **版本兼容**: 本脚本适用于MySQL 5.7+或MariaDB 10.2+

## 故障排查

### 问题1: 无法连接MySQL

**解决方案:**
- 检查MySQL服务是否启动
- 检查用户名和密码是否正确
- 检查端口3306是否开放

### 问题2: 权限不足

**解决方案:**
- 确保MySQL用户有CREATE DATABASE权限
- 可以使用root用户执行初始化

### 问题3: 表已存在

**解决方案:**
- 脚本使用`CREATE TABLE IF NOT EXISTS`，不会重复创建表
- 如果表结构有问题，需要手动删除旧表后重新初始化

## 升级说明

如果是从旧版本升级系统，请使用`patches`目录下的升级脚本，**不要**使用本初始化脚本。

参见: `patches/UPGRADE_v2.0_README.md`

## 技术支持

如遇到问题，请检查：
1. MySQL/MariaDB版本是否符合要求
2. 数据库连接配置是否正确
3. 错误日志信息（logs/目录）

---

**文档版本:** v1.0  
**最后更新:** 2026-02-27
