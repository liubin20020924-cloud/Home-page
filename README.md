# 云户科技网站 - 整合项目

> 🎯 整合官网、知识库、工单三个系统的统一 Web 应用平台

|[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)
|[![Flask](https://img.shields.io/badge/Flask-3.0.3-green)](https://flask.palletsprojects.com)
|[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 项目简介

云户科技网站是一个全功能的 Web 应用平台，整合了三个独立但相互关联的系统：

- **官网系统** - 企业官网展示、产品介绍、解决方案展示
- **知识库系统** - 文档管理、内容搜索、Trilium 笔记集成
- **工单系统** - 客户服务、实时聊天、问题跟踪

所有系统共享统一的用户管理和认证体系，使用 Flask 框架构建，采用蓝图路由架构，支持 MySQL/MariaDB 数据库。

---

## ✨ 主要特性

### 🏠 官网系统
- 响应式设计，支持多设备访问
- 产品展示和解决方案介绍
- 客户案例和公司介绍
- 在线联系表单
- 留言管理

### 📚 知识库系统
- 集成 Trilium 笔记服务
- 强大的搜索功能（支持 Trilium 搜索）
- 分页浏览和分类管理
- 统一用户认证
- 管理后台（记录管理、批量操作）
- 用户管理界面（添加、编辑、删除用户）
- 密码复杂度提示（最少 6 位，建议包含大小写字母、数字、特殊符号）
- 附件代理支持

### 🎫 工单系统
- WebSocket 实时聊天
- 工单创建和跟踪
- 邮件通知
- 客户与服务人员实时交流
- 工单状态管理
- **用户需由管理员创建**（无自助注册功能）

### 🔒 统一安全特性
- Werkzeug 密码加密（PBKDF2）
- Session 超时管理（3小时）
- 登录失败锁定
- 基于角色的访问控制（RBAC）
- 登录日志审计
- 配置安全检查

---

## 📁 项目结构

```
Integrate-code/
├── 🐍 核心文件
│   ├── app.py                      # Flask 应用主入口
│   ├── config.py                   # 配置读取（从 .env）
│   ├── requirements.txt            # Python 依赖
│   ├── .env.example               # 环境变量模板
│   └── .env                       # 环境变量（本地配置，不提交）
│
├── 🔧 公共模块 (common/)
│   ├── db_manager.py              # 数据库连接池管理
│   ├── database_context.py         # 数据库连接上下文管理器
│   ├── kb_utils.py                # 知识库工具函数
│   ├── logger.py                  # 结构化日志模块
│   ├── password_policy.py          # 密码策略配置
│   ├── response.py                # 统一 API 响应
│   ├── trilium_helper.py          # Trilium 集成
│   ├── unified_auth.py            # 统一认证模块
│   └── validators.py              # 输入验证
│
├── 📋 路由蓝图 (routes/)
│   ├── __init__.py                # 蓝图注册
│   ├── home_bp.py                # 官网路由
│   ├── kb_bp.py                  # 知识库认证和浏览路由
│   ├── kb_management_bp.py        # 知识库管理路由
│   ├── case_bp.py                # 工单系统路由
│   ├── unified_bp.py              # 统一用户管理路由
│   ├── auth_bp.py                # 认证 API 路由
│   ├── api_bp.py                # API 路由（Trilium 等）
│   └── user_management_bp.py     # 用户管理控制台路由
│
├── 💼 业务逻辑 (services/)
│   ├── user_service.py            # 用户服务层
│   ├── socketio_service.py       # WebSocket 服务
│   └── email_service.py          # 邮件服务
│
├── 🎨 前端模板 (templates/)
│   ├── home/                      # 官网模板
│   ├── kb/                        # 知识库模板
│   ├── case/                      # 工单模板
│   ├── user_management/           # 用户管理模板
│   └── common/                    # 通用模板
│
├── 📦 静态资源 (static/)
│   ├── common.css                 # 统一样式
│   ├── common/js/                 # 通用 JavaScript
│   ├── home/                      # 官网资源
│   ├── kb/                        # 知识库资源
│   └── case/                      # 工单资源
│
├── 📜 工具脚本 (scripts/)
│   ├── check_config.py            # 配置安全检查
│   ├── check_dependencies.py      # 依赖检查
│   ├── check_security.py          # 快速安全检查
│   ├── generate_secure_env.py     # 生成安全配置
│   ├── optimize_images.py         # 图片优化
│   ├── test_email_config.py       # 邮件配置测试
│   ├── deploy.sh                  # 自动部署脚本 ⭐
│   ├── rollback.sh                # 回滚脚本 ⭐
│   ├── check_and_deploy.sh        # 自动检测部署 ⭐
│   ├── webhook_receiver.py        # Webhook 接收器 ⭐
│   └── deploy_service.sh          # 部署服务安装 ⭐
│
├── 📚 文档 (docs/)
│   ├── README.md                  # 文档索引
│   ├── QUICK_START.md             # 快速开始
│   ├── CONFIGURATION_GUIDE.md    # 配置详细说明
│   ├── CONFIG_MIGRATION_GUIDE.md  # 配置迁移指南
│   ├── EMAIL_CONFIG_GUIDE.md      # 邮件配置指南
│   ├── HOME_SYSTEM_GUIDE.md       # 官网系统说明
│   ├── KB_SYSTEM_GUIDE.md         # 知识库系统说明
│   ├── CASE_SYSTEM_GUIDE.md       # 工单系统说明
│   ├── UNIFIED_SYSTEM_GUIDE.md    # 统一用户管理说明
│   ├── API_DOCS.md               # API 文档
│   ├── SECURITY_IMPROVEMENTS.md  # 安全改进文档
│   ├── CHANGELOG.md               # 版本更新日志
│   ├── CODE_STATISTICS.md         # 代码统计
│   └── archive/                   # 归档的旧文档
│
├── 🗄️ 数据库 (database/)
│   ├── init_database.sql           # 数据库初始化脚本
│   ├── README.md                  # 数据库文档
│   ├── QUICK_START.md             # 数据库快速开始
│   └── patches/                   # 数据库补丁
│       ├── v2.1_to_v2.2/          # v2.1→v2.2 补丁
│       ├── v2.2_to_v2.3/          # v2.2→v2.3 补丁
│       └── v2.4_to_v2.5/          # v2.4→v2.5 补丁
│
├── 🧪 测试 (tests/)
│   ├── conftest.py                # Pytest 配置
│   ├── test_case.py               # 工单系统测试
│   ├── test_home.py               # 官网系统测试
│   ├── test_kb.py                 # 知识库系统测试
│   └── MANUAL_TEST_GUIDE.md       # 手动测试指南
│
├── 🚀 启动脚本
│   ├── start.bat                 # Windows 启动脚本
│   └── start.sh                  # Linux/Mac 启动脚本
│
├── 📋 日志 (logs/)
│   └── app.log                    # 应用日志
│
└── 📄 其他
    ├── .gitignore                 # Git 忽略规则
    └── README.md                  # 本文件
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- MySQL/MariaDB 5.7 或更高版本
- Trilium 笔记服务器（用于知识库功能，可选）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- Flask 3.0.3
- Flask-SocketIO 5.3.6
- PyMySQL 1.1.0
- trilium-py 0.8.5
- python-dotenv 1.0.0

### 2. 配置环境

#### 方法一：生成安全配置（推荐）

```bash
python scripts/generate_secure_env.py
```

#### 方法二：手动创建 .env 文件

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
nano .env  # 或使用你喜欢的编辑器
```

**必须配置的项**（生产环境）：

```env
# Flask 安全密钥
FLASK_SECRET_KEY=your-secret-key-here-change-in-production

# 数据库配置
DB_PASSWORD=your-strong-database-password

# Trilium Token（知识库功能）
TRILIUM_TOKEN=your-trilium-api-token

# 默认管理员密码
DEFAULT_ADMIN_PASSWORD=your-strong-admin-password

# 邮件密码
MAIL_PASSWORD=your-email-password-or-authorization-code

# 网站域名
SITE_URL=https://www.your-domain.com
```

详细配置说明请参考：
- [配置详细说明](./docs/CONFIGURATION_GUIDE.md)
- [配置迁移指南](./docs/CONFIG_MIGRATION_GUIDE.md)
- [邮件配置指南](./docs/EMAIL_CONFIG_GUIDE.md)

### 3. 初始化数据库

```bash
mysql -u root -p < init_database.sql
```

这会创建三个数据库：
- `clouddoors_db` - 官网系统
- `YHKB` - 知识库系统
- `casedb` - 工单系统

### 4. 检查配置安全

```bash
python scripts/check_config.py
```

### 5. 启动应用

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**或直接运行:**
```bash
python app.py
```

### 6. 访问系统

启动成功后，访问以下地址：

| 系统 | 地址 | 说明 |
|------|------|------|
| 官网首页 | http://localhost:5000/ | 企业官网 |
| 知识库系统 | http://localhost:5000/kb | 文档管理 |
| 知识库管理 | http://localhost:5000/kb/MGMT | 知识库后台 |
| 工单系统 | http://localhost:5000/case | 客户服务 |
| 用户管理 | http://localhost:5000/user-mgmt/ | 用户管理 |
| API 文档 | http://localhost:5000/api/docs | Swagger 文档 |

---

## 🔐 默认账号

### 知识库系统

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | YHKB@2024 | 管理员 |

⚠️ **安全提示**: 生产环境请立即修改默认密码！

### 工单系统

工单系统使用统一的用户管理，**不支持自助注册**。用户账户需由管理员通过以下方式创建：

1. 访问用户管理：http://localhost:5000/user-mgmt/

---

## 📊 路由架构

### 蓝图划分

| 蓝图 | 前缀 | 说明 |
|------|--------|------|
| `home_bp` | `/` | 官网首页路由 |
| `kb_bp` | `/kb` | 知识库认证和浏览 |
| `kb_management_bp` | `/kb/MGMT` | 知识库管理后台 |
| `case_bp` | `/case` | 工单系统 |
| `unified_bp` | `/unified` | 统一用户管理 |
| `auth_bp` | `/auth` | 认证 API（用户管理） |
| `api_bp` | `/api` | API 路由（Trilium 等） |

### API 端点

#### Trilium 集成 API
- `GET /api/trilium/search` - 搜索 Trilium 笔记
- `GET /api/trilium/content` - 获取笔记内容
- `GET /api/trilium/test` - 测试 Trilium 连接
- `GET /kb/api/attachments/<path>` - Trilium 附件代理

#### 用户管理 API
- `POST /auth/api/add-user` - 添加用户
- `PUT /auth/api/update-user/<id>` - 更新用户
- `DELETE /auth/api/delete-user/<id>` - 删除用户
- `POST /auth/api/reset-password/<id>` - 重置密码

---

## 🔧 配置说明

### 配置文件策略

从 v2.5 开始，项目采用**单一配置文件**策略：

- **唯一配置源**: `.env` 文件
- **配置读取**: `config.py` 仅负责从 `.env` 读取配置
- **配置检查**: 启动时自动检查关键配置项

### 快速配置清单

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `FLASK_SECRET_KEY` | Flask 安全密钥（必须配置） | 自动生成 |
| `FLASK_DEBUG` | 调试模式 | `False` |
| `FLASK_HOST` | 服务器监听地址 | `0.0.0.0` |
| `FLASK_PORT` | 服务器端口 | `5000` |
| `DB_HOST` | 数据库主机 | `127.0.0.1` |
| `DB_PORT` | 数据库端口 | `3306` |
| `DB_PASSWORD` | 数据库密码（必须配置） | - |
| `MAIL_SERVER` | 邮件服务器 | `smtp.exmail.qq.com` |
| `MAIL_PORT` | 邮件端口 | `465` |
| `MAIL_USERNAME` | 邮件用户名 | - |
| `MAIL_PASSWORD` | 邮件密码（必须配置） | - |
| `TRILIUM_SERVER_URL` | Trilium 服务器 | `http://127.0.0.1:8080` |
| `TRILIUM_TOKEN` | Trilium Token（必须配置） | - |
| `DEFAULT_ADMIN_PASSWORD` | 默认管理员密码（必须配置） | `YHKB@2024` |
| `SITE_URL` | 网站域名 | `http://0.0.0.0:5000` |

### 数据库配置

三个系统共用一个数据库服务器，使用三个独立的数据库：

- `clouddoors_db` (DB_NAME_HOME) - 官网系统
- `YHKB` (DB_NAME_KB) - 知识库系统
- `casedb` (DB_NAME_CASE) - 工单系统

### 连接池配置

```env
DB_POOL_MAX_CONNECTIONS=20  # 最大连接数
DB_POOL_MIN_CACHED=5        # 最小缓存连接
DB_POOL_MAX_CACHED=10       # 最大缓存连接
DB_POOL_MAX_SHARED=5        # 最大共享连接
```

### 配置安全检查

启动应用时会自动检查配置，显示警告和错误：

```
============================================================
配置检查结果:

【警告提示】:
  [!] 知识库默认管理员密码未修改，建议立即修改

【严重错误】: 
  [X] DB_PASSWORD 未设置，数据库连接将失败
  [X] TRILIUM_TOKEN 未设置，知识库功能将无法使用

============================================================
```

### 配置文档

- [配置详细说明](./docs/configuration/CONFIGURATION_GUIDE.md) - 所有配置项的详细说明
- [配置迁移指南](./docs/configuration/CONFIG_MIGRATION_GUIDE.md) - 从旧版本迁移配置
- [邮件配置指南](./docs/configuration/EMAIL_CONFIG_GUIDE.md) - 企业微信/QQ 邮箱配置

---

## 🌟 核心功能

### 统一用户认证

所有系统共享用户表和认证逻辑：

- **用户名或邮箱登录**
- **密码强度验证**（最少 6 位）
- **密码复杂度提示**（建议包含大小写字母、数字、特殊符号）
- **密码显示/隐藏切换**
- **登录失败锁定**
- **Session 超时**（3 小时）
- **登录日志审计**

### WebSocket 实时通信

工单系统支持 WebSocket 实时聊天：

- 客户与服务人员实时交流
- 工单房间机制（每工单独立房间）
- 消息广播和通知
- 在线状态显示

### Trilium 集成

知识库系统集成 Trilium 笔记：

- 从 Trilium 搜索笔记
- 获取笔记内容
- 附件代理访问
- 使用 ETAPI 认证

### 统一 API 响应

所有 API 使用统一的响应格式：

```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... }
}
```

---

## 📚 文档

详细文档请查看 [`docs/`](./docs/) 目录：

### 核心文档
- [文档总览](./docs/README.md) ⭐
- [快速开始](./docs/QUICK_START.md)
- [Git配置方案](./docs/GIT_CONFIG_SOLUTION.md) ⭐ **新** - 腾讯云完整配置
- [快速配置指南（简化版）](./docs/QUICK_SETUP_GUIDE.md) ⭐
- [简化版CI/CD配置](./docs/SIMPLIFIED_CI_CD.md)
- [版本管理规范](./docs/project-management/VERSION_MANAGEMENT_GUIDE.md) ⭐
- [版本管理快速指南](./docs/QUICK_START_VERSIONING.md) ⭐
- [自动部署配置](./docs/AUTO_DEPLOY_SETUP.md)

### 系统文档
- [官网系统说明](./docs/system-guides/HOME_SYSTEM_GUIDE.md)
- [知识库系统说明](./docs/system-guides/KB_SYSTEM_GUIDE.md)
- [工单系统说明](./docs/system-guides/工单系统设计文档.md)
- [统一用户管理说明](./docs/system-guides/UNIFIED_SYSTEM_GUIDE.md)

### 配置文档
- [配置详细说明](./docs/configuration/CONFIGURATION_GUIDE.md)
- [配置迁移指南](./docs/configuration/CONFIG_MIGRATION_GUIDE.md)
- [邮件配置指南](./docs/configuration/EMAIL_CONFIG_GUIDE.md)
- [用户注册指南](./docs/system-guides/USER_REGISTRATION_GUIDE.md)

### 技术文档
- [API 文档](./docs/API_DOCS.md)
- [安全改进文档](./docs/SECURITY_IMPROVEMENTS.md)
- [CI/CD 部署文档](./docs/CI_CD_DEPLOYMENT_GUIDE.md)
- [代码统计](./docs/CODE_STATISTICS.md)

### 版本信息
- [变更日志](./CHANGELOG.md) ⭐

---

## 🔒 安全特性

### 密码安全

- **Werkzeug PBKDF2 加密**
- **密码强度验证**（最少 6 位，建议包含大小写字母、数字、特殊符号）
- **禁止常见弱密码**
- **密码修改需验证旧密码**
- **密码显示/隐藏切换功能**

### 会话安全

- **HttpOnly Cookies**
- **SameSite=Lax**
- **3 小时超时**
- **自动清理过期 Session**

### API 安全

- **登录验证装饰器**
- **角色权限控制**（RBAC）
- **SQL 注入防护**（参数化查询）
- **XSS 防护**（HTML 内容清理）
- **CSRF 保护**（生产环境）

### 审计日志

- 登录成功/失败日志
- 登录 IP 和 User-Agent
- 用户操作日志
- 系统错误日志

---

## 🛠️ 开发指南

### 代码规范

项目遵循 PEP 8 代码规范：

- 使用 4 空格缩进
- 函数和类使用驼峰命名
- 变量使用下划线命名
- 添加类型注解和文档字符串

### 添加新路由

1. 在对应的蓝图文件中添加路由函数（`routes/` 目录）
2. 使用统一响应格式（`common/response.py`）
3. 添加登录验证装饰器（如需要）
4. 记录日志（`common/logger.py`）
5. 在 `app.py` 中注册新蓝图

### 修改配置

1. 编辑 `.env` 文件（推荐）
2. 或修改 `config.py` 中的默认值
3. 运行安全检查确认

### 数据库迁移

修改数据库结构时：

1. 更新 `init_database.sql`
2. 提供数据迁移脚本
3. 更新文档说明

---

## 🐛 故障排除

### 数据库连接失败

```bash
# 检查 MySQL 服务
systemctl status mysql

# 测试连接
mysql -h 127.0.0.1 -u root -p

# 检查防火墙
firewall-cmd --list-all
```

### 端口被占用

```bash
# 查看占用端口的进程
netstat -ano | findstr :5000  # Windows
lsof -i :5000                  # Linux/Mac

# 修改端口（编辑 .env）
FLASK_PORT=5001
```

### Trilium 连接失败

1. 确认 Trilium 服务运行中
2. 检查 `TRILIUM_SERVER_URL` 配置
3. 在 Trilium 中生成 ETAPI Token
4. 更新 `.env` 中的 `TRILIUM_TOKEN`

### WebSocket 连接失败

1. 确认安装了 `eventlet` 或 `gevent`
2. 检查防火墙设置
3. 确认使用正确的异步模式



## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 提交规范

- 功能: `feat: 添加新功能`
- 修复: `fix: 修复 bug`
- 文档: `docs: 更新文档`
- 重构: `refactor: 代码重构`
- 测试: `test: 添加测试`

---

## 📄 许可证

MIT License

---

## 📞 联系方式

- **邮箱**: Leon.Liu@cloud-doors.com
- **工单系统**: http://your-server:5000/case
- **官网**: http://your-server:5000/

---

## 🙏 致谢

感谢以下开源项目：

- [Flask](https://flask.palletsprojects.com)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io)
- [Bootstrap](https://getbootstrap.com)
- [Trilium Notes](https://github.com/zadam/trilium)
- [trilium-py](https://github.com/naereen/trilium-py)

---

<div align="center">

**云户科技 © 2026**

Made with ❤️ by CloudDoors Team

</div>
