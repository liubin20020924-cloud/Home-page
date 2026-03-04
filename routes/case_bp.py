"""
工单系统路由蓝图
"""
from flask import Blueprint, request, render_template, session, jsonify, redirect
from common.response import success_response, error_response, unauthorized_response, server_error_response
from common.unified_auth import get_current_user, authenticate_user
from common.validators import validate_email, validate_required, validate_phone
from common.logger import logger, log_request, log_exception
from common.database_context import db_connection
from datetime import datetime, timedelta
import pymysql

case_bp = Blueprint('case', __name__, url_prefix='/case')

# 用户状态缓存（减少数据库查询）
_user_status_cache = {}


def check_force_password_change():
    """检查是否需要强制修改密码"""
    if session.get('force_password_change', False):
        logger.warning("[工单系统] 用户需要强制修改密码，拒绝访问")
        return True
    return False


def generate_ticket_id():
    """生成唯一工单ID"""
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    import uuid
    random_str = str(uuid.uuid4())[:6].upper()
    return f"TK-{now}-{random_str}"


@case_bp.route('/')
def index():
    """首页"""
    return render_template('case/login.html')


@case_bp.route('/api/login', methods=['POST'])
def login():
    """工单系统登录
    
    用户登录工单系统
    ---
    tags:
      - 工单-认证
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: 用户名
            password:
              type: string
              description: 密码
    responses:
      200:
        description: 登录成功
        schema:
          $ref: '#/definitions/SuccessResponse'
      401:
        description: 登录失败
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    try:
        log_request(logger, request)
        # 支持两种提交方式：JSON 和 表单
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        # 简单验证用户名和密码
        if not username:
            return error_response(message='用户名不能为空')
        if not password:
            return error_response(message='密码不能为空')
        
        # 使用统一认证
        success, result = authenticate_user(username, password)

        if not success:
            return unauthorized_response(message='用户名或密码错误')

        user_info = result

        # 设置session数据
        session['user_id'] = user_info['id']
        session['username'] = user_info['username']
        session['role'] = user_info['role']
        session['display_name'] = user_info.get('display_name', '')
        session['login_time'] = datetime.now().isoformat()
        session['force_password_change'] = user_info.get('force_password_change', False)

        # 检查密码复杂度（不阻止登录，仅记录）
        from common.validators import check_password_strength
        is_strong, strength_msg = check_password_strength(password)
        session['password_strength_warning'] = None if is_strong else strength_msg
        if not is_strong:
            logger.info(f"用户 {username} 密码复杂度不足: {strength_msg}")

        # 处理"记住我"功能
        remember_me = data.get('remember', 'off') == 'on'
        if remember_me:
            session.permanent = True
            logger.info(f"用户 {username} 选择记住我，session有效期为7天")
        else:
            session.permanent = False
            logger.info(f"用户 {username} 未选择记住我，session有效期1小时")

        # 记录来源系统（用于修改密码后跳转回）
        session['redirect_after_password_change'] = '/case/my-tickets'

        return success_response(data={
            'user_id': user_info['id'],
            'username': user_info['username'],
            'display_name': user_info.get('display_name', ''),
            'role': user_info['role'],
            'force_password_change': user_info.get('force_password_change', False)
        }, message='登录成功')
    except Exception as e:
        log_exception(logger, "登录失败")
        return server_error_response(message=f'登录失败：{str(e)}')


@case_bp.route('/api/logout', methods=['POST'])
def logout():
    """登出"""
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"用户 {username} 退出登录")
    return redirect('/case/')


@case_bp.route('/auth/check-login')
def check_login():
    """检查登录状态

    用于前端AJAX检查用户是否登录
    ---
    tags:
      - 工单-认证
    responses:
      200:
        description: 登录状态检查结果
        schema:
          type: object
          properties:
            success:
              type: boolean
              description: 是否登录
            message:
              type: string
              description: 响应消息
            data:
              type: object
              properties:
                user:
                  type: object
                  description: 用户信息
    """
    user = get_current_user()

    # 只在未登录时记录日志，避免正常使用时产生大量日志
    if not user:
        logger.debug(f"[工单系统] 用户未登录")
        return unauthorized_response(message='未登录')

    # 验证session中的用户是否在数据库中仍然有效
    # 防止用户被锁定后，旧session仍然有效的问题
    user_id = session.get('user_id')
    if user_id:
        # 使用缓存减少数据库查询（5分钟缓存）
        cache_key = f'user_status_{user_id}'
        cache_time, cached_status = _user_status_cache.get(cache_key, (None, None))
        
        # 如果缓存未过期且状态有效，直接使用缓存
        if cache_time and (datetime.now() - cache_time) < timedelta(minutes=5):
            if cached_status not in ['active']:
                logger.warning(f"[工单系统] 用户状态缓存异常: {cached_status}, 清除session, user_id: {user_id}")
                session.clear()
                return unauthorized_response(message='账户已被禁用，请重新登录')
        else:
            # 缓存过期或不存在，查询数据库
            from common.unified_auth import get_connection
            conn = get_connection('kb')
            if conn:
                try:
                    with conn.cursor() as cursor:
                        # 检查用户状态
                        cursor.execute("SELECT status FROM `users` WHERE id = %s", (user_id,))
                        result = cursor.fetchone()
                        if result:
                            user_status = result[0] if isinstance(result, tuple) else result.get('status')
                            # 更新缓存
                            _user_status_cache[cache_key] = (datetime.now(), user_status)
                            
                            # 如果用户被锁定或删除，清除session
                            if user_status not in ['active']:
                                logger.warning(f"[工单系统] 用户session中的用户状态异常: {user_status}, 清除session, user_id: {user_id}")
                                session.clear()
                                return unauthorized_response(message='账户已被禁用，请重新登录')
                except Exception as e:
                    logger.error(f"验证用户状态失败: {str(e)}")
                finally:
                    conn.close()

    return success_response(data={'user': user}, message='已登录')


@case_bp.route('/api/user/info', methods=['GET'])
def get_user_info():
    """获取用户信息"""
    user_id = session.get('user_id')
    if not user_id:
        return unauthorized_response(message='未登录')

        return success_response(data={
            'user_id': session.get('user_id'),
            'username': session.get('username'),
            'display_name': session.get('display_name', ''),
            'role': session.get('role'),
            'email': session.get('email')
    })


@case_bp.route('/api/admins', methods=['GET'])
def get_admins():
    """获取管理员和普通用户列表（用于工单分配）"""
    try:
        log_request(logger, request)

        # 检查权限，只有 admin 和 user 角色可以查看
        user_role = session.get('role')
        if user_role not in ['admin', 'user']:
            return unauthorized_response(message='权限不足')

        with db_connection('kb') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 查询 admin 和 user 角色的活跃用户
            select_sql = """
                SELECT id, username, display_name, role, email
                FROM `users`
                WHERE role IN ('admin', 'user') AND status = 'active'
                ORDER BY role, username
            """
            cursor.execute(select_sql)
            users = cursor.fetchall()

        # 格式化用户数据，使用 display_name
        formatted_users = []
        for user in users:
            name = user.get('display_name') or user.get('username', '')
            formatted_users.append({
                'id': user['id'],
                'username': user['username'],
                'name': name,
                'role': user['role'],
                'email': user.get('email', '')
            })

        return success_response(data=formatted_users, message='查询成功')
    except Exception as e:
        log_exception(logger, "查询用户列表失败")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return server_error_response(message=f'查询失败：{str(e)}')


@case_bp.route('/api/customers/companies', methods=['GET'])
def get_customer_companies():
    """获取客户公司列表（用于创建工单时选择公司）"""
    try:
        log_request(logger, request)

        # 检查权限，只有 admin 和 user 角色可以查看
        user_role = session.get('role')
        if user_role not in ['admin', 'user']:
            return unauthorized_response(message='权限不足')

        with db_connection('kb') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 查询 customer 角色的活跃用户，按公司分组
            select_sql = """
                SELECT DISTINCT company_name
                FROM `users`
                WHERE role = 'customer' AND status = 'active'
                  AND company_name IS NOT NULL AND company_name != ''
                ORDER BY company_name
            """
            cursor.execute(select_sql)
            companies = cursor.fetchall()

        companies_list = [c['company_name'] for c in companies if c['company_name']]

        return success_response(data=companies_list, message='查询成功')
    except Exception as e:
        log_exception(logger, "查询客户公司列表失败")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return server_error_response(message=f'查询失败：{str(e)}')


@case_bp.route('/api/customers', methods=['GET'])
def get_customers():
    """获取客户联系人列表（可按公司筛选）"""
    try:
        log_request(logger, request)

        # 检查权限，只有 admin 和 user 角色可以查看
        user_role = session.get('role')
        if user_role not in ['admin', 'user']:
            return unauthorized_response(message='权限不足')

        # 获取公司名称参数
        company_name = request.args.get('company_name', '').strip()

        with db_connection('kb') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 查询 customer 角色的活跃用户
            if company_name:
                select_sql = """
                    SELECT id, username, display_name, email, phone, company_name
                    FROM `users`
                    WHERE role = 'customer' AND status = 'active'
                      AND company_name = %s
                    ORDER BY display_name, username
                """
                cursor.execute(select_sql, (company_name,))
            else:
                select_sql = """
                    SELECT id, username, display_name, email, phone, company_name
                    FROM `users`
                    WHERE role = 'customer' AND status = 'active'
                    ORDER BY company_name, display_name, username
                """
                cursor.execute(select_sql)

            customers = cursor.fetchall()

        # 格式化客户数据
        formatted_customers = []
        for customer in customers:
            name = customer.get('display_name') or customer.get('username', '')
            formatted_customers.append({
                'id': customer['id'],
                'username': customer['username'],
                'name': name,
                'email': customer.get('email', ''),
                'phone': customer.get('phone', ''),
                'company_name': customer.get('company_name', '')
            })

        return success_response(data=formatted_customers, message='查询成功')
    except Exception as e:
        log_exception(logger, "查询客户列表失败")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return server_error_response(message=f'查询失败：{str(e)}')


@case_bp.route('/api/ticket', methods=['POST'])
def create_ticket():
    """创建工单

    创建新的工单
    ---
    tags:
      - 工单-操作
    security:
      - CookieAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - customer_name
            - customer_contact_phone
            - customer_email
            - product
            - issue_type
            - priority
            - title
            - content
          properties:
            customer_name:
              type: string
              description: 客户公司名称
            customer_contact_name:
              type: string
              description: 客户联系人姓名
            customer_contact_phone:
              type: string
              description: 联系电话
            customer_email:
              type: string
              format: email
              description: 联系邮箱
            cc_emails:
              type: string
              description: 抄送邮箱(多个邮箱用逗号分隔)
            product:
              type: string
              description: 涉及产品
            issue_type:
              type: string
              enum: [technical, service, complaint, other]
              description: 问题类型
            priority:
              type: string
              enum: [low, medium, high, urgent]
              description: 优先级
            title:
              type: string
              description: 工单标题
            content:
              type: string
              description: 工单详情
    responses:
      200:
        description: 创建成功
        schema:
          $ref: '#/definitions/SuccessResponse'
      400:
        description: 参数错误
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    try:
        log_request(logger, request)
        # 支持两种提交方式：JSON 和 表单
        if request.is_json:
            data = request.get_json()
        else:
            # 获取表单数据
            data = request.form.to_dict()

        user_role = session.get('role')
        user_display_name = session.get('display_name', '')
        user_username = session.get('username', '')
        user_email = session.get('email', '')

        # 检查权限：admin、user 和 customer 角色都可以创建工单
        if user_role not in ['admin', 'user', 'customer']:
            return unauthorized_response(message='权限不足')

        required_fields = [
            'customer_name', 'customer_contact_phone', 'customer_email',
            'product', 'issue_type', 'priority', 'title', 'content'
        ]

        # 验证必填字段
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return error_response(message=f'缺少必填字段：{field}或字段值为空')

        customer_email = data['customer_email'].strip()
        is_valid, error_msg = validate_email(customer_email)
        if not is_valid:
            return error_response(message=error_msg)

        # 验证抄送邮箱（如果提供）
        cc_emails = data.get('cc_emails', '').strip()
        if cc_emails:
            # 分割多个邮箱
            cc_email_list = [e.strip() for e in cc_emails.split(',') if e.strip()]
            # 验证每个邮箱
            for cc_email in cc_email_list:
                is_valid, error_msg = validate_email(cc_email)
                if not is_valid:
                    return error_response(message=f'抄送邮箱格式错误：{cc_email}')

        valid_issue_types = ['technical', 'service', 'complaint', 'other']
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if data['issue_type'].strip() not in valid_issue_types:
            return error_response(message='问题类型值不合法')
        if data['priority'].strip() not in valid_priorities:
            return error_response(message='优先级值不合法')

        ticket_id = generate_ticket_id()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 检查是否有上传的文件
        uploaded_files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename:
                    import os
                    from werkzeug.utils import secure_filename

                    allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}

                    def allowed_file(filename):
                        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                        saved_filename = f"{ticket_id}_{timestamp}_{filename}"

                        upload_dir = os.path.join('static', 'uploads', 'case')
                        os.makedirs(upload_dir, exist_ok=True)

                        file_path = os.path.join(upload_dir, saved_filename)
                        file.save(file_path)
                        uploaded_files.append(saved_filename)

        with db_connection('case') as conn:
            cursor = conn.cursor()
            insert_sql = """
                INSERT INTO tickets (ticket_id, customer_name, customer_contact_name, customer_contact, customer_email,
                                    cc_emails, submit_user, product, issue_type, priority, title, content,
                                    status, create_time, update_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # 客户名称（公司名）：用户填写或选择的客户公司
            final_customer_name = data['customer_name'].strip()

            # 客户联系人姓名：用户选择的联系人姓名
            final_contact_name = data.get('customer_contact_name', user_display_name or user_username).strip()

            # 提交用户名：当前登录用户的用户名
            submit_user = user_username or 'unknown'

            logger.info(f"创建工单 - submit_user: {submit_user}, final_customer_name: {final_customer_name}, final_contact_name: {final_contact_name}")
            logger.info(f"创建工单参数 - ticket_id: {ticket_id}, customer_contact_phone: {data.get('customer_contact_phone')}, customer_email: {customer_email}, cc_emails: {cc_emails}")

            cursor.execute(insert_sql, (
                ticket_id, final_customer_name, final_contact_name,
                data['customer_contact_phone'].strip(), customer_email, cc_emails if cc_emails else None, submit_user,
                data['product'].strip(), data['issue_type'].strip(),
                data['priority'].strip(), data['title'].strip(), data['content'].strip(),
                'pending', now, now
            ))

            # 如果有附件，保存到数据库
            if uploaded_files:
                for filename in uploaded_files:
                    file_url = f'/static/uploads/case/{filename}'
                    insert_msg_sql = """
                        INSERT INTO messages (ticket_id, sender, sender_name, content, send_time)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_msg_sql, (
                        ticket_id, 'system', '系统',
                        f'附件上传: {filename}|url:{file_url}', now
                    ))

            conn.commit()

        logger.info(f"工单创建成功: {ticket_id}")

        # 发送邮件通知到企业微信邮箱
        try:
            from services.email_service import EmailService
            email_service = EmailService()

            # 准备附件信息
            attachments = None
            if uploaded_files:
                attachments = []
                for filename in uploaded_files:
                    file_path = os.path.join('static', 'uploads', 'case', filename)
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / 1024 / 1024:.1f} MB"
                        attachments.append({
                            'filename': filename,
                            'url': f'/static/uploads/case/{filename}',
                            'size': size_str
                        })

            success, message = email_service.send_ticket_created_notification(
                ticket_id=ticket_id,
                title=data['title'].strip(),
                customer_name=final_customer_name,
                contact_name=final_contact_name,
                priority=data['priority'].strip(),
                issue_type=data['issue_type'].strip(),
                content=data['content'].strip(),
                attachments=attachments
            )

            if not success:
                logger.warning(f"工单邮件发送失败: {message}")
                # 邮件发送失败不阻止工单创建，只记录警告

        except ImportError:
            logger.warning("邮件服务模块未找到，跳过邮件发送")
        except Exception as e:
            logger.error(f"工单邮件发送异常: {str(e)}")
            # 邮件发送异常不阻止工单创建

        return success_response(data={'ticket_id': ticket_id}, message='工单创建成功')
    except Exception as e:
        log_exception(logger, "工单创建失败")
        return server_error_response(message=f'工单创建失败：{str(e)}')


