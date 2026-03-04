"""
Trilium 笔记服务辅助模块
提供 Trilium API 调用功能
"""
import requests
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class TriliumHelper:
    """Trilium 笔记服务辅助类"""

    def __init__(self, server_url=None, token=None):
        """
        初始化 Trilium 辅助类

        Args:
            server_url: Trilium 服务器地址
            token: Trilium 认证令牌
        """
        self.server_url = server_url or ''
        self.token = token or ''
        self.session = requests.Session()

    def search_note(self, query, limit=30):
        """
        搜索Trilium笔记(基于trilium-py官方API重写)

        Trilium 搜索语法(官方):
        - 普通搜索: 关键词 - 在标题、内容、属性中搜索
        - 精确匹配: "关键词" - 用引号包裹
        - 标签搜索: #标签名
        - 属性搜索: #属性名=属性值
        - 通配符: * - 匹配任意字符
        - 多词搜索: 空格分隔(AND关系)

        Args:
            query: 搜索关键词(空字符串表示获取所有笔记)
            limit: 返回结果数量限制

        Returns:
            tuple: (success: bool, results: list, message: str)
        """
        try:
            # 如果查询为空，使用通配符获取所有笔记
            search_query = query if query else "*"

            # 尝试使用 trilium-py 模块
            try:
                from trilium_py.client import ETAPI

                server_url = self.server_url.rstrip('/')
                token = self.token

                # 如果没有token，尝试使用密码登录
                if not token:
                    logger.info("使用密码模式连接Trilium")
                    ea = ETAPI(server_url)
                    token = None
                else:
                    ea = ETAPI(server_url, token)

                # Trilium ETAPI 搜索参数(基于官方文档)
                # search: 搜索字符串,支持 Trilium 查询语法
                # limit: 限制返回结果数量
                # orderBy: 排序字段(可选,如 'title', 'utcDateModified')
                # fastSearch: 是否启用快速搜索(可选,默认true)
                # includeArchived: 是否包含已归档笔记(可选,默认false)

                logger.info(f"Trilium搜索: query='{search_query}', limit={limit}")

                # 执行搜索 - 移除orderBy参数,让它使用默认设置
                # Trilium 界面搜索可用,说明基本参数应该就够用
                results = ea.search_note(search=search_query, limit=limit)
                logger.info(f"Trilium搜索返回: {type(results)}, keys: {list(results.keys()) if isinstance(results, dict) else 'N/A'}")

                # 检查返回数据格式
                if not isinstance(results, dict):
                    logger.error(f"Trilium搜索返回非字典类型: {type(results)}")
                    return False, [], '搜索返回数据格式错误'

                # Trilium ETAPI 标准返回格式: {results: [...]}
                if 'results' not in results:
                    logger.warning(f"Trilium搜索结果中没有 'results' 字段, keys: {list(results.keys())}")
                    results['results'] = []

                # 获取搜索结果
                notes = results.get('results', [])
                logger.info(f"Trilium搜索返回 {len(notes)} 条结果")

                # 格式化结果
                formatted_results = []
                for note in notes[:limit]:
                    formatted_results.append({
                        'noteId': note.get('noteId', ''),
                        'title': note.get('title', ''),
                        'type': note.get('type', 'text'),
                        'dateModified': note.get('utcDateModified', '')
                    })

                logger.info(f"Trilium搜索最终返回 {len(formatted_results)} 条结果")

                if formatted_results:
                    return True, formatted_results, '搜索成功'
                else:
                    return True, [], '未找到匹配的笔记'

            except ImportError:
                logger.warning("trilium-py 模块未安装，回退到基础API模式")
                # 回退方案：直接调用Trilium API
                return self._search_via_api(search_query, limit)

        except Exception as e:
            logger.error(f"搜索Trilium笔记异常: {e}", exc_info=True)
            return False, [], f'搜索失败: {str(e)}'

    def _search_via_api(self, query, limit=30):
        """
        通过基础API搜索（备用方案）

        Args:
            query: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            tuple: (success: bool, results: list, message: str)
        """
        try:
            # 构建搜索URL
            search_url = f"{self.server_url.rstrip('/')}/api/notes/search"
            
            headers = {}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'

            params = {
                'search': query,
                'limit': limit
            }

            response = self.session.get(search_url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                return True, results, '搜索成功'
            else:
                return False, [], f'搜索失败: {response.status_code}'

        except Exception as e:
            logger.error(f"基础API搜索失败: {e}")
            return False, [], f'搜索失败: {str(e)}'

    def get_note_content(self, note_url):
        """
        获取笔记内容

        Args:
            note_url: 笔记的 URL

        Returns:
            tuple: (success: bool, content: str, message: str)
        """
        try:
            # 构建完整的 API URL
            if not note_url.startswith('http'):
                if self.server_url:
                    base_url = self.server_url.rstrip('/')
                    note_url = f"{base_url}/{note_url}"
                else:
                    return False, '', 'Trilium 服务未配置'

            # 尝试使用 trilium-py 模块
            try:
                from trilium_py.client import ETAPI

                server_url = self.server_url.rstrip('/')
                token = self.token

                # 如果没有token，尝试使用密码登录
                if not token:
                    logger.info("使用密码模式连接Trilium")
                    ea = ETAPI(server_url)
                    # 注意：这里需要从外部获取密码
                    token = None
                else:
                    ea = ETAPI(server_url, token)

                # 从URL中提取noteId
                # URL格式可能是: http://server/#root/noteId 或 http://server/#/root/noteId
                # 注意：noteId可能是克隆笔记，格式为 parent_child
                if '#/root/' in note_url:
                    note_id = note_url.split('#/root/')[-1].split('?')[0]
                elif '#root/' in note_url:
                    note_id = note_url.split('#root/')[-1].split('?')[0]
                else:
                    note_id = None

                logger.info(f"尝试获取Trilium笔记内容: note_id={note_id}, url={note_url}")

                # 检查是否是克隆笔记（包含路径分隔符）
                is_branch_note = '/' in note_id if note_id else False
                if is_branch_note:
                    logger.info(f"检测到克隆笔记，原始noteId: {note_id}")
                    # 对于克隆笔记，使用子noteId
                    child_note_id = note_id.split('/')[-1]
                    logger.info(f"使用子noteId: {child_note_id}")
                    note_id = child_note_id

                if note_id:
                    try:
                        # 使用ETAPI获取笔记内容
                        logger.info(f"通过ETAPI获取笔记内容: note_id={note_id}")

                        # 获取笔记内容
                        content = ea.get_note_content(note_id)

                        if content:
                            logger.info(f"成功获取Trilium笔记内容，内容长度: {len(content)}")

                            # 清理内容
                            content = self._clean_content(content)
                            return True, content, '获取成功'
                        elif response.status_code == 401:
                            logger.warning("HTTP访问失败，尝试使用get_note方法")
                            # 回退到 get_note 方法
                            note_info = ea.get_note(note_id)
                            logger.info(f"Trilium笔记信息: {note_info}")

                            # 检查返回的数据结构
                            if isinstance(note_info, dict):
                                note_type = note_info.get('type', 'text')
                                logger.info(f"笔记类型: {note_type}")

                                # 对于笔记本（book）类型，获取第一个子笔记的内容
                                if note_type == 'book':
                                    child_note_ids = note_info.get('childNoteIds', [])
                                    if child_note_ids:
                                        # 获取第一个子笔记的内容
                                        first_child_id = child_note_ids[0]
                                        logger.info(f"检测到笔记本类型，获取第一个子笔记: {first_child_id}")

                                        # 递归获取子笔记内容
                                        child_note_info = ea.get_note(first_child_id)
                                        logger.info(f"子笔记信息: {child_note_info}")

                                        if isinstance(child_note_info, dict):
                                            # 尝试从子笔记获取内容
                                            content = None
                                            for field in ['content', 'noteContent', 'text', 'contentText']:
                                                if field in child_note_info and child_note_info[field]:
                                                    content = child_note_info[field]
                                                    logger.info(f"从子笔记字段 '{field}' 获取到内容")
                                                    break

                                            if content:
                                                logger.info(f"成功获取Trilium笔记本内容，内容长度: {len(content) if content else 0}")
                                                return True, content, '获取成功'
                                            else:
                                                logger.warning(f"子笔记中未找到内容字段，子笔记信息: {child_note_info}")
                                                return False, f'笔记本格式不支持: {str(child_note_info)[:100]}', '无法解析笔记内容'
                                    else:
                                        logger.warning("笔记本类型笔记但没有子笔记")
                                        return False, '笔记本为空', '笔记本为空，没有可显示的内容'
                                else:
                                    # 对于普通笔记，尝试从不同的字段获取内容
                                    content = None

                                    # 尝试多个可能的字段名
                                    for field in ['content', 'noteContent', 'text', 'contentText']:
                                        if field in note_info and note_info[field]:
                                            content = note_info[field]
                                            logger.info(f"从字段 '{field}' 获取到内容")
                                            break

                                    if content:
                                        logger.info(f"成功获取Trilium笔记内容，内容长度: {len(content) if content else 0}")
                                        return True, content, '获取成功'
                                    else:
                                        # 如果没有内容字段，返回整个笔记信息
                                        logger.warning(f"笔记信息中未找到内容字段，笔记信息: {note_info}")
                                        return False, f'笔记格式不支持: {str(note_info)[:100]}', '无法解析笔记内容'
                            else:
                                logger.error(f"get_note 返回了非字典类型: {type(note_info)}")
                                return False, '', f'笔记数据格式错误: {str(note_info)[:100]}'
                        elif response.status_code == 404:
                            logger.error(f"笔记不存在: {note_id}")
                            return False, '', '笔记不存在'
                        else:
                            logger.error(f"HTTP返回错误: {response.status_code}")
                            return False, '', f'访问失败: HTTP {response.status_code}'

                    except Exception as api_error:
                        logger.error(f"获取笔记内容失败: {api_error}", exc_info=True)
                        return False, '', f'获取笔记失败: {str(api_error)}'
                else:
                    logger.error(f"无法从URL中解析noteId: {note_url}")
                    return False, '', '无法解析笔记ID'

            except ImportError:
                logger.warning("trilium-py 模块未安装，回退到基础API模式")
                # 回退方案：直接获取
                return self._get_content_via_api(note_url)

        except Exception as e:
            logger.error(f"获取Trilium内容异常: {e}", exc_info=True)
            return False, '', f'获取内容失败: {str(e)}'

    def _get_content_via_api(self, note_url):
        """
        通过直接HTTP请求获取笔记渲染内容（备用方案）

        Args:
            note_url: 笔记的 URL

        Returns:
            tuple: (success: bool, content: str, message: str)
        """
        try:
            # 从URL中提取noteId
            if '#/root/' in note_url:
                note_id = note_url.split('#/root/')[-1].split('?')[0]
            elif '#root/' in note_url:
                note_id = note_url.split('#root/')[-1].split('?')[0]
            else:
                note_id = None

            if not note_id:
                return False, '', '无法解析笔记ID'

            # 构建Trilium笔记的HTTP访问URL（直接获取渲染后的HTML）
            # 这种方法可以直接获取笔记的渲染内容，无需通过API
            trilium_note_url = f"{self.server_url.rstrip('/')}/#/root/{note_id}"

            # 添加认证头
            headers = {}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'

            logger.info(f"通过HTTP直接访问Trilium笔记: {trilium_note_url}")

            # 调用 Trilium 的HTTP接口获取渲染后的HTML
            response = self.session.get(trilium_note_url, headers=headers, timeout=10)

            if response.status_code == 200:
                content = response.text
                logger.info(f"成功获取Trilium笔记渲染内容，内容长度: {len(content)}")

                # 清理内容
                content = self._clean_content(content)
                return True, content, '获取成功'
            elif response.status_code == 401:
                return False, '', 'Trilium 认证失败，请检查 Token 配置'
            elif response.status_code == 404:
                return False, '', '笔记不存在'
            else:
                logger.error(f"Trilium HTTP返回错误: {response.status_code}")
                return False, '', f'Trilium 服务返回错误: {response.status_code}'

        except requests.exceptions.Timeout:
            logger.error(f"获取 Trilium 内容超时: {note_url}")
            return False, '', '请求超时，请稍后重试'
        except requests.exceptions.ConnectionError:
            logger.error(f"连接 Trilium 服务失败: {note_url}")
            return False, '', '无法连接到 Trilium 服务'
        except Exception as e:
            logger.error(f"获取 Trilium 内容异常: {e}", exc_info=True)
            return False, '', f'获取内容失败: {str(e)}'

    def _clean_content(self, content):
        """
        清理和规范化 HTML 内容

        Args:
            content: 原始 HTML 内容

        Returns:
            str: 清理后的 HTML 内容
        """
        import re

        if not content:
            return content

        # 检查是否有外部引用
        has_kb_ref = '/kb/' in content
        has_svg_ref = '.svg' in content or '<svg' in content
        has_img_ref = '<img' in content
        logger.info(f"清理前检查: has_kb_ref={has_kb_ref}, has_svg_ref={has_svg_ref}, has_img_ref={has_img_ref}")

        # 移除外部CSS链接引用（这些会导致404错误）
        # 移除 <link> 标签引用的CSS文件
        content = re.sub(r'<link[^>]*>', '', content)

        # 移除外部CSS样式表
        # 移除 <style> 标签中引用的外部CSS
        content = re.sub(r"@import\s+url\(['\"]?[^'\"]+['\"]?\)", '', content, flags=re.IGNORECASE)
        content = re.sub(r"@import\s+url\([^)]+\)", '', content, flags=re.IGNORECASE)

        # 移除内联样式表中的外部URL引用（相对路径和绝对路径）
        # 处理 style 标签中的 background-image、src 等属性
        content = re.sub(r"url\(['\"]?https?://[^'\"]+['\"]?\)", '', content, flags=re.IGNORECASE)
        content = re.sub(r"url\(['\"]?/kb/[^'\"]*['\"]?\)", '', content, flags=re.IGNORECASE)
        content = re.sub(r"url\(['\"]?\.\./[^'\"]*['\"]?\)", '', content, flags=re.IGNORECASE)

        # 移除或替换图片标签中的外部资源引用
        # 保留图片标签以便正常显示图片
        # 移除包含外部路径的 img 标签，但保留本地或 base64 图片
        content = re.sub(r'<img[^>]*src=["\']/?kb/[^"\']*["\'][^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<img[^>]*src=["\']?\.\./[^"\']*["\'][^>]*>', '', content, flags=re.IGNORECASE)
        # 注意：以下正则会移除所有图片，已注释掉以允许图片显示
        # content = re.sub(r'<img[^>]*src=["\'][^"\"]*\.(png|jpg|jpeg|gif|svg|ico|webp)["\'][^>]*>', '', content, flags=re.IGNORECASE)

        # 保留 SVG 标签以显示图标和矢量图形
        # content = re.sub(r'<svg[^>]*>.*?</svg>', '', content, flags=re.DOTALL | re.IGNORECASE)

        # 移除 script 标签（避免外部脚本加载问题）
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)

        # 移除 iframe 标签（避免外部资源加载）
        content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', content, flags=re.DOTALL | re.IGNORECASE)

        # 移除所有 meta 标签（除了 charset 和 viewport）
        content = re.sub(r'<meta(?![^>]*(charset|viewport))[^>]*>', '', content, flags=re.IGNORECASE)

        # 再次检查清理后的内容
        has_kb_ref_after = '/kb/' in content
        has_svg_ref_after = '.svg' in content or '<svg' in content
        has_img_ref_after = '<img' in content
        logger.info(f"清理后检查: has_kb_ref={has_kb_ref_after}, has_svg_ref={has_svg_ref_after}, has_img_ref={has_img_ref_after}")

        # 确保HTML标签正确闭合
        # 添加基本的内联样式，确保基本可读性
        cleaned_html = content

        # 提取body内容（如果有）
        body_match = re.search(r'<body[^>]*>(.*?)</body>', cleaned_html, re.DOTALL | re.IGNORECASE)
        if body_match:
            body_content = body_match.group(1)
            # 添加基础样式容器
            styled_body = f"""
                <div style="
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 100%;
                    overflow-x: auto;
                    padding: 20px;
                ">
                    {body_content}
                </div>
            """
            cleaned_html = cleaned_html.replace(body_match.group(0), styled_body)

        # 添加meta标签确保正确的字符集
        meta_tag = '<meta charset="UTF-8">'
        if '<meta' not in cleaned_html:
            cleaned_html = meta_tag + cleaned_html

        return cleaned_html

    def get_all_notes(self):
        """
        获取 Trilium 中的所有笔记
        使用分页策略获取所有笔记，避免 Trilium API 的返回数量限制

        Returns:
            tuple: (success: bool, results: list, message: str)
        """
        try:
            # 尝试使用 trilium-py 模块
            try:
                from trilium_py.client import ETAPI

                server_url = self.server_url.rstrip('/')
                token = self.token

                if not token:
                    logger.info("使用密码模式连接Trilium")
                    ea = ETAPI(server_url)
                else:
                    ea = ETAPI(server_url, token)

                # 使用分页策略获取所有笔记
                logger.info("开始分页获取 Trilium 所有笔记...")
                all_results = []
                page_size = 1000  # Trilium API 的最大限制
                max_iterations = 100  # 最多尝试100次

                for iteration in range(max_iterations):
                    # 使用 orderBy 和 offset 来分页
                    # 添加各种参数以确保获取所有类型的笔记
                    results = ea.search_note(
                        search="*",
                        limit=page_size,
                        orderBy="noteId",
                        offset=iteration * page_size,
                        # 其他可能的参数
                        ancestorNoteId=None,  # 不限制祖先笔记
                        type=None  # 不限制笔记类型
                    )

                    if 'results' in results and results['results']:
                        all_results.extend(results['results'])
                        # 减少日志输出：只在每10页或最后一页打印
                        if (iteration + 1) % 10 == 0 or len(results['results']) < page_size:
                            logger.info(f"第 {iteration + 1} 页: 获取到 {len(results['results'])} 条笔记，累计 {len(all_results)} 条")

                        # 如果返回的数量少于 page_size，说明已经获取完所有笔记
                        if len(results['results']) < page_size:
                            logger.info(f"已获取所有笔记，共 {len(all_results)} 条")
                            break
                    else:
                        logger.info(f"第 {iteration + 1} 页: 没有更多笔记，累计 {len(all_results)} 条")
                        break

                # 格式化结果
                formatted_results = []
                for result in all_results:
                    formatted_results.append({
                        'noteId': result.get('noteId', ''),
                        'title': result.get('title', ''),
                        'type': result.get('type', 'text'),
                        'dateModified': result.get('utcDateModified', '')
                    })

                logger.info(f"成功获取 Trilium 所有笔记: {len(formatted_results)} 条")

                # 如果通过分页获取的笔记数量很少（少于 2000），尝试使用递归方法获取更完整的结果
                # 这可能是因为搜索 API 对某些笔记类型有限制
                if len(all_results) < 2000:
                    logger.warning(f"通过搜索 API 只获取到 {len(all_results)} 条笔记，尝试使用递归方法获取更完整的结果")
                    success_recursive, recursive_results, msg_recursive = self.get_all_notes_recursive()
                    if success_recursive and len(recursive_results) > len(formatted_results):
                        logger.info(f"递归方法获取到更多笔记: {len(recursive_results)} 条，将使用递归结果")
                        return success_recursive, recursive_results, msg_recursive
                    else:
                        logger.info(f"递归方法获取到的笔记数量相同或更少，继续使用搜索结果")

                return True, formatted_results, '获取成功'

            except ImportError:
                logger.warning("trilium-py 模块未安装，回退到基础API模式")
                # 回退方案：直接调用 Trilium API
                return self._get_all_notes_via_api()

        except Exception as e:
            logger.error(f"获取 Trilium 所有笔记异常: {e}", exc_info=True)
            return False, [], f'获取失败: {str(e)}'

    def get_all_notes_recursive(self):
        """
        通过递归方式获取 Trilium 中的所有笔记
        从根节点开始，递归获取所有子笔记

        Returns:
            tuple: (success: bool, results: list, message: str)
        """
        try:
            from trilium_py.client import ETAPI

            server_url = self.server_url.rstrip('/')
            token = self.token

            if not token:
                logger.info("使用密码模式连接Trilium")
                ea = ETAPI(server_url)
            else:
                ea = ETAPI(server_url, token)

            logger.info("开始递归获取 Trilium 所有笔记...")
            all_results = []

            # 获取根节点
            try:
                root_note = ea.get_note('root')
                logger.info(f"获取到根节点: {root_note.get('noteId', 'root')}")
            except Exception as e:
                logger.error(f"获取根节点失败: {e}")
                return False, [], f'获取根节点失败: {str(e)}'

            # 递归获取所有笔记
            def collect_notes(note_id):
                """递归收集笔记"""
                try:
                    note_info = ea.get_note(note_id)

                    if not note_info:
                        return

                    # 添加当前笔记（排除根节点）
                    if note_id != 'root':
                        all_results.append({
                            'noteId': note_info.get('noteId', note_id),
                            'title': note_info.get('title', ''),
                            'type': note_info.get('type', 'text'),
                            'dateModified': note_info.get('utcDateModified', '')
                        })
                        logger.debug(f"收集笔记: {note_id} - {note_info.get('title', '')}")

                    # 递归处理子笔记
                    child_note_ids = note_info.get('childNoteIds', [])
                    for child_id in child_note_ids:
                        collect_notes(child_id)

                except Exception as e:
                    logger.warning(f"获取笔记 {note_id} 失败: {e}")

            # 从根节点开始递归
            collect_notes('root')

            logger.info(f"递归获取完成，共获取 {len(all_results)} 条笔记")
            return True, all_results, '获取成功'

        except Exception as e:
            logger.error(f"递归获取 Trilium 所有笔记异常: {e}", exc_info=True)
            return False, [], f'获取失败: {str(e)}'

    def _get_all_notes_via_api(self):
        """
        通过基础 API 获取所有笔记（备用方案）
        使用分页策略获取所有笔记，避免 Trilium API 的返回数量限制

        Returns:
            tuple: (success: bool, results: list, message: str)
        """
        try:
            # 构建搜索URL
            search_url = f"{self.server_url.rstrip('/')}/api/notes/search"

            headers = {}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'

            # 使用分页策略获取所有笔记
            logger.info("通过基础 API 分页获取所有笔记...")
            all_results = []
            page_size = 1000  # Trilium API 的最大限制
            max_iterations = 100  # 最多尝试100次

            for iteration in range(max_iterations):
                params = {
                    'search': '*',
                    'limit': page_size,
                    'orderBy': 'noteId',
                    'offset': iteration * page_size
                }

                logger.info(f"获取第 {iteration + 1} 页，offset={iteration * page_size}")
                response = self.session.get(search_url, headers=headers, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])

                    if results:
                        all_results.extend(results)
                        logger.info(f"第 {iteration + 1} 页: 获取到 {len(results)} 条笔记，累计 {len(all_results)} 条")

                        # 如果返回的数量少于 page_size，说明已经获取完所有笔记
                        if len(results) < page_size:
                            logger.info("已获取所有笔记")
                            break
                    else:
                        logger.info(f"第 {iteration + 1} 页: 没有更多笔记")
                        break
                else:
                    logger.error(f"获取第 {iteration + 1} 页失败: {response.status_code}")
                    break

            # 格式化结果
            formatted_results = []
            for result in all_results:
                formatted_results.append({
                    'noteId': result.get('noteId', ''),
                    'title': result.get('title', ''),
                    'type': result.get('type', 'text'),
                    'dateModified': result.get('utcDateModified', '')
                })

            logger.info(f"基础 API 成功获取所有笔记: {len(formatted_results)} 条")
            return True, formatted_results, '获取成功'

        except Exception as e:
            logger.error(f"基础 API 获取所有笔记失败: {e}")
            return False, [], f'获取失败: {str(e)}'

    def check_connection(self):
        """
        检查 Trilium 服务连接

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.server_url:
                return False, 'Trilium 服务未配置'

            headers = {}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'

            response = self.session.get(
                self.server_url.rstrip('/') + '/api/notes/root',
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                return True, '连接成功'
            elif response.status_code == 401:
                return False, '认证失败'
            else:
                return False, f'服务返回错误: {response.status_code}'

        except Exception as e:
            return False, f'连接失败: {str(e)}'


def get_trilium_helper(server_url=None, token=None):
    """
    获取 Trilium 辅助类实例（工厂函数）

    Args:
        server_url: Trilium 服务器地址（可选，从配置读取）
        token: Trilium 认证令牌（可选，从配置读取）

    Returns:
        TriliumHelper: Trilium 辅助类实例
    """
    try:
        # 从配置导入
        import config

        if server_url is None:
            server_url = getattr(config, 'TRILIUM_SERVER_URL', '')
        if token is None:
            token = getattr(config, 'TRILIUM_TOKEN', '')

        return TriliumHelper(server_url, token)
    except ImportError:
        logger.warning("无法导入 config 模块")
        return TriliumHelper(server_url, token)
