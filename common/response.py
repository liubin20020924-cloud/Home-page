"""
统一响应处理模块
提供标准化的API响应格式
"""
from flask import jsonify
from typing import Any, Dict, Optional, Tuple


def success_response(data: Any = None, message: str = '操作成功') -> Tuple[Dict, int]:
    """
    成功响应
    
    Args:
        data: 返回的数据
        message: 成功消息
        
    Returns:
        (json, status_code)
    """
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), 200


def error_response(message: str = '操作失败', code: int = 400, details: Optional[Dict] = None) -> Tuple[Dict, int]:
    """
    错误响应
    
    Args:
        message: 错误消息
        code: HTTP状态码
        details: 详细错误信息
        
    Returns:
        (json, status_code)
    """
    response = {
        'success': False,
        'message': message
    }
    if details:
        response['details'] = details
    return jsonify(response), code


def not_found_response(message: str = '资源未找到') -> Tuple[Dict, int]:
    """404 响应"""
    return error_response(message, 404)


def unauthorized_response(message: str = '未授权访问') -> Tuple[Dict, int]:
    """401 响应"""
    return error_response(message, 401)


def forbidden_response(message: str = '权限不足') -> Tuple[Dict, int]:
    """403 响应"""
    return error_response(message, 403)


def validation_error_response(errors: Dict[str, str]) -> Tuple[Dict, int]:
    """
    参数验证错误响应
    
    Args:
        errors: 字段名到错误消息的映射
        
    Returns:
        (json, 400)
    """
    return error_response('参数验证失败', 400, details={'validation_errors': errors})


def server_error_response(message: str = '服务器内部错误', details: Optional[Dict] = None) -> Tuple[Dict, int]:
    """500 响应"""
    return error_response(message, 500, details=details)
