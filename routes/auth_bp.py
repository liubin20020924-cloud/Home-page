"""
认证路由蓝图 - 处理 /auth/api/ 路径的用户管理 API

注意：所有路由都已豁免 CSRF 保护，因为使用 session 认证
"""
from flask import Blueprint, request, session
from common.response import success_response, error_response, validation_error_response, server_error_response
from common.unified_auth import login_required, create_user
from common.validators import validate_user_data
from common.logger import logger, log_exception
from common.database_context import db_connection

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# 在路由定义后豁免 CSRF
def init_csrf_exemption():
    """初始化 CSRF 豁免"""
    try:
        from app import csrf
        if csrf:
            csrf.exempt(auth_bp)
    except (ImportError, AttributeError):
        pass


@auth_bp.route('/api/add-user', methods=['POST'])
@login_required(roles=['admin'])
def add_user():
    """添加知识库用户"""
    try:
        logger.info("添加用户请求")
        data = request.get_json()
        logger.info(f"接收到的数据: {data}")

        # 添加必填字段验证
        if not data.get('username') or not data.get('password'):
            logger.warning("添加用户失败：用户名或密码为空")
            return error_response('用户名和密码不能为空', 400)

        if not data.get('company_name'):
            logger.warning("添加用户失败：公司名称为空")
            return error_response('公司名称不能为空', 400)

        # 验证输入
        is_valid, errors = validate_user_data(data)
        if not is_valid:
            logger.warning(f"添加用户验证失败: {errors}")
            return validation_error_response(errors)

        # 使用统一用户创建接口
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

        logger.info(f"创建用户结果: success={success}, message={message}")

        if success:
            logger.info(f"添加用户 {data['username']} 成功")
            return success_response(message=message)
        else:
            logger.warning(f"添加用户失败: {message}")
            return error_response(message, 400)
    except Exception as e:
        log_exception(logger, "添加用户失败")
        return server_error_response(f'添加用户失败：{str(e)}')


@auth_bp.route('/api/update-user/<int:user_id>', methods=['PUT'])
@login_required(roles=['admin'])
def update_user(user_id):
    """更新知识库用户"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)

        logger.info(f"更新用户请求数据: {data}")

        # 输入验证 - 更新用户时不验证 username（用户名不可修改）
        is_valid, errors = validate_user_data(data, skip_username_validation=True)
        if not is_valid:
            logger.warning(f"用户数据验证失败: {errors}")
            return validation_error_response(errors)

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

        logger.info(f"更新用户 {user_id} 成功")
        return success_response(message='用户更新成功')

    except Exception as e:
        log_exception(logger, "更新用户失败")
        return server_error_response(f'更新用户失败：{str(e)}')


@auth_bp.route('/api/delete-user/<int:user_id>', methods=['DELETE'])
@login_required(roles=['admin'])
def delete_user(user_id):
    """删除知识库用户"""
    try:
        # 检查是否是当前登录用户
        if user_id == session.get('user_id'):
            return error_response('不能删除当前登录用户')

        # 先检查是否是 admin 用户（ID 为 1）
        if user_id == 1:
            return error_response('不能删除 admin 用户')

        with db_connection('kb') as conn:
            cursor = conn.cursor()

            # 检查用户是否存在
            cursor.execute("SELECT id, username, status FROM `users` WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            if not user:
                return error_response('用户不存在', 404)

            # 不删除用户，而是锁定用户（防止session复用）
            cursor.execute("UPDATE `users` SET status = 'locked', updated_at = NOW() WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()

        # 清除该用户的所有session（如果可能）
        try:
            from flask import session as session_class
            if hasattr(session_class, 'clear_all'):
                # 使用session.clear_all()清除所有session
                pass
        except:
            pass

        logger.info(f"锁定用户 {user_id} 成功，而不是删除（防止session复用）")
        return success_response(message='用户已锁定')

    except Exception as e:
        log_exception(logger, "删除用户失败")
        return server_error_response(f'删除用户失败：{str(e)}')



@auth_bp.route('/api/reset-password/<int:user_id>', methods=['POST'])
@login_required(roles=['admin'])
def reset_password(user_id):
    """重置用户密码"""
    try:
        data = request.get_json()
        new_password = data.get('password', '').strip()

        if not new_password:
            return error_response('请输入新密码')

        if len(new_password) < 6:
            return error_response('密码长度至少为6位')

        with db_connection('kb') as conn:
            cursor = conn.cursor()

            # 获取用户信息
            cursor.execute("SELECT id, username FROM `users` WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            if not user:
                return error_response('用户不存在', 404)

            # 检查是否是 admin 用户
            if user[1] == 'admin':
                return error_response('不能重置 admin 用户密码')

            # 更新密码
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash(new_password)

            cursor.execute(
                "UPDATE `users` SET password_hash = %s, password_type = %s, updated_at = NOW() WHERE id = %s",
                (password_hash, 'werkzeug', user_id)
            )
            conn.commit()
            cursor.close()

        logger.info(f"重置用户 {user_id} 密码成功")
        return success_response(message='密码重置成功')

    except Exception as e:
        log_exception(logger, "重置密码失败")
        return server_error_response(f'重置密码失败：{str(e)}')


@auth_bp.route('/api/change-password', methods=['POST'])
@login_required()
def change_password():
    """用户修改自己的密码"""
    try:
        username = session.get('username')
        if not username:
            return error_response('未登录', 401)

        data = request.get_json()
        old_password = data.get('old_password', '').strip()
        new_password = data.get('new_password', '').strip()

        # 验证输入
        if not old_password or not new_password:
            return error_response('旧密码和新密码不能为空')

        if len(new_password) < 6:
            return error_response('新密码长度至少为6位')

        if old_password == new_password:
            return error_response('新密码不能与旧密码相同')

        with db_connection('kb') as conn:
            cursor = conn.cursor()

            # 获取用户信息和密码
            cursor.execute(
                "SELECT id, username, password_hash FROM `users` WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()

            if not user:
                logger.error(f"用户 {username} 不存在")
                return error_response('用户不存在', 404)

            # 检查返回类型
            if isinstance(user, dict):
                user_id = user.get('id')
                password_hash = user.get('password_hash')
            else:
                user_id, _, password_hash = user

            # 验证旧密码
            from werkzeug.security import check_password_hash, generate_password_hash

            if not check_password_hash(password_hash, old_password):
                logger.warning(f"用户 {username} 旧密码验证失败")
                return error_response('旧密码错误')

            # 更新新密码
            new_password_hash = generate_password_hash(new_password)

            cursor.execute(
                "UPDATE `users` SET password_hash = %s, updated_at = NOW() WHERE id = %s",
                (new_password_hash, user_id)
            )
            conn.commit()
            cursor.close()

        logger.info(f"用户 {username} 修改密码成功")
        return success_response(message='密码修改成功')

    except Exception as e:
        log_exception(logger, "修改密码失败")
        return server_error_response(f'修改密码失败：{str(e)}')
