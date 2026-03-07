"""认证相关的工具函数"""
from functools import wraps
from flask import request, redirect, url_for
from common.unified_auth import get_current_user
from common.response import error_response


def admin_login_required(f):
    """管理员登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查登录状态
        user = get_current_user()
        if not user:
            # 未登录，跳转到登录页面
            if request.is_json:
                return error_response('未登录，请先登录', 401)
            return redirect(url_for('admin.login'))

        # 检查是否是管理员
        if user.get('role') != 'admin':
            if request.is_json:
                return error_response('权限不足', 403)
            return redirect(url_for('admin.login'))

        return f(*args, **kwargs)

    return decorated_function
