# 系统监控与告警使用指南

## 📋 概述

系统监控与告警功能提供了完整的系统性能监控、告警通知和健康检查能力，帮助您及时发现和解决系统问题。

---

## 🚀 功能特性

### 1. 系统资源监控
- ✅ CPU 使用率监控
- ✅ 内存使用率监控
- ✅ 磁盘使用率监控
- ✅ 网络流量监控
- ✅ 进程数监控

### 2. 应用性能监控
- ✅ API 响应时间追踪
- ✅ 错误率监控
- ✅ 慢查询检测
- ✅ 并发请求数监控

### 3. 智能告警
- ✅ 多级别告警（信息、警告、严重）
- ✅ 可配置的告警阈值
- ✅ 自动告警恢复通知
- ✅ 邮件通知支持

### 4. 监控仪表板
- ✅ 实时系统指标展示
- ✅ 活跃告警查看
- ✅ 告警历史记录
- ✅ 手动测试告警功能

### 5. 健康检查
- ✅ `/monitoring/health` - 健康检查端点
- ✅ `/monitoring/readiness` - 就绪检查端点

---

## 🔧 安装与配置

### 1. 安装依赖

```bash
pip install psutil
```

或者更新所有依赖：
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在 `.env` 文件中添加以下配置：

```bash
# 监控与告警配置
MONITORING_ENABLED=True

# CPU 告警阈值（百分比）
CPU_WARNING_THRESHOLD=70
CPU_CRITICAL_THRESHOLD=90

# 内存告警阈值（百分比）
MEMORY_WARNING_THRESHOLD=70
MEMORY_CRITICAL_THRESHOLD=85

# 磁盘告警阈值（百分比）
DISK_WARNING_THRESHOLD=80
DISK_CRITICAL_THRESHOLD=90

# 是否启用邮件告警通知
MONITORING_EMAIL_ENABLED=True

# 告警邮件接收者（多个邮箱用逗号分隔）
MONITORING_EMAIL_RECIPIENTS=admin@company.com,ops@company.com

# 监控数据采集间隔（秒）
MONITOR_INTERVAL=60
```

### 3. 重启应用

```bash
# 开发环境
python app.py

# 或使用生产启动脚本
./start.sh  # Linux/Mac
start.bat   # Windows
```

---

## 📊 使用监控仪表板

### 访问监控仪表板

启动应用后，访问：
```
http://your-domain.com:5000/monitoring/
```

**注意**: 需要管理员权限才能访问监控仪表板。

### 仪表板功能

#### 1. 系统指标卡片
- **CPU 使用率**: 实时显示 CPU 使用百分比
- **内存使用率**: 显示内存使用百分比和可用容量
- **磁盘使用率**: 显示磁盘使用百分比和可用容量
- **进程数**: 显示系统进程总数

#### 2. 网络统计
- **网络发送**: 显示总发送数据量（GB）
- **网络接收**: 显示总接收数据量（GB）

#### 3. 告警查看
- **活跃告警**: 当前未解决的告警
- **告警历史**: 最近 24 小时的告警记录

#### 4. 测试告警
- **测试警告告警**: 发送警告级别的测试告警
- **测试严重告警**: 发送严重级别的测试告警

---

## 🔔 告警规则

### CPU 告警
| 级别 | 阈值 | 说明 |
|------|--------|------|
| 警告 | > 70% | CPU 使用率超过 70% |
| 严重 | > 90% | CPU 使用率超过 90% |

### 内存告警
| 级别 | 阈值 | 说明 |
|------|--------|------|
| 警告 | > 70% | 内存使用率超过 70% |
| 严重 | > 85% | 内存使用率超过 85% |

### 磁盘告警
| 级别 | 阈值 | 说明 |
|------|--------|------|
| 警告 | > 80% | 磁盘使用率超过 80% |
| 严重 | > 90% | 磁盘使用率超过 90% |

### API 响应时间告警
| 级别 | 阈值 | 说明 |
|------|--------|------|
| 警告 | > 1000ms | API 响应时间超过 1 秒 |
| 严重 | > 3000ms | API 响应时间超过 3 秒 |

---

## 📡 API 接口

### 获取当前指标

```bash
GET /monitoring/api/metrics
```

