"""
云户科技网站 - 统一主入口
整合官网、知识库、工单三个系统
使用统一路由管理
"""
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect
from flasgger import Swagger
import jinja2
import config
from common.db_manager import get_pool
from services.socketio_service import register_socketio_events, init_case_database
from routes import home_bp, kb_bp, kb_management_bp, case_bp, unified_bp, api_bp, auth_bp, user_management_bp
import os
from datetime import timedelta

# 初始化主应用
template_dirs = [
    os.path.join(os.path.dirname(__file__), 'templates')
]
app = Flask(__name__, template_folder='templates')
app.jinja_loader = jinja2.ChoiceLoader([jinja2.FileSystemLoader(d) for d in template_dirs])
app.secret_key = config.BaseConfig.SECRET_KEY
app.config['JSON_AS_ASCII'] = False
app.config['SESSION_COOKIE_SAMESITE'] = config.BaseConfig.SESSION_COOKIE_SAMESITE
app.config['SESSION_COOKIE_HTTPONLY'] = config.BaseConfig.SESSION_COOKIE_HTTPONLY

# Session 安全配置（生产环境使用 HTTPS 时启用）
if os.getenv('HTTPS_ENABLED', 'false').lower() == 'true':
    app.config['SESSION_COOKIE_SECURE'] = True

# 启用 CSRF 保护
# 注意：需要安装 flask-wtf: pip install flask-wtf
# 登录和认证 API 不使用 CSRF 保护，因为它们是公开接口
# 其他表单需要在模板中添加 {% csrf_token() %}
csrf = None
try:
    csrf = CSRFProtect(app)
except ImportError:
    print("警告: flask-wtf 未安装，CSRF 保护未启用。运行: pip install flask-wtf")

# 为所有模板添加 CSRF token 到上下文
@app.context_processor
def inject_csrf_token():
    if csrf:
        return dict(csrf_token=lambda: csrf._get_csrf_token())
    return dict(csrf_token=lambda: '')

# 性能优化配置
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=3)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = config.BaseConfig.STATIC_CACHE_TIME

# Swagger UI 配置
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "云户科技网站 API 文档",
        "description": """
        云户科技整合平台 API 文档

        本平台整合了以下三个系统的 API：
        - **官网系统** - 官网首页、联系表单、留言管理
        - **知识库系统** - 知识库浏览、搜索、管理、Trilium 集成
        - **工单系统** - 工单创建、查询、聊天、状态管理
        - **统一用户管理** - 用户认证、权限管理

        ### 认证说明

        大多数 API 需要用户登录认证。登录后，Session 会自动携带认证信息。

        ### 响应格式

        所有 API 返回统一的 JSON 格式：

        ```json
        {
          "success": true,
          "message": "操作成功",
          "data": {}
        }
        ```
        """,
        "contact": {
            "name": "云户科技",
            "email": "support@cloud-doors.com"
        },
        "version": "1.0"
    },
    "host": f"{config.FLASK_HOST}:{config.FLASK_PORT}",
    "basePath": "/",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "tags": [
        {
            "name": "官网",
            "description": "官网系统相关 API"
        },
        {
            "name": "知识库-认证",
            "description": "知识库系统用户认证 API"
        },
        {
            "name": "知识库-浏览",
            "description": "知识库内容浏览和搜索 API"
        },
        {
            "name": "知识库-管理",
            "description": "知识库管理功能 API（需要管理员权限）"
        },
        {
            "name": "工单-认证",
            "description": "工单系统认证 API"
        },
        {
            "name": "工单-操作",
            "description": "工单创建和查询 API"
        },
        {
            "name": "用户管理",
            "description": "统一用户管理 API"
        },
        {
            "name": "Trilium",
            "description": "Trilium 笔记集成 API"
        }
    ],
    "definitions": {
        "SuccessResponse": {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "请求是否成功",
                    "example": True
                },
                "message": {
                    "type": "string",
                    "description": "响应消息",
                    "example": "操作成功"
                },
                "data": {
                    "type": "object",
                    "description": "返回数据"
                }
            }
        },
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "请求是否成功",
                    "example": False
                },
                "message": {
                    "type": "string",
                    "description": "错误消息",
                    "example": "操作失败"
                }
            }
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# CSRF 保护 - 已禁用以避免登录问题


# 请求速率限制
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "100 per hour"],  # 增加每小时的限制从50到100
    storage_uri="memory://"  # 生产环境可改为 Redis
)
limiter.init_app(app)

# 初始化SocketIO
try:
    import eventlet
    eventlet.monkey_patch()
    async_mode = 'eventlet'
except ImportError:
    try:
        import gevent
        import gevent.monkey
        gevent.monkey.patch_all()
        async_mode = 'gevent'
    except ImportError:
        async_mode = 'threading'

