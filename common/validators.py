# -*- coding: utf-8 -*-
"""
输入验证和清理模块
防止 XSS、SQL 注入等安全攻击
"""

import re
from bleach import clean
from html import escape
from typing import Optional, List, Dict, Any

# 允许的 HTML 标签（白名单）
ALLOWED_TAGS = [
    'p', 'b', 'i', 'u', 'em', 'strong', 'a', 'br',
    'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre'
]

# 允许的 HTML 属性（白名单）
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height']
}

# 允许的 CSS 属性（白名单）
ALLOWED_STYLES = []

# 允许的协议
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto', 'tel']


def sanitize_html(content: str, tags: Optional[List[str]] = None,
                 attributes: Optional[Dict[str, List[str]]] = None) -> str:
    """清理 HTML 内容，防止 XSS 攻击
    
    Args:
        content: 待清理的 HTML 内容
        tags: 允许的 HTML 标签列表，默认使用预定义的白名单
        attributes: 允许的 HTML 属性字典，默认使用预定义的白名单
    
    Returns:
        清理后的安全 HTML 内容
    
    Example:
        >>> sanitize_html('<script>alert("xss")</script>')
        'alert("xss")'
        >>> sanitize_html('<a href="javascript:alert(1)">Click</a>')
        '<a>Click</a>'
    """
    if not content:
        return ''
    
    return clean(
        content,
        tags=tags or ALLOWED_TAGS,
        attributes=attributes or ALLOWED_ATTRIBUTES,
        styles=ALLOWED_STYLES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
        strip_comments=True
    )


def escape_html(content: str) -> str:
    """转义 HTML 特殊字符（简单转义，不保留任何 HTML）
    
    Args:
        content: 待转义的内容
    
    Returns:
        转义后的安全内容
    
    Example:
        >>> escape_html('<script>alert("xss")</script>')
        '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'
    """
    if not content:
        return ''
    
    return escape(content, quote=True)


def sanitize_text(content: str, max_length: int = 5000) -> str:
    """清理纯文本内容（移除所有 HTML 标签）
    
    Args:
        content: 待清理的文本内容
        max_length: 最大允许长度
    
    Returns:
        清理后的纯文本
    """
    if not content:
        return ''
    
    # 移除所有 HTML 标签
    text = re.sub(r'<[^>]+>', '', content)
    
    # 转义 HTML 特殊字符
    text = escape_html(text)
    
    # 限制长度
    if max_length > 0 and len(text) > max_length:
        text = text[:max_length] + '...'
    
    return text


def sanitize_email(email: str) -> str:
    """清理并验证邮箱地址
    
    Args:
        email: 待验证的邮箱地址
    
    Returns:
        清理后的邮箱地址，或空字符串（如果无效）
    """
    if not email:
        return ''
    
    # 移除前后空格
    email = email.strip().lower()
    
    # 基本的邮箱格式验证
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return ''
    
    return email


def sanitize_phone(phone: str) -> str:
    """清理电话号码
    
    Args:
        phone: 待清理的电话号码
    
    Returns:
        清理后的电话号码（只保留数字）
    """
    if not phone:
        return ''
    
    # 只保留数字
    phone = re.sub(r'[^\d]', '', phone)
    
    # 验证长度（中国大陆手机号：11位）
    if len(phone) == 11:
        return phone
    
    return ''


def sanitize_filename(filename: str) -> str:
    """清理文件名（防止路径遍历攻击）
    
    Args:
        filename: 待清理的文件名
    
    Returns:
        清理后的安全文件名
    """
    if not filename:
        return ''
    
    # 移除路径分隔符
    filename = re.sub(r'[\\/]', '', filename)
    
    # 移除危险字符
    filename = re.sub(r'[:*?"<>|]', '', filename)
    
    # 限制文件名长度
    max_length = 255
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:max_length - len(ext) - 1] + ('.' + ext if ext else '')
    
    return filename


def sanitize_username(username: str) -> str:
    """清理用户名
    
    Args:
        username: 待清理的用户名
    
    Returns:
        清理后的用户名
    """
    if not username:
        return ''
    
    # 只允许字母、数字、下划线、中文
    username = re.sub(r'[^\w\u4e00-\u9fff]', '', username)
    
    # 限制长度
    username = username[:50]
    
    return username


def validate_positive_integer(value: Any, default: int = 0,
                               max_value: Optional[int] = None) -> int:
    """验证并返回正整数
    
    Args:
        value: 待验证的值
        default: 默认值（当验证失败时返回）
        max_value: 最大允许值
    
    Returns:
        验证后的正整数
    """
    try:
        num = int(value)
        if num < 0:
            return default
        if max_value is not None and num > max_value:
            return max_value
        return num
    except (ValueError, TypeError):
        return default


