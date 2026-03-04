# 简化版CI/CD配置指南

> 云主机直接从GitHub拉取代码，无需Gitee中转

---

## 🎯 两种方案对比

### 方案一：GitHub → Gitee → 云主机（当前方案）
```
本地 → GitHub → GitHub Actions → Gitee → 云主机
```

**优点**:
- 国内访问Gitee更快
- GitHub连接失败时有备选方案

**缺点**:
- 配置复杂（需要SSH密钥、Gitee仓库、双重同步）
- 延迟更高（GitHub→Gitee→云主机）
- 维护成本高（三个平台都要管理）

### 方案二：GitHub → 云主机直接拉取（简化方案）⭐ 推荐
```
本地 → GitHub → 云主机直接拉取
```

**优点**:
- ✅ 配置简单（只需GitHub）
- ✅ 延迟更低（直接拉取）
- ✅ 维护成本低（只需管理GitHub）
- ✅ 无需SSH密钥配置
- ✅ 无需Gitee仓库

**缺点**:
- 国内访问GitHub可能稍慢（可通过CDN/代理解决）

---

## 🚀 简化方案配置

### 步骤1: 配置GitHub仓库权限

#### 使用GitHub Personal Access Token (PAT)

1. 生成Personal Access Token

访问：https://github.com/settings/tokens

2. 点击 **Generate new token (classic)**

3. 配置Token权限（选择最少权限原则）：
   - ✅ `repo` - 完整仓库访问权限
   - ✅ `workflow` - GitHub Actions权限

4. 复制生成的Token（只显示一次，请妥善保存）

---

### 步骤2: 云主机配置

#### 2.1 克隆GitHub仓库

```bash
# 克隆仓库（使用HTTPS）
cd /opt
git clone https://github.com/liubin20020924-cloud/Home-page.git

# 进入项目目录
cd /opt/Home-page
```

#### 2.2 配置Git凭据

**方式A: 使用Personal Access Token（推荐）**

```bash
# 配置Git凭据（使用Token代替密码）
git config --global credential.helper store
git pull

# 输入用户名和Token
Username: liubin20020924-cloud
Password: <粘贴您的GitHub Personal Access Token>
```

**方式B: 使用SSH密钥**

如果您更喜欢SSH方式：

```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy -N ""

# 查看公钥
cat ~/.ssh/github_deploy.pub
```

1. 访问：https://github.com/liubin20020924-cloud/Home-page/settings/keys
2. 点击 **Add deploy key**
3. 粘贴公钥
4. 勾选 **Allow write access**
5. 点击 **Add deploy key**

然后重新克隆：
```bash
git clone git@github.com:liubin20020924-cloud/Home-page.git
```

---

### 步骤3: 更新检测脚本

修改 `scripts/check_and_deploy.sh`，改为从GitHub拉取：

```bash
# 编辑检测脚本
nano /opt/Home-page/scripts/check_and_deploy.sh
```

**修改远程仓库地址**：

```bash
# 原来是Gitee：
# git remote add origin https://gitee.com/liubin_studies/Home-page.git

# 改为GitHub：
git remote add origin https://github.com/liubin20020924-cloud/Home-page.git
```

或者直接使用已克隆的GitHub仓库，无需修改。

---

### 步骤4: 配置GitHub Webhook（可选）

如果想要代码推送到GitHub后立即触发部署：

#### 4.1 修改Webhook接收器

```bash
# 编辑webhook接收器
nano /opt/Home-page/scripts/webhook_receiver.py
```

修改验证逻辑，改为GitHub Webhook验证：

```python
# GitHub Webhook密钥
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-webhook-secret-here')

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """接收 GitHub Webhook"""
    # 验证签名（GitHub使用HMAC签名）
    signature = request.headers.get('X-Hub-Signature-256')
    if signature:
        import hmac
        import hashlib

        payload = request.data
        expected_signature = 'sha256=' + hmac.new(
            WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 401

    payload = request.json
    branch = payload.get('ref', '').replace('refs/heads/', '')

    logger.info(f"Received webhook event: branch={branch}")

    if branch == 'main':
        logger.info("Triggering deployment for branch: main")
        # 触发部署
        result = subprocess.run([DEPLOY_SCRIPT], shell=True)
        return jsonify({'message': 'Deployment started'}), 200

    return jsonify({'message': 'Ignored'}), 200
```

