#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 requirements.txt 中的所有依赖是否可用
"""

import subprocess
import sys
import re

# 从 requirements.txt 提取的包列表
REQUIREMENTS = [
    # Flask 核心框架
    ('Flask', '3.0.3', 'flask'),
    ('Flask-Cors', '4.0.0', 'flask_cors'),
    ('Flask-SQLAlchemy', '3.1.1', 'flask_sqlalchemy'),
    ('Flask-Session', '0.5.0', 'flask_session'),
    ('flask-socketio', '5.3.6', 'flask_socketio'),
    ('python-socketio', '5.11.0', 'python_socketio'),

    # WebSocket 异步驱动
    ('eventlet', '0.33.3', 'eventlet'),
    ('gevent', '23.9.1', 'gevent'),

    # 数据库相关
    ('PyMySQL', '1.1.0', 'pymysql'),
    ('mysql-connector-python', '8.0.33', 'mysql.connector'),
    ('dbutils', '3.0.3', 'dbutils'),
    ('SQLAlchemy', '2.0.35', 'sqlalchemy'),

    # 其他依赖
    ('python-dotenv', '1.0.0', 'dotenv'),
    ('cryptography', '41.0.7', 'cryptography'),
    ('werkzeug', '3.0.1', 'werkzeug'),
    ('requests', '2.31.0', 'requests'),
    ('beautifulsoup4', '4.12.2', 'bs4'),
    ('bleach', '6.0.0', 'bleach'),
    ('trilium-py', '0.8.5', 'trilium_py'),

    # API 文档
    ('flasgger', '0.9.7.1', 'flasgger'),

    # 安全增强
    ('Flask-WTF', '1.2.1', 'flask_wtf'),
    ('flask-limiter', '3.5.0', 'flask_limiter'),

    # 图片优化
    ('Pillow', '10.0.0', 'PIL'),

    # 开发和测试依赖
    ('pytest', '7.4.3', 'pytest'),
    ('pytest-cov', '4.1.0', 'pytest_cov'),
    ('coverage', '7.2.7', 'coverage'),
]

def check_package_exists(package_name, version):
    """检查包是否存在于 PyPI"""
    try:
        result = subprocess.run(
            ['pip', 'index', 'versions', package_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def check_package_installed(import_name):
    """检查包是否已安装"""
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("Requirements.txt Dependency Verification")
    print("=" * 80)
    print()

    all_packages_exist = True
    all_packages_installed = True

    print(f"{'Package Name':<30} {'Version':<12} {'PyPI':<8} {'Installed':<10}")
    print("-" * 80)

    for package_name, version, import_name in REQUIREMENTS:
        # 检查是否存在于 PyPI
        exists = check_package_exists(package_name, version)
        if not exists:
            all_packages_exist = False

        # 检查是否已安装
        installed = check_package_installed(import_name)
        if not installed:
            all_packages_installed = False

        # 输出结果
        exists_mark = "[OK]" if exists else "[X]"
        installed_mark = "[OK]" if installed else "[X]"
        print(f"{package_name:<30} {version:<12} {exists_mark:<8} {installed_mark:<10}")

    print("=" * 80)

    # 总结
    print()
    if all_packages_exist and all_packages_installed:
        print("[SUCCESS] All packages exist in PyPI and are installed!")
        print("You can run: python app.py")
        return 0
    elif all_packages_exist and not all_packages_installed:
        print("[WARNING] All packages exist in PyPI, but some are not installed.")
        print("Run: pip install -r requirements.txt")
        return 1
    elif not all_packages_exist and all_packages_installed:
        print("[ERROR] Some packages do not exist in PyPI!")
        return 1
    else:
        print("[ERROR] Some packages do not exist in PyPI and are not installed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
