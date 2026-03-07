# 清除云主机上的 Webhook 配置

> 本指南提供完整的手动清理步骤，彻底移除云主机上的所有webhook相关配置

---

## 📋 清理清单

- [ ] 停止并禁用webhook服务
- [ ] 删除systemd服务文件
- [ ] 清理webhook脚本文件
- [ ] 移除防火墙规则
- [ ] 删除webhook日志文件
- [ ] 移除环境变量配置
- [ ] 停止webhook进程
- [ ] 清理临时文件

---

## 🔧 清理步骤

### 1. 停止并禁用webhook服务

```bash
# 停止webhook服务
sudo systemctl stop webhook-receiver

# 禁用webhook服务（禁止开机自启）
sudo systemctl disable webhook-receiver

# 验证服务状态
sudo systemctl status webhook-receiver
```

预期输出应该显示服务已停止和禁用。

### 2. 删除systemd服务文件

```bash
# 删除服务文件
sudo rm /etc/systemd/system/webhook-receiver.service

# 重新加载systemd配置
sudo systemctl daemon-reload

# 重置systemd失败计数
sudo systemctl reset-failed

# 验证服务已删除
sudo systemctl list-unit-files | grep webhook
```

预期输出应该为空，表示服务已完全删除。

### 3. 停止所有webhook相关进程

```bash
# 查找所有webhook进程
ps aux | grep webhook

# 强制停止所有webhook进程
pkill -9 -f webhook_receiver_github.py
pkill -9 -f webhook.*receiver

# 验证进程已停止
ps aux | grep webhook
```

预期输出应该只显示grep进程本身，没有webhook相关进程。

### 4. 清理webhook脚本文件

```bash
# 进入项目目录
cd /opt/Home-page

# 删除webhook接收器脚本
sudo rm -f scripts/webhook_receiver_github.py
sudo rm -f scripts/webhook_starter.sh
sudo rm -f scripts/webhook_receiver.py
sudo rm -f scripts/generate-webhook-secret.py

# 验证文件已删除
ls -la scripts/ | grep webhook
```

预期输出应该为空。

### 5. 移除防火墙规则

```bash
# 查看当前防火墙规则
sudo ufw status numbered

# 移除webhook端口规则（9000端口）
# 假设规则编号是X，根据实际情况替换
sudo ufw delete allow 9000/tcp

# 或者直接删除规则（如果知道编号）
# sudo ufw delete <规则编号>

# 验证规则已删除
sudo ufw status | grep 9000
```

预期输出应该为空，表示9000端口规则已删除。

### 6. 删除webhook日志文件

```bash
# 删除webhook日志目录
sudo rm -rf /var/log/integrate-code/webhook.log
sudo rm -rf /var/log/integrate-code/

# 或如果日志在其他位置
sudo rm -rf /var/log/Home-page/webhook.log

# 清理systemd日志
sudo journalctl --rotate
sudo journalctl --vacuum-time=1d

# 验证日志已删除
ls -la /var/log/integrate-code/ 2>/dev/null || echo "目录已删除"
```

### 7. 移除环境变量配置

```bash
# 进入项目目录
cd /opt/Home-page

# 备份当前.env文件
sudo cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 编辑.env文件，移除webhook相关配置
sudo nano .env
```

在`.env`文件中删除以下行（如果存在）：

```env
# 删除这些webhook相关配置
WEBHOOK_URL=http://cloud-doors.com:9000
WEBHOOK_SECRET=your-secret-here
```

或者使用sed命令自动删除：

```bash
# 备份
sudo cp .env .env.backup

# 删除webhook相关行
sudo sed -i '/WEBHOOK_URL/d' .env
sudo sed -i '/WEBHOOK_SECRET/d' .env

# 验证配置已删除
grep -i webhook .env || echo "webhook配置已清理"
```

### 8. 清理临时文件和目录

```bash
# 进入项目目录
cd /opt/Home-page

# 删除临时webhook启动脚本（如果在/tmp目录）
sudo rm -f /tmp/start_webhook.sh
sudo rm -f /tmp/webhook_starter.sh

# 删除webhook相关临时文件
sudo find /tmp -name "*webhook*" -type f -delete

# 清理Python缓存（包含webhook模块的.pyc文件）
sudo find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
sudo find . -type f -name "*.pyc" -delete

# 验证清理完成
find /tmp -name "*webhook*" 2>/dev/null || echo "临时文件已清理"
```

