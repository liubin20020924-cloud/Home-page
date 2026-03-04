# 知识库系统说明文档

## 概述

知识库系统是云户科技的文档管理和知识共享平台，整合了 Trilium 笔记系统，提供完整的知识文档管理、搜索、查看和权限控制功能。支持用户认证、多级权限管理和安全的文档浏览。

## 技术架构

### 后端技术
- **框架**: Flask (Python Web框架)
- **数据库**: MySQL
- **认证**: Session + Werkzeug Security
- **API客户端**: Trilium API

### 前端技术
- **HTML5**: 页面结构
- **CSS3**: 样式设计
- **JavaScript**: 交互功能
- **Edge兼容**: 针对IE/Edge浏览器的优化

## 目录结构

```
modules/kb/
├── app.py                         # 知识库应用主文件
├── __init__.py                    # 模块初始化
├── auth/                          # 认证模块
│   ├── __init__.py
│   ├── routes.py                  # 登录/登出路由
│   └── utils.py                   # 认证工具函数
├── database/                      # 数据库模块
│   ├── __init__.py
│   └── db_utils.py                # 数据库工具函数
├── management/                    # 管理模块
│   ├── __init__.py
│   └── routes.py                  # 数据管理路由
└── views/                         # 视图模块
    ├── __init__.py
    └── routes.py                  # 内容查看路由

templates/kb/                      # 知识库模板
├── index.html                     # 知识库首页
├── login.html                     # 登录页面
├── management.html                # 数据管理页面
└── user_management.html           # 用户管理页面（已废弃）

static/kb/                         # 知识库静态资源
├── css/
│   ├── style.css                  # 主样式文件
│   ├── debug.css                  # 调试样式
│   └── edge_fixes.css             # Edge浏览器修复
├── image/
│   └── Logo.jpg                   # Logo图片
└── js/
    └── edge_compat.js             # Edge兼容脚本
```

## 功能模块

### 1. 用户认证系统

#### 1.1 登录功能

**访问路径**: `/kb/auth/login`

**功能说明**:
- 用户登录验证
- 登录失败尝试限制（5次）
- 密码使用 Werkzeug Security 加密（PBKDF2）
- Session 管理

**登录字段**:
- 用户名
- 密码

**关键代码位置**:
- 路由: `modules/kb/auth/routes.py`
- 工具: `modules/kb/auth/utils.py`
- 模板: `templates/kb/login.html`

**密码加密**:
```python
from werkzeug.security import generate_password_hash, check_password_hash
```

#### 1.2 登出功能

**访问路径**: `/kb/auth/logout`

**功能说明**:
- 清除 Session
- 重定向到登录页

**关键代码位置**:
- 路由: `modules/kb/auth/routes.py`

#### 1.3 权限控制

**装饰器**: `login_required(roles=['admin', 'user'])`

**功能说明**:
- 验证用户登录状态
- 检查用户角色权限
- 自动重定向未登录用户

**关键代码位置**:
- 工具: `modules/kb/auth/utils.py`

### 2. 知识库管理

#### 2.1 知识库首页

**访问路径**: `/kb`

**功能说明**:
- 显示所有知识库文档列表
- 分页展示（每页15条）
- 搜索功能
- 知识库统计信息

**主要功能**:
- 查看所有知识库
- 按名称搜索知识库
- 分页浏览
- 查看知识库详情

**关键代码位置**:
- 路由: `modules/kb/views/routes.py`
- 模板: `templates/kb/index.html`
- 数据库: `modules/kb/database/db_utils.py`

#### 2.2 知识库搜索

**访问路径**: `/kb?search=关键词`

**功能说明**:
- 按知识库名称模糊搜索
- 支持分页
- 实时搜索

**搜索API**:
```python
fetch_records_by_name(name)
fetch_records_by_name_with_pagination(name, page, per_page)
```

**关键代码位置**:
- 路由: `modules/kb/views/routes.py`
- 数据库: `modules/kb/database/db_utils.py`