#### 4.2 在GitHub配置Webhook

1. 访问：https://github.com/liubin20020924-cloud/Home-page/settings/hooks
2. 点击 **Add webhook**
3. 配置：
   - **Payload URL**: `http://your-server-ip:9000/webhook/github`
   - **Content type**: `application/json`
   - **Secret**: 填写WEBHOOK_SECRET的值
   - **Events**: 选择 `Just the push event`
4. 点击 **Add webhook**

---

### 步骤5: 测试部署

#### 5.1 手动测试

```bash
# 在云主机上手动运行部署脚本
bash /opt/Home-page/scripts/deploy.sh
```

#### 5.2 自动测试

```bash
# 推送代码到GitHub
git push origin main

# 等待1-5分钟（定时检查）或立即触发（如果配置了Webhook）
```

---

## 📊 简化方案完整流程

### 方式A: 定时检测（最简单）

```
本地开发
  ↓
git push origin main
  ↓
GitHub仓库更新
  ↓
云主机每5分钟检测一次
  ↓
发现更新 → 自动拉取 → 自动部署
```

### 方式B: Webhook触发（实时）

```
本地开发
  ↓
git push origin main
  ↓
GitHub Webhook触发
  ↓
云主机立即接收通知
  ↓
立即拉取 → 立即部署
```

---

## 🔧 简化后的配置文件

### 1. 检测脚本 (`check_and_deploy.sh`)

```bash
#!/bin/bash

# 云主机自动检测并部署脚本 - GitHub版

PROJECT_DIR="/opt/Home-page"
LOG_FILE="/var/log/integrate-code/auto-deploy.log"

# 配置（无需额外配置，直接使用已克隆的GitHub仓库）

# 检查更新
check_updates() {
    cd "$PROJECT_DIR" || exit 1

    LOCAL_COMMIT=$(git rev-parse HEAD)
    git fetch origin main 2>&1 || {
        log_error "无法获取远程更新"
        return 1
    }

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

# ... 其他部分保持不变
```

### 2. Webhook接收器 (`webhook_receiver.py`)

```python
"""GitHub Webhook 接收器"""
from flask import Flask, request, jsonify
import subprocess
import logging
import os
import hmac
import hashlib

app = Flask(__name__)

# GitHub Webhook 密钥
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-webhook-secret-here')

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """接收 GitHub Webhook"""
    signature = request.headers.get('X-Hub-Signature-256')

    if signature:
        payload = request.data
        expected_signature = 'sha256=' + hmac.new(
            WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 401

    payload = request.json
    branch = payload.get('ref', '').replace('refs/heads/', '')

    logger.info(f"Received GitHub webhook: branch={branch}")

    if branch == 'main':
        logger.info("Triggering deployment...")
        # 触发部署
        subprocess.run([DEPLOY_SCRIPT], shell=True)
        return jsonify({'message': 'Deployment started'}), 200

    return jsonify({'message': 'Ignored'}), 200
```

---

## ✅ 简化方案优势总结

| 对比项 | GitHub→Gitee→云主机 | GitHub→云主机直接 |
|--------|-------------------|-----------------|
| **配置复杂度** | 高（3个平台） | 低（1个平台） |
| **SSH密钥** | 需要 | 可选 |
| **维护成本** | 高 | 低 |
| **部署延迟** | 5-10分钟 | 实时或5分钟 |
| **访问速度** | Gitee快 | GitHub稍慢 |
| **故障点** | 多（GitHub/Gitee/云主机） | 少（GitHub/云主机） |

---

## 🎉 推荐方案

**对于您的项目，推荐使用简化方案：GitHub → 云主机直接拉取**

理由：
1. ✅ 您的GitHub仓库已有，无需额外配置Gitee
2. ✅ 配置简单，易于维护
3. ✅ 部署延迟更低
4. ✅ 国内访问GitHub的速度通过CDN/代理可优化

---

## 📚 相关文档

- [完整配置指南](REPO_CONFIG_GUIDE.md)
- [自动部署配置](AUTO_DEPLOY_SETUP.md)
- [故障排查指南](TROUBLESHOOTING_SYNC.md)

---

**选择简化方案，让CI/CD更简单！** 🚀
