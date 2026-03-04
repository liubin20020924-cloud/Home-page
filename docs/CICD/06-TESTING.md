# CI/CD 测试指南

> CI/CD 系统的完整测试流程和验证方法

---

## 📋 目录

1. [测试概述](#测试概述)
2. [本地测试](#本地测试)
3. [CI 测试](#ci-测试)
4. [CD 测试](#cd-测试)
5. [集成测试](#集成测试)
6. [性能测试](#性能测试)
7. [测试报告](#测试报告)

---

## 测试概述

### 测试目标

确保 CI/CD 系统的每个环节都经过充分测试，验证：

1. ✅ 代码质量：符合规范，无语法错误
2. ✅ 功能完整性：所有功能正常工作
3. ✅ 安全性：无已知漏洞
4. ✅ 部署可靠性：自动化部署稳定可重复
5. ✅ 回滚能力：可以快速恢复
6. ✅ 监控告警：问题能及时发现

### 测试策略

| 测试类型 | 测试频率 | 执行方式 |
|---------|---------|----------|
| 单元测试 | 每次 Push | GitHub Actions |
| 集成测试 | 每次 PR | GitHub Actions |
| 部署测试 | 部署后 | 云主机 |
| 安全扫描 | 每次 Push | GitHub Actions |
| 性能测试 | 定期 | 手动/自动 |

---

## 本地测试

### 开发前检查

```bash
# 1. Python 语法检查
python -m py_compile app.py

# 2. 代码风格检查
flake8 --max-line-length=120 app/ routes/ services/

# 3. 类型检查（如果使用 mypy）
mypy app.py

# 4. 安全检查（静态）
bandit -r app/ routes/ services/
```

### 单元测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_routes.py -v

# 运行特定测试函数
pytest tests/test_routes.py::test_login -v

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html

# 查看覆盖率
open htmlcov/index.html
```

### 本地集成测试

```bash
# 启动测试服务器
python app.py

# 在另一个终端运行集成测试
pytest tests/test_integration.py -v

# 或使用 pytest 的并发执行
pytest tests/ -n auto
```

### 测试清单

- [ ] 所有单元测试通过
- [ ] 测试覆盖率 > 80%
- [ ] 无代码风格警告
- [ ] 无类型检查错误
- [ ] 无安全漏洞警告
- [ ] 应用可以正常启动
- [ ] 所有核心功能正常
- [ ] 数据库连接正常
- [ ] 文件上传功能正常
- [ ] 用户认证功能正常

---

## CI 测试

### GitHub Actions 测试验证

#### 检查 1: 代码质量检查

```yaml
# 验证步骤
1. Push 代码到功能分支
2. 查看 Actions 标签页
3. 等待 "Code Check" 完成
4. 查看检查结果
```

**预期结果：**
- ✅ 语法检查通过
- ✅ 代码风格符合 PEP 8
- ✅ 无严重警告
- ⚠️ 警告已记录

#### 检查 2: 单元测试

```yaml
# 验证步骤
1. 查看 "Run Tests" 任务
2. 等待测试完成
3. 查看测试报告
```

**预期结果：**
- ✅ 所有测试通过
- ✅ 覆盖率 > 80%
- ✅ 无测试超时
- ✅ 测试结果已上传

#### 检查 3: 安全扫描

```yaml
# 验证步骤
1. 查看 "Security Check" 任务
2. 等待扫描完成
3. 查看安全报告
```

**预期结果：**
- ✅ 无严重漏洞
- ✅ 无中危漏洞
- ⚠️ 低危漏洞已记录
- ✅ SQL 注入检查通过

#### 检查 4: 自动合并

```yaml
# 验证步骤
1. 确保 PR 标签包含 `auto-merge`
2. 等待 "Auto Merge" 任务
3. 确认代码已合并到 main
```

**预期结果：**
- ✅ PR 已合并
- ✅ main 分支已更新
- ✅ 触发部署流程

### Actions 测试命令

```bash
# 本地触发测试 workflow
gh workflow run ci-cd.yml --ref main

# 查看最近运行
gh run list --workflow=ci-cd.yml --limit 5

# 查看特定运行的日志
gh run view <run-id>

# 下载运行日志
gh run download <run-id>
```

### CI 测试清单

- [ ] Code Check 通过
- [ ] 所有 Lint 检查通过
- [ ] 测试通过（所有用例）
- [ ] 测试覆盖率达标
- [ ] Security Check 通过
- [ ] 无严重安全漏洞
- [ ] Auto Merge 成功执行
- [ ] 部署通知已触发
- [ ] Actions 日志正常

---

## CD 测试

### Webhook 测试

#### 测试 1: 健康检查

```bash
# 测试 Webhook 服务健康状态
curl http://cloud-doors.com:9000/webhook/health

# 预期响应
{
  "status": "healthy",
  "version": "x.x.x",
  "last_deployment": "2026-03-04T12:00:00Z"
}
```

**验证点：**
- ✅ HTTP 状态码为 200
- ✅ 响应包含 `status: healthy`
- ✅ 响应时间 < 1 秒

#### 测试 2: 手动触发部署

```bash
# 模拟 GitHub Webhook 请求
curl -X POST http://cloud-doors.com:9000/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=<测试签名>" \
  -d '{
    "ref": "refs/heads/main",
    "repository": {
      "name": "Home-page",
      "full_name": "liubin20020924-cloud/Home-page"
    },
    "pusher": {
      "name": "Test User"
    },
    "sender": {
      "login": "test-user"
    }
  }'
```

**验证点：**
- ✅ 返回 200 OK
- ✅ 部署日志开始记录
- ✅ 部署流程正常执行
- ✅ 最终应用成功更新

#### 测试 3: 版本查询

```bash
# 查询当前部署版本
curl http://cloud-doors.com:9000/webhook/version

# 预期响应
{
  "version": "Home-page_20260304_120000",
  "sha": "abc123...",
  "time": "2026-03-04T12:00:00Z",
  "git_ref": "refs/heads/main"
}
```

### 部署测试

#### 测试 1: 完整部署流程

```bash
# 1. 本地创建测试提交
git commit --allow-empty -m "test: 部署测试"

# 2. 推送到 GitHub
git push origin main

# 3. 监控部署过程
tail -f /var/log/Home-page/deploy.log

# 4. 等待部署完成（约 2-5 分钟）
# 5. 验证应用更新
curl http://cloud-doors.com:5000/health
```

**验证点：**
- ✅ 备份成功创建
- ✅ 代码成功拉取
- ✅ 依赖成功更新
- ✅ 服务成功重启
- ✅ 应用健康检查通过
- ✅ 功能验证正常

#### 测试 2: 回滚测试

```bash
# 1. 查看可用备份
ls -lh /var/backups/Home-page/

# 2. 执行回滚
cd /opt/Home-page
./scripts/rollback.sh Home-page_20260303_120000

# 3. 验证回滚成功
curl http://cloud-doors.com:5000/health

# 4. 检查应用功能
```

**验证点：**
- ✅ 备份文件成功恢复
- ✅ 服务成功重启
- ✅ 应用使用回滚版本
- ✅ 功能验证正常
- ✅ 无数据丢失

#### 测试 3: 备份验证

```bash
# 1. 创建测试文件
echo "test content $(date)" > /opt/Home-page/test.txt

# 2. 触发部署
# 通过 Push 或 Webhook

# 3. 验证备份存在
ls -lh /var/backups/Home-page/Home-page_*/

# 4. 验证备份文件内容
grep "test content" /var/backups/Home-page/Home-page_*/test.txt
```

**验证点：**
- ✅ 备份目录存在
- ✅ 时间戳备份目录已创建
- ✅ 备份包含所有文件
- ✅ 备份文件内容正确
- ✅ rsync 增量备份工作

### CD 测试清单

- [ ] Webhook 健康检查通过
- [ ] 手动触发部署成功
- [ ] 版本查询 API 正常
- [ ] 完整部署流程成功
- [ ] 回滚功能正常
- [ ] 备份机制正常
- [ ] 服务重启成功
- [ ] 应用健康检查通过
- [ ] 功能验证正常
- [ ] 部署日志完整

---

## 集成测试

### 端到端测试

#### 测试 1: 用户注册 → 工单提交

```bash
# 1. 测试用户注册
curl -X POST http://cloud-doors.com:5000/unified/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test@123",
    "email": "test@example.com"
  }'

# 2. 使用返回的 token 提交工单
TOKEN="返回的jwt_token"
curl -X POST http://cloud-doors.com:5000/case/tickets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试工单",
    "description": "这是一个测试工单",
    "priority": "normal"
  }'
```

#### 测试 2: 知识库搜索 → 文件下载

```bash
# 1. 搜索知识库
curl http://cloud-doors.com:5000/kb/search?q=测试

# 2. 下载文档
curl http://cloud-doors.com:5000/kb/download/1 -o test.pdf
```

### 跨浏览器测试

```bash
# 使用 pytest 和 Playwright 进行跨浏览器测试
pytest tests/test_browser.py --browser=chromium
pytest tests/test_browser.py --browser=firefox

# 或使用 Selenium 进行兼容性测试
pytest tests/test_selenium.py
```

### API 兼容性测试

```bash
# 测试 API 版本兼容性
curl -H "API-Version: v1" http://cloud-doors.com:5000/api/users
curl -H "API-Version: v2" http://cloud-doors.com:5000/api/users

# 测试响应格式
curl -H "Accept: application/json" http://cloud-doors.com:5000/api/data
curl -H "Accept: application/xml" http://cloud-doors.com:5000/api/data
```

### 集成测试清单

- [ ] 用户注册登录流程正常
- [ ] 工单系统完整流程正常
- [ ] 知识库搜索下载正常
- [ ] 跨浏览器兼容性正常
- [ ] API 兼容性正常
- [ ] 系统间数据一致性正常
- [ ] 无功能回归问题

---

## 性能测试

### 响应时间测试

```bash
# 测试应用响应时间
for i in {1..10}; do
  time curl http://cloud-doors.com:5000/health
  sleep 1
done

# 测试 Webhook 响应时间
for i in {1..10}; do
  time curl http://cloud-doors.com:9000/webhook/health
  sleep 1
done

# 计算平均响应时间
# 平均响应时间应 < 1 秒
```

### 并发测试

```bash
# 使用 Apache Bench 进行并发测试
ab -n 1000 -c 10 http://cloud-doors.com:5000/

# 或使用 wrk
wrk -t 30 -c 10 http://cloud-doors.com:5000/

# 预期结果
# 请求/秒: > 50
# 失败率: < 1%
# 95% 百分位响应时间: < 500ms
```

### 负载测试

```bash
# 使用 Locust 进行负载测试
locust -f locustfile.py --host=http://cloud-doors.com:5000 --users=50 --spawn-rate=10 --run-time=1m

# 监控指标
# 平均响应时间
# RPS (每秒请求数)
# 失败率
```

### 资源使用监控

```bash
# 监控 CPU 使用
top -b -n 1 | grep app.py

# 监控内存使用
ps aux | grep app.py | awk '{print $6}'

# 监控网络使用
netstat -tuln | grep 5000

# 监控磁盘 I/O
iostat -x 1 5
```

### 性能测试清单

- [ ] 应用响应时间 < 1 秒
- [ ] Webhook 响应时间 < 1 秒
- [ ] 并发处理能力 > 50 req/s
- [ ] 负载测试失败率 < 1%
- [ ] CPU 使用 < 80%
- [ ] 内存使用 < 80%
- [ ] 无内存泄漏
- [ ] 数据库查询优化
- [ ] 静态资源加载优化

---

## 测试报告

### 测试报告模板

```markdown
# CI/CD 测试报告

**测试日期**: 2026-03-04
**测试人员**: [姓名]
**测试环境**: [开发/测试/生产]

## 测试概览

| 测试类型 | 测试用例数 | 通过数 | 失败数 | 通过率 |
|---------|----------|-------|--------|--------|
| 单元测试 | 50 | 50 | 0 | 100% |
| 集成测试 | 20 | 19 | 1 | 95% |
| 部署测试 | 5 | 5 | 0 | 100% |
| 回滚测试 | 3 | 3 | 0 | 100% |
| 性能测试 | 10 | 10 | 0 | 100% |

## 详细测试结果

### 单元测试
- ✅ 所有测试通过
- ✅ 覆盖率: 85%
- ✅ 无严重问题

### 集成测试
- ✅ 用户注册流程正常
- ✅ 工单提交流程正常
- ✅ 知识库功能正常
- ⚠️ 回滚功能有 1 个小问题

### 部署测试
- ✅ Webhook 触发正常
- ✅ 部署流程完成
- ✅ 备份机制正常
- ✅ 回滚功能正常

### 性能测试
- ✅ 响应时间达标
- ✅ 并发能力达标
- ⚠️ 高负载下响应稍慢

## 问题和建议

### 发现的问题
1. 回滚时有个别文件权限问题
   - 影响范围: 中
   - 状态: 已记录

### 改进建议
1. 优化高负载下的响应时间
2. 增加性能自动化测试
3. 完善回滚后的权限修复

## 测试结论

✅ 所有核心功能测试通过
✅ CI/CD 流程验证成功
✅ 部署机制稳定可靠
✅ 回滚功能正常
⚠️ 发现 1 个小问题，建议后续优化

**总体评价**: 通过
```

### 自动化测试报告

```bash
# 生成测试报告
pytest tests/ --html=reports/test-report.html --self-contained-html

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html --html=reports/coverage-report.html

# 打开报告
open reports/test-report.html
open reports/coverage-report.html
```

### 测试数据收集

```bash
# 收集测试指标
pytest tests/ -v --tb=no 2>&1 | tee test_results.log

# 解析测试结果
grep -E "PASSED|FAILED|ERROR" test_results.log

# 生成统计报告
python scripts/generate_test_report.py test_results.log
```

---

## 测试最佳实践

### 测试原则

1. **测试驱动开发 (TDD)**
   - 先写测试，再写代码
   - 确保每个功能都有测试

2. **金字塔原则**
   - 大量单元测试（70%）
   - 适量集成测试（20%）
   - 少量端到端测试（10%）

3. **独立性**
   - 每个测试独立运行
   - 不依赖其他测试
   - 不依赖外部状态

4. **可重复性**
   - 测试结果稳定
   - 不随机失败
   - 相同输入相同输出

### CI/CD 测试规范

1. **测试自动化**
   - 所有测试集成到 CI/CD
   - 自动化执行，无需手动
   - 结果自动上报

2. **快速反馈**
   - 测试 < 5 分钟完成
   - 失败立即告警
   - 修复后快速验证

3. **持续监控**
   - 监控测试通过率
   - 监控部署成功率
   - 及时发现和修复问题

---

<div align="center">

**文档版本**: v1.0  
**创建日期**: 2026-03-04  
**维护者**: 云户科技技术团队

</div>
