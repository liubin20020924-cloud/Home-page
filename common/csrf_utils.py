"""CSRF 豁免装饰器"""
from functools import wraps

def csrf_exempt(view):
    """CSRF 豁免装饰器 - 用于 API 路由"""
    @wraps(view)
    def wrapped(*args, **kwargs):
        return view(*args, **kwargs)
    # 标记为豁免 CSRF
    wrapped._csrf_exempt = True
    return wrapped