@case_bp.route('/api/tickets/debug', methods=['GET'])
def debug_tickets():
    """调试接口：检查工单数据"""
    try:
        user_role = session.get('role')
        user_username = session.get('username')

        with db_connection('case') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 查询所有工单
            cursor.execute("SELECT ticket_id, customer_name, customer_contact_name, customer_contact, customer_email, submit_user, status, create_time FROM tickets ORDER BY create_time DESC LIMIT 10")
            all_tickets = cursor.fetchall()

            # 查询当前用户相关的工单
            cursor.execute("SELECT COUNT(*) as cnt FROM tickets WHERE submit_user = %s", (user_username,))
            user_ticket_count = cursor.fetchone()

            # 检查 submit_user 字段是否存在
            cursor.execute("SELECT COUNT(*) as cnt FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='casedb' AND TABLE_NAME='tickets' AND COLUMN_NAME='submit_user'")
            submit_user_exists = cursor.fetchone()

            return success_response(data={
                'user_role': user_role,
                'user_username': user_username,
                'submit_user_exists': submit_user_exists,
                'user_ticket_count': user_ticket_count,
                'all_tickets': all_tickets
            }, message='调试信息')
    except Exception as e:
        log_exception(logger, "调试查询失败")
        import traceback
        return server_error_response(message=f'调试失败：{str(e)}\n{traceback.format_exc()}')


