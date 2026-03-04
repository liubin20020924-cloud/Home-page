#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 Webhook 密钥
"""
import secrets
import os


def generate_secret():
    """生成随机的 Webhook 密钥"""
    secret = secrets.token_urlsafe(32)
    return secret


def update_env_file(secret):
    """更新 .env 文件（仅用于密钥生成说明）"""
    env_path = '.env'
    
    # 读取现有内容（用于检查）
    lines = []
    secret_exists = False
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    # 检查是否已存在 WEBHOOK_SECRET
    for line in lines:
        if line.strip().startswith('WEBHOOK_SECRET='):
            secret_exists = True
            break
    
    return secret_exists


if __name__ == '__main__':
    print("=" * 60)
    print("Webhook 密钥生成工具")
    print("=" * 60)
    print()
    
    # 生成密钥
    secret = generate_secret()
    
    print(f"✅ 生成的密钥: {secret}")
    print()
    
    # 检查 .env 文件
    secret_exists = update_env_file(secret)
    
    print("=" * 60)
    print("配置说明")
    print("=" * 60)
    print()
    print("【方案 1：使用默认密钥（推荐）")
    print("=" * 60)
    print()
    print("在 GitHub 仓库中配置以下 Secret：")
    print()
    print("  1. 访问：")
    print("     https://github.com/liubin20020924-cloud/Home-page/settings/secrets/actions")
    print()
    print("  2. 点击 'New repository secret'")
    print()
    print("  3. 添加 Secret：")
    print("     Name: WEBHOOK_URL")
    print("     Value: http://your-server-ip:9000")
    print()
    print("  4. 点击 'Add secret'")
    print()
    print("✅ 无需配置 WEBHOOK_SECRET")
    print("   - Webhook 接收器会使用默认密钥验证")
    print("   - CI/CD workflow 会使用固定签名")
    print()
    
    print("=" * 60)
    print("【方案 2：生成真正密钥（更安全）")
    print("=" * 60)
    print()
    print("1. 在 GitHub 仓库中配置 Secrets：")
    print()
    print("  Name: WEBHOOK_URL")
    print("  Value: http://your-server-ip:9000")
    print()
    print("  Name: WEBHOOK_SECRET")
    print(f"  Value: {secret}")
    print()
    print("2. 在云主机 .env 文件中添加配置：")
    print()
    print("  WEBHOOK_SECRET=" + secret)
    print()
    print("3. 重启 webhook 服务：")
    print()
    print("  systemctl restart webhook-receiver")
    print()
    print("=" * 60)
    print("当前 .env 文件状态:")
    print("=" * 60)
    
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'WEBHOOK_SECRET=' in content:
                print("✅ 已配置 WEBHOOK_SECRET")
                print("   - 使用严格签名验证")
                print("   - 更安全但需要配置")
            else:
                print("⚠️  未配置 WEBHOOK_SECRET")
                print("   - 使用默认密钥验证")
                print("   - 配置更简单")
    else:
        print("⚠️  .env 文件不存在")
        print("   - 云主机上需要创建 .env 文件")
    print()
    
    print("=" * 60)
    print("配置完成后，重启 webhook 服务：")
    print("=" * 60)
    print()
    print("  systemctl restart webhook-receiver")
    print()
