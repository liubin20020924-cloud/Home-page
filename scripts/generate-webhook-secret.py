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
    """更新 .env 文件"""
    env_path = '.env'
    
    # 读取现有内容
    lines = []
    secret_exists = False
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    # 检查并更新或添加 WEBHOOK_SECRET
    new_lines = []
    for line in lines:
        if line.strip().startswith('WEBHOOK_SECRET='):
            new_lines.append(f'WEBHOOK_SECRET={secret}\n')
            secret_exists = True
        else:
            new_lines.append(line)
    
    if not secret_exists:
        new_lines.append(f'\n# ===========================================\n')
        new_lines.append(f'# Webhook 配置\n')
        new_lines.append(f'# ===========================================\n')
        new_lines.append(f'WEBHOOK_SECRET={secret}\n')
    
    # 写回文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    return secret


if __name__ == '__main__':
    print("=" * 60)
    print("Webhook 密钥生成工具")
    print("=" * 60)
    print()
    
    # 生成密钥
    secret = generate_secret()
    
    print(f"✅ 生成的密钥: {secret}")
    print()
    
    # 更新 .env 文件
    if os.path.exists('.env'):
        print("正在更新 .env 文件...")
        update_env_file(secret)
        print("✅ .env 文件已更新")
        print()
    else:
        print("⚠️  .env 文件不存在，请手动添加以下内容：")
        print()
        print(f"WEBHOOK_SECRET={secret}")
        print()
    
    print("=" * 60)
    print("配置步骤：")
    print("=" * 60)
    print()
    print("1. 在 GitHub 仓库中配置以下 Secrets：")
    print("   - Name: WEBHOOK_URL")
    print("   - Value: http://your-server-ip:9000")
    print()
    print("   - Name: WEBHOOK_SECRET")
    print(f"   - Value: {secret}")
    print()
    print("2. GitHub Secret 配置页面:")
    print("   https://github.com/liubin20020924-cloud/Home-page/settings/secrets/actions")
    print()