@case_bp.route('/api/tickets', methods=['GET'])
def get_tickets():
    """获取工单列表（支持分页）"""
    try:
        log_request(logger, request)
        user_role = session.get('role')
        user_username = session.get('username')
        user_id = session.get('user_id')

        # 添加调试日志
        logger.info(f"工单列表查询 - user_role: {user_role}, user_username: {user_username}, user_id: {user_id}")

        if not user_role:
            return unauthorized_response(message='未登录')

        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        status = request.args.get('status', '').strip()
        priority = request.args.get('priority', '').strip()
        search = request.args.get('search', '').strip()
        my_only = request.args.get('my_only', 'false').lower() == 'true'

        logger.info(f"查询参数 - page: {page}, page_size: {page_size}, status: {status}, priority: {priority}, search: {search}, my_only: {my_only}")

        with db_connection('case') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 构建基础 WHERE 条件
            where_conditions = []
            params = []

            # 根据角色添加基础条件
            if user_role == 'customer':
                # 客户：显示自己提交的所有工单
                where_conditions.append("submit_user = %s")
                params.append(user_username)
            elif user_role in ['admin', 'user']:
                # 管理员/普通用户：显示所有工单（无需添加过滤条件）
                pass
            else:
                return unauthorized_response(message='角色权限不足')

            # 添加状态过滤
            if status:
                where_conditions.append("status = %s")
                params.append(status)

            # 添加优先级过滤
            if priority:
                where_conditions.append("priority = %s")
                params.append(priority)

            # 添加搜索（支持工单编号和标题）
            if search:
                where_conditions.append("(ticket_id LIKE %s OR title LIKE %s)")
                params.extend([f"%{search}%", f"%{search}%"])

            # 构建 SQL
            base_sql = """
                SELECT ticket_id, customer_name, customer_contact_name, customer_contact, customer_email,
                       cc_emails, product, issue_type, priority, title, status, create_time
                FROM tickets
            """

            if where_conditions:
                base_sql += " WHERE " + " AND ".join(where_conditions)

            # 先查询总数
            count_sql = "SELECT COUNT(*) as total FROM tickets"
            if where_conditions:
                count_sql += " WHERE " + " AND ".join(where_conditions)

            cursor.execute(count_sql, tuple(params))
            total_result = cursor.fetchone()
            total = total_result['total'] if total_result else 0

            # 添加排序和分页
            base_sql += " ORDER BY create_time DESC"

            # 添加分页
            offset = (page - 1) * page_size
            base_sql += f" LIMIT {page_size} OFFSET {offset}"

            logger.info(f"SQL: {base_sql}, params: {params}")
            cursor.execute(base_sql, tuple(params))
            tickets = cursor.fetchall()

            logger.info(f"查询到工单数量: {len(tickets)}, 总数: {total}")

            # 格式化工单数据
            for ticket in tickets:
                ticket['created_at'] = ticket['create_time'].strftime('%Y-%m-%d %H:%M:%S')
                if ticket.get('update_time'):
                    ticket['updated_at'] = ticket['update_time'].strftime('%Y-%m-%d %H:%M:%S')

        return success_response(data={
            'tickets': tickets,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }, message='查询成功')
    except Exception as e:
        log_exception(logger, "查询工单列表失败")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return server_error_response(message=f'查询失败：{str(e)}')


