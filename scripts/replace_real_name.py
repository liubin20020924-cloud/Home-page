#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量替换 real_name 为 display_name
删除 password_md5 相关代码
"""
import os
import re
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 需要处理的文件列表
FILES_TO_PROCESS = [
    'routes/case_bp.py',
    'services/socketio_service.py',
    'templates/case/base.html',
    'templates/case/submit_ticket.html',
    'templates/case/ticket_list.html',
    'templates/case/ticket_detail.html',
    'templates/kb/user_management.html',
]

def replace_in_file(file_path):
    """替换单个文件中的 real_name"""
    print(f"\n处理文件: {file_path}")

    file_path = PROJECT_ROOT / file_path
    if not file_path.exists():
        print(f"  [跳过] 文件不存在")
        return

    try:
        # 读取文件内容
        content = file_path.read_text(encoding='utf-8')

        original_content = content

        # 替换规则
        replacements = [
            # Python代码中的 session.get('real_name')
            (r"session\.get\('real_name'\)", r"session.get('display_name', '')"),
            # Python代码中的 session.get("real_name")
            (r'session\.get\("real_name"\)', r'session.get("display_name", "")'),

            # Python代码中的 user.get('real_name')
            (r"user\.get\('real_name'\)", r"user.get('display_name', '')"),
            (r'user\.get\("real_name"\)', r'user.get("display_name", "")'),

            # Python代码中的 customer.get('real_name')
            (r"customer\.get\('real_name'\)", r"customer.get('display_name', '')"),

            # 模板中的 session.get('real_name')
            (r"\{\{\s*session\.get\(['\"]real_name['\"]\)\s*\}\}", r"{{ session.get('display_name', '') }}"),

            # 模板中的 current_user.real_name
            (r"\{\{\s*current_user\.real_name\s*\}\}", r"{{ current_user.display_name }}"),

            # SQL中的 real_name 字段
            (r",\s*real_name,", r", "),
            (r",\s*real_name\s*", r""),
            (r"\breal_name\b", r"display_name"),  # 最后替换单词 real_name

            # ORDER BY real_name
            (r"ORDER BY\s+real_name", r"ORDER BY display_name"),

            # password_md5 相关（删除）
            (r",\s*password_md5\b", r""),
        ]

        # 应用替换
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        # 检查是否有变化
        if content != original_content:
            # 备份原文件
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            backup_path.write_text(original_content, encoding='utf-8')
            print(f"  [备份] {backup_path.name}")

            # 写入新内容
            file_path.write_text(content, encoding='utf-8')
            print(f"  [完成] 已替换并保存")
        else:
            print(f"  [跳过] 没有需要替换的内容")

    except Exception as e:
        print(f"  [错误] {str(e)}")


def main():
    print("=" * 60)
    print("批量替换 real_name 为 display_name")
    print("=" * 60)

    for file_path in FILES_TO_PROCESS:
        replace_in_file(file_path)

    print("\n" + "=" * 60)
    print("处理完成！")
    print("=" * 60)
    print("\n注意事项：")
    print("1. 已自动创建备份文件（.backup后缀）")
    print("2. 请检查修改后的代码是否正确")
    print("3. 如有问题，可以从备份文件恢复")


if __name__ == '__main__':
    main()
