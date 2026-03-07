"""
应用监控与告警服务

功能：
1. 系统资源监控（CPU、内存、磁盘）
2. 应用性能监控（API响应时间、错误率）
3. 自定义业务指标监控
4. 告警规则配置
5. 告警通知（邮件、日志）
"""

import psutil
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import os

from services.email_service import EmailService


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """告警信息"""
    level: AlertLevel
    metric_name: str
    current_value: float
    threshold: float
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class Metric:
    """指标数据"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str]


class MonitoringService:
    """监控服务"""
    
    def __init__(self, config: dict = None):
        """
        初始化监控服务

        Args:
            config: 配置字典，包含告警阈值、通知方式等
        """
        self.config = config or self._get_default_config()
        self.email_service = EmailService()
        self.logger = logging.getLogger(__name__)
        self.metrics: List[Metric] = []
        self.alerts: List[Alert] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.is_running = False
        self.monitor_thread = None
        
        # 告警通知回调
        self.alert_callbacks: List[Callable[[Alert], None]] = []

    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            # CPU 告警阈值
            'cpu_warning_threshold': 70.0,  # CPU 使用率 > 70% 警告
            'cpu_critical_threshold': 90.0,  # CPU 使用率 > 90% 严重
            
            # 内存告警阈值
            'memory_warning_threshold': 70.0,  # 内存使用率 > 70% 警告
            'memory_critical_threshold': 85.0,  # 内存使用率 > 85% 严重
            
            # 磁盘告警阈值
            'disk_warning_threshold': 80.0,  # 磁盘使用率 > 80% 警告
            'disk_critical_threshold': 90.0,  # 磁盘使用率 > 90% 严重
            
            # API 响应时间告警（毫秒）
            'api_response_warning': 1000,  # > 1秒 警告
            'api_response_critical': 3000,  # > 3秒 严重
            
            # 错误率告警
            'error_rate_warning': 5.0,  # 错误率 > 5% 警告
            'error_rate_critical': 10.0,  # 错误率 > 10% 严重
            
            # 监控配置
            'monitor_interval': 60,  # 监控间隔（秒）
            'metrics_retention_days': 7,  # 指标保留天数
            'alert_retention_days': 30,  # 告警保留天数
            
            # 通知配置
            'email_enabled': True,
            'email_recipients': os.getenv('MONITORING_EMAIL_RECIPIENTS', ''),
            'log_alerts': True,
        }

    def start(self):
        """启动监控服务"""
        if self.is_running:
            self.logger.warning("Monitoring service is already running")
            return

        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Monitoring service started")

    def stop(self):
        """停止监控服务"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Monitoring service stopped")

    def _monitor_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                self._collect_metrics()
                self._check_alerts()
                self._cleanup_old_data()
                time.sleep(self.config.get('monitor_interval', 60))
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}", exc_info=True)

    def _collect_metrics(self):
        """收集系统指标"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self._add_metric('cpu_usage', cpu_percent, '%')
            
            # 内存使用率
            memory = psutil.virtual_memory()
            self._add_metric('memory_usage', memory.percent, '%')
            self._add_metric('memory_available', memory.available / (1024**3), 'GB')
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            self._add_metric('disk_usage', disk.percent, '%')
            self._add_metric('disk_available', disk.free / (1024**3), 'GB')
            
            # 网络统计
            net_io = psutil.net_io_counters()
            self._add_metric('network_bytes_sent', net_io.bytes_sent, 'bytes')
            self._add_metric('network_bytes_recv', net_io.bytes_recv, 'bytes')
            
            # 进程统计
            self._add_metric('process_count', len(psutil.pids()), 'count')
            
            self.logger.debug(f"Collected metrics: CPU {cpu_percent}%, Memory {memory.percent}%")
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}", exc_info=True)

    def _check_alerts(self):
        """检查告警条件"""
        try:
            # 获取最新的指标
            metrics = {m.name: m for m in self.metrics}
            
            # 检查 CPU
            cpu_metric = metrics.get('cpu_usage')
            if cpu_metric:
                self._check_threshold('cpu_usage', cpu_metric.value,
                                    self.config['cpu_warning_threshold'],
                                    self.config['cpu_critical_threshold'])
            
            # 检查内存
            memory_metric = metrics.get('memory_usage')
            if memory_metric:
                self._check_threshold('memory_usage', memory_metric.value,
                                    self.config['memory_warning_threshold'],
                                    self.config['memory_critical_threshold'])
            
            # 检查磁盘
            disk_metric = metrics.get('disk_usage')
            if disk_metric:
                self._check_threshold('disk_usage', disk_metric.value,
                                    self.config['disk_warning_threshold'],
                                    self.config['disk_critical_threshold'])
            
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}", exc_info=True)

    def _check_threshold(self, metric_name: str, value: float,
                         warning_threshold: float, critical_threshold: float):
        """
        检查阈值并触发告警

        Args:
            metric_name: 指标名称
            value: 当前值
            warning_threshold: 警告阈值
            critical_threshold: 严重阈值
        """
        # 如果已经存在告警，检查是否恢复
        if metric_name in self.active_alerts:
            if value < warning_threshold:
                self._resolve_alert(metric_name)
            return

        # 触发新告警
        if value >= critical_threshold:
            alert = Alert(
                level=AlertLevel.CRITICAL,
                metric_name=metric_name,
                current_value=value,
                threshold=critical_threshold,
                message=f"{metric_name} 达到严重阈值: {value:.2f}% >= {critical_threshold}%",
                timestamp=datetime.now()
            )
            self._trigger_alert(alert)
        elif value >= warning_threshold:
            alert = Alert(
                level=AlertLevel.WARNING,
                metric_name=metric_name,
                current_value=value,
                threshold=warning_threshold,
                message=f"{metric_name} 达到警告阈值: {value:.2f}% >= {warning_threshold}%",
                timestamp=datetime.now()
            )
            self._trigger_alert(alert)

    def _trigger_alert(self, alert: Alert):
        """触发告警"""
        # 记录告警
        self.alerts.append(alert)
        self.active_alerts[alert.metric_name] = alert
        
        # 记录日志
        log_level = logging.WARNING if alert.level == AlertLevel.WARNING else logging.ERROR
        self.logger.log(log_level, f"Alert triggered: {alert.message}")
        
        # 发送邮件通知
        if self.config.get('email_enabled'):
            self._send_alert_email(alert)
        
        # 调用回调函数
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}", exc_info=True)

    def _resolve_alert(self, metric_name: str):
        """解决告警"""
        if metric_name in self.active_alerts:
            alert = self.active_alerts[metric_name]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            del self.active_alerts[metric_name]
            
            self.logger.info(f"Alert resolved: {metric_name}")
            
            # 发送恢复通知
            if self.config.get('email_enabled'):
                self._send_alert_resolved_email(alert)

    def _send_alert_email(self, alert: Alert):
        """发送告警邮件"""
        try:
            recipients = self.config.get('email_recipients', '').split(',')
            if not recipients or not recipients[0]:
                return

            subject = f"[告警] {alert.level.value.upper()} - {alert.metric_name}"
            html_content = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .alert-container {{
                        border: 2px solid {'red' if alert.level == AlertLevel.CRITICAL else 'orange'};
                        border-radius: 5px;
                        padding: 20px;
                        margin: 10px 0;
                    }}
                    .critical {{ background-color: #fff3f3; }}
                    .warning {{ background-color: #fff9e6; }}
                    .info {{ background-color: #f0f8ff; }}
                    .metric-name {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                    .metric-value {{ font-size: 24px; font-weight: bold; color: {'red' if alert.level == AlertLevel.CRITICAL else 'orange'}; }}
                </style>
            </head>
            <body>
                <div class="alert-container {alert.level.value}">
                    <h2>🚨 系统告警通知</h2>
                    <p><strong>服务器:</strong> {os.getenv('SITE_URL', 'localhost')}</p>
                    <p><strong>告警级别:</strong> {alert.level.value.upper()}</p>
                    <p><strong>告警时间:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <hr>
                    <div class="metric-name">{alert.metric_name}</div>
                    <div class="metric-value">{alert.current_value:.2f}%</div>
                    <p><strong>阈值:</strong> {alert.threshold:.2f}%</p>
                    <p><strong>详细信息:</strong></p>
                    <pre>{alert.message}</pre>
                    <hr>
                    <p>请尽快检查服务器状态并采取相应措施。</p>
                </div>
            </body>
            </html>
            """

            self.email_service.send_email(recipients, subject, html_content, html=True)
            self.logger.info(f"Alert email sent for {alert.metric_name}")

        except Exception as e:
            self.logger.error(f"Error sending alert email: {e}", exc_info=True)

    def _send_alert_resolved_email(self, alert: Alert):
        """发送告警恢复邮件"""
        try:
            recipients = self.config.get('email_recipients', '').split(',')
            if not recipients or not recipients[0]:
                return

            subject = f"[恢复] {alert.metric_name} - 告警已解决"
            html_content = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .alert-container {{
                        border: 2px solid green;
                        border-radius: 5px;
                        padding: 20px;
                        margin: 10px 0;
                        background-color: #f0fff4;
                    }}
                </style>
            </head>
            <body>
                <div class="alert-container">
                    <h2>✅ 告警已解决</h2>
                    <p><strong>服务器:</strong> {os.getenv('SITE_URL', 'localhost')}</p>
                    <p><strong>指标名称:</strong> {alert.metric_name}</p>
                    <p><strong>告警触发时间:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>告警解决时间:</strong> {alert.resolved_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>持续时间:</strong> {(alert.resolved_at - alert.timestamp).total_seconds() / 60:.1f} 分钟</p>
                    <hr>
                    <p>系统已恢复正常，无需进一步处理。</p>
                </div>
            </body>
            </html>
            """

            self.email_service.send_email(recipients, subject, html_content, html=True)
            self.logger.info(f"Alert resolved email sent for {alert.metric_name}")

        except Exception as e:
            self.logger.error(f"Error sending alert resolved email: {e}", exc_info=True)

    def _add_metric(self, name: str, value: float, unit: str, tags: dict = None):
        """添加指标"""
        metric = Metric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self.metrics.append(metric)

    def _cleanup_old_data(self):
        """清理旧数据"""
        try:
            retention_days = self.config.get('metrics_retention_days', 7)
            cutoff_time = datetime.now() - timedelta(days=retention_days)

            # 清理旧指标
            self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]

            # 清理旧告警
            alert_retention_days = self.config.get('alert_retention_days', 30)
            alert_cutoff_time = datetime.now() - timedelta(days=alert_retention_days)
            self.alerts = [a for a in self.alerts if a.timestamp > alert_cutoff_time]

            self.logger.debug("Cleaned up old monitoring data")

        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}", exc_info=True)

    def get_current_metrics(self) -> Dict[str, float]:
        """获取当前指标"""
        # 返回最新的指标
        metrics = {}
        for metric in reversed(self.metrics):
            if metric.name not in metrics:
                metrics[metric.name] = metric.value
        return metrics

    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return list(self.active_alerts.values())

    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """获取最近的告警"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [a for a in self.alerts if a.timestamp > cutoff_time]

    def register_alert_callback(self, callback: Callable[[Alert], None]):
        """注册告警回调函数"""
        self.alert_callbacks.append(callback)

    def record_api_metric(self, endpoint: str, response_time: float, status_code: int):
        """记录 API 指标"""
        # 记录响应时间
        self._add_metric(f'api_{endpoint}_response_time', response_time, 'ms',
                       {'endpoint': endpoint})

        # 记录错误
        if status_code >= 400:
            error_count = sum(1 for m in self.metrics
                            if m.name == f'api_{endpoint}_error_count')
            self._add_metric(f'api_{endpoint}_error_count', error_count + 1, 'count',
                           {'endpoint': endpoint, 'status_code': str(status_code)})


# 全局监控服务实例
_monitoring_service: Optional[MonitoringService] = None


def init_monitoring_service(config: dict = None) -> MonitoringService:
    """
    初始化全局监控服务

    Args:
        config: 配置字典

    Returns:
        MonitoringService 实例
    """
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService(config)
    return _monitoring_service


def get_monitoring_service() -> MonitoringService:
    """获取全局监控服务实例"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service
