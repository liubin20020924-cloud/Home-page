# 统一用户管理系统说明文档

## 概述

统一用户管理系统是云户科技网站的集中式用户管理平台，整合了知识库系统和工单系统的用户管理功能。通过一个统一的界面管理两个系统的用户，实现便捷的用户创建、编辑、删除和权限管理。

## 技术架构

### 后端技术
- **框架**: Flask (Python Web框架)
- **数据库**: MySQL
- **认证**: Session + Werkzeug Security (知识库) / MD5 (工单)
- **密码加密**: Werkzeug Security (PBKDF2) + MD5 (兼容)

### 前端技术
- **HTML5**: 页面结构
- **CSS3**: 现代化样式设计
- **Bootstrap 5**: 响应式UI框架
- **JavaScript**: 交互功能
- **jQuery**: DOM操作和AJAX

## 目录结构

```
modules/unified/
├── __init__.py                 # 模块初始化
├── routes.py                   # 统一用户管理路由
└── utils.py                    # 认证工具函数

templates/unified/              # 统一用户管理模板
└── user_management.html       # 用户管理界面

common/
└── db_manager.py               # 数据库连接管理
```

## 功能模块

### 1. 统一登录界面

#### 1.1 登录页面

**访问路径**: `/unified/login`

**功能说明**:
- 统一的登录入口
- 支持知识库和工单系统用户登录
- 自动识别用户所属系统

**登录字段**:
- 用户名
- 密码

**登录逻辑**:
1. 先尝试知识库系统登录（使用 Werkzeug Security）
2. 如果失败，尝试工单系统登录（使用 MD5）
3. 登录成功后跳转到用户管理页面

**关键代码位置**:
- 路由: `modules/unified/routes.py`
- 工具: `modules/unified/utils.py`

### 2. 用户管理界面

#### 2.1 用户管理首页

**访问路径**: `/user-mgmt/`

**功能说明**:
- 分标签页管理知识库和工单系统用户
- 实时用户统计
- 用户搜索和筛选
- 批量操作

**界面结构**:
```
┌─────────────────────────────────────────┐
│  统一用户管理系统                         │
├─────────────────────────────────────────┤
│  [统计信息]                              │
│  • 总用户数: 100                         │
│  • 活跃用户: 85                          │
│  • 今日登录: 12                          │
├─────────────────────────────────────────┤
│  [知识库用户] | [工单系统用户]           │
├─────────────────────────────────────────┤
│  用户列表                               │
│  • 搜索框                               │
│  • 添加用户按钮                         │
│  • 用户表格                             │
│  • 操作按钮（编辑/删除）                 │
└─────────────────────────────────────────┘
```

**主要功能**:
- 切换知识库/工单系统用户
- 查看用户列表
- 搜索用户（按用户名、邮箱）
- 添加新用户
- 编辑用户信息
- 删除用户
- 查看用户统计

**关键代码位置**:
- 路由: `modules/unified/routes.py`
- 模板: `templates/unified/user_management.html`

### 3. 知识库用户管理

#### 3.1 获取知识库用户列表

**接口**: `GET /unified/api/kb/users`

**参数**:
- `search`: 搜索关键词（可选）

**响应示例**:
```json
{
    "success": true,
    "users": [
        {
            "id": 1,
            "username": "admin",
            "display_name": "系统管理员",
            "email": "admin@example.com",
            "role": "admin",
            "status": "active",
            "last_login": "2026-02-06 10:00:00",
            "created_at": "2026-01-01 00:00:00"
        }
    ],
    "total": 10
}
```

#### 3.2 添加知识库用户

**接口**: `POST /unified/api/kb/users`

**请求参数**:
```json
{
    "username": "newuser",
    "password": "Password123!",
    "display_name": "新用户",
    "email": "newuser@example.com",
    "role": "user",
    "status": "active"
}
```

**密码要求**:
- 最小长度: 6位
- 必须包含字母和数字
- 使用 Werkzeug Security 加密（PBKDF2）

**响应示例**:
```json
{
    "success": true,
    "message": "用户创建成功",
    "user": {
        "id": 11,
        "username": "newuser",
        "display_name": "新用户",
        "role": "user",
        "status": "active"
    }
}
```