@case_bp.route('/api/ticket/<ticket_id>', methods=['GET'])
def get_ticket_detail(ticket_id):
    """获取工单详情"""
    try:
        log_request(logger, request)
        user_role = session.get('role')
        user_username = session.get('username')

        if not user_role:
            return unauthorized_response(message='未登录')

        with db_connection('case') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            select_sql = "SELECT * FROM tickets WHERE ticket_id = %s"
            cursor.execute(select_sql, (ticket_id,))
            ticket = cursor.fetchone()

        if not ticket:
            from common.response import not_found_response
            return not_found_response(message='工单不存在')

        # customer 角色只能查看自己提交的工单
        if user_role == 'customer' and ticket.get('submit_user') != user_username:
            from common.response import forbidden_response
            return forbidden_response(message='无权访问此工单')

        ticket['create_time'] = ticket['create_time'].strftime('%Y-%m-%d %H:%M:%S')
        ticket['update_time'] = ticket['update_time'].strftime('%Y-%m-%d %H:%M:%S')
        ticket['current_user_role'] = user_role

        return success_response(data=ticket, message='查询成功')
    except Exception as e:
        log_exception(logger, "查询工单详情失败")
        return server_error_response(message=f'查询失败：{str(e)}')


@case_bp.route('/api/ticket/<ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id):
    """更新工单状态"""
    try:
        log_request(logger, request)
        user_role = session.get('role')
        # admin 和 user 都可以更新状态
        if not user_role or user_role not in ['admin', 'user']:
            from common.response import forbidden_response
            return forbidden_response(message='无权执行此操作')

        data = request.get_json()
        new_status = data.get('status', '').strip()

        valid_statuses = ['pending', 'processing', 'completed', 'closed']
        if new_status not in valid_statuses:
            return error_response(message='工单状态值不合法')

        with db_connection('case') as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM tickets WHERE ticket_id = %s", (ticket_id,))
            if not cursor.fetchone():
                from common.response import not_found_response
                return not_found_response(message='工单不存在')

            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_sql = "UPDATE tickets SET status = %s, update_time = %s WHERE ticket_id = %s"
            cursor.execute(update_sql, (new_status, now, ticket_id))
            conn.commit()

        # 发送 WebSocket 更新通知
        try:
            from services.socketio_service import emit_ticket_update
            emit_ticket_update(ticket_id)
        except ImportError:
            pass

        logger.info(f"工单状态更新: {ticket_id} -> {new_status} by {user_role}")
        return success_response(message='工单状态更新成功')
    except Exception as e:
        log_exception(logger, "更新工单状态失败")
        return server_error_response(message=f'更新失败：{str(e)}')


@case_bp.route('/api/ticket/<ticket_id>/messages', methods=['GET'])
def get_messages(ticket_id):
    """获取工单消息"""
    try:
        log_request(logger, request)

        with db_connection('case') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            select_sql = """
                SELECT id, ticket_id, sender, sender_name, content, send_time
                FROM messages WHERE ticket_id = %s ORDER BY send_time ASC
            """
            cursor.execute(select_sql, (ticket_id,))
            messages = cursor.fetchall()
        
        for msg in messages:
            msg['send_time'] = msg['send_time'].strftime('%Y-%m-%d %H:%M:%S')
        
        return success_response(data=messages, message='查询成功')
    except Exception as e:
        log_exception(logger, "查询工单消息失败")
        return server_error_response(message=f'查询失败：{str(e)}')


@case_bp.route('/submit', methods=['GET'])
def submit_ticket_page():
    """工单提交页面"""
    # 检查是否需要强制修改密码
    if check_force_password_change():
        return redirect('/kb/auth/change-password')

    user_id = session.get('user_id')
    logger.info(f"[工单系统] 访问提交页面, session keys: {list(session.keys())}, user_id: {user_id}")

    if not user_id:
        logger.warning(f"[工单系统] 用户未登录, session为空或缺少user_id")
        return redirect('/case/')

    # 获取完整用户信息
    with db_connection('kb') as conn:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT id, username, display_name, role, email, phone, company_name
            FROM `users`
            WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()

    if not user:
        return redirect('/case/')

    user_data = {
        'id': user['id'],
        'username': user['username'],
        'display_name': user.get('display_name', ''),
        'role': user['role'],
        'email': user.get('email', ''),
        'phone': user.get('phone', ''),
        'company_name': user.get('company_name', '')
    }

    # 管理员和普通用户需要获取公司和用户列表
    companies = []
    company_users = {}

    if user_data['role'] in ['admin', 'user']:
        with db_connection('kb') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 获取所有有公司名称的公司列表（去重）
            cursor.execute("""
                SELECT DISTINCT company_name
                FROM `users`
                WHERE company_name IS NOT NULL AND company_name != ''
                ORDER BY company_name
            """)
            companies = [row['company_name'] for row in cursor.fetchall()]

            # 为每个公司获取用户列表
            for company in companies:
                cursor.execute("""
                    SELECT id, display_name, email, phone
                    FROM `users`
                    WHERE company_name = %s
                    ORDER BY display_name
                """, (company,))
                company_users[company] = cursor.fetchall()

    return render_template('case/submit_ticket.html',
                         current_user=user_data,
                         companies=companies,
                         company_users=company_users)


@case_bp.route('/my-tickets', methods=['GET'])
def my_tickets_page():
    """我的工单列表页面"""
    # 检查是否需要强制修改密码
    if check_force_password_change():
        return redirect('/kb/auth/change-password')

    user_id = session.get('user_id')
    logger.info(f"[工单系统] 访问我的工单页面, session keys: {list(session.keys())}, user_id: {user_id}")

    if not user_id:
        logger.warning(f"[工单系统] 用户未登录, 重定向到登录页面")
        return redirect('/case/?next=' + request.url)

    return render_template('case/ticket_list.html')


@case_bp.route('/admin/tickets', methods=['GET'])
def admin_tickets_page():
    """管理员工单列表页面"""
    user_id = session.get('user_id')
    logger.info(f"[工单系统] 访问工单管理页面, session keys: {list(session.keys())}, user_id: {user_id}")

    if not user_id:
        logger.warning(f"[工单系统] 用户未登录, 重定向到登录页面")
        return redirect('/case/?next=' + request.url)

    return render_template('case/ticket_list.html')


@case_bp.route('/ticket/<ticket_id>', methods=['GET'])
def ticket_detail_page(ticket_id):
    """工单详情页面（论坛样式）"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/case/?next=' + request.url)

    return render_template('case/ticket_detail_forum.html', ticket_id=ticket_id)


@case_bp.route('/api/ticket/<ticket_id>/message', methods=['POST'])
def send_message(ticket_id):
    """发送消息"""
    try:
        log_request(logger, request)
        
        user_id = session.get('user_id')
        if not user_id:
            return unauthorized_response(message='未登录')
        
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return error_response(message='消息内容不能为空')
        
        sender = session.get('role')
        sender_name = session.get('display_name') or session.get('username', '匿名用户')
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with db_connection('case') as conn:
            cursor = conn.cursor()
            insert_sql = """
                INSERT INTO messages (ticket_id, sender, sender_name, content, send_time)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (ticket_id, sender, sender_name, content, now))
            conn.commit()
        
        logger.info(f"工单 {ticket_id} 新消息: {sender_name}")
        return success_response(message='消息发送成功')
    except Exception as e:
        log_exception(logger, "发送消息失败")
        return server_error_response(message=f'发送失败：{str(e)}')


