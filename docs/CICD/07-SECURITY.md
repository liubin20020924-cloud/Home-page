# CI/CD 安全指南

## 📋 概述

本文档详细说明了 Home-page 项目 CI/CD 系统的安全措施、潜在风险以及相应的修复方案。通过实施这些安全措施，可以显著提高 CI/CD 流程的安全性，防止各种安全威胁。

## 🔐 安全等级定义

| 等级 | 描述 | 处理优先级 | 示例 |
|------|------|-----------|------|
| 🔴 高危 | 可能导致严重安全漏洞或数据泄露 | 立即修复 | 私钥泄露、代码注入 |
| 🟡 中危 | 可能导致中等程度的安全问题 | 尽快修复 | 权限配置不当、缺少验证 |
| 🟢 低危 | 潜在的安全风险，影响较小 | 计划修复 | 日志清理策略、版本管理 |

## 🚨 已识别的安全隐患与修复

### 高危风险（High Severity）

#### 1. SSH 私钥泄露风险

**问题描述**: SSH 私钥被写入 GitHub Actions 日志，如果日志被公开访问可能导致私钥泄露。

**位置**: `.github/workflows/ci-cd.yml:180`

**原始代码**:
```bash
echo "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
```

**风险分析**:
- GitHub Actions 日志可能被公开访问
- 攻击者获取私钥后可以访问云主机
- 可能导致服务器被完全控制

**修复方案**:
```yaml
# 在写入私钥前后禁用命令回显
set +x
mkdir -p ~/.ssh
echo "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
chmod 600 ~/.ssh/deploy_key
set -x

# 清理时也禁用命令回显
set +x
rm -f ~/.ssh/deploy_key
rm -f ~/.ssh/known_hosts
set -x
```

**验证方法**:
1. 在 GitHub Actions 运行日志中搜索 "SSH_PRIVATE_KEY"
2. 确认私钥内容不会出现在日志中
3. 检查部署脚本的执行日志

**相关文档**:
- GitHub Actions Secrets: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- SSH 密钥管理: https://www.ssh.com/academy/ssh/key

---

#### 2. 缺少代码签名验证

**问题描述**: 直接拉取代码，没有验证提交者身份和 GPG 签名。如果 GitHub 账户被入侵或仓库被篡改，会部署恶意代码。

**位置**: `scripts/deploy.sh:89`

**原始代码**:
```bash
git reset --hard origin/main
```

**风险分析**:
- 恶意提交可能被部署到生产环境
- 无法追溯代码来源的真实性
- 供应链攻击风险

**修复方案**:
```bash
# 添加签名验证函数
verify_commit_signature() {
    log_info "验证提交签名..."

    cd "$PROJECT_DIR"

    # 检查是否配置了 GPG 签名验证
    if ! git config --get commit.gpgsign >/dev/null 2>&1; then
        log_warn "未配置 GPG 签名验证，跳过验证步骤"
        return 0
    fi

    # 验证最新提交的签名
    LATEST_COMMIT=$(git rev-parse origin/main)
    if ! git verify-commit "$LATEST_COMMIT" 2>/dev/null; then
        log_error "提交签名验证失败，拒绝部署"
        log_error "提交哈希: $LATEST_COMMIT"
        exit 1
    fi

    log_info "提交签名验证通过"
}

# 在 pull_code 函数中调用
pull_code() {
    # ... 前面的代码 ...
    git fetch origin
    if [ $? -eq 0 ]; then
        # 验证提交签名
        verify_commit_signature
        git reset --hard origin/main
        # ... 后面的代码 ...
    fi
}
```

**GPG 签名配置步骤**:
```bash
# 1. 生成 GPG 密钥
gpg --full-generate-key

# 2. 导出公钥
gpg --armor --export your-email@example.com > public-key.asc

# 3. 将公钥添加到 GitHub
# Settings -> SSH and GPG keys -> New GPG key

# 4. 配置 Git 使用 GPG 签名
git config --global commit.gpgsign true
git config --global gpg.program gpg
git config --global user.signingkey YOUR_GPG_KEY_ID

# 5. 为现有提交添加签名（可选）
git commit --amend --no-edit -S
```

**验证方法**:
```bash
# 检查提交是否已签名
git log --show-signature

# 验证特定提交
git verify-commit <commit-hash>
```

