"""
回复模板管理蓝图
"""
from flask import Blueprint, request, render_template, session
import pymysql
from common.response import success_response, error_response, validation_error_response, server_error_response
from common.logger import logger, log_exception
from common.database_context import db_connection
from common.auth_utils import admin_login_required

reply_templates_bp = Blueprint('reply_templates', __name__)


@reply_templates_bp.route('/admin/reply-templates')
@admin_login_required
def reply_templates_page():
    """回复模板管理页面"""
    return render_template('admin/reply_templates.html')


@reply_templates_bp.route('/admin/reply-templates/api/list')
@admin_login_required
def reply_templates_api_list():
    """获取回复模板列表 API"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        category = request.args.get('category', '')  # 分类筛选
        is_active = request.args.get('is_active', '')  # 启用状态筛选
        search = request.args.get('search', '')  # 搜索关键词

        with db_connection('home') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 构建查询条件
            where_clause = []
            params = []

            if category:
                where_clause.append("category = %s")
                params.append(category)

            if is_active != '':
                where_clause.append("is_active = %s")
                params.append(is_active)

            if search:
                where_clause.append("(name LIKE %s OR content LIKE %s OR description LIKE %s)")
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern])

            # 构建 WHERE 子句
            where_sql = ""
            if where_clause:
                where_sql = "WHERE " + " AND ".join(where_clause)

            # 获取总数
            count_sql = f"SELECT COUNT(*) as total FROM reply_templates {where_sql}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()['total']

            # 获取分页数据
            offset = (page - 1) * page_size
            list_sql = f"""
                SELECT id, name, category, content, description, is_active, is_system,
                       sort_order, use_count, created_by, updated_by, created_at, updated_at
                FROM reply_templates {where_sql}
                ORDER BY sort_order ASC, created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(list_sql, params + [page_size, offset])
            templates = cursor.fetchall()

            cursor.close()

            return success_response(data={
                'templates': templates,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            })

    except Exception as e:
        log_exception(logger, "获取回复模板列表失败")
        return server_error_response(f'获取回复模板列表失败：{str(e)}')


@reply_templates_bp.route('/admin/reply-templates/api/<int:template_id>', methods=['GET'])
@admin_login_required
def reply_templates_api_detail(template_id):
    """获取回复模板详情 API"""
    try:
        with db_connection('home') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            cursor.execute("SELECT * FROM reply_templates WHERE id = %s", (template_id,))
            template = cursor.fetchone()

            if not template:
                return error_response('模板不存在', 404)

            cursor.close()

            return success_response(data=template)

    except Exception as e:
        log_exception(logger, "获取回复模板详情失败")
        return server_error_response(f'获取回复模板详情失败：{str(e)}')


@reply_templates_bp.route('/admin/reply-templates/api', methods=['POST'])
@admin_login_required
def reply_templates_api_create():
    """创建回复模板 API"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)

        # 验证必填字段
        required_fields = ['name', 'category', 'content']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return validation_error_response(f'缺少必填字段: {", ".join(missing_fields)}')

        # 验证分类
        valid_categories = ['general', 'account', 'technical', 'billing', 'other']
        if data['category'] not in valid_categories:
            return error_response('无效的分类', 400)

        admin_username = session.get('username', 'unknown')

        with db_connection('home') as conn:
            cursor = conn.cursor()

            # 插入新模板
            insert_sql = """
                INSERT INTO reply_templates (name, category, content, description,
                                            is_active, is_system, sort_order, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                data['name'],
                data['category'],
                data['content'],
                data.get('description', ''),
                data.get('is_active', True),
                0,  # 非系统模板
                data.get('sort_order', 0),
                admin_username
            ))
            template_id = cursor.lastrowid
            conn.commit()
            cursor.close()

            logger.info(f"管理员 {admin_username} 创建回复模板成功，ID: {template_id}")
            return success_response(data={'id': template_id}, message='模板创建成功')

    except Exception as e:
        log_exception(logger, "创建回复模板失败")
        return server_error_response(f'创建回复模板失败：{str(e)}')