@case_bp.route('/api/ticket/<ticket_id>/attachment', methods=['POST'])
def upload_attachment(ticket_id):
    """上传附件"""
    try:
        log_request(logger, request)

        user_id = session.get('user_id')
        if not user_id:
            return unauthorized_response(message='未登录')
        
        if 'file' not in request.files:
            return error_response(message='未选择文件')
        
        file = request.files['file']
        if file.filename == '':
            return error_response(message='未选择文件')
        
        import os
        from werkzeug.utils import secure_filename
        
        allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
        
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
        
        if not allowed_file(file.filename):
            return error_response(message='不支持的文件类型')
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        saved_filename = f"{timestamp}_{filename}"
        
        upload_dir = os.path.join('static', 'uploads', 'case')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, saved_filename)
        file.save(file_path)
        
        logger.info(f"工单 {ticket_id} 附件上传: {saved_filename}")
        return success_response(data={'filename': saved_filename}, message='附件上传成功')
    except Exception as e:
        log_exception(logger, "附件上传失败")
        return server_error_response(message=f'上传失败：{str(e)}')


@case_bp.route('/api/ticket/<ticket_id>/attachments', methods=['GET'])
def get_attachments(ticket_id):
    """获取附件列表"""
    try:
        import os
        
        upload_dir = os.path.join('static', 'uploads', 'case')
        
        if not os.path.exists(upload_dir):
            return success_response(data=[], message='查询成功')
        
        files = []
        for filename in os.listdir(upload_dir):
            if filename.startswith(f"{ticket_id}_"):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path):
                    files.append({
                        'filename': filename,
                        'url': f'/static/uploads/case/{filename}',
                        'size': os.path.getsize(file_path)
                    })
        
        return success_response(data=files, message='查询成功')
    except Exception as e:
        log_exception(logger, "获取附件列表失败")
        return server_error_response(message=f'查询失败：{str(e)}')


