"""
统一管理后台路由

功能：
1. 统一登录入口
2. 统一导航布局
3. 整合用户管理
4. 整合留言管理
5. 整合监控管理
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from datetime import datetime
from functools import wraps
from common.unified_auth import get_current_user, authenticate_user
from common.database_context import db_connection
from common.response import success_response, error_response, validation_error_response, server_error_response
from common.validators import validate_user_data
from common.logger import logger, log_exception

# 创建统一管理蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# 登录验证装饰器
def admin_login_required(f):
    """管理员登录验证"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查登录状态
        user = get_current_user()
        if not user:
            # 未登录，跳转到登录页面
            if request.is_json:
                return error_response('未登录，请先登录', 401)
            return redirect(url_for('admin.login'))

        # 检查是否是管理员
        if user.get('role') != 'admin':
            if request.is_json:
                return error_response('权限不足', 403)
            flash('权限不足，只有管理员才能访问此页面', 'error')
            return redirect(url_for('admin.login'))

        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_login_required
def dashboard():
    """管理后台首页 - 仪表板"""
    # 获取统计数据
    stats = {
        'user_count': 0,
        'pending_messages': 0,
        'ticket_count': 0,
        'recent_messages': []
    }

    try:
        # 获取用户总数（从 kb 数据库）
        with db_connection('kb') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM `users`")
            result = cursor.fetchone()
            if result:
                stats['user_count'] = result.get('count', 0)
            cursor.close()

        # 获取待处理留言数（从 home 数据库）
        with db_connection('home') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM messages WHERE status = 'pending'")
            result = cursor.fetchone()
            if result:
                stats['pending_messages'] = result.get('count', 0)

            # 获取最近5条留言
            cursor.execute("""
                SELECT id, name, email, message, created_at, status
                FROM messages
                ORDER BY created_at DESC
                LIMIT 5
            """)
            messages = cursor.fetchall()
            stats['recent_messages'] = [
                {
                    'id': msg['id'],
                    'name': msg['name'],
                    'email': msg['email'],
                    'message': msg['message'][:50] + '...' if len(msg['message']) > 50 else msg['message'],
                    'created_at': msg['created_at'].strftime('%Y-%m-%d %H:%M') if msg['created_at'] else '',
                    'status': msg['status']
                }
                for msg in messages
            ]
            cursor.close()

        # 获取工单总数（从 case 数据库）
        with db_connection('case') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM tickets")
            result = cursor.fetchone()
            if result:
                stats['ticket_count'] = result.get('count', 0)
            cursor.close()

    except Exception as e:
        logger.error(f"获取仪表盘统计数据失败: {str(e)}", exc_info=True)

    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """统一登录页面"""
    # 如果已登录且是管理员，直接跳转到仪表板
    user = get_current_user()
    if user and user.get('role') == 'admin':
        logger.info("管理员已登录，重定向到仪表板")
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('用户名或密码不能为空', 'error')
            return render_template('admin/login.html', username=username)

        # 认证用户
        success, result = authenticate_user(username, password)

        if success:
            user_info = result

            # 检查是否是管理员
            if user_info.get('role') != 'admin':
                flash('权限不足，只有管理员才能访问此页面', 'error')
                logger.warning(f"非管理员用户 {username} 尝试访问管理后台")
                return render_template('admin/login.html', username=username)

            # 检查账户状态
            if user_info.get('status') == 'inactive':
                flash('账户未激活，请联系管理员', 'error')
                return render_template('admin/login.html', username=username)

            if user_info.get('status') == 'locked':
                flash('账户已锁定，请联系管理员', 'error')
                return render_template('admin/login.html', username=username)

            # 设置 session
            session['user_id'] = user_info['id']
            session['username'] = user_info['username']
            session['display_name'] = user_info.get('display_name', '')
            session['role'] = user_info['role']
            session['login_time'] = datetime.now().isoformat()

            # session 有效期设置为 3 小时
            session.permanent = False
            logger.info(f"管理员 {username} 成功登录管理后台")

            # 记录登录日志
            try:
                with db_connection('kb') as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO mgmt_login_logs
                        (user_id, username, ip_address, status, login_time)
                        VALUES (%s, %s, %s, 'success', NOW())
                    """, (user_info['id'], user_info['username'], request.remote_addr))
                    conn.commit()
                    cursor.close()
            except Exception as e:
                logger.error(f"记录登录日志失败: {str(e)}")

            return redirect(url_for('admin.dashboard'))
        else:
            flash(f'登录失败: {result}', 'error')
            logger.warning(f"用户 {username} 登录失败: {result}")
            return render_template('admin/login.html', username=username)

    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    """登出"""
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"用户 {username} 退出管理后台")
    flash('您已成功退出登录', 'info')
    return redirect(url_for('admin.login'))


# ==================== 用户管理 ====================

@admin_bp.route('/users')
@admin_login_required
def users():
    """用户管理页面"""
    return render_template('admin/users.html')


@admin_bp.route('/users/api/list')
@admin_login_required
def users_api_list():
    """用户列表 API"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        search_type = request.args.get('search_type', '')
        search_keyword = request.args.get('search', '')

        import pymysql
        with db_connection('kb') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 构建查询条件
            where_clause = []
            params = []

            if search_type and search_keyword:
                if search_type == 'username':
                    where_clause.append("username LIKE %s")
                    params.append(f"%{search_keyword}%")
                elif search_type == 'email':
                    where_clause.append("email LIKE %s")
                    params.append(f"%{search_keyword}%")
                elif search_type == 'role':
                    where_clause.append("role = %s")
                    params.append(search_keyword)
                elif search_type == 'status':
                    where_clause.append("status = %s")
                    params.append(search_keyword)
                elif search_type == 'company':
                    where_clause.append("company_name LIKE %s")
                    params.append(f"%{search_keyword}%")
                elif search_type == 'display_name':
                    where_clause.append("display_name LIKE %s")
                    params.append(f"%{search_keyword}%")

            # 构建 WHERE 子句
            where_sql = ""
            if where_clause:
                where_sql = "WHERE " + " AND ".join(where_clause)

            # 获取总数
            count_sql = f"SELECT COUNT(*) as total FROM users {where_sql}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()['total']

            # 获取分页数据
            offset = (page - 1) * page_size
            list_sql = f"""
                SELECT id, username, display_name, email, phone, company_name,
                       role, status, last_login, created_at, updated_at, created_by
                FROM users {where_sql}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(list_sql, params + [page_size, offset])
            users = cursor.fetchall()

            cursor.close()

            return success_response(data={
                'users': users,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            })

    except Exception as e:
        log_exception(logger, "获取用户列表失败")
        return server_error_response(f'获取用户列表失败：{str(e)}')


@admin_bp.route('/users/api/create', methods=['POST'])
@admin_login_required
def users_api_create():
    """创建用户 API"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)

        # 验证必填字段
        if not data.get('username') or not data.get('password'):
            return error_response('用户名和密码不能为空', 400)

        if not data.get('company_name'):
            return error_response('公司名称不能为空', 400)

        # 验证输入
        is_valid, errors = validate_user_data(data)
        if not is_valid:
            return validation_error_response(errors)

        # 使用统一用户创建接口
        from common.unified_auth import create_user
        success, message = create_user(
            username=data['username'],
            password=data['password'],
            display_name=data.get('display_name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            company_name=data.get('company_name', ''),
            role=data.get('role', 'user'),
            created_by=session.get('username', 'admin')
        )

        if success:
            logger.info(f"管理员 {session.get('username')} 创建用户 {data['username']} 成功")
            return success_response(message=message)
        else:
            return error_response(message, 400)

    except Exception as e:
        log_exception(logger, "创建用户失败")
        return server_error_response(f'创建用户失败：{str(e)}')


@admin_bp.route('/users/api/update', methods=['POST'])
@admin_login_required
def users_api_update():
    """更新用户 API"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)

        user_id = data.get('id')
        if not user_id:
            return error_response('用户ID不能为空', 400)

        # 输入验证
        is_valid, errors = validate_user_data(data, skip_username_validation=True)
        if not is_valid:
            return validation_error_response(errors)

        import pymysql
        with db_connection('kb') as conn:
            cursor = conn.cursor()

            # 检查用户是否存在
            cursor.execute("SELECT id, username FROM `users` WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            if not user:
                return error_response('用户不存在', 404)

            # 构建更新 SQL
            update_fields = []
            update_values = []

            if 'display_name' in data:
                update_fields.append("display_name = %s")
                update_values.append(data['display_name'])

            if 'email' in data:
                update_fields.append("email = %s")
                update_values.append(data['email'])

            if 'phone' in data:
                update_fields.append("phone = %s")
                update_values.append(data['phone'])

            if 'role' in data:
                update_fields.append("role = %s")
                update_values.append(data['role'])

            if 'status' in data:
                update_fields.append("status = %s")
                update_values.append(data['status'])

            if 'company_name' in data:
                update_fields.append("company_name = %s")
                update_values.append(data['company_name'])

            if 'password' in data and data['password']:
                from werkzeug.security import generate_password_hash
                update_fields.append("password_hash = %s")
                update_values.append(generate_password_hash(data['password']))
                update_fields.append("password_type = %s")
                update_values.append('werkzeug')

            if update_fields:
                update_values.append(user_id)
                sql = f"UPDATE `users` SET {', '.join(update_fields)}, updated_at = NOW() WHERE id = %s"
                cursor.execute(sql, update_values)
                conn.commit()

            cursor.close()

        logger.info(f"管理员 {session.get('username')} 更新用户 {user_id} 成功")
        return success_response(message='用户更新成功')

    except Exception as e:
        log_exception(logger, "更新用户失败")
        return server_error_response(f'更新用户失败：{str(e)}')


@admin_bp.route('/users/api/delete', methods=['POST'])
@admin_login_required
def users_api_delete():
    """删除用户 API"""
    try:
        data = request.get_json()
        user_id = data.get('id')

        if not user_id:
            return error_response('用户ID不能为空', 400)

        # 检查是否是当前登录用户
        if user_id == session.get('user_id'):
            return error_response('不能删除当前登录用户')

        # 检查是否是 admin 用户（ID 为 1）
        if user_id == 1:
            return error_response('不能删除 admin 用户')

        import pymysql
        with db_connection('kb') as conn:
            cursor = conn.cursor()

            # 检查用户是否存在
            cursor.execute("SELECT id, username, status FROM `users` WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            if not user:
                return error_response('用户不存在', 404)

            # 获取用户名用于日志
            if isinstance(user, dict):
                username = user.get('username', f"user_{user_id}")
            else:
                username = user[1] if len(user) > 1 else f"user_{user_id}"

            # 删除用户记录
            cursor.execute("DELETE FROM `users` WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()

        logger.info(f"管理员 {session.get('username')} 删除用户 {user_id} ({username}) 成功")
        return success_response(message='用户已删除')

    except Exception as e:
        log_exception(logger, "删除用户失败")
        return server_error_response(f'删除用户失败：{str(e)}')


@admin_bp.route('/users/api/login-logs', methods=['GET'])
@admin_login_required
def users_api_login_logs():
    """获取登录记录 API"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))

        import pymysql
        with db_connection('kb') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 获取总数
            cursor.execute("SELECT COUNT(*) as total FROM mgmt_login_logs")
            total = cursor.fetchone()['total']

            # 获取分页数据
            offset = (page - 1) * page_size
            list_sql = """
                SELECT id, username, display_name, ip_address,
                       login_time, status, failure_reason
                FROM mgmt_login_logs
                ORDER BY login_time DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(list_sql, [page_size, offset])
            logs = cursor.fetchall()

            # 将 datetime 对象转换为字符串
            for log in logs:
                if log.get('login_time'):
                    log['login_time'] = log['login_time'].strftime('%Y-%m-%d %H:%M:%S')

            cursor.close()

            return success_response(data={
                'logs': logs,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            })

    except Exception as e:
        log_exception(logger, "获取登录记录失败")
        return server_error_response(f'获取登录记录失败：{str(e)}')


# ==================== 留言管理 ====================

@admin_bp.route('/messages')
@admin_login_required
def messages():
    """留言管理页面"""
    return render_template('admin/messages.html')


@admin_bp.route('/messages/api/list')
@admin_login_required
def messages_api_list():
    """留言列表 API"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        status = request.args.get('status', '')  # 1/2/3/pending/processed
        search = request.args.get('search', '')

        import pymysql
        with db_connection('home') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 构建查询条件
            where_clause = []
            params = []

            if status:
                where_clause.append("status = %s")
                params.append(status)

            if search:
                where_clause.append("(name LIKE %s OR phone LIKE %s OR message LIKE %s)")
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern])

            # 构建 WHERE 子句
            where_sql = ""
            if where_clause:
                where_sql = "WHERE " + " AND ".join(where_clause)

            # 获取总数
            count_sql = f"SELECT COUNT(*) as total FROM messages {where_sql}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()['total']

            # 获取分页数据
            offset = (page - 1) * page_size
            list_sql = f"""
                SELECT id, name, email, phone, message, created_at, status
                FROM messages {where_sql}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(list_sql, params + [page_size, offset])
            messages = cursor.fetchall()

            cursor.close()

            return success_response(data={
                'messages': messages,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            })

    except Exception as e:
        log_exception(logger, "获取留言列表失败")
        return server_error_response(f'获取留言列表失败：{str(e)}')


@admin_bp.route('/messages/api/update', methods=['POST'])
@admin_login_required
def messages_api_update():
    """更新留言状态 API"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)

        message_id = data.get('id')
        status = data.get('status')

        if not message_id:
            return error_response('留言ID不能为空', 400)

        # 支持 1/2/3 和 pending/processed 两种格式
        valid_statuses = ['1', '2', '3', 'pending', 'processed']
        if status not in valid_statuses:
            return error_response('状态值无效', 400)
            return error_response('状态值无效', 400)

        import pymysql
        with db_connection('home') as conn:
            cursor = conn.cursor()

            # 检查留言是否存在
            cursor.execute("SELECT id FROM `messages` WHERE id = %s", (message_id,))
            message = cursor.fetchone()

            if not message:
                return error_response('留言不存在', 404)

            # 更新状态
            cursor.execute(
                "UPDATE `messages` SET status = %s WHERE id = %s",
                (status, message_id)
            )
            conn.commit()
            cursor.close()

        logger.info(f"管理员 {session.get('username')} 更新留言 {message_id} 状态为 {status}")
        return success_response(message='留言状态更新成功')

    except Exception as e:
        log_exception(logger, "更新留言状态失败")
        return server_error_response(f'更新留言状态失败：{str(e)}')


