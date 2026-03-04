#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成安全的环境变量配置
"""

import os
import secrets
import random
import string


def generate_secure_key(length=64):
    """生成安全的密钥"""
    return secrets.token_hex(length // 2)


def generate_secure_password(length=16):
    """生成安全的密码"""
    # 确保包含大小写字母、数字和特殊字符
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    password = ''.join(random.choice(chars) for _ in range(length))

    # 确保至少包含每种类型
    if not any(c.islower() for c in password):
        password = password[:-1] + random.choice(string.ascii_lowercase)
    if not any(c.isupper() for c in password):
        password = password[:-2] + random.choice(string.ascii_uppercase)
    if not any(c.isdigit() for c in password):
        password = password[:-3] + random.choice(string.digits)

    return password


def main():
    env_content = f"""# 云户科技网站 - 环境变量配置
# 警告：此文件包含敏感信息，请勿提交到版本控制系统
# 生成时间: {os.popen('date /t && time /t').read().strip()}

# ============================================
# Flask 基础配置
# ============================================
FLASK_SECRET_KEY={generate_secure_key(64)}
FLASK_DEBUG=False

# ============================================
# 数据库配置
# ============================================
DB_HOST=10.10.10.250
DB_PORT=3306
DB_USER=root
DB_PASSWORD={generate_secure_password(20)}

DB_NAME_HOME=clouddoors_db
DB_NAME_KB=YHKB
DB_NAME_CASE=casedb

# ============================================
# 邮件配置
# ============================================
SMTP_SERVER=smtp.qq.com
SMTP_PORT=465
SMTP_USERNAME=your-email@qq.com
SMTP_PASSWORD=<请替换为邮箱授权码>
EMAIL_SENDER=your-email@qq.com

# ============================================
# Trilium 配置
# ============================================
TRILIUM_SERVER_URL=http://10.10.10.250:8080
TRILIUM_TOKEN=<请从 Trilium 复制 ETAPI Token>
TRILIUM_SERVER_HOST=10.10.10.250:8080
TRILIUM_LOGIN_PASSWORD={generate_secure_password(16)}

# ============================================
# 其他配置
# ============================================
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@cloud-doors.com

CONTACT_EMAIL=support@cloud-doors.com
"""

    print("=" * 60)
    print("安全环境变量生成器")
    print("=" * 60)
    print()
    print("生成的配置内容:")
    print("-" * 60)
    print(env_content)
    print("-" * 60)
    print()

    # 保存到文件
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)

    print(f"[OK] 已保存到: {env_file}")
    print()
    print("重要提示:")
    print("1. 请立即修改以下占位符:")
    print("   - SMTP_PASSWORD: 替换为你的邮箱授权码")
    print("   - TRILIUM_TOKEN: 替换为 Trilium ETAPI Token")
    print("2. 根据实际情况修改其他配置项")
    print("3. 确保 .env 文件不会被提交到版本控制系统")


if __name__ == '__main__':
    main()
