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
- ✅ 通过 SSH 通知云主机
- ✅ 云主机自动拉取代码并部署

**完成工作**：
- ✅ 创建 GitHub Actions CI/CD workflow (`.github/workflows/ci-cd.yml`)
- ✅ 创建 SSH 通知步骤
- ✅ 更新部署脚本支持 SSH 触发
- ✅ 创建智能拉取脚本 (`scripts/smart-pull.sh`)

**问题**: 未验证 GitHub Actions workflow 的实际运行

---

### 阶段 2: 配置 SSH 部署 (2026-03-04 19:30)

**目标**: 配置 SSH 作为部署方式

**需求**：
- ✅ SSH 方式更可靠，不依赖外部网络
- ✅ 使用 SSH 密钥认证，安全性高
- ✅ GitHub Actions 通过 SSH 连接云主机执行部署

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
if [[ "$BACKUP_PATH" != "$PROJECT_DIR/"* ]]; then
    rsync -av --delete "$PROJECT_DIR/" "$BACKUP_PATH/"
else
    echo "错误: 备份路径在项目目录内"
    return 1
fi
```

---

### 阶段 5: 简化 CI/CD 流程 - 移除 Webhook (2026-03-05 10:00)

**目标**: 移除 Webhook 部署方式，统一使用 SSH 部署

**原因分析**：
- Webhook 需要额外的服务和端口配置
- 增加系统复杂度和维护成本
- SSH 部署已经足够稳定可靠
- 统一部署方式简化配置

**完成工作**：
- ✅ 更新 CI/CD workflow，移除 Webhook 通知步骤
- ✅ 仅保留 SSH 部署作为唯一部署方式
- ✅ 更新部署脚本，移除 Webhook 重启逻辑
- ✅ 更新所有 CI/CD 文档，移除 Webhook 相关内容
- ✅ 创建 Webhook 清理指南文档

**技术细节**：
- 移除 GitHub Webhook 配置
- 停止并删除 webhook-receiver 服务
- 从部署脚本中移除 `restart_webhook()` 函数
- 更新 GitHub Secrets，移除 `WEBHOOK_URL` 和 `WEBHOOK_SECRET`

**效果**：
- ✅ 简化 CI/CD 流程
- ✅ 减少系统组件
- ✅ 降低维护成本
- ✅ 提高系统稳定性

---

## 问题记录

### 问题 1: SSH 权限问题

**发生时间**: 2026-03-04 20:00

**错误信息**:
```
bash: ./scripts/deploy.sh: Permission denied
```

**根本原因**:
- Git 拉取代码后，脚本文件的执行权限被重置
- GitHub Actions 运行环境中没有执行权限

**解决方案**:
在执行脚本前添加 `chmod +x` 命令

**预防措施**:
- 在每次部署前检查并设置执行权限
- 在 .gitattributes 中设置文件权限（如果 Git 支持）

---

### 问题 2: 备份路径冲突

**发生时间**: 2026-03-04 20:30

**错误信息**:
```
cp: cannot copy a directory, '/opt/Home-page', into itself
```

**根本原因**:
- 备份目录 `/opt/Home-page/backups` 在项目目录内
- rsync/cp 命令尝试将目录复制到自己的子目录

**解决方案**:
- 将备份目录移到项目外部：`/var/backups/Home-page`
- 添加路径验证逻辑

**预防措施**:
- 在部署脚本中添加路径冲突检测
- 使用绝对路径，避免相对路径问题

---

### 问题 3: GitHub Actions 超时

**发生时间**: 2026-03-05 09:30

**错误信息**:
```
Error: The operation was canceled
```

**根本原因**:
- SSH 连接超时
- 网络不稳定

**解决方案**:
- 增加 GitHub Actions 的 timeout 时间
- 添加重试逻辑
- 配置 SSH KeepAlive

**预防措施**:
- 在 GitHub Actions 中设置超时配置
- 添加连接超时检测

---

## 解决方案

### SSH 部署配置

**完整的 SSH 部署配置**：

1. **生成 SSH 密钥对**
   ```bash
   ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_key
   ```

2. **配置 GitHub Secrets**
   - `SSH_HOST`: 云主机地址
   - `SSH_USERNAME`: SSH 用户名
   - `SSH_PRIVATE_KEY`: 私钥内容

3. **配置云主机 SSH**
   ```bash
   # 添加公钥到 authorized_keys
   echo "[公钥内容]" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

