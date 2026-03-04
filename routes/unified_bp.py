"""
统一用户管理路由蓝图
"""
from flask import Blueprint, request, render_template, session
from common.response import success_response, error_response, validation_error_response, server_error_response
from common.unified_auth import login_required, get_current_user, create_user
from common.validators import validate_user_data
from common.logger import logger, log_request, log_exception
from services.user_service import UserService
from common.database_context import db_connection
from werkzeug.security import generate_password_hash

unified_bp = Blueprint('unified', __name__, url_prefix='/unified')


@unified_bp.route('/users')
@login_required(roles=['admin'])
def users():
    """统一用户管理页面"""
    return render_template('unified_user_management.html',
                         users=[],
                         error=None,
                         current_user=get_current_user())


@unified_bp.route('/api/users', methods=['GET'])
@login_required(roles=['admin'])
def get_users():
    """获取统一用户列表
    
    获取所有用户列表
    ---
    tags:
      - 用户管理
    security:
      - CookieAuth: []
    responses:
      200:
        description: 获取成功
        schema:
          $ref: '#/definitions/SuccessResponse'
    """
    try:
        log_request(logger, request)
        with db_connection('kb') as conn:
            users, total = UserService.get_users(conn)
            return success_response(data=users, message='获取用户列表成功')
    except Exception as e:
        log_exception(logger, "获取用户列表失败")
        return server_error_response(message=f'获取用户列表失败：{str(e)}')


@unified_bp.route('/api/users', methods=['POST'])
@login_required(roles=['admin'])
def add_user():
    """添加统一用户
    
    创建新用户
    ---
    tags:
      - 用户管理
    security:
      - CookieAuth: []
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
            display_name:
              type: string
              description: 显示名称
            email:
              type: string
              format: email
              description: 邮箱
            role:
              type: string
              enum: [admin, user, editor, customer]
              description: 角色
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
        data = request.get_json()
        
        # 验证输入
        is_valid, errors = validate_user_data(data)
        if not is_valid:
            return validation_error_response(errors)
        
        # 添加必填字段验证
        if not data.get('username') or not data.get('password'):
            return error_response('用户名和密码不能为空', 400)
        
        if not data.get('company_name'):
            return error_response('公司名称不能为空', 400)
        
        # 使用统一用户创建接口
        success, message = create_user(
            username=data['username'],
            password=data['password'],
            display_name=data.get('display_name'),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            company_name=data.get('company_name', ''),
            role=data.get('role', 'user'),
            created_by=session.get('username', 'admin')
        )
        
        if success:
            logger.info(f"用户创建成功: {data['username']}")
            return success_response(message=message)
        else:
            return error_response(message=message)
    except Exception as e:
        log_exception(logger, "添加用户失败")
        return server_error_response(message=f'添加用户失败：{str(e)}')


@unified_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required(roles=['admin'])
def update_user(user_id):
    """更新统一用户
    
    更新用户信息
    ---
    tags:
      - 用户管理
    security:
      - CookieAuth: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用户ID
      - in: body
        name: body
        schema:
          type: object
          properties:
            display_name:
              type: string
            role:
              type: string
            email:
              type: string
            status:
              type: string
            password:
              type: string
              description: 新密码（可选）
    responses:
      200:
        description: 更新成功
        schema:
          $ref: '#/definitions/SuccessResponse'
      400:
        description: 参数错误
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    try:
        log_request(logger, request)
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)
        
        with db_connection('kb') as conn:
            # 调用服务层
            success, message = UserService.update_user(conn, user_id, data)
            
            if success:
                logger.info(f"更新用户 {user_id} 成功")
                return success_response(message=message)
            else:
                return error_response(message, 400)
    except Exception as e:
        log_exception(logger, "更新用户失败")
        return server_error_response(message=f'更新用户失败：{str(e)}')


