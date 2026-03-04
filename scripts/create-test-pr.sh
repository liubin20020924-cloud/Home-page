#!/bin/bash

# 创建测试 PR 脚本

set -e

# 配置
REPO="liubin20020924-cloud/Home-page"
SOURCE_BRANCH="feat/cicd-test-20260304-001"
TARGET_BRANCH="main"
TITLE="测试CI/CD流程"
LABELS='["auto-merge","test"]'

PR_BODY="## CI/CD 流程测试

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
**自动化测试** - 请不要人工合并，等待 CI/CD 检查通过后自动合并。"

# 检查是否配置了 GitHub Token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "错误: 未设置 GITHUB_TOKEN 环境变量"
    echo "请设置: export GITHUB_TOKEN=your_github_token"
    exit 1
fi

echo "正在创建 Pull Request..."
echo "源分支: $SOURCE_BRANCH"
echo "目标分支: $TARGET_BRANCH"

# 创建 PR
RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/pulls" \
  -d "{
    \"title\": \"$TITLE\",
    \"head\": \"$SOURCE_BRANCH\",
    \"base\": \"$TARGET_BRANCH\",
    \"body\": \"$PR_BODY\",
    \"labels\": $LABELS
  }")

# 检查是否创建成功
PR_URL=$(echo "$RESPONSE" | grep -o '"html_url":"[^"]*' | cut -d'"' -f4)
PR_NUMBER=$(echo "$RESPONSE" | grep -o '"number":[0-9]*' | cut -d':' -f2)

if [ -n "$PR_URL" ]; then
    echo "✅ Pull Request 创建成功!"
    echo "PR URL: $PR_URL"
    echo "PR 编号: #$PR_NUMBER"
    echo ""
    echo "📌 标签: auto-merge, test"
    echo "🔄 CI/CD 检查将自动开始..."
    echo ""
    echo "请访问以下链接查看 CI/CD 流程："
    echo "https://github.com/$REPO/pull/$PR_NUMBER"
else
    echo "❌ 创建 Pull Request 失败"
    echo "响应: $RESPONSE"
    exit 1
fi
