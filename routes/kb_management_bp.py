"""
知识库系统路由蓝图 - 管理功能（需要管理员权限）
"""
from flask import Blueprint, request, render_template, session, jsonify
from common.unified_auth import login_required, get_current_user
from common.response import success_response, error_response, validation_error_response, server_error_response
from common.validators import validate_required
from common.logger import logger, log_exception
from common.kb_utils import fetch_record_by_id, fetch_records_with_pagination, get_total_count, fetch_all_records, serialize_records
from common.database_context import db_connection
from datetime import datetime

kb_management_bp = Blueprint('kb_management', __name__, url_prefix='/kb/MGMT')

# 缓存Trilium笔记列表，避免重复获取
_trilium_notes_cache = {
    'data': None,
    'timestamp': 0,
    'ttl': 300  # 5分钟缓存
}





@kb_management_bp.route('/')
@login_required(roles=['admin'])
def management():
    """管理页面"""
    user = get_current_user()
    try:
        username = user.get('username') if user else 'unknown'
        logger.info(f"用户 {username} 访问知识库管理页面")
        page = request.args.get('page', 1, type=int)
        per_page = 20
        logger.info(f"分页参数: page={page}, per_page={per_page}")

        records, total_count = fetch_records_with_pagination(page, per_page)
        logger.info(f"获取到 records={len(records)} 条, total_count={total_count}")

        # 序列化 datetime 对象为字符串（用于 JavaScript）
        records_json = serialize_records(records) if records else []

        total_pages = (total_count + per_page - 1) // per_page
        showing_start = (page - 1) * per_page + 1
        showing_end = min(page * per_page, total_count)

        logger.info(f"渲染管理页面，传递 total_count={total_count}, records_json length={len(records_json)}")
        return render_template('kb/management.html', records=records,
                             records_json=records_json,
                             total_count=total_count,
                             showing_count=showing_end - showing_start + 1 if records else 0,
                             page=page,
                             per_page=per_page,
                             total_pages=total_pages,
                             showing_start=showing_start,
                             showing_end=showing_end,
                             current_user=user,
                             debug_mode=False)
    except Exception as e:
        logger.error(f"加载知识库管理页面失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return render_template('kb/management.html', records=[],
                             records_json=[],
                             error=str(e),
                             total_count=0,
                             page=1,
                             per_page=20,
                             total_pages=1)


