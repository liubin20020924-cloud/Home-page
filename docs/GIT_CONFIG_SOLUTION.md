# 腾讯云主机Git完整配置方案

> 针对腾讯云访问GitHub速度慢的完整解决方案

---

## 🎯 推荐方案：混合架构（Gitee + GitHub）

**架构设计**：
```
本地开发
  ↓
推送到 GitHub
  ↓
  ├─ CI/CD触发（可选，通知云主机）
  │
  └─ Gitee自动镜像（可选，用于云主机快速拉取）
         ↓
      云主机从Gitee拉取（快速）
         ↓
      自动部署
```

**核心思路**：
- ✅ 代码只推送到GitHub（单源管理）
- ✅ Gitee作为镜像（加速拉取）
- ✅ GitHub CI/CD通知云主机（实时触发）
- ✅ 云主机从Gitee拉取（速度快）

---

## 📦 完整配置步骤

### 第一步：配置本地Git（本地开发环境）

#### 1.1 初始化Git配置

```bash
# 用户名和邮箱
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 使用凭证存储
git config --global credential.helper store

# 推送时使用GitHub
git config --global push.default simple
```

#### 1.2 克隆或更新本地仓库

```bash
# 如果还没有克隆
git clone https://github.com/liubin20020924-cloud/Home-page.git

# 或更新现有仓库
cd /path/to/Home-page
git pull origin main
```

---

### 第二步：配置GitHub Personal Access Token

#### 2.1 生成Token

1. 访问：https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 配置Token权限：
   - ✅ `repo` - 完整仓库访问权限
   - ✅ `workflow` - GitHub Actions权限
4. 点击 **Generate token**
5. **复制Token**（只显示一次，请妥善保存）

#### 2.2 配置本地Git凭据

```bash
cd /path/to/Home-page

# 测试拉取（会提示输入用户名和Token）
git pull

# 输入：
# Username: liubin20020924-cloud
# Password: <粘贴刚才生成的Personal Access Token>
```

配置成功后，后续操作都不需要输入密码。

---

### 第三步：配置云主机Git

#### 3.1 克隆GitHub仓库到云主机

```bash
# SSH连接到云主机
ssh root@your-server-ip

# 克隆仓库到/opt/Home-page
cd /opt
git clone https://github.com/liubin20020924-cloud/Home-page.git

# 进入项目目录
cd /opt/Home-page
```

#### 3.2 配置云主机Git凭据

```bash
# 配置Git凭据
git config --global credential.helper store

# 测试拉取（会提示输入用户名和Token）
git pull

# 输入：
# Username: liubin20020924-cloud
# Password: <粘贴云专用的Personal Access Token>
```

**建议**：为云主机生成专用的Personal Access Token，便于管理。

---

### 第四步：配置双远程仓库（GitHub + Gitee）

#### 4.1 添加Gitee作为镜像

```bash
# 在云主机上添加Gitee远程仓库
cd /opt/Home-page
git remote add gitee https://gitee.com/liubin_studies/Home-page.git

# 查看配置的远程仓库
git remote -v

# 应该看到：
# origin    https://github.com/liubin20020924-cloud/Home-page.git (fetch)
# origin    https://github.com/liubin20020924-cloud/Home-page.git (push)
# gitee     https://gitee.com/liubin_studies/Home-page.git (fetch)
# gitee     https://gitee.com/liubin_studies/Home-page.git (push)
```

#### 4.2 创建智能拉取脚本

创建 `scripts/smart-pull.sh`：

