"""
路由蓝图模块
将所有路由按系统拆分为独立蓝图，提高代码可维护性
"""
from .home_bp import home_bp
from .kb_bp import kb_bp
from .kb_management_bp import kb_management_bp
from .case_bp import case_bp
from .unified_bp import unified_bp
from .api_bp import api_bp
from .auth_bp import auth_bp
from .user_management_bp import user_management_bp

__all__ = [
    'home_bp',
    'kb_bp',
    'kb_management_bp',
    'case_bp',
    'unified_bp',
    'api_bp',
    'auth_bp',
    'user_management_bp'
]
