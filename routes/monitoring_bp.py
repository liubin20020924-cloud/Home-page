"""
监控管理路由

功能：
1. 查看系统监控指标
2. 查看告警历史
3. 管理告警规则
4. 手动触发测试告警
"""

from flask import Blueprint, render_template, jsonify, request
from datetime import datetime, timedelta

from services.monitoring_service import get_monitoring_service, AlertLevel

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')


@monitoring_bp.route('/')
def dashboard():
    """监控仪表板"""
    monitoring = get_monitoring_service()
    current_metrics = monitoring.get_current_metrics()
    active_alerts = monitoring.get_active_alerts()
    recent_alerts = monitoring.get_recent_alerts(hours=24)

    return render_template('monitoring/dashboard.html',
                        metrics=current_metrics,
                        active_alerts=active_alerts,
                        recent_alerts=recent_alerts)


@monitoring_bp.route('/api/metrics')
def api_metrics():
    """获取当前指标 API"""
    monitoring = get_monitoring_service()
    metrics = monitoring.get_current_metrics()
    return jsonify({
        'success': True,
        'data': metrics,
        'timestamp': datetime.now().isoformat()
    })


@monitoring_bp.route('/api/alerts')
def api_alerts():
    """获取告警列表 API"""
    monitoring = get_monitoring_service()

    # 获取查询参数
    hours = request.args.get('hours', 24, type=int)
    status = request.args.get('status', 'all')  # all, active, resolved
    level = request.args.get('level', 'all')  # all, warning, error, critical

    alerts = monitoring.get_recent_alerts(hours=hours)

    # 过滤状态
    if status == 'active':
        alerts = [a for a in alerts if not a.resolved]
    elif status == 'resolved':
        alerts = [a for a in alerts if a.resolved]

    # 过滤级别
    if level != 'all':
        level_enum = AlertLevel(level)
        alerts = [a for a in alerts if a.level == level_enum]

    return jsonify({
        'success': True,
        'data': [
            {
                'level': alert.level.value,
                'metric_name': alert.metric_name,
                'current_value': alert.current_value,
                'threshold': alert.threshold,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'resolved': alert.resolved,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
            }
            for alert in alerts
        ],
        'count': len(alerts)
    })


@monitoring_bp.route('/api/alerts/active')
def api_active_alerts():
    """获取活跃告警 API"""
    monitoring = get_monitoring_service()
    active_alerts = monitoring.get_active_alerts()

    return jsonify({
        'success': True,
        'data': [
            {
                'level': alert.level.value,
                'metric_name': alert.metric_name,
                'current_value': alert.current_value,
                'threshold': alert.threshold,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat()
            }
            for alert in active_alerts
        ],
        'count': len(active_alerts)
    })


@monitoring_bp.route('/api/test-alert', methods=['POST'])
def test_alert():
    """测试告警 API"""
    from services.monitoring_service import Alert

    level = request.json.get('level', 'warning')
    metric_name = request.json.get('metric_name', 'test_metric')
    value = request.json.get('value', 85.0)

    monitoring = get_monitoring_service()

    alert = Alert(
        level=AlertLevel(level),
        metric_name=metric_name,
        current_value=value,
        threshold=80.0,
        message=f"测试告警: {metric_name} = {value}%",
        timestamp=datetime.now()
    )

    # 手动触发告警
    monitoring._trigger_alert(alert)

    return jsonify({
        'success': True,
        'message': '测试告警已发送'
    })


@monitoring_bp.route('/api/config', methods=['GET', 'PUT'])
def api_config():
    """获取或更新监控配置 API"""
    monitoring = get_monitoring_service()

    if request.method == 'GET':
        # 返回配置（隐藏敏感信息）
        config = monitoring.config.copy()
        config.pop('email_recipients', None)
        return jsonify({
            'success': True,
            'data': config
        })
    else:
        # 更新配置
        data = request.json
        for key, value in data.items():
            if key in monitoring.config:
                monitoring.config[key] = value

        return jsonify({
            'success': True,
            'message': '配置已更新'
        })


@monitoring_bp.route('/health')
def health_check():
    """健康检查端点"""
    try:
        monitoring = get_monitoring_service()
        metrics = monitoring.get_current_metrics()

        # 检查是否有严重告警
        active_alerts = monitoring.get_active_alerts()
        critical_alerts = [a for a in active_alerts if a.level == AlertLevel.CRITICAL]

        status = 'healthy' if not critical_alerts else 'unhealthy'

        return jsonify({
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'active_alerts': len(active_alerts),
            'critical_alerts': len(critical_alerts)
        }), 200 if status == 'healthy' else 503

    except Exception as e:
        return jsonify({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503


@monitoring_bp.route('/readiness')
def readiness_check():
    """就绪检查端点"""
    try:
        # 检查数据库连接
        from common.database_context import get_db_connection
        conn = get_db_connection('clouddoors_db')
        conn.close()

        return jsonify({
            'status': 'ready',
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503
