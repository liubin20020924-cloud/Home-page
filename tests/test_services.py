"""
Services 模块测试
"""
import pytest
import os


def test_services_directory_exists():
    """测试服务目录是否存在"""
    assert os.path.exists('services/'), "services/ 目录不存在"


def test_check_git_config_exists():
    """测试Git配置检查脚本是否存在"""
    assert os.path.exists('scripts/check_git_config.sh'), "scripts/check_git_config.sh 文件不存在"