#### 2.3 知识库详情

**访问路径**: `/kb/view/<id>`

**功能说明**:
- 显示知识库详细信息
- 内容安全渲染（防XSS）
- 图片代理加载
- HTML内容过滤

**安全特性**:
- HTML标签白名单过滤
- HTML属性白名单控制
- 图片防盗链保护
- 内容缓存机制

**关键代码位置**:
- 路由: `modules/kb/views/routes.py`
- 配置: `config.py` (ALLOWED_HTML_TAGS, ALLOWED_HTML_ATTRIBUTES)

### 3. 数据管理后台

#### 3.1 管理首页

**访问路径**: `/kb/MGMT`

**功能说明**:
- 知识库数据管理
- CRUD操作（增删改查）
- 分页浏览

**权限要求**: admin

**主要功能**:
- 查看所有知识库记录
- 添加新知识库
- 编辑现有知识库
- 删除知识库

**关键代码位置**:
- 路由: `modules/kb/management/routes.py`
- 模板: `templates/kb/management.html`

#### 3.2 添加知识库

**接口**: `POST /kb/MGMT/add`

**请求参数**:
```json
{
    "KB_Number": "KB001",
    "KB_Name": "知识库名称",
    "KB_Content": "知识库内容",
    "KB_Type": "类型"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "添加成功"
}
```

#### 3.3 编辑知识库

**接口**: `POST /kb/MGMT/edit/<id>`

**请求参数**:
```json
{
    "KB_Name": "更新后的名称",
    "KB_Content": "更新后的内容",
    "KB_Type": "更新后的类型"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "编辑成功"
}
```

#### 3.4 删除知识库

**接口**: `DELETE /kb/MGMT/delete/<id>`

**响应示例**:
```json
{
    "success": true,
    "message": "删除成功"
}
```

### 4. 用户管理

**注意**: 用户管理功能已迁移到独立用户管理系统，本模块不再提供用户管理功能。

**访问路径**: `/user-mgmt/`

**功能**: 统一管理知识库、工单系统和用户管理的所有用户账号。

详见 [统一用户管理说明](./UNIFIED_SYSTEM_GUIDE.md)

## 数据库设计

### 数据库: YHKB

#### 用户表 (mgmt_users)

```sql
CREATE TABLE mgmt_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,           -- 用户名
    password_hash VARCHAR(255) NOT NULL,            -- 密码哈希（Werkzeug）
    display_name VARCHAR(100),                      -- 显示名称
    role VARCHAR(20) DEFAULT 'user',                -- 角色: admin/user
    status VARCHAR(20) DEFAULT 'active',            -- 状态: active/inactive/locked
    last_login TIMESTAMP NULL,                      -- 最后登录时间
    login_attempts INT DEFAULT 0,                    -- 登录尝试次数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(50)                           -- 创建者
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 知识库表 (KB-info)

```sql
CREATE TABLE `KB-info` (
    KB_Number INT PRIMARY KEY AUTO_INCREMENT,       -- 知识库编号
    KB_Name VARCHAR(255) NOT NULL,                  -- 知识库名称
    KB_Content TEXT,                                -- 知识库内容
    KB_Type VARCHAR(100),                           -- 知识库类型
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
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
```

### Trilium 服务器配置

```python
# Trilium 服务器配置
TRILIUM_SERVER_URL = 'http://127.0.0.1:8080'
TRILIUM_TOKEN = 'your-trilium-token'
TRILIUM_SERVER_HOST = '127.0.0.1:8080'

# Trilium 登录配置
TRILIUM_LOGIN_USERNAME = ''
TRILIUM_LOGIN_PASSWORD = 'your-password'
```

### Session 配置

```python
SESSION_TIMEOUT = 180  # Session超时时间（秒），3小时
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'YHKB@2024'
```

### 内容安全配置

```python
# HTML 内容安全配置
ALLOWED_HTML_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'div', 'span',
    'strong', 'b', 'em', 'i', 'u', 's',
    'ul', 'ol', 'li',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'a', 'img',
    'pre', 'code',
    'blockquote', 'hr'
]

