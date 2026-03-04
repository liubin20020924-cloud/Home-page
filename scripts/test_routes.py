#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试路由是否正确"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')

# 测试路由逻辑
@app.route('/case/<path:filename>')
def case_serve_frontend(filename):
    """提供前端文件"""
    print(f"Request for: {filename}")
    try:
        # 如果 filename 不包含扩展名，添加 .html
        if not filename.endswith('.html'):
            template_path = f'case/{filename}.html'
            print(f"Rendering: {template_path}")
            return render_template(template_path)
        else:
            template_path = f'case/{filename}'
            print(f"Rendering: {template_path}")
            return render_template(template_path)
    except Exception as e:
        print(f"Error: {e}")
        return f"404 - 文件未找到: {filename}", 404

if __name__ == '__main__':
    print("=" * 60)
    print("测试路由逻辑")
    print("=" * 60)
    
    # 列出所有可用的 case 模板
    print("\n可用的模板:")
    for template in app.jinja_env.list_templates():
        if 'case' in template:
            print(f"  - {template}")
    
    print("\n测试路由:")
    print("  /case/ticket-list → case/ticket_list.html")
    print("  /case/ticket-list.html → case/ticket_list.html")
    print("=" * 60)
