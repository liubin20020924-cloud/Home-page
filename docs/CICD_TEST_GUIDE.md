# CI/CD 测试指南

## 测试步骤

### 1. 代码已推送到 GitHub ✅

分支: `feat/cicd-test-20260304-001`
提交: "test(ci-cd): 添加CI/CD部署测试文件"

### 2. 手动创建 Pull Request

请通过以下方式创建 PR：

#### 方式 A: 通过 GitHub 网页（推荐）

1. 访问以下链接创建 PR：
   ```
   https://github.com/liubin20020924-cloud/Home-page/pull/new/feat/cicd-test-20260304-001
   ```

2. 填写 PR 信息：
   - **Title**: 测试CI/CD流程
   - **Base**: main
   - **Compare**: feat/cicd-test-20260304-001

3. 添加标签：
   - 点击右侧 "Labels"
   - 选择 `auto-merge`
   - 选择 `test`

4. 提交 PR

#### 方式 B: 使用 PowerShell 脚本

```powershell
# 设置 GitHub Token
$env:GITHUB_TOKEN = "your_github_token_here"

# 运行脚本
cd e:/Home-page
powershell -ExecutionPolicy Bypass -File scripts/create-test-pr.ps1
```

### 3. 查看 CI/CD 检查状态

创建 PR 后，GitHub Actions 会自动执行以下检查：

| 检查项 | 状态 | 链接 |
|-------|------|------|
| Run Tests | ⏳ 待运行 | 查看 Actions |
| Code Lint | ⏳ 待运行 | 查看 Actions |
| Security Check | ⏳ 待运行 | 查看 Actions |

访问 Actions 页面：
```
https://github.com/liubin20020924-cloud/Home-page/actions
```

### 4. 验证自动合并

PR 创建后：

1. 等待所有 CI/CD 检查通过（约 5-10 分钟）
2. PR 会自动合并到 main 分支
3. 合并后会触发云主机部署

### 5. 验证云主机部署

main 分支更新后，检查部署状态：

#### 查看部署版本
```bash
curl http://your-server:9000/webhook/version
```

#### 查看部署日志
```bash
curl http://your-server:9000/webhook/logs
```

#### SSH 登录查看
```bash
ssh user@your-server
tail -f /var/log/integrate-code/deploy.log
```

### 6. 预期结果

完整流程验证清单：

- [ ] 1. 代码成功推送到 GitHub
- [ ] 2. PR 创建成功，包含 auto-merge 和 test 标签
- [ ] 3. GitHub Actions 开始运行
- [ ] 4. Run Tests 检查通过
- [ ] 5. Code Lint 检查通过
- [ ] 6. Security Check 检查通过
- [ ] 7. PR 自动合并到 main 分支
- [ ] 8. 云主机收到 Webhook 通知
- [ ] 9. 部署脚本执行成功
- [ ] 10. 应用服务重启成功
- [ ] 11. 部署日志记录完整
- [ ] 12. 版本信息更新

## 常见问题

### Q: CI/CD 检查失败怎么办？

A:
1. 点击失败的检查项查看详细日志
2. 修复问题后提交新的 commit
3. PR 会自动重新触发检查

### Q: PR 没有自动合并？

A:
1. 确认 PR 添加了 `auto-merge` 标签
2. 确认所有 CI/CD 检查都通过了
3. 检查 GitHub Actions 是否有权限自动合并

### Q: 云主机没有收到部署通知？

A:
1. 检查 GitHub Secrets 是否配置了 `WEBHOOK_URL`
2. 检查云主机防火墙是否开放 9000 端口
3. 检查 webhook 服务是否运行：`systemctl status webhook-receiver`

### Q: 部署失败怎么办？

A:
1. 查看部署日志：`tail -f /var/log/integrate-code/deploy.log`
2. 执行回滚：`cd /opt/Home-page && ./scripts/rollback.sh`
3. 修复问题后重新部署

## 测试完成后的清理

测试完成后，可以删除测试分支：

```bash
git checkout main
git branch -d feat/cicd-test-20260304-001
git push origin --delete feat/cicd-test-20260304-001
```

---

**测试时间**: 2026-03-04
**测试分支**: feat/cicd-test-20260304-001
**测试状态**: 进行中