4. **测试 SSH 连接**
   ```bash
   ssh -i ~/.ssh/github_actions_key root@cloud-doors.com "echo 'SSH OK'"
   ```

### 部署脚本优化

**关键优化点**：

1. **执行权限检查**
   ```bash
   chmod +x ./scripts/deploy.sh
   bash ./scripts/deploy.sh
   ```

2. **备份路径验证**
   ```bash
   BACKUP_DIR="/var/backups/Home-page"
   if [[ "$BACKUP_PATH" == "$PROJECT_DIR/"* ]]; then
       echo "错误: 备份路径在项目目录内"
       return 1
   fi
   ```

3. **错误处理**
   ```bash
   set -e  # 遇到错误立即退出
   trap 'echo "部署失败，查看日志"; tail -50 /var/log/deploy.log' ERR
   ```

---

## 经验总结

### 成功经验

1. **简单即最好**
   - Webhook + SSH 双保险看似可靠，实际增加复杂度
   - 单一 SSH 部署方式更稳定，更易维护

2. **路径规划很重要**
   - 备份目录必须在项目目录外
   - 使用绝对路径避免相对路径问题

3. **权限管理要细致**
   - Git 拉取会重置权限
   - 部署前必须检查和设置权限

4. **文档要及时更新**
   - 代码变更时同步更新文档
   - 移除不再使用的功能时要清理文档

### 避免的陷阱

1. **不要过度设计**
   - 双保险机制不如单一可靠机制
   - 过多的组件增加故障点

2. **不要忽视路径问题**
   - 相对路径容易出错
   - 使用绝对路径更安全

3. **不要假设权限正确**
   - Git 操作会改变文件权限
   - 每次部署前都要检查权限

4. **不要忽视文档**
   - 代码变更必须同步更新文档
   - 过时的文档会误导使用者

### 最佳实践

1. **配置管理**
   - 使用 GitHub Secrets 管理敏感信息
   - 不要将密钥写死在代码中

2. **错误处理**
   - 使用 `set -e` 确保错误时退出
   - 添加详细的日志记录
   - 提供清晰的错误信息

3. **测试验证**
   - 配置变更后立即测试
   - 手动验证自动化流程
   - 保留手动部署的回退方案

4. **文档维护**
   - 代码和文档同步更新
   - 提供清晰的步骤和示例
   - 记录问题和解决方案

---

## 技术栈

### 核心技术

| 组件 | 技术 | 版本 |
|------|------|------|
| 版本控制 | Git | 2.x |
| CI/CD | GitHub Actions | latest |
| 远程部署 | SSH | OpenSSH 8.x |
| 自动化脚本 | Bash | 4.x |
| Web 框架 | Flask | 3.0.3 |

### 依赖工具

| 工具 | 用途 |
|------|------|
| rsync | 增量备份和文件同步 |
| systemctl | 系统服务管理 |
| ufw | 防火墙管理 |
| journalctl | 系统日志查看 |

---

## 版本信息

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-03-04 | 初始部署规划 |
| v1.1 | 2026-03-04 | 添加 SSH 备用部署 |
| v1.2 | 2026-03-04 | 修复权限和备份问题 |
| v2.0 | 2026-03-05 | 移除 Webhook，统一使用 SSH |

---

<div align="center">

**文档版本**: v2.0
**创建日期**: 2026-03-04
**最后更新**: 2026-03-05
**维护者**: 云户科技技术团队

</div>
