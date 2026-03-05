# CI/CD 功能设计说明

> 云户科技网站 CI/CD 系统的功能设计和实现细节

---

## 📋 目录

1. [功能概览](#功能概览)
2. [核心功能](#核心功能)
3. [技术选型](#技术选型)
4. [架构设计](#架构设计)
5. [数据流设计](#数据流设计)
6. [安全设计](#安全设计)

---

## 功能概览

### 系统目标

建立从代码提交到生产部署的全自动化 CI/CD 流程，实现：

1. **持续集成 (CI)**
   - 自动化代码测试
   - 自动化代码质量检查
   - 自动化安全扫描
   - 自动化代码格式化

2. **持续部署 (CD)**
   - 自动化备份机制
   - 自动化代码拉取
   - 自动化依赖更新
   - 自动化服务重启
   - 自动化健康检查

3. **监控和告警**
   - 实时部署状态监控
   - 部署失败告警
   - 服务异常告警
   - 性能指标收集

### 核心功能列表

| 功能模块 | 状态 | 优先级 |
|---------|------|--------|
| 自动化测试 | ✅ 已实现 | 🔴 高 |
| 代码质量检查 | ✅ 已实现 | 🔴 高 |
| 安全扫描 | ✅ 已实现 | 🔴 高 |
| 自动合并 | ✅ 已实现 | 🟡 中 |
| SSH 自动部署 | ✅ 已实现 | 🔴 高 |
| 自动备份 | ✅ 已实现 | 🔴 高 |
| 智能拉取 | ✅ 已实现 | 🟡 中 |
| 版本回滚 | ✅ 已实现 | 🟡 中 |
| 日志记录 | ✅ 已实现 | 🔴 高 |
| 健康检查 | ✅ 已实现 | 🔴 高 |
| 监控告警 | ⏳ 待实现 | 🟢 低 |

---

## 核心功能

### 1. GitHub Actions 工作流

**功能描述：**
自动响应 GitHub 事件，执行 CI/CD 任务流水线

**触发条件：**
- Push 事件到 `main` 分支
- Pull Request 创建/更新
- 手动触发 (workflow_dispatch)

**工作流步骤：**

#### 步骤 1: 代码检查 (Code Check)

```yaml
- name: Code Check
  run: |
    python -m py_compile app.py
    python -m flake8 --max-line-length=120 routes/
```

**功能点：**
- ✅ Python 语法检查
- ✅ 代码风格检查 (PEP 8)
- ✅ 导入依赖检查

**技术实现：**
- 使用 `actions/checkout` 检出代码
- 使用 Python 内置 `py_compile` 编译检查
- 使用 `flake8` 进行代码质量检查

#### 步骤 2: 单元测试 (Unit Tests)

```yaml
- name: Run Tests
  run: |
    pip install -r requirements-dev.txt
    pytest tests/ -v --cov=. --cov-report=xml
```

**功能点：**
- ✅ 自动运行所有测试
- ✅ 生成覆盖率报告
- ✅ 测试失败阻止部署

**技术实现：**
- 使用 `pytest` 测试框架
- 使用 `pytest-cov` 生成覆盖率
- 覆盖率报告上传到 Codecov

#### 步骤 3: 代码质量检查

```yaml
- name: Code Quality
  run: |
    pylint app.py routes/ services/ --max-line-length=120
```

**功能点：**
- ✅ 代码复杂度分析
- ✅ 潜在 Bug 检测
- ✅ 代码风格统一

**技术实现：**
- 使用 `pylint` 静态分析工具
- 配置合理的阈值

#### 步骤 4: 安全扫描

```yaml
- name: Security Scan
  run: |
    bandit -r app/ routes/ services/ -f json -o security-report.json
```

**功能点：**
- ✅ 安全漏洞检测
- ✅ SQL 注入风险检查
- ✅ XSS 风险检查

**技术实现：**
- 使用 `bandit` 安全扫描工具
- 生成 JSON 格式报告

#### 步骤 5: SSH 部署

```yaml
- name: Deploy via SSH
  run: |
    chmod +x ./scripts/deploy.sh
    bash ./scripts/deploy.sh
```

**功能点：**
- ✅ SSH 连接测试
- ✅ 远程执行部署脚本
- ✅ 错误处理和重试

**技术实现：**
- 使用 SSH 连接云主机
- 执行远程部署脚本
- 监控执行状态

---

### 2. 自动部署脚本

**文件位置**: `scripts/deploy.sh`

**执行步骤：**

#### 步骤 1: 创建备份

```bash
create_backup() {
    BACKUP_NAME="${APP_NAME}_$(date '+%Y%m%d_%H%M%S')"
    BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"
    
    # 使用 rsync 进行增量备份
    rsync -av --delete "$PROJECT_DIR/" "$BACKUP_PATH/"
    
    # 保留最近 5 个备份
    ls -t | tail -n +6 | xargs rm -rf
}
```

**功能点：**
- ✅ 增量备份，只备份变化的文件
- ✅ 自动清理过期备份
- ✅ 备份命名包含时间戳

#### 步骤 2: 拉取代码

```bash
pull_code() {
    cd "$PROJECT_DIR"
    
    # 智能选择最快的源
    if smart-pull.sh; then
        echo "智能拉取成功"
    else
        # 备用方案：直接从 GitHub 拉取
        git fetch origin
        git reset --hard origin/main
    fi
}
```

**功能点：**
- ✅ 智能选择 GitHub/Gitee 源
- ✅ 失败自动重试
- ✅ 显示当前版本

#### 步骤 3: 更新依赖

```bash
update_dependencies() {
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
}
```

**功能点：**
- ✅ 使用虚拟环境
- ✅ 自动安装新依赖
- ✅ 处理依赖冲突

#### 步骤 4: 重启服务

```bash
restart_app() {
    # 停止旧进程
    pkill -f "app.py"
    
    # 启动新进程
    nohup venv/bin/python app.py > /var/log/app.log 2>&1 &
    
    # 等待启动
    sleep 5
    
    # 验证服务状态
    if pgrep -f "app.py" > /dev/null; then
        echo "服务启动成功"
    else
        echo "服务启动失败"
        exit 1
    fi
}
```

**功能点：**
- ✅ 优雅停止旧进程
- ✅ 后台启动新进程
- ✅ 启动验证

---

### 3. 智能拉取机制

**文件位置**: `scripts/smart-pull.sh`

**智能选择逻辑：**
```bash
# 测试 GitHub 连接速度
SPEED_GITHUB=$(measure_speed github.com)

# 测试 Gitee 连接速度
SPEED_GITEE=$(measure_speed gitee.com)

# 选择最快的源
if [ "$SPEED_GITHUB" -gt "$SPEED_GITEE" ]; then
    echo "选择 Gitee 作为拉取源"
    git pull gitee main
else
    echo "选择 GitHub 作为拉取源"
    git pull origin main
fi
```

**功能点：**
- ✅ 自动测速选择最快源
- ✅ 失败自动切换源
- ✅ 支持国内镜像加速

---

### 4. 回滚脚本

**文件位置**: `scripts/rollback.sh`

**回滚流程：**
```bash
rollback_to_backup() {
    # 1. 列出可用备份
    echo "可用备份："
    ls -t "$BACKUP_DIR" | head -5
    
    # 2. 选择备份
    read -p "选择备份版本: " BACKUP_NAME
    
    # 3. 停止服务
    pkill -f "app.py"
    
    # 4. 恢复备份
    rsync -av "$BACKUP_DIR/$BACKUP_NAME/" "$PROJECT_DIR/"
    
    # 5. 重启服务
    restart_app
}
```

**功能点：**
- ✅ 列出所有备份版本
- ✅ 选择性恢复
- ✅ 验证回滚成功

---

## 技术选型

### CI/CD 工具

| 类别 | 技术选型 | 理由 |
|------|---------|------|
| CI 平台 | GitHub Actions | 与 GitHub 深度集成，免费额度充足 |
| 版本控制 | Git 2.x | 行业标准，功能强大 |
| 远程部署 | SSH | 安全可靠，不依赖外部网络 |
| 测试框架 | pytest | 功能强大，插件丰富 |
| 代码检查 | flake8, pylint | 标准 Python 工具链 |
| 安全扫描 | bandit | 专注于 Python 安全 |

### 部署工具

| 工具 | 用途 | 优势 |
|------|------|------|
| rsync | 文件同步 | 增量备份，速度快 |
| bash | 脚本语言 | 跨平台兼容，内置 |
| systemd | 服务管理 | 标准化，自动重启 |
| ufw | 防火墙 | 简单易用 |

---

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD 系统架构                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
        ┌──────────────────┐  ┌──────────────────┐
        │  GitHub Actions  │  │  云主机 SSH      │
        └──────────────────┘  └──────────────────┘
                 ↓                      ↓
        ┌───────────────────────────────────────┐
        │  自动化部署流程                   │
        └───────────────────────────────────────┘
                 ↓
        ┌──────────────────┐  ┌──────────────────┐
        │   应用服务      │  │   备份存储     │
        └──────────────────┘  └──────────────────┘
```

### 模块划分

| 模块 | 职责 | 输入 | 输出 |
|------|------|------|------|
| CI 模块 | 代码检查、测试 | 代码提交 | 测试报告 |
| 部署模块 | 自动部署 | CI 通过 | 部署状态 |
| 监控模块 | 状态监控 | 运行状态 | 告警信息 |
| 备份模块 | 版本备份 | 代码变更 | 备份文件 |

---

## 数据流设计

### 部署数据流

```
开发者提交代码
    ↓
GitHub Push 事件
    ↓
GitHub Actions 触发
    ↓
├─ 代码检查
├─ 运行测试
├─ 安全扫描
└─ SSH 部署
    ↓
云主机执行 deploy.sh
    ↓
├─ 创建备份
├─ 拉取代码
├─ 更新依赖
└─ 重启服务
    ↓
部署完成，通知结果
```

### 监控数据流

```
服务运行状态
    ↓
健康检查端点
    ↓
状态数据收集
    ↓
日志记录
    ↓
告警判断
    ↓
发送告警（如需要）
```

---

## 安全设计

### SSH 密钥管理

**密钥生成：**
```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_key
```

**密钥存储：**
- 私钥：GitHub Secrets（加密存储）
- 公钥：云主机 `~/.ssh/authorized_keys`

**密钥轮换：**
- 定期更换（建议每 3 个月）
- 泄露立即更换
- 使用强密码短语（可选）

### 访问控制

**最小权限原则：**
- SSH 用户仅能执行部署脚本
- 服务用户仅能运行应用
- 数据库用户仅能访问所需数据库

**文件权限：**
```bash
# SSH 密钥
chmod 600 ~/.ssh/github_actions_key
chmod 644 ~/.ssh/github_actions_key.pub

# authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 脚本文件
chmod 755 scripts/*.sh
```

### 网络安全

**防火墙规则：**
```bash
# 仅开放必要端口
ufw allow 22/tcp    # SSH
ufw allow 5000/tcp  # 应用
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
```

**SSH 配置：**
```bash
# /etc/ssh/sshd_config
PermitRootLogin without-password
PasswordAuthentication no
PubkeyAuthentication yes
```

### 数据安全

**敏感信息保护：**
- ✅ 使用 GitHub Secrets
- ✅ 不在日志中输出敏感信息
- ✅ 使用环境变量
- ❌ 不将密钥提交到代码库

**日志管理：**
```bash
# 配置日志轮换
/var/log/app.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
}
```

---

## 扩展功能

### 未来规划

1. **监控告警**
   - 集成 Prometheus + Grafana
   - 实时性能监控
   - 智能告警

2. **灰度发布**
   - 支持 A/B 测试
   - 金丝雀部署
   - 自动回滚

3. **多环境支持**
   - 开发环境
   - 测试环境
   - 预发布环境
   - 生产环境

4. **性能优化**
   - 并行部署
   - 缓存优化
   - 增量部署

---

## 相关文档

- [CI/CD 快速使用指南](./00-QUICK_START.md)
- [CI/CD 完整介绍](./01-INTRODUCTION.md)
- [CI/CD 配置指南](./02-CONFIGURATION.md)
- [CI/CD 部署历史](./03-DEPLOYMENT_HISTORY.md)
- [CI/CD 故障排除](./05-TROUBLESHOOTING.md)
- [CI/CD 测试指南](./06-TESTING.md)

---

<div align="center">

**文档版本**: v2.0
**创建日期**: 2026-03-04
**最后更新**: 2026-03-05
**维护者**: 云户科技技术团队

</div>
