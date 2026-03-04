"""
统一用户管理路由蓝图 - 独立管理页面
"""
from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from common.unified_auth import get_current_user, authenticate_user
from common.database_context import db_connection
from common.logger import logger
from datetime import datetime

user_management_bp = Blueprint('user_management', __name__, url_prefix='/user-mgmt')


@user_management_bp.route('/login', methods=['GET', 'POST'])
def login():
    """统一用户管理登录页面
    
    仅允许管理员登录
    """
    # 如果已登录且是管理员,直接跳转到管理页面
    user = get_current_user()
    if user and user.get('role') == 'admin':
        logger.info("管理员已登录,重定向到用户管理页面")
        return redirect(url_for('user_management.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember', 'off') == 'on'

        if not username or not password:
            flash('用户名或密码错误', 'error')
            return render_template('user_management/login.html', username=username)

        # 认证用户
        success, result = authenticate_user(username, password)

        if success:
            user_info = result

            # 检查是否是管理员
            if user_info.get('role') != 'admin':
                flash('访问拒绝: 只有管理员才能访问此页面', 'error')
                logger.warning(f"非管理员用户 {username} 尝试访问用户管理页面")
                return render_template('user_management/login.html', username=username)

            # 设置session
            session['user_id'] = user_info['id']
            session['username'] = user_info['username']
            session['display_name'] = user_info.get('display_name', '')
            session['role'] = user_info['role']
            session['login_time'] = datetime.now().isoformat()

            # 检查密码复杂度（不阻止登录，仅记录）
            from common.validators import check_password_strength
            is_strong, strength_msg = check_password_strength(password)
            session['password_strength_warning'] = None if is_strong else strength_msg
            if not is_strong:
                logger.info(f"用户 {username} 密码复杂度不足: {strength_msg}")

            # 处理"记住我"功能
            if remember_me:
                session.permanent = True
                logger.info(f"管理员 {username} 选择记住我，session有效期为7天")
            else:
                session.permanent = False
                logger.info(f"管理员 {username} 未选择记住我，session有效期1小时")

            logger.info(f"管理员 {username} 成功登录用户管理系统")
            
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
            
            return redirect(url_for('user_management.dashboard'))
        else:
            flash(f'登录失败: {result}', 'error')
            logger.warning(f"用户 {username} 登录失败: {result}")
            return render_template('user_management/login.html', username=username)
    
    return render_template('user_management/login.html')


@user_management_bp.route('/logout')
def logout():
    """退出登录"""
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"用户 {username} 退出用户管理系统")
    flash('您已成功退出登录', 'info')
    return redirect(url_for('user_management.login'))


@user_management_bp.route('/')
def dashboard():
    """用户管理仪表盘"""
    # 检查登录状态
    user = get_current_user()
    if not user:
        # 未登录,跳转到用户管理登录页面
        return redirect(url_for('user_management.login'))

    # 检查是否是管理员
    if user.get('role') != 'admin':
        # 不是管理员,显示权限不足
        return render_template('error.html',
                             error_message="权限不足，只有管理员才能访问此页面",
                             error_code=403), 403

    try:
        with db_connection('kb') as conn:
            import pymysql
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 获取用户列表
            cursor.execute("SELECT * FROM `users` ORDER BY created_at DESC")
            users = cursor.fetchall()

            # 获取最近登录日志
            cursor.execute("""
                SELECT l.*, u.username, u.display_name
                FROM mgmt_login_logs l
                LEFT JOIN `users` u ON l.user_id = u.id
                ORDER BY l.login_time DESC
                LIMIT 50
            """)
            login_logs = cursor.fetchall()

            return render_template('user_management/dashboard.html',
                                 users=users,
                                 login_logs=login_logs,
                                 total_count=len(users) if users else 0,
                                 current_user=user)
    except Exception as e:
        logger.error(f"加载用户管理仪表盘失败: {str(e)}")
        return render_template('user_management/dashboard.html',
                             users=[],
                             login_logs=[],
                             error=str(e),
                             total_count=0,
                             current_user=user)


@user_management_bp.route('/check-login')
def check_login():
    """检查登录状态(用于AJAX检查)"""
    user = get_current_user()
    if user and user.get('role') == 'admin':
        from common.response import success_response
        return success_response(data={'user': user}, message='已登录且是管理员')
    from common.response import unauthorized_response
    return unauthorized_response(message='未登录或不是管理员')




# 限流豁免配置 - 必须在所有路由定义后执行
# 使用延迟导入避免循环依赖
try:
    from app import limiter as app_limiter
    if app_limiter:
        # 豁免频繁调用的check-login端点
        app_limiter.exempt(check_login)
        print("[用户管理系统] check-login端点已豁免限流")
except ImportError:
    print("[用户管理系统] 无法导入limiter,跳过豁免配置")
except Exception as e:
    print(f"[用户管理系统: 豁免限流配置失败: {str(e)}")
