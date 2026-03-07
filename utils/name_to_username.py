"""
用户名转换工具模块
"""
import re
import secrets


def name_to_username(display_name: str) -> str:
    """
    将显示名称转换为用户名
    - 英文：直接使用（去除特殊字符，保留字母、数字、点、下划线、短横线）
    - 中文：转换为全拼
    - 混合：中文转拼音，英文保留

    Args:
        display_name: 显示名称

    Returns:
        str: 用户名
    """
    try:
        from pypinyin import lazy_pinyin, Style

        # 检查是否包含中文字符
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', display_name))

        if has_chinese:
            # 包含中文，转换为拼音
            # 使用全拼，首字母大写，用空格分隔
            pinyin_list = lazy_pinyin(display_name, style=Style.NORMAL)
            username = ''.join(pinyin_list)
        else:
            # 纯英文/数字，直接使用
            username = display_name

        # 清理用户名：只保留字母、数字、点、下划线、短横线
        username = re.sub(r'[^a-zA-Z0-9._-]', '', username)

        # 确保用户名不为空
        if not username:
            username = f'user_{secrets.token_hex(4)}'

        # 转换为小写
        username = username.lower()

        return username

    except ImportError:
        # 降级方案：只保留字母、数字、点、下划线、短横线
        username = re.sub(r'[^a-zA-Z0-9._-]', '', display_name)
        if not username:
            username = f'user_{secrets.token_hex(4)}'
        return username.lower()
    except Exception as e:
        from common.logger import logger
        logger.error(f"转换用户名失败: {str(e)}")
        return f'user_{secrets.token_hex(4)}'
