"""
密码策略配置模块
定义密码强度要求和验证规则
"""
import re

# 普通用户密码策略
USER_PASSWORD_POLICY = {
    'min_length': 8,
    'max_length': 50,
    'require_uppercase': False,  # 不强制要求大写字母
    'require_lowercase': True,    # 必须包含小写字母
    'require_digit': True,        # 必须包含数字
    'require_special': False,     # 不强制要求特殊字符
    'forbid_common': True,        # 禁止常见弱密码
    'min_unique_chars': 4,        # 至少4个不重复字符
}

# 管理员密码策略（更严格）
ADMIN_PASSWORD_POLICY = {
    'min_length': 10,
    'max_length': 50,
    'require_uppercase': True,    # 必须包含大写字母
    'require_lowercase': True,    # 必须包含小写字母
    'require_digit': True,        # 必须包含数字
    'require_special': True,     # 必须包含特殊字符
    'forbid_common': True,        # 禁止常见弱密码
    'min_unique_chars': 6,        # 至少6个不重复字符
}

# 常见弱密码列表
WEAK_PASSWORDS = [
    '123456', 'password', 'qwerty', 'abc123', '111111',
    '12345678', '123456789', 'admin123', 'password123',
    'YHKB@2024', 'admin@2024', 'root123', 'test123',
    '1234567890', 'qwertyuiop', 'letmein', 'welcome',
    'monkey', 'dragon', 'sunshine', 'iloveyou',
    'admin', 'root', 'test', 'guest', 'passw0rd'
]

# 允许的特殊字符
SPECIAL_CHARS = '!@#$%^&*(),.?":{}|<>'

# 密码强度等级描述
PASSWORD_STRENGTH = {
    'weak': '弱',
    'medium': '中',
    'strong': '强',
    'very_strong': '非常强'
}


def get_password_policy(role: str) -> dict:
    """
    根据用户角色获取密码策略

    Args:
        role: 用户角色 ('admin', 'user', 'customer' 等)

    Returns:
        dict: 密码策略配置
    """
    return ADMIN_PASSWORD_POLICY if role == 'admin' else USER_PASSWORD_POLICY


def check_password_strength(password: str) -> dict:
    """
    检查密码强度

    Args:
        password: 密码

    Returns:
        dict: 包含强度等级和建议的字典
    """
    score = 0
    feedback = []

    # 长度评分
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1

    # 字符类型评分
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[0-9]', password):
        score += 1
    if re.search(rf'[{re.escape(SPECIAL_CHARS)}]', password):
        score += 1

    # 确定强度等级
    if score <= 2:
        strength = 'weak'
        feedback.append('密码强度较弱，建议增加长度和字符类型')
    elif score <= 4:
        strength = 'medium'
        feedback.append('密码强度中等，可以继续增强')
    elif score == 5:
        strength = 'strong'
        feedback.append('密码强度良好')
    else:
        strength = 'very_strong'
        feedback.append('密码非常强')

    return {
        'strength': strength,
        'score': score,
        'feedback': feedback,
        'max_score': 6
    }