响应示例：
```json
{
  "success": true,
  "data": {
    "cpu_usage": 45.2,
    "memory_usage": 62.3,
    "memory_available": 7.5,
    "disk_usage": 55.8,
    "disk_available": 45.2,
    "network_bytes_sent": 1024000000,
    "network_bytes_recv": 2048000000,
    "process_count": 234
  },
  "timestamp": "2026-03-07T10:30:00"
}
```

### 获取告警列表

```bash
GET /monitoring/api/alerts?hours=24&status=all&level=all
```

参数：
- `hours`: 时间范围（小时），默认 24
- `status`: 状态筛选（all, active, resolved），默认 all
- `level`: 级别筛选（all, warning, error, critical），默认 all

### 获取活跃告警

```bash
GET /monitoring/api/alerts/active
```

### 测试告警

```bash
POST /monitoring/api/test-alert
Content-Type: application/json

{
  "level": "warning",
  "metric_name": "test_metric",
  "value": 85.0
}
```

### 健康检查

```bash
GET /monitoring/health
```

响应示例：
```json
{
  "status": "healthy",
  "timestamp": "2026-03-07T10:30:00",
  "metrics": { ... },
  "active_alerts": 0,
  "critical_alerts": 0
}
```

### 就绪检查

```bash
GET /monitoring/readiness
```

---

## 🛠️ 数据库索引优化

### 运行索引优化

```bash
# 测试模式（不实际创建索引）
python scripts/optimize_database_indexes.py --dry-run

# 实际创建索引
python scripts/optimize_database_indexes.py

# 查看报告
cat index_optimization_report.md
```

### 优化范围

索引优化脚本会分析以下数据库：
- `clouddoors_db` - 官网系统数据库
- `YHKB` - 知识库系统数据库
- `casedb` - 工单系统数据库

---

## 🔒 安全加固

### 运行安全审计

```bash
# 执行安全审计
python scripts/security_hardening.py

# 查看报告
cat security_audit_report.md
```

### 安全检查项目

- ✅ XSS 漏洞检查
- ✅ CSRF 保护检查
- ✅ API 限流检查
- ✅ 敏感信息泄露检查
- ✅ 依赖漏洞检查

---

## 📈 性能监控

### API 响应时间

监控中间件会自动记录每个 API 请求的响应时间，并在响应头中添加：
```
X-Response-Time: 245.67ms
X-Request-ID: 20260307103000123456
```

### 慢查询日志

当 API 响应时间超过 3 秒时，会自动记录警告日志：

```
WARNING - Slow request: POST /api/tickets - 3456.78ms - Status: 200
```

---

## 🔧 故障排查

### 监控服务未启动

**症状**: 监控仪表板无数据

**解决方案**:
1. 检查 `psutil` 是否已安装
2. 检查 `.env` 文件中是否配置了监控参数
3. 查看应用日志中的错误信息

### 告警邮件未发送

**症状**: 触发告警但未收到邮件

**解决方案**:
1. 检查邮件配置是否正确
2. 检查 `MONITORING_EMAIL_ENABLED` 是否为 `True`
3. 检查 `MONITORING_EMAIL_RECIPIENTS` 是否配置
4. 查看邮件服务日志

### 健康检查失败

**症状**: `/monitoring/health` 返回 503

**解决方案**:
1. 检查是否有严重告警
2. 检查数据库连接是否正常
3. 查看应用日志中的错误信息

---

## 📊 监控数据保留

- **指标数据**: 默认保留 7 天
- **告警数据**: 默认保留 30 天

可在 `.env` 文件中配置：
```bash
METRICS_RETENTION_DAYS=7
ALERT_RETENTION_DAYS=30
```

---

## 🎯 最佳实践

### 1. 合理设置告警阈值
- 根据实际情况调整阈值
- 避免阈值过低导致告警泛滥
- 定期review告警有效性

### 2. 及时处理告警
- 严重告警应立即响应
- 警告告警应在 1 小时内处理
- 定期检查告警历史

### 3. 定期优化数据库
- 每月运行一次索引优化
- 监控慢查询日志
- 定期清理历史数据

### 4. 安全审计
- 每季度运行一次安全审计
- 及时修复发现的安全问题
- 保持依赖库更新

---

## 📞 技术支持

如有问题，请联系：
- 邮箱: support@cloud-doors.com
- 工单: http://cloud-doors.com:5000/case

---

**文档版本**: v1.0
**最后更新**: 2026-03-07
