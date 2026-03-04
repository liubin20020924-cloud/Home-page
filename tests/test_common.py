"""
Common 模块测试
"""
import pytest
import os
import sys


def test_response_module_exists():
    """测试响应模块是否存在"""
    assert os.path.exists('common/response.py'), "common/response.py 文件不存在"


def test_logger_module_exists():
    """测试日志模块是否存在"""
    assert os.path.exists('common/logger.py'), "common/logger.py 文件不存在"


def test_database_module_exists():
    """测试数据库模块是否存在"""
    assert os.path.exists('common/database.py'), "common/database.py 文件不存在"


def test_trilium_helper_exists():
    """测试Trilium辅助模块是否存在"""
    assert os.path.exists('common/trilium_helper.py'), "common/trilium_helper.py 文件不存在"


def test_import_response():
    """测试能否导入响应模块"""
    try:
        from common.response import success_response, error_response
        assert callable(success_response)
        assert callable(error_response)
    except ImportError as e:
        pytest.fail(f"无法导入 response 模块: {e}")


def test_import_logger():
    """测试能否导入日志模块"""
    try:
        from common.logger import setup_logger, get_logger
        assert callable(setup_logger)
        assert callable(get_logger)
    except ImportError as e:
        pytest.fail(f"无法导入 logger 模块: {e}")
