#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置安全检查工具
用于检查和生成安全配置建议
"""

import os
import secrets
import sys
from pathlib import Path

# 设置输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import check_config, BaseConfig, DB_PASSWORD


def generate_secure_key(length=64):
    """生成安全的密钥"""
    return secrets.token_hex(length // 2)


def generate_secure_password(length=16):
    """生成安全的密码"""
    import random
    import string

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


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title):
    """打印小节标题"""
    print(f"\n{title}")
    print("-" * 70)


def main():
    print_header("云户科技网站 - 配置安全检查工具")

    # 检查当前配置
    warnings, errors = check_config()

    print_section("配置检查结果")

    if errors:
        print("\n❌ 严重错误（必须修复）：")
        for error in errors:
            print(f"   • {error}")

    if warnings:
        print("\n⚠️  警告提示（建议修复）：")
        for warning in warnings:
            print(f"   • {warning}")

    if not errors and not warnings:
        print("\n✅ 所有配置检查通过！")

    # 生成安全建议
    print_section("安全配置建议")

    # SECRET_KEY
    print("\n1. Flask SECRET_KEY")
    if BaseConfig.SECRET_KEY == 'yihu-website-secret-key-2024-CHANGE-ME':
        new_key = generate_secure_key(64)
        print(f"   当前：使用默认值（不安全）")
        print(f"   建议：使用以下随机密钥")
        print(f"   FLASK_SECRET_KEY={new_key}")
    else:
        print("   ✅ 已配置自定义密钥")

    # 数据库密码
    print("\n2. 数据库密码")
    if DB_PASSWORD == 'Nutanix/4u123!':
        new_password = generate_secure_password(20)
        print(f"   当前：使用默认值（不安全）")
        print(f"   建议：使用以下强密码")
        print(f"   DB_PASSWORD={new_password}")
    else:
        print("   ✅ 已配置自定义密码")

    # Trilium Token
    print("\n3. Trilium Token")
    from config import TRILIUM_TOKEN
    if not TRILIUM_TOKEN:
        new_token = generate_secure_key(64)
        print(f"   当前：未配置")
        print(f"   建议：在 Trilium 中生成 ETAPI Token，然后设置环境变量")
        print(f"   TRILIUM_TOKEN=<从 Trilium 复制的 Token>")
    else:
        print("   ✅ 已配置")

    # SMTP 配置
    print("\n4. 邮件服务配置")
    from config import SMTP_PASSWORD
    if not SMTP_PASSWORD:
        print("   ⚠️  SMTP_PASSWORD 未配置，邮件功能将无法使用")
        print("   建议：在邮箱设置中生成授权码，然后设置环境变量")
        print("   SMTP_PASSWORD=<邮箱授权码>")
    else:
        print("   ✅ 已配置")

    # 环境变量检查
    print_section("环境变量检查")

    env_vars = [
        'FLASK_SECRET_KEY',
        'DB_PASSWORD',
        'TRILIUM_TOKEN',
        'SMTP_PASSWORD',
    ]

    print("\n必需的环境变量：")
    all_set = True
    for var in env_vars:
        value = os.getenv(var, '')
        if value:
            print(f"   ✅ {var}")
        else:
            print(f"   ❌ {var} （未设置）")
            all_set = False

    # 生成 .env 文件模板
    if not os.path.exists('.env'):
        print_section("生成 .env 配置文件")

        env_content = f"""# 云户科技网站 - 环境变量配置
# 由配置检查工具自动生成，请根据实际情况修改

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

        print("\n以下 .env 文件内容已准备好：")
        print("-" * 70)
        print(env_content)
        print("-" * 70)
        print("\n提示：将上述内容保存到项目根目录的 .env 文件中")

        # 询问是否保存
        try:
            save = input("\n是否自动保存到 .env 文件？(y/n): ").strip().lower()
            if save == 'y':
                with open('.env', 'w', encoding='utf-8') as f:
                    f.write(env_content)
                print("✅ .env 文件已创建，请立即修改其中的占位符！")
        except (KeyboardInterrupt, EOFError):
            print("\n操作已取消")

    # 总结
    print_header("检查完成")

    if errors:
        print("\n⚠️  发现严重配置错误，请按照上述建议修复后再启动应用！")
        return 1
    elif warnings:
        print("\n⚠️  存在一些配置警告，建议进行优化")
        return 0
    else:
        print("\n✅ 配置检查通过，可以安全启动应用")
        return 0


if __name__ == '__main__':
    exit(main())
