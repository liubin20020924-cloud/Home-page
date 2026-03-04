# 云主机代理配置快速指南

## 🚀 快速配置 (推荐 HTTP 代理)

### 1. 获取代理服务

推荐服务商:
- 蚁链 AntLink: https://antlink.cc
- 芝麻代理: https://www.zhimaruanjian.com
- 快代理: https://www.kuaidaili.com

购买后获得: `proxy-server:port`

### 2. 配置 Git 代理

```bash
# SSH 到云主机
ssh root@10.10.10.250

# 配置 Git 代理 (仅对 GitHub)
git config --global http.https://github.com.proxy http://proxy-server:port

# 验证配置
git config --global --get http.https://github.com.proxy
```

### 3. 测试连接

```bash
# 测试拉取
cd /opt/Home-page
git fetch origin

# 如果成功,输出应该类似:
# From https://github.com/liubin20020924-cloud/Home-page
#    * [new branch]      main -> origin/main
```

### 4. 配置环境变量 (可选)

```bash
# 编辑 .bashrc
vim ~/.bashrc

# 添加:
export http_proxy=http://proxy-server:port
export https_proxy=http://proxy-server:port
export no_proxy=localhost,127.0.0.1,10.0.0.0/8

# 使配置生效
source ~/.bashrc
```

### 5. 验证部署

```bash
# 手动触发部署
cd /opt/Home-page
bash ./scripts/deploy.sh

# 查看部署日志
tail -f /var/log/integrate-code/deployment.log
```

## 📋 配置清单

- [ ] 购买代理服务
- [ ] 配置 Git 代理
- [ ] 测试 GitHub 连接
- [ ] 验证部署流程
- [ ] 配置环境变量 (可选)

## 🆘 常见问题

### Q: 拉取超时怎么办?

A: 增加 Git 超时时间:
```bash
git config --global http.timeout 300
git config --global http.lowSpeedLimit 0
```

### Q: 代理需要认证怎么办?

A: 使用带认证的代理地址:
```bash
git config --global http.https://github.com.proxy http://username:password@proxy-server:port
```

### Q: 如何查看当前代理配置?

A:
```bash
git config --global --get http.proxy
git config --global --get https.proxy
git config --global --get http.https://github.com.proxy
```

### Q: 如何取消代理?

A:
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
git config --global --unset http.https://github.com.proxy
```

## 💰 成本估算

- 每次部署: ~10MB
- 每天5次: ~50MB
- 每月: ~1.5GB
- 代理费用: ~0.015元/月 (按0.01元/GB计算)

## 📚 详细文档

完整配置指南: [docs/PROXY_SETUP.md](./PROXY_SETUP.md)

---

配置完成后,GitHub CI/CD 流程将正常工作!
