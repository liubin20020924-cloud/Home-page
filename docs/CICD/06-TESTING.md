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
- [ ] 集成测试全部通过
- [ ] 手动测试关键功能

---

## CI 测试

### GitHub Actions 测试

#### 1. 代码检查测试

```yaml
# .github/workflows/ci-cd.yml
- name: Code Check
  run: |
    python -m py_compile app.py routes/ services/
    flake8 --max-line-length=120 routes/
```

**测试内容：**
- ✅ Python 语法正确性
- ✅ 代码风格符合 PEP 8
- ✅ 无明显的代码问题

#### 2. 单元测试

```yaml
- name: Run Tests
  run: |
    pip install -r requirements-dev.txt
    pytest tests/ -v --cov=. --cov-report=xml
```

**测试内容：**
- ✅ 所有单元测试通过
- ✅ 测试覆盖率达标
- ✅ 无测试失败或跳过

#### 3. 代码质量检查

```yaml
- name: Code Quality
  run: |
    pip install pylint
    pylint app.py routes/ services/ --max-line-length=120
```

**测试内容：**
- ✅ 代码质量评分 > 8.0
- ✅ 无严重质量问题
- ✅ 无潜在的 bug

#### 4. 安全扫描

```yaml
- name: Security Scan
  run: |
    pip install bandit
    bandit -r app/ routes/ services/ -f json -o security-report.json
```

**测试内容：**
- ✅ 无高风险漏洞
- ✅ 无中风险漏洞（除非确认可接受）
- ✅ 安全问题已修复或记录

### CI 测试清单

- [ ] 代码检查通过
- [ ] 单元测试全部通过
- [ ] 测试覆盖率 > 80%
- [ ] 代码质量检查通过
- [ ] 安全扫描无高风险
- [ ] CI workflow 执行时间 < 10 分钟
- [ ] 所有 artifact 正常生成

---

## CD 测试

### SSH 部署测试

#### 1. SSH 连接测试

```bash
# 测试 SSH 密钥配置
ssh -i ~/.ssh/github_actions_key root@cloud-doors.com "echo 'SSH OK'"

# 预期输出
# SSH OK
```

**测试内容：**
- ✅ SSH 密钥配置正确
- ✅ 连接云主机成功
- ✅ 认证方式正确

#### 2. 部署脚本测试

```bash
# SSH 登录云主机
ssh root@cloud-doors.com

# 进入项目目录
cd /opt/Home-page

# 手动执行部署脚本
bash scripts/deploy.sh

# 查看部署日志
tail -f /var/log/integrate-code/deploy.log
```

**测试内容：**
- ✅ 备份创建成功
- ✅ 代码拉取成功
- ✅ 依赖更新成功
- ✅ 服务重启成功
- ✅ 健康检查通过

### 部署验证

#### 1. 验证代码更新

```bash
# SSH 登录云主机
ssh root@cloud-doors.com

# 查看最新提交
cd /opt/Home-page
git log -1

# 验证文件更新
ls -la
```

**验证内容：**
- ✅ Git 记录显示最新提交
- ✅ 文件修改时间正确
- ✅ 新文件已存在

#### 2. 验证服务状态

```bash
# 查看服务状态
sudo systemctl status Home-page

# 验证进程运行
ps aux | grep app.py

# 查看服务日志
sudo journalctl -u Home-page -n 50
```

**验证内容：**
- ✅ 服务状态为 active (running)
- ✅ 进程正在运行
- ✅ 日志无错误

#### 3. 验证应用可访问

```bash
# 测试本地访问
curl http://localhost:5000

# 测试外部访问
curl http://cloud-doors.com:5000

# 测试健康检查
curl http://cloud-doors.com:5000/health
```

**验证内容：**
- ✅ HTTP 响应状态码 200
- ✅ 页面内容正常
- ✅ 健康检查返回 OK

### 回滚测试

```bash
# 1. 列出可用备份
ls -lt /var/backups/Home-page/

# 2. 选择一个备份
BACKUP_NAME="Home-page_20260304_120000"

# 3. 执行回滚
cd /opt/Home-page
bash scripts/rollback.sh $BACKUP_NAME

# 4. 验证回滚成功
git log -1
curl http://localhost:5000
```

**测试内容：**
- ✅ 备份文件存在
- ✅ 回滚脚本执行成功
- ✅ 代码已恢复到备份版本
- ✅ 服务正常运行

### CD 测试清单

- [ ] SSH 连接测试通过
- [ ] 部署脚本测试通过
- [ ] 备份创建成功
- [ ] 代码拉取成功
- [ ] 依赖更新成功
- [ ] 服务重启成功
- [ ] 应用可正常访问
- [ ] 健康检查通过
- [ ] 回滚功能正常
- [ ] 部署时间 < 5 分钟

---

## 集成测试

### 端到端测试流程

#### 测试 1: 完整部署流程

1. **本地代码修改**
   ```bash
   # 修改测试文件
   echo "# Test $(date)" >> README.md
   
   # 提交并推送
   git add README.md
   git commit -m "test: integration test"
   git push origin main
   ```

2. **观察 GitHub Actions**
   - 访问 Actions 页面
   - 查看 workflow 执行状态
   - 查看日志输出

3. **验证云主机部署**
   ```bash
   # SSH 登录
   ssh root@cloud-doors.com
   
   # 验证代码更新
   cd /opt/Home-page
   git log -1
   tail README.md
   ```

4. **验证应用功能**
   ```bash
   # 测试应用访问
   curl http://cloud-doors.com:5000
   
   # 测试关键功能
   curl http://cloud-doors.com:5000/kb
   curl http://cloud-doors.com:5000/case
   ```