@admin_bp.route('/messages/api/delete', methods=['POST'])
@admin_login_required
def messages_api_delete():
    """删除留言 API"""
    try:
        data = request.get_json()
        message_id = data.get('id')

        if not message_id:
            return error_response('留言ID不能为空', 400)

        import pymysql
        with db_connection('home') as conn:
            cursor = conn.cursor()

            # 检查留言是否存在
            cursor.execute("SELECT id FROM `messages` WHERE id = %s", (message_id,))
            message = cursor.fetchone()

            if not message:
                return error_response('留言不存在', 404)

            # 删除留言
            cursor.execute("DELETE FROM `messages` WHERE id = %s", (message_id,))
            conn.commit()
            cursor.close()

        logger.info(f"管理员 {session.get('username')} 删除留言 {message_id} 成功")
        return success_response(message='留言删除成功')

    except Exception as e:
        log_exception(logger, "删除留言失败")
        return server_error_response(f'删除留言失败：{str(e)}')


# ==================== 监控管理 ====================

@admin_bp.route('/monitoring')
@admin_login_required
def monitoring():
    """监控管理页面"""
    from services.monitoring_service import get_monitoring_service
    monitoring_service = get_monitoring_service()
    
    current_metrics = monitoring_service.get_current_metrics()
    active_alerts = monitoring_service.get_active_alerts()
    
    return render_template('admin/monitoring.html',
                        metrics=current_metrics,
                        active_alerts=active_alerts)


@admin_bp.route('/monitoring/api/metrics')
@admin_login_required
def monitoring_api_metrics():
    """监控指标 API"""
    from services.monitoring_service import get_monitoring_service
    monitoring_service = get_monitoring_service()
    
    return jsonify({
        'success': True,
        'data': monitoring_service.get_current_metrics(),
        'timestamp': datetime.now().isoformat()
    })


@admin_bp.route('/monitoring/api/alerts')
@admin_login_required
def monitoring_api_alerts():
    """告警列表 API"""
    from services.monitoring_service import get_monitoring_service
    monitoring_service = get_monitoring_service()
    
    return jsonify({
        'success': True,
        'data': [alert.__dict__ for alert in monitoring_service.get_active_alerts()]
    })
