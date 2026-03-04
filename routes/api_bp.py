"""
API 路由蓝图 - 处理所有 /api/* 路由
包括 Trilium 集成 API
"""
from flask import Blueprint, request, Response
import requests
import config
from common.logger import logger
from common.response import success_response, error_response, server_error_response
from common.logger import log_exception

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/trilium/search')
def trilium_search():
    """Trilium 笔记搜索

    在 Trilium 笔记系统中搜索内容
    ---
    tags:
      - Trilium
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: 搜索关键词
      - name: limit
        in: query
        type: integer
        default: 30
        description: 返回结果数量限制
    responses:
      200:
        description: 搜索成功
      400:
        description: 参数错误
      500:
        description: Trilium 服务错误
    """
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 30))

        if not query:
            return error_response('请输入搜索关键词', 400)

        # 检查 Trilium 配置
        if not hasattr(config, 'TRILIUM_SERVER_URL') or not config.TRILIUM_SERVER_URL:
            logger.error("Trilium 服务未配置")
            return error_response('Trilium 服务未配置', 500)

        logger.info(f"开始Trilium搜索: {query}")

        # 使用 trilium-py 模块进行搜索
        try:
            from trilium_py.client import ETAPI

            server_url = config.TRILIUM_SERVER_URL.rstrip('/')
            token = config.TRILIUM_TOKEN

            # 如果没有token，尝试使用密码登录
            if not token and hasattr(config, 'TRILIUM_LOGIN_PASSWORD'):
                ea = ETAPI(server_url)
                token = ea.login(config.TRILIUM_LOGIN_PASSWORD)
                logger.info("使用密码登录Trilium成功")
                if not token:
                    return error_response('Trilium登录失败，请检查密码配置', 500)

            # 创建ETAPI客户端
            ea = ETAPI(server_url, token)

            # 执行搜索
            search_results = ea.search_note(search=query)

            # 格式化返回结果
            results = []
            if 'results' in search_results:
                # 限制返回结果数量
                for i, result in enumerate(search_results['results']):
                    if i >= limit:
                        break
                    results.append({
                        'noteId': result.get('noteId', ''),
                        'title': result.get('title', ''),
                        'type': result.get('type', 'text'),
                        'dateModified': result.get('utcDateModified', '')
                    })

            logger.info(f"Trilium搜索完成: 找到 {len(results)} 条结果")
            return success_response(
                data={'results': results, 'query': query, 'count': len(results)},
                message='搜索完成'
            )

        except ImportError as e:
            logger.error(f"trilium-py 模块未安装: {e}")
            return error_response('trilium-py 模块未安装，请运行: pip install trilium-py', 500)
        except Exception as e:
            logger.error(f"Trilium搜索异常: {str(e)}")
            return error_response(f'Trilium搜索失败: {str(e)}', 500)

    except Exception as e:
        log_exception(logger, "Trilium搜索失败")
        return server_error_response(f'搜索失败：{str(e)}')


