"""
官网系统路由蓝图
"""
from flask import Blueprint, request, render_template, send_from_directory
from datetime import datetime
import os
import pymysql
import secrets
import re
from werkzeug.security import generate_password_hash
from common.response import success_response, error_response, validation_error_response, server_error_response
from common.validators import validate_required, validate_email
from common.logger import logger, log_exception
from common.database_context import db_connection

home_bp = Blueprint('home', __name__)


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

        logger.info(f"将显示名称 '{display_name}' 转换为用户名: '{username}'")
        return username

    except ImportError:
        logger.warning("pypinyin 库未安装，使用简单转换逻辑")
        # 降级方案：只保留字母、数字、点、下划线、短横线
        username = re.sub(r'[^a-zA-Z0-9._-]', '', display_name)
        if not username:
            username = f'user_{secrets.token_hex(4)}'
        return username.lower()
    except Exception as e:
        logger.error(f"转换用户名失败: {str(e)}")
        return f'user_{secrets.token_hex(4)}'


@home_bp.route('/')
def index():
    """官网首页"""
    return render_template('home/index.html', now=datetime.now)


@home_bp.route('/about')
def about():
    """关于我们页面"""
    return render_template('home/about.html', now=datetime.now)


@home_bp.route('/parts')
def parts():
    """备件库页面"""
    return render_template('home/parts.html', now=datetime.now)


@home_bp.route('/service-guarantee')
def service_guarantee():
    """服务保障体系页面"""
    return render_template('home/service-guarantee.html', now=datetime.now)


@home_bp.route('/cases')
def cases():
    """用户案例页面"""
    return render_template('home/cases.html', now=datetime.now)


@home_bp.route('/jpg/<path:filename>')
def serve_jpg_static(filename):
    """提供官网静态图片文件 - 映射到 static/home/images/"""
    try:
        # 获取项目根目录
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_dir = os.path.join(base_dir, 'static', 'home', 'images')
        return send_from_directory(image_dir, filename)
    except FileNotFoundError:
        logger.error(f"图片文件不存在: /jpg/{filename}")
        return "404 - Image Not Found", 404
    except Exception as e:
        logger.error(f"静态文件访问错误: {e}")
        return "500 - Internal Server Error", 500


@home_bp.route('/test-images')
def test_images():
    """图片测试页面"""
    return render_template('home_test_images.html')


@home_bp.route('/view-messages')
def view_messages():
    """留言管理页面"""
    return render_template('home/admin_messages.html')