@case_bp.route('/api/ticket/<ticket_id>/assign', methods=['POST'])
def assign_ticket(ticket_id):
    """分配工单"""
    try:
        log_request(logger, request)
        
        user_role = session.get('role')
        if not user_role or user_role != 'admin':
            from common.response import forbidden_response
            return forbidden_response(message='无权执行此操作')
        
        data = request.get_json()
        assignee = data.get('assignee', '').strip()
        
        if not assignee:
            return error_response(message='请选择处理人')
        
        with db_connection('case') as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM tickets WHERE ticket_id = %s", (ticket_id,))
            if not cursor.fetchone():
                from common.response import not_found_response
                return not_found_response(message='工单不存在')
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_sql = "UPDATE tickets SET assignee = %s, update_time = %s WHERE ticket_id = %s"
            cursor.execute(update_sql, (assignee, now, ticket_id))
            conn.commit()

        # 发送 WebSocket 更新通知
        try:
            from services.socketio_service import emit_ticket_update
            emit_ticket_update(ticket_id)
        except ImportError:
            pass

        logger.info(f"工单分配: {ticket_id} -> {assignee}")
        return success_response(message='工单分配成功')
    except Exception as e:
        log_exception(logger, "分配工单失败")
        return server_error_response(message=f'分配失败：{str(e)}')