**错误响应**:
```json
{
    "success": false,
    "message": "用户名已存在"
}
```

#### 3.3 编辑知识库用户

**接口**: `PUT /unified/api/kb/users/<user_id>`

**请求参数**:
```json
{
    "username": "newuser",
    "display_name": "更新后的名称",
    "email": "updated@example.com",
    "role": "admin",
    "status": "active"
}
```

**注意**: admin 账号不能修改角色

**响应示例**:
```json
{
    "success": true,
    "message": "用户信息已更新"
}
```

#### 3.4 删除知识库用户

**接口**: `DELETE /unified/api/kb/users/<user_id>`

**注意**: admin 账号不能删除

**响应示例**:
```json
{
    "success": true,
    "message": "用户已删除"
}
```

#### 3.5 重置知识库用户密码

**接口**: `POST /unified/api/kb/users/<user_id>/reset-password`

**请求参数**:
```json
{
    "new_password": "NewPassword123!"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "密码已重置"
}
```

### 4. 工单系统用户管理

#### 4.1 获取工单系统用户列表

**接口**: `GET /unified/api/case/users`

**参数**:
- `search`: 搜索关键词（可选）

**响应示例**:
```json
{
    "success": true,
    "users": [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "phone": "13800138000",
            "full_name": "系统管理员",
            "role": "admin",
            "created_at": "2026-01-01 00:00:00",
            "last_login": "2026-02-06 10:00:00"
        }
    ],
    "total": 20
}
```

#### 4.2 添加工单系统用户

**接口**: `POST /unified/api/case/users`

**请求参数**:
```json
{
    "username": "newcustomer",
    "password": "Password123!",
    "email": "newcustomer@example.com",
    "phone": "13900139000",
    "full_name": "新客户",
    "role": "customer"
}
```

**密码要求**:
- 最小长度: 6位
- 使用 MD5 加密（兼容旧系统）

**响应示例**:
```json
{
    "success": true,
    "message": "用户创建成功",
    "user": {
        "id": 21,
        "username": "newcustomer",
        "email": "newcustomer@example.com",
        "role": "customer"
    }
}
```

#### 4.3 编辑工单系统用户

**接口**: `PUT /unified/api/case/users/<user_id>`

**请求参数**:
```json
{
    "username": "newcustomer",
    "email": "updated@example.com",
    "phone": "13900139000",
    "full_name": "更新后的名称",
    "role": "admin"
}
```

**注意**: admin 账号不能修改角色

**响应示例**:
```json
{
    "success": true,
    "message": "用户信息已更新"
}
```

#### 4.4 删除工单系统用户

**接口**: `DELETE /unified/api/case/users/<user_id>`

**注意**: admin 账号不能删除

**响应示例**:
```json
{
    "success": true,
    "message": "用户已删除"
}
```

#### 4.5 重置工单系统用户密码

**接口**: `POST /unified/api/case/users/<user_id>/reset-password`

**请求参数**:
```json
{
    "new_password": "NewPassword123!"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "密码已重置"
}
```

### 5. 用户统计

#### 5.1 获取用户统计信息

**接口**: `GET /unified/api/statistics`

**响应示例**:
```json
{
    "success": true,
    "statistics": {
        "kb": {
            "total_users": 10,
            "active_users": 8,
            "admin_users": 2,
            "regular_users": 6,
            "today_logins": 5
        },
        "case": {
            "total_users": 20,
            "active_users": 18,
            "admin_users": 3,
            "customer_users": 15,
            "today_logins": 8
        }
    }
}
```

### 6. 登录日志

#### 6.1 获取登录日志

**接口**: `GET /unified/api/login-logs`

**参数**:
- `system`: 系统类型（kb/case）
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20）

**响应示例**:
```json
{
    "success": true,
    "logs": [
        {
            "id": 1,
            "user_id": 1,
            "username": "admin",
            "ip_address": "192.168.X.X",
            "user_agent": "Mozilla/5.0...",
            "status": "success",
            "created_at": "2026-02-06 10:00:00"
        }
    ],
    "total": 100,
    "page": 1,
    "per_page": 20
}
```

## 数据库设计

### 知识库系统数据库 (YHKB)

#### 用户表 (mgmt_users)

