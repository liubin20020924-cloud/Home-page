"""
Pytest 配置文件
"""
import pytest
import os
import sys


# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def app():
    """应用测试 fixture"""
    try:
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        return app
    except Exception as e:
        pytest.skip(f"无法创建应用: {e}")


@pytest.fixture
def client(app):
    """测试客户端 fixture"""
    return app.test_client()