@api_bp.route('/trilium/content')
def trilium_content():
    """获取 Trilium 笔记内容"""
    try:
        kb_number = request.args.get('kb_number', '').strip()
        trilium_url = request.args.get('trilium_url', '').strip()

        if not trilium_url:
            return error_response(message='缺少 Trilium URL 参数')

        # 从数据库获取知识库信息
        title = '知识库内容'
        modified = None

        if kb_number:
            try:
                from common.kb_utils import get_kb_db_connection
                conn = get_kb_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT KB_Name, KB_UpdateTime FROM `KB-info` WHERE KB_Number = %s",
                        (kb_number,)
                    )
                    kb_info = cursor.fetchone()
                    cursor.close()
                    conn.close()

                    if kb_info:
                        title = kb_info[0]  # KB_Name
                        if kb_info[1]:  # KB_UpdateTime
                            modified = kb_info[1].strftime('%Y-%m-%d %H:%M:%S')
            except Exception as db_error:
                logger.warning(f"获取知识库信息失败: {db_error}")

        # 构建完整的 Trilium URL
        if not trilium_url.startswith('http'):
            if hasattr(config, 'TRILIUM_SERVER_URL') and config.TRILIUM_SERVER_URL:
                base_url = config.TRILIUM_SERVER_URL.rstrip('/')
                trilium_url = f"{base_url}/{trilium_url}"
            else:
                return error_response(message='Trilium 服务未配置')

        # 检查 Trilium Token 配置
        if not hasattr(config, 'TRILIUM_TOKEN') or not config.TRILIUM_TOKEN:
            return error_response(message='Trilium 认证未配置')

        # 使用 Trilium 辅助类获取内容
        from common.trilium_helper import get_trilium_helper

        logger.info(f"开始获取Trilium内容: trilium_url={trilium_url}, kb_number={kb_number}")

        trilium_helper = get_trilium_helper()
        success, content, message = trilium_helper.get_note_content(trilium_url)

        logger.info(f"Trilium内容获取结果: success={success}, message={message}, content_length={len(content) if content else 0}")

        if success:
            return success_response(data={
                'content': content,
                'title': title,
                'modified': modified,
                'kb_number': kb_number,
                'url': trilium_url
            }, message='获取成功')
        else:
            # 返回错误信息，但不是 501 错误
            logger.error(f"Trilium内容获取失败: {message}")
            return error_response(message=message)

    except Exception as e:
        log_exception(logger, "加载Trilium内容失败")
        return server_error_response(message=f'加载内容失败：{str(e)}')


@api_bp.route('/trilium/test')
def trilium_test():
    """测试 Trilium 连接"""
    try:
        if not hasattr(config, 'TRILIUM_SERVER_URL') or not config.TRILIUM_SERVER_URL:
            return error_response(message='Trilium 服务未配置')

        server_url = config.TRILIUM_SERVER_URL.rstrip('/')
        token = config.TRILIUM_TOKEN

        # 如果没有token，尝试使用密码登录
        if not token and hasattr(config, 'TRILIUM_LOGIN_PASSWORD'):
            from trilium_py.client import ETAPI
            ea = ETAPI(server_url)
            token = ea.login(config.TRILIUM_LOGIN_PASSWORD)
            if not token:
                return error_response(message='Trilium登录失败，请检查密码配置')

        # 测试连接
        from trilium_py.client import ETAPI
        ea = ETAPI(server_url, token)

        # 获取根笔记测试连接
        root_note = ea.get_note('root')

        if root_note:
            return success_response(data={'server_url': server_url}, message='Trilium 连接成功')
        else:
            return error_response(message='Trilium 连接失败')

    except Exception as e:
        logger.error(f"Trilium连接测试失败: {str(e)}")
        return error_response(message=f'连接失败: {str(e)}')


@api_bp.route('/attachments/<path:attachment_path>')
def proxy_trilium_attachment(attachment_path):
    """代理 Trilium 附件请求

    将前端请求的 Trilium 附件代理转发到 Trilium 服务器
    ---
    tags:
      - Trilium
    parameters:
      - name: attachment_path
        in: path
        type: string
        required: true
        description: 附件路径
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
            return error_response('Trilium 服务未配置', 500)

        server_url = config.TRILIUM_SERVER_URL.rstrip('/')
        # 构建目标 URL
        target_url = f"{server_url}/api/attachments/{attachment_path}"

        logger.info(f"代理 Trilium 附件: {target_url}")

        # 转发请求
        trilium_response = requests.get(
            target_url,
            params=request.args,
            timeout=10
        )

        # 返回响应
        return Response(
            trilium_response.content,
            status=trilium_response.status_code,
            headers={
                'Content-Type': trilium_response.headers.get('Content-Type', 'application/octet-stream'),
                'Content-Disposition': trilium_response.headers.get('Content-Disposition', ''),
                'Cache-Control': 'public, max-age=86400'  # 缓存1天
            }
        )

    except requests.exceptions.Timeout:
        logger.error(f"Trilium 附件请求超时: {attachment_path}")
        return error_response('请求超时', 504)
    except Exception as e:
        logger.error(f"代理 Trilium 附件失败: {str(e)}")
        return error_response(f'代理失败: {str(e)}', 500)

