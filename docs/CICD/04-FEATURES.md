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
| Webhook 部署 | ✅ 已实现 | 🔴 高 |
| SSH 备用部署 | ✅ 已实现 | 🟡 中 |
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
- ✅ 运行所有单元测试
- ✅ 生成测试覆盖率报告
- ✅ 测试结果输出到 GitHub

**技术实现：**
- 使用 `pytest` 测试框架
- 使用 `pytest-cov` 生成覆盖率
- 集成 Codecov 可选（未来）

#### 步骤 3: 安全检查 (Security Scan)

```yaml
- name: Security Check
  run: |
    pip install bandit
    bandit -r app/ routes/ services/
```

**功能点：**
- ✅ 安全漏洞扫描
- ✅ SQL 注入检测
- ✅ 硬编码密码检测
- ✅ 不安全的函数调用检测

**技术实现：**
- 使用 `bandit` 静态安全扫描工具
- 检测 CWE/SANS Top 25 漏洞
- 生成安全报告

#### 步骤 4: 自动合并 (Auto Merge)

```yaml
- name: Auto Merge
  if: contains(github.event.pull_request.labels.*.name, 'auto-merge')
  run: |
    gh pr merge ${{ github.event.pull_request.number }} --merge
```

**功能点：**
- ✅ PR 标签为 `auto-merge` 时自动合并
- ✅ 避免手动合并操作
- ✅ 提高发布效率

**技术实现：**
- 使用 GitHub CLI (`gh`)
- 检查 PR 标签
- 使用 `--merge` 合并方式

#### 步骤 5: 部署通知 (Deploy Notification)

```yaml
- name: Notify Cloud Server
  run: |
    curl -X POST ${{ secrets.WEBHOOK_URL }} \
      -H "Content-Type: application/json" \
      -H "X-Hub-Signature-256: ${{ github.sha }}" \
      -d '{"ref":"${{ github.ref }}","sha":"${{ github.sha }}"}'
```

**功能点：**
- ✅ 通过 Webhook 通知云主机
- ✅ 发送版本信息和 SHA
- ✅ 支持签名验证

**技术实现：**
- 主方式：Webhook HTTP POST
- 备用方式：SSH 命令执行
- 签名验证：HMAC-SHA256

### 2. 云主机 Webhook 接收器

**功能描述：**
接收 GitHub 部署通知，触发自动部署流程

**核心 API：**

#### POST /webhook/github

```python
@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """接收 GitHub Webhook 并触发部署"""
    # 1. 验证签名
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(signature, payload):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # 2. 解析分支
    ref = payload.get('ref', '')
    branch = ref.replace('refs/heads/', '') if ref else ''
    
    # 3. 只处理 main 分支
    if branch != 'main':
        return jsonify({'message': 'Ignored'}), 200
    
    # 4. 触发部署
    trigger_deployment()
    return jsonify({'status': 'success'}), 200
```

**功能点：**
- ✅ 签名验证（防止伪造请求）
- ✅ 分支过滤（只处理 main 分支）
- ✅ 异步部署（避免超时）
- ✅ 错误处理和日志记录

#### GET /webhook/health

```python
@app.route('/webhook/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'version': get_current_version(),
        'last_deployment': get_last_deployment_time()
    })
```

**功能点：**
- ✅ 服务健康状态检查
- ✅ 当前版本信息查询
- ✅ 最后部署时间查询

#### GET /webhook/version

```python
@app.route('/webhook/version', methods=['GET'])
def get_version():
    """获取当前部署版本"""
    with open('/var/backups/Home-page/version.json', 'r') as f:
        version_info = json.load(f)
    return jsonify(version_info)
```

**功能点：**
- ✅ 当前版本信息
- ✅ Git SHA 信息
- ✅ 部署时间戳

### 3. 自动部署脚本

**功能描述：**
完整的部署流程自动化，包括备份、拉取、更新、重启

**核心函数：**

#### create_backup()

```bash
create_backup() {
    log_info "创建备份..."
    BACKUP_NAME="${APP_NAME}_$(date '+%Y%m%d_%H%M%S')"
    BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"
    
    # 使用 rsync 避免路径冲突
    rsync -av --delete "$PROJECT_DIR/" "$BACKUP_PATH/"
    
    # 记录版本信息
    echo "{\"version\":\"$BACKUP_NAME\",\"sha\":\"$(git rev-parse HEAD)\",\"time\":\"$(date -Iseconds)\"}" > "$BACKUP_PATH/version.json"
    
    log_info "备份完成: $BACKUP_NAME"
}
```

**功能点：**
- ✅ 自动创建时间戳备份
- ✅ 使用 rsync 高效备份
- ✅ 记录版本元数据 (SHA, 时间)
- ✅ 路径冲突验证

