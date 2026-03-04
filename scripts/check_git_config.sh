#!/bin/bash

# Git 配置检查和诊断脚本

set -e

# 配置
PROJECT_DIR="/opt/Home-page"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Git 配置检查和诊断${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 检查 Git 全局配置
echo -e "${GREEN}1. Git 全局配置:${NC}"
echo "----------------------------------------"

if git config --global --list &> /dev/null; then
    echo "Git 全局配置:"
    git config --global --list | sed 's/^/  /'
else
    echo "未找到 Git 全局配置"
fi

echo ""

# 2. 检查代理配置
echo -e "${GREEN}2. 代理配置:${NC}"
echo "----------------------------------------"

HTTP_PROXY=$(git config --global --get http.proxy 2>/dev/null || echo "未配置")
HTTPS_PROXY=$(git config --global --get https.proxy 2>/dev/null || echo "未配置")
GITHUB_PROXY=$(git config --global --get http.https://github.com.proxy 2>/dev/null || echo "未配置")

echo "HTTP 代理:  $HTTP_PROXY"
echo "HTTPS 代理: $HTTPS_PROXY"
echo "GitHub 代理:  $GITHUB_PROXY"

if [ "$HTTP_PROXY" != "未配置" ] || [ "$HTTPS_PROXY" != "未配置" ] || [ "$GITHUB_PROXY" != "未配置" ]; then
    log_info "代理已配置"
else
    log_warn "未配置代理,可能无法访问 GitHub"
fi

echo ""

# 3. 检查远程仓库配置
echo -e "${GREEN}3. 远程仓库配置:${NC}"
echo "----------------------------------------"

if git remote -v &> /dev/null; then
    git remote -v
else
    log_error "未配置远程仓库"
fi

echo ""

# 4. 检查当前分支
echo -e "${GREEN}4. 当前分支:${NC}"
echo "----------------------------------------"

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "未检出分支")
echo "当前分支: $CURRENT_BRANCH"

echo ""

# 5. 检查最新提交
echo -e "${GREEN}5. 最新提交:${NC}"
echo "----------------------------------------"

LATEST_COMMIT=$(git log -1 --format='%h' 2>/dev/null || echo "N/A")
LATEST_MESSAGE=$(git log -1 --format='%s' 2>/dev/null || echo "N/A")
LATEST_TIME=$(git log -1 --format='%ci' 2>/dev/null || echo "N/A")

echo "提交 SHA:   $LATEST_COMMIT"
echo "提交信息:   $LATEST_MESSAGE"
echo "提交时间:   $LATEST_TIME"

echo ""

# 6. 测试 GitHub 连接
echo -e "${GREEN}6. 测试 GitHub 连接:${NC}"
echo "----------------------------------------"

if [ "$GITHUB_PROXY" != "未配置" ]; then
    PROXY_CMD="--proxy $GITHUB_PROXY"
else
    PROXY_CMD=""
fi

echo "测试 GitHub API..."
if curl $PROXY_CMD -I --connect-timeout 10 https://api.github.com &> /dev/null 2>&1; then
    log_info "✓ GitHub API 连接成功"
    GITHUB_STATUS="正常"
else
    log_error "✗ GitHub API 连接失败"
    GITHUB_STATUS="失败"
fi

echo ""

# 7. 测试 Git 拉取
echo -e "${GREEN}7. 测试 Git 拉取:${NC}"
echo "----------------------------------------"

echo "测试拉取 (dry-run)..."
if git fetch origin --dry-run $PROXY_CMD &> /dev/null 2>&1; then
    log_info "✓ Git 拉取测试成功"
    GIT_FETCH_STATUS="正常"
else
    log_error "✗ Git 拉取测试失败"
    GIT_FETCH_STATUS="失败"
fi

echo ""

# 8. 测试代理连接
echo -e "${GREEN}8. 测试代理连接:${NC}"
echo "----------------------------------------"

if [ "$HTTP_PROXY" != "未配置" ] || [ "$HTTPS_PROXY" != "未配置" ]; then
    PROXY_FOR_TEST="${HTTP_PROXY:-$HTTPS_PROXY}"
    echo "测试代理: $PROXY_FOR_TEST"

    # 提取代理服务器地址
    PROXY_SERVER=$(echo $PROXY_FOR_TEST | sed 's|.*://||' | cut -d: -f1)

    echo "测试代理服务器: $PROXY_SERVER"

    if timeout 5 nc -zv -w5 "$PROXY_SERVER" 443 &> /dev/null 2>&1; then
        log_info "✓ 代理连接正常"
        PROXY_STATUS="正常"
    else
        log_warn "✗ 代理连接超时"
        PROXY_STATUS="异常"
    fi
else
    log_warn "未配置代理"
    PROXY_STATUS="未配置"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}诊断结果总结${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 9. 诊断总结
echo -e "${GREEN}配置状态:${NC}"
echo "----------------------------------------"
echo "代理配置:     $PROXY_STATUS"
echo "GitHub 连接:   $GITHUB_STATUS"
echo "Git 拉取:     $GIT_FETCH_STATUS"
echo "远程仓库:     已配置"
echo "----------------------------------------"
echo ""

# 10. 建议和修复建议
echo -e "${GREEN}建议和修复:${NC}"
echo "----------------------------------------"

if [ "$PROXY_STATUS" = "正常" ] && [ "$GITHUB_STATUS" = "正常" ] && [ "$GIT_FETCH_STATUS" = "正常" ]; then
    log_info "✓ 配置正常,CI/CD 流程应该可以正常工作"
else
    log_warn "存在以下问题:"
    [ "$PROXY_STATUS" = "异常" ] && echo "  - 代理连接异常,请检查代理服务"
    [ "$PROXY_STATUS" = "未配置" ] && echo "  - 未配置代理,请参考 docs/PROXY_QUICK_START.md"
    [ "$GITHUB_STATUS" = "失败" ] && echo "  - GitHub 连接失败,请检查网络或代理"
    [ "$GIT_FETCH_STATUS" = "失败" ] && echo "  - Git 拉取失败,请检查代理配置"
    echo ""
    echo "修复建议:"
    echo "  1. 检查代理服务是否正常运行"
    echo "  2. 验证代理地址和端口是否正确"
    echo "  3. 尝试手动测试代理连接"
    echo "  4. 检查防火墙设置"
    echo "  5. 参考文档: docs/PROXY_SETUP.md"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}检查完成!${NC}"
echo -e "${BLUE}========================================${NC}"
