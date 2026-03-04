# 官网系统说明文档

## 概述

官网系统是云户科技的官方网站，用于展示公司形象、产品介绍、解决方案和服务信息。采用 Flask + SQLAlchemy 技术栈，支持响应式设计和现代化的用户界面。

## 技术架构

### 后端技术
- **框架**: Flask (Python Web框架)
- **ORM**: Flask-SQLAlchemy
- **数据库**: MySQL (主) / SQLite (备用)
- **模板引擎**: Jinja2

### 前端技术
- **HTML5**: 页面结构
- **CSS3**: 样式和动画
- **JavaScript**: 交互功能
- **Bootstrap**: 响应式布局

## 目录结构

```
modules/home/
├── app.py                    # 官网应用主文件
├── __init__.py               # 模块初始化
└── routes/                  # 路由模块
    ├── __init__.py
    ├── main.py               # 主路由（首页、各页面）
    ├── api.py                # API路由（联系表单等）
    └── admin.py              # 管理后台路由

templates/home/               # 官网模板
├── index.html                # 首页模板
├── base.html                 # 基础模板
├── test_images.html          # 图片测试页
├── admin/
│   └── messages.html         # 留言管理页面
└── components/               # 页面组件
    ├── header.html           # 页头组件
    ├── footer.html           # 页脚组件
    ├── home.html             # 首页内容
    ├── about.html            # 关于我们
    ├── services.html         # 服务介绍
    ├── solutions.html        # 解决方案
    ├── cases.html            # 成功案例
    └── contact.html          # 联系方式

static/home/                  # 官网静态资源
└── images/                   # 图片资源
    ├── Logo1.jpg
    ├── Logo2.jpg
    ├── Logo4.png
    ├── Logo5.png
    ├── Logo6.jpg
    ├── 1.jpg ~ 5.jpg         # 轮播图
    └── ...                   # 其他图片

instance/                     # SQLite数据库文件（备用）
└── clouddoors.db             # SQLite数据库
```

## 功能模块

### 1. 首页模块

**访问路径**: `/`

**功能说明**:
- 企业形象展示
- 产品服务概览
- 导航到各个子页面

**主要组件**:
- 轮播图展示
- 产品/服务卡片
- 公司简介
- 快速导航

**关键代码位置**:
- 路由: `modules/home/routes/main.py`
- 模板: `templates/home/index.html`
- 组件: `templates/home/components/*.html`

### 2. 关于我们

**访问路径**: `/about`

**功能说明**:
- 公司介绍
- 发展历程
- 企业文化
- 团队介绍

**关键代码位置**:
- 路由: `modules/home/routes/main.py`
- 组件: `templates/home/components/about.html`

### 3. 产品服务

**访问路径**: `/services`

**功能说明**:
- 产品列表展示
- 服务项目介绍
- 产品详情

**关键代码位置**:
- 路由: `modules/home/routes/main.py`
- 组件: `templates/home/components/services.html`

### 4. 解决方案

**访问路径**: `/solutions`

**功能说明**:
- 行业解决方案
- 技术方案展示
- 客户案例链接

**关键代码位置**:
- 路由: `modules/home/routes/main.py`
- 组件: `templates/home/components/solutions.html`

### 5. 成功案例

**访问路径**: `/cases`

**功能说明**:
- 客户案例展示
- 项目成果
- 合作伙伴

**关键代码位置**:
- 路由: `modules/home/routes/main.py`
- 组件: `templates/home/components/cases.html`

### 6. 联系我们

**访问路径**: `/contact`

**功能说明**:
- 联系信息展示
- 在线留言表单
- 地图位置

**表单字段**:
- 姓名
- 邮箱
- 电话
- 公司名称
- 留言内容

**关键代码位置**:
- 路由: `modules/home/routes/api.py`
- 组件: `templates/home/components/contact.html`

### 7. 留言管理

**访问路径**: `/admin/messages`

**功能说明**:
- 查看所有留言
- 留言详情
- 留言状态管理

**关键代码位置**:
- 路由: `modules/home/routes/admin.py`
- 模板: `templates/home/admin/messages.html`

## 数据库设计

### MySQL 数据库 (clouddoors_db)

**表名**: `messages`

**字段说明**:
```sql
CREATE TABLE messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,        -- 留言人姓名
    email VARCHAR(100) NOT NULL,       -- 留言人邮箱
    phone VARCHAR(20),                 -- 电话号码
    company VARCHAR(100),              -- 公司名称
    message TEXT NOT NULL,             -- 留言内容
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 留言时间
    status VARCHAR(20) DEFAULT 'pending'  -- 状态: pending/read/replied
);
```

### SQLite 数据库 (备用)

**数据库文件**: `instance/clouddoors.db`

用于本地开发或测试环境，表结构与 MySQL 一致。

## API 接口

### 提交联系表单

**接口**: `POST /api/contact`