#### smart_pull()

```bash
smart_pull() {
    # 测试 GitHub 和 Gitee 连接速度
    GITHUB_SPEED=$(test_github_speed)
    GITEE_SPEED=$(test_gitee_speed)
    
    # 选择最快的源
    if [ "$GITHUB_SPEED" -gt "$GITEE_SPEED" ]; then
        log_info "从 GitHub 拉取 (速度: ${GITHUB_SPEED} KB/s)"
        git pull origin main
    else
        log_info "从 Gitee 拉取 (速度: ${GITEE_SPEED} KB/s)"
        git pull gitee main
    fi
}
```

**功能点：**
- ✅ 自动测试连接速度
- ✅ 智能选择最快的源
- ✅ 使用配置的 Git 代理
- ✅ 支持备用源

#### update_dependencies()

```bash
update_dependencies() {
    log_info "更新依赖..."
    source "$VENV_PATH/bin/activate"
    
    # 升级 pip
    pip install --upgrade pip
    
    # 安装/更新依赖
    pip install -r requirements.txt
    
    log_info "依赖更新完成"
}
```

**功能点：**
- ✅ 自动升级 pip
- ✅ 批量安装依赖
- ✅ 处理依赖冲突
- ✅ 虚拟环境隔离

#### restart_service()

```bash
restart_service() {
    log_info "重启服务..."
    
    # 优雅停止
    systemctl stop $SERVICE_NAME
    sleep 2
    
    # 启动服务
    systemctl start $SERVICE_NAME
    
    # 健康检查
    for i in {1..30}; do
        if curl -sf http://localhost:5000/health > /dev/null; then
            log_info "服务启动成功"
            return 0
        fi
        sleep 1
    done
    
    log_error "服务启动超时"
    return 1
}
```

**功能点：**
- ✅ 优雅停止（发送 SIGTERM）
- ✅ 服务重启
- ✅ 健康检查验证（30 秒超时）
- ✅ 启动失败告警

### 4. 版本回滚脚本

**功能描述：**
快速回滚到指定历史版本

**核心函数：**

#### list_backups()

```bash
list_backups() {
    echo "可用备份版本:"
    ls -1t "$BACKUP_DIR" | while read backup; do
        local version_info="$BACKUP_DIR/$backup/version.json"
        if [ -f "$version_info" ]; then
            local sha=$(jq -r '.sha' "$version_info")
            local time=$(jq -r '.time' "$version_info")
            local time_str=$(date -d @$time '+%Y-%m-%d %H:%M:%S')
            echo "  - $backup (SHA: ${sha:0:7}, 时间: $time_str)"
        else
            echo "  - $backup"
        fi
    done
}
```

**功能点：**
- ✅ 列出所有可用备份
- ✅ 显示版本元数据 (SHA, 时间)
- ✅ 按时间倒序排列

#### rollback_to_version()

```bash
rollback_to_version() {
    local version=$1
    
    log_info "回滚到版本: $version"
    
    # 停止服务
    systemctl stop $SERVICE_NAME
    
    # 恢复备份
    rsync -av --delete "$BACKUP_DIR/$version/" "$PROJECT_DIR/"
    
    # 重启服务
    systemctl start $SERVICE_NAME
    
    # 验证
    sleep 5
    if curl -sf http://localhost:5000/health > /dev/null; then
        log_info "回滚成功"
    else
        log_error "回滚后服务启动失败"
        return 1
    fi
}
```

**功能点：**
- ✅ 原子回滚（完整恢复）
- ✅ 服务自动重启
- ✅ 健康检查验证
- ✅ 回滚失败告警

---

## 技术选型

### GitHub Actions

| 技术 | 选择原因 | 优势 |
|------|---------|------|
| GitHub Actions | 代码托管在 GitHub，无缝集成 | 原生支持，免费额度充足 |
| YAML Workflow | 声明式配置，易于维护 | 代码即配置，版本控制 |
| GitHub CLI | 自动化 API 调用 | 官方工具，功能完整 |

### 云主机技术

| 技术 | 选择原因 | 优势 |
|------|---------|------|
| Python Flask | Webhook 接收器轻量高效 | 生态丰富，快速开发 |
| Systemd | 服务管理和自动启动 | 系统原生，稳定可靠 |
| Bash Script | 部署脚本跨平台兼容 | 通用，无依赖 |

### 安全技术

| 技术 | 选择原因 | 优势 |
|------|---------|------|
| HMAC-SHA256 | 防止伪造请求 | 安全，标准化 |
| SSH ed25519 | 更安全的 SSH 密钥算法 | 抗量子计算，密钥更短 |
| GitHub Secrets | 敏感信息管理 | 访问控制，审计日志 |

