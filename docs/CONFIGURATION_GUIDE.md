# 配置文件说明

> config.py 和 .env 文件的详细配置说明

---

## 📋 目录

- [配置文件概述](#配置文件概述)
- [环境变量配置说明](#环境变量配置说明)
- [配置检查机制](#配置检查机制)
- [安全性建议](#安全性建议)
- [常见问题](#常见问题)

---

## 📄 配置文件概述

### config.py

**作用**: 应用配置定义文件

**特点**:
- 从 `.env` 文件读取所有配置项
- 提供默认值作为回退
- 自动配置检查，启动时验证关键配置
- 按功能模块分组，易于维护

### .env

**作用**: 环境变量配置文件（包含敏感信息）

**特点**:
- 包含所有可配置的环境变量
- 存储敏感信息（密码、Token等）
- **不提交到版本控制系统**
- 在 `.gitignore` 中被忽略

---

## 🔧 环境变量配置说明

### Flask 基础配置

| 变量名 | 默认值 | 说明 | 是否必填 |
|--------|---------|------|---------|
| `FLASK_SECRET_KEY` | `yihu-website-secret-key-2024-CHANGE-ME` | Flask 会话密钥 | ❌ 生产环境必填 |
| `FLASK_DEBUG` | `False` | 调试模式 | ⭕ 建议设置 |
| `FLASK_HOST` | `0.0.0.0` | 服务器监听地址 | ⭕ 建议设置 |
| `FLASK_PORT` | `5000` | 服务器端口 | ⭕ 建议设置 |

**说明**:
- `FLASK_HOST`: 生产环境通常设为 `0.0.0.0`（监听所有网卡）
- `FLASK_SECRET_KEY`: 生产环境必须修改为随机密钥

### 服务器配置

| 变量名 | 默认值 | 说明 | 示例 |
|--------|---------|------|------|
| `SITE_URL` | `http://0.0.0.0:5000` | 网站基础URL | `https://www.yundour.com` |

**说明**:
- 用于生成链接、重定向等
- 生产环境必须设置为实际域名
- 开发环境可以使用 `http://localhost:5000`

### 数据库配置

| 变量名 | 默认值 | 说明 | 是否必填 |
|--------|---------|------|---------|
| `DB_HOST` | `127.0.0.1` | 数据库服务器地址 | ✅ 必填 |
| `DB_PORT` | `3306` | 数据库端口 | ⭕ 可选 |
| `DB_USER` | `root` | 数据库用户名 | ✅ 必填 |
| `DB_PASSWORD` | - | 数据库密码 | ✅ 必填 |
| `DB_NAME_HOME` | `clouddoors_db` | 官网系统数据库名 | ⭕ 可选 |
| `DB_NAME_KB` | `YHKB` | 知识库系统数据库名 | ⭕ 可选 |
| `DB_NAME_CASE` | `casedb` | 工单系统数据库名 | ⭕ 可选 |

**说明**:
- `DB_PASSWORD`: 生产环境必须设置强密码
- 三个系统可以共用一个数据库服务器，使用不同的数据库

### 邮件配置

| 变量名 | 默认值 | 说明 | 是否必填 |
|--------|---------|------|---------|
| `SMTP_SERVER` | `smtp.qq.com` | SMTP服务器 | ⭕ 使用邮件功能必填 |
| `SMTP_PORT` | `465` | SMTP端口 | ⭕ 使用邮件功能必填 |
| `SMTP_USERNAME` | - | SMTP用户名 | ⭕ 使用邮件功能必填 |
| `SMTP_PASSWORD` | - | SMTP密码或授权码 | ⭕ 使用邮件功能必填 |
| `EMAIL_SENDER` | - | 发件人邮箱 | ⭕ 使用邮件功能必填 |

**QQ邮箱配置示例**:
```env
SMTP_SERVER=smtp.qq.com
SMTP_PORT=465
SMTP_USERNAME=your-email@qq.com
SMTP_PASSWORD=your-qq-authorization-code  # 不是QQ密码，是授权码
EMAIL_SENDER=your-email@qq.com
```

**Gmail配置示例**:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=noreply@yundour.com
```

### Trilium 配置

| 变量名 | 默认值 | 说明 | 是否必填 |
|--------|---------|------|---------|
| `TRILIUM_SERVER_URL` | `http://127.0.0.1:8080` | Trilium服务器地址 | ⭕ 使用知识库必填 |
| `TRILIUM_TOKEN` | - | Trilium ETAPI Token | ✅ 使用知识库必填 |
| `TRILIUM_SERVER_HOST` | `127.0.0.1:8080` | Trilium服务器Host | ⭕ 使用知识库必填 |
| `TRILIUM_LOGIN_USERNAME` | - | Trilium登录用户名 | ⭕ 需要认证时必填 |
| `TRILIUM_LOGIN_PASSWORD` | - | Trilium登录密码 | ⭕ 需要认证时必填 |

**如何获取 Trilium Token**:
1. 打开 Trilium 笔记
2. 进入 `Options → API tokens`
3. 点击 `Generate new token`
4. 设置 Token 名称和权限
5. 复制生成的 Token 到 `TRILIUM_TOKEN`

### CORS 配置

| 变量名 | 默认值 | 说明 | 示例 |
|--------|---------|------|------|
| `ALLOWED_ORIGINS` | `*` | 允许的跨域来源 | `https://www.yundour.com,https://yundour.com` |

**说明**:
- 开发环境可以使用 `*` 允许所有来源
- 生产环境建议设置为实际域名
- 多个域名用逗号分隔

### Redis 配置

| 变量名 | 默认值 | 说明 | 是否必填 |
|--------|---------|------|---------|
| `REDIS_ENABLED` | `False` | 是否启用Redis | ⭕ 需要缓存时必填 |
| `REDIS_HOST` | `127.0.0.1` | Redis服务器地址 | ✅ 启用时必填 |
| `REDIS_PORT` | `6379` | Redis端口 | ⭕ 可选 |
| `REDIS_DB` | `0` | Redis数据库编号 | ⭕ 可选 |
| `REDIS_PASSWORD` | - | Redis密码 | ⭕ 设置密码时必填 |

### CDN 配置

| 变量名 | 默认值 | 说明 | 是否必填 |
|--------|---------|------|---------|
| `CDN_ENABLED` | `False` | 是否启用CDN | ⭕ 需要CDN时必填 |
| `CDN_DOMAIN` | - | CDN域名 | ✅ 启用时必填 |
| `CDN_PROTOCOL` | `https` | CDN协议 | ⭕ 可选 |

**示例**:
```env
CDN_ENABLED=True
CDN_DOMAIN=cdn.yundour.com
CDN_PROTOCOL=https
```

### 图片优化配置

| 变量名 | 默认值 | 说明 | 范围 |
|--------|---------|------|------|
| `IMAGE_QUALITY` | `80` | 图片压缩质量 | 1-100 |
| `IMAGE_ENABLE_WEBP` | `True` | 是否启用WebP | True/False |
| `IMAGE_AUTO_COMPRESS` | `True` | 是否自动压缩 | True/False |
| `IMAGE_CACHE_TTL` | `604800` | 图片缓存TTL（秒） | 任意正整数 |

### 缓存配置

| 变量名 | 默认值 | 说明 | 可选值 |
|--------|---------|------|--------|
| `CACHE_TYPE` | `simple` | 缓存类型 | `simple`, `redis`, `filesystem` |
| `CACHE_DEFAULT_TIMEOUT` | `604800` | 默认缓存TTL（秒） | 任意正整数 |
| `CACHE_KEY_PREFIX` | `yundour_` | 缓存键前缀 | 任意字符串 |

### 日志配置

| 变量名 | 默认值 | 说明 | 可选值 |
|--------|---------|------|--------|
| `LOG_LEVEL` | `INFO` | 日志级别 | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `LOG_FILE` | `logs/app.log` | 日志文件路径 | 任意文件路径 |
| `LOG_MAX_BYTES` | `10` | 日志文件最大大小（MB） | 任意正整数 |
| `LOG_BACKUP_COUNT` | `5` | 日志文件备份数量 | 任意正整数 |

---

## ✅ 配置检查机制

### 启动时自动检查

应用启动时会自动检查关键配置项，输出如下：

```
============================================================
配置检查结果:

【严重错误】:
  [X] TRILIUM_TOKEN 未设置，知识库功能将无法使用

【警告提示】:
  [!] 警告: 知识库默认管理员密码未修改，建议立即修改
============================================================

注意：存在严重配置错误，建议立即修复！
```

### 检查项目

| 检查项 | 级别 | 说明 |
|--------|--------|------|
| SECRET_KEY 使用默认值 | 严重错误 | 生产环境必须修改 |
| DB_PASSWORD 未设置 | 严重错误 | 数据库连接将失败 |
| TRILIUM_TOKEN 未设置 | 严重错误 | 知识库功能将无法使用 |
| SITE_URL 使用默认值 | 严重错误 | 生产环境必须设置实际域名 |
| SMTP_PASSWORD 未设置 | 警告 | 邮件功能可能无法使用 |
| Redis 地址使用默认值 | 警告 | 生产环境需要确认 |
| 默认管理员密码未修改 | 警告 | 建议立即修改 |

---

## 🔒 安全性建议

### 1. 生产环境必改配置

```env
# ❌ 不要使用默认值
FLASK_SECRET_KEY=your-secret-key-here-CHANGE-ME
DB_PASSWORD=your-db-password-here
TRILIUM_LOGIN_PASSWORD=your-trilium-password-here

# ✅ 生产环境必须修改为强密码
FLASK_SECRET_KEY=your-random-secret-key-here-at-least-32-chars
DB_PASSWORD=your-strong-database-password-here
TRILIUM_LOGIN_PASSWORD=your-strong-trilium-password-here
```

### 2. 生成强密码

```bash
# 生成 Flask SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# 生成数据库密码
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

### 3. 保护 .env 文件

```bash
# 设置文件权限（仅所有者可读写）
chmod 600 .env

# 确保 .env 在 .gitignore 中
echo ".env" >> .gitignore

# 生产环境不要提交到版本控制
git rm --cached .env
```

### 4. 定期更换密码

建议：
- 数据库密码：每3个月更换一次
- Trilium Token：怀疑泄露时立即更换
- SMTP 密码：定期更换

---

## ❓ 常见问题

### Q1: 如何生成 Flask SECRET_KEY？

```bash
# 方法1：使用 Python secrets 模块
python -c "import secrets; print(secrets.token_hex(32))"

# 方法2：使用在线生成器
# 访问：https://randomkeygen.com/
```

### Q2: Trilium Token 如何获取？

1. 打开 Trilium 笔记系统
2. 点击右上角 `Options` → `API tokens`
3. 点击 `Generate new token`
4. 设置：
   - Token name: `cloud-doors-website`
   - Permissions: 勾选 `Read notes`, `Read attributes`, `Read note content`
5. 点击 `Generate`
6. 复制生成的 Token 到 `.env` 文件的 `TRILIUM_TOKEN`

### Q3: QQ邮箱授权码如何获取？

1. 登录 QQ 邮箱 → 设置 → 账户
2. 找到 `POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务`
3. 点击 `生成授权码`
4. 按提示发送短信验证
5. 复制生成的授权码（16位字符）
6. 填入 `SMTP_PASSWORD`（不是QQ密码）

### Q4: 生产环境 SITE_URL 应该填什么？

```env
# 示例1：使用域名
SITE_URL=https://www.your-domain.com

# 示例2：使用IP和端口
SITE_URL=http://YOUR_PUBLIC_IP:5000

# 示例3：使用HTTPS（推荐）
SITE_URL=https://your-domain.com
```

### Q5: 如何启用 Redis？

```env
# 1. 安装 Redis
sudo apt-get install redis-server

# 2. 启动 Redis
sudo systemctl start redis-server

# 3. 配置 .env
REDIS_ENABLED=True
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# 4. 安装 Python 客户端
pip install redis Flask-Caching

# 5. 重启应用
python app.py
```

### Q6: 如何切换开发/生产环境？

```env
# 开发环境
FLASK_DEBUG=True
DB_HOST=127.0.0.1
SITE_URL=http://localhost:5000

# 生产环境
FLASK_DEBUG=False
DB_HOST=your-production-db-host
SITE_URL=https://www.your-domain.com
```

### Q7: 配置修改后如何生效？

```bash
# 方法1：重启应用
# Ctrl+C 停止应用
python app.py  # 重新启动

# 方法2：如果使用 supervisor
sudo supervisorctl restart cloud-doors-website

# 方法3：如果使用 systemd
sudo systemctl restart cloud-doors-website
```

---

## 📝 配置模板

### 本地开发环境

```env
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=local-dev-password

TRILIUM_SERVER_URL=http://127.0.0.1:8080
TRILIUM_TOKEN=your-dev-trilium-token

SITE_URL=http://localhost:5000
ALLOWED_ORIGINS=*
```

### 生产环境（内网部署）

```env
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

DB_HOST=your-db-host
DB_USER=root
DB_PASSWORD=strong-database-password

TRILIUM_SERVER_URL=http://your-trilium-host:8080
TRILIUM_TOKEN=your-prod-trilium-token

SITE_URL=http://your-site-url:5000
ALLOWED_ORIGINS=http://your-site-url:5000
```

### 生产环境（公网部署）

```env
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

DB_HOST=your-db-host.your-domain.com
DB_USER=website_user
DB_PASSWORD=strong-database-password

TRILIUM_SERVER_URL=http://trilium.your-domain.com:8080
TRILIUM_TOKEN=your-prod-trilium-token

SMTP_SERVER=smtp.exmail.qq.com
SMTP_USERNAME=official@your-domain.com
SMTP_PASSWORD=your-qq-authorization-code
EMAIL_SENDER=official@your-domain.com

SITE_URL=https://www.your-domain.com
ALLOWED_ORIGINS=https://www.your-domain.com,https://your-domain.com

CONTACT_EMAIL=contact@your-domain.com
```

---

<div align="center">

**文档版本: v1.0**  
**创建日期: 2026-02-11**  
**最后更新: 2026-02-11**

</div>