**请求示例**:
```json
{
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "company": "示例公司",
    "message": "我想咨询产品信息"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "留言提交成功，我们会尽快联系您"
}
```

**错误响应**:
```json
{
    "success": false,
    "message": "提交失败，请稍后重试"
}
```

## 配置说明

### 数据库配置

在 `config.py` 中配置：

```python
# MySQL 配置（推荐）
DB_NAME_HOME = 'clouddoors_db'
DB_HOST = 'your-host'
DB_PORT = 3306
DB_USER = 'your-user'
DB_PASSWORD = 'your-password'

# SQLite 配置（备用）
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'clouddoors.db')
```

### 邮件配置

```python
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-password'
MAIL_DEFAULT_SENDER = 'noreply@cloud-doors.com'
```

### 联系信息配置

```python
CONTACT_EMAIL = 'support@cloud-doors.com'
```

## 部署说明

### 1. 数据库初始化

```sql
-- 创建数据库
CREATE DATABASE clouddoors_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE clouddoors_db;

-- 创建留言表
CREATE TABLE messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    company VARCHAR(100),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);
```

### 2. 依赖安装

```bash
pip install flask flask-sqlalchemy pymysql
```

### 3. 环境变量配置

创建 `.env` 文件：

```env
DB_HOST=your-db-host
DB_PORT=3306
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME_HOME=clouddoors_db
```

### 4. 启动应用

```bash
python app.py
```

或使用启动脚本：

```bash
./start.sh  # Linux
start.bat   # Windows
```

### 5. 访问官网

打开浏览器访问: `http://localhost:5000/`

## 自定义配置

### 修改公司信息

编辑模板文件中的公司信息：

- `templates/home/components/header.html`: 公司名称和Logo
- `templates/home/components/footer.html`: 地址、电话、邮箱
- `templates/home/components/about.html`: 公司简介

### 替换图片

替换 `static/home/images/` 目录下的图片文件：

- `Logo1.jpg`, `Logo2.jpg`: 公司Logo
- `1.jpg` ~ `5.jpg`: 首页轮播图
- 其他自定义图片

### 修改页面样式

编辑 `static/home/css/` 目录下的CSS文件（如果存在）或修改模板中的内联样式。

## 故障排除

### 1. 数据库连接失败

**症状**: 访问页面时提示数据库错误

**解决方案**:
- 检查 MySQL 服务是否启动
- 确认数据库配置信息正确
- 测试数据库连接: `mysql -h host -u user -p`

### 2. 留言表单提交失败

**症状**: 提交留言后无响应或提示错误

**解决方案**:
- 检查 API 路由是否正确配置
- 查看服务器日志获取详细错误信息
- 确认数据库连接正常

### 3. 静态资源加载失败

**症状**: 页面样式或图片无法加载

**解决方案**:
- 检查 `static/` 目录路径是否正确
- 确认文件权限设置正确
- 清除浏览器缓存后重试

### 4. 页面显示异常

**症状**: 页面布局错乱或组件缺失

**解决方案**:
- 检查模板文件是否完整
- 确认模板继承关系正确
- 查看 Jinja2 模板渲染错误

## 维护建议

### 定期备份

```bash
# 备份 MySQL 数据库
mysqldump -h host -u user -p clouddoors_db > backup.sql

# 备份 SQLite 数据库
cp instance/clouddoors.db backup/clouddoors.db
```

### 日志监控

建议配置日志记录，监控网站访问和错误信息：

```python
import logging
logging.basicConfig(filename='logs/home.log', level=logging.INFO)
```

### 性能优化

1. 启用静态资源缓存
2. 使用 CDN 加速图片加载
3. 数据库查询优化
4. 启用 gzip 压缩

## 安全建议

1. **启用 HTTPS**: 使用 SSL 证书加密传输
2. **CSRF 保护**: 为表单添加 CSRF Token
3. **输入验证**: 验证所有用户输入
4. **SQL 注入防护**: 使用参数化查询
5. **XSS 防护**: 转义输出内容

## 扩展功能

### 计划添加的功能

1. **多语言支持**: 中英文切换
2. **博客功能**: 发布公司动态
3. **产品展示系统**: 独立的产品管理
4. **在线客服**: 集成客服系统
5. **搜索功能**: 全站搜索
6. **统计分析**: 访问统计和分析

## 相关文档

- [项目总览](../README.md)
- [知识库系统说明](./KB_SYSTEM_GUIDE.md)
- [工单系统说明](./CASE_SYSTEM_GUIDE.md)
- [统一用户管理说明](./UNIFIED_SYSTEM_GUIDE.md)
- [代码风格指南](./STYLE_GUIDE.md)

## 技术支持

如有问题请联系：
- 邮箱: support@cloud-doors.com
- 工单系统: http://cloud-doors.com:5000/case

---

**文档版本**: v1.0
**更新日期**: 2026-02-06