### 9. 从GitHub移除Webhook配置

#### 方式1：通过Web界面

1. 访问GitHub仓库：`https://github.com/liubin20020924-cloud/Home-page/settings/hooks`
2. 找到webhook配置
3. 点击webhook右侧的设置图标
4. 选择"Delete"删除webhook
5. 确认删除

#### 方式2：通过GitHub CLI

```bash
# 安装gh CLI（如果未安装）
# Ubuntu/Debian
sudo apt install gh

# 登录GitHub
gh auth login

# 列出所有webhook
gh api repos/liubin20020924-cloud/Home-page/hooks

# 删除指定webhook（使用webhook ID）
gh api --method DELETE /repos/liubin20020924-cloud/Home-page/hooks/{webhook_id}
```

### 10. 清理GitHub Secrets

```bash
# 删除webhook相关的secrets
gh secret delete WEBHOOK_URL
gh secret delete WEBHOOK_SECRET

# 验证secrets已删除
gh secret list
```

---

## ✅ 验证清理完成

执行以下验证命令，确保所有webhook配置已清理：

### 1. 检查系统服务

```bash
# 检查webhook服务
sudo systemctl list-units --all | grep webhook

# 预期输出：无结果
```

### 2. 检查运行进程

```bash
# 检查webhook进程
ps aux | grep -i webhook | grep -v grep

# 预期输出：无结果
```

### 3. 检查端口占用

```bash
# 检查9000端口
sudo netstat -tlnp | grep 9000
# 或
sudo ss -tlnp | grep 9000

# 预期输出：无结果
```

### 4. 检查文件系统

```bash
# 检查webhook脚本
ls -la /opt/Home-page/scripts/ | grep webhook

# 检查日志文件
ls -la /var/log/integrate-code/ 2>/dev/null || echo "目录不存在"

# 检查临时文件
find /tmp -name "*webhook*" 2>/dev/null || echo "无临时文件"

# 预期输出：所有命令都应显示"无结果"或"目录不存在"
```

### 5. 检查环境变量

```bash
# 检查.env文件
grep -i webhook /opt/Home-page/.env || echo "无webhook配置"

# 预期输出："无webhook配置"
```

### 6. 检查防火墙

```bash
# 检查9000端口规则
sudo ufw status | grep 9000

# 预期输出：无结果
```

### 7. 检查GitHub配置

访问：https://github.com/liubin20020924-cloud/Home-page/settings/hooks

预期结果：webhook列表应为空。

---

## 🔒 清理后检查清单

- [x] webhook服务已停止
- [x] webhook服务已禁用
- [x] systemd服务文件已删除
- [x] 所有webhook进程已停止
- [x] webhook脚本文件已删除
- [x] 防火墙规则已移除
- [x] 日志文件已清理
- [x] 环境变量已移除
- [x] 临时文件已清理
- [x] GitHub webhook已删除
- [x] GitHub secrets已删除
- [x] 端口9000已释放
- [x] 验证测试全部通过

---

## 🚨 回滚方法（如果需要）

如果清理后需要恢复，可以使用以下方法：

### 恢复webhook脚本

```bash
# 从GitHub恢复
cd /opt/Home-page
git checkout scripts/webhook_receiver_github.py
git checkout scripts/generate-webhook-secret.py
```

### 恢复环境变量

```bash
# 从备份恢复
sudo cp .env.backup.* .env

# 或从GitHub恢复
git checkout .env
```

### 恢复systemd服务

```bash
# 重新创建服务文件
sudo nano /etc/systemd/system/webhook-receiver.service
```

粘贴之前的服务配置，然后：

```bash
# 重新加载
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable webhook-receiver

# 启动服务
sudo systemctl start webhook-receiver
```

---

## 📝 完整清理脚本

如果需要一键清理所有webhook配置，可以使用以下脚本：

