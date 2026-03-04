"""
统一认证工具函数
统一使用 werkzeug 密码加密（更安全）
整合知识库和工单系统的用户认证
"""
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session, request
from common.db_manager import get_connection


def authenticate_user(username, password):
    """
    统一用户认证
    统一使用 werkzeug 密码加密（更安全）
    """
    conn = get_connection('kb')
    if conn is None:
        return False, "数据库连接失败"

    try:
        with conn.cursor() as cursor:
            # 查询用户信息 - 支持用户名或邮箱登录
            sql = """
            SELECT id, username, password_hash, display_name, role, status, login_attempts, last_login, force_password_change
            FROM `users`
            WHERE (username = %s OR email = %s) AND status = 'active'
            """
            cursor.execute(sql, (username, username))
            user = cursor.fetchone()

            if not user:
                return False, "用户名或密码错误"

            # 统一使用 werkzeug 密码验证
            password_valid = False

            # 检查返回数据类型（dict或tuple）
            if isinstance(user, dict):
                # 字典类型（DictCursor）
                password_hash = user.get('password_hash')
                if password_hash:
                    password_valid = check_password_hash(password_hash, password)
                user_id = user.get('id')
                display_name_val = user.get('display_name')
                role_val = user.get('role')
                login_attempts = user.get('login_attempts', 0)
                last_login_val = user.get('last_login')
                force_password_change_val = user.get('force_password_change', 0)
            else:
                # 元组类型（普通cursor）
                # 字段索引: 0=id, 1=username, 2=password_hash, 3=display_name, 4=role, 5=status, 6=login_attempts, 7=last_login, 8=force_password_change
                user_id, user_name, pwd_hash, disp_name, user_role, user_status, attempts, last_login_val, force_password_change_val = user

                if pwd_hash:
                    password_valid = check_password_hash(pwd_hash, password)

                display_name_val = disp_name
                role_val = user_role
                login_attempts = attempts

            if password_valid:
                # 获取用户ID（兼容dict和tuple）
                if isinstance(user, dict):
                    user_id = user.get('id')
                    display_name_val = user.get('display_name')
                    role_val = user.get('role')
                    login_attempts = user.get('login_attempts', 0)
                else:
                    user_id = user[0]
                    display_name_val = user[4]
                    role_val = user[5]
                    login_attempts = user[7]

                # 登录成功，更新登录信息
                update_sql = """
                UPDATE `users`
                SET last_login = NOW(), login_attempts = 0
                WHERE id = %s
                """
                cursor.execute(update_sql, (user_id,))

                # 记录登录日志
                log_sql = """
                INSERT INTO `mgmt_login_logs` (user_id, username, ip_address, user_agent, status)
                VALUES (%s, %s, %s, %s, 'success')
                """
                cursor.execute(log_sql, (
                    user_id,
                    username,
                    request.remote_addr,
                    request.headers.get('User-Agent')
                ))

                conn.commit()

                # 返回用户信息
                display_name = display_name_val or username
                user_info = {
                    'id': user_id,
                    'username': username,
                    'display_name': display_name,
                    'role': role_val,
                    'force_password_change': force_password_change_val == 1
                }
                return True, user_info
            else:
                # 获取用户ID和登录尝试次数（兼容dict和tuple）
                if isinstance(user, dict):
                    user_id = user.get('id')
                    login_attempts = user.get('login_attempts', 0)
                else:
                    user_id = user[0]
                    login_attempts = user[7]

                # 登录失败，增加尝试次数
                update_sql = """
                UPDATE `users`
                SET login_attempts = login_attempts + 1
                WHERE id = %s
                """
                cursor.execute(update_sql, (user_id,))

                # 记录失败日志
                if login_attempts >= 5:
                    # 锁定账户
                    lock_sql = "UPDATE `users` SET status = 'locked' WHERE id = %s"
                    cursor.execute(lock_sql, (user_id,))

                log_sql = """
                INSERT INTO `mgmt_login_logs` (user_id, username, ip_address, user_agent, status, failure_reason)
                VALUES (%s, %s, %s, %s, 'failed', '密码错误')
                """
                cursor.execute(log_sql, (
                    user_id,
                    username,
                    request.remote_addr,
                    request.headers.get('User-Agent')
                ))

                conn.commit()
                return False, "用户名或密码错误"

    except Exception as e:
        print(f"用户验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False, f"系统错误: {str(e)}"
    finally:
        if conn:
            conn.close()


def get_current_user():
    """获取当前登录用户信息"""
    if 'user_id' in session and 'username' in session:
        return {
            'id': session['user_id'],
            'username': session['username'],
            'display_name': session.get('display_name'),
            'role': session.get('role')
        }
    return None


def login_required(roles=None):
    """登录验证装饰器"""
    def decorator(f):
        from functools import wraps

        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                from flask import redirect, url_for
                return redirect(url_for('kb.login', next=request.url))

            if roles and user.get('role') not in roles:
                from flask import render_template
                return render_template('error.html',
                                     error_message="权限不足，无法访问此页面",
                                     error_code=403), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def create_user(username, password, display_name=None, email=None, phone=None, company_name=None, role='user', created_by='admin', force_password_change=False):
    """
    创建新用户（统一接口）
    统一使用 werkzeug 密码加密
    
    参数:
        force_password_change: 是否强制修改密码，默认为False
    """
    conn = get_connection('kb')
    if conn is None:
        return False, "数据库连接失败"

    try:
        with conn.cursor() as cursor:
            # 检查用户名是否已存在
            cursor.execute("SELECT id FROM `users` WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "用户名已存在"

            # 统一使用 werkzeug 生成密码哈希
            password_hash = generate_password_hash(password)

            # 插入用户
            insert_sql = """
            INSERT INTO `users` (username, password_hash, password_type, display_name, email, phone, role, status, system, created_by, company_name, force_password_change)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                username,
                password_hash,
                'werkzeug',
                display_name,
                email,
                phone,
                role,
                'active',
                'unified',
                created_by,
                company_name,
                1 if force_password_change else 0
            ))
            conn.commit()

            return True, "用户创建成功"
    except Exception as e:
        conn.rollback()
        return False, f"创建用户失败：{str(e)}"
    finally:
        if conn:
            conn.close()


def update_user_password(user_id, new_password):
    """
    更新用户密码
    统一使用 werkzeug 加密
    """
    conn = get_connection('kb')
    if conn is None:
        return False, "数据库连接失败"

    try:
        with conn.cursor() as cursor:
            # 统一使用 werkzeug 生成密码哈希
            password_hash = generate_password_hash(new_password)

            update_sql = """
            UPDATE `users`
            SET password_hash = %s, password_type = 'werkzeug', updated_at = NOW()
            WHERE id = %s
            """
            cursor.execute(update_sql, (password_hash, user_id))
            conn.commit()

            return True, "密码更新成功"
    except Exception as e:
        conn.rollback()
        return False, f"更新密码失败：{str(e)}"
    finally:
        if conn:
            conn.close()