def sanitize_json_input(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """根据模式验证和清理 JSON 输入
    
    Args:
        data: 待验证的 JSON 数据
        schema: 验证模式字典
            {
                'field_name': {
                    'type': str,          # 期望的类型：str, int, float, bool, list, dict
                    'required': bool,     # 是否必填
                    'default': Any,       # 默认值
                    'sanitize': callable, # 可选的清理函数
                    'max_length': int,    # 最大长度（针对字符串）
                    'min': int,           # 最小值（针对数字）
                    'max': int,           # 最大值（针对数字）
                    'allowed_values': list # 允许的值列表
                }
            }
    
    Returns:
        验证和清理后的数据
    """
    result = {}
    
    for field_name, field_schema in schema.items():
        if field_name not in data:
            if field_schema.get('required', False):
                result[field_name] = field_schema.get('default')
            continue
        
        value = data[field_name]
        expected_type = field_schema.get('type', str)
        
        # 类型转换
        try:
            if expected_type == str:
                value = str(value)
            elif expected_type == int:
                value = int(value)
            elif expected_type == float:
                value = float(value)
            elif expected_type == bool:
                value = bool(value)
        except (ValueError, TypeError):
            value = field_schema.get('default')
        
        # 清理
        sanitize_func = field_schema.get('sanitize')
        if sanitize_func and callable(sanitize_func):
            value = sanitize_func(value)
        
        # 验证
        if isinstance(value, str):
            max_length = field_schema.get('max_length')
            if max_length and len(value) > max_length:
                value = value[:max_length]
        
        if isinstance(value, (int, float)):
            min_val = field_schema.get('min')
            max_val = field_schema.get('max')
            if min_val is not None and value < min_val:
                value = min_val
            if max_val is not None and value > max_val:
                value = max_val
        
        allowed_values = field_schema.get('allowed_values')
        if allowed_values and value not in allowed_values:
            value = field_schema.get('default')
        
        result[field_name] = value
    
    return result


def is_safe_url(url: str, allowed_hosts: List[str]) -> bool:
    """验证 URL 是否安全（防止开放重定向攻击）
    
    Args:
        url: 待验证的 URL
        allowed_hosts: 允许的主机名列表
    
    Returns:
        是否安全
    """
    if not url:
        return False
    
    from urllib.parse import urlparse, urlunparse
    
    # 允许相对路径
    if url.startswith('/') and not url.startswith('//'):
        return True
    
    try:
        parsed = urlparse(url)
        
        # 禁止 javascript: 等危险协议
        if parsed.scheme and parsed.scheme.lower() not in ('http', 'https'):
            return False
        
        # 验证主机名
        if parsed.netloc:
            hostname = parsed.netloc.split(':')[0]
            if hostname not in allowed_hosts:
                return False
        
        return True
    except Exception:
        return False


# 工单系统输入验证模式
TICKET_SCHEMA = {
    'customer_name': {'type': str, 'required': True, 'max_length': 200, 'sanitize': sanitize_text},
    'customer_contact_name': {'type': str, 'required': True, 'max_length': 100, 'sanitize': sanitize_text},
    'customer_contact_phone': {'type': str, 'required': True, 'max_length': 20, 'sanitize': sanitize_phone},
    'customer_email': {'type': str, 'required': True, 'max_length': 100, 'sanitize': sanitize_email},
    'issue_type': {'type': str, 'required': True, 'max_length': 50,
                  'allowed_values': ['technical', 'service', 'complaint', 'other']},
    'priority': {'type': str, 'required': True, 'max_length': 20,
                'allowed_values': ['low', 'medium', 'high', 'urgent']},
    'product': {'type': str, 'required': False, 'max_length': 200, 'sanitize': sanitize_text},
    'title': {'type': str, 'required': True, 'max_length': 500, 'sanitize': sanitize_text},
    'content': {'type': str, 'required': True, 'max_length': 10000, 'sanitize': sanitize_html}
}

# 知识库输入验证模式
KB_SCHEMA = {
    'KB_Name': {'type': str, 'required': True, 'max_length': 200, 'sanitize': sanitize_text},
    'KB_Category': {'type': str, 'required': True, 'max_length': 100, 'sanitize': sanitize_text},
    'KB_Description': {'type': str, 'required': True, 'max_length': 1000, 'sanitize': sanitize_text},
    'KB_link': {'type': str, 'required': False, 'max_length': 500, 'sanitize': sanitize_text}
}

# 用户输入验证模式
USER_SCHEMA = {
    'username': {'type': str, 'required': True, 'max_length': 50, 'sanitize': sanitize_username},
    'display_name': {'type': str, 'required': False, 'max_length': 100, 'sanitize': sanitize_text},
    'email': {'type': str, 'required': False, 'max_length': 100, 'sanitize': sanitize_email},
    'password': {'type': str, 'required': True, 'min_length': 6, 'max_length': 100}
}


# ============================================
# 兼容函数（保持向后兼容性）
# ============================================

def validate_required(data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, Dict[str, str]]:
    """验证必填字段（兼容旧 API）
    
    Args:
        data: 待验证的数据字典
        required_fields: 必填字段列表
    
    Returns:
        (is_valid, errors) 元组
    """
    errors = {}
    
    for field in required_fields:
        if field not in data or not data[field] or (isinstance(data[field], str) and not data[field].strip()):
            errors[field] = f'{field} 为必填字段'
    
    return (len(errors) == 0, errors)


def validate_email(email: str) -> tuple[bool, str]:
    """验证邮箱地址（兼容旧 API）
    
    Args:
        email: 待验证的邮箱地址
    
    Returns:
        (is_valid, error_message) 元组
    """
    if not email:
        return (False, '邮箱不能为空')
    
    cleaned = sanitize_email(email)
    if not cleaned:
        return (False, '邮箱格式不正确')
    
    return (True, '')


def validate_phone(phone: str) -> tuple[bool, str]:
    """验证电话号码（兼容旧 API）
    
    Args:
        phone: 待验证的电话号码
    
    Returns:
        (is_valid, error_message) 元组
    """
    if not phone:
        return (False, '电话不能为空')
    
    cleaned = sanitize_phone(phone)
    if not cleaned:
        return (False, '电话格式不正确')
    
    return (True, '')


def validate_username(username: str) -> tuple[bool, str]:
    """验证用户名（兼容旧 API）
    
    Args:
        username: 待验证的用户名
    
    Returns:
        (is_valid, error_message) 元组
    """
    if not username:
        return (False, '用户名不能为空')
    
    cleaned = sanitize_username(username)
    if not cleaned:
        return (False, '用户名格式不正确')
    
    if len(cleaned) < 3:
        return (False, '用户名至少需要3个字符')
    
    return (True, '')


def validate_password(password: str) -> tuple[bool, str]:
    """验证密码（兼容旧 API）

    Args:
        password: 待验证的密码

    Returns:
        (is_valid, error_message) 元组
    """
    if not password:
        return (False, '密码不能为空')

    if len(password) < 6:
        return (False, '密码至少需要6个字符')

    # 检查密码强度（至少包含字母和数字）
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)

    if not (has_letter and has_digit):
        return (False, '密码需要包含字母和数字')

    return (True, '')