@home_bp.route('/api/contact', methods=['POST'])
def contact():
    """联系表单提交

    提交官网联系表单，自动创建禁用客户账户（系统生成随机密码），并发送邮件到企业微信邮箱
    ---
    tags:
      - 官网
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        description: 联系表单数据
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - company_name
            - message
          properties:
            name:
              type: string
              description: 联系人姓名
              example: 张三
            company_name:
              type: string
              description: 公司名称
              example: 某某公司
            email:
              type: string
              format: email
              description: 联系人邮箱
              example: test@example.com
            phone:
              type: string
              description: 联系电话
              example: 13800138000
            message:
              type: string
              description: 留言内容
              example: 这是测试消息
    responses:
      200:
        description: 提交成功
        schema:
          $ref: '#/definitions/SuccessResponse'
      400:
        description: 参数错误
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: 服务器错误
        schema:
          $ref: '#/definitions/ErrorResponse'
        """
    try:
        data = request.get_json()

        # 记录接收到的数据（调试用）
        logger.info(f"收到联系表单数据: {data}")

        # 验证必填字段
        is_valid, errors = validate_required(data, ['name', 'email', 'company_name', 'message'])
        if not is_valid:
            logger.warning(f"联系表单验证失败: {errors}")
            return validation_error_response(errors)

        # 验证邮箱
        is_valid, msg = validate_email(data['email'])
        if not is_valid:
            return error_response(msg, 400)

        logger.info(f"收到联系表单: {data['name']} <{data['email']}> - 公司: {data['company_name']}")

        # 自动生成随机密码（由管理员通过邮件发送给客户）
        temp_password = secrets.token_urlsafe(10)
        password_hash = generate_password_hash(temp_password)

        # 根据姓名生成用户名（英文直接使用，中文转拼音）
        display_name = data['name']
        username = name_to_username(display_name)

        user_created = False
        user_info = None

        # 自动创建禁用客户账户
        try:
            with db_connection('kb') as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)

                # 检查用户是否已存在
                cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s",
                             (username, data['email']))
                existing_user = cursor.fetchone()

                if existing_user:
                    logger.warning(f"用户 {username} 或邮箱 {data['email']} 已存在，跳过创建")
                    user_created = False
                else:
                    # 插入新用户（状态为inactive，角色为customer）
                    insert_sql = """
                    INSERT INTO users (
                        username, password_hash, password_type, display_name, email,
                        company_name, phone, role, status, system, created_by, force_password_change,
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """
                    cursor.execute(insert_sql, (
                        username,  # 使用姓名生成的用户名
                        password_hash,
                        'werkzeug',  # 密码类型
                        display_name,  # 使用原始姓名作为显示名称
                        data['email'],
                        data['company_name'],
                        data.get('phone', ''),
                        'customer',
                        'inactive',  # 账户状态为禁用
                        'unified',  # 所属系统
                        'contact_form',  # 创建人
                        1,  # 强制修改密码
                    ))
                    conn.commit()
                    user_created = True
                    user_info = {
                        'username': username,
                        'password': temp_password,
                        'display_name': display_name,
                        'company_name': data['company_name'],
                        'email': data['email']
                    }
                    logger.info(f"成功创建客户账户: {username} ({display_name})")

        except ImportError:
            logger.warning("缺少 pymysql 模块，跳过用户创建")
            user_created = False
        except Exception as e:
            logger.error(f"创建用户账户失败: {str(e)}")
            user_created = False

        # 发送邮件通知到 support@cloud-doors.com
        try:
            logger.info("开始准备发送邮件...")
            from services.email_service import EmailService
            from config import MAIL_DEFAULT_SENDER

            email_service = EmailService()

            # 准备邮件收件人
            recipient_email = MAIL_DEFAULT_SENDER or 'support@cloud-doors.com'
            logger.info(f"邮件收件人: {recipient_email}")

            # 检查邮件配置
            if not email_service.smtp_username or not email_service.smtp_password:
                logger.warning("邮件配置不完整，无法发送邮件")
            else:
                logger.info("邮件配置完整，准备发送")

            # 构建邮件内容
            subject = f"【云户科技】新客户注册申请 - {data['company_name']}"

            # 如果创建了用户，包含登录信息
            if user_created and user_info:
                account_info_html = f"""
            <div class="info-item">
                <label>显示名称：</label>
                <span>{user_info['display_name']}</span>
            </div>
            <div class="info-item">
                <label>账户状态：</label>
                <span class="status-badge">待审核（已创建临时账户）</span>
            </div>
            <div class="account-box" style="background: #eff6ff; padding: 20px; border-radius: 8px; border: 1px solid #3b82f6; margin-top: 20px;">
                <h3 style="margin-top: 0; color: #1d4ed8; font-size: 16px; margin-bottom: 15px;">🔑 客户登录信息（请通过邮件发送给客户）</h3>
                <div style="background: white; padding: 15px; border-radius: 6px; border: 1px solid #bfdbfe;">
                    <p style="margin: 8px 0; color: #374151;"><strong>用户名：</strong>{user_info['username']}</p>
                    <p style="margin: 8px 0; color: #374151;"><strong>初始密码：</strong><span style="background: #fef3c7; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-size: 14px;">{user_info['password']}</span></p>
                    <p style="margin: 12px 0 8px 0; color: #ef4444; font-size: 13px;">⚠️ 请将此信息通过邮件发送给客户，提醒客户首次登录后修改密码</p>
                </div>
            </div>
                """
            else:
                account_info_html = f"""
            <div class="info-item">
                <label>显示名称：</label>
                <span>{display_name}</span>
            </div>
            <div class="info-item">
                <label>账户状态：</label>
                <span class="status-badge">待审核</span>
            </div>
                """

            content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, "Microsoft YaHei", sans-serif; line-height: 1.6; color: #333; background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%); padding: 40px 20px; margin: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #0A4DA2 0%, #2563eb 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; }}
        .content {{ padding: 30px; }}
        .info-item {{ margin-bottom: 20px; padding: 20px; background: #f9fafb; border-radius: 8px; border-left: 4px solid #0A4DA2; }}
        .info-item label {{ display: block; font-weight: 600; color: #6b7280; margin-bottom: 8px; font-size: 14px; }}
        .info-item span {{ font-size: 16px; color: #1a202c; }}
        .message-box {{ background: #fef3c7; padding: 20px; border-radius: 8px; border: 1px solid #fbbf24; }}
        .message-box h3 {{ margin-top: 0; color: #92400e; font-size: 18px; margin-bottom: 12px; }}
        .message-content {{ color: #374151; white-space: pre-wrap; line-height: 1.8; font-size: 15px; }}
        .status-badge {{ display: inline-block; padding: 6px 12px; border-radius: 6px; font-size: 14px; font-weight: 600; background: #fef3c7; color: #92400e; }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 新客户注册申请</h1>
        </div>
        <div class="content">
            <div class="info-item">
                <label>申请人姓名：</label>
                <span>{data['name']}</span>
            </div>
            <div class="info-item">
                <label>公司名称：</label>
                <span>{data['company_name']}</span>
            </div>
            <div class="info-item">
                <label>联系邮箱：</label>
                <span>{data['email']}</span>
            </div>
            <div class="info-item">
                <label>联系电话：</label>
                <span>{data.get('phone', '未提供')}</span>
            </div>
            {account_info_html}
            <div class="message-box">
                <h3>留言内容：</h3>
                <div class="message-content">{data['message']}</div>
            </div>
        </div>
        <div class="footer">
            <p>请及时审核并激活该客户账户</p>
            <p style="margin-top: 10px;">—<br>云户科技 | 专业IT服务商</p>
        </div>
    </div>
</body>
</html>
            """

            # 发送邮件
            logger.info("开始发送邮件...")
            success, message = email_service.send_email(
                to_email=recipient_email,
                subject=subject,
                content=content,
                is_html=True
            )

            if not success:
                logger.warning(f"邮件发送失败: {message}")
            else:
                logger.info(f"邮件发送成功至: {recipient_email}")

        except ImportError:
            logger.warning("邮件服务模块未找到，跳过邮件发送")
        except Exception as e:
            logger.error(f"邮件发送异常: {str(e)}", exc_info=True)

        return success_response(message='留言提交成功！我们会尽快与您联系。')
    except Exception as e:
        log_exception(logger, "提交联系表单失败")
        return server_error_response(f'提交失败：{str(e)}')


@home_bp.route('/api/messages', methods=['GET'])
def get_messages():
    """获取留言列表"""
    return success_response(data={'messages': []}, message='查询成功')
