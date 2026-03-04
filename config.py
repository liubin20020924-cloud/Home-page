"""
云户科技网站统一配置文件

所有配置从 .env 文件读取，如未设置则使用默认值。
生产环境请务必配置 .env 文件并修改敏感配置。
"""

import os
import secrets
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


# ============================================
# Flask 基础配置
# ============================================
class BaseConfig:
    """基础配置类"""
    # Flask 安全密钥 - 生产环境请必须修改！
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY') or secrets.token_hex(32)

    # 调试模式
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # JSON 中文支持
    JSON_AS_ASCII = False

    # Session 配置
    SESSION_COOKIE_NAME = os.getenv('SESSION_COOKIE_NAME', 'cloud_doors_session')
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # 启用 HTTPS 后改为 True
    SESSION_COOKIE_MAX_AGE = int(os.getenv('SESSION_TIMEOUT', '10800'))  # 默认 3 小时
    PERMANENT_SESSION_LIFETIME = int(os.getenv('SESSION_TIMEOUT', '10800'))

    # 最大上传大小
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 默认 16MB

    # 静态文件缓存时间
    STATIC_CACHE_TIME = int(os.getenv('STATIC_CACHE_TIME', '3600'))  # 默认 1 小时


# ============================================
# Flask 服务器配置
# ============================================
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
SITE_URL = os.getenv('SITE_URL', f'http://{FLASK_HOST}:{FLASK_PORT}')


# ============================================
# 数据库配置
# ============================================
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

DB_NAME_HOME = os.getenv('DB_NAME_HOME', 'clouddoors_db')
DB_NAME_KB = os.getenv('DB_NAME_KB', 'YHKB')
DB_NAME_CASE = os.getenv('DB_NAME_CASE', 'casedb')

# 数据库连接池配置
DB_POOL_MAX_CONNECTIONS = int(os.getenv('DB_POOL_MAX_CONNECTIONS', '20'))
DB_POOL_MIN_CACHED = int(os.getenv('DB_POOL_MIN_CACHED', '5'))
DB_POOL_MAX_CACHED = int(os.getenv('DB_POOL_MAX_CACHED', '10'))
DB_POOL_MAX_SHARED = int(os.getenv('DB_POOL_MAX_SHARED', '5'))


# ============================================
# 邮件配置
# ============================================
# 邮件服务器配置
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.exmail.qq.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', '465'))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'support@cloud-doors.com')

# SMTP 配置（用于 EmailService，兼容旧代码）
SMTP_SERVER = MAIL_SERVER
SMTP_PORT = MAIL_PORT
SMTP_USERNAME = MAIL_USERNAME
SMTP_PASSWORD = MAIL_PASSWORD
EMAIL_SENDER = MAIL_DEFAULT_SENDER

# 联系邮箱
CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'support@cloud-doors.com')


# ============================================
# Trilium 配置
# ============================================
TRILIUM_SERVER_URL = os.getenv('TRILIUM_SERVER_URL', 'http://127.0.0.1:8080')
TRILIUM_TOKEN = os.getenv('TRILIUM_TOKEN', '')
TRILIUM_SERVER_HOST = os.getenv('TRILIUM_SERVER_HOST', '127.0.0.1:8080')
TRILIUM_LOGIN_USERNAME = os.getenv('TRILIUM_LOGIN_USERNAME', '')
TRILIUM_LOGIN_PASSWORD = os.getenv('TRILIUM_LOGIN_PASSWORD', '')


# ============================================
# 知识库系统配置
# ============================================
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '180'))
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'YHKB@2024')

ENABLE_CONTENT_VIEW = True
CONTENT_CACHE_TIMEOUT = 300

# HTML 内容安全配置
ALLOWED_HTML_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'div', 'span',
    'strong', 'b', 'em', 'i', 'u', 's',
    'ul', 'ol', 'li',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'a', 'img',
    'pre', 'code',
    'blockquote', 'hr'
]

ALLOWED_HTML_ATTRIBUTES = {
    '*': ['class', 'style', 'id'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'table': ['border', 'cellpadding', 'cellspacing', 'width'],
}

# 调试配置
DEBUG_MODE = False
DEBUG_ADMIN_ONLY = True

# 图片处理配置
ENABLE_IMAGE_PROXY = True

# 浏览器优化配置
ENABLE_EDGE_OPTIMIZATION = True
EDGE_COMPATIBILITY_MODE = True
CACHE_CONTROL_HEADERS = True


# ============================================
# 路由配置
# ============================================
HOME_PREFIX = ''
KB_PREFIX = '/kb'
CASE_PREFIX = '/case'


# ============================================
# CORS 配置
# ============================================
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*')


# ============================================
# Redis 配置
# ============================================
REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'False').lower() == 'true'
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')