def check_password_strength(password: str) -> tuple[bool, str]:
    """检查密码复杂度（不阻止登录，仅提示）

    用于登录后的密码强度检查，返回是否合格和详细的强度信息

    Args:
        password: 待检查的密码

    Returns:
        (is_strong, message) 元组
        - is_strong: True表示密码强度合格，False表示建议修改
        - message: 描述性消息，说明密码强度问题或确认强度合格
    """
    issues = []

    # 检查密码长度
    if len(password) < 8:
        issues.append('长度不足8位')

    # 检查是否包含大写字母
    if not any(c.isupper() for c in password):
        issues.append('缺少大写字母')

    # 检查是否包含数字
    if not any(c.isdigit() for c in password):
        issues.append('缺少数字')

    # 检查是否包含特殊字符
    if not any(c in '!@#$%^&*(),.?":{}|<>~`-_=+[]' for c in password):
        issues.append('缺少特殊字符')

    if not issues:
        return True, '密码强度良好'
    else:
        issue_str = '、'.join(issues)
        return False, f'密码强度不足（{issue_str}），建议修改'


def validate_user_data(data: Dict[str, Any], skip_username_validation: bool = False) -> tuple[bool, Dict[str, str]]:
    """验证用户数据（兼容旧 API）

    Args:
        data: 待验证的用户数据
        skip_username_validation: 是否跳过用户名验证（更新用户时）

    Returns:
        (is_valid, errors) 元组
    """
    errors = {}

    # 验证用户名（如果需要）
    if not skip_username_validation:
        username = data.get('username')
        is_valid, msg = validate_username(username)
        if not is_valid:
            errors['username'] = msg
    
    # 验证邮箱（如果提供）
    email = data.get('email')
    if email:
        is_valid, msg = validate_email(email)
        if not is_valid:
            errors['email'] = msg
    
    # 验证密码（如果提供）
    password = data.get('password')
    if password:
        is_valid, msg = validate_password(password)
        if not is_valid:
            errors['password'] = msg
    
    return (len(errors) == 0, errors)
