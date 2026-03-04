"""
配置文件测试
"""
import pytest
import os


def test_config_file_exists():
    """测试配置文件是否存在"""
    assert os.path.exists('config.py'), "config.py 文件不存在"


def test_requirements_file_exists():
    """测试依赖文件是否存在"""
    assert os.path.exists('requirements.txt'), "requirements.txt 文件不存在"


def test_app_file_exists():
    """测试应用入口文件是否存在"""
    assert os.path.exists('app.py'), "app.py 文件不存在"