ALLOWED_HTML_ATTRIBUTES = {
    '*': ['class', 'style', 'id'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'table': ['border', 'cellpadding', 'cellspacing', 'width'],
}
```

## API 接口

### 认证接口

#### 用户登录

**接口**: `POST /kb/auth/login`

**请求参数**:
```json
{
    "username": "admin",
    "password": "YHKB@2024"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "登录成功",
    "redirect": "/kb"
}
```

**错误响应**:
```json
{
    "success": false,
    "message": "用户名或密码错误"
}
```

#### 用户登出

**接口**: `GET /kb/auth/logout`

**响应**: 重定向到登录页

### 数据管理接口

#### 获取知识库列表

**接口**: `GET /kb/MGMT/data`

**参数**:
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认15）

**响应示例**:
```json
{
    "success": true,
    "data": [
        {
            "KB_Number": 1,
            "KB_Name": "知识库名称",
            "KB_Type": "类型",
            "created_at": "2026-02-06 10:00:00"
        }
    ],
    "total": 100,
    "page": 1,
    "per_page": 15
}
```

#### 添加知识库

**接口**: `POST /kb/MGMT/add`

**请求参数**:
```json
{
    "KB_Name": "新知识库",
    "KB_Content": "知识库内容",
    "KB_Type": "类型"
}
```

#### 编辑知识库

**接口**: `POST /kb/MGMT/edit/<id>`

**请求参数**:
```json
{
    "KB_Name": "更新后的名称",
    "KB_Content": "更新后的内容",
    "KB_Type": "更新后的类型"
}
```

#### 删除知识库

**接口**: `DELETE /kb/MGMT/delete/<id>`

**响应示例**:
```json
{
    "success": true,
    "message": "删除成功"
}
```

### 视图接口

#### 获取知识库列表

**接口**: `GET /kb`

**参数**:
- `page`: 页码（默认1）
- `search`: 搜索关键词

**响应**: HTML页面

#### 查看知识库详情

**接口**: `GET /kb/view/<id>`

**响应**: HTML页面

## 默认账号

- **用户名**: `admin`
- **密码**: `YHKB@2024`
- **角色**: `admin`

**注意**: 首次登录后请立即修改默认密码。

## 部署说明

### 1. 数据库初始化

```sql
-- 创建数据库
CREATE DATABASE YHKB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE YHKB;

-- 创建用户表
CREATE TABLE mgmt_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    status VARCHAR(20) DEFAULT 'active',
    last_login TIMESTAMP NULL,
    login_attempts INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建知识库表
CREATE TABLE `KB-info` (
    KB_Number INT PRIMARY KEY AUTO_INCREMENT,
    KB_Name VARCHAR(255) NOT NULL,
    KB_Content TEXT,
    KB_Type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建登录日志表
CREATE TABLE mgmt_login_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    status VARCHAR(20),
    failure_reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建默认管理员（密码: YHKB@2024）
INSERT INTO mgmt_users (username, password_hash, display_name, role, created_by)
VALUES ('admin', 'pbkdf2:sha256:260000$...', '系统管理员', 'admin', 'system');
```

### 2. Trilium 服务器配置

确保 Trilium 服务器正常运行并配置正确：

```bash
# 检查 Trilium 服务
curl http://your-trilium-host:8080/api/notes
```

### 3. 依赖安装

```bash
pip install flask pymysql werkzeug python-dotenv trilium-py
```

### 4. 环境变量配置

创建 `.env` 文件：

```env
DB_HOST=your-db-host
DB_PORT=3306
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME_KB=YHKB

TRILIUM_SERVER_URL=http://your-trilium-host:8080
TRILIUM_TOKEN=your-trilium-token
```

### 5. 启动应用

```bash
python app.py
```

### 6. 访问知识库

- 登录页面: `http://localhost:5000/kb/auth/login`
- 知识库首页: `http://localhost:5000/kb`
- 管理后台: `http://localhost:5000/kb/MGMT`

## 自定义配置

### 修改默认密码

```python
# 在 config.py 中修改
DEFAULT_ADMIN_PASSWORD = 'your-new-password'
```

或登录后在统一用户管理中修改。

### 自定义HTML标签白名单

```python
# 在 config.py 中添加自定义标签
ALLOWED_HTML_TAGS = [
    # ... 现有标签
    'video',  # 添加视频标签
]
```

### 修改Session超时时间

```python
# 在 config.py 中修改（秒）
SESSION_TIMEOUT = 3600  # 1小时
```

## 故障排除

### 1. 登录失败

**症状**: 提示"用户名或密码错误"

**解决方案**:
- 确认用户名和密码正确
- 检查用户状态是否为 active
- 查看登录日志了解失败原因
- 重置用户密码

### 2. 数据库连接失败

**症状**: 无法连接数据库

**解决方案**:
- 检查 MySQL 服务是否启动
- 确认数据库配置信息正确
- 测试数据库连接: `mysql -h host -u user -p YHKB`

### 3. Trilium API 调用失败

**症状**: 无法获取 Trilium 数据

**解决方案**:
- 检查 Trilium 服务是否运行
- 确认 Token 配置正确
- 测试 API 连接: `curl http://trilium-host:8080/api/notes`

### 4. 内容显示异常

**症状**: HTML内容无法正常显示

**解决方案**:
- 检查 HTML 标签是否在白名单中
- 确认 HTML 属性是否被允许
- 查看浏览器控制台错误信息

### 5. Edge/IE 浏览器兼容性问题

**症状**: 在 IE 或旧版 Edge 中样式异常

**解决方案**:
- 确保 `edge_compat.js` 正确加载
- 检查 `edge_fixes.css` 是否生效
- 更新浏览器到最新版本

## 安全建议

1. **密码安全**: 使用强密码，定期更换
2. **Session管理**: 启用 HTTPS 保护 Session
3. **输入验证**: 验证所有用户输入
4. **SQL注入防护**: 使用参数化查询
5. **XSS防护**: 使用 HTML 过滤器
6. **CSRF防护**: 为表单添加 CSRF Token
7. **日志审计**: 记录所有登录和操作日志
8. **权限控制**: 严格管理用户角色和权限

## 性能优化

1. **数据库优化**:
   - 添加索引: `CREATE INDEX idx_kb_name ON KB-info(KB_Name);`
   - 使用分页查询
   - 启用查询缓存

2. **内容缓存**:
   ```python
   CONTENT_CACHE_TIMEOUT = 300  # 缓存5分钟
   ```

3. **静态资源缓存**:
   ```python
   STATIC_CACHE_TIME = 3600  # 缓存1小时
   ```

## 扩展功能

### 计划添加的功能

1. **全文搜索**: 集成 Elasticsearch
2. **知识库分类**: 支持多级分类
3. **知识库标签**: 标签管理和搜索
4. **版本控制**: 知识库版本管理
5. **评论功能**: 支持用户评论
6. **导出功能**: 导出为 PDF/Word
7. **移动端适配**: 响应式设计

## 相关文档

- [项目总览](../README.md)
- [官网系统说明](./HOME_SYSTEM_GUIDE.md)
- [工单系统说明](./CASE_SYSTEM_GUIDE.md)
- [统一用户管理说明](./UNIFIED_SYSTEM_GUIDE.md)
- [统一用户管理详细指南](./UNIFIED_USER_MANAGEMENT.md)
- [代码风格指南](./STYLE_GUIDE.md)

## 技术支持

如有问题请联系：
- 邮箱: support@cloud-doors.com
- 工单系统: http://your-server:5000/case

---

**文档版本**: v1.0
**更新日期**: 2026-02-06
