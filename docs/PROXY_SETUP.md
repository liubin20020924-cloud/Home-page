# 云主机代理配置指南

## 概述

由于 GitHub 在国内访问不稳定,云主机需要配置代理来稳定拉取代码。

## 方案选择

### 方案 1: 使用 HTTP/HTTPS 代理 (推荐)

#### 1.1 购买或获取代理服务

推荐使用的代理服务商:
- 蚁链 (AntLink)
- 芝麻代理
- 快代理
- 自建代理服务器

#### 1.2 配置 Git 使用代理

```bash
# 在云主机上配置
cd /opt/Home-page

# 设置 HTTP 代理
git config --global http.proxy http://proxy-server:port

# 设置 HTTPS 代理
git config --global https.proxy http://proxy-server:port

# 验证配置
git config --global --get http.proxy
git config --global --get https.proxy
```

#### 1.3 测试代理连接

```bash
# 测试 GitHub 连接
curl --proxy http://proxy-server:port https://github.com

# 测试 Git 拉取
git fetch origin
```

### 方案 2: 使用 SSH 代理

#### 2.1 配置 SSH 代理

```bash
# 编辑 SSH 配置文件
vim ~/.ssh/config

# 添加以下内容:
Host github.com
    ProxyCommand nc -X connect -x proxy-server:port %h %p
    User git
    Port 22
```

#### 2.2 使用 SSH 地址

```bash
# 修改远程仓库为 SSH 地址
git remote set-url origin git@github.com:liubin20020924-cloud/Home-page.git
```

### 方案 3: 使用 GitHub 镜像 (临时方案)

不推荐长期使用,但可以作为临时解决方案:

```bash
# 修改 hosts 文件 (不推荐,可能失效)
sudo vim /etc/hosts
# 添加: 20.205.243.166 github.com
```

## 推荐配置: HTTP 代理

### 1. 配置系统代理

```bash
# 设置环境变量
export http_proxy=http://proxy-server:port
export https_proxy=http://proxy-server:port
export no_proxy=localhost,127.0.0.1,10.0.0.0/8

# 添加到 .bashrc 或 .zshrc 持久化
echo "export http_proxy=http://proxy-server:port" >> ~/.bashrc
echo "export https_proxy=http://proxy-server:port" >> ~/.bashrc
```

### 2. 配置 Git 代理

```bash
# 全局配置
git config --global http.proxy http://proxy-server:port
git config --global https.proxy http://proxy-server:port

# 仅对 GitHub 配置 (推荐)
git config --global http.https://github.com.proxy http://proxy-server:port
```

### 3. 配置 Python pip 代理

```bash
# 在 .env 文件中添加
HTTP_PROXY=http://proxy-server:port
HTTPS_PROXY=http://proxy-server:port
NO_PROXY=localhost,127.0.0.1,10.0.0.0/8
```

### 4. 配置 Docker 代理 (如果使用)

```bash
# 创建或编辑 Docker 配置
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo vim /etc/systemd/system/docker.service.d/http-proxy.conf

# 添加:
[Service]
Environment="HTTP_PROXY=http://proxy-server:port"
Environment="HTTPS_PROXY=http://proxy-server:port"
Environment="NO_PROXY=localhost,127.0.0.1"

# 重启 Docker
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## 部署脚本配置

### 更新 deploy.sh 使用代理

编辑 `/opt/Home-page/scripts/deploy.sh`:

```bash
# 在脚本开头添加代理配置
export http_proxy=http://proxy-server:port
export https_proxy=http://proxy-server:port
export no_proxy=localhost,127.0.0.1,10.0.0.0/8

# 或只在 Git 操作时使用
git -c http.proxy=http://proxy-server:port fetch origin
```

### 更新 smart-pull.sh 使用代理

脚本已更新为检测 GitHub 速度,如果速度慢则报错。需要配置代理后才能正常拉取。

## 代理服务推荐

### 付费代理 (稳定可靠)

| 服务商 | 价格 | 特点 |
|--------|------|------|
| 蚁链 AntLink | 按流量计费 | 稳定,速度快 |
| 芝麻代理 | 按流量计费 | IP多,切换灵活 |
| 快代理 | 按流量计费 | 节点多 |

### 免费代理 (不推荐生产使用)

- 只用于测试
- 稳定性差
- 速度慢
- 可能存在安全风险

## 安全建议

1. **使用可信的代理服务**
   - 选择知名服务商
   - 避免使用免费代理

2. **配置白名单**
   - 只代理必要的域名
   - 配置 `no_proxy` 排除内网地址

3. **定期更换代理**
   - 定期评估代理服务质量
   - 准备备用代理

4. **监控代理状态**
   - 监控代理可用性
   - 监控连接速度
   - 设置告警

## 故障排查

### 问题1: Git 拉取超时

**解决方案**:
```bash
# 增加超时时间
git config --global http.timeout 300
git config --global http.lowSpeedLimit 0
git config --global http.postBuffer 524288000

# 测试代理
curl --proxy http://proxy-server:port https://api.github.com
```

### 问题2: 代理认证失败

**解决方案**:
```bash
# 如果代理需要认证
git config --global http.proxy http://username:password@proxy-server:port

# 或使用环境变量
export http_proxy=http://username:password@proxy-server:port
```

### 问题3: SSL 证书错误

**解决方案**:
```bash
# 跳过 SSL 验证 (不推荐,仅测试使用)
git config --global http.sslVerify false

# 或更新 CA 证书
sudo apt-get install ca-certificates  # Ubuntu/Debian
sudo yum install ca-certificates      # CentOS/RHEL
```

### 问题4: 代理连接不稳定

**解决方案**:
```bash
# 配置代理重试
git config --global http.lowSpeedTime 999999
git config --global http.lowSpeedLimit 0

# 使用多个代理轮换 (需要编写脚本)
```

## 监控和日志

### 监控代理可用性

```bash
# 创建监控脚本
vim /opt/scripts/check-proxy.sh

# 内容:
#!/bin/bash
PROXY="http://proxy-server:port"
if curl --proxy "$PROXY" --connect-timeout 5 https://github.com > /dev/null 2>&1; then
    echo "Proxy OK: $(date)" >> /var/log/proxy-status.log
else
    echo "Proxy FAIL: $(date)" >> /var/log/proxy-status.log
    # 发送告警
fi

# 添加到定时任务
crontab -e
# 添加: */5 * * * * /opt/scripts/check-proxy.sh
```

### 查看代理使用日志

```bash
# Git 代理日志
export GIT_CURL_VERBOSE=1
git fetch origin

# 系统代理日志
journalctl -u docker | grep proxy
```

## 成本估算

### 代理服务成本

以部署场景估算:
- 每次部署拉取: ~10MB
- 每天5次部署: ~50MB
- 每月: ~1.5GB

假设代理费用 0.01元/GB:
- 每月成本: ~0.015元
- 几乎可以忽略不计

## 备选方案

如果代理方案不适用,可以考虑:

1. **自建 GitHub 镜像**
   - 使用 GitHub Archive Program
   - 或使用 git mirror 功能

2. **使用 CDN 加速**
   - Cloudflare Workers
   - Vercel Edge Functions

3. **定期手动同步**
   - 定期从 GitHub 拉取
   - 推送到云主机

## 相关文档

- [GitHub Actions CI/CD 配置](./CICD_SUMMARY.md)
- [版本管理规范](./VERSION_MANAGEMENT_GUIDE.md)
- [Webhook 配置指南](./WEBHOOK_TROUBLESHOOTING.md)

---

配置完成时间: 2026-03-04
配置负责人: [您的名字]
