#!/bin/bash

# CI/CD 部署验证脚本

echo "======================================"
echo "CI/CD 部署验证"
echo "======================================"
echo ""

# 1. 检查部署日志
echo "1. 检查最近部署日志..."
if [ -f "/var/log/integrate-code/deploy.log" ]; then
    tail -20 /var/log/integrate-code/deploy.log
    echo ""
else
    echo "❌ 部署日志文件不存在"
    echo ""
fi

# 2. 检查版本信息
echo "2. 检查版本信息..."
if [ -f "/opt/Home-page/.version_info.json" ]; then
    cat /opt/Home-page/.version_info.json
    echo ""
else
    echo "❌ 版本信息文件不存在"
    echo ""
fi

# 3. 检查服务状态
echo "3. 检查应用服务状态..."
systemctl status integrate-code --no-pager
echo ""

# 4. 检查当前 Git 提交
echo "4. 检查当前代码版本..."
if [ -d "/opt/Home-page/.git" ]; then
    cd /opt/Home-page
    git log -1 --oneline --decorate
    echo ""
else
    echo "❌ Git 仓库不存在"
    echo ""
fi

# 5. 检查备份
echo "5. 检查最近备份..."
if [ -d "/opt/Home-page/backups" ]; then
    ls -lht /opt/Home-page/backups | head -5
    echo ""
else
    echo "❌ 备份目录不存在"
    echo ""
fi

# 6. 检查 webhook 服务
echo "6. 检查 webhook 服务状态..."
systemctl status webhook-receiver --no-pager
echo ""

# 7. 检查端口监听
echo "7. 检查端口监听状态..."
netstat -tlnp | grep -E ':(5000|9000)' || echo "❌ 端口 5000/9000 未监听"
echo ""

echo "======================================"
echo "验证完成"
echo "======================================"
