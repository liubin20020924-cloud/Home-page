#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
依赖检查脚本
验证所有必需的 Python 包是否已安装
"""

import sys

# 必需的依赖列表
REQUIRED_PACKAGES = {
    # Flask 核心框架
    'flask': 'Flask',
    'flask_cors': 'Flask-Cors',
    'flask_sqlalchemy': 'Flask-SQLAlchemy',
    'flask_session': 'Flask-Session',
    'flask_socketio': 'flask-socketio',
    'python_socketio': 'python-socketio',

    # WebSocket 异步驱动
    'eventlet': 'eventlet',
    'gevent': 'gevent',

    # 数据库相关
    'pymysql': 'PyMySQL',
    'mysql.connector': 'mysql-connector-python',
    'dbutils': 'dbutils',
    'sqlalchemy': 'SQLAlchemy',

    # 其他依赖
    'dotenv': 'python-dotenv',
    'cryptography': 'cryptography',
    'werkzeug': 'werkzeug',
    'requests': 'requests',
    'bs4': 'beautifulsoup4',
    'bleach': 'bleach',
    'trilium_py': 'trilium-py',

    # API 文档
    'flasgger': 'flasgger',

    # 安全增强
    'flask_wtf': 'Flask-WTF',
    'flask_limiter': 'flask-limiter',

    # 图片优化
    'PIL': 'Pillow',
}

def check_import(package_name, display_name):
    """检查包是否可以导入"""
    try:
        __import__(package_name)
        return True, None
    except ImportError as e:
        return False, str(e)

def main():
    """主函数"""
    print("=" * 60)
    print("Dependency Check")
    print("=" * 60)

    missing_packages = []
    error_packages = []

    for package_name, display_name in REQUIRED_PACKAGES.items():
        success, error = check_import(package_name, display_name)

        if success:
            print(f"[OK] {display_name}")
        else:
            print(f"[MISSING] {display_name}")
            missing_packages.append(display_name)
            if error:
                error_packages.append((display_name, error))

    print("=" * 60)

    if missing_packages:
        print(f"\n[WARNING] Missing {len(missing_packages)} packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")

        if error_packages:
            print(f"\n[ERROR] Details:")
            for pkg, error in error_packages:
                print(f"   - {pkg}: {error}")

        print("\n[INSTALL] Run the following command to install missing dependencies:")
        print("   pip install -r requirements.txt")

        sys.exit(1)
    else:
        print("\n[SUCCESS] All dependencies are installed!")
        print("   You can run: python app.py")
        sys.exit(0)

if __name__ == '__main__':
    main()
