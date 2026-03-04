"""
Services 模块测试
"""
import pytest
import os


def test_services_directory_exists():
    """测试服务目录是否存在"""
    assert os.path.exists('services/'), "services/ 目录不存在"


def test_check_dependencies_exists():
    """测试依赖检查脚本是否存在"""
    assert os.path.exists('scripts/check_dependencies.py'), "scripts/check_dependencies.py 文件不存在"


def test_check_config_exists():
    """测试配置检查脚本是否存在"""
    assert os.path.exists('scripts/check_config.py'), "scripts/check_config.py 文件不存在"
