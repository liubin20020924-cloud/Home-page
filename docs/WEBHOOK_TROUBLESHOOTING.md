# Webhook 通知问题排查指南

## 问题现象

GitHub Actions 中 notify cloud server 显示：
```
未配置 WEBHOOK_URL，跳过 webhook 通知
```

## 原因分析

### 可能的原因

1. **GitHub Secrets 未配置**
   - GitHub 仓库中没有配置 `WEBHOOK_URL` secret
   - 或配置了但变量名不正确

2. **.env 文件中缺少配置**
   - 云主机上的 `/opt/Home-page/.env` 文件中没有 `WEBHOOK_URL`

3. **webhook 服务未运行**
   - webhook-receiver 服务没有启动
   - 或启动失败

4. **webhook 接收器代码未更新**
   - 云主机上的 `webhook_receiver_github.py` 还是旧版本
   - 需要手动拉取最新代码

## 排查步骤

### 步骤 1：检查 GitHub Secrets

1. 访问 GitHub 仓库设置页面：
   ```
   https://github.com/liubin20020924-cloud/Home-page/settings/secrets/actions
   ```

2. 检查是否配置了 `WEBHOOK_URL`：
   - 在 "Secrets" 列表中查找
   - 如果没有，点击 "New repository secret" 添加

3. 配置正确的值：
   ```
   Name: WEBHOOK_URL
   Value: http://10.10.10.250:9000
   ```

### 步骤 2：检查云主机 webhook 服务

SSH 登录云主机，检查服务状态：

```bash
# 1. 检查服务状态
systemctl status webhook-receiver

# 2. 查看服务日志
journalctl -u webhook-receiver -f

# 3. 检查端口监听
netstat -tlnp | grep 9000

# 4. 查看 webhook 接收器进程
ps aux | grep webhook_receiver
```

**预期结果**：
- 服务状态应该是：`active (running)`
- 日志应该显示：`Starting GitHub webhook receiver on port 9000...`
- 端口 9000 应该在监听

### 步骤 3：检查 webhook 接收器代码版本

```bash
# SSH 登录云主机
ssh user@server

# 检查代码版本
cd /opt/Home-page
git log -1 --oneline -- scripts/webhook_receiver_github.py

# 对比本地版本
```

**如果版本不一致**：
- 云主机上的版本比 GitHub 上的旧
- 需要手动拉取最新代码：

```bash
cd /opt/Home-page
git fetch origin main
git reset --hard origin/main
```

### 步骤 4：重启 webhook 服务

```bash
# 重启服务
systemctl restart webhook-receiver

# 查看启动日志
journalctl -u webhook-receiver -f
```

### 步骤 5：测试 webhook 连接

```bash
# 在本地机器测试（云主机需要开放外部访问）
curl -X POST http://10.10.10.250:9000/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: test" \
  -d '{
    "ref": "refs/heads/main",
    "repository": "liubin20020924-cloud/Home-page",
    "commit": "test"
  }'

# 或测试健康检查
curl http://10.10.10.250:9000/webhook/health
```

### 步骤 6：查看部署日志

```bash
# 查看部署日志
tail -50 /var/log/integrate-code/deploy.log

# 查看应用日志
tail -50 /var/log/integrate-code/app.log
```

## 常见错误和解决

### 错误 1：subprocess.run() 命令未找到

**错误代码**: 6 或 127

**原因**: 部署脚本路径错误或命令不存在

**解决方法**:
```bash
# SSH 登录云主机
ssh user@server

# 检查部署脚本是否存在
ls -la /opt/Home-page/scripts/deploy.sh

# 手动测试脚本
cd /opt/Home-page
bash scripts/deploy.sh
```

### 错误 2：Git 拉取失败

**现象**: `smart-pull.sh` 拉取失败

**原因**: GitHub 或 Gitee 网络问题

**解决方法**:
```bash
# 检查 Git 远程配置
cd /opt/Home-page
git remote -v

# 如果没有 Gitee，添加
git remote add gitee https://gitee.com/liubin_studies/Home-page.git

# 强制从 GitHub 拉取
git fetch origin main
git reset --hard origin/main
```

### 错误 3：Python 环境问题

**现象**: 依赖安装失败

**解决方法**:
```bash
# 检查虚拟环境
cd /opt/Home-page

# 如果使用虚拟环境
source venv/bin/activate

# 手动安装依赖
pip install -r requirements.txt

# 验证安装
python scripts/check_dependencies.py
```

## 快速修复流程

### 方案 A：使用默认密钥（最简单）

1. **配置 GitHub Secret**:
   ```
   Name: WEBHOOK_URL
   Value: http://10.10.10.250:9000
   ```
   - 不需要配置 `WEBHOOK_SECRET`

2. **无需修改 .env**:
   - webhook 接收器会使用默认密钥
   - CI/CD workflow 使用固定签名
   - 双方会匹配

3. **重启 webhook 服务**:
   ```bash
   systemctl restart webhook-receiver
   ```

4. **测试部署**:
   ```bash
   # 创建测试提交
   git checkout main
   echo "test-webhook-$(date +%s)" >> test.txt
   git add . && git commit -m "test: 测试webhook通知"
   git push origin main
   ```

### 方案 B：生成真正密钥（更安全）

1. **在云主机生成密钥**:
   ```bash
   # SSH 登录
   ssh user@server
   
   # 生成密钥
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # 或运行脚本
   cd /opt/Home-page
   python scripts/generate-webhook-secret.py
   ```

2. **更新 .env 文件**:
   ```bash
   # SSH 登录
   ssh user@server
   
   # 编辑 .env
   nano /opt/Home-page/.env
   
   # 添加以下内容：
   # WEBHOOK_SECRET=生成的32位密钥
   ```

3. **配置 GitHub Secrets**:
   - `WEBHOOK_URL` = `http://10.10.10.250:9000`
   - `WEBHOOK_SECRET` = `<生成的密钥>`

4. **重启 webhook 服务**:
   ```bash
   systemctl restart webhook-receiver
   ```

5. **测试部署**:
   创建测试提交推送测试

## 推荐配置

### 最低配置（推荐）

使用方案 A（默认密钥），配置最简单：

1. GitHub: 只配置 `WEBHOOK_URL`
2. 云主机: 无需修改 .env
3. 优势: 配置简单，维护成本低

### 完整配置（更安全）

使用方案 B（真正密钥），增强安全性：

1. GitHub: 配置 `WEBHOOK_URL` + `WEBHOOK_SECRET`
2. 云主机: 在 .env 中配置 `WEBHOOK_SECRET`
3. 优势: 安全性更高，防止未授权访问

## 验证成功

配置后，检查 GitHub Actions 日志：

1. 访问 GitHub Actions 页面
2. 点击 "Notify Cloud Server" job
3. 查看日志输出：
   - 应该看到："通知云服务器开始部署..."
   - 应该看到："云服务器响应: ..."  
   - 不应该看到："未配置 WEBHOOK_URL"

## 联系方式

如果以上方法都无法解决问题，请提供以下信息：

1. GitHub Actions 运行 ID
2. 错误截图
3. 云主机 webhook 服务状态
4. `/var/log/integrate-code/deploy.log` 的最新日志

联系支持：
- 技术支持: support@cloud-doors.com
- 开发团队: development-team@cloud-doors.com

---

**文档版本**: v1.0
**创建时间**: 2026-03-04