# ============================================
# CDN 配置
# ============================================
CDN_ENABLED = os.getenv('CDN_ENABLED', 'False').lower() == 'true'
CDN_DOMAIN = os.getenv('CDN_DOMAIN', '')
CDN_PROTOCOL = os.getenv('CDN_PROTOCOL', 'https')


# ============================================
# 图片优化配置
# ============================================
IMAGE_QUALITY = int(os.getenv('IMAGE_QUALITY', '80'))
IMAGE_ENABLE_WEBP = os.getenv('IMAGE_ENABLE_WEBP', 'True').lower() == 'true'
IMAGE_AUTO_COMPRESS = os.getenv('IMAGE_AUTO_COMPRESS', 'True').lower() == 'true'
IMAGE_CACHE_TTL = int(os.getenv('IMAGE_CACHE_TTL', '604800'))


# ============================================
# 缓存配置
# ============================================
CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '604800'))
CACHE_KEY_PREFIX = os.getenv('CACHE_KEY_PREFIX', 'yundour_')


# ============================================
# 日志配置
# ============================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10'))
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))


# ============================================
# 配置检查函数
# ============================================
def check_config():
    """检查关键配置项，返回警告和错误列表"""
    warnings = []
    errors = []

    # 检查生产环境配置
    if not BaseConfig.DEBUG:
        if BaseConfig.SECRET_KEY == secrets.token_hex(32) and not os.getenv('FLASK_SECRET_KEY'):
            errors.append('生产环境使用了随机生成的SECRET_KEY，请设置 FLASK_SECRET_KEY 环境变量')

    # 检查数据库配置
    if not DB_PASSWORD:
        errors.append('DB_PASSWORD 未设置，数据库连接将失败')

    if DB_HOST == '127.0.0.1' and not BaseConfig.DEBUG:
        warnings.append('生产环境数据库地址使用默认值 127.0.0.1，请确认 DB_HOST 配置正确')

    # 检查邮件配置
    if not SMTP_PASSWORD and not MAIL_PASSWORD:
        errors.append('SMTP_PASSWORD 和 MAIL_PASSWORD 均未设置，邮件功能可能无法使用')

    if SMTP_USERNAME and '@qq.com' in SMTP_USERNAME:
        warnings.append('邮件配置使用QQ邮箱，确保已配置正确的授权码')

    # 检查 Trilium 配置
    if not TRILIUM_TOKEN:
        errors.append('TRILIUM_TOKEN 未设置，知识库功能将无法使用')

    if not TRILIUM_LOGIN_PASSWORD and TRILIUM_LOGIN_USERNAME:
        warnings.append('TRILIUM_LOGIN_PASSWORD 未设置，Trilium 认证功能可能无法使用')

    if TRILIUM_SERVER_URL == 'http://127.0.0.1:8080' and not BaseConfig.DEBUG:
        warnings.append('生产环境 Trilium 地址使用默认值，请确认 TRILIUM_SERVER_URL 配置正确')

    # 检查默认管理员密码
    if DEFAULT_ADMIN_PASSWORD == 'YHKB@2024':
        warnings.append('知识库默认管理员密码未修改，建议立即修改')

    # 检查 .env 文件
    if not os.path.exists('.env'):
        warnings.append('未找到 .env 文件，请创建并配置环境变量')

    # 检查 Redis 配置
    if REDIS_ENABLED and REDIS_HOST == '127.0.0.1' and not BaseConfig.DEBUG:
        warnings.append('生产环境 Redis 地址使用默认值，请确认 REDIS_HOST 配置正确')

    # 检查网站域名配置
    if SITE_URL == 'http://0.0.0.0:5000' and not BaseConfig.DEBUG:
        errors.append('生产环境 SITE_URL 使用默认值，请设置为实际网站域名')

    # 检查 CDN 配置
    if CDN_ENABLED and not CDN_DOMAIN:
        errors.append('CDN_ENABLED 为 True 但未设置 CDN_DOMAIN')

    return warnings, errors


# ============================================
# 启动时自动检查配置
# ============================================
if __name__ != '__main__':
    config_warnings, config_errors = check_config()
    if config_warnings or config_errors:
        print("=" * 60)
        print("配置检查结果:")
        if config_errors:
            print("\n【严重错误】: ")
            for error in config_errors:
                print(f"  [X] {error}")
        if config_warnings:
            print("\n【警告提示】: ")
            for warning in config_warnings:
                print(f"  [!] {warning}")
        print("=" * 60)
        if config_errors:
            print("\n注意：存在严重配置错误，建议立即修复！\n")
    else:
        print("=" * 60)
        print("配置检查通过 [OK]")
        print("=" * 60)
