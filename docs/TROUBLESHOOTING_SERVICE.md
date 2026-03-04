# 云主机服务启动故障排查指南

> 解决 webhook-receiver 服务启动失败问题

---

## 🚨 错误信息

```
Process: 4027243 ExecStart=/usr/bin/python3 /opt/Home-page/scripts/webhook_receiver_github.py (code=exited, status=1/FAILURE)
```

**原因**：`webhook_receiver_github.py` 脚本执行失败

---

## 🔍 排查步骤

### 第一步：手动运行脚本查看详细错误

```bash
# 在云主机上执行
cd /opt/Home-page
python3 scripts/webhook_receiver_github.py
```

**观察输出**，应该能看到具体的错误信息。

---

### 第二步：检查Python环境

#### 2.1 检查Python版本

```bash
# 检查Python3版本
python3 --version

# 应该看到：Python 3.8 或更高版本
```

#### 2.2 检查Flask是否安装

```bash
# 检查Flask
python3 -c "import flask; print(flask.__version__)"
```

如果报错 `ModuleNotFoundError: No module named 'flask'`，需要安装：

```bash
# 安装Flask
pip3 install flask

# 或使用系统的pip
pip install flask
```

#### 2.3 检查依赖

```bash
# 检查所有依赖
python3 -c "
import sys
try:
    import flask
    print('✓ Flask')
except ImportError:
    print('✗ Flask 未安装')

try:
    import hmac
    print('✓ hmac')
except ImportError:
    print('✗ hmac 未安装')

try:
    import hashlib
    print('✓ hashlib')
except ImportError:
    print('✗ hashlib 未安装')
"
```

---

### 第三步：检查文件权限和路径

```bash
# 检查文件是否存在
ls -la /opt/Home-page/scripts/webhook_receiver_github.py

# 应该看到：
# -rwxr-xr-x 1 root root XXXX XX XX:XX webhook_receiver_github.py

# 检查文件内容
head -20 /opt/Home-page/scripts/webhook_receiver_github.py
```

---

### 第四步：检查端口占用

```bash
# 检查9000端口是否被占用
netstat -tuln | grep 9000
# 或
ss -tuln | grep 9000

# 如果被占用，杀掉占用进程
# lsof -i:9000
# kill -9 <PID>
```

---

### 第五步：查看详细日志

```bash
# 查看systemd日志
journalctl -u webhook-receiver -n 50

# 实时查看
journalctl -u webhook-receiver -f

# 查看错误日志
tail -f /var/log/integrate-code/webhook-error.log
```

---

## 🔧 常见问题和解决方案

### 问题1：Flask未安装

**错误**：
```
ModuleNotFoundError: No module named 'flask'
```

**解决**：
```bash
# 安装Flask
pip3 install flask

# 验证安装
python3 -c "import flask; print('Flask已安装')"
```

---

### 问题2：Python3路径错误

**错误**：
```
/usr/bin/python3: No such file or directory
```

**解决**：
```bash
# 查找Python3路径
which python3

# 更新服务文件
nano /etc/systemd/system/webhook-receiver.service
```

修改 `ExecStart` 行：
```ini
# 找到的路径，例如：
ExecStart=/usr/local/bin/python3 /opt/Home-page/scripts/webhook_receiver_github.py
```

重新加载：
```bash
systemctl daemon-reload
systemctl restart webhook-receiver
```

---

### 问题3：端口被占用

**错误**：
```
OSError: [Errno 98] Address already in use
```

**解决**：
```bash
# 查找占用9000端口的进程
lsof -i:9000
# 或
netstat -tuln | grep 9000

# 杀掉进程
kill -9 <PID>

# 重启服务
systemctl restart webhook-receiver
```

---

### 问题4：权限问题

**错误**：
```
PermissionError: [Errno 13] Permission denied
```

**解决**：
```bash
# 确保文件所有者正确
chown root:root /opt/Home-page/scripts/webhook_receiver_github.py

# 设置可执行权限
chmod +x /opt/Home-page/scripts/webhook_receiver_github.py
```