@reply_templates_bp.route('/admin/reply-templates/api/<int:template_id>', methods=['PUT'])
@admin_login_required
def reply_templates_api_update(template_id):
    """更新回复模板 API"""
    try:
        data = request.get_json()
        logger.info(f"收到更新模板请求: template_id={template_id}, data={data}")

        if not data:
            logger.warning("请求数据为空")
            return error_response('请求数据不能为空', 400)

        admin_username = session.get('username', 'unknown')

        with db_connection('home') as conn:
            cursor = conn.cursor()

            # 检查模板是否存在
            cursor.execute("SELECT id FROM reply_templates WHERE id = %s", (template_id,))
            template = cursor.fetchone()

            if not template:
                return error_response('模板不存在', 404)

            # 所有模板都可以修改所有字段
            update_fields = []
            update_values = []

            logger.info(f"待更新字段: {list(data.keys())}")

            if 'name' in data:
                if not data['name']:
                    return error_response('模板名称不能为空', 400)
                update_fields.append("name = %s")
                update_values.append(data['name'])
            if 'category' in data:
                valid_categories = ['general', 'account', 'technical', 'billing', 'other']
                if data['category'] not in valid_categories:
                    return error_response('无效的分类', 400)
                update_fields.append("category = %s")
                update_values.append(data['category'])
            if 'content' in data:
                if not data['content']:
                    return error_response('模板内容不能为空', 400)
                update_fields.append("content = %s")
                update_values.append(data['content'])
            if 'description' in data:
                update_fields.append("description = %s")
                update_values.append(data['description'])
            if 'is_active' in data:
                update_fields.append("is_active = %s")
                update_values.append(data['is_active'])
            if 'sort_order' in data:
                update_fields.append("sort_order = %s")
                update_values.append(data['sort_order'])

            if update_fields:
                update_fields.append("updated_by = %s")
                update_values.append(admin_username)
                update_values.append(template_id)

                update_sql = f"UPDATE reply_templates SET {', '.join(update_fields)} WHERE id = %s"
                logger.info(f"执行SQL: {update_sql}")
                logger.info(f"参数: {update_values}")
                cursor.execute(update_sql, update_values)
            else:
                return error_response('没有要更新的字段', 400)

            conn.commit()
            cursor.close()

            logger.info(f"管理员 {admin_username} 更新回复模板 {template_id} 成功")
            return success_response(message='模板更新成功')

    except Exception as e:
        log_exception(logger, "更新回复模板失败")
        return server_error_response(f'更新回复模板失败：{str(e)}')


@reply_templates_bp.route('/admin/reply-templates/api/<int:template_id>', methods=['DELETE'])
@admin_login_required
def reply_templates_api_delete(template_id):
    """删除回复模板 API"""
    try:
        with db_connection('home') as conn:
            cursor = conn.cursor()

            # 检查模板是否存在
            cursor.execute("SELECT is_system FROM reply_templates WHERE id = %s", (template_id,))
            template = cursor.fetchone()

            if not template:
                return error_response('模板不存在', 404)

            # 系统模板不允许删除
            if template[0] == 1:
                return error_response('系统模板不允许删除', 400)

            # 删除模板
            cursor.execute("DELETE FROM reply_templates WHERE id = %s", (template_id,))
            conn.commit()
            cursor.close()

            logger.info(f"回复模板 {template_id} 删除成功")
            return success_response(message='模板删除成功')

    except Exception as e:
        log_exception(logger, "删除回复模板失败")
        return server_error_response(f'删除回复模板失败：{str(e)}')


@reply_templates_bp.route('/admin/reply-templates/api/<int:template_id>/increment-use', methods=['POST'])
@admin_login_required
def reply_templates_api_increment_use(template_id):
    """增加模板使用次数 API"""
    try:
        with db_connection('home') as conn:
            cursor = conn.cursor()

            # 增加使用次数
            cursor.execute(
                "UPDATE reply_templates SET use_count = use_count + 1 WHERE id = %s",
                (template_id,)
            )
            conn.commit()
            cursor.close()

            return success_response(message='使用次数已更新')

    except Exception as e:
        log_exception(logger, "更新模板使用次数失败")
        return server_error_response(f'更新模板使用次数失败：{str(e)}')


@reply_templates_bp.route('/admin/reply-templates/api/preview', methods=['POST'])
@admin_login_required
def reply_templates_api_preview():
    """预览模板内容（替换变量）API"""
    try:
        data = request.get_json()
        if not data:
            return error_response('请求数据不能为空', 400)

        template_content = data.get('content', '')
        variables = data.get('variables', {})

        # 替换变量
        preview_content = template_content
        for key, value in variables.items():
            preview_content = preview_content.replace(f'{{{key}}}', str(value))

        return success_response(data={'preview': preview_content})

    except Exception as e:
        log_exception(logger, "预览模板内容失败")
        return server_error_response(f'预览模板内容失败：{str(e)}')
