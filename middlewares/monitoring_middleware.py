"""
监控中间件

功能：
1. 记录每个请求的响应时间
2. 记录错误率
3. 追踪并发请求数
4. 记录 API 调用统计
"""

import time
import logging
from flask import request, g
from functools import wraps
from typing import Callable
from datetime import datetime

from services.monitoring_service import get_monitoring_service


logger = logging.getLogger(__name__)


class MonitoringMiddleware:
    """监控中间件"""

    def __init__(self, app):
        """
        初始化监控中间件

        Args:
            app: Flask 应用实例
        """
        self.app = app
        self.monitoring = get_monitoring_service()
        self._setup_hooks()

    def _setup_hooks(self):
        """设置请求钩子"""
        self.app.before_request(self._before_request)
        self.app.after_request(self._after_request)
        self.app.teardown_request(self._teardown_request)

    def _before_request(self):
        """请求前处理"""
        g.start_time = time.time()
        g.request_id = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        # 记录并发请求数（简化实现）
        logger.debug(f"Request {g.request_id}: {request.method} {request.path}")

    def _after_request(self, response):
        """请求后处理"""
        try:
            if hasattr(g, 'start_time'):
                # 计算响应时间
                response_time = (time.time() - g.start_time) * 1000  # 转换为毫秒

                # 记录指标
                endpoint = request.endpoint or request.path
                self.monitoring.record_api_metric(endpoint, response_time, response.status_code)

                # 添加响应头
                response.headers['X-Response-Time'] = f"{response_time:.2f}ms"
                response.headers['X-Request-ID'] = g.request_id

                # 慢请求警告
                if response_time > 3000:  # 超过 3 秒
                    logger.warning(
                        f"Slow request: {request.method} {request.path} - "
                        f"{response_time:.2f}ms - Status: {response.status_code}"
                    )

                logger.debug(
                    f"Request {g.request_id} completed: {response_time:.2f}ms - "
                    f"Status: {response.status_code}"
                )

        except Exception as e:
            logger.error(f"Error in after_request: {e}", exc_info=True)

        return response

    def _teardown_request(self, exception):
        """请求清理"""
        if exception:
            logger.error(
                f"Request {getattr(g, 'request_id', 'unknown')} failed: {exception}",
                exc_info=True
            )


def track_performance(func: Callable) -> Callable:
    """
    性能追踪装饰器

    用于追踪特定函数的执行时间

    Args:
        func: 要追踪的函数

    Returns:
        包装后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            execution_time = (time.time() - start_time) * 1000
            func_name = f"{func.__module__}.{func.__name__}"

            # 记录慢函数
            if execution_time > 1000:  # 超过 1 秒
                logger.warning(f"Slow function: {func_name} - {execution_time:.2f}ms")
            else:
                logger.debug(f"Function: {func_name} - {execution_time:.2f}ms")

    return wrapper


def track_errors(func: Callable) -> Callable:
    """
    错误追踪装饰器

    用于追踪函数的错误和异常

    Args:
        func: 要追踪的函数

    Returns:
        包装后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            func_name = f"{func.__module__}.{func.__name__}"
            logger.error(f"Error in {func_name}: {e}", exc_info=True)
            raise

    return wrapper


def get_request_metrics():
    """获取请求指标（简化版）"""
    monitoring = get_monitoring_service()
    return monitoring.get_current_metrics()