**相关文档**:
- Git GPG 签名: https://git-scm.com/book/zh/v2/Git-%E5%B7%A5%E5%85%B7-%E7%AD%BE%E5%90%8D%E5%B7%A5%E4%BD%9C
- GitHub GPG 密钥: https://docs.github.com/en/authentication/managing-commit-signature-verification/adding-a-gpg-key-to-your-github-account

---

#### 3. 自动合并存在供应链攻击风险

**问题描述**: 自动合并逻辑不够严格，可能导致恶意 PR 被合并。

**位置**: `.github/workflows/ci-cd.yml:104-136`

**原始代码**:
```yaml
auto-merge:
  if: |
    github.event_name == 'pull_request' &&
    github.event.pull_request.base.ref == 'main' &&
    github.event.pull_request.head.repo.full_name == github.repository
```

**风险分析**:
- `if: failure()` 会导致任何失败都会触发自动合并
- PR 状态检查不完整
- 可能被绕过安全检查

**修复方案**:
```yaml
auto-merge:
  name: Auto Merge to Main
  needs: [test, lint, security]
  # 严格检查条件
  if: |
    github.event_name == 'pull_request' &&
    github.event.pull_request.base.ref == 'main' &&
    github.event.pull_request.head.repo.full_name == github.repository &&
    contains(github.event.pull_request.labels.*.name, 'auto-merge')
  runs-on: ubuntu-latest
  permissions:
    contents: write
    pull-requests: write

  steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Merge PR with label check
      run: |
        # 验证 PR 状态
        PR_STATE=$(gh pr view ${{ github.event.pull_request.number }} --json state --jq .state)
        if [ "$PR_STATE" != "OPEN" ]; then
          echo "PR 状态不是 OPEN，跳过自动合并"
          exit 0
        fi

        # 验证 auto-merge 标签是否存在
        HAS_LABEL=$(gh pr view ${{ github.event.pull_request.number }} --json labels --jq '.labels[] | select(.name == "auto-merge") | .name')
        if [ -z "$HAS_LABEL" ]; then
          echo "PR 缺少 'auto-merge' 标签，跳过自动合并"
          exit 0
        fi

        # 执行合并
        gh pr merge ${{ github.event.pull_request.number }} --squash --delete-branch
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**使用方法**:
1. 创建 PR
2. 添加 `auto-merge` 标签
3. 等待所有检查通过
4. 自动合并到 main 分支

**验证方法**:
1. 测试没有 `auto-merge` 标签的 PR 不应该自动合并
2. 测试检查失败的 PR 不应该自动合并
3. 测试已关闭的 PR 不应该自动合并

**相关文档**:
- GitHub 自动合并: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request
- PR 标签: https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels

---

### 中危风险（Medium Severity）

#### 4. pip 依赖安装缺少安全验证

**问题描述**: 没有验证依赖包的完整性和签名，可能受到供应链攻击（恶意依赖包）。

**位置**: `.github/workflows/ci-cd.yml:35` 和 `scripts/deploy.sh:114`

**原始代码**:
```bash
pip install -r requirements.txt
```

**风险分析**:
- PyPI 上可能存在恶意包
- 依赖包可能被劫持
- 版本范围可能导致不可预测的依赖

**修复方案**:
```yaml
# 在 GitHub Actions 中添加依赖安全扫描
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    # 安全检查：扫描依赖漏洞
    pip install pip-audit
    pip-audit --desc || echo "依赖安全扫描完成（发现潜在问题）"
```

**高级方案（使用哈希验证）**:
```bash
# 1. 生成依赖哈希文件
pip install pip-tools
pip-compile requirements.in --generate-hashes

# 2. 在 requirements.txt 中使用哈希验证
# example==1.0.0 \
#     --hash=sha256:abc123... \
#     --hash=sha256:def456...

# 3. 安装时验证哈希
pip install -r requirements.txt --require-hashes --no-deps
```

**依赖安全最佳实践**:
1. 定期更新依赖：`pip list --outdated`
2. 使用虚拟环境隔离依赖
3. 锁定依赖版本：`pip freeze > requirements.lock`
4. 使用可信的镜像源：`pip install -i https://pypi.org/simple`
5. 审计依赖漏洞：`pip-audit --desc`

**验证方法**:
```bash
# 扫描依赖漏洞
pip-audit --desc

# 检查依赖树
pipdeptree

# 查看过期的依赖
pip list --outdated
```