---

### 问题5：编码问题

**错误**：
```
UnicodeDecodeError
```

**解决**：
确保文件使用UTF-8编码：
```bash
# 检查文件编码
file -i /opt/Home-page/scripts/webhook_receiver_github.py

# 应该看到：
# text/plain; charset=utf-8
```

如果不是UTF-8，重新转换：
```bash
iconv -f ISO-8859-1 -t UTF-8 webhook_receiver_github.py > webhook_receiver_github_utf8.py
mv webhook_receiver_github_utf8.py webhook_receiver_github.py
```

---

## 🚀 快速诊断命令

在云主机上复制粘贴以下命令：

```bash
echo "=========================================="
echo "诊断webhook-receiver服务"
echo "=========================================="
echo ""

echo "1. 检查Python版本..."
python3 --version

echo ""
echo "2. 检查Flask..."
python3 -c "import flask; print('Flask已安装:', flask.__version__)" 2>&1 || echo "Flask未安装，需要运行: pip3 install flask"

echo ""
echo "3. 检查文件..."
ls -la /opt/Home-page/scripts/webhook_receiver_github.py

echo ""
echo "4. 检查端口..."
netstat -tuln | grep 9000 || echo "端口9000未被占用"

echo ""
echo "5. 手动运行脚本（查看详细错误）..."
cd /opt/Home-page
timeout 5 python3 scripts/webhook_receiver_github.py 2>&1 || echo "脚本执行失败"

echo ""
echo "6. 查看服务日志..."
journalctl -u webhook-receiver -n 20 --no-pager

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="
```

---

## 🔧 完整修复流程

### 步骤1：安装依赖

```bash
# 安装Flask（如果需要）
pip3 install flask

# 验证
python3 -c "import flask; print('OK')"
```

### 步骤2：手动测试脚本

```bash
cd /opt/Home-page
timeout 10 python3 scripts/webhook_receiver_github.py
```

**期望**：启动并监听端口9000，超时后自动退出（正常）。

**如果报错**：根据错误信息修复。

### 步骤3：检查并修复权限

```bash
chown root:root /opt/Home-page/scripts/webhook_receiver_github.py
chmod +x /opt/Home-page/scripts/webhook_receiver_github.py
```

### 步骤4：重启服务

```bash
# 重新加载systemd
systemctl daemon-reload

# 重启服务
systemctl restart webhook-receiver

# 查看状态
systemctl status webhook-receiver
```

### 步骤5：验证服务运行

```bash
# 检查服务状态
systemctl is-active webhook-receiver

# 应该看到：active

# 测试端口监听
netstat -tuln | grep 9000

# 应该看到：
# tcp  0  0 0.0.0.0:9000  0.0.0.0:*  LISTEN
```

---

## 📋 修复检查清单

完成修复后，确认：

### 环境检查
- [ ] Python3版本 >= 3.8
- [ ] Flask已安装
- [ ] 其他Python依赖已安装

### 文件检查
- [ ] 文件存在于 `/opt/Home-page/scripts/webhook_receiver_github.py`
- [ ] 文件所有者为root
- [ ] 文件有执行权限

### 网络检查
- [ ] 端口9000未被占用
- [ ] 防火墙规则已添加（允许9000端口）

### 服务检查
- [ ] 服务状态为active
- [ ] 端口9000正在监听
- [ ] 服务日志无错误

### 功能检查
- [ ] 手动运行脚本成功
- [ ] Webhook健康检查可访问
- [ ] curl测试返回200状态码

---

## ✅ 验证命令

```bash
# 1. 服务状态
systemctl status webhook-receiver

# 2. 端口监听
netstat -tuln | grep 9000

# 3. 健康检查
curl http://localhost:9000/webhook/health

# 应该返回：{"status":"ok","message":"Webhook service is running"}

# 4. 查看日志
tail -f /var/log/integrate-code/webhook.log
```

---

**运行快速诊断命令，查看详细错误信息！** 🚀
