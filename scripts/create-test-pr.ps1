# 创建测试 PR 脚本 (PowerShell)

$ErrorActionPreference = "Stop"

# 配置
$repo = "liubin20020924-cloud/Home-page"
$sourceBranch = "feat/cicd-test-20260304-001"
$targetBranch = "main"
$title = "测试CI/CD流程"
$labels = @("auto-merge", "test")

$prBody = @"
## CI/CD 流程测试

此 PR 用于测试完整的 CI/CD 自动化流程。

### 测试步骤
1. ✅ 代码推送到功能分支
2. ⏳ 创建 PR 并添加 auto-merge 标签
3. ⏳ 触发 CI/CD 检查（测试、代码检查、安全检查）
4. ⏳ 检查通过后自动合并到 main
5. ⏳ main 分支更新触发云主机部署
6. ⏳ 验证部署成功

### 预期结果
- 所有 CI/CD 检查通过
- PR 自动合并到 main 分支
- 云主机收到部署通知并执行部署
- 部署日志记录完整

---
**自动化测试** - 请不要人工合并，等待 CI/CD 检查通过后自动合并。
"@

# 检查是否配置了 GitHub Token
$githubToken = $env:GITHUB_TOKEN
if ([string]::IsNullOrEmpty($githubToken)) {
    Write-Error "错误: 未设置 GITHUB_TOKEN 环境变量"
    Write-Host "请设置: `$env:GITHUB_TOKEN = 'your_github_token'" -ForegroundColor Yellow
    exit 1
}

Write-Host "正在创建 Pull Request..." -ForegroundColor Green
Write-Host "源分支: $sourceBranch" -ForegroundColor Cyan
Write-Host "目标分支: $targetBranch" -ForegroundColor Cyan

# 创建请求体
$bodyJson = @{
    title = $title
    head = $sourceBranch
    base = $targetBranch
    body = $prBody
    labels = $labels
} | ConvertTo-Json

# 创建 PR
$headers = @{
    "Authorization" = "token $githubToken"
    "Accept" = "application/vnd.github.v3+json"
}

try {
    $response = Invoke-RestMethod `
        -Uri "https://api.github.com/repos/$repo/pulls" `
        -Method Post `
        -Headers $headers `
        -Body $bodyJson `
        -ContentType "application/json"

    $prUrl = $response.html_url
    $prNumber = $response.number

    Write-Host "✅ Pull Request 创建成功!" -ForegroundColor Green
    Write-Host "PR URL: $prUrl" -ForegroundColor Cyan
    Write-Host "PR 编号: #$prNumber" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📌 标签: auto-merge, test" -ForegroundColor Yellow
    Write-Host "🔄 CI/CD 检查将自动开始..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请访问以下链接查看 CI/CD 流程：" -ForegroundColor Yellow
    Write-Host "https://github.com/$repo/pull/$prNumber" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "或者直接点击:" -ForegroundColor Yellow
    Write-Host $prUrl -ForegroundColor Cyan

} catch {
    Write-Error "创建 Pull Request 失败: $_"
    exit 1
}