# CORS 配置 - 限制允许的来源
allowed_origins = config.ALLOWED_ORIGINS.split(',') if config.ALLOWED_ORIGINS else '*'
socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode=async_mode)

# 预热数据库连接池
print("预热数据库连接池...")
for db_name in ['home', 'kb', 'case']:
    _ = get_pool(db_name)
print("数据库连接池初始化完成")

# 静态文件优化 - 添加缓存头
@app.after_request
def add_cache_headers(response):
    """为静态资源添加缓存头"""
    # 静态文件缓存
    if request.path.startswith('/static/'):
        response.cache_control.max_age = config.BaseConfig.STATIC_CACHE_TIME
        response.cache_control.public = True
        response.headers['Cache-Control'] = f'public, max-age={config.BaseConfig.STATIC_CACHE_TIME}'
    # API响应不缓存
    elif request.path.startswith('/kb/api/') or request.path.startswith('/auth/api/') or request.path.startswith('/unified/api/'):
        response.cache_control.no_cache = True
        response.cache_control.no_store = True
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# 初始化工单系统数据库
print("初始化工单系统数据库...")
init_case_database()

# 注册蓝图
print("注册路由系统...")
app.register_blueprint(home_bp)
app.register_blueprint(kb_bp)
app.register_blueprint(kb_management_bp)
app.register_blueprint(case_bp)
app.register_blueprint(unified_bp)
app.register_blueprint(api_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(user_management_bp)
app.register_blueprint(monitoring_bp)

# 排除登录端点的 CSRF 保护（这些是公开接口）
if csrf:
    csrf.exempt(kb_bp)
    csrf.exempt(kb_management_bp)  # 知识库管理后台也需要exempt
    csrf.exempt(case_bp)
    csrf.exempt(auth_bp)
    csrf.exempt(user_management_bp)
    csrf.exempt(home_bp)  # 官网系统的公开接口（如联系表单）不需要 CSRF 保护

# 注册SocketIO事件
register_socketio_events(socketio)

print("=" * 60)
print("云户科技网站启动完成")
print("=" * 60)
print(f"官网首页: http://{config.FLASK_HOST}:{config.FLASK_PORT}/")
print(f"知识库系统: http://{config.FLASK_HOST}:{config.FLASK_PORT}/kb")
print(f"工单系统: http://{config.FLASK_HOST}:{config.FLASK_PORT}/case")
print(f"用户管理: http://{config.FLASK_HOST}:{config.FLASK_PORT}/user-mgmt/")
print(f"API 文档: http://{config.FLASK_HOST}:{config.FLASK_PORT}/api/docs")
print(f"监控仪表板: http://{config.FLASK_HOST}:{config.FLASK_PORT}/monitoring/")
print("=" * 60)


# 初始化监控服务
from services.monitoring_service import init_monitoring_service
from middlewares.monitoring_middleware import MonitoringMiddleware

# 创建监控服务实例
monitoring_config = {
    'cpu_warning_threshold': float(os.getenv('CPU_WARNING_THRESHOLD', '70')),
    'cpu_critical_threshold': float(os.getenv('CPU_CRITICAL_THRESHOLD', '90')),
    'memory_warning_threshold': float(os.getenv('MEMORY_WARNING_THRESHOLD', '70')),
    'memory_critical_threshold': float(os.getenv('MEMORY_CRITICAL_THRESHOLD', '85')),
    'disk_warning_threshold': float(os.getenv('DISK_WARNING_THRESHOLD', '80')),
    'disk_critical_threshold': float(os.getenv('DISK_CRITICAL_THRESHOLD', '90')),
    'email_enabled': os.getenv('MONITORING_EMAIL_ENABLED', 'true').lower() == 'true',
    'email_recipients': os.getenv('MONITORING_EMAIL_RECIPIENTS', ''),
    'monitor_interval': int(os.getenv('MONITOR_INTERVAL', '60')),
}

monitoring_service = init_monitoring_service(monitoring_config)

# 启动监控服务
try:
    monitoring_service.start()
    print("监控服务已启动")
except Exception as e:
    print(f"监控服务启动失败: {e}")

# 注册监控中间件
try:
    monitoring_middleware = MonitoringMiddleware(app)
    print("监控中间件已注册")
except Exception as e:
    print(f"监控中间件注册失败: {e}")


if __name__ == '__main__':
    # 使用socketio.run以支持WebSocket
    try:
        socketio.run(app, host=config.FLASK_HOST, port=config.FLASK_PORT,
                     debug=config.BaseConfig.DEBUG, allow_unsafe_werkzeug=True)
    finally:
        # 停止监控服务
        monitoring_service.stop()
        print("监控服务已停止")
