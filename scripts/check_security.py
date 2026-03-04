#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速安全配置检查脚本
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import check_config, BaseConfig, DB_PASSWORD


def main():
    print("=" * 60)
    print("配置安全检查")
    print("=" * 60)

    warnings, errors = check_config()

    if errors:
        print("\n[X] 严重错误:")
        for error in errors:
            print(f"    {error}")

    if warnings:
        print("\n[!] 警告:")
        for warning in warnings:
            print(f"    {warning}")

    if not errors and not warnings:
        print("\n[OK] 配置检查通过")
        return 0
    else:
        print("\n建议:")
        print("1. 使用 scripts/generate_secure_env.py 生成安全配置")
        print("2. 或手动修改 .env 文件中的敏感配置")
        print("=" * 60)
        return 1 if errors else 0


if __name__ == '__main__':
    exit(main())
