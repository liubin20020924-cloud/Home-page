# 监控功能快速开始指南

## 🚀 5 分钟快速启用

### 步骤 1: 安装依赖
```bash
pip install psutil
```

### 步骤 2: 配置环境变量
在 `.env` 文件中添加：
```bash
# 监控配置（最小配置）
MONITORING_ENABLED=True
MONITORING_EMAIL_ENABLED=False  # 暂时关闭邮件通知
```

### 步骤 3: 重启应用
```bash
python app.py
```

### 步骤 4: 访问监控仪表板
```
http://localhost:5000/monitoring/
```

需要管理员权限才能访问。

---

## 📊 查看系统指标

### 访问仪表板
打开浏览器访问: `http://localhost:5000/monitoring/`

你会看到：
- ✅ CPU 使用率
- ✅ 内存使用率
- ✅ 磁盘使用率
- ✅ 网络流量统计
- ✅ 告警历史

### 使用 API
```bash
# 获取当前指标
curl http://localhost:5000/monitoring/api/metrics

# 健康检查
curl http://localhost:5000/monitoring/health
```

---

## 🔔 配置邮件告警

### 1. 确保邮件配置正确
在 `.env` 文件中配置邮件服务：
```bash
MAIL_SERVER=smtp.exmail.qq.com
MAIL_PORT=465
MAIL_USERNAME=your_email@company.com
MAIL_PASSWORD=your-password
```

### 2. 启用邮件告警
```bash
MONITORING_EMAIL_ENABLED=True
MONITORING_EMAIL_RECIPIENTS=admin@company.com
```

### 3. 重启应用
```bash
python app.py
```

### 4. 测试告警
在监控仪表板点击"测试告警"按钮，检查是否收到邮件。

---

## 🔧 调整告警阈值

### 默认阈值
| 指标 | 警告 | 严重 |
|------|------|------|
| CPU | 70% | 90% |
| 内存 | 70% | 85% |
| 磁盘 | 80% | 90% |

### 自定义阈值
在 `.env` 文件中修改：
```bash
CPU_WARNING_THRESHOLD=80    # 提高到 80%
CPU_CRITICAL_THRESHOLD=95   # 提高到 95%
MEMORY_WARNING_THRESHOLD=80 # 提高到 80%
```

重启应用后生效。

---

## 🛠️ 运行数据库优化

### 1. 测试模式（推荐先运行）
```bash
python scripts/optimize_database_indexes.py --dry-run
```

### 2. 查看推荐报告
```bash
cat index_optimization_report.md
```

### 3. 应用优化（确认无误后）
```bash
python scripts/optimize_database_indexes.py
```

---

## 🔒 运行安全审计

### 1. 执行审计
```bash
python scripts/security_hardening.py
```

### 2. 查看报告
```bash
cat security_audit_report.md
```

### 3. 修复发现的问题
根据报告中的建议逐项修复。

---

## 🐛 故障排查

### 问题 1: 监控仪表板显示 "无数据"

**解决方案**:
1. 检查 `psutil` 是否已安装
   ```bash
   python -c "import psutil; print(psutil.cpu_percent())"
   ```

2. 检查应用日志是否有错误

### 问题 2: 收不到告警邮件

**解决方案**:
1. 检查邮件配置是否正确
2. 检查 `MONITORING_EMAIL_ENABLED` 是否为 `True`
3. 检查 `MONITORING_EMAIL_RECIPIENTS` 是否配置
4. 查看应用日志中的邮件发送错误

### 问题 3: 健康检查返回 503

**解决方案**:
1. 检查是否有严重告警
2. 检查数据库连接是否正常
3. 查看应用日志

---

## 📚 更多信息

- 完整文档: `docs/MONITORING_GUIDE.md`
- 实施总结: `docs/IMPLEMENTATION_SUMMARY_MONITORING.md`
- API 文档: http://localhost:5000/api/docs

---

**快速开始完成！** 🎉

现在你已经成功启用了系统监控功能。
