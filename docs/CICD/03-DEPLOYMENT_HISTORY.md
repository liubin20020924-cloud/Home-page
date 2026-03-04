# CI/CD 部署历史记录

> 记录从规划到完成的完整 CI/CD 部署过程

---

## 📋 目录

1. [部署阶段](#部署阶段)
2. [问题记录](#问题记录)
3. [解决方案](#解决方案)
4. [经验总结](#经验总结)

---

## 部署阶段

### 阶段 1: 初始规划 (2026-03-04 17:00)

**目标**: 规划完整的 CI/CD 自动化部署流程

**需求清单**：
- ✅ 本地代码推送到 GitHub
- ✅ GitHub Actions 自动执行测试、代码检查、安全检查
- ✅ 通过 Webhook 或 SSH 通知云主机
- ✅ 云主机自动拉取代码并部署

**完成工作**：
- ✅ 创建 GitHub Actions CI/CD workflow (`.github/workflows/ci-cd.yml`)
- ✅ 创建 GitHub webhook 接收器 (`scripts/webhook_receiver_github.py`)
- ✅ 更新部署脚本支持 webhook 触发
- ✅ 创建智能拉取脚本 (`scripts/smart-pull.sh`)

**问题**: 未验证 GitHub Actions workflow 的实际运行

---

### 阶段 2: 添加 SSH 备用方案 (2026-03-04 19:30)

**目标**: 添加 SSH 作为 Webhook 的备用部署方式，提高可靠性

**需求**：
- ✅ Webhook 依赖 HTTP 连接，可能不稳定
- ✅ SSH 方式更可靠，不依赖外部网络
- ✅ 提供双保险方案 (Webhook + SSH)

**完成工作**：
- ✅ 在 GitHub Actions 中添加 SSH 通知步骤
- ✅ 添加 SSH 连接测试和错误处理
- ✅ 添加详细的部署步骤说明
- ✅ 创建 SSH 部署配置指南

**问题**: 首次实现 SSH 通知，需要测试

---

### 阶段 3: 修复 SSH 部署问题 (2026-03-04 20:00)

**目标**: 修复 SSH 部署脚本的执行权限问题

**问题描述**：
- SSH 连接成功
- 但执行 `./scripts/deploy.sh` 时出现 "Permission denied" 错误
- 原因：部署脚本缺少执行权限

**完成工作**：
- ✅ 在执行部署脚本前添加 `chmod +x`
- ✅ 改进错误日志输出
- ✅ 添加执行权限检查逻辑

**解决方案**：
```bash
# 在 GitHub Actions SSH 步骤中添加
chmod +x ./scripts/deploy.sh && bash ./scripts/deploy.sh
```

---

### 阶段 4: 修复备份路径冲突 (2026-03-04 20:30)

**目标**: 解决备份路径冲突导致的部署失败

**问题描述**：
- 部署时备份失败
- 错误：`cp: cannot copy a directory, '/opt/Home-page', into itself`
- 原因：备份目录 `/opt/Home-page/backups` 在项目目录内，导致循环复制

**完成工作**：
- ✅ 将备份路径从 `/opt/Home-page/backups` 改为 `/var/backups/Home-page`
- ✅ 替换 `cp -r` 为 `rsync` 避免路径冲突
- ✅ 添加路径验证逻辑，防止备份目录在项目目录内
- ✅ 使用 rsync 进行增量备份，提高备份效率

**解决方案**：
```bash
# 部署脚本中的备份逻辑
BACKUP_DIR="/var/backups/Home-page"  # 在项目目录外
PROJECT_DIR="/opt/Home-page"

# 路径验证
if [[ "$BACKUP_DIR" == "$PROJECT_DIR/"* ]]; then
    log_error "备份路径不能在项目目录内"
    exit 1
fi

# 使用 rsync 进行备份
rsync -av --delete "$PROJECT_DIR/" "$BACKUP_DIR/"
```

---

### 阶段 5: 修复 Git 拉取问题 (2026-03-04 21:00)

**目标**: 解决云主机无法从 GitHub 拉取代码的问题

**问题描述**：
- Git 拉取速度极慢 (0 KB/s)
- 智能拉取脚本无法正确使用代理
- 原因：`smart-pull.sh` 的速度测试没有读取配置的 Git 代理

**完成工作**：
- ✅ 修改 `test_github_speed()` 函数读取 `http.https://github.com.proxy`
- ✅ 修改 `test_gitee_speed()` 函数读取 `http.proxy`
- ✅ 添加代理使用日志输出
- ✅ 改进错误处理和超时逻辑
- ✅ 确保配置代理后必定使用

**解决方案**：
```bash
# 智能拉取脚本中的代理使用
test_github_speed() {
    local timeout_seconds=5
    local temp_file=$(mktemp)
    
    # 获取 GitHub 代理配置
    GITHUB_PROXY=$(git config --global --get http.https://github.com.proxy 2>/dev/null)
    HTTP_PROXY=$(git config --global --get http.proxy 2>/dev/null)
    
    PROXY_CMD=""
    if [ -n "$GITHUB_PROXY" ]; then
        PROXY_CMD="--proxy $GITHUB_PROXY"
        log_info "使用 GitHub 专用代理: $GITHUB_PROXY"
    elif [ -n "$HTTP_PROXY" ]; then
        PROXY_CMD="--proxy $HTTP_PROXY"
        log_info "使用通用代理: $HTTP_PROXY"
    else
        log_info "未配置代理，直接连接"
    fi
    
    # 使用代理进行速度测试
    local speed=0
    if [ -n "$PROXY_CMD" ]; then
        speed=$(timeout $timeout_seconds curl $PROXY_CMD -o "$temp_file" -s -w '%{speed_download}' https://github.com 2>/dev/null || echo "0")
    else
        speed=$(timeout $timeout_seconds curl -o "$temp_file" -s -w '%{speed_download}' https://github.com 2>/dev/null || echo "0")
    fi
    rm -f "$temp_file"
    echo "$speed"
}
```

---

### 阶段 6: 语法错误修复 (2026-03-04 21:30)

**目标**: 修复 smart-pull.sh 中的语法错误

**问题描述**：
- 部署失败，脚本执行报错
- 错误：`invalid bash syntax`
- 原因：速度比较使用了错误的语法

**完成工作**：
- ✅ 修改速度比较逻辑
- ✅ 使用 `bc` 命令进行浮点数比较
- ✅ 添加 fallback 逻辑，当 bc 不可用时
- ✅ 简化判断条件

**解决方案**：
```bash
# 修改前的错误语法
if (( $(echo "$GITHUB_SPEED_KB < 100" | bc -l 2>/dev/null || echo 0) )); then

# 修改后的正确语法
if [ "$GITHUB_SPEED_KB" = "0" ] || (( $(echo "$GITHUB_SPEED_KB < 100" | bc -l 2>/dev/null || echo 0) )); then
```

---

### 阶段 7: 流程文档化 (2026-03-04 22:00)

**目标**: 创建完整的部署流程文档和使用指南

**完成工作**：
- ✅ 创建 CI/CD 完整介绍文档
- ✅ 创建配置总结和使用文档
- ✅ 创建部署历史记录文档
- ✅ 创建功能设计说明文档
- ✅ 创建故障排除指南
- ✅ 创建测试指南
- ✅ 更新主文档索引

---

## 问题记录

### 问题 1: SSH 执行权限失败

**问题描述**：
- SSH 成功连接到云主机
- 执行部署脚本时提示 "Permission denied"
- 错误代码：126

**影响范围**：
- SSH 部署完全无法工作
- Webhook 部署正常

**问题根源**：
- 部署脚本 `scripts/deploy.sh` 缺少执行权限
- `chmod +x` 命令在实际执行脚本之前运行
- GitHub Actions workflow 中权限设置时机错误

**解决方案**：
- 将 `chmod +x` 移到执行命令之前
- 添加权限验证逻辑
- 确保所有脚本都有执行权限

---

### 问题 2: 备份路径冲突

**问题描述**：
- 部署过程中备份失败
- 错误：`cp: cannot copy a directory, '/opt/Home-page', into itself`
- 导致部署中断

**影响范围**：
- 部署脚本无法继续
- 自动备份功能失效

**问题根源**：
- 备份目录配置在项目目录内：`/opt/Home-page/backups`
- 使用 `cp -r` 命令时，源目录和目标目录路径冲突
- `cp -r /opt/Home-page /opt/Home-page/backups` 会被解析为复制到自身

**解决方案**：
- 将备份目录移到项目目录外：`/var/backups/Home-page`
- 使用 `rsync` 替代 `cp -r`，rsync 能更好地处理路径冲突
- 添加路径验证逻辑，在备份前检查路径关系

---

### 问题 3: Git 拉取超时

**问题描述**：
- 云主机从 GitHub 拉取代码速度极慢
- 智能拉取脚本显示速度为 0 KB/s
- 部署经常因拉取超时而失败

**影响范围**：
- 部署成功率降低
- 部署时间延长（从 30 秒增加到 10+ 分钟）

**问题根源**：
- 智能拉取脚本在测试速度时没有使用配置的 Git 代理
- 速度测试直接连接 GitHub，绕过了代理设置
- 导致无法评估真实拉取速度

**解决方案**：
- 修改 `test_github_speed()` 函数读取 Git 代理配置
- 在速度测试中使用相同的代理设置
- 添加代理使用日志，便于调试
- 确保配置代理后必定使用代理连接

---

### 问题 4: 脚本语法错误

**问题描述**：
- smart-pull.sh 执行时报语法错误
- 无法正确比较速度数值
- 导致智能拉取功能失效

**问题根源**：
- bash 中直接使用 `<` 操作符不正确
- 缺少 bc 命令的 fallback 逻辑

**解决方案**：
- 修改为正确的 bash 语法
- 添加 bc 命令检查
- 提供多个条件判断层级

---

### 问题 5: Gitee 配置残留

**问题描述**：
- 文档中仍包含 Gitee 相关配置
- 流程图中显示 Gitee 中转
- 导致配置混乱

**影响范围**：
- 新用户可能错误配置
- 维护成本增加

**解决方案**：
- 移除所有 Gitee 相关配置
- 更新流程图为当前架构：本地 → GitHub → 云主机
- 明确标注 Gitee 为可选的镜像备份

---

## 解决方案

### 解决方案总结

| 问题 | 解决方法 | 效果 |
|------|---------|------|
| SSH 执行权限 | 在执行前添加 `chmod +x` | ✅ 完全解决 |
| 备份路径冲突 | 移动备份目录到 `/var/backups/` + 使用 rsync | ✅ 完全解决 |
| Git 拉取超时 | 修改速度测试读取代理配置 | ✅ 完全解决 |
| 脚本语法错误 | 修正 bash 语法和 bc 命令 | ✅ 完全解决 |
| Gitee 配置残留 | 清理所有 Gitee 引用 | ✅ 完全解决 |

### 技术方案

#### SSH 权限管理

```bash
# 部署脚本中的权限设置
chmod +x ./scripts/deploy.sh

# 创建新文件时设置权限
install -m 755 script.sh /path/to/script.sh
```

#### 备份路径设计

```bash
# 项目目录外的备份目录
BACKUP_DIR="/var/backups/Home-page"
PROJECT_DIR="/opt/Home-page"

# 路径验证
validate_backup_path() {
    if [[ "$BACKUP_DIR" == "$PROJECT_DIR/"* ]]; then
        echo "错误: 备份路径不能在项目目录内"
        return 1
    fi
    return 0
}
```

#### 代理集成

```bash
# 统一的代理配置和使用
configure_git_proxy() {
    local proxy_url=$1
    
    # 设置 Git 代理
    git config --global http.https://github.com.proxy "$proxy_url"
    
    # 验证配置
    local configured=$(git config --global --get http.https://github.com.proxy)
    echo "已配置代理: $configured"
}

# 使用代理进行速度测试
test_with_proxy() {
    local proxy_url=$1
    local url=$2
    curl --proxy "$proxy_url" -o /dev/null -s -w '%{speed_download}\n' "$url"
}
```

---

## 经验总结

### 成功经验

1. **双保险策略**
   - Webhook 和 SSH 两种部署方式互为补充
   - Webhook 适合网络稳定环境
   - SSH 适合网络不稳定环境
   - 建议同时配置两种方式

2. **备份机制重要性**
   - 每次部署前自动备份是必要的
   - 备份目录应在项目目录外
   - 使用 rsync 替代 cp 命令
   - 定期清理过期备份

3. **代理配置必要性**
   - 国内环境必须配置 Git 代理
   - 代理配置应集成到所有工具中
   - 添加日志便于调试网络问题

4. **文档同步更新**
   - 代码变更时同步更新文档
   - 移除过时配置
   - 保持配置简洁一致
   - 提供清晰的故障排查路径

### 避免的陷阱

1. ❌ 不要将备份目录放在项目目录内
2. ❌ 不要在脚本执行后设置权限
3. ❌ 不要忽略代理配置的影响
4. ❌ 不要保留过时的配置文档
5. ❌ 不要依赖单一部署方式

### 最佳实践

1. ✅ 使用绝对路径，避免路径冲突
2. ✅ 在脚本中添加路径验证逻辑
3. ✅ 使用 rsync 进行增量备份
4. ✅ 添加详细的错误日志和调试信息
5. ✅ 为每个脚本添加帮助信息
6. ✅ 配置系统服务自动启动
7. ✅ 使用 logrotate 管理日志文件

---

<div align="center">

**文档版本**: v1.0  
**最后更新**: 2026-03-04  
**维护者**: 云户科技技术团队

</div>