```bash
#!/bin/bash

# 智能拉取脚本 - 自动选择最快的源

set -e

PROJECT_DIR="/opt/Home-page"
LOG_FILE="/var/log/integrate-code/smart-pull.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 测试GitHub速度
test_github_speed() {
    local start_time=$(date +%s)
    curl -o /dev/null -s -w '%{time_total}' https://github.com > /dev/null 2>&1
    local end_time=$(date +%s)
    echo $((end_time - start_time))
}

# 从Gitee拉取
pull_from_gitee() {
    log "从Gitee拉取..."
    cd "$PROJECT_DIR"
    git fetch gitee main
    git reset --hard gitee/main
}

# 从GitHub拉取
pull_from_github() {
    log "从GitHub拉取..."
    cd "$PROJECT_DIR"
    git fetch origin main
    git reset --hard origin/main
}

# 主逻辑
main() {
    log "=========================================="
    log "开始智能拉取..."
    log "=========================================="

    # 测试GitHub速度（超时3秒）
    GITHUB_SPEED=$(timeout 3 curl -o /dev/null -s -w '%{speed_download}' https://github.com 2>/dev/null || echo "0")

    # 转换为KB/s
    GITHUB_SPEED_KB=$(echo "scale=2; $GITHUB_SPEED / 1024" | bc 2>/dev/null || echo "0")

    log "GitHub下载速度: ${GITHUB_SPEED_KB} KB/s"

    # 如果GitHub速度低于100KB/s，使用Gitee
    if (( $(echo "$GITHUB_SPEED_KB < 100" | bc -l 2>/dev/null || echo 0) )); then
        log "GitHub速度慢，使用Gitee拉取..."
        pull_from_gitee
    else
        log "GitHub速度正常，使用GitHub拉取..."
        pull_from_github
    fi

    # 获取当前提交
    CURRENT_COMMIT=$(git rev-parse HEAD | cut -c1-7)
    log "当前版本: $CURRENT_COMMIT"

    log "=========================================="
    log "拉取完成"
    log "=========================================="
}

# 执行
main
```

设置权限：
```bash
chmod +x /opt/Home-page/scripts/smart-pull.sh
```

---

### 第五步：更新部署脚本使用智能拉取

#### 5.1 修改deploy.sh中的拉取逻辑

```bash
# 编辑部署脚本
nano /opt/Home-page/scripts/deploy.sh
```

找到拉取代码的部分，替换为智能拉取：

```bash
# 原来是：
# git fetch origin main
# git reset --hard origin/main

# 改为：
# 使用智能拉取
bash /opt/Home-page/scripts/smart-pull.sh
```

#### 5.2 修改check_and_deploy_github.sh

```bash
# 编辑自动检测脚本
nano /opt/Home-page/scripts/check_and_deploy_github.sh
```

在 `check_updates()` 函数中：

```bash
check_updates() {
    cd "$PROJECT_DIR" || exit 1

    # 使用智能拉取检测更新
    bash "$PROJECT_DIR/scripts/smart-pull.sh" > /dev/null 2>&1

    # 比较提交
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/main)

    if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
        log_info "检测到新版本"
        log_info "本地: ${LOCAL_COMMIT:0:7}"
        log_info "远程: ${REMOTE_COMMIT:0:7}"
        return 0  # 有更新
    else
        log_info "已是最新版本"
        return 1  # 无更新
    fi
}
```

---

### 第六步：配置GitHub Webhook（可选，实时触发）

#### 6.1 在云主机配置Webhook密钥

```bash
# 生成Webhook密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

复制生成的密钥。

#### 6.2 配置Webhook接收器

```bash
# 编辑GitHub版Webhook接收器
nano /opt/Home-page/scripts/webhook_receiver_github.py
# 替换 WEBHOOK_SECRET 占位符

# 编辑自动检测脚本
nano /opt/Home-page/scripts/check_and_deploy_github.sh
# 替换 WEBHOOK_SECRET 占位符
```

#### 6.3 在GitHub配置Webhook

访问：https://github.com/liubin20020924-cloud/Home-page/settings/hooks

添加Webhook：

- **Payload URL**: `http://your-server-ip:9000/webhook/github`
- **Content type**: `application/json`
- **Secret**: 填写Webhook密钥
- **Events**: **Just the push event**
- **Active**: ✅ 勾选

#### 6.4 配置GitHub Secrets（用于Actions通知）

访问：https://github.com/liubin20020924-cloud/Home-page/settings/secrets/actions

添加：

**WEBHOOK_URL**:
```
http://your-server-ip:9000
```

**WEBHOOK_SECRET**:
```
生成的Webhook密钥
```

---

### 第七步：优化Git配置（提高速度）

#### 7.1 增加缓冲区大小

```bash
# 在云主机上配置
git config --global http.postBuffer 524288000  # 500MB缓冲区
git config --global http.maxRequestBuffer 100M
git config --global core.compression 9  # 启用最大压缩
```

#### 7.2 使用浅克隆（首次部署）

```bash
# 删除现有仓库
cd /opt
rm -rf Home-page

# 使用浅克隆（只拉取最近10次提交）
git clone --depth 10 https://github.com/liubin20020924-cloud/Home-page.git

# 进入项目后拉取完整历史
cd /opt/Home-page
git fetch --unshallow
```

---

## 🔧 使用流程

### 日常开发流程（本地）