@case_bp.route('/api/ticket/<ticket_id>/close', methods=['POST'])
def close_ticket(ticket_id):
    """关闭工单"""
    try:
        log_request(logger, request)

        user_role = session.get('role')
        if not user_role or user_role not in ['admin', 'user']:
            from common.response import forbidden_response
            return forbidden_response(message='无权执行此操作')

        with db_connection('case') as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM tickets WHERE ticket_id = %s", (ticket_id,))
            if not cursor.fetchone():
                from common.response import not_found_response
                return not_found_response(message='工单不存在')

            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_sql = "UPDATE tickets SET status = 'closed', update_time = %s WHERE ticket_id = %s"
            cursor.execute(update_sql, (now, ticket_id))
            conn.commit()

        logger.info(f"工单关闭: {ticket_id} by {user_role}")
        return success_response(message='工单关闭成功')
    except Exception as e:
        log_exception(logger, "关闭工单失败")
        return server_error_response(message=f'关闭失败：{str(e)}')


@case_bp.route('/api/ticket/<ticket_id>/satisfaction', methods=['POST'])
def submit_satisfaction(ticket_id):
    """提交满意度评价"""
    try:
        log_request(logger, request)

        user_id = session.get('user_id')
        if not user_id:
            return unauthorized_response(message='未登录')

        user_role = session.get('role')
        if user_role != 'customer':
            return forbidden_response(message='只有客户可以进行评价')

        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment', '').strip()

        if not rating or not (1 <= rating <= 5):
            return error_response(message='评分必须在1-5之间')

        with db_connection('case') as conn:
            cursor = conn.cursor()

            # 检查工单是否存在
            cursor.execute("SELECT id, submit_user FROM tickets WHERE ticket_id = %s", (ticket_id,))
            ticket = cursor.fetchone()

            if not ticket:
                from common.response import not_found_response
                return not_found_response(message='工单不存在')

            # 检查是否已经评价过
            cursor.execute("SELECT id FROM satisfaction WHERE ticket_id = %s", (ticket_id,))
            if cursor.fetchone():
                return error_response(message='该工单已经评价过，无法重复评价')

            # 插入评价记录
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insert_sql = """
                INSERT INTO satisfaction (ticket_id, rating, comment, create_time)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (ticket_id, rating, comment, now))
            conn.commit()

        logger.info(f"工单评价提交: {ticket_id}, 评分: {rating} by user {user_id}")
        return success_response(message='评价提交成功')
    except Exception as e:
        log_exception(logger, "提交满意度评价失败")
        return server_error_response(message=f'提交失败：{str(e)}')


@case_bp.route('/api/ticket/<ticket_id>/satisfaction', methods=['GET'])
def get_satisfaction(ticket_id):
    """获取工单满意度评价"""
    try:
        log_request(logger, request)

        user_id = session.get('user_id')
        if not user_id:
            return unauthorized_response(message='未登录')

        with db_connection('case') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            select_sql = """
                SELECT ticket_id, rating, comment, create_time
                FROM satisfaction
                WHERE ticket_id = %s
            """
            cursor.execute(select_sql, (ticket_id,))
            satisfaction = cursor.fetchone()

        if not satisfaction:
            return success_response(data=None, message='该工单暂无评价')

        satisfaction['create_time'] = satisfaction['create_time'].strftime('%Y-%m-%d %H:%M:%S')

        return success_response(data=satisfaction, message='查询成功')
    except Exception as e:
        log_exception(logger, "查询满意度评价失败")
        return server_error_response(message=f'查询失败：{str(e)}')


@case_bp.route('/api/admin/reports', methods=['GET'])
def get_reports():
    """获取工单统计数据（管理员）"""
    try:
        log_request(logger, request)

        user_role = session.get('role')
        if not user_role or user_role not in ['admin', 'user']:
            return forbidden_response(message='无权访问此功能')

        # 获取时间范围参数
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')

        with db_connection('case') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 构建时间过滤条件
            time_filter = ""
            params = []
            if start_date:
                time_filter += " AND create_time >= %s"
                params.append(start_date)
            if end_date:
                time_filter += " AND create_time <= %s"
                params.append(end_date + " 23:59:59")

            # 1. 工单总量统计
            cursor.execute(f"""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed
                FROM tickets
                WHERE 1=1 {time_filter}
            """, tuple(params))
            status_stats = cursor.fetchone()

            # 2. 按优先级统计
            cursor.execute(f"""
                SELECT
                    priority,
                    COUNT(*) as count
                FROM tickets
                WHERE 1=1 {time_filter}
                GROUP BY priority
                ORDER BY
                    CASE priority
                        WHEN 'urgent' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                    END
            """, tuple(params))
            priority_stats = cursor.fetchall()

            # 3. 按问题类型统计
            cursor.execute(f"""
                SELECT
                    issue_type,
                    COUNT(*) as count
                FROM tickets
                WHERE 1=1 {time_filter}
                GROUP BY issue_type
                ORDER BY count DESC
            """, tuple(params))
            type_stats = cursor.fetchall()

            # 4. 按产品统计
            cursor.execute(f"""
                SELECT
                    product,
                    COUNT(*) as count
                FROM tickets
                WHERE 1=1 {time_filter}
                GROUP BY product
                ORDER BY count DESC
                LIMIT 10
            """, tuple(params))
            product_stats = cursor.fetchall()

            # 5. 满意度统计
            cursor.execute(f"""
                SELECT
                    AVG(rating) as avg_rating,
                    COUNT(*) as total_ratings,
                    SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) as satisfied,
                    SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as neutral,
                    SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) as unsatisfied
                FROM satisfaction s
                INNER JOIN tickets t ON s.ticket_id = t.ticket_id
                WHERE 1=1 {time_filter}
            """, tuple(params))
            satisfaction_stats = cursor.fetchone()

            # 6. 最近7天趋势
            cursor.execute("""
                SELECT
                    DATE(create_time) as date,
                    COUNT(*) as count
                FROM tickets
                WHERE create_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY DATE(create_time)
                ORDER BY date
            """)
            trend_stats = cursor.fetchall()

        return success_response(data={
            'status_distribution': status_stats,
            'priority_distribution': priority_stats,
            'type_distribution': type_stats,
            'product_distribution': product_stats,
            'satisfaction': satisfaction_stats,
            'daily_trend': trend_stats
        }, message='查询成功')
    except Exception as e:
        log_exception(logger, "查询统计数据失败")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return server_error_response(message=f'查询失败：{str(e)}')


@case_bp.route('/admin/reports', methods=['GET'])
def admin_reports_page():
    """管理员报表页面"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/case/?next=' + request.url)

    return render_template('case/admin_reports.html')




# 限流豁免配置 - 必须在所有路由定义后执行
# 使用延迟导入避免循环依赖
try:
    from app import limiter as app_limiter
    if app_limiter:
        # 豁免频繁调用的check-login端点
        app_limiter.exempt(check_login)
        print("[工单系统] check-login端点已豁免限流")
except ImportError:
    print("[工单系统] 无法导入limiter,跳过豁免配置")
except Exception as e:
    print(f"[工单系统] 豁免限流配置失败: {str(e)}")