```sql
CREATE TABLE mgmt_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,           -- 用户名
    password_hash VARCHAR(255) NOT NULL,            -- 密码哈希（Werkzeug）
    display_name VARCHAR(100),                      -- 显示名称
    email VARCHAR(100) UNIQUE,                      -- 邮箱
    role VARCHAR(20) DEFAULT 'user',                -- 角色: admin/user
    status VARCHAR(20) DEFAULT 'active',            -- 状态: active/inactive/locked
    last_login TIMESTAMP NULL,                      -- 最后登录时间
    login_attempts INT DEFAULT 0,                    -- 登录尝试次数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(50)                           -- 创建者
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 登录日志表 (mgmt_login_logs)

```sql
CREATE TABLE mgmt_login_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,                           -- 用户ID
    username VARCHAR(50) NOT NULL,                   -- 用户名
    ip_address VARCHAR(45),                          -- IP地址
    user_agent TEXT,                                -- 用户代理
    status VARCHAR(20),                             -- 登录状态: success/failed
    failure_reason VARCHAR(255),                    -- 失败原因
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 登录时间
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 工单系统数据库 (casedb)

#### 用户表 (users)

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,           -- 用户名
    password VARCHAR(255) NOT NULL,                 -- 密码（MD5）
    email VARCHAR(100) UNIQUE,                      -- 邮箱
    phone VARCHAR(20),                              -- 电话
    full_name VARCHAR(100),                         -- 全名
    role ENUM('admin', 'customer') DEFAULT 'customer',  -- 角色
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    last_login TIMESTAMP NULL,                      -- 最后登录时间
    is_active BOOLEAN DEFAULT TRUE                  -- 是否激活
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 配置说明

### 数据库配置

在 `config.py` 中配置：

```python
# 知识库数据库
DB_NAME_KB = 'YHKB'
DB_HOST = 'your-host'
DB_PORT = 3306
DB_USER = 'your-user'
DB_PASSWORD = 'your-password'

# 工单数据库
DB_NAME_CASE = 'casedb'
```

### 默认配置

```python
# 知识库默认管理员
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'YHKB@2024'

# Session配置
SESSION_TIMEOUT = 180  # Session超时时间（秒），3小时
```

## 默认账号

### 知识库系统
- **用户名**: `admin`
- **密码**: `YHKB@2024`
- **角色**: `admin`

### 工单系统
- **用户名**: `admin`
- **密码**: `admin123`
- **角色**: `admin`

**注意**: 两个系统的 admin 账号相互独立，密码不同。首次登录后请立即修改密码。

## 部署说明

### 1. 数据库初始化