@kb_management_bp.route('/api/add', methods=['POST'])
@login_required(roles=['admin'])
def add_record():
    """添加记录

    添加新的知识库记录
    ---
    tags:
      - 知识库-管理
    security:
      - CookieAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - KB_Number
            - KB_Name
          properties:
            KB_Number:
              type: integer
              description: 知识库编号
            KB_Name:
              type: string
              description: 知识库名称
            KB_link:
              type: string
              description: 知识库链接
    responses:
      200:
        description: 添加成功
        schema:
          $ref: '#/definitions/SuccessResponse'
      400:
        description: 参数错误或记录已存在
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    try:
        data = request.get_json()

        # 验证必填字段 - KB_Name 是必填的，KB_Number 可以为空（自动分配）
        if not data.get('KB_Name'):
            return error_response('知识库名称不能为空', 400)

        # 如果用户没有提供 KB_Number，自动分配（使用最大编号+1）
        if not data.get('KB_Number'):
            with db_connection('kb') as conn:
                cursor = conn.cursor()
                # 获取最大编号
                cursor.execute("SELECT MAX(KB_Number) as max_number FROM `KB-info`")
                result = cursor.fetchone()
                max_number = result['max_number'] if result and result['max_number'] else 0

                # 新编号 = 最大编号 + 1
                data['KB_Number'] = max_number + 1
                logger.info(f"自动分配编号: {data['KB_Number']} (最大编号: {max_number})")

        # 检查编号是否已存在
        existing = fetch_record_by_id(data['KB_Number'])
        if existing:
            return error_response(f"编号 {data['KB_Number']} 已存在", 400)

        # 截断过长的名称（避免数据库错误）
        kb_name = str(data['KB_Name'])[:500]  # 数据库字段最大长度
        if len(data['KB_Name']) > 500:
            logger.warning(f"知识库名称过长，已截断：{len(data['KB_Name'])} -> 500，编号：{data['KB_Number']}")

        with db_connection('kb') as conn:
            cursor = conn.cursor()
            sql = "INSERT INTO `KB-info` (KB_Number, KB_Name, KB_link) VALUES (%s, %s, %s)"
            cursor.execute(sql, (data['KB_Number'], kb_name, data.get('KB_link', '')))
            conn.commit()
            affected_rows = cursor.rowcount

        if affected_rows > 0:
            logger.info(f"添加知识库记录 {data['KB_Number']} 成功")
            return success_response(message='记录添加成功', data={'id': data['KB_Number']})
        else:
            return error_response('添加记录失败', 500)
    except Exception as e:
        log_exception(logger, "添加知识库记录失败")
        return server_error_response(f"添加记录时发生错误: {str(e)}")


@kb_management_bp.route('/api/next-number', methods=['GET'])
@login_required(roles=['admin'])
def get_next_available_number():
    """获取下一个可用的编号

    查找第一个未被使用的知识库编号
    ---
    tags:
      - 知识库-管理
    responses:
      200:
        description: 获取成功
        schema:
          type: object
          properties:
            success:
              type: boolean
            next_number:
              type: integer
              description: 下一个可用编号
            used_numbers:
              type: array
              description: 已使用的编号列表
    """
    try:
        with db_connection('kb') as conn:
            cursor = conn.cursor()
            # 获取最大编号
            cursor.execute("SELECT MAX(KB_Number) as max_number FROM `KB-info`")
            result = cursor.fetchone()
            max_number = result['max_number'] if result and result['max_number'] else 0

        # 下一个可用编号 = 最大编号 + 1
        next_number = max_number + 1

        return success_response(
            data={
                'next_number': next_number,
                'used_numbers': []  # 不再返回已使用编号列表
            },
            message=f'找到下一个可用编号：{next_number} (当前最大编号: {max_number})'
        )
    except Exception as e:
        log_exception(logger, "获取下一个可用编号失败")
        return server_error_response(f"获取编号失败: {str(e)}")


@kb_management_bp.route('/api/batch-add', methods=['POST'])
@login_required(roles=['admin'])
def batch_add_records():
    """批量添加记录

    批量添加知识库记录，用于Trilium笔记导入
    ---
    tags:
      - 知识库-管理
    security:
      - CookieAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - records
          properties:
            records:
              type: array
              description: 要添加的记录列表
              items:
                type: object
                properties:
                  noteId:
                    type: string
                    description: Trilium笔记ID
                  title:
                    type: string
                    description: 笔记标题
            start_number:
              type: integer
              description: 起始编号（可选，默认使用下一个可用编号）
    responses:
      200:
        description: 批量添加成功
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                success_count:
                  type: integer
                  description: 成功添加的数量
                fail_count:
                  type: integer
                  description: 失败的数量
                failed_items:
                  type: array
                  description: 失败的记录详情
                  items:
                    type: object
                    properties:
                      noteId:
                        type: string
                      title:
                        type: string
                      reason:
                        type: string
    """
    try:
        data = request.get_json()
        records = data.get('records', [])
        start_number = data.get('start_number')

        if not records:
            return error_response('没有要添加的记录', 400)

        # 获取起始编号
        if start_number is None:
            with db_connection('kb') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(KB_Number) as max_number FROM `KB-info`")
                result = cursor.fetchone()
                max_number = result['max_number'] if result and result['max_number'] else 0
                current_number = max_number + 1
        else:
            current_number = start_number

        success_count = 0
        fail_count = 0
        failed_items = []

        # 批量插入
        with db_connection('kb') as conn:
            cursor = conn.cursor()

            for record in records:
                note_id = record.get('noteId', '')
                title = record.get('title', '')

                # 检查编号是否已存在
                while True:
                    cursor.execute("SELECT KB_Number FROM `KB-info` WHERE KB_Number = %s", (current_number,))
                    if cursor.fetchone():
                        current_number += 1
                    else:
                        break

                # 截断过长的名称
                kb_name = str(title)[:500]

                try:
                    sql = "INSERT INTO `KB-info` (KB_Number, KB_Name, KB_link) VALUES (%s, %s, %s)"
                    kb_link = f"{request.host_url}#/root/{note_id}" if note_id else ""
                    cursor.execute(sql, (current_number, kb_name, kb_link))
                    success_count += 1
                    logger.info(f"批量导入成功: KB_Number={current_number}, title={title}")
                    current_number += 1
                except Exception as e:
                    fail_count += 1
                    failed_items.append({
                        'noteId': note_id,
                        'title': title,
                        'reason': str(e)
                    })
                    logger.error(f"批量导入失败: noteId={note_id}, title={title}, error={e}")
                    # 跳过冲突的编号
                    current_number += 1

            conn.commit()

        return success_response(
            message=f'批量导入完成，成功 {success_count} 条，失败 {fail_count} 条',
            data={
                'success_count': success_count,
                'fail_count': fail_count,
                'failed_items': failed_items
            }
        )
    except Exception as e:
        log_exception(logger, "批量添加知识库记录失败")
        return server_error_response(f"批量添加记录时发生错误: {str(e)}")


@kb_management_bp.route('/api/trilium/search', methods=['GET'])
@login_required(roles=['admin'])
def search_trilium_notes():
    """搜索Trilium笔记
    
    搜索Trilium笔记，用于快速添加到知识库
    ---
    tags:
      - 知识库-管理
    parameters:
      - in: query
        name: query
        type: string
        required: true
        description: 搜索关键词
      - in: query
        name: limit
        type: integer
        default: 20
        description: 返回结果数量限制
    responses:
      200:
        description: 搜索成功
        schema:
          type: object
          properties:
            success:
              type: boolean
            results:
              type: array
              items:
                type: object
                properties:
                  noteId:
                    type: string
                    description: 笔记ID
                  title:
                    type: string
                    description: 笔记标题
                  type:
                    type: string
                    description: 笔记类型
                  dateModified:
                    type: string
                    description: 修改时间
    """
    try:
        query = request.args.get('query', '').strip()
        limit = request.args.get('limit', 20, type=int)

        if not query:
            return error_response('搜索关键词不能为空', 400)

        # 使用TriliumHelper搜索笔记
        from common.trilium_helper import get_trilium_helper
        trilium = get_trilium_helper()

        success, results, message = trilium.search_note(query, limit)

        if success:
            return success_response(
                message='搜索成功',
                data={'results': results}
            )
        else:
            return error_response(message, 500)

    except Exception as e:
        log_exception(logger, "搜索Trilium笔记失败")
        return server_error_response(f"搜索失败: {str(e)}")


@kb_management_bp.route('/api/trilium/note/<note_id>', methods=['GET'])
@login_required(roles=['admin'])
def get_trilium_note():
    """获取Trilium笔记信息

    获取指定Trilium笔记的详细信息
    ---
    tags:
      - 知识库-管理
    parameters:
      - in: path
        name: note_id
        type: string
        required: true
        description: 笔记ID
    responses:
      200:
        description: 获取成功
        schema:
          type: object
          properties:
            success:
              type: boolean
            note:
              type: object
              properties:
                noteId:
                  type: string
                title:
                  type: string
                content:
                  type: string
    """
    try:
        note_id = request.args.get('note_id', '').strip()

        if not note_id:
            return error_response('笔记ID不能为空', 400)

        # 使用TriliumHelper获取笔记内容
        from common.trilium_helper import get_trilium_helper
        trilium = get_trilium_helper()

        # 构建笔记URL
        note_url = f"#root/{note_id}"
        success, content, message = trilium.get_note_content(note_url)

        if success:
            # 获取笔记基本信息
            try:
                from trilium_py.client import ETAPI
                import config

                server_url = config.TRILIUM_SERVER_URL.rstrip('/')
                token = config.TRILIUM_TOKEN

                if token:
                    ea = ETAPI(server_url, token)
                    note_info = ea.get_note(note_id)

                    note_data = {
                        'noteId': note_id,
                        'title': note_info.get('title', ''),
                        'content': content,
                        'type': note_info.get('type', 'text'),
                        'dateModified': note_info.get('utcDateModified', '')
                    }
                else:
                    note_data = {
                        'noteId': note_id,
                        'title': note_id,
                        'content': content
                    }
            except ImportError:
                note_data = {
                    'noteId': note_id,
                    'title': note_id,
                    'content': content
                }
            except Exception as e:
                logger.warning(f"获取笔记元数据失败: {e}")
                note_data = {
                    'noteId': note_id,
                    'title': note_id,
                    'content': content
                }

            return success_response(
                message='获取成功',
                data={'note': note_data}
            )
        else:
            return error_response(message, 404)

    except Exception as e:
        log_exception(logger, "获取Trilium笔记失败")
        return server_error_response(f"获取笔记失败: {str(e)}")


@kb_management_bp.route('/api/trilium/clear-cache', methods=['POST'])
@login_required(roles=['admin'])
def clear_trilium_cache():
    """清除Trilium笔记缓存"""
    global _trilium_notes_cache
    _trilium_notes_cache = {'data': None, 'timestamp': 0, 'ttl': 300}
    logger.info("Trilium笔记缓存已清除")
    return success_response(message='缓存已清除')


@kb_management_bp.route('/api/trilium/unimported', methods=['GET'])
@login_required(roles=['admin'])
def get_unimported_notes():
    """获取未导入的Trilium笔记

    获取Trilium中所有笔记，排除已导入到知识库的笔记
    ---
    tags:
      - 知识库-管理
    parameters:
      - in: query
        name: search
        type: string
        required: false
        description: 筛选关键词
      - in: query
        name: limit
        type: integer
        default: 100
        description: 返回结果数量限制
      - in: query
        name: refresh
        type: boolean
        default: false
        description: 是否强制刷新缓存
    responses:
      200:
        description: 获取成功
        schema:
          type: object
          properties:
            success:
              type: boolean
            results:
              type: array
              description: 未导入的笔记列表
    """
    try:
        import time

        search = request.args.get('search', '').strip()
        limit = request.args.get('limit', 100, type=int)
        refresh = request.args.get('refresh', 'false').lower() == 'true'

        logger.info(f"获取未导入笔记: search='{search}', limit={limit}, refresh={refresh}")

        # 性能优化：使用集合进行快速查找
        # 预编译排除关键词列表为集合，提高查找速度
        excluded_prefixes = {'_', 'config', 'settings', 'sys', 'hidden', 'trilium'}
        excluded_keywords = {
            '设置', '配置', '设置', 'config', 'settings', 'config.',
            'system', 'sys', 'trilium', 'attributes', 'attributeset',
            'hidden', 'private', 'deleted', 'recycle'
        }

        # 获取知识库中已导入的笔记ID（一次性获取所有）
        imported_note_ids = set()
        try:
            import pymysql
            with db_connection('kb') as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute("SELECT KB_link FROM `KB-info` WHERE KB_link IS NOT NULL AND KB_link != ''")
                rows = cursor.fetchall()

                # 批量提取noteId，减少循环中的字符串操作
                for row in rows:
                    kb_link = row.get('KB_link')
                    if kb_link and '/#/root/' in kb_link:
                        # 从链接中提取noteId
                        note_id = kb_link.split('/#/root/')[-1].split('?')[0]
                        imported_note_ids.add(note_id)
        except Exception as db_err:
            logger.error(f"获取已导入笔记ID失败: {db_err}")
            # 即使获取已导入笔记失败，也继续执行，只是无法过滤

        # 获取 Trilium 中的所有笔记（使用缓存）
        global _trilium_notes_cache
        current_time = time.time()

        # 检查缓存是否有效
        if not refresh and _trilium_notes_cache['data'] and (current_time - _trilium_notes_cache['timestamp']) < _trilium_notes_cache['ttl']:
            logger.info(f"使用缓存数据: {len(_trilium_notes_cache['data'])} 条笔记")
            all_trilium_notes = _trilium_notes_cache['data']
        else:
            # 缓存过期或强制刷新，重新获取
            from common.trilium_helper import get_trilium_helper
            trilium = get_trilium_helper()

            logger.info("开始获取 Trilium 所有笔记...")
            start_time = time.time()
            success, all_trilium_notes, message = trilium.get_all_notes()
            elapsed_time = time.time() - start_time

            if not success:
                logger.error(f"获取 Trilium 所有笔记失败: {message}")
                return error_response(f"获取 Trilium 笔记失败: {message}")

            # 更新缓存
            _trilium_notes_cache['data'] = all_trilium_notes
            _trilium_notes_cache['timestamp'] = current_time
            logger.info(f"Trilium 共有 {len(all_trilium_notes)} 条笔记，耗时 {elapsed_time:.2f}秒，已缓存")

        logger.info(f"已导入 {len(imported_note_ids)} 条笔记")

        # 性能优化：使用生成器表达式 + 过滤器，一次性完成所有过滤
        # 避免创建多个中间列表，减少内存使用
        def filter_notes(notes):
            """高效过滤笔记的生成器"""
            for note in notes:
                # 快速类型检查（最先过滤）
                if note.get('type', 'text') != 'text':
                    continue

                note_id = note.get('noteId', '').lower()

                # 快速ID前缀检查
                if any(note_id.startswith(prefix) for prefix in excluded_prefixes):
                    continue

                # 跳过已导入的笔记（使用集合快速查找）
                if note.get('noteId', '') in imported_note_ids:
                    continue

                # 最后检查标题（相对较慢的操作）
                title = note.get('title', '').lower()
                if any(keyword in title for keyword in excluded_keywords):
                    continue

                # 应用搜索关键词过滤（如果有）
                if search:
                    search_lower = search.lower()
                    if not (search_lower in title or search_lower in note_id):
                        continue

                yield note

        # 使用生成器一次性完成所有过滤和分页
        # 只获取limit数量的结果，避免处理所有笔记
        all_unimported = []
        for i, note in enumerate(filter_notes(all_trilium_notes)):
            if i >= limit:
                break
            all_unimported.append(note)

        # 统计总数（只计算一次）
        total_count = sum(1 for _ in filter_notes(all_trilium_notes))

        logger.info(f"过滤后返回: {len(all_unimported)} 条（共 {total_count} 条可用）")

        return success_response(
            message='获取成功',
            data={
                'results': all_unimported,
                'total': total_count,
                'imported_count': len(imported_note_ids),
                'from_cache': not refresh and _trilium_notes_cache['data'] and (current_time - _trilium_notes_cache['timestamp']) < _trilium_notes_cache['ttl']
            }
        )

    except Exception as e:
        log_exception(logger, "获取未导入笔记失败")
        return server_error_response(f"获取未导入笔记失败: {str(e)}")


@kb_management_bp.route('/api/update/<int:record_id>', methods=['PUT'])
@login_required(roles=['admin'])
def update_record(record_id):
    """更新记录"""
    try:
        data = request.get_json()
        existing = fetch_record_by_id(record_id)
        if not existing:
            return error_response(f"记录 {record_id} 不存在", 404)

        with db_connection('kb') as conn:
            cursor = conn.cursor()
            sql = "UPDATE `KB-info` SET KB_Name = %s, KB_link = %s WHERE KB_Number = %s"
            cursor.execute(sql, (data.get('KB_Name', existing['KB_Name']), data.get('KB_link', existing['KB_link']), record_id))
            conn.commit()
            affected_rows = cursor.rowcount

        if affected_rows > 0:
            logger.info(f"更新知识库记录 {record_id} 成功")
            return success_response(message='记录更新成功')
        else:
            return error_response('更新记录失败', 500)
    except Exception as e:
        log_exception(logger, "更新知识库记录失败")
        return server_error_response(f"更新记录时发生错误: {str(e)}")


@kb_management_bp.route('/api/delete/<int:record_id>', methods=['DELETE'])
@login_required(roles=['admin'])
def delete_record(record_id):
    """删除记录"""
    try:
        existing = fetch_record_by_id(record_id)
        if not existing:
            return error_response(f"记录 {record_id} 不存在", 404)

        with db_connection('kb') as conn:
            cursor = conn.cursor()
            sql = "DELETE FROM `KB-info` WHERE KB_Number = %s"
            cursor.execute(sql, (record_id,))
            conn.commit()
            affected_rows = cursor.rowcount

        if affected_rows > 0:
            logger.info(f"删除知识库记录 {record_id} 成功")
            return success_response(message='记录删除成功')
        else:
            return error_response('删除记录失败', 500)
    except Exception as e:
        log_exception(logger, "删除知识库记录失败")
        return server_error_response(f"删除记录时发生错误: {str(e)}")


@kb_management_bp.route('/api/batch-delete', methods=['POST'])
@login_required(roles=['admin'])
def batch_delete_records():
    """批量删除记录"""
    try:
        # 获取原始请求数据
        raw_data = request.get_data(as_text=True)
        logger.info(f"批量删除请求，原始数据: {raw_data}")

        data = request.get_json()
        logger.info(f"批量删除请求，解析后的数据: {data}")
        logger.info(f"数据类型: {type(data)}, 是否为dict: {isinstance(data, dict)}")

        if not isinstance(data, dict):
            logger.error(f"请求数据不是字典类型: {type(data)}")
            return error_response('请求数据格式错误', 400)

        ids = data.get('ids', [])
        logger.info(f"提取的ids: {ids}, 类型: {type(ids)}, 是否为list: {isinstance(ids, list)}, 长度: {len(ids) if ids else 0}")

        if not ids:
            logger.warning("批量删除失败: ids为空")
            logger.info(f"data.keys(): {list(data.keys()) if data else 'None'}")
            return error_response('没有要删除的记录', 400)

        from common.kb_utils import get_kb_db_connection
        connection = get_kb_db_connection()
        if connection is None:
            logger.error("批量删除失败: 数据库连接失败")
            return server_error_response('数据库连接失败')

        with connection.cursor() as cursor:
            placeholders = ','.join(['%s'] * len(ids))
            sql = f"DELETE FROM `KB-info` WHERE KB_Number IN ({placeholders})"
            logger.info(f"执行SQL: {sql}, 参数: {ids}")
            cursor.execute(sql, ids)
            affected_rows = cursor.rowcount
            connection.commit()
            logger.info(f"批量删除成功: 影响了 {affected_rows} 行")

        connection.close()

        logger.info(f"批量删除知识库记录完成: {affected_rows} 条")
        return success_response(
            message=f'成功删除 {affected_rows} 条记录'
        )
    except Exception as e:
        logger.exception("批量删除知识库记录失败")
        return server_error_response(f"批量删除记录时发生错误: {str(e)}")
        # 获取原始请求数据
        raw_data = request.get_data(as_text=True)
        logger.info(f"批量删除请求，原始数据: {raw_data}")
        print(f"原始请求数据: {raw_data}")

        # 先尝试不解析JSON，直接检查
        if not raw_data or raw_data.strip() == '':
            logger.error("请求数据为空")
            print("ERROR: 请求数据为空")
            return error_response('请求数据为空', 400)

        data = request.get_json()
        logger.info(f"批量删除请求，解析后的数据: {data}")
        logger.info(f"数据类型: {type(data)}, 是否为dict: {isinstance(data, dict)}")
        print(f"解析后的数据: {data}")
        print(f"数据类型: {type(data)}")

        if data is None:
            logger.error("JSON解析失败，data为None")
            print("ERROR: JSON解析失败")
            return error_response('JSON数据格式错误', 400)

        if not isinstance(data, dict):
            logger.error(f"请求数据不是字典类型: {type(data)}")
            print(f"ERROR: 数据类型错误: {type(data)}")
            return error_response('请求数据格式错误', 400)

        ids = data.get('ids', [])
        logger.info(f"提取的ids: {ids}, 类型: {type(ids)}, 是否为list: {isinstance(ids, list)}, 长度: {len(ids) if ids else 0}")
        print(f"提取的ids: {ids}")

        if not ids:
            logger.warning("批量删除失败: ids为空")
            logger.info(f"data.keys(): {list(data.keys()) if data else 'None'}")
            print("ERROR: ids为空")
            return error_response('没有要删除的记录', 400)

        from common.kb_utils import get_kb_db_connection
        connection = get_kb_db_connection()
        if connection is None:
            logger.error("批量删除失败: 数据库连接失败")
            return server_error_response('数据库连接失败')

        with connection.cursor() as cursor:
            placeholders = ','.join(['%s'] * len(ids))
            sql = f"DELETE FROM `KB-info` WHERE KB_Number IN ({placeholders})"
            logger.info(f"执行SQL: {sql}, 参数: {ids}")
            cursor.execute(sql, ids)
            affected_rows = cursor.rowcount
            connection.commit()
            logger.info(f"批量删除成功: 影响了 {affected_rows} 行")

        connection.close()

        logger.info(f"批量删除知识库记录完成: {affected_rows} 条")
        return success_response(
            message=f'成功删除 {affected_rows} 条记录'
        )
    except Exception as e:
        logger.exception("批量删除知识库记录失败")
        return server_error_response(f"批量删除记录时发生错误: {str(e)}")


@kb_management_bp.route('/api/export', methods=['GET'])
@login_required(roles=['admin'])
def export_data():
    """导出所有数据"""
    try:
        records = fetch_all_records()
        logger.info(f"导出知识库数据: {len(records)} 条记录")
        return success_response(
            message='数据导出成功',
            data={
                'data': records,
                'count': len(records)
            }
        )
    except Exception as e:
        log_exception(logger, "导出知识库数据失败")
        return server_error_response(f"导出数据时发生错误: {str(e)}")


@kb_management_bp.route('/api/records', methods=['GET'])
@login_required(roles=['admin'])
def get_paginated_records():
    """获取分页记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search_name = request.args.get('search', '').strip()
        
        if not page or page < 1:
            page = 1
        if not per_page or per_page < 1 or per_page > 100:
            per_page = 20
        
        from common.kb_utils import fetch_records_by_name_with_pagination
        if search_name:
            records, total_count = fetch_records_by_name_with_pagination(search_name, page, per_page)
        else:
            records, total_count = fetch_records_with_pagination(page, per_page)
        
        total_pages = (total_count + per_page - 1) // per_page
        showing_start = (page - 1) * per_page + 1
        showing_end = min(page * per_page, total_count)
        
        response_data = {
            'records': records,
            'total_count': total_count,
            'showing_count': showing_end - showing_start + 1 if records else 0,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'showing_start': showing_start,
            'showing_end': showing_end
        }
        return jsonify({
            'success': True,
            'message': '查询成功',
            **response_data
        })
    except Exception as e:
        log_exception(logger, "获取知识库分页记录失败")
        return server_error_response(
            message=f"获取记录失败: {str(e)}"
        )


@kb_management_bp.route('/api/system-status', methods=['GET'])
@login_required(roles=['admin'])
def system_status():
    """获取系统状态"""
    try:
        total_records = get_total_count()

        user_count = 0
        latest_record_time = None
        database_connected = True

        with db_connection('kb') as conn:
            try:
                import pymysql
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute("SELECT COUNT(*) as count FROM `users`")
                user_count = cursor.fetchone()['count']

                if total_records > 0:
                    cursor.execute("SELECT MAX(KB_UpdateTime) as max_time FROM `KB-info`")
                    result = cursor.fetchone()
                    if result and result.get('max_time'):
                        latest_record_time = result['max_time'].strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                logger.error(f"获取知识库系统状态失败: {e}")
                database_connected = False

        system_health = 'database_error' if not database_connected else ('connected_no_data' if total_records == 0 else 'healthy')

        return success_response(
            data={
                'system_health': system_health,
                'database_connected': database_connected,
                'total_records': total_records,
                'user_count': user_count,
                'latest_record_time': latest_record_time,
                'current_user': get_current_user(),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            message='查询成功'
        )
    except Exception as e:
        log_exception(logger, "获取知识库系统状态失败")
        return server_error_response(message=f"获取系统状态失败: {str(e)}")
