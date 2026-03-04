"""
Routes 模块测试
"""
import pytest
import os


def test_home_bp_exists():
    """测试首页路由模块是否存在"""
    assert os.path.exists('routes/home_bp.py'), "routes/home_bp.py 文件不存在"


def test_kb_bp_exists():
    """测试知识库路由模块是否存在"""
    assert os.path.exists('routes/kb_bp.py'), "routes/kb_bp.py 文件不存在"


def test_case_bp_exists():
    """测试工单路由模块是否存在"""
    assert os.path.exists('routes/case_bp.py'), "routes/case_bp.py 文件不存在"


def test_api_bp_exists():
    """测试API路由模块是否存在"""
    assert os.path.exists('routes/api_bp.py'), "routes/api_bp.py 文件不存在"


def test_auth_bp_exists():
    """测试认证路由模块是否存在"""
    assert os.path.exists('routes/auth_bp.py'), "routes/auth_bp.py 文件不存在"


def test_routes_directory_structure():
    """测试路由目录结构"""
    required_files = [
        'routes/home_bp.py',
        'routes/kb_bp.py',
        'routes/case_bp.py',
        'routes/api_bp.py',
        'routes/auth_bp.py',
        'routes/kb_management_bp.py',
    ]

    for file_path in required_files:
        assert os.path.exists(file_path), f"{file_path} 文件不存在"
