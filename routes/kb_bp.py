"""
知识库系统路由蓝图 - 认证和浏览
"""
from flask import Blueprint, request, redirect, url_for, session, render_template, Response, current_app, jsonify
from datetime import datetime, timedelta
import requests
from common.unified_auth import get_current_user, login_required
from common.logger import logger
from common.kb_utils import (
    fetch_all_records, fetch_record_by_id, fetch_records_by_name_with_pagination,
    get_total_count, fetch_records_with_pagination, get_kb_db_connection
)
from common.response import (
    success_response, error_response, not_found_response, unauthorized_response,
    forbidden_response, validation_error_response, server_error_response
)
import config

kb_bp = Blueprint('kb', __name__, url_prefix='/kb')

# 用户状态缓存（减少数据库查询）
_user_status_cache = {}


def check_force_password_change():
    """检查是否需要强制修改密码"""
    if session.get('force_password_change', False):
        logger.warning("用户需要强制修改密码，拒绝访问")
        return True
    return False


@kb_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    """知识库系统登录

    用户登录知识库系统
    ---
    tags:
      - 知识库-认证
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: username
        type: string
        required: true
        description: 用户名或邮箱
      - in: formData
        name: password
        type: string
        required: true
        description: 密码
    responses:
      200:
        description: 登录成功，重定向到知识库首页
      302:
        description: 已登录，重定向到知识库首页
    """
    user = get_current_user()
    if user:
        logger.info("用户已登录，重定向到知识库首页")
        return redirect(url_for('kb.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember', 'off') == 'on'

        if not username or not password:
            return render_template('kb/login.html', error="用户名或密码错误")

        from common.unified_auth import authenticate_user
        success, result = authenticate_user(username, password)


        if success:
            user_info = result
            session['user_id'] = user_info['id']
            session['username'] = user_info['username']
            session['display_name'] = user_info['display_name']
            session['role'] = user_info['role']
            session['login_time'] = datetime.now().isoformat()
            session['force_password_change'] = user_info.get('force_password_change', False)

            # 检查密码复杂度（不阻止登录，仅记录）
            from common.validators import check_password_strength
            is_strong, strength_msg = check_password_strength(password)
            session['password_strength_warning'] = None if is_strong else strength_msg
            if not is_strong:
                logger.info(f"用户 {username} 密码复杂度不足: {strength_msg}")

            # 处理"记住我"功能
            if remember_me:
                session.permanent = True
                logger.info(f"用户 {username} 选择记住我，session有效期为7天")
            else:
                session.permanent = False
                logger.info(f"用户 {username} 未选择记住我，session有效期1小时")

            # 记录来源系统（用于修改密码后跳转回）
            session['redirect_after_password_change'] = '/kb/'

            logger.info(f"用户 {username} 登录成功, 设置session: {list(session.keys())}, 强制修改密码: {user_info.get('force_password_change', False)}")

            # 检查是否为AJAX请求
            is_ajax = (request.headers.get('Accept') == 'application/json' or
                      request.headers.get('X-Requested-With') == 'XMLHttpRequest')

            # AJAX请求返回JSON
            if is_ajax:
                return jsonify({
                    'success': True,
                    'message': '登录成功',
                    'data': {
                        'username': user_info['username'],
                        'display_name': user_info.get('display_name', ''),
                        'role': user_info['role'],
                        'force_password_change': user_info.get('force_password_change', False)
                    }
                })
            else:
                # 普通表单提交，重定向
                next_url = request.form.get('next')

                # 检查是否需要强制修改密码
                if user_info.get('force_password_change', False):
                    logger.info(f"用户 {username} 需要强制修改密码, 跳转到修改密码页面")
                    return redirect(url_for('kb.change_password'))

                if next_url:
                    return redirect(next_url)
                return redirect(url_for('kb.index'))
        else:
            logger.warning(f"用户 {username} 登录失败: {result}")

            # 检查是否为AJAX请求
            is_ajax = (request.headers.get('Accept') == 'application/json' or
                      request.headers.get('X-Requested-With') == 'XMLHttpRequest')

            # AJAX请求返回JSON错误
            if is_ajax:
                return jsonify({
                    'success': False,
                    'error': result
                }), 401
            else:
                # 普通表单提交，渲染错误页面
                return render_template('kb/login.html', error=result, username=username)

    return render_template('kb/login.html')


@kb_bp.route('/auth/change-password', methods=['GET', 'POST'])
@login_required()
def change_password():
    """修改密码页面"""
    user = get_current_user()
    if not user:
        return redirect(url_for('kb.login'))

    # 检查是否需要强制修改密码
    force_password_change = session.get('force_password_change', False)

    if request.method == 'POST':
        from common.unified_auth import update_user_password
        from werkzeug.security import check_password_hash
        from common.db_manager import get_connection

        old_password = request.form.get('old_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        logger.info(f"修改密码请求 - 用户: {user['username']}, 旧密码长度: {len(old_password)}, 新密码长度: {len(new_password)}, 确认密码长度: {len(confirm_password)}")

        # 简单验证
        if not old_password or not new_password:
            logger.warning("修改密码失败: 请输入旧密码和新密码")
            return render_template('kb/change_password.html', error='请输入旧密码和新密码', force_password_change=force_password_change)
        if not confirm_password:
            logger.warning("修改密码失败: 请确认新密码")
            return render_template('kb/change_password.html', error='请确认新密码', force_password_change=force_password_change)
        if len(new_password) < 6:
            logger.warning("修改密码失败: 新密码长度至少为6位")
            return render_template('kb/change_password.html', error='新密码长度至少为6位', force_password_change=force_password_change)
        if new_password != confirm_password:
            logger.warning("修改密码失败: 两次输入的新密码不一致")
            return render_template('kb/change_password.html', error='两次输入的新密码不一致', force_password_change=force_password_change)

        # 验证旧密码 - 直接从数据库查询,不调用authenticate_user
        conn = get_connection('kb')
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT password_hash FROM `users` WHERE id = %s", (user['id'],))
                    result = cursor.fetchone()
                    if result:
                        password_hash = result[0] if isinstance(result, tuple) else result.get('password_hash')

                        # 验证旧密码
                        if not check_password_hash(password_hash, old_password):
                            logger.warning(f"修改密码失败: 旧密码密码错误")
                            return render_template('kb/change_password.html', error='旧密码错误', force_password_change=force_password_change)
                        logger.info("旧密码验证通过")
            finally:
                conn.close()

        # 更新新密码
        success, message = update_user_password(user['id'], new_password)
        if success:
            # 清除强制修改密码标记
            session.pop('force_password_change', None)
            # 清除force_password_change字段
            conn = get_connection('kb')
            if conn:
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("UPDATE `users` SET force_password_change = 0 WHERE id = %s", (user['id'],))
                        conn.commit()
                        logger.info(f"用户 {user['username']} 清除强制修改密码标记")
                finally:
                    conn.close()

            logger.info(f"用户 {user['username']} 修改密码成功")
            # 修改密码成功后跳转到来源系统
            redirect_url = session.pop('redirect_after_password_change', None)
            if redirect_url:
                logger.info(f"跳转回来源系统: {redirect_url}")
                return redirect(redirect_url)
            else:
                logger.info("跳转到知识库首页")
                return redirect(url_for('kb.index'))
        else:
            logger.error(f"修改密码失败: {message}")
            return render_template('kb/change_password.html', error=message, force_password_change=force_password_change)

    return render_template('kb/change_password.html', force_password_change=force_password_change)




@kb_bp.route('/auth/logout')
def logout():
    """退出登录"""
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"用户 {username} 退出登录")
    return redirect(url_for('kb.login'))


@kb_bp.route('/auth/check-login')
def check_login():
    """检查登录状态"""
    user = get_current_user()
    # 只在未登录时记录日志，避免正常使用时产生大量日志
    if not user:
        logger.debug(f"[知识库] 用户未登录")
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
                logger.warning(f"[知识库] 用户状态缓存异常: {cached_status}, 清除session, user_id: {user_id}")
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
                                logger.warning(f"[知识库] 用户session中的用户状态异常: {user_status}, 清除session, user_id: {user_id}")
                                session.clear()
                                return unauthorized_response(message='账户已被禁用，请重新登录')
                except Exception as e:
                    logger.error(f"验证用户状态失败: {str(e)}")
                finally:
                    conn.close()

    return success_response(data={'user': user}, message='已登录')


@kb_bp.route('/')
def index():
    """知识库首页"""
    # 检查是否已登录
    user = get_current_user()
    if not user:
        return render_template('kb/login.html')

    # 检查是否需要强制修改密码
    if check_force_password_change():
        return redirect(url_for('kb.change_password'))

    try:
        page = request.args.get('page', 1, type=int)
        per_page = 15
        records, total_count = fetch_records_with_pagination(page, per_page)
        total_pages = (total_count + per_page - 1) // per_page
        showing_start = (page - 1) * per_page + 1
        showing_end = min(page * per_page, total_count)

        # 获取Trilium基础URL
        trilium_base_url = getattr(config, 'TRILIUM_SERVER_URL', '').rstrip('/')

        return render_template('kb/index.html', records=records,
                             total_count=total_count,
                             showing_count=showing_end - showing_start + 1 if records else 0,
                             page=page,
                             per_page=per_page,
                             total_pages=total_pages,
                             showing_start=showing_start,
                             showing_end=showing_end,
                             is_search=False,
                             current_user=user,
                             trilium_base_url=trilium_base_url)
    except Exception as e:
        from common.response import error_response
        logger.error(f"加载知识库首页失败: {e}")

        # 获取Trilium基础URL
        trilium_base_url = getattr(config, 'TRILIUM_SERVER_URL', '').rstrip('/')

        return render_template('kb/index.html', records=[],
                             error=str(e),
                             total_count=0,
                             showing_count=0,
                             page=1,
                             per_page=15,
                             total_pages=1,
                             is_search=False,
                             current_user=user,
                             trilium_base_url=trilium_base_url)


@kb_bp.route('/search', methods=['GET'])
@login_required()
def search():
    """知识库搜索页面"""
    # 检查是否需要强制修改密码
    if check_force_password_change():
        return redirect(url_for('kb.change_password'))
    """搜索知识库"""
    search_id = request.args.get('id', '').strip()
    page = request.args.get('page', 1, type=int)

    # 获取Trilium基础URL
    trilium_base_url = getattr(config, 'TRILIUM_SERVER_URL', '').rstrip('/')

    if not search_id:
        return render_template('kb/index.html', records=[],
                             error="请输入搜索ID",
                             total_count=get_total_count(),
                             showing_count=0,
                             page=1,
                             per_page=15,
                             total_pages=1,
                             is_search=True,
                             search_id="",
                             trilium_base_url=trilium_base_url)

    try:
        record_id = int(search_id)
        record = fetch_record_by_id(record_id)

        if record:
            logger.info(f"搜索知识库记录: {record_id}")
            return render_template('kb/index.html', records=[record],
                                 total_count=1,
                                 showing_count=1,
                                 page=page,
                                 per_page=15,
                                 total_pages=1,
                                 search_id=search_id,
                                 is_search=True,
                                 trilium_base_url=trilium_base_url)
        else:
            return render_template('kb/index.html', records=[],
                                 error=f"未找到ID为 {search_id} 的记录",
                                 total_count=get_total_count(),
                                 showing_count=0,
                                 page=1,
                                 per_page=15,
                                 total_pages=1,
                                 search_id=search_id,
                                 is_search=True,
                                 trilium_base_url=trilium_base_url)
    except ValueError:
        return render_template('kb/index.html', records=[],
                             error="请输入有效的数字ID",
                             total_count=get_total_count(),
                             showing_count=0,
                             page=1,
                             per_page=15,
                             total_pages=1,
                             search_id=search_id,
                             is_search=True,
                             trilium_base_url=trilium_base_url)


@kb_bp.route('/api/all')
@login_required()
def get_all():
    """获取所有数据"""
    try:
        records = fetch_all_records()
        from common.response import success_response
        return success_response(data={'records': records, 'count': len(records)}, message='查询成功')
    except Exception as e:
        from common.response import server_error_response
        from common.logger import log_exception
        log_exception(logger, "获取所有知识库记录失败")
        return server_error_response(f"数据库错误: {str(e)}")


@kb_bp.route('/search/name', methods=['POST'])
@login_required()
def search_by_name():
    """按名称搜索"""
    name = request.form.get('name', '').strip()
    page = request.form.get('page', 1, type=int)
    per_page = request.form.get('per_page', 15, type=int)
    
    if not name:
        from common.response import error_response
        return error_response('请输入知识库名称', 400)
    
    try:
        records, total_count = fetch_records_by_name_with_pagination(name, page, per_page)
        total_pages = (total_count + per_page - 1) // per_page
        from common.response import success_response
        return success_response(
            data={
                'records': records,
                'count': len(records),
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            },
            message='搜索完成'
        )
    except Exception as e:
        from common.response import server_error_response
        from common.logger import log_exception
        log_exception(logger, "按名称搜索知识库记录失败")
        return server_error_response(f"搜索错误: {str(e)}")


@kb_bp.route('/api/stats')
@login_required()
def get_stats():
    """统计信息"""
    try:
        count = get_total_count()
        from common.response import success_response
        return success_response(data={'total_count': count}, message='查询成功')
    except Exception as e:
        from common.response import server_error_response
        from common.logger import log_exception
        log_exception(logger, "获取知识库统计信息失败")
        return server_error_response(f"统计信息获取失败: {str(e)}")


@kb_bp.route('/api/attachments/<path:attachment_path>')
def proxy_trilium_attachment(attachment_path):
    """代理 Trilium 附件请求，使用 ETAPI

    将前端请求的 Trilium 附件代理转发到 Trilium 服务器
    ---
    tags:
      - Trilium
    parameters:
      - name: attachment_path
        in: path
        type: string
        required: true
        description: 附件路径 (格式: ZjD0OZLY4aWU/image/f6f83bfe35c1711a70ed62a985ab1a92.png)
    responses:
      200:
        description: 附件内容
      404:
        description: 附件未找到
      500:
        description: 服务器错误
    """
    try:
        # 检查 Trilium 配置
        if not hasattr(config, 'TRILIUM_SERVER_URL') or not config.TRILIUM_SERVER_URL:
            logger.error("Trilium 服务未配置")
            from common.response import error_response
            return error_response('Trilium 服务未配置', 500)

        # attachment_path 格式: ZjD0OZLY4aWU/image/f6f83bfe35c1711a70ed62a985ab1a92.png
        # 提取 attachment_id (第一部分)
        parts = attachment_path.split('/')
        if not parts or len(parts) < 1:
            return Response('Invalid attachment path', status=400)

        attachment_id = parts[0]
        logger.info(f"代理 Trilium 附件: attachment_id={attachment_id}, full_path={attachment_path}")

        server_url = config.TRILIUM_SERVER_URL.rstrip('/')
        token = config.TRILIUM_TOKEN

        # 尝试使用 trilium-py 的 ETAPI 获取附件内容
        try:
            from trilium_py.client import ETAPI

            # 如果没有token，尝试使用密码登录
            if not token and hasattr(config, 'TRILIUM_LOGIN_PASSWORD'):
                ea = ETAPI(server_url)
                token = ea.login(config.TRILIUM_LOGIN_PASSWORD)
                logger.info("使用密码登录Trilium成功")
                if not token:
                    from common.response import error_response
                    return error_response('Trilium登录失败，请检查密码配置', 500)

            ea = ETAPI(server_url, token)

            # 获取附件内容
            attachment_content = ea.get_attachment_content(attachment_id)
        except ImportError:
            # 回退：直接通过API获取附件
            try:
                import requests
                headers = {}
                if token:
                    headers['Authorization'] = f'Bearer {token}'

                # Trilium 附件API端点
                attachment_url = f"{server_url}/api/attachments/{attachment_id}/content"
                response = requests.get(attachment_url, headers=headers, timeout=10)

                if response.status_code == 200:
                    attachment_content = response.content
                else:
                    logger.error(f"从 Trilium 获取附件失败: HTTP {response.status_code}")
                    return Response('Attachment not found', status=404)
            except Exception as api_error:
                logger.error(f"通过API获取Trilium附件失败: {api_error}")
                return Response(f'Failed to proxy attachment: {str(api_error)}', status=500)

        if attachment_content:
            # 返回图片内容
            return Response(
                attachment_content,
                mimetype='image/png',
                headers={
                    'Cache-Control': 'public, max-age=86400',  # 缓存 1 天
                }
            )
        else:
            logger.error(f"从 Trilium 获取附件失败: attachment_id={attachment_id}")
            return Response('Attachment not found', status=404)

    except Exception as e:
        logger.error(f"代理 Trilium 附件失败: {str(e)}")
        return Response(f'Failed to proxy attachment: {str(e)}', status=500)


@kb_bp.route('/test-check-login')
@login_required()
def test_check_login_page():
    """测试 check-login API 页面"""
    return render_template('test_check_login.html')




# 限流豁免配置 - 必须在所有路由定义后执行
# 使用延迟导入避免循环依赖
try:
    from app import limiter as app_limiter
    if app_limiter:
        # 豁免频繁调用的check-login端点
        app_limiter.exempt(check_login)
        print("[知识库系统] check-login端点已豁免限流")
except ImportError:
    print("[知识库系统] 无法导入limiter,跳过豁免配置")
except Exception as e:
    print(f"[知识库系统: 豁免限流配置失败: {str(e)}")