```bash
#!/bin/bash

# webhook完全清理脚本
# 使用前请仔细阅读并理解每个步骤！

set -e

echo "========================================"
echo "开始清理Webhook配置..."
echo "========================================"

# 1. 停止并禁用服务
echo "[1/10] 停止并禁用webhook服务..."
sudo systemctl stop webhook-receiver 2>/dev/null || true
sudo systemctl disable webhook-receiver 2>/dev/null || true

# 2. 删除服务文件
echo "[2/10] 删除systemd服务文件..."
sudo rm -f /etc/systemd/system/webhook-receiver.service
sudo systemctl daemon-reload
sudo systemctl reset-failed 2>/dev/null || true

# 3. 停止进程
echo "[3/10] 停止webhook进程..."
pkill -9 -f webhook_receiver_github.py 2>/dev/null || true
pkill -9 -f webhook.*receiver 2>/dev/null || true

# 4. 删除脚本
echo "[4/10] 删除webhook脚本..."
cd /opt/Home-page
sudo rm -f scripts/webhook_receiver_github.py
sudo rm -f scripts/webhook_starter.sh
sudo rm -f scripts/webhook_receiver.py
sudo rm -f scripts/generate-webhook-secret.py

# 5. 移除防火墙规则
echo "[5/10] 移除防火墙规则..."
sudo ufw delete allow 9000/tcp 2>/dev/null || true

# 6. 删除日志
echo "[6/10] 删除webhook日志..."
sudo rm -rf /var/log/integrate-code/

# 7. 移除环境变量
echo "[7/10] 移除环境变量配置..."
sudo sed -i '/WEBHOOK_URL/d' .env 2>/dev/null || true
sudo sed -i '/WEBHOOK_SECRET/d' .env 2>/dev/null || true

# 8. 清理临时文件
echo "[8/10] 清理临时文件..."
sudo rm -f /tmp/start_webhook.sh
sudo rm -f /tmp/webhook_starter.sh
sudo find /tmp -name "*webhook*" -type f -delete 2>/dev/null || true

# 9. 清理Python缓存
echo "[9/10] 清理Python缓存..."
sudo find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
sudo find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 10. 验证
echo "[10/10] 验证清理结果..."
echo ""
echo "========================================"
echo "验证结果："
echo "========================================"

if systemctl list-units --all | grep -q webhook; then
    echo "❌ 警告：webhook服务仍存在"
else
    echo "✅ webhook服务已清理"
fi

if ps aux | grep -i webhook | grep -v grep >/dev/null; then
    echo "❌ 警告：webhook进程仍在运行"
else
    echo "✅ webhook进程已停止"
fi

if ls scripts/ | grep -q webhook; then
    echo "❌ 警告：webhook脚本仍存在"
else
    echo "✅ webhook脚本已删除"
fi

if grep -qi webhook .env; then
    echo "❌ 警告：.env中仍有webhook配置"
else
    echo "✅ 环境变量已清理"
fi

if sudo ufw status | grep -q 9000; then
    echo "❌ 警告：9000端口防火墙规则仍存在"
else
    echo "✅ 防火墙规则已移除"
fi

echo ""
echo "========================================"
echo "Webhook配置清理完成！"
echo "========================================"
echo ""
echo "⚠️  请手动完成以下步骤："
echo "   1. 访问GitHub仓库设置"
echo "   2. 删除Webhook配置（Settings → Webhooks）"
echo "   3. 删除GitHub Secrets（WEBHOOK_URL, WEBHOOK_SECRET）"
echo ""
```

使用方法：

```bash
# 1. 保存脚本
nano /tmp/cleanup_webhook.sh

# 2. 粘贴上面的脚本内容

# 3. 设置执行权限
chmod +x /tmp/cleanup_webhook.sh

# 4. 执行清理
sudo /tmp/cleanup_webhook.sh
```

---

## 📚 相关文档

- [CI/CD配置指南](./CICD/02-CONFIGURATION.md)
- [故障排除指南](./CICD/05-TROUBLESHOOTING.md)
- [版本管理规范](../project-management/VERSION_MANAGEMENT_GUIDE.md)

---

<div align="center">

**最后更新**: 2026-03-05
**维护者**: 云户科技技术团队

</div>
