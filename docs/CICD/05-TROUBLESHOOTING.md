# CI/CD 故障排除指南

> CI/CD 系统常见问题和解决方案

---

## 📋 目录

1. [快速诊断](#快速诊断)
2. [GitHub Actions 问题](#github-actions-问题)
3. [Webhook 问题](#webhook-问题)
4. [部署问题](#部署问题)
5. [服务问题](#服务问题)
6. [网络问题](#网络问题)
7. [性能问题](#性能问题)

---

## 快速诊断

### 诊断流程图

```
┌─────────────────┐
│   问题发生   │
└─────────┬─────┘
          ↓
    ┌─────────────────────┐
    │  确定问题类型   │
    └─────────┬─────────┘
              ↓
    ┌──────────────────────────┬──────────────────────────┐
    │                      │                      │
    ↓                      ↓                      ↓
┌────────┐         ┌────────┐        ┌────────┐      ┌────────┐
│GitHub  │         │Webhook │        │ 部署   │      │ 服务   │
│Actions │         │        │        │        │      │        │
└────────┘         └────────┘        └────────┘      └────────┘
     ↓                  ↓                  ↓              ↓
┌────────┐         ┌────────┐        ┌────────┐      ┌────────┐
│ 查对应 │         │ 查对应 │        │ 查对应 │      │ 查对应 │
│ 章节   │         │ 章节   │        │ 章节   │      │ 章节   │
└────────┘         └────────┘        └────────┘      └────────┘
```

### 健康检查命令

```bash
# 1. GitHub Actions 状态
# 访问: https://github.com/liubin20020924-cloud/Home-page/actions

# 2. Webhook 健康检查
curl http://cloud-doors.com:9000/webhook/health

# 3. 应用服务状态
sudo systemctl status Home-page

# 4. 应用健康检查
curl http://cloud-doors.com:5000/health

# 5. 查看部署日志
tail -50 /var/log/Home-page/deploy.log

# 6. 查看 Webhook 日志
sudo journalctl -u webhook-receiver -n 50
```

### 状态检查清单

- [ ] GitHub Actions 能正常运行
- [ ] Webhook 服务健康
- [ ] 应用服务运行中
- [ ] 网络连接正常
- [ ] 磁盘空间充足 (> 5GB)
- [ ] 内存使用正常 (< 80%)

---

## GitHub Actions 问题

### 问题 1: Actions 失败

**症状：**
- Actions 显示为失败状态
- 没有执行日志
- 错误信息不明确

**诊断步骤：**

1. 查看 Actions 日志
   ```
   GitHub 仓库 → Actions → 选择失败的 workflow → 查看日志
   ```

2. 常见错误类型：
   ```yaml
   Error: Resource not accessible by integration
   # → Secrets 配置错误

   Error: Workflow run failed
   # → 代码或脚本错误

   Error: Timeout
   # → 执行超时
   ```

**解决方案：**

| 错误类型 | 解决方案 |
|---------|----------|
| Secrets 未配置 | 检查所有必需的 Secret 是否已添加 |
| 代码语法错误 | 本地运行 `python -m py_compile app.py` 修复 |
| 测试失败 | 本地运行 `pytest tests/` 修复测试 |
| 权限错误 | 检查 GitHub Token 权限，重新生成 |

### 问题 2: Secrets 配置错误

**症状：**
- 错误：`Resource not accessible by integration`
- Secrets 读取失败

**诊断步骤：**

```bash
# 1. 检查 Secrets 是否存在
gh secret list

# 2. 检查 workflow 中是否引用
cat .github/workflows/ci-cd.yml | grep secrets.

# 3. 验证 Secret 名称拼写
```

**解决方案：**

1. **添加缺失的 Secrets**
   - 进入：Settings → Secrets and variables → Actions
   - 点击：New repository secret
   - 填写正确的名称和值
   - 点击：Add secret

2. **检查名称拼写**
   - 大小写敏感
   - 不允许空格
   - 必须与 workflow 中一致

### 问题 3: Actions 超时

**症状：**
- Workflow 运行超过时间限制
- 错误：`Timeout after 360 minutes`

**解决方案：**

| 优化项 | 方法 |
|---------|------|
| 分割任务 | 将长时间任务拆分为多个 job |
| 优化测试 | 使用并行测试，减少总耗时 |
| 增加超时 | 在 workflow 中设置 `timeout-minutes` |
| 优化脚本 | 减少不必要的依赖安装 |

---

## Webhook 问题

### 问题 1: Webhook 不触发

**症状：**
- Push 代码到 main 分支后，云主机无反应
- Webhook 交付日志显示失败
- 部署没有自动开始

**诊断步骤：**

```bash
# 1. 检查 GitHub Webhook 配置
# GitHub 仓库 → Settings → Webhooks → 查看交付历史

# 2. 检查 Webhook 响应
curl -v -X POST http://cloud-doors.com:9000/webhook/github \
  -H "Content-Type: application/json" \
  -d '{"ref":"refs/heads/main","sha":"test"}'

# 3. 检查云主机服务状态
sudo systemctl status webhook-receiver
```

**解决方案：**

| 可能原因 | 解决方案 |
|---------|----------|
| Webhook URL 错误 | 检查 URL 是否为 `http://cloud-doors.com:9000/webhook/github` |
| Secret 不匹配 | GitHub 和云主机的 Secret 必须完全一致 |
| 防火墙阻挡 | 检查 9000 端口是否开放 |
| 服务未启动 | 运行 `sudo systemctl start webhook-receiver` |
| 网络不通 | 检查云主机网络连接 |

### 问题 2: 签名验证失败

**症状：**
- Webhook 日志显示：`Invalid signature`
- 返回 401 错误

**诊断步骤：**

```bash
# 1. 检查 Secret 配置
grep WEBHOOK_SECRET /opt/Home-page/.env

# 2. 重新测试 Webhook
curl -X POST http://cloud-doors.com:9000/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=<测试签名>" \
  -d '{"ref":"refs/heads/main"}'

# 3. 查看日志
sudo journalctl -u webhook-receiver -f
```

**解决方案：**

1. **同步 Secret**
   - 确保配置文件中的 Secret 与 GitHub 一致
   - 重启 webhook 服务：`sudo systemctl restart webhook-receiver`

2. **重新生成 Secret**
   ```bash
   # 生成新密钥
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # 更新 GitHub Secret
   gh secret set WEBHOOK_SECRET <新密钥>
   
   # 更新云主机配置
   nano /opt/Home-page/.env
   ```

### 问题 3: Webhook 服务崩溃

**症状：**
- Webhook 服务频繁重启
- 无法访问健康检查端点
- 日志中有未捕获的异常

**诊断步骤：**

```bash
# 1. 查看服务状态
sudo systemctl status webhook-receiver

# 2. 查看崩溃日志
sudo journalctl -u webhook-receiver --since "1 hour ago" -p err

# 3. 查看资源使用
top -p webhook-receiver
```

**解决方案：**

| 问题类型 | 解决方案 |
|---------|----------|
| 内存泄漏 | 重启服务，监控内存使用 |
| 未捕获异常 | 查看 Python 错误日志，添加 try-except |
| 端口冲突 | 检查 9000 端口是否被占用 |
| 配置错误 | 验证 `.env` 文件格式 |

---

## 部署问题

### 问题 1: 部署脚本失败

**症状：**
- 部署日志显示错误
- 脚本中途退出
- 服务未更新

**诊断步骤：**

```bash
# 1. 查看完整部署日志
tail -100 /var/log/Home-page/deploy.log

# 2. 查找错误关键词
grep -i "error\|fail\|exception" /var/log/Home-page/deploy.log | tail -20

# 3. 手动测试脚本
cd /opt/Home-page
bash -x scripts/deploy.sh 2>&1 | tee deploy_test.log
```

**常见错误和解决方案：**

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `Permission denied` | 脚本无执行权限 | `chmod +x scripts/deploy.sh` |
| `command not found` | 依赖未安装 | 安装缺失的命令 |
| `connection timeout` | 网络或代理问题 | 检查网络配置 |
| `disk full` | 磁盘空间不足 | 清理日志或扩容 |

### 问题 2: 备份失败

**症状：**
- 部署在备份阶段失败
- 错误：`cannot copy a directory into itself`
- 备份目录冲突

**诊断步骤：**

```bash
# 1. 检查备份路径配置
grep BACKUP_DIR /opt/Home-page/scripts/deploy.sh

# 2. 检查磁盘空间
df -h /var/backups

# 3. 检查路径关系
PROJECT_DIR="/opt/Home-page"
BACKUP_DIR="/var/backups/Home-page"
echo "项目目录: $PROJECT_DIR"
echo "备份目录: $BACKUP_DIR"
if [[ "$BACKUP_DIR" == "$PROJECT_DIR/"* ]]; then
    echo "错误: 备份路径在项目目录内"
fi
```

**解决方案：**

1. **修正备份路径**
   ```bash
   # 部署脚本中
   BACKUP_DIR="/var/backups/Home-page"  # 在项目目录外
   ```

2. **使用 rsync 替代 cp**
   ```bash
   # rsync 更安全，避免路径冲突
   rsync -av --delete "$PROJECT_DIR/" "$BACKUP_DIR/"
   ```

3. **清理旧备份**
   ```bash
   # 删除 7 天前的备份
   find /var/backups/Home-page -mtime +7 -exec rm -rf {} \;
   ```

### 问题 3: Git 拉取失败

**症状：**
- 无法拉取最新代码
- 错误：`fatal: unable to access`
- 部署使用旧代码

**诊断步骤：**

```bash
# 1. 检查 Git 配置
cd /opt/Home-page
git remote -v

# 2. 测试连接
git fetch --dry-run origin main

# 3. 检查代理配置
git config --global --get http.https://github.com.proxy
```

**解决方案：**

| 问题 | 解决方案 |
|------|----------|
| 认证失败 | 更新 Git 凭据或使用 Token |
| 代理配置错误 | 重新配置代理：`git config --global http.https://github.com.proxy http://proxy:port` |
| 网络不通 | 检查防火墙和 DNS |
| 权限不足 | 检查目录和文件权限 |

### 问题 4: 依赖安装失败

**症状：**
- pip install 过程出错
- 版本冲突
- 依赖缺失

**诊断步骤：**

```bash
# 1. 激活虚拟环境
source /opt/Home-page/venv/bin/activate

# 2. 测试 pip
pip --version

# 3. 查看详细错误
pip install -r requirements.txt -v 2>&1 | tee pip_error.log
```

**解决方案：**

| 问题 | 解决方案 |
|------|----------|
| 版本冲突 | 更新 `requirements.txt`，指定兼容版本 |
| 网络超时 | 配置 pip 镜像源或代理 |
| 编译失败 | 安装 wheel 包：`pip install package.whl` |
| 权限问题 | 使用 `--user` 参数或修复虚拟环境 |

---

## 服务问题

### 问题 1: 应用服务无法启动

**症状：**
- systemctl 显示服务失败
- 无法访问应用
- 端口无法连接

**诊断步骤：**

```bash
# 1. 查看服务状态
sudo systemctl status Home-page

# 2. 查看详细日志
sudo journalctl -u Home-page -n 100 --no-pager

# 3. 检查端口监听
sudo netstat -tlnp | grep 5000

# 4. 检查应用日志
tail -100 /var/log/Home-page/app.log
```

**常见错误和解决方案：**

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 端口被占用 | 其他服务占用 5000 端口 | 修改端口配置或停止冲突服务 |
| 数据库连接失败 | 数据库未启动或配置错误 | 检查数据库服务：`systemctl status mysql` |
| 配置文件错误 | config.py 语法或值错误 | 检查配置文件格式 |
| 依赖缺失 | Python 包未安装 | 运行 `pip install -r requirements.txt` |

### 问题 2: 服务频繁重启

**症状：**
- 服务状态反复重启
- 应用不稳定
- 日志中有崩溃记录

**诊断步骤：**

```bash
# 1. 查看重启次数
sudo journalctl -u Home-page --since "1 hour ago" | grep -i "started\|stopped"

# 2. 查看崩溃日志
grep -i "traceback\|exception\|error" /var/log/Home-page/error.log | tail -50

# 3. 检查内存使用
free -h
ps aux | grep app.py
```

**解决方案：**

| 问题 | 解决方案 |
|------|----------|
| 内存不足 | 增加 swap 或升级内存 |
| 未捕获异常 | 查看完整日志，添加异常处理 |
| 配置错误 | 验证配置文件，修复错误值 |
| 数据库连接池耗尽 | 增加数据库连接池大小 |

---

## 网络问题

### 问题 1: 无法连接 GitHub

**症状：**
- git fetch 失败
- curl 超时
- 代理不生效

**诊断步骤：**

```bash
# 1. 测试直连 GitHub
curl -I https://github.com

# 2. 测试代理连接
curl -I --proxy http://proxy:port https://github.com

# 3. 测试 DNS
nslookup github.com

# 4. 测试路由
traceroute github.com
```

**解决方案：**

| 问题 | 解决方案 |
|------|----------|
| DNS 解析失败 | 更换 DNS 服务器为 8.8.8.8 |
| 防火墙阻挡 | 添加防火墙规则允许 GitHub |
| 代理配置错误 | 重新配置：`git config --global http.proxy http://proxy:port` |
| 证书问题 | 更新 CA 证书或忽略证书验证 |

### 问题 2: 网络极慢

**症状：**
- Git 拉取耗时 > 10 分钟
- pip install 超时
- 部署时间过长

**诊断步骤：**

```bash
# 1. 测试速度
speedtest-cli

# 2. 测试 GitHub 连接
curl -o /dev/null -s -w '%{time_total}\n' https://github.com

# 3. 测试代理速度
curl -o /dev/null -s -w '%{time_total}\n' --proxy http://proxy:port https://github.com
```

**解决方案：**

| 问题 | 解决方案 |
|------|----------|
| 代理慢 | 更换为更快的代理服务 |
| 无代理 | 配置国内镜像源或 CDN |
| 带宽限制 | 优化依赖，减少下载数量 |
| 网络拥塞 | 错峰部署，选择低峰时段 |

---

## 性能问题

### 问题 1: 部署耗时过长

**症状：**
- 完整部署 > 10 分钟
- 备份阶段慢
- 依赖更新慢

**诊断步骤：**

```bash
# 1. 分析部署日志
grep "Creating backup\|Pulling\|Updating\|Restarting" /var/log/Home-page/deploy.log

# 2. 测量各阶段时间
time ./scripts/deploy.sh 2>&1 | tee deploy_timing.log

# 3. 检查 I/O 性能
iostat -x 1
```

**优化方案：**

| 阶段 | 优化方法 |
|------|----------|
| 备份 | 使用 rsync 增量备份，跳过未改变文件 |
| 拉取 | 使用 shallow clone：`git clone --depth 1` |
| 依赖 | 使用缓存，避免重复下载 |
| 重启 | 优化应用启动时间，减少启动等待 |

### 问题 2: 磁盘空间不足

**症状：**
- 部署失败：`No space left on device`
- 备份无法创建
- 日志无法写入

**诊断步骤：**

```bash
# 1. 检查磁盘使用
df -h

# 2. 查看目录大小
du -sh /opt/Home-page
du -sh /var/backups/Home-page

# 3. 查找大文件
find /opt/Home-page -type f -size +100M | xargs ls -lh
```

**清理方案：**

| 清理目标 | 清理方法 |
|---------|----------|
| 日志文件 | 配置 logrotate，自动清理旧日志 |
| 旧备份 | 删除 7 天前的备份 |
| 临时文件 | 清理 `__pycache__`, `.pyc` 等 |
| 未使用的依赖 | 清理虚拟环境并重建 |

---

## 紧急恢复流程

### 快速回滚

当部署严重失败时，立即执行：

```bash
# 1. 停止新版本
sudo systemctl stop Home-page

# 2. 查看最近备份
ls -lt /var/backups/Home-page/ | head -5

# 3. 执行回滚
./scripts/rollback.sh Home-page_YYYYMMDD_HHMMSS

# 4. 验证服务
curl http://cloud-doors.com:5000/health
```

### 回滚检查清单

- [ ] 回滚版本已选择
- [ ] 服务已成功启动
- [ ] 健康检查通过
- [ ] 功能验证正常
- [ ] 通知相关人员

---

## 联系支持

### 收集诊断信息

在报告问题时，请提供以下信息：

```bash
# 系统信息
uname -a
cat /etc/os-release

# 服务状态
sudo systemctl status Home-page webhook-receiver

# 最近的日志
tail -100 /var/log/Home-page/deploy.log > deploy_diagnostic.log
tail -100 /var/log/Home-page/app.log > app_diagnostic.log
tail -100 /var/log/Home-page/error.log > error_diagnostic.log

# Git 信息
cd /opt/Home-page
git log -5 --oneline
git remote -v
```

### 报告模板

```
问题描述：
-----------
[详细描述问题]

影响范围：
-----------
- [ ] GitHub Actions
- [ ] Webhook
- [ ] 部署脚本
- [ ] 应用服务

已尝试的解决方法：
-----------
1. [方法 1]
2. [方法 2]

诊断信息：
-----------
- 系统版本：
- 日志文件：
- 错误代码：
```

---

<div align="center">

**文档版本**: v1.0  
**创建日期**: 2026-03-04  
**维护者**: 云户科技技术团队

</div>