**相关文档**:
- pip-audit: https://pypi.org/project/pip-audit/
- Pip 安全最佳实践: https://pip.pypa.io/en/stable/topics/security/

---

#### 5. 远程命令执行缺少白名单验证（已修复）

**问题描述**: 使用 `StrictHostKeyChecking=no` 容易受到中间人攻击，直接执行脚本没有验证完整性。

**位置**: `.github/workflows/ci-cd.yml:204-205`

**修复方案**:
```bash
# 预先验证主机指纹
SSH_KNOWN_HASH=$(ssh-keyscan -p "$SSH_PORT" -H "$SSH_HOST" 2>/dev/null | grep "ssh-ed25519")
if [ -z "$SSH_KNOWN_HASH" ]; then
    echo "无法获取主机指纹"
    exit 1
fi
echo "$SSH_KNOWN_HASH" >> ~/.ssh/known_hosts

# 使用严格主机密钥检查
ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=yes -o ConnectTimeout=10 -p "$SSH_PORT" \
  "$SSH_USERNAME@$SSH_HOST" "cd /opt/Home-page && chmod +x ./scripts/deploy.sh && bash ./scripts/deploy.sh"
```

**SSH 安全最佳实践**:
1. 使用 ed25519 密钥（比 RSA 更安全）
2. 禁用密码认证：`PasswordAuthentication no`
3. 限制 SSH 用户权限
4. 使用密钥密码短语
5. 定期轮换 SSH 密钥
6. 启用 fail2ban 防止暴力破解

**验证方法**:
```bash
# 测试 SSH 连接
ssh -i ~/.ssh/deploy_key -o StrictHostKeyChecking=yes -o ConnectTimeout=10 user@host

# 检查主机密钥
ssh-keyscan -H host

# 验证 known_hosts
cat ~/.ssh/known_hosts
```

---

#### 6. 日志文件权限不安全

**问题描述**: 日志文件没有明确的权限设置，可能包含敏感信息。

**位置**: `scripts/deploy.sh:11`

**修复方案**:
```bash
# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
    # 设置日志文件权限为仅所有者可读写
    if [ -f "$LOG_FILE" ]; then
        chmod 600 "$LOG_FILE"
    fi
}
```

**日志安全最佳实践**:
1. 不要记录敏感信息（密码、密钥、令牌）
2. 设置严格的文件权限（600 或 640）
3. 定期清理旧日志
4. 使用日志轮转（logrotate）
5. 加密敏感日志

**logrotate 配置示例**:
```
/var/log/Home-page/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 600 root root
    sharedscripts
    postrotate
        # 可以在这里添加日志处理脚本
    endscript
}
```

**验证方法**:
```bash
# 检查日志文件权限
ls -la /var/log/Home-page/

# 测试日志写入
echo "test log" | tee -a /var/log/Home-page/deploy.log

# 验证权限
stat /var/log/Home-page/deploy.log
```

---

#### 7. 缺少部署前环境检查

**问题描述**: 没有检查目标环境是否符合部署要求（如磁盘空间、内存、Python版本等）。

**位置**: `scripts/deploy.sh:189`

**修复方案**:
```bash
# 部署前环境检查
pre_deploy_check() {
    log_info "预部署检查..."

    # 检查磁盘空间（至少 1GB）
    AVAILABLE_SPACE=$(df -BG "$PROJECT_DIR" | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 1 ]; then
        log_error "磁盘空间不足，至少需要 1GB，当前: ${AVAILABLE_SPACE}GB"
        exit 1
    fi
    log_info "磁盘空间检查通过: ${AVAILABLE_SPACE}GB 可用"

    # 检查 Python 版本
    if ! command -v python3 &> /dev/null; then
        log_error "未找到 Python3"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    log_info "Python 版本: $PYTHON_VERSION"

    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        log_error "未找到 pip3"
        exit 1
    fi
    log_info "Pip 检查通过"

    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        log_warn "虚拟环境不存在，将使用系统 Python"
    else
        log_info "虚拟环境已存在"
    fi

    # 检查 requirements.txt
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt 文件不存在"
        exit 1
    fi
    log_info "requirements.txt 检查通过"

    # 检查部署脚本
    if [ ! -f "./scripts/deploy.sh" ]; then
        log_error "部署脚本不存在: ./scripts/deploy.sh"
        exit 1
    fi
    log_info "部署脚本检查通过"

    log_info "预部署检查通过"
}

# 在 main 函数开头调用
main() {
    log_info "========================================"
    log_info "开始部署: $APP_NAME"
    log_info "========================================"

    # 部署前检查
    pre_deploy_check

    # ... 其余部署流程 ...
}
```