```bash
# 1. 创建功能分支
git checkout -b feat/your-feature

# 2. 编写代码并提交
git add .
git commit -m "feat(home: 添加新功能"

# 3. 推送到GitHub（单源管理）
git push origin feat/your-feature

# 4. 在GitHub创建PR并合并到main
```

### 自动部署流程（云主机）

#### 方式A：定时检测（默认）
```
每5分钟
  ↓
智能拉取（自动选择最快源）
  ↓
发现更新 → 自动部署
```

#### 方式B：Webhook触发（实时）
```
代码推送到GitHub
  ↓
GitHub Webhook通知云主机
  ↓
智能拉取（自动选择最快源）
  ↓
立即部署
```

---

## 📊 方案优势

| 特性 | 说明 |
|------|------|
| **单源管理** | 代码只推送到GitHub，管理简单 |
| **速度优化** | 自动选择最快源（Gitee或GitHub） |
| **高可用性** | GitHub或Gitee任一可用即可部署 |
| **实时部署** | Webhook触发，几秒内开始部署 |
| **故障恢复** | 一源故障自动切换到另一源 |

---

## 🚀 快速配置命令

### 一键配置脚本

在云主机上执行：

```bash
#!/bin/bash

# 腾讯云主机Git一键配置脚本

set -e

echo "=========================================="
echo "开始配置Git..."
echo "=========================================="

# 1. 配置Git
git config --global http.postBuffer 524288000
git config --global core.compression 9
git config --global credential.helper store
echo "✓ Git配置完成"

# 2. 添加Gitee远程仓库
cd /opt/Home-page
if ! git remote | grep -q gitee; then
    git remote add gitee https://gitee.com/liubin_studies/Home-page.git
    echo "✓ Gitee远程仓库已添加"
else
    echo "✓ Gitee远程仓库已存在"
fi

# 3. 配置智能拉取脚本
chmod +x /opt/Home-page/scripts/smart-pull.sh
echo "✓ 智能拉取脚本已配置"

# 4. 测试拉取速度
echo ""
echo "测试拉取速度..."
bash /opt/Home-page/scripts/smart-pull.sh

echo ""
echo "=========================================="
echo "配置完成！"
echo "=========================================="
```

保存为 `/opt/Home-page/scripts/one-time-setup.sh` 并执行：

```bash
chmod +x /opt/Home-page/scripts/one-time-setup.sh
bash /opt/Home-page/scripts/one-time-setup.sh
```

---

## 📝 配置检查清单

完成配置后，确认：

### 本地配置
- [ ] 本地Git用户名和邮箱已配置
- [ ] Personal Access Token已生成
- [ ] 本地Git凭据已配置（git pull无需密码）

### 云主机配置
- [ ] GitHub仓库已克隆到 `/opt/Home-page`
- [ ] 云主机Git凭据已配置
- [ ] Gitee远程仓库已添加（`git remote -v` 可看到）
- [ ] 智能拉取脚本已创建并可执行
- [ ] Git配置已优化（缓冲区、压缩）

### 自动部署配置
- [ ] Webhook密钥已生成
- [ ] Webhook接收器配置已更新
- [ ] Webhook服务正在运行（`systemctl status webhook-receiver`）
- [ ] 定时任务已配置（`crontab -l` 可看到）

### 验证测试
- [ ] 智能拉取脚本运行成功
- [ ] 推送代码后自动检测到更新
- [ ] 自动部署成功，应用正常运行

---

## 🔍 故障排查

### 智能拉取总是从Gitee拉取

**原因**: GitHub速度测试失败

**解决**:
```bash
# 手动测试GitHub连接
curl -v https://github.com

# 检查DNS解析
nslookup github.com

# 如果GitHub不可访问，会自动使用Gitee
```

### Gitee拉取失败

**原因**: Gitee未同步最新代码

**解决**:
```bash
# 手动从GitHub拉取
git fetch origin main
git reset --hard origin/main

# 推送到Gitee
git push gitee main
```

### Webhook未触发

**原因**: Webhook密钥不匹配或防火墙阻止

**解决**:
```bash
# 检查服务状态
systemctl status webhook-receiver

# 查看日志
tail -f /var/log/integrate-code/webhook.log

# 检查防火墙
firewall-cmd --list-ports
```

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [快速配置指南](QUICK_SETUP_GUIDE.md) | 简化版配置指南 |
| [简化版CI/CD配置](SIMPLIFIED_CI_CD.md) | 方案对比和选择 |
| [版本管理规范](VERSION_MANAGEMENT_GUIDE.md) | Git提交规范 |

---

**配置完成，享受高速自动部署！** 🚀
