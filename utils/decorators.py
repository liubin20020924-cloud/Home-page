"""
装饰器工具
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """
    管理员权限验证装饰器

    要求用户必须登录且具有管理员权限
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))

        if not current_user.is_admin:
            flash('需要管理员权限', 'danger')
            return redirect(url_for('home.index'))

        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    """
    角色权限验证装饰器

    Args:
        role: 所需角色名（如 'admin', 'customer_service'）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login'))

            if current_user.role != role:
                flash(f'需要 {role} 角色', 'danger')
                return redirect(url_for('home.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