**检查项扩展建议**:
1. 内存检查（至少 512MB）
2. CPU 核心数检查
3. 网络连接检查
4. 数据库连接检查
5. 环境变量检查
6. 配置文件完整性检查

**验证方法**:
```bash
# 手动运行部署前检查
cd /opt/Home-page
bash -c 'source scripts/deploy.sh && pre_deploy_check'

# 测试磁盘空间不足的情况
# 临时减少磁盘空间或调整阈值
```

---

## ✅ 已有的安全措施

以下是项目中已经实现的安全措施：

1. ✅ **代码测试**: 执行 pytest 单元测试
2. ✅ **代码检查**: 使用 flake8 和 bandit 检测安全问题
3. ✅ **分支保护**: 仅 main 分支触发部署
4. ✅ **备份机制**: 部署前创建备份
5. ✅ **健康检查**: 部署后验证应用状态
6. ✅ **自动回滚**: 部署失败时自动回滚
7. ✅ **SSH 连接超时**: 设置了 10 秒连接超时
8. ✅ **SSH 密钥清理**: 部署完成后清理临时密钥

---

## 📊 安全检查清单

### 日常检查

- [ ] 检查 GitHub Actions 日志中是否包含敏感信息
- [ ] 验证所有提交都有 GPG 签名
- [ ] 运行依赖安全扫描：`pip-audit --desc`
- [ ] 检查日志文件权限：`ls -la /var/log/Home-page/`
- [ ] 验证 SSH 密钥是否定期轮换

### 每周检查

- [ ] 审查 GitHub 仓库的访问权限
- [ ] 检查自动合并的 PR 列表
- [ ] 审查依赖更新日志
- [ ] 检查备份文件的完整性
- [ ] 审查部署日志中的异常

### 每月检查

- [ ] 审查和更新安全策略
- [ ] 进行安全审计
- [ ] 更新依赖包到最新版本
- [ ] 轮换 SSH 密钥和访问令牌
- [ ] 进行渗透测试

---

## 🔧 安全工具推荐

### 依赖安全
- **pip-audit**: 扫描 Python 依赖的已知漏洞
- **safety**: 检查已安装包的漏洞
- **pip-audit**: 依赖安全审计工具

### 代码安全
- **bandit**: Python 代码安全检查
- **semgrep**: 语义化代码分析
- **CodeQL**: GitHub 的代码分析平台

### 密钥管理
- **HashiCorp Vault**: 企业级密钥管理
- **AWS Secrets Manager**: AWS 密钥管理服务
- **GitHub Secrets**: GitHub 内置密钥管理

### 容器安全（如果使用）
- **Trivy**: 容器镜像漏洞扫描
- **Clair**: 容器静态分析
- **Docker Bench**: Docker 安全基准测试

---

## 📚 相关文档

- [CI/CD 快速开始](00-QUICK_START.md)
- [CI/CD 配置指南](02-CONFIGURATION.md)
- [故障排查指南](05-TROUBLESHOOTING.md)
- [测试指南](06-TESTING.md)

---

## 🆘 安全事件响应

如果发现安全问题，请按照以下步骤操作：

1. **立即隔离**: 停止受影响的系统
2. **评估影响**: 确定受影响的范围和严重程度
3. **修复漏洞**: 应用补丁或临时缓解措施
4. **通知相关方**: 通知团队成员和用户（如适用）
5. **事后分析**: 记录事件，分析根本原因
6. **改进措施**: 更新安全策略和流程

---

## 📧 安全报告

如果您发现任何安全问题，请通过以下方式报告：

- **GitHub Security Advisory**: https://github.com/liubin20020924-cloud/Home-page/security/advisories
- **私人问题反馈**: 创建一个私有 Issue，包含 "Security" 标签

请提供：
- 问题描述
- 复现步骤
- 潜在影响
- 建议的修复方案

---

## 🔄 更新历史

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-03-05 | 1.0 | 初始版本，包含所有安全措施 |

---

**文档版本**: 1.0
**最后更新**: 2026-03-05
**维护者**: DevOps Team