@unified_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required(roles=['admin'])
def delete_user(user_id):
    """删除统一用户
    
    删除指定用户
    ---
    tags:
      - 用户管理
    security:
      - CookieAuth: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用户ID
    responses:
      200:
        description: 删除成功
        schema:
          $ref: '#/definitions/SuccessResponse'
      400:
        description: 不能删除当前用户或admin用户
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    try:
        log_request(logger, request)
        
        with db_connection('kb') as conn:
            # 检查是否是当前登录用户
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM `users` WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user and user[0] == session.get('username'):
                cursor.close()
                return error_response('不能删除当前登录用户')
            cursor.close()
            
            # 调用服务层
            success, message = UserService.delete_user(conn, user_id)
            
            if success:
                logger.info(f"用户删除成功: {user_id}")
                return success_response(message=message)
            else:
                return error_response(message, 400)
    except Exception as e:
        log_exception(logger, "删除用户失败")
        return server_error_response(message=f'删除用户失败：{str(e)}')


@unified_bp.route('/api/user-stats', methods=['GET'])
@login_required(roles=['admin'])
def get_user_stats():
    """获取用户统计信息
    
    获取用户和登录日志统计
    ---
    tags:
      - 用户管理
    security:
      - CookieAuth: []
    responses:
      200:
        description: 查询成功
        schema:
          $ref: '#/definitions/SuccessResponse'
    """
    try:
        log_request(logger, request)
        stats = {
            'users': {'total': 0, 'active': 0, 'admins': 0, 'customers': 0, 'kb_users': 0},
            'login_logs': {'total': 0, 'today': 0, 'success': 0, 'failed': 0}
        }
        
        # 统一用户表统计
        with db_connection('kb') as conn:
            import pymysql
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # 总用户数
            cursor.execute("SELECT COUNT(*) as total FROM `users`")
            stats['users']['total'] = cursor.fetchone()['total']
            
            # 活跃用户数
            cursor.execute("SELECT COUNT(*) as count FROM `users` WHERE status = 'active'")
            stats['users']['active'] = cursor.fetchone()['count']
            
            # 管理员数量
            cursor.execute("SELECT COUNT(*) as count FROM `users` WHERE role = 'admin'")
            stats['users']['admins'] = cursor.fetchone()['count']
            
            # 客户数量
            cursor.execute("SELECT COUNT(*) as count FROM `users` WHERE role = 'customer'")
            stats['users']['customers'] = cursor.fetchone()['count']
            
            # 知识库用户数
            cursor.execute("SELECT COUNT(*) as count FROM `users` WHERE role IN ('admin', 'user')")
            stats['users']['kb_users'] = cursor.fetchone()['count']
            
            # 登录日志统计
            cursor.execute("SELECT COUNT(*) as total FROM mgmt_login_logs")
            stats['login_logs']['total'] = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as count FROM mgmt_login_logs WHERE DATE(login_time) = CURDATE()")
            stats['login_logs']['today'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM mgmt_login_logs WHERE status = 'success'")
            stats['login_logs']['success'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM mgmt_login_logs WHERE status = 'failed'")
            stats['login_logs']['failed'] = cursor.fetchone()['count']
            
            cursor.close()
        
        return success_response(data=stats, message='获取统计信息成功')
    except Exception as e:
        log_exception(logger, "获取统计信息失败")
        return server_error_response(message=f'获取统计信息失败：{str(e)}')


@unified_bp.route('/auth/api/reset-password/<int:user_id>', methods=['POST'])
@login_required(roles=['admin'])
def reset_user_password(user_id):
    """管理员重置指定用户的密码
    
    重置用户密码
    ---
    tags:
      - 用户管理
    security:
      - CookieAuth: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用户ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - password
          properties:
            password:
              type: string
              description: 新密码
    responses:
      200:
        description: 重置成功
        schema:
          $ref: '#/definitions/SuccessResponse'
      400:
        description: 参数错误或权限不足
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    try:
        log_request(logger, request)
        
        with db_connection('kb') as conn:
            cursor = conn.cursor()
            
            # 获取用户信息
            cursor.execute("SELECT username FROM `users` WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                from common.response import not_found_response
                return not_found_response(message='用户不存在')
            
            username = user[0]
            
            # 检查是否是admin用户
            if username == 'admin':
                cursor.close()
                return error_response('不能重置admin用户密码')
            
            data = request.get_json()
            new_password = data.get('password', '').strip()
            
            if not new_password:
                return error_response('请输入新密码')
            
            if len(new_password) < 6:
                return error_response('密码长度至少为6位')
            
            # 生成新的 werkzeug 密码哈希
            password_hash = generate_password_hash(new_password)
            
            update_sql = "UPDATE `users` SET password_hash = %s, password_type = %s, updated_at = NOW() WHERE id = %s"
            cursor.execute(update_sql, (password_hash, 'werkzeug', user_id))
            conn.commit()
            cursor.close()
        
        logger.info(f"管理员重置用户密码成功: {username}")
        return success_response(message=f'用户 {username} 的密码已重置')
    except Exception as e:
        log_exception(logger, "重置用户密码失败")
        return server_error_response(message=f'重置密码失败：{str(e)}')