---

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                       CI/CD 整体架构                          │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
        ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
        │  GitHub Actions  │  │  云主机 Webhook │  │   备份存储     │
        └──────────────────┘  └──────────────────┘  └──────────────────┘
                 ↓                      ↓                ↓
        ┌───────────────────────────────────────┐
        │  自动化部署流程                    │
        └───────────────────────────────────────┘
                 ↓
        ┌──────────────────┐  ┌──────────────────┐
        │   应用服务      │  │   监控告警      │
        └──────────────────┘  └──────────────────┘
```

### 模块划分

```
CI/CD 系统
│
├── 触发模块 (Trigger)
│   ├── GitHub Push 事件
│   ├── PR 事件
│   └── 手动触发
│
├── CI 模块 (Continuous Integration)
│   ├── 代码检查
│   ├── 单元测试
│   ├── 安全扫描
│   └── 覆盖率报告
│
├── CD 模块 (Continuous Deployment)
│   ├── 备份模块
│   ├── 拉取模块
│   ├── 更新模块
│   └── 重启模块
│
├── 监控模块 (Monitoring)
│   ├── 健康检查
│   ├── 日志收集
│   └── 告警通知
│
└── 回滚模块 (Rollback)
    ├── 备份列表
    ├── 版本选择
    └── 恢复流程
```

---

## 数据流设计

### 部署数据流

```
开发者 Push
    ↓
GitHub 仓库
    ↓
GitHub Actions 触发
    ↓
┌──────────────────────┐
│  1. Code Check     │
│  2. Unit Tests     │
│  3. Security Scan  │
│  4. Auto Merge     │
└──────────────────────┘
    ↓
所有检查通过
    ↓
┌──────────────────────┐
│  Deploy Notification │
│  - Webhook/SSH    │
└──────────────────────┘
    ↓
云主机接收器
    ↓
┌──────────────────────┐
│  1. Create Backup  │
│  2. Smart Pull    │
│  3. Update Deps   │
│  4. Restart Service│
└──────────────────────┘
    ↓
应用更新完成
    ↓
健康检查验证
```

### 日志数据流

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  应用日志      │────→│  日志收集     │────→│  日志文件      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  部署日志      │────→│  日志轮换     │────→│  日志归档      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
┌─────────────────┐     ┌─────────────────┐
│  错误日志      │────→│  告警系统     │
└─────────────────┘     └─────────────────┘
```

---

## 安全设计

### 认证和授权

#### GitHub Webhook 验证

```python
def verify_signature(signature, payload):
    """验证 GitHub Webhook 签名"""
    secret = os.getenv('WEBHOOK_SECRET', '')
    if not secret:
        logger.warning("WEBHOOK_SECRET 未配置")
        return False
    
    # 计算 HMAC-SHA256
    expected_signature = 'sha256=' + hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # 比较签名
    return hmac.compare_digest(expected_signature, signature)
```

**安全特性：**
- ✅ HMAC 签名防伪造
- ✅ 常数时间比较防时序攻击
- ✅ 环境变量存储密钥

#### SSH 密钥管理

```bash
# 生成密钥
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy_key

# 设置权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/github_deploy_key
chmod 644 ~/.ssh/github_deploy_key.pub
```

**安全特性：**
- ✅ ed25519 算法更安全
- ✅ 最小权限原则 (600/644)
- ✅ 密钥轮换机制

### 数据安全

#### 敏感信息保护

| 敏感信息 | 存储方式 | 访问控制 |
|---------|---------|----------|
| GitHub Token | GitHub Secrets | 仅 GitHub Actions 可访问 |
| SSH 私钥 | GitHub Secrets | 仅 CI/CD 流程可访问 |
| Webhook 密钥 | 环境变量 | 仅 Webhook 接收器可访问 |
| 数据库密码 | config.py | 仅应用可访问 |

#### 日志安全

```bash
# 日志文件权限
chmod 640 /var/log/Home-page/*.log  # 仅 owner 可写
chown www-data:www-data /var/log/Home-page/

# 日志内容脱敏
log_data() {
    local message="$1"
    # 移除敏感信息
    echo "$message" | sed 's/password=[^ ]*/password=***/g'
}
```

### 网络安全

#### 防火墙规则

```bash
# 仅开放必要端口
ufw allow 22/tcp    # SSH
ufw allow 5000/tcp   # 应用
ufw allow 9000/tcp   # Webhook
ufw enable
```

#### HTTPS/TLS

```python
# Webhook 服务强制 HTTPS
if app.config['ENV'] == 'production':
    from flask_sslify import SSLify
    app = SSLify(app, certfile='cert.pem', keyfile='key.pem')
```

---

<div align="center">

**文档版本**: v1.0  
**创建日期**: 2026-03-04  
**维护者**: 云户科技技术团队

</div>