知识库和工单系统的数据库已在各自系统的文档中详细说明，请参考：
- [知识库系统说明](./KB_SYSTEM_GUIDE.md#数据库初始化)
- [工单系统说明](./CASE_SYSTEM_GUIDE.md#数据库初始化)

### 2. 依赖安装

```bash
pip install flask pymysql werkzeug security
```

### 3. 环境变量配置

创建 `.env` 文件：

```env
DB_HOST=your-db-host
DB_PORT=3306
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME_KB=YHKB
DB_NAME_CASE=casedb
```

### 4. 启动应用

```bash
python app.py
```

### 5. 访问统一用户管理

- 登录页面: `http://localhost:5000/user-mgmt/login`
- 用户管理: `http://localhost:5000/user-mgmt/`

## 使用说明

### 1. 登录系统

1. 访问 `http://localhost:5000/unified/login`
2. 输入知识库或工单系统的用户名和密码
3. 系统自动识别并登录

### 2. 管理知识库用户

1. 切换到"知识库用户"标签页
2. 点击"添加用户"按钮创建新用户
3. 点击"编辑"按钮修改用户信息
4. 点击"删除"按钮删除用户（admin账号除外）
5. 使用搜索框查找用户

### 3. 管理工单系统用户

1. 切换到"工单系统用户"标签页
2. 点击"添加用户"按钮创建新用户
3. 点击"编辑"按钮修改用户信息
4. 点击"删除"按钮删除用户（admin账号除外）
5. 使用搜索框查找用户

### 4. 查看统计信息

页面顶部显示实时统计信息：
- 总用户数
- 活跃用户数
- 今日登录数
- 管理员数量

### 5. 重置用户密码

在编辑用户时，可以重置用户密码：
- 知识库用户：使用新的密码（Werkzeug加密）
- 工单用户：使用新的密码（MD5加密）

## 自定义配置

### 修改默认密码

在 `config.py` 中修改：

```python
DEFAULT_ADMIN_PASSWORD = 'your-new-password'
```

或登录后在统一用户管理中修改。

### 修改密码策略

在 `modules/unified/routes.py` 中修改密码验证逻辑：

```python
def validate_password(password):
    # 自定义密码验证规则
    if len(password) < 8:
        return False, "密码长度至少8位"
    # 添加其他验证规则
    return True, ""
```

### 自定义用户角色

在数据库中添加自定义角色，然后在代码中添加对应权限检查。

## 权限说明

### 用户角色

#### 知识库系统
- `admin`: 管理员，拥有所有权限
- `user`: 普通用户，只能查看和编辑自己的信息

#### 工单系统
- `admin`: 管理员，拥有所有权限
- `customer`: 客户，只能查看和编辑自己的工单

### 保护机制

1. **admin账号保护**: admin账号不能被删除或修改角色
2. **登录验证**: 所有操作需要登录验证
3. **权限检查**: 根据角色检查操作权限
4. **操作日志**: 记录所有关键操作

## 故障排除

### 1. 登录失败

**症状**: 提示"用户名或密码错误"

**解决方案**:
- 确认用户名和密码正确
- 检查用户状态是否为 active
- 查看登录日志了解失败原因
- 尝试重置密码

### 2. 用户创建失败

**症状**: 创建用户时提示错误

**解决方案**:
- 检查用户名是否已存在
- 确认密码符合要求
- 检查邮箱格式是否正确
- 查看数据库错误信息

### 3. 数据库连接失败

**症状**: 无法连接数据库

**解决方案**:
- 检查 MySQL 服务是否启动
- 确认数据库配置信息正确
- 测试数据库连接: `mysql -h host -u user -p`

### 4. 统计信息不更新

**症状**: 统计信息显示不正确

**解决方案**:
- 刷新页面
- 检查数据库中的数据
- 查看统计查询逻辑

## 安全建议

1. **密码安全**:
   - 使用强密码
   - 定期更换密码
   - 工单系统建议升级到更安全的加密方式

2. **Session管理**:
   - 启用 HTTPS 保护 Session
   - 设置合理的超时时间
   - 定期清理过期 Session

3. **输入验证**:
   - 验证所有用户输入
   - 防止SQL注入
   - 防止XSS攻击

4. **日志审计**:
   - 记录所有登录尝试
   - 记录用户操作
   - 定期审查日志

5. **访问控制**:
   - 限制登录尝试次数
   - 锁定异常账户
   - 严格权限管理

## 性能优化

1. **数据库优化**:
   - 添加索引: `CREATE INDEX idx_username ON mgmt_users(username);`
   - 使用连接池（已配置）
   - 优化查询语句

2. **缓存策略**:
   - 缓存用户统计信息
   - 缓存用户列表
   - 使用 Redis 作为缓存

3. **分页查询**:
   - 所有列表使用分页
   - 限制每页数量
   - 优化分页查询

## 扩展功能

### 计划添加的功能

1. **批量导入**: Excel/CSV 批量导入用户
2. **批量导出**: 导出用户列表
3. **用户组**: 支持用户组管理
4. **权限矩阵**: 更细粒度的权限控制
5. **审计日志**: 详细的操作审计
6. **密码策略**: 自定义密码策略
7. **双因素认证**: 2FA 支持
8. **SSO集成**: 单点登录集成

## 相关文档

- [项目总览](../README.md)
- [官网系统说明](./HOME_SYSTEM_GUIDE.md)
- [知识库系统说明](./KB_SYSTEM_GUIDE.md)
- [工单系统说明](./CASE_SYSTEM_GUIDE.md)
- [统一用户管理详细指南](./UNIFIED_USER_MANAGEMENT.md)
- [代码风格指南](./STYLE_GUIDE.md)

## 技术支持

如有问题请联系：
- 邮箱: support@cloud-doors.com
- 工单系统: http://your-server:5000/case

---

**文档版本**: v1.0
**更新日期**: 2026-02-06