**预期结果：**
- ✅ GitHub Actions 自动触发
- ✅ CI 测试全部通过
- ✅ SSH 部署成功执行
- ✅ 云主机代码已更新
- ✅ 应用功能正常

#### 测试 2: 部署失败恢复

1. **模拟部署失败**
   ```bash
   # SSH 登录
   ssh root@cloud-doors.com
   
   # 修改部署脚本制造失败
   cd /opt/Home-page
   echo "exit 1" >> scripts/deploy.sh
   ```

2. **触发部署**
   ```bash
   # 本地提交
   echo "# Test failure" >> README.md
   git add .
   git commit -m "test: deploy failure"
   git push origin main
   ```

3. **观察失败**
   - GitHub Actions 显示失败
   - 云主机代码未更新

4. **修复并重新部署**
   ```bash
   # SSH 登录
   ssh root@cloud-doors.com
   
   # 恢复部署脚本
   git checkout scripts/deploy.sh
   
   # 重新部署
   bash scripts/deploy.sh
   ```

**预期结果：**
- ✅ 部署失败能被检测
- ✅ 修复后能成功部署
- ✅ 不影响系统稳定性

### 集成测试清单

- [ ] 完整部署流程正常
- [ ] 失败场景处理正确
- [ ] 回滚机制有效
- [ ] 所有系统集成正常
- [ ] 错误日志记录完整
- [ ] 监控告警正常

---

## 性能测试

### 部署性能

```bash
# 测量部署时间
time bash scripts/deploy.sh

# 记录各阶段耗时
START_TIME=$(date +%s)
# ... 部署过程 ...
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo "部署耗时: ${ELAPSED} 秒"
```

**性能指标：**
- ✅ 部署总时间 < 5 分钟
- ✅ 备份时间 < 30 秒
- ✅ 代码拉取 < 2 分钟
- ✅ 依赖更新 < 1 分钟
- ✅ 服务重启 < 30 秒

### 应用性能

```bash
# 测试响应时间
for i in {1..10}; do
  curl -w "@curl-format.txt" -o /dev/null -s http://cloud-doors.com:5000
done

# curl-format.txt 内容
# time_namelookup:  %{time_namelookup}\n
# time_connect:     %{time_connect}\n
# time_appconnect:  %{time_appconnect}\n
# time_pretransfer: %{time_pretransfer}\n
# time_starttransfer: %{time_starttransfer}\n
# ----------\n
# time_total:      %{time_total}\n
```

**性能指标：**
- ✅ 平均响应时间 < 500ms
- ✅ 最大响应时间 < 2s
- ✅ 99% 请求 < 1s

---

## 测试报告

### 自动化报告

#### 覆盖率报告

```bash
# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html --cov-report=xml

# 查看报告
open htmlcov/index.html

# 上传到 Codecov
# 在 GitHub Actions 中自动上传
```

报告包含：
- 总体覆盖率
- 每个文件的覆盖率
- 未覆盖的代码行
- 覆盖趋势

#### 安全报告

```bash
# 生成安全报告
bandit -r app/ routes/ services/ -f json -o security-report.json

# 查看报告
cat security-report.json
```

报告包含：
- 高风险漏洞
- 中风险漏洞
- 低风险漏洞
- 修复建议

### 手动测试报告

创建测试报告模板：

```markdown
# 部署测试报告

## 测试环境
- 测试时间: 2026-03-05 10:00
- 测试人员: xxx
- 云主机: cloud-doors.com
- Git 版本: xxxxx

## 测试项目

### CI 测试
- [x] 代码检查
- [x] 单元测试
- [x] 代码质量
- [x] 安全扫描

### CD 测试
- [x] SSH 连接
- [x] 部署脚本
- [x] 服务重启
- [x] 健康检查

### 集成测试
- [x] 完整流程
- [x] 回滚测试
- [x] 性能测试

## 测试结果
- 总测试数: 10
- 通过数: 10
- 失败数: 0
- 通过率: 100%

## 问题和建议
- 无

## 结论
部署系统运行正常，可以投入使用。
```

---

## 测试最佳实践

### 测试原则

1. **自动化优先**
   - 自动化所有可自动化的测试
   - 集成到 CI/CD 流程
   - 定期更新测试用例

2. **覆盖全面**
   - 覆盖所有核心功能
   - 覆盖边界条件
   - 覆盖错误场景

3. **快速反馈**
   - 单元测试快速执行
   - CI 结果及时通知
   - 问题立即报告

4. **可重复性**
   - 测试环境一致
   - 测试数据稳定
   - 测试结果可重现

### 测试建议

1. **本地充分测试**
   - 推送前本地运行所有测试
   - 确保测试通过再推送
   - 减少 CI 失败率

2. **持续改进**
   - 定期审查测试覆盖率
   - 优化慢速测试
   - 移除过时的测试

3. **文档记录**
   - 记录测试用例
   - 记录已知问题
   - 记录测试结果

---

## 相关文档

- [CI/CD 快速使用指南](./00-QUICK_START.md)
- [CI/CD 完整介绍](./01-INTRODUCTION.md)
- [CI/CD 配置指南](./02-CONFIGURATION.md)
- [CI/CD 部署历史](./03-DEPLOYMENT_HISTORY.md)
- [CI/CD 功能设计](./04-FEATURES.md)
- [CI/CD 故障排除](./05-TROUBLESHOOTING.md)

---

<div align="center">

**文档版本**: v2.0
**创建日期**: 2026-03-04
**最后更新**: 2026-03-05
**维护者**: 云户科技技术团队

</div>
