# Scripts 目录说明文档

> 项目中所有脚本的功能说明和使用指南

---

## 📋 目录

1. [核心部署脚本](#核心部署脚本)
2. [辅助脚本](#辅助脚本)
3. [已删除的脚本](#已删除的脚本)
4. [脚本使用最佳实践](#脚本使用最佳实践)

---

## 核心部署脚本

### 1. deploy.sh - 主部署脚本

**文件位置**: `scripts/deploy.sh`

**功能描述**：
完整的自动化部署流程，包括备份、拉取代码、更新依赖、重启服务等所有步骤。

**主要功能**：
- ✅ 自动创建时间戳备份
- ✅ 智能拉取代码（GitHub/Gitee）
- ✅ 自动更新 Python 依赖
- ✅ 优雅停止和重启应用服务
- ✅ 记录版本信息和部署日志
- ✅ 健康检查验证

**核心函数**：
```bash
create_backup()           # 创建备份
smart_pull()            # 智能拉取代码
update_dependencies()    # 更新依赖
restart_service()       # 重启服务
verify_deployment()      # 验证部署
```

**使用方法**：
```bash
# 手动触发部署
cd /opt/Home-page
./scripts/deploy.sh

# Webhook 自动触发（主要方式）
# GitHub Actions 推送 → Webhook 通知 → 自动执行

# SSH 备用触发
# GitHub Actions 通过 SSH 连接执行
```

**依赖关系**：
- 需要虚拟环境：`/opt/Home-page/venv`
- 需要配置文件：`.env`
- 需要服务文件：`/etc/systemd/system/Home-page.service`

---

### 2. smart-pull.sh - 智能拉取脚本

**文件位置**: `scripts/smart-pull.sh`

**功能描述**：
智能拉取代码，优先使用 GitHub，支持代理配置，Gitee 作为后备方案。

**主要功能**：
- ✅ 测试 GitHub 直接连接速度
- ✅ 检查配置的 Git 代理
- ✅ 低速时自动切换到代理拉取
- ✅ GitHub 完全不可用时使用 Gitee 作为后备
- ✅ 支持代理超时处理
- ✅ 显示当前版本信息（SHA、时间、提交消息）
- ✅ 完整的错误处理和日志记录

**核心函数**：
```bash
test_github_speed()    # 测试 GitHub 连接速度
pull_from_github()    # 从 GitHub 拉取代码（带代理支持）
pull_from_gitee()     # 从 Gitee 拉取代码（后备方案）
```

**工作流程**：
1. 测试 GitHub 直接连接速度
2. 如果速度 ≥ 100 KB/s：直接从 GitHub 拉取
3. 如果速度 < 100 KB/s：尝试使用代理从 GitHub 拉取
4. 如果 GitHub 完全无法访问：自动切换到 Gitee 拉取
5. 拉取成功后显示版本信息

**使用场景**：
```bash
# 部署脚本自动调用
./scripts/deploy.sh  # 内部调用 smart-pull.sh

# 手动使用
cd /opt/Home-page
./scripts/smart-pull.sh  # 手动测试和拉取
```

**配置要求**：
- GitHub 代理配置（可选，但推荐）：`git config --global http.https://github.proxy http://proxy-server:port`
- 通用代理配置（可选）：`git config --global http.proxy http://proxy-server:port`
- 远程仓库：origin → GitHub（主源），gitee → Gitee（后备）

**代理配置示例**：
```bash
# 配置 GitHub 专用代理
git config --global http.https://github.proxy http://proxy-server:port

# 配置通用代理（所有 HTTPS）
git config --global http.proxy http://proxy-server:port
git config --global https.proxy http://proxy-server:port

# 验证配置
git config --global --get http.https://github.com.proxy
```

**注意事项**：
- 代理配置可使用 `one-time-setup.sh` 和 `check_git_config.sh` 脚本辅助管理
- 如果网络环境可以直接访问 GitHub，无需配置代理
- 代理地址格式：`http://proxy-host:port` 或 `https://proxy-host:port`
- 建议定期同步 GitHub → Gitee，确保 Gitee 仓库是最新的

**Gitee 后备方案**：
- Gitee 作为 GitHub 完全不可访问时的后备选项
- 需要定期同步 GitHub 代码到 Gitee
- Gitee 仓库地址：`https://gitee.com/liubin_studies/Home-page.git`
- 添加 Gitee 远程仓库：
  ```bash
  git remote add gitee https://gitee.com/liubin_studies/Home-page.git
  ```

---

### 3. rollback.sh - 回滚脚本

**文件位置**: `scripts/rollback.sh`

**功能描述**：
快速回滚到指定历史版本，支持版本列表选择和交互式操作。

**主要功能**：
- ✅ 列出所有可用备份版本
- ✅ 显示版本元数据（SHA、时间）
- ✅ 选择指定版本进行回滚
- ✅ 自动停止和重启服务
- ✅ 验证回滚成功

**核心函数**：
```bash
list_backups()            # 列出备份
rollback_to_version()     # 回滚到指定版本
verify_rollback()          # 验证回滚
```

**使用方法**：
```bash
# 查看可用备份
./scripts/rollback.sh

# 回滚到指定版本
./scripts/rollback.sh Home-page_20260304_120000

# 回滚到上一个版本
./scripts/rollback.sh
```

**备份存储位置**：
`/var/backups/Home-page/` - 项目目录外的备份目录

---

### 4. webhook_receiver_github.py - Webhook 接收器

**文件位置**: `scripts/webhook_receiver_github.py`

**功能描述**：
Flask Webhook 接收服务，接收 GitHub 部署通知并触发部署流程。

**主要功能**：
- ✅ 接收 GitHub Webhook POST 请求
- ✅ HMAC-SHA256 签名验证
- ✅ 分支过滤（只处理 main 分支）
- ✅ 异步触发部署脚本
- ✅ 记录部署日志
- ✅ 健康检查端点
- ✅ 版本查询端点
- ✅ 日志查询端点

**API 端点**：
```
POST /webhook/github     # 接收 GitHub Webhook
GET  /webhook/health     # 健康检查
GET  /webhook/version    # 查询当前版本
GET  /webhook/logs       # 查询部署日志
```

**使用方法**：
```bash
# 启动服务
python3 /opt/Home-page/scripts/webhook_receiver_github.py

# 或使用 systemd 管理
sudo systemctl start webhook-receiver

# 测试端点
curl http://localhost:9000/webhook/health
curl http://localhost:9000/webhook/version
```

**配置要求**：
- 环境变量文件：`.env`
- 必需变量：`WEBHOOK_SECRET`
- 端口：9000

---

### 5. check_git_config.sh - Git 配置检查

**文件位置**: `scripts/check_git_config.sh`

**功能描述**：
检查 Git 配置状态，包括代理设置、远程仓库、用户信息等。

**主要功能**：
- ✅ 检查 Git 安装状态
- ✅ 检查用户配置（name/email）
- ✅ 检查网络配置（缓冲区、压缩）
- ✅ 检查代理配置（GitHub 代理、通用代理）
- ✅ 检查凭证存储配置
- ✅ 检查项目远程仓库配置
- ✅ 测试 GitHub 连接状态
- ✅ 显示所有 Git 配置
- ✅ 提供配置建议

**使用方法**：
```bash
# 检查 Git 配置
./scripts/check_git_config.sh

# 查看特定配置
git config --global --list
git config --global --get http.https://github.com.proxy
```

**输出内容**：
- Git 版本信息
- 用户配置状态
- 网络配置（缓冲区、压缩）
- 代理配置（GitHub 专用、通用）
- 凭证存储方式
- 远程仓库配置
- GitHub 连接测试结果
- 配置建议和优化提示

**适用场景**：
- 首次配置 Git 环境
- 排查 Git 连接问题
- 验证代理配置是否生效
- 检查远程仓库配置
- 诊断网络传输问题

---

### 6. generate_secure_env.py - 安全环境生成

**文件位置**: `scripts/generate_secure_env.py`

**功能描述**：
生成安全的环境变量配置，包括随机密钥、安全的数据库密码等。

**主要功能**：
- ✅ 生成随机的 Webhook 密钥
- ✅ 生成安全的数据库密码
- ✅ 生成加密的密钥
- ✅ 创建 `.env` 文件

**使用方法**：
```bash
python3 scripts/generate_secure_env.py
```

**输出文件**：
- `.env` - 环境变量文件
- 配置说明和警告信息

---

### 7. create-test-pr.sh - 创建测试 PR 脚本

**文件位置**: `scripts/create-test-pr.sh`

**功能描述**：
使用 GitHub CLI 创建 Pull Request 的辅助脚本。

**主要功能**：
- ✅ 自动创建 PR
- ✅ 自动添加标签
- ✅ 设置 PR 描述
- ✅ 指定基础和功能分支

**使用方法**：
```bash
# 设置 GitHub Token
export GITHUB_TOKEN="your_token_here"

# 创建 PR
./scripts/create-test-pr.sh feat/new-feature main
```

**依赖**：
- GitHub CLI: `gh`
- 有效的 GitHub Token

---

### 8. one-time-setup.sh - 一次性设置脚本

**文件位置**: `scripts/one-time-setup.sh`

**功能描述**：
云主机首次部署时的初始化脚本，执行所有必要的配置和安装。

**主要功能**：
- ✅ 创建日志目录（/var/log/integrate-code）
- ✅ 配置 Git 全局设置（缓冲区、压缩、凭证存储）
- ✅ 配置 GitHub 远程仓库（origin）
- ✅ 配置智能拉取脚本权限
- ✅ 测试代码拉取流程
- ✅ 显示配置状态和下一步操作提示

**使用方法**：
```bash
# 使用 root 权限运行
sudo bash scripts/one-time-setup.sh
```

**执行步骤**：
1. 检查 root 权限
2. 创建日志目录
3. 配置 Git（缓冲区、压缩、凭证）
4. 添加 GitHub 远程仓库
5. 配置智能拉取脚本
6. 测试拉取流程

**配置的远程仓库**：
- `origin`: https://github.com/liubin20020924-cloud/Home-page.git（主源）
- `gitee`: 需要手动添加（可选后备）：`git remote add gitee https://gitee.com/liubin_studies/Home-page.git`

**适用场景**：
- 首次部署云主机
- 重新配置 Git 环境
- 更新远程仓库地址
- 初始化 CI/CD 环境

**注意事项**：
- 需要使用 root 权限运行
- 项目目录必须存在：/opt/Home-page
- 建议在运行后使用 `check_git_config.sh` 验证配置
- 如需代理访问 GitHub，请手动配置代理
- Gitee 作为后备方案，需要定期同步 GitHub 代码

---

### 9. install-flask-venv.sh - Flask 虚拟环境安装

**文件位置**: `scripts/install-flask-venv.sh`

**功能描述**：
创建和配置 Python 虚拟环境，安装 Flask 和相关依赖。

**主要功能**：
- ✅ 创建 Python 虚拟环境
- ✅ 安装 Flask 和依赖
- ✅ 配置环境变量
- ✅ 创建激活脚本

**使用方法**：
```bash
./scripts/install-flask-venv.sh

# 激活虚拟环境
source /opt/Home-page/venv/bin/activate
```

**虚拟环境位置**：
`/opt/Home-page/venv/`

---

### 10. test_routes.py - 路由测试

**文件位置**: `scripts/test_routes.py`

**功能描述**：
自动化测试应用的所有 API 路由。

**主要功能**：
- ✅ 测试认证路由
- ✅ 测试用户管理路由
- ✅ 测试工单系统路由
- ✅ 测试知识库路由
- ✅ 生成测试报告

**使用方法**：
```bash
# 运行所有路由测试
python3 scripts/test_routes.py

# 运行特定模块测试
python3 scripts/test_routes.py --module auth
python3 scripts/test_routes.py --module kb
```

---

## 辅助脚本

### generate-webhook-secret.py - Webhook 密钥生成

**文件位置**: `scripts/generate-webhook-secret.py`

**功能描述**：
生成 Webhook 签名所需的密钥，用于 GitHub 和 Webhook 之间的签名验证。

**使用方法**：
```bash
python3 scripts/generate-webhook-secret.py
```

---

### get_smtp_ip.py - SMTP 服务器 IP 查询

**文件位置**: `scripts/get_smtp_ip.py`

**功能描述**：
查询 SMTP 服务器的 IP 地址，用于邮件服务配置。

**使用方法**：
```bash
python3 scripts/get_smtp_ip.py smtp.example.com
```

---

### replace_real_name.py - 替换真实名称

**文件位置**: `scripts/replace_real_name.py`

**功能描述**：
将配置文件中的占位符替换为真实的域名、用户名等信息。

**使用方法**：
```bash
python3 scripts/replace_real_name.py --domain cloud-doors.com
```

---

## 已删除的脚本

### 临时配置和测试脚本

| 脚本 | 删除原因 | 替代方案 |
|------|---------|----------|
| `QUICK_DEPLOY_SETUP.md` | 临时快速指南文档 | 已整合到 [CI/CD配置文档](./CICD/02-CONFIGURATION.md) |
| `diagnose-webhook.sh` | 临时诊断脚本 | 问题已解决，不再需要 |
| `fix-webhook-service.sh` | 临时修复脚本 | 功能已集成到 deploy.sh |
| `check_and_deploy_github.sh` | 旧版本检查脚本 | 已被新的 CI/CD 流程取代 |
| `check_config.py` | 配置检查脚本 | 功能已整合到 verify-deployment.sh |
| `check_dependencies.py` | 依赖检查脚本 | 功能已整合到主流程 |
| `check_deploy_config.py` | 部署配置检查 | 功能简单，保留 |
| `count_code.py` | 代码统计脚本 | 开发工具，非部署必需 |
| `create-test-pr.ps1` | PowerShell PR 创建脚本 | 改用 create-test-pr.sh |
| `deploy_service.sh` | 服务部署脚本 | 功能已整合到 deploy.sh |
| `verify_requirements.py` | 依赖验证脚本 | 功能已整合到主流程 |
| `verify-deployment.sh` | 部署验证脚本 | 功能简单，保留 |

### 不建议使用的脚本

| 脚本 | 不建议原因 | 建议替代方案 |
|------|-------------|-------------|
| `check_and_deploy_github.sh` | 与 GitHub Actions 功能重复 | 使用 GitHub Actions 的自动合并 |
| `deploy_service.sh` | 独编码服务配置 | 使用 systemd 管理 |
| `verify_requirements.py` | 过于严格的依赖检查 | 放宽依赖版本要求 |

---

## 脚本使用最佳实践

### 1. 部署脚本规范

**权限设置**：
```bash
# 设置可执行权限
chmod +x deploy.sh
chmod +x smart-pull.sh
chmod +x rollback.sh
```

**路径配置**：
- 使用绝对路径，避免相对路径问题
- 备份目录应在项目目录外
- 日志目录应有适当的权限

**错误处理**：
- 所有关键操作都应有错误处理
- 提供清晰的错误日志
- 失败时返回明确的错误代码

### 2. 环境变量管理

**敏感信息保护**：
- 不要在代码中硬编码密码、密钥
- 使用 `.env` 文件存储敏感信息
- `.env` 文件不要提交到 Git
- 使用 GitHub Secrets 管理部署密钥

**环境文件优先级**：
1. `.env` - 项目特定配置
2. `/etc/environment` - 系统级配置
3. 环境变量 - 运行时配置

### 3. 日志管理

**日志级别**：
- DEBUG: 开发调试信息
- INFO: 正常操作信息
- WARN: 警告信息
- ERROR: 错误信息

**日志轮换**：
```bash
# 配置 logrotate
/var/log/Home-page/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 4. 监控和告警

**监控指标**：
- 部署成功率
- 部署耗时
- 服务可用性
- 资源使用情况

**告警触发条件**：
- 部署失败
- 服务启动失败
- 健康检查连续失败 3 次
- 磁盘空间 < 5%

### 5. 安全实践

**密钥管理**：
- 定期轮换 Webhook 密钥
- 使用 ed25519 而非 RSA 密钥
- 私钥权限设置为 600
- 公钥权限设置为 644

**访问控制**：
- 使用最小权限原则
- 定期审计 SSH 访问日志
- 限制 GitHub Token 的作用域

---

## 脚本依赖关系图

```
┌─────────────────────────────────────────────────────────────┐
│                CI/CD 脚本依赖关系              │
└─────────────────────────────────────────────────────────────┘
                    ↓
        ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
        │  deploy.sh     │  │  smart-pull.sh  │  │  webhook...py   │
        └──────────────────┘  └──────────────────┘  └──────────────────┘
                 ↓                      ↓                  ↓
        ┌──────────────────────────────────────────────────┐
        │    核心部署流程                       │
        └──────────────────────────────────────────────────┘
                 ↓
        ┌──────────────────┐  ┌──────────────────┐
        │  rollback.sh     │  │  辅助脚本       │
        └──────────────────┘  └──────────────────┘
```

---

## 常用命令速查

### 部署相关

```bash
# 触发部署
./scripts/deploy.sh

# 查看部署日志
tail -f /var/log/Home-page/deploy.log

# 回滚到上一个版本
./scripts/rollback.sh

# 查看可用备份
ls -lh /var/backups/Home-page/

# 手动拉取代码
./scripts/smart-pull.sh
```

### 服务管理

```bash
# 重启应用服务
sudo systemctl restart Home-page

# 重启 webhook 服务
sudo systemctl restart webhook-receiver

# 查看服务状态
sudo systemctl status Home-page webhook-receiver

# 查看服务日志
sudo journalctl -u Home-page -f
```

### 配置检查

```bash
# 检查 Git 配置
./scripts/check_git_config.sh

# 生成安全配置
python3 scripts/generate_secure_env.py

# 运行测试
python3 scripts/test_routes.py
```

---

## 故障排查

### 部署失败

**问题 1**: 部署脚本无执行权限
```
错误：Permission denied
解决：chmod +x deploy.sh && ./deploy.sh
```

**问题 2**: 备份路径冲突
```
错误：cannot copy a directory into itself
解决：检查 BACKUP_DIR 配置，确保在项目目录外
```

**问题 3**: Git 拉取失败
```
错误：fatal: unable to access
解决：检查代理配置，检查 SSH 密钥
```

### 服务问题

**问题 1**: 服务无法启动
```
检查：systemctl status Home-page
解决：查看日志 journalctl -u Home-page -n 50
```

**问题 2**: 端口被占用
```
检查：netstat -tlnp | grep 5000
解决：停止占用端口的服务，或修改配置
```

---

## 文档参考

相关文档：
- [CI/CD 完整介绍](./CICD/01-INTRODUCTION.md)
- [CI/CD 配置总结](./CICD/02-CONFIGURATION.md)
- [CI/CD 部署历史](./CICD/03-DEPLOYMENT_HISTORY.md)
- [CI/CD 功能设计](./CICD/04-FEATURES.md)
- [CI/CD 故障排除](./CICD/05-TROUBLESHOOTING.md)
- [CI/CD 测试指南](./CICD/06-TESTING.md)

---

<div align="center">

**文档版本**: v1.0  
**创建日期**: 2026-03-04  
**维护者**: 云户科技技术团队

</div>
